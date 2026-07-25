# ARCH-002 — Unified Coordination Model Extraction

Status: **Architecture Consolidation**, completed. Research task, not a
design task, per the request's own framing: "Не проектирай нищо ново"
("Do not design anything new") / "Бъди археолог" ("Be an
archaeologist"). Follows directly from `ARCH-001`'s finding that the
coordination layer was independently designed at least three times.

## What this task is, precisely

Discover every existing description of coordination across the
ecosystem's repositories, extract facts only (no improvement, no
rewriting), and determine what is already common between them —
sourced only from documents that are `ACCEPTED`/`FROZEN`, or from
concepts that independently repeat across repositories without any
single ratifying document. Both constraints are honored literally
throughout; every claim in the deliverables below traces to a cited
document and its actual status, not to this task's preference for a
clean result.

## Repositories searched

`discovery-lab`, `project-memory`, `kod`, `trust-engine` (the required
minimum four), plus `generative-discovery-engine` (available, checked,
contributes one corroborating data point — see
`1-ARCHITECTURE-INVENTORY.md`). Search was by content across the
keyword list in the request (coordination, runtime, supervisor,
scheduler, dispatcher, execution, workflow, governance, orchestration,
control plane, event flow, organization, AI organization, operating
model), not by filename pattern.

## Deliverables

1. `1-ARCHITECTURE-INVENTORY.md` — every document found, with its
   actual status as written, and whether it is eligible as a canonical
   source under the task's own sourcing rule.
2. `2-COMPONENT-MATRIX.md` — the eight required components
   (Scheduler, Supervisor, Runtime, Dispatch, Queue, Event, Approval,
   Planning) × four repositories, with per-component extracted facts.
3. `3-MERGE-ANALYSIS.md` — what is the same under different names,
   what only looks the same, what overlaps partially, and the zero
   contradictions actually found.
4. `4-UNIFIED-COORDINATION-MODEL.md` — the canonical model, built only
   from ratified documents or independently-repeated concepts; nothing
   invented.
5. `5-REMAINING-GAPS.md` — five gaps (`G1`–`G5`), each necessary for
   the model to become executable, none of them merely desirable.
6. `6-EXECUTION-READINESS-REPORT.md` — verdict: **`PARTIALLY READY`**.
7. `7-EXECUTIVE-SUMMARY.md`.

## Headline finding

Three coordination mechanisms — Contract-Defined Roles, a Formal Gate,
and Human Final Authority — are not merely similar across
`project-memory`, `kod`, and `discovery-lab`. They are, at the
mechanism level, the same concept, independently ratified three times
in three separate ADR/governance instruments, in three different
vocabularies. `DLOS` was never a missing fourth coordination system —
this task makes that a documented fact rather than an argued
conclusion, and produces the reconciled model (`Unified Coordination
Model v1.0`) that removes the need to design one.
