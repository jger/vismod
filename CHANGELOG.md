# Changelog

All notable changes to **VisMod** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.2] - 2026-11-25

### Changed
- Updated `LICENSE` copyright holder to Jannis Gerardis.
- Renamed schema to `spec/schema/vismod-0.1.schema.json` and updated `$id` to point to the GitHub repository.
- **Breaking:** Step IDs and `entry` must now be lowercase (`^[a-z0-9][a-z0-9_-]*$`); fields not allowed for a step type are rejected.
- Removed redundant `free:` branch in `examples/user-onboarding.vismod.yaml` in favor of `default`.

### Added
- Execution semantics (context shallow merge, branch key handling, step limit) and graph rules in `spec/SPEC.md`.
- Minimal Python reference runner (`scripts/vismod_reference.py`) so conformance cases are executed in CI.
- Negative conformance fixtures (`spec/conformance/invalid/*.vismod.yaml`) verified by `scripts/validate_spec.py`.
- Pinned validation dependencies in `scripts/requirements.txt` and attached `LICENSE` to GitHub Releases.

### Fixed
- Unquoted YAML boolean branch keys (`true:` / `false:`) are now rejected instead of silently accepted.
- Flows with no `end` step, dead-end loops, or unreachable steps are now rejected.

## [0.0.1] - 2026-11-25

### Added
- Initial multi-language monorepo structure for VisMod.
- VisMod v0.1 specification (`spec/SPEC.md`) and JSON Schema (`spec/schema/vismod.v1.schema.json`).
- Language-agnostic conformance test fixtures (`spec/conformance/`).
- Example flows (`examples/checkout-discount.vismod.yaml`, `examples/user-onboarding.vismod.yaml`).
- Multi-language package layout skeletons (`packages/js/`, `packages/python/`).
- Architecture and AI coding agent guidelines (`docs/`).
- GitHub Actions CI and tag-driven release workflows (`.github/workflows/`).
