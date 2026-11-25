# VisMod Implementations

Each language or framework implementation lives in its own isolated directory under `packages/` with its native build tooling and package manager.

| Package | Ecosystem | Status | Responsibilities |
| :--- | :--- | :--- | :--- |
| [`packages/js`](js/README.md) | TypeScript / React | Planned (`v0.1.0`) | `@vismod/core` parser/validator/runner + `@vismod/react` embedded flowchart viewer |
| [`packages/python`](python/README.md) | Python | Planned (`v0.1.0`) | `vismod` parser/validator/runner + handler decorators + web viewer integration |

## Checklist for Adding a New Implementation

1. Parse `*.vismod.yaml` and validate against `spec/schema/vismod-0.1.schema.json`.
2. Pass all cases in `spec/conformance/cases/`.
3. Support the `visibility` attribute (`public`, `admin`, `internal`) when exposing flows to UI viewers.
4. Add a `README.md` with setup, usage, and test commands.
