# Deliverable 3 — Event Classification

Per the task's required categories. For each: what it would mean, and
whether it exists today — checked directly, not assumed.

## Repository Events

Commits, branches, merges, new/moved/deleted files. **Exists as
observable fact** — `AG-001/RUN-PROTOCOL.md` already lists exactly
this category among its Responsibilities, and `RUN-0001` exercised it
for real. **Does not exist as a trigger** — nothing watches for these
events happening; they are only checked when a human-invoked run reads
them.

## Knowledge Events

New Knowledge Object, status change, Relationship/Merge/Core Principle
Proposal filed. **Exists as observable fact** — `AG-003`'s six output
kinds, `memory/knowledge-objects/KO-S3-01.md` as a real instance.
**Does not exist as a trigger** — `EXEC-001`'s entire pipeline ran only
because a human asked for it at each step.

## Governance Events

New ADR, new Proposal, Freeze, Ratification. **Exists as observable
fact** — `docs/adr/`, `docs/proposals/`, `GOVERNANCE.md`'s lifecycle,
and `PROP-0001`'s own ratification are all real, dated, citable events.
**Does not exist as a trigger.**

## Documentation Events

`STATE.md`/`CHANGELOG.md` changes, new Sprint documents. **Exists as
observable fact** — this session's own repeated `STATE.md`/
`CHANGELOG.md` updates, and `kod`'s real `SPRINT-024.md` (found fresh
during `DL-001`). **Does not exist as a trigger.**

## Health Events

Stale documents, broken dependencies, missing references. **Exists as
a concept, exercised manually exactly once** — `PROP-0001`'s `C1`/`C2`/`C3`
criteria, run for real in `DL-001`, which found four real instances
across two repositories. **Does not exist as an ongoing mechanism** —
`DL-001` was one dated, human-invoked pass, not a recurring check.

## External Events

Something happening outside the fixed, already-known repository set.
**Does not exist, and is not proposed here.** `PROP-0001`'s own scope
rule is explicit: *"No repository may be added to scope mid-review...
expanding that list is a mandate change."* This category is named,
per the task's instruction, and immediately closed — no candidate
input source is proposed for it, since doing so would itself require a
mandate change this proposal is not authorized to make.

## Human Events

A human sending a task instruction, rendering a ratification decision
(`PROP-0001`'s own "ACCEPT"), or approving a Recommendation. **Exists,
fully** — and per `DL-002`'s own central finding, **this is currently
the only category of event that actually functions as a trigger for
anything, anywhere in this ecosystem.** Every event category above is
real as an observable fact and unobserved as a live trigger, precisely
because nothing except a human message currently starts any process in
this repository set. This proposal's recommended pilot (`6-PILOT-
SPECIFICATION.md`) is deliberately scoped to run entirely inside this
one, already-functioning category — it does not depend on any of the
others becoming real triggers first.

## Summary table

| Category | Observable fact exists? | Functions as a trigger today? |
|---|---|---|
| Repository Events | Yes | No |
| Knowledge Events | Yes | No |
| Governance Events | Yes | No |
| Documentation Events | Yes | No |
| Health Events | Yes (exercised once, `DL-001`) | No |
| External Events | Not applicable — out of ratified scope | No |
| Human Events | Yes | **Yes — the only one** |

This table is the same finding `DL-002` reached, restated per-category
rather than as a single conclusion — the granularity makes clear the
gap is uniform across every category, not specific to one.
