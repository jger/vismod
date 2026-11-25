# VisMod Conformance Test Suite

Every language runtime under `packages/` **MUST** pass the language-agnostic test cases in `cases/` and reject all fixtures in `invalid/`.

CI automatically validates and executes all positive cases using the Python reference runner (`scripts/vismod_reference.py`) and verifies that every negative fixture is rejected.

---

## Positive Cases (`cases/*.json`)

Each `.json` file in `cases/` contains:
- `name`: Human-readable test name.
- `flow`: Inline VisMod flow object (valid against `../schema/vismod-0.1.schema.json`).
- `initialContext`: Initial input payload passed to the flow.
- `mockHandlers`: Map of handler names to deterministic mock return values (for decisions, the branch key; for actions, the context patch).
- `expectedTrace`: Ordered list of step IDs visited during execution.
- `expectedContext`: Expected final context after the `end` step completes.

---

## Invalid Fixtures (`invalid/*.vismod.yaml`)

Each `.vismod.yaml` file in `invalid/` represents a malformed flow that **MUST** be rejected by validators. The first line contains an `# expect: <substring>` comment indicating the failure reason that must be reported.
