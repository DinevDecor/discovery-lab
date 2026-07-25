# Deliverable 1 — Candidate Pilot Analysis

Per `ARCH-003` Phase 1. Every candidate below is a **real, already
existing** artifact — none is hypothetical or invented for this task.
All five come from `docs/proposals/AG-003-reality-stress-test/`, whose
four datasets all received `PASS` verdicts
(`REALITY-STRESS-TEST-REPORT.md`), and are governed exclusively by
`AG-003`'s own `FROZEN v1.0` specification set (`KNOWLEDGE-OBJECT-SPEC.md`,
`PROMOTION-RULES.md`, `REVIEW-PROTOCOL.md`, `OUTPUTS.md` — all
individually marked `Status: FROZEN`). None of the demonstration
artifacts in `AG-003-knowledge-curator-walkthrough/` are used as
candidates — that folder's own `README.md` and every object in it are
explicitly self-labeled "Demonstration... not filed to a real
Knowledge Base," which disqualifies them from a task whose Mission is
to test *real* execution.

## C1 — Promote `KO-S3-01` via `CPP-S3-01` (`Draft → Candidate Principle`)

A real Core Principle Proposal, already filed in
`AG-003-reality-stress-test/CURATION-0004.md`, naming `KO-S3-01`
("the research process matters more than its conclusions") for
promotion from `Draft` to `Candidate Principle`. The proposal already
demonstrates its own threshold is met (`occurrences: 3 >= 2`,
`maturity: Recurring`, no open Contradiction Report) per
`PROMOTION-RULES.md`. Never reviewed, never acted on since 2026-07-24.

- Architectural risk: **Low** — single-object, single-field change;
  no other document is modified.
- Complexity: **Low** — one Knowledge Object, no dependency on any
  other object existing first.
- Expected value: **High** — this is the narrowest possible test of
  whether "approved" can become "actually filed" at all; also produces
  the first real file under `memory/knowledge-objects/`, closing a
  standing open question in `AG-003`'s own `STATUS.yaml`.
- Measurability: **High** — before/after diff is a single YAML field.
- Reversible without consequence: **High** — a new file addition; a
  `git revert` removes it entirely with zero effect on any existing
  ratified artifact.

## C2 — Execute `KMP-S3-01` (merge two `ADR-0002`/`ART-0001`-derived objects)

A real Knowledge Merge Proposal in the same document, recommending
`MERGE` for two overlapping "reality is the final arbiter" claims.

- Architectural risk: **Moderate** — the two candidate objects
  (`ART-0001`'s and `ADR-0002`'s versions) were never independently
  filed as standalone Knowledge Objects with full field blocks inside
  `CURATION-0004.md`; executing the merge would first require
  materializing two objects that do not yet exist as real files, an
  extra, ungated step the proposal itself does not specify.
- Complexity: **Higher than C1** — two source objects plus a merge
  operation plus `merged_from_ko` provenance rewriting.
- Expected value: **Moderate** — tests the merge mechanism, but a
  first pilot does not need to test the ecosystem's most complex
  `AG-003` output kind.
- Measurability: **Moderate** — more moving parts to verify against.
- Reversible without consequence: **Moderate** — reversible, but the
  extra materialization step means more surface area to roll back.

## C3 — File `REL-S2-01` (relationship between `KO-S2-04` and `KO-S2-03`)

A real Relationship Proposal in `CURATION-0003.md`, arising from a
genuine ontology gap (`ADR-0004` amending `ADR-0003`).

- Architectural risk: **Moderate** — `CURATION-0003.md`'s own text
  shows the type-selection reasoning still working through several
  candidate relationship types against `RELATIONSHIP-ONTOLOGY.md`;
  using a proposal whose own type determination is the most
  intellectually contested of the five candidates is a worse choice
  for a *first* pilot, which should isolate the execution question, not
  also re-litigate an ontology judgment call.
- Complexity: **Moderate–High** — both `KO-S2-03` and `KO-S2-04` would
  need to exist as real filed objects before a relationship between
  them can be filed.
- Expected value: **Moderate**.
- Measurability: **Moderate**.
- Reversible without consequence: **Moderate**.

## C4 — File `REL-S4-01` (relationship between `KO-S4-02` and `KO-S4-03`)

A real Relationship Proposal in `CURATION-0005.md`.

- Architectural risk: **Moderate–High** — the proposal itself states
  "this relationship is inferred from shared table names alone" and
  flags its own evidence as comparatively weak; piloting execution on
  the weakest-evidenced candidate risks conflating "the model can't
  execute" with "the proposal wasn't strong enough," muddying what the
  pilot is actually testing.
- Complexity: **Moderate–High** — same two-object-prerequisite issue as
  `C3`.
- Expected value: **Lower** — a rejected outcome here would be
  ambiguous evidence.
- Measurability: **Moderate**.
- Reversible without consequence: **Moderate**.

## C5 — Authorize a new Investigation from a Gap Report

Considered and rejected at the design stage, not merely deprioritized.
`AG-003` produces exactly six output kinds (`OUTPUTS.md`); "authorize a
new Investigation" is not one of them — a Gap Report only *names* a
candidate investigation, per `CURATION-PROTOCOL.md`'s own restraint
rule. Specifying this as an execution pilot would require inventing
either a new output kind or a new authorizing mechanism, which
`ARCH-003`'s Critical Rules explicitly forbid ("Не измисляй нови
компоненти"). Listed here to show it was considered, not overlooked.

## Ranking

| Candidate | Risk | Complexity | Value | Measurability | Reversibility | Rank |
|---|---|---|---|---|---|---|
| **C1 — `CPP-S3-01`** | Low | Low | High | High | High | **1st** |
| C2 — `KMP-S3-01` | Moderate | Higher | Moderate | Moderate | Moderate | 2nd |
| C3 — `REL-S2-01` | Moderate | Moderate–High | Moderate | Moderate | Moderate | 3rd |
| C4 — `REL-S4-01` | Moderate–High | Moderate–High | Lower | Moderate | Moderate | 4th |
| C5 — Investigation authorization | — | — | — | — | — | Rejected — would require a new component |
