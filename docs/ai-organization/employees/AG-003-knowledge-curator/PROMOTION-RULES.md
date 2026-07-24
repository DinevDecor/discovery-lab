# Promotion Rules — AG-003 Knowledge Curator

Employee ID: **AG-003** · Role Name: **Knowledge Curator** ·
Status: **Prototype / DRAFT / EXPERIMENTAL / NOT ADOPTED** · Version:
**v0.1**

Governs Track 1 of `LIFECYCLE.md` — the `status` field. Every rule below
produces, at most, a Core Principle Proposal (`OUTPUTS.md`). **No rule
in this document ever changes a `status` field by itself.** Meeting a
threshold is necessary to justify filing a proposal; it is never
sufficient to act.

## Disambiguation note, read first

`../AG-002-discovery-archaeologist/runs/PILOT-RUN-0002-recovery-report.md`
(RI-10) recovered KOD's own "Evidence Ladder" — `Observation → Pattern →
Independent Convergence → Candidate Principle → Validated Principle,
never skip levels` — from `KOD Research Protocol v1.0`, a document
belonging to a different project this repository has no access to. The
four-step ladder below (`Draft → Candidate Principle → Validated
Principle → Core Principle`) is **`discovery-lab`'s own**, named to match
the task that requested AG-003, not a copy or an implementation of
KOD's Ladder. The resemblance (both apply a strict "never skip levels"
discipline to how much a claim should be trusted before more evidence
accumulates) is a real, independently-arrived-at convergence worth
noting — RI-10's own "Convergence Mode" would call this exactly the kind
of pattern worth flagging — but AG-003 does not read, extend, or take
direction from KOD's Ladder. It is cited here only as related, recovered
context, per `ROLE.md`'s Terminology note.

## One step at a time

A Core Principle Proposal names exactly one transition — never
`Draft → Validated Principle` in a single proposal, even if the evidence
looks strong enough to justify skipping. If the evidence supports more
than one step, file the proposals sequentially (a second proposal may be
filed immediately after the first is accepted), not as one combined
claim.

## Threshold: `Draft → Candidate Principle`

All of the following must hold:

- `occurrences >= 2` in `provenance`.
- The two-or-more occurrences are **not** the same sentence quoted
  twice — they are distinct citations (distinct dates, or distinct
  Recovery Report entries) that AG-002 itself recorded as separate.
- `maturity` is at least `Recurring`.
- No open Contradiction Report names this Knowledge Object.

This is the lowest bar — it proposes only that the idea is worth
formally tracking as a candidate, not that it is validated.

## Threshold: `Candidate Principle → Validated Principle`

All of the `Draft → Candidate` conditions, plus:

- `maturity` is at least `Convergent` — the occurrences span **at least
  two independent sources or two independent Recovery Report runs**, not
  just multiple restatements within one archive scanned once. (A single
  diary scanned in one AG-002 run, however many times an idea repeats
  inside it, is one independent source — see the RT-3 worked example in
  `../../../proposals/AG-003-knowledge-curator-walkthrough/`, which
  meets `Draft → Candidate` but explicitly does not yet meet this bar.)
- At least one Knowledge Review (`REVIEW-PROTOCOL.md`) has examined the
  proposal and the reviewer is independent of whoever curated it.
- No `INSUFFICIENT EVIDENCE`-marked tension from AG-002 remains
  unaddressed against this specific claim.

## Threshold: `Validated Principle → Core Principle`

All of the `Candidate → Validated` conditions, plus:

- `maturity` is `Entrenched` — `Convergent`, sustained across a minimum
  span of independent recovery. This design sets that span at **90 days
  of first_seen-to-last_seen range, or three separate AG-002 runs,
  whichever the available evidence can show** — a placeholder threshold,
  explicitly flagged as a number invented for this architecture, not
  derived from any external precedent, and open to human revision before
  any real proposal relies on it.
- An explicit, recorded human ratification exists (a decision entry, in
  the spirit of an ADR, not merely a Knowledge Review sign-off) — Core
  Principle is the highest standing a Knowledge Object can hold in this
  Role's architecture, and this document requires the strongest gate to
  match.

## What "promotion is never automatic" means concretely

- AG-003 may compute that a threshold is met. It may not, on that basis
  alone, write a new `status` value anywhere — not in a Knowledge
  Object's own file, not in a Registry.
- The only artifact a met threshold produces is a Core Principle
  Proposal (`OUTPUTS.md`), which itself is inert until a human accepts
  it (or until a Knowledge Review recommends acceptance and a human
  ratifies that recommendation, per `REVIEW-PROTOCOL.md`).
- A rejected or deferred Core Principle Proposal does not lower
  `maturity` or otherwise penalize the Knowledge Object — it simply
  means `status` does not change this round.

## Relationship to other documents

Thresholds here read `maturity` and `occurrences` as defined in
`KNOWLEDGE-OBJECT-SPEC.md` and `LIFECYCLE.md`. The proposal format these
thresholds feed is `OUTPUTS.md`'s Core Principle Proposal. Review of a
filed proposal is `REVIEW-PROTOCOL.md`.
