# VisMod Specification (`v0.1`)

This document defines the canonical `*.vismod.yaml` file format shared by all VisMod runtimes and embedded viewers.

---

## 1. File Naming

Every VisMod flow file **MUST** use the `.vismod.yaml` suffix (for example: `checkout-discount.vismod.yaml`, `user-onboarding.vismod.yaml`).

---

## 2. Identifiers & Top-Level Structure

All flow `id`, `entry`, and step `id` values **MUST** match `^[a-z0-9][a-z0-9_-]*$` (lowercase alphanumeric, starting with a letter or digit).

| Field | Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `vismod` | `"0.1"` | Yes | Exact spec version (`"0.1"`). |
| `id` | `identifier` | Yes | Unique lowercase identifier for the flow. |
| `name` | `string` | Yes | Human-readable title displayed in the embedded viewer. |
| `description` | `string` | No | Concise explanation of what the flow decides or orchestrates. |
| `visibility` | `"public" \| "admin" \| "internal"` | No | Controls who can see the flowchart inside the app. Defaults to `"admin"`. |
| `entry` | `identifier` | Yes | `id` of the first step to execute. Must exist in `steps`. |
| `steps` | `Step[]` | Yes | Ordered list of nodes in the flow (at least 1). |
| `metadata` | `object` | No | Arbitrary key/value metadata (e.g., `owner`, `tags`). |
| `dependencies` | `Dependency[]` | No | Reserved for Phase 3 system-level dependency mapping. |

---

## 3. Step Types

Every item in `steps` has a unique `id`, a `type`, and optional `label` and `description` fields for human display. Fields not belonging to a step's `type` are **forbidden**.

| Type | Required Fields | Optional Fields | Forbidden Fields |
| :--- | :--- | :--- | :--- |
| `action` | `id`, `type`, `handler`, `next` | `label`, `description`, `params` | `branches`, `default`, `flow` |
| `decision` | `id`, `type`, `handler`, `branches` | `label`, `description`, `params`, `default` | `next`, `flow` |
| `subflow` | `id`, `type`, `flow`, `next` | `label`, `description`, `params` | `handler`, `branches`, `default` |
| `end` | `id`, `type` | `label`, `description`, `handler`, `params` | `next`, `branches`, `default`, `flow` |

### Branch Keys
- Every key in `branches` **MUST** be a string matching `^[A-Za-z0-9_-]+$`.
- Boolean branch keys **MUST** be quoted in YAML (e.g. `"true": next_step`, `"false": other_step`).

> [!NOTE]
> Unquoted `true:` / `false:` keys in YAML 1.1 parsers (such as PyYAML) are parsed as booleans (`True` / `False`), while JavaScript object keys are always strings (`"true"` / `"false"`). Quoting them guarantees identical behavior across all languages.

---

## 4. Handler Binding Contract

Handlers are small, modular functions registered in the host language (e.g., TypeScript, Python):
- A runtime receives `(context, params)` and invokes the registered `handler`.
- Every `entry`, `next`, `branches[*]`, and `default` target **MUST** reference a valid `step.id` in the same file.

---

## 5. Validation

All `*.vismod.yaml` files **MUST** validate against [vismod-0.1.schema.json](schema/vismod-0.1.schema.json) and satisfy the graph rules in §7.

---

## 6. Execution Semantics

1. **Context initialization:** Execution starts with a shallow copy of the caller-provided `initialContext` key/value object.
2. **`action` and `end` handlers:**
   - Receive `(context, params)`.
   - Must return either a key/value object (a context patch) or nothing (`null` / `None` / `undefined`).
   - Returning an object **shallowly merges** its keys into the current context (returned keys overwrite existing top-level keys; nested objects are replaced, not deep-merged).
   - Returning nothing leaves the context unchanged.
   - Returning any other type is a runtime error.
3. **`decision` handlers:**
   - Receive `(context, params)` and **MUST NOT** mutate context.
   - Return a string branch key. Booleans **MUST** be coerced to `"true"` / `"false"`. Returning any other type is a runtime error.
   - The runtime routes to `branches[key]`, or `default` if `key` is not in `branches`. If neither matches, it is a runtime error.
4. **Termination:** Reaching an `end` step executes its optional `handler` (if present), stops execution, and returns the execution trace and final context.
5. **Step limit:** Runtimes **MUST** enforce a maximum step count (recommended default: `1000`) and abort with an error if exceeded, preventing infinite loops.

---

## 7. Graph Rules

A valid VisMod flow **MUST** satisfy all of the following structural invariants:
1. Every `step.id` is unique within the file.
2. `entry` and every `next`, `default`, and `branches[*]` target exists in `steps`.
3. Every step in `steps` is reachable from `entry` (no dead/unreachable steps).
4. The flow contains at least one `end` step, and every reachable step has at least one path to an `end` step.
5. Loops (cycles) are allowed when an `end` step remains reachable (for example, retry flows), but validators should emit a warning so authors remember to rely on runtime step limits.
