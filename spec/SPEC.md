# VisMod Specification (`v0.1`)

This document defines the canonical `*.vismod.yaml` file format shared by all VisMod runtimes and embedded viewers.

---

## 1. File Naming

Every VisMod flow file **MUST** use the `.vismod.yaml` suffix (for example: `checkout-discount.vismod.yaml`, `user-onboarding.vismod.yaml`).

---

## 2. Top-Level Structure

| Field | Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `vismod` | `string` | Yes | Spec version (`"0.1"`). |
| `id` | `string` | Yes | Unique kebab/snake-case identifier for the flow. |
| `name` | `string` | Yes | Human-readable title displayed in the embedded viewer. |
| `description` | `string` | No | Concise explanation of what the flow decides or orchestrates. |
| `visibility` | `"public" \| "admin" \| "internal"` | No | Controls who can see the flowchart inside the app. Defaults to `"admin"`. |
| `entry` | `string` | Yes | `id` of the first step to execute. Must exist in `steps`. |
| `steps` | `Step[]` | Yes | Ordered list of nodes in the flow (at least 1). |
| `metadata` | `object` | No | Arbitrary key/value metadata (e.g., `owner`, `tags`). |
| `dependencies` | `Dependency[]` | No | Reserved for Phase 3 system-level dependency mapping. |

---

## 3. Step Types

Every item in `steps` has a unique `id`, a `type`, and optional `label` and `description` fields for human display.

### `action`
Executes a modular handler function and continues to `next`.
- **Required:** `id`, `type: "action"`, `handler`, `next`
- **Optional:** `label`, `description`, `params`

### `decision`
Executes a modular decision handler that returns a string branch key (booleans MUST be coerced to `"true"` / `"false"`), then routes to `branches[result]` (or `default` if present).
- **Required:** `id`, `type: "decision"`, `handler`, `branches` (non-empty map of `branchKey -> stepId`)
- **Optional:** `label`, `description`, `params`, `default`

### `subflow`
Delegates to another VisMod flow by `flow` ID or relative path, then continues to `next`.
- **Required:** `id`, `type: "subflow"`, `flow`, `next`
- **Optional:** `label`, `description`, `params`

### `end`
Terminates the flow, optionally running a final `handler` to compute or format the return value.
- **Required:** `id`, `type: "end"`
- **Optional:** `label`, `description`, `handler`, `params`

---

## 4. Handler Binding Contract

Handlers are small, modular functions registered in the host language (e.g., TypeScript, Python):
- A runtime receives `(context, params)` and invokes the registered `handler`.
- Action handlers return updated context (or patch); decision handlers return a branch key matching `branches`.
- Every `entry`, `next`, `branches[*]`, and `default` target **MUST** reference a valid `step.id` in the same file.

---

## 5. Validation

All `*.vismod.yaml` files **MUST** validate against [vismod.v1.schema.json](schema/vismod.v1.schema.json).
