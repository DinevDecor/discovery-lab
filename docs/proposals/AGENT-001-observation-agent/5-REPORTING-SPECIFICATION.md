# Deliverable 5 — Reporting Specification

Extends `AG-001/OUTPUTS.md`'s report format (not reviewed in full here,
cited as precedent) and `DL-001`'s own working dashboard structure
(exercised for real, once) with the fields needed to track findings
*across* runs — a genuinely new formal requirement, since both prior
precedents were one-shot. This is a bookkeeping delta-tracking
capability, not a new governance concept — it mirrors `PROP-0001`'s own
Recommendation Ledger design (`status`, `PENDING_NO_RESPONSE`,
never-infer-rejection-from-silence), specified there and reused here,
not reinvented.

## Report structure

```
# Observation Report <ID> — <date>

## Summary
One paragraph: scope of this run, how many observations, how many
MISMATCH/INSUFFICIENT_EVIDENCE found, headline finding if any.

## New Observations
Every observation from this run not seen in the immediately prior run
covering the same scope, in the full 7-field schema
(2-OBSERVATION-LOOP.md).

## Repeated Findings
An observation matching a prior run's MISMATCH that has not been
resolved — cites the prior report by ID and date. Never silently
dropped; a repeated finding is evidence the recommendation from the
prior run was not acted on (feeds the same acceptance_rate-style metric
PROP-0001 already specifies for its Ledger).

## Resolved Findings
A prior MISMATCH that this run's fresh evidence now shows as MATCH —
cites what changed and how it was verified, not assumed from the
absence of a re-check.

## Risk Changes
Any observation whose Confidence or apparent severity changed since the
last run on the same subject — new evidence either strengthening or
weakening a prior finding, stated plainly either direction.

## Confidence
Per observation, restated in aggregate: count of MATCH /
MISMATCH / INSUFFICIENT_EVIDENCE this run. No single aggregate score
across repositories or subjects — same explicit prohibition PROP-0001
states for Ecosystem Health Review v0.1, inherited here without
exception.

## Evidence Links
Every citation used in this report, collected in one place for
independent re-verification — mirrors KR-0001's own demonstrated
practice of checking every citation against source text before trusting
it.

## Recommended Actions
Every Recommendation from this run's observations, each already passed
through the Formal Gate before appearing here (2-OBSERVATION-LOOP.md
step 7) — never a raw, ungated suggestion.

## Human Decisions Required
An explicit list: which Recommended Actions are awaiting a decision,
carried over from prior reports if still undecided (never re-listed as
if new, never silently dropped if still pending).
```

## What this format does not do

It does not compute `PROP-0001`'s own forbidden single aggregate score.
It does not infer a Recommended Action's disposition from silence — an
unaddressed prior recommendation is reported as still-pending, exactly
matching `PROP-0001`'s `PENDING_NO_RESPONSE` discipline, never
collapsed into an assumed acceptance or rejection. It does not
auto-close a Repeated Finding after any fixed number of appearances —
`PROP-0001`'s own "anti-theater" caution (borrowed conceptually from
`project-memory`'s Kernel clause, `G2` §3) applies here too: a
Repeated Finding that keeps repeating is a signal about the review
process or the destination repository's responsiveness, not something
to quietly stop reporting.
