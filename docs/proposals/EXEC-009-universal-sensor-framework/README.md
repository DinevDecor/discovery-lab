# EXEC-009 — Universal Sensor Framework v1.0 (Proposed)

**Status**: ARCHITECTURAL CONSOLIDATION — proposal only. No code was
written or modified to produce this proposal. `observation-agent/` and
`reality-sensor/` are unchanged. Nothing in this proposal is
implemented; adoption requires a separate, later, explicitly-approved
task, per `EXEC-009`'s own "Do not modify the operational baseline
without explicit human approval."

## Mission recap

Extract the common architecture underlying Observation Agent and
Reality Sensor 001, so future Reality Sensors (Research, Business,
Public Procurement, Regulations, Markets, Calendar/Personal Operations)
have a foundation to build on instead of each reinventing capture,
normalization, trust, deduplication, registry, and reporting from
scratch. The framework must be **discovered, not invented** — every
promotion in this proposal traces to evidence found in the two
implementations that already exist, per the task's own Anti-
Abstraction Rule: "every shared component must have evidence from at
least two independent implementations."

## What was actually found

The comparison (`2-COMPARATIVE-MATRIX.md`) surfaced something the
task's own draft target-architecture didn't anticipate: **Observation
Agent and Reality Sensor 001 are not the same shape of tool wearing
different domain logic.** They split into two genuinely different
sensor families —

- **Internal/Deterministic** (Observation Agent; likely the future
  Calendar/Personal Operations sensor): no trust question, no
  duplicate-event question, ephemeral cross-run diffing.
- **External/Evidentiary** (Reality Sensor; likely Research, Business,
  Procurement, Regulations, Markets): trust classification and
  duplicate detection are central, persistent cross-run identity is
  valuable.

Three of the six layers the task's own draft diagram named as
universal (Trust Classification, Deduplication, Signal Registry) are
in fact evidenced by only *one* of the two current sensors. Meanwhile,
the single most strongly evidenced shared component in the entire
review — Safety enforcement, independently reinvented three times now
(`observation-agent`, `headquarters`, `reality-sensor`) — wasn't in
the task's draft diagram at all.

`1-FRAMEWORK-SPECIFICATION.md` revises the architecture accordingly:
Safety, configuration loading, and the CLI shape become mandatory,
cross-cutting components (strongly evidenced); Trust Classification,
Deduplication, and the persistent Signal Registry become **optional,
family-scoped layers**, offered to sensors that need them, required of
none, and explicitly *not* retrofitted onto Observation Agent.

## Deliverables (this proposal)

1. **[Framework Specification](./1-FRAMEWORK-SPECIFICATION.md)** — the
   revised layered architecture, two-family model, and Required Design
   Constraints.
2. **[Comparative Matrix](./2-COMPARATIVE-MATRIX.md)** — 18-dimension,
   evidence-sourced comparison of the two existing sensors.
3. **[Shared Component Inventory](./3-SHARED-COMPONENT-INVENTORY.md)**
   — every candidate component from `EXEC-009`'s own list, promoted,
   conditionally promoted, or explicitly rejected, each with its
   evidentiary reasoning shown.
4. **[Adapter Contract](./4-ADAPTER-CONTRACT.md)** — the minimal
   interface a future sensor must implement itself, and what it gets
   from the framework without writing it.
5. **[Migration Plan](./5-MIGRATION-PLAN.md)** — Current → Framework
   Introduction → Partial Adoption → Full Adoption, additive at every
   stage, no stage requiring either existing sensor to change.
6. **[Risk Analysis](./6-RISK-ANALYSIS.md)** — over-abstraction, future
   incompatibility, performance, and governance risks, each with a
   named mitigation or an explicit "no material risk identified."

## Recommendation

### **PARTIAL**

Not **ACCEPT**, because accepting the framework as specified would
still mean committing to build a `sensor-framework/` package now, and
`EXEC-009` itself asks only for architecture, explicitly excluding
"add new sensors" and any operational-baseline change — there is
nothing yet to fully accept *into*.

Not **REJECT**, because the evidence genuinely supports extraction:
three components (Safety, config loading, CLI shape) are independently
proven across all three existing tools, not merely plausible, and the
Migration Plan shows adoption can be entirely additive with zero
required change to either operational sensor.

**PARTIAL, specifically**: accept the architecture and the
two-family model as the ecosystem's standing design reference for any
future sensor work; **defer building the actual `sensor-framework/`
package** until either (a) a real third sensor is authorized and about
to be built, giving Stage 2 ("Framework Introduction") a concrete
consumer to validate against rather than a hypothetical one, or (b) a
human decides the three already-triple-evidenced components (Safety
above all) are worth extracting on their own merits regardless of a
third sensor's timing. Either trigger is a separate, later,
explicitly-authorized task — not decided here.

This recommendation itself follows the same discipline the proposal
argues for throughout: don't build ahead of evidence, even when the
evidence is suggestive rather than conclusive.

## Success Criteria — self-assessment

| Criterion | Met? |
|---|---|
| Every abstraction is justified by existing implementations | Yes — see the evidence citation in every Deliverable 3 entry; three items were explicitly held back for lacking it |
| No unnecessary framework complexity is introduced | Yes — optional-layer model exists specifically to avoid forcing complexity Observation Agent doesn't need |
| Future sensors become easier to build | Directionally yes for the External/Evidentiary family (Trust/Dedup/Registry templates exist to copy from); unverified until a real one is built |
| Current sensors remain compatible | Yes — zero code changes proposed or made; both remain exactly as merged |
| Migration is incremental | Yes — four additive stages, each with its own exit criterion, none requiring the next |
| Architecture remains simpler than multiple independent implementations | Partially — simpler for the 3 mandatory components (already true today, informally); genuinely uncertain for the optional layers until a third implementation tests whether "reusable template" actually holds across a domain further from Reality Sensor's own |
