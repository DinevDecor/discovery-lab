# Deliverable 3 — Mapping Between the Three Documents

Section-by-section correspondence, so a reader can locate the primary
text behind any statement in `1-UNIFIED-CONTROL-PLANE-SPECIFICATION.md`.

## Source of Truth

| PM | KOD | DL |
|---|---|---|
| `INV-2`; Authority/Truth Model (§6, "Двата слоя на истината") | "Repository Governance" section | Assumed throughout; no single section |

## Contract-Defined Roles

| PM | KOD | DL |
|---|---|---|
| `INV-3`; §7 "Agent Roles and Contracts," "Формат на договора" | "Roles" and "Agent Contracts" sections | §"The mandatory lifecycle," stage 2 ("Draft" requires `CONTRACT.md`) |

## Formal Gate

| PM | KOD | DL |
|---|---|---|
| §8 "Kernel Governance Layer" in full | "ADR Lifecycle" section (Kernel Review gates Draft→Accepted) | §"The mandatory lifecycle," stage 4 "Adversarial Review" |

## Human Final Authority

| PM | KOD | DL |
|---|---|---|
| `INV-4`; §6 "Матрица на правомощията" | "ADR Lifecycle" ("Headquarters commits the status change") | §"The mandatory lifecycle," stage 7 "`FROZEN`" |

## Drift

| PM | KOD | DL |
|---|---|---|
| `INV-6`; §6 "Architecture–Implementation Drift" | "Authority Matrix" precedence-order rules (partial, narrower overlap only) | §"The mandatory lifecycle," stage 6 (`NOT READY` rollback — partial, narrower overlap only) |

## Communication / Handoff

| PM | KOD | DL |
|---|---|---|
| §14 "Handoff Protocol" | "Communication Protocol" + "Human Message Bus (Current Implementation)" | not addressed in `GOVERNANCE.md` |

## Staged Lifecycle & Versioning

| PM | KOD | DL |
|---|---|---|
| Authority Matrix's ADR-acceptance row; §16 "Artifact Lifecycles" (referenced, not reconciled in full — outside the Stable Core sections this task's scope note names) | "ADR Lifecycle" section | §"The mandatory lifecycle" (full 7 stages) + §"Versioning" (full 5-way taxonomy) |

## Anti-theater / self-exemption

| PM | KOD | DL |
|---|---|---|
| §8, "Анти-театър клауза" | Writer/Authority Matrices' structural role-separation (no named self-check clause) | "no stage may be self-certified by the same act that produced the artifact under review" (structural, not a named clause) |

## What is not mapped

`PM`'s §5 (Project Repository Architecture), §9 (Conversation and
Session Lifecycle), §15 (Parallel Work and Conflict Control), and §16
in full are real sections of `AI-Collaboration-Architecture-v1_1.md`
but fall under Operational Defaults, not the Stable Core `ADR-0001`
ratifies — out of this task's scope per `README.md`'s scope note, not
overlooked. `KOD`'s "Consequences" section restates points already
mapped above and is not separately tabled. `DL`'s "Relationship to
`HIRING-LIFECYCLE-DRAFT.md`" section describes a second, independent
axis (organizational trust) that this reconciliation does not touch —
`HIRING-LIFECYCLE-DRAFT.md` is itself `DRAFT`, excluded as a source per
`G2`'s own rule against using unratified documents as an architectural
foundation.
