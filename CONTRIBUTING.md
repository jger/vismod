# Contributing to VisMod

Thank you for your interest in contributing to **VisMod**!

## Repository Layout

- `spec/` — The canonical `*.vismod.yaml` specification, JSON Schema, and language-agnostic conformance tests.
- `examples/` — Reference `*.vismod.yaml` flows that all implementations should be able to parse and visualize.
- `packages/<ecosystem>/` — Self-contained language or framework implementations (`js`, `python`, etc.).
- `docs/` — Architecture notes and AI coding agent guidelines.

## Adding a New Language or Framework Implementation

1. Create a directory under `packages/<language-or-framework>/` with its own native project manifest (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, etc.).
2. Implement parsing and validation against `spec/schema/vismod.v1.schema.json`.
3. Run and pass all test cases in `spec/conformance/cases/`.
4. Document installation, usage, and viewer integration in `packages/<language-or-framework>/README.md` and add it to the matrix in `packages/README.md`.

## Proposing Specification Changes

1. Open an issue describing the use case and proposed schema change.
2. Update `spec/SPEC.md`, `spec/schema/vismod.v1.schema.json`, and add or update conformance cases in `spec/conformance/cases/`.
3. Ensure all `examples/*.vismod.yaml` files validate cleanly against the updated schema.

## Versioning & Releases

VisMod follows [Semantic Versioning](https://semver.org/):
- Root version is tracked in `VERSION` and documented in `CHANGELOG.md`.
- Pushing an annotated tag `vX.Y.Z` triggers `.github/workflows/release.yml` to validate the schema and publish a GitHub Release.
