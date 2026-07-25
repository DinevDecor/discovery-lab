# Deliverable 4 — Unified Coordination Model v1.0

Per `ARCH-002` Phase 5. Built exclusively from the `Ratified` and
`Repeated-concept` rows of `1-ARCHITECTURE-INVENTORY.md`, using the
merges (and refused merges) from `3-MERGE-ANALYSIS.md`. **No new
concept is introduced.** Every component below cites the specific
document that already defines it.

## What qualifies, restated as a gate

Per the task's own sourcing rule, a component enters this model only
if: (a) it is defined in at least one document carrying an explicit
`ACCEPTED`/`FROZEN` status, **or** (b) it is not individually ratified
anywhere but the same underlying concept is independently designed in
two or more repositories. Components meeting neither test
(`contracts/dispatcher.md`'s Dispatch; `kod`'s `RUNTIME_ARCHITECTURE.md`
in the coordination sense; anything from `ORB-PROTOCOL.md`,
`ORGANIZATION-DRAFT.md`, `HIRING-LIFECYCLE-DRAFT.md`,
`FOUNDING-CHARTER.md`, `MEMORY-SOURCE-PROTOCOL.md`, or
`generative-discovery-engine`) are **excluded from v1.0** and listed
instead under "Excluded, and why" below — not because they are wrong,
but because they have not yet earned canonical standing under this
task's own rule.

## The model

```
                    ┌─────────────────────────────┐
                    │   CONTROL PLANE (concept)    │
                    │  project-memory/ADR-0001,    │
                    │  Stable Core (Ratified)      │
                    └──────────────┬────────────────┘
                                   │  (designed to be inherited;
                                   │   not yet enacted — see Phase 6)
      ┌────────────────────────────┼────────────────────────────┐
      │                            │                            │
┌─────▼──────┐             ┌───────▼───────┐            ┌───────▼───────┐
│ project-    │             │      kod       │            │ discovery-lab │
│ memory repo │             │      repo      │            │      repo     │
│ = local SSOT│             │  = local SSOT  │            │  = local SSOT │
│ (Stable Core)│            │  (ADR-0009,    │            │  (implicit,   │
│              │            │   Accepted)     │            │   enacted)    │
└─────┬───────┘             └───────┬────────┘            └───────┬───────┘
      │                             │                             │
      │   every repo independently instantiates the same          │
      │   three mechanisms below (each separately ratified):       │
      ▼                             ▼                             ▼
┌───────────────────────────────────────────────────────────────────────┐
│  CONTRACT-DEFINED ROLES — roles are versioned contracts, executors    │
│  (human or AI model) are interchangeable                              │
│  PM: Stable Core §7 (Ratified) · KOD: Agent Contracts, ADR-0009        │
│  (Accepted) · DL: Role `CONTRACT.md` files under `GOVERNANCE.md`       │
│  (Ratified)                                                            │
├───────────────────────────────────────────────────────────────────────┤
│  FORMAL GATE — a check against fixed criteria, small enumerated       │
│  verdict, never the final authority                                   │
│  PM: "Kernel as gate concept," Stable Core (Ratified) · KOD: Kernel    │
│  Review PASS/BLOCKED, ADR-0009 (Accepted) · DL: Adversarial Review     │
│  stage, GOVERNANCE.md (Ratified) · Trust: Proposal Quality Gate        │
│  (independently repeated, unratified by label)                        │
├───────────────────────────────────────────────────────────────────────┤
│  HUMAN FINAL AUTHORITY — the gate's output is input to a human        │
│  decision, never a substitute for one; stated as its own invariant    │
│  PM: Stable Core invariant (Ratified) · KOD: enacted structurally,    │
│  ADR-0009 (Accepted) · DL: ADR-0001-human-authority-gates (Ratified)  │
│  · Trust: "even CRITICAL does not mean automatic trust mutation"      │
│  (independently repeated, unratified by label)                        │
├───────────────────────────────────────────────────────────────────────┤
│  STAGED, HUMAN-GATED, REVISABLE LIFECYCLE (shape only — stage names   │
│  stay domain-specific, per 3-MERGE-ANALYSIS.md)                       │
│  DL: Freeze Lifecycle, GOVERNANCE.md (Ratified) · Trust: Mechanism     │
│  Lifecycle, meta_trust_layer_operating_model.md (independently        │
│  repeated, unratified by label)                                       │
└───────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────┐
│  MATERIAL QUEUE PATTERN — intake → manifest → processed, currently    │
│  proven in exactly one repository, ratified there                     │
│  DL only: Reality Inbox, ADR-0003 (Ratified — FROZEN). Not yet         │
│  instantiated in PM, KOD, or Trust — included as canon because a      │
│  single ratified document is sufficient per the sourcing rule, not    │
│  because it has been shown to generalize.                             │
└───────────────────────────────────────────────────────────────────────┘
```

## Reading the model

The Control Plane box at the top is drawn with a dashed relationship
deliberately: `project-memory`'s own Stable Core names the Control
Plane concept and explicitly diagrams other projects as inheritors of
it (per `ARCH-001`'s prior finding, reconfirmed here from the primary
document itself, §4 "Control Plane Architecture"). But `kod`'s
`ADR-0009` and `discovery-lab`'s `GOVERNANCE.md` each *independently
ratify the same three mechanisms* (Contract-Defined Roles, Formal
Gate, Human Final Authority) **without referencing or inheriting from
`project-memory`'s Control Plane document**. This is the precise,
document-level confirmation of `ARCH-001`'s central finding: the
concepts are the same and each is independently ratified, but the
*inheritance* the Control Plane document itself calls for has not
actually happened. The model above draws what is ratified (three
solid boxes, each independently instantiated) separately from what is
only designed (the dashed inheritance line) — collapsing the two would
overstate what exists.

## What this model is not

It is not a runtime. Nothing in it executes an approved action; it
only describes how a proposal gets *checked and approved*, never how
an approved proposal gets *carried out*. Every ratified document this
model draws from stops at the human-approval step. That gap is not a
defect in this extraction — it is what Phase 6 exists to name.

## Excluded, and why

| Excluded component | Why it does not qualify for v1.0 |
|---|---|
| `project-memory`'s Dispatcher (`contracts/dispatcher.md`) | `PILOT`, not ratified; `3-MERGE-ANALYSIS.md` found no independent repetition of the same concept elsewhere (Reality Inbox is a different concept, not a repetition of this one) |
| `kod`'s `RUNTIME_ARCHITECTURE.md`, in the "coordination runtime" sense | The document is real and roadmap-corroborated, but describes a reasoning/data pipeline, not a task/action-execution runtime — including it under "Runtime" here would repeat the false-cognate error `3-MERGE-ANALYSIS.md` flagged |
| `discovery-lab`'s ORB, `ORGANIZATION-DRAFT.md`, `HIRING-LIFECYCLE-DRAFT.md`, `FOUNDING-CHARTER.md`, `MEMORY-SOURCE-PROTOCOL.md` | All explicitly `DRAFT`/`Experimental`, and none is repeated as the same concept in another repository |
| `generative-discovery-engine`'s `RVS-00` validation kernel | `DRAFT`, `BLOCKED`; corroborates the Formal Gate pattern as a fifth data point but is not itself a qualifying source |
| Scheduler, Event, Planning (as named components) | Absent everywhere — see `2-COMPONENT-MATRIX.md`; nothing to extract |
