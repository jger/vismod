# VisMod Conformance Test Suite

Every language runtime under `packages/` **MUST** pass the language-agnostic test cases in `cases/`.

## Case Format

Each `.json` file in `cases/` contains:
- `name`: Human-readable test name.
- `flow`: Inline VisMod flow object (valid against `../schema/vismod.v1.schema.json`).
- `initialContext`: Initial input payload passed to the flow.
- `mockHandlers`: Map of handler names to deterministic mock return values (for decisions, the branch key; for actions, the context patch).
- `expectedTrace`: Ordered list of step IDs visited during execution.
- `expectedContext`: Expected final context after the `end` step completes.
