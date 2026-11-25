#!/usr/bin/env python3
"""Validate VisMod JSON Schema, example flows, conformance cases, and invalid fixtures."""

from __future__ import annotations

import json
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

import jsonschema
import yaml

from vismod_reference import VisModError, run

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "spec" / "schema" / "vismod-0.1.schema.json"
EXAMPLES_DIR = ROOT / "examples"
CONFORMANCE_DIR = ROOT / "spec" / "conformance" / "cases"
INVALID_DIR = ROOT / "spec" / "conformance" / "invalid"


def _step_targets(step: dict[str, Any]) -> list[str]:
    targets: list[str] = []
    if isinstance(step.get("next"), str):
        targets.append(step["next"])
    if isinstance(step.get("default"), str):
        targets.append(step["default"])
    branches = step.get("branches")
    if isinstance(branches, dict):
        for target in branches.values():
            if isinstance(target, str):
                targets.append(target)
    return targets


def check_flow(
    flow: Any,
    source: str,
    validator: jsonschema.Draft202012Validator,
) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for a single VisMod flow document."""
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(flow, dict):
        return [f"{source}: flow document must be a mapping"], warnings

    # 1. Explicit non-string branch key check (PyYAML parses unquoted true:/false: as bool)
    raw_steps = flow.get("steps")
    if isinstance(raw_steps, list):
        for step in raw_steps:
            if isinstance(step, dict) and isinstance(step.get("branches"), dict):
                sid = step.get("id", "<unknown>")
                for key in step["branches"].keys():
                    if not isinstance(key, str):
                        errors.append(
                            f"{source}: step '{sid}' branch key {key!r} is not a string "
                            f"(got {type(key).__name__}; quote boolean keys like '\"true\"')"
                        )

    # 2. JSON Schema validation
    for err in validator.iter_errors(flow):
        errors.append(f"{source}: {err.message}")

    if not isinstance(raw_steps, list) or not all(isinstance(s, dict) and "id" in s for s in raw_steps):
        return errors, warnings

    # 3. Referential integrity
    step_ids = [s["id"] for s in raw_steps]
    if len(step_ids) != len(set(step_ids)):
        errors.append(f"{source}: duplicate step IDs found")

    id_set = set(step_ids)
    steps_by_id = {s["id"]: s for s in raw_steps}
    entry = flow.get("entry")
    if entry not in id_set:
        errors.append(f"{source}: entry '{entry}' does not match any step id")

    for step in raw_steps:
        sid = step["id"]
        if "next" in step and step["next"] not in id_set:
            errors.append(f"{source}: step '{sid}' next '{step['next']}' not found")
        if "default" in step and step["default"] not in id_set:
            errors.append(f"{source}: step '{sid}' default '{step['default']}' not found")
        branches = step.get("branches")
        if isinstance(branches, dict):
            for branch_key, target in branches.items():
                if target not in id_set:
                    errors.append(
                        f"{source}: step '{sid}' branch '{branch_key}' target '{target}' not found"
                    )

    if errors:
        return errors, warnings

    # 4. Graph checks: at least one end, forward reachability, backward reachability to end, cycles
    ends = [sid for sid, s in steps_by_id.items() if s.get("type") == "end"]
    if not ends:
        errors.append(f"{source}: flow has no end step")
        return errors, warnings

    # Forward BFS from entry
    reachable: set[str] = set()
    queue: deque[str] = deque([entry])
    while queue:
        node = queue.popleft()
        if node in reachable:
            continue
        reachable.add(node)
        for nxt in _step_targets(steps_by_id[node]):
            if nxt in id_set and nxt not in reachable:
                queue.append(nxt)

    unreachable = sorted(id_set - reachable)
    if unreachable:
        errors.append(f"{source}: unreachable step(s) from entry '{entry}': {', '.join(unreachable)}")

    # Reverse BFS from all end steps
    reverse_adj: dict[str, list[str]] = defaultdict(list)
    for sid, step in steps_by_id.items():
        for nxt in _step_targets(step):
            if nxt in id_set:
                reverse_adj[nxt].append(sid)

    can_reach_end: set[str] = set()
    rev_queue: deque[str] = deque(ends)
    while rev_queue:
        node = rev_queue.popleft()
        if node in can_reach_end:
            continue
        can_reach_end.add(node)
        for prev in reverse_adj[node]:
            if prev not in can_reach_end:
                rev_queue.append(prev)

    dead_ends = sorted(reachable - can_reach_end)
    if dead_ends:
        errors.append(
            f"{source}: reachable step(s) cannot reach an end step: {', '.join(dead_ends)}"
        )

    # Cycle detection (warning only if flow can still reach an end)
    color: dict[str, int] = {sid: 0 for sid in reachable}  # 0=unvisited, 1=visiting, 2=done
    has_cycle = False

    def dfs(u: str) -> None:
        nonlocal has_cycle
        color[u] = 1
        for v in _step_targets(steps_by_id[u]):
            if v not in color:
                continue
            if color[v] == 1:
                has_cycle = True
            elif color[v] == 0:
                dfs(v)
        color[u] = 2

    dfs(entry)
    if has_cycle and not dead_ends:
        warnings.append(f"{source}: flow contains a loop (ensure runtime step limits are configured)")

    return errors, warnings


def _read_expected_error(path: Path) -> str | None:
    first_line = path.read_text(encoding="utf-8").splitlines()[0].strip()
    prefix = "# expect:"
    if first_line.lower().startswith(prefix):
        return first_line[len(prefix) :].strip()
    return None


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    validator = jsonschema.Draft202012Validator(schema)

    errors: list[str] = []
    warnings: list[str] = []

    # 1. Validate examples
    example_files = sorted(EXAMPLES_DIR.glob("*.vismod.yaml"))
    if not example_files:
        errors.append("No *.vismod.yaml files found in examples/")

    for path in example_files:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        e, w = check_flow(data, str(path.relative_to(ROOT)), validator)
        errors.extend(e)
        warnings.extend(w)

    # 2. Validate & execute conformance cases
    case_files = sorted(CONFORMANCE_DIR.glob("*.json"))
    if not case_files:
        errors.append("No conformance cases found in spec/conformance/cases/")

    for path in case_files:
        rel = str(path.relative_to(ROOT))
        case = json.loads(path.read_text(encoding="utf-8"))
        flow = case.get("flow")
        e, w = check_flow(flow, rel, validator)
        errors.extend(e)
        warnings.extend(w)
        if not e:
            try:
                trace, ctx = run(flow, case["initialContext"], case["mockHandlers"])
            except VisModError as exc:
                errors.append(f"{rel}: reference runner failed: {exc}")
            else:
                if trace != case["expectedTrace"]:
                    errors.append(
                        f"{rel}: trace mismatch: got {trace}, expected {case['expectedTrace']}"
                    )
                if ctx != case["expectedContext"]:
                    errors.append(
                        f"{rel}: context mismatch: got {ctx}, expected {case['expectedContext']}"
                    )

    # 3. Validate negative fixtures (all MUST fail)
    invalid_files = sorted(INVALID_DIR.glob("*.vismod.yaml"))
    if not invalid_files:
        errors.append("No invalid fixtures found in spec/conformance/invalid/")

    for path in invalid_files:
        rel = str(path.relative_to(ROOT))
        expected = _read_expected_error(path)
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        e, _ = check_flow(data, rel, validator)
        if not e:
            errors.append(f"{rel}: expected validation failure, but flow was ACCEPTED")
        elif expected and not any(expected.lower() in msg.lower() for msg in e):
            errors.append(
                f"{rel}: failed validation, but no error matched expected '{expected}'; got: {e}"
            )

    for w in warnings:
        print(f"WARNING: {w}")

    if errors:
        print("Validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(
        f"Validation PASSED: schema valid, {len(example_files)} examples, "
        f"{len(case_files)} conformance cases executed, "
        f"{len(invalid_files)} invalid fixtures rejected."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
