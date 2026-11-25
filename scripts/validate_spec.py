#!/usr/bin/env python3
"""Validate VisMod JSON Schema, example *.vismod.yaml files, and conformance fixtures."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "spec" / "schema" / "vismod.v1.schema.json"
EXAMPLES_DIR = ROOT / "examples"
CONFORMANCE_DIR = ROOT / "spec" / "conformance" / "cases"


def check_referential_integrity(flow: dict, source: str) -> list[str]:
    errors: list[str] = []
    steps = flow.get("steps", [])
    step_ids = [s["id"] for s in steps]
    if len(step_ids) != len(set(step_ids)):
        errors.append(f"{source}: duplicate step IDs found")

    id_set = set(step_ids)
    entry = flow.get("entry")
    if entry not in id_set:
        errors.append(f"{source}: entry '{entry}' does not match any step id")

    for step in steps:
        sid = step["id"]
        if "next" in step and step["next"] not in id_set:
            errors.append(f"{source}: step '{sid}' next '{step['next']}' not found")
        if "default" in step and step["default"] not in id_set:
            errors.append(f"{source}: step '{sid}' default '{step['default']}' not found")
        for branch_key, target in step.get("branches", {}).items():
            if target not in id_set:
                errors.append(
                    f"{source}: step '{sid}' branch '{branch_key}' target '{target}' not found"
                )
    return errors


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    validator = jsonschema.Draft202012Validator(schema)

    errors: list[str] = []

    example_files = sorted(EXAMPLES_DIR.glob("*.vismod.yaml"))
    if not example_files:
        errors.append("No *.vismod.yaml files found in examples/")

    for path in example_files:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for err in validator.iter_errors(data):
            errors.append(f"{path.relative_to(ROOT)}: {err.message}")
        errors.extend(check_referential_integrity(data, str(path.relative_to(ROOT))))

    case_files = sorted(CONFORMANCE_DIR.glob("*.json"))
    if not case_files:
        errors.append("No conformance cases found in spec/conformance/cases/")

    for path in case_files:
        case = json.loads(path.read_text(encoding="utf-8"))
        flow = case.get("flow")
        for err in validator.iter_errors(flow):
            errors.append(f"{path.relative_to(ROOT)}: {err.message}")
        errors.extend(check_referential_integrity(flow, str(path.relative_to(ROOT))))

    if errors:
        print("Validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(
        f"Validation PASSED: schema valid, {len(example_files)} examples and "
        f"{len(case_files)} conformance cases verified."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
