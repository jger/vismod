# AI Agent Guidelines for VisMod

Use these guidelines in your repository's `AGENTS.md`, `CLAUDE.md`, or `.cursorrules` when working with AI coding agents on a VisMod-enabled codebase.

---

## Rules for AI Coding Agents

1. **Keep high-level decision logic in `*.vismod.yaml`, not nested `if/else` blocks.**
   - Whenever implementing a non-trivial workflow, pricing rule, permission check, onboarding path, or multi-step algorithm, define the control flow in a `<feature>.vismod.yaml` file.
2. **Write small, single-responsibility handlers.**
   - Each step's `handler` must map to a focused, unit-testable function in code.
   - Decision handlers should return a deterministic branch key (e.g., `"true"` / `"false"` or an explicit enum string matching `branches`).
3. **Never let code and YAML drift.**
   - Do not bypass a `*.vismod.yaml` flow with ad-hoc conditionals outside the flow.
   - Validate every modified `*.vismod.yaml` against `spec/schema/vismod.v1.schema.json`.
4. **Set appropriate `visibility`.**
   - Use `visibility: admin` (default) for internal business logic and `visibility: public` only when the flow is safe and intended for end users to inspect.
5. **Keep step IDs and descriptions human-readable.**
   - Step `id`s and `description`s appear directly in the in-app flowchart viewer; write them clearly for human reviewers.
