"""Minimal reference interpreter for VisMod v0.1 conformance testing."""

from __future__ import annotations

from typing import Any


class VisModError(Exception):
    """Raised when a VisMod flow fails during execution."""


def _branch_key(value: Any, step_id: str) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return value
    raise VisModError(
        f"{step_id}: decision handler returned {type(value).__name__}, expected str or bool"
    )


def _merge(ctx: dict[str, Any], patch: Any, step_id: str) -> dict[str, Any]:
    if patch is None:
        return ctx
    if not isinstance(patch, dict):
        raise VisModError(
            f"{step_id}: handler returned {type(patch).__name__}, expected dict or None"
        )
    return {**ctx, **patch}


def run(
    flow: dict[str, Any],
    context: dict[str, Any],
    handlers: dict[str, Any],
    max_steps: int = 1000,
) -> tuple[list[str], dict[str, Any]]:
    """Execute a validated VisMod flow using mock or callable handlers."""
    steps = {s["id"]: s for s in flow["steps"]}
    ctx: dict[str, Any] = dict(context)
    trace: list[str] = []
    current: str = flow["entry"]

    for _ in range(max_steps):
        step = steps[current]
        trace.append(current)
        kind = step["type"]

        if kind == "subflow":
            raise NotImplementedError("subflow execution is not implemented in the reference runner")

        if kind == "decision":
            handler_name = step["handler"]
            if handler_name not in handlers:
                raise VisModError(f"{current}: missing handler '{handler_name}'")
            raw = handlers[handler_name]
            result = raw(ctx, step.get("params") or {}) if callable(raw) else raw
            key = _branch_key(result, current)
            target = step["branches"].get(key, step.get("default"))
            if target is None:
                raise VisModError(f"{current}: no branch for '{key}' and no default")
            current = target
            continue

        if "handler" in step:
            handler_name = step["handler"]
            if handler_name not in handlers:
                raise VisModError(f"{current}: missing handler '{handler_name}'")
            raw = handlers[handler_name]
            patch = raw(ctx, step.get("params") or {}) if callable(raw) else raw
            ctx = _merge(ctx, patch, current)

        if kind == "end":
            return trace, ctx

        current = step["next"]

    raise VisModError(f"max_steps ({max_steps}) exceeded (possible infinite loop)")
