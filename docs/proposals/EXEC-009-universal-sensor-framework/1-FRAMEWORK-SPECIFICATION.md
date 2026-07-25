# Deliverable 1 — Universal Sensor Framework Specification v1.0 (proposed)

Status: **PROPOSED ARCHITECTURE — not implemented, not ratified.**
Per `EXEC-009`'s own constraints, this document specifies a design;
it does not create `sensor-framework/` code, does not modify
`observation-agent/` or `reality-sensor/`, and is not itself an
executable artifact.

## Why this document revises `EXEC-009`'s own proposed layer diagram

The task's own target-form sketch —

```
Reality
  ↓
Capture Adapter
  ↓
Normalization
  ↓
Evidence Validation
  ↓
Trust Classification
  ↓
Deduplication
  ↓
Signal Registry
  ↓
Reporting
  ↓
Headquarters
```

— is a reasonable starting hypothesis, and the task explicitly says
"Layers may change if evidence suggests a better structure." Deliverable
2's comparison and Deliverable 3's per-component assessment found that
**three of these named layers (Trust Classification, Deduplication,
Signal Registry) are evidenced by exactly one of the two existing
sensors**, and **one layer that isn't in the diagram at all (Safety
enforcement) is the single most strongly evidenced shared component in
the entire review** (three independent, convergent implementations).
A framework that copied the diagram unchanged would both force an
unevidenced abstraction onto Observation Agent and omit the one thing
most worth extracting. The specification below corrects both.

## Proposed architecture

```
Reality
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│ Capture Adapter          — domain-owned, framework defines only │
│                             the RawUnit boundary shape           │
└─────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│ Normalization             — domain-owned transform; framework    │
│                              defines only the Core Finding shape │
└─────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│ [Trust Classification]    — OPTIONAL: required only for          │
│                              external/evidentiary sensors        │
└─────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│ [Deduplication]           — OPTIONAL: required only where        │
│                              capture can yield >1 unit per event │
└─────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│ [Signal Registry]         — RECOMMENDED where persistent cross-  │
│                              run identity is needed; Observation │
│                              Agent's own ephemeral diff model is │
│                              equally valid and untouched         │
└─────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│ Reporting                 — framework-provided render helpers,   │
│                              sensor-owned section layout         │
└─────────────────────────────────────────────────────────┘
  │
  ▼
Headquarters                 — unchanged, out of this task's scope

════════════════════════════════════════════════════════════
Cross-cutting, MANDATORY for every sensor regardless of family:
  • Safety enforcement        (static forbidden-pattern + write-
                                scope check; strongest evidence base
                                of any component in this review)
  • Configuration pattern     (JSON + dataclass, fixed list, no
                                dynamic discovery, no third-party dep)
  • CLI shape                 (thin shim → argparse → orchestration
                                function separated from I/O)
════════════════════════════════════════════════════════════
```

Brackets `[...]` mark layers that are available, not required — a
sensor's `CONTRACT.md` states which optional layers it uses and why,
the same way `observation-agent/CONTRACT.md` and `reality-sensor/
CONTRACT.md` already state their own scope explicitly rather than
inheriting silently from a template.

## Two sensor families, named explicitly

The comparative evidence sorts naturally into two families rather than
one universal shape:

- **Internal/Deterministic sensors** (Observation Agent; the future
  Calendar/Personal Operations sensor plausibly belongs here): capture
  is synchronous and checked-in, findings are facts-about-owned-state,
  no trust question exists, no duplicate-event question exists,
  cross-run tracking is naturally ephemeral (did this specific fact
  change since last time?).
- **External/Evidentiary sensors** (Reality Sensor; the future
  Research, Business, Public Procurement, Regulations, and Markets
  sensors plausibly all belong here): capture is external and
  necessarily separated from processing, findings are claims-with-
  varying-reliability, the same real event is routinely reported by
  multiple sources, and cross-run tracking benefits from a persistent
  identity so a human can watch one recurring signal's evidence grow
  over time.

The framework serves both by making the family-specific layers
optional rather than by inventing a third, artificially general shape
that fits neither family well. This is a direct application of the
Anti-Abstraction Rule, not a hedge.

## Required Design Constraints (all preserved, all sensor-family-agnostic)

- **Read-only operation.** Every sensor's checked-in source may write
  only inside its own `reports/` directory. Enforced by the shared
  Safety module, not merely documented — this is precisely why Safety
  is promoted to a mandatory, cross-cutting layer rather than an
  optional one.
- **Deterministic processing.** Given the same captured input, a
  sensor's processing pipeline must produce byte-identical output. For
  external/evidentiary sensors this is exactly why capture must stay
  outside the checked-in, tested pipeline (see `reality-sensor/
  ARCHITECTURE.md`, unchanged by this proposal). For internal/
  deterministic sensors this already holds by construction.
- **Evidence provenance.** Every Finding's supporting evidence is a
  list of small, individually-citable, provenance-tagged records —
  never prose that blends fact and interpretation. A structural
  constraint (see `3-SHARED-COMPONENT-INVENTORY.md`'s "Evidence-plus-
  citation structure"), not a shared dataclass.
- **Reproducibility.** Both existing sensors already satisfy this by
  different, domain-appropriate means (Observation Agent: same
  filesystem state → same output; Reality Sensor: same raw-captures
  file → same output, proven by 3x-repeated-execution tests). The
  framework does not require a single mechanism, only the property.
- **Stable IDs — where identity is used at all.** Observation Agent
  does not mint persistent IDs and is not required to start. Where a
  sensor does use the optional Signal Registry, IDs must be reused by
  content-derived key, never silently re-minted (the `RS-000N`/
  `HQ-000N` convention).
- **Headquarters compatibility.** Every sensor's durable output (a
  report, a registry, or both) must be readable by Headquarters'
  existing tolerant-JSON/regex-parsing style — a specific,
  pre-configured artifact path, never a directory walk, never a new
  parser library. Confirmed compatible for both current sensors
  (`headquarters/src/headquarters/collector.py` for Observation Agent,
  already wired; `reality-sensor/tests/test_headquarters_compatibility
  .py` for Reality Sensor, structurally proven, not yet wired).
- **Human authority.** No sensor decides, merges, or acts. Every
  `recommended_action`/equivalent field is advisory prose, never an
  instruction anything downstream executes — identical in both
  existing `CONTRACT.md` files, and the one property this
  specification treats as completely non-negotiable for any future
  sensor.
