# Deliverable 3 — Complete Execution Specification

Per `ARCH-003` Phase 3. This is a **specification**, not an execution
log — per the task's own Definition of Done ("спецификация... която
може да бъде изпълнена," a specification that *can* be executed), no
step below has been carried out. Running it requires a human trigger
decision and a genuinely independent reviewer, both explicitly out of
scope for this document — see `8-GO-NO-GO-RECOMMENDATION.md`.

## Trigger

The pre-existing, real, already-filed Core Principle Proposal
`CPP-S3-01` (`docs/proposals/AG-003-reality-stress-test/
CURATION-0004.md`, lines 141–155), naming `KO-S3-01` for
`Draft → Candidate Principle`, filed 2026-07-24, never yet reviewed or
acted on. The pilot is triggered by a human (or delegate) deciding to
run the already-specified `REVIEW-PROTOCOL.md` process against this
specific, already-existing proposal — not by any new event, poll, or
schedule.

## Inputs

- `CPP-S3-01` itself (the proposal text).
- `KO-S3-01`'s current object definition, currently embedded inline in
  `CURATION-0004.md` (not yet a standalone file).
- The cited Recovery Report: `STRESS-RUN-0004-recovery-report.md`
  (`AG-002`, `FROZEN v1.0`).
- The governing specs, all `Status: FROZEN`:
  `KNOWLEDGE-OBJECT-SPEC.md`, `PROMOTION-RULES.md`, `REVIEW-PROTOCOL.md`,
  `OUTPUTS.md`, `RELATIONSHIP-ONTOLOGY.md` (not needed for this
  specific proposal kind, listed because `REVIEW-PROTOCOL.md`'s
  Procedure step 3 requires the Reviewer to read whichever of the four
  applies).

## Roles

Exactly the three ratified mechanisms, no others:

- **`AG-003` Knowledge Curator** (Contract-Defined Role, `FROZEN v1.0`)
  — already discharged its part; produced `KO-S3-01` and `CPP-S3-01`
  during the Reality Stress Test. No further `AG-003` action is
  required for this pilot.
- **Knowledge Reviewer** — a procedural function, not an organizational
  Role (`REVIEW-PROTOCOL.md` explicitly: "no Employee ID, no
  `CONTRACT.md` of its own"). Must be **any human, or any AI Executor
  other than the Executor who produced `CPP-S3-01`.** This is a live,
  named constraint on who may run the pilot — see
  `7-RISK-ASSESSMENT.md`.
- **Human Final Authority** — Petko Dinev, or an explicit delegate.
  Non-optional, non-simulatable: `REVIEW-PROTOCOL.md` states "nothing
  is final until a human acts on it" as an explicit rule, not a
  default.

## Gates

One Formal Gate: a **Knowledge Review**, per `REVIEW-PROTOCOL.md`.

1. Select the subject: `CPP-S3-01`, concerning `KO-S3-01`.
2. The Reviewer records their independence from the proposal's
   production.
3. The Reviewer reads `KNOWLEDGE-OBJECT-SPEC.md` and
   `PROMOTION-RULES.md` (the two specs applicable to a Core Principle
   Proposal) as the fixed standard.
4. The Reviewer reads `STRESS-RUN-0004-recovery-report.md` in full,
   not only `CPP-S3-01`'s excerpted citations.
5. The Reviewer answers all six mandatory questions
   (`REVIEW-PROTOCOL.md` §"The six mandatory questions"), each with a
   verdict of `SOUND`, `UNSOUND`, or `INSUFFICIENT EVIDENCE`.
6. The completed review is filed at
   `docs/proposals/AG-003-reality-stress-test/reviews/
   KR-0001-cpp-s3-01.md` — a new `reviews/` directory, created only now
   because a first real review exists to put in it, matching
   `REVIEW-PROTOCOL.md`'s own stated precedent (ORB and `AG-002` do not
   create their run-style directories speculatively either). Filed
   under the Reality Stress Test's own proposal directory, not the
   `AG-003-knowledge-curator-walkthrough` directory `REVIEW-PROTOCOL.md`
   names as an example path — that directory holds demonstration
   material only; this pilot's subject is real.
7. The review's verdict is recorded as a recommendation, per
   `REVIEW-PROTOCOL.md` §7 — "itself only a recommendation — nothing is
   final until a human acts on it."

## Human approval

A short, dated **Human Decision** record, appended to or filed
alongside the Knowledge Review, stating one of: `Accept`, `Reject`, or
`Defer`, with the deciding human named. `PROMOTION-RULES.md`'s higher
bar (an ADR-style ratification entry) applies only at
`Validated → Core Principle`, a later threshold this pilot does not
reach — a short decision record is the correct weight for
`Draft → Candidate Principle`, per that document's own tiered
requirements.

## Execution

Only if the Human Decision is `Accept`:

1. Create `memory/knowledge-objects/` (does not yet exist — confirmed
   directly; this is the location `KNOWLEDGE-OBJECT-SPEC.md` and
   `OUTPUTS.md` already specify, not a new one).
2. Write `memory/knowledge-objects/KO-S3-01.md`, containing the
   `KO-S3-01` YAML block exactly as it appears in `CURATION-0004.md`,
   with exactly one field changed: `status: Candidate Principle`
   (was `Draft`). A short prose note beneath the block records the
   promotion — citing `CPP-S3-01`, the Knowledge Review's file path,
   and the Human Decision — in the same prose-under-YAML convention
   `CURATION-0004.md` itself already uses for `KO-S3-01`'s Finding F-2.
3. No other file is modified. `CURATION-0004.md`, the Recovery Report,
   and every other existing artifact remain untouched — a Knowledge
   Review "never modifies the proposal it reviews, the Knowledge
   Object(s) it concerns, or any Recovery Report"
   (`REVIEW-PROTOCOL.md` §"Boundaries").
4. The Executor who performs this write is **not required to be
   `AG-003`** — `PROMOTION-RULES.md` is explicit that a met threshold
   "is inert until a human accepts it," meaning the write is a
   mechanical filing action following an already-made decision, not a
   further curatorial judgment. No Role is named for this step because
   none is ratified for it in `Unified Coordination Model v1.0` — see
   `4-COMPONENT-MAPPING.md`'s note on this being, deliberately, the
   pilot's narrowest possible test of `ARCH-002`'s `G1` gap.

If the Human Decision is `Reject` or `Defer`: no file is created;
`KO-S3-01`'s `status` remains `Draft`; the Knowledge Review and Human
Decision records are still filed, as evidence the gate operated.

## Outputs

- `docs/proposals/AG-003-reality-stress-test/reviews/
  KR-0001-cpp-s3-01.md`
- The Human Decision record
- (If accepted) `memory/knowledge-objects/KO-S3-01.md`

## Evidence produced

See `5-EVIDENCE-COLLECTION-PLAN.md`.

## Success criteria / Failure criteria / Rollback procedure

See `6-SUCCESS-METRICS.md` and `7-RISK-ASSESSMENT.md`. Rollback, in
summary: every artifact this pilot can produce is a **new** file — no
existing ratified artifact is ever edited. A `git revert` of the
pilot's commit removes all three possible new files with zero effect
on anything else in the repository.
