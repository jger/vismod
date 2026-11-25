# VisMod — Visual-Modular Programming

> *"Caesar's wife must be above suspicion."*
>
> Make AI-generated and complex application logic transparent, modular, and visually auditable directly inside your app.

---

## Why VisMod?

In the era of AI-assisted development and "vibe coding," agents generate code faster than humans can review it. While an application may *appear* to work, it is increasingly difficult for developers and stakeholders to verify whether an agent implemented the right algorithms, edge cases, and business rules.

**VisMod** solves this by placing critical program decisions in declarative YAML files (`*.vismod.yaml`) that live alongside your source code and bind directly to small, modular handler functions:

1. **Enforce modularity** — Business logic is split into discrete, single-responsibility steps referenced by the flow definition.
2. **Render live visual flowcharts inside the app** — Humans inspect the exact decision logic running in the application, configurable for **all users** or **admins/developers only**.
3. **Single source of truth** — Because the `*.vismod.yaml` file drives (or validates) execution, the visual diagram never drifts out of sync with the code.

---

## Quick Example (`checkout-discount.vismod.yaml`)

```yaml
vismod: "0.1"
id: checkout-discount
name: Checkout Discount Logic
visibility: admin
entry: check_membership

steps:
  - id: check_membership
    type: decision
    handler: isPremiumMember
    branches:
      "true": apply_member_discount
      "false": check_promo_code

  - id: apply_member_discount
    type: action
    handler: applyPercentDiscount
    params:
      percent: 15
    next: finalize_total

  - id: check_promo_code
    type: decision
    handler: hasValidPromoCode
    branches:
      "true": apply_promo_discount
      "false": finalize_total

  - id: apply_promo_discount
    type: action
    handler: applyPromoDiscount
    next: finalize_total

  - id: finalize_total
    type: end
    handler: calculateFinalTotal
```

---

## Repository Structure

VisMod is a **multi-language specification and monorepo**. The language-agnostic contract lives in `spec/`, while individual language and UI framework implementations live independently under `packages/`.

```text
vismod/
├── spec/                   # Canonical *.vismod.yaml specification, JSON Schema & conformance tests
│   ├── SPEC.md
│   ├── schema/
│   │   └── vismod-0.1.schema.json
│   └── conformance/
├── examples/               # Shared example *.vismod.yaml flows
├── packages/               # Language & framework implementations
│   ├── js/                 # TypeScript core + React embedded viewer
│   └── python/             # Python runtime + web framework integrations
├── docs/                   # Architecture & AI coding agent guidelines
├── CHANGELOG.md
└── VERSION
```

---

## Roadmap

### Phase 1 — Core MVP (Current)
- Canonical `*.vismod.yaml` specification and JSON Schema (`spec/`).
- Language-agnostic conformance test suite (`spec/conformance/`).
- Core runtimes and embeddable in-app flowchart viewer (starting with TypeScript/React and Python).

### Phase 2 — Online Editing
- Interactive in-app visual editor allowing authorized users to adjust flowcharts and decision paths online, exporting or syncing back to `*.vismod.yaml`.

### Phase 3 — System Dependencies
- Extend VisMod beyond individual decision flows to represent **system-level dependencies** (modules, services, APIs, and data flows) in the same visual, declarative format.

---

## Documentation

- [Specification (`spec/SPEC.md`)](spec/SPEC.md)
- [JSON Schema (`spec/schema/vismod-0.1.schema.json`)](spec/schema/vismod-0.1.schema.json)
- [Architecture (`docs/architecture.md`)](docs/architecture.md)
- [AI Agent Guidelines (`docs/ai-agent-guidelines.md`)](docs/ai-agent-guidelines.md)
- [Implementations (`packages/README.md`)](packages/README.md)
- [Contributing (`CONTRIBUTING.md`)](CONTRIBUTING.md)

---

## License

MIT — see [LICENSE](LICENSE).
