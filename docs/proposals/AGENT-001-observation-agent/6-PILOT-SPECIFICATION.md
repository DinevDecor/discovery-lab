# Deliverable 6 — Pilot Specification

## Recommended pilot

**A single, human-invoked run of the Observation Model
(`2-OBSERVATION-LOOP.md`) applied to `discovery-lab` itself**, with two
concrete, already-identified subjects: (1) re-verify and correct-by-
recommendation the `AG-001/STATUS.yaml` vs. `HISTORY.md` mismatch this
proposal already found; (2) re-express `DL-001`'s own five real
findings in the new 7-field Observation Model schema, to test whether
the schema captures at least as much as `DL-001`'s manual `C1`/`C2`/`C3`
format did.

## Why this pilot, specifically

- **Requires no new governance**: uses `AG-001`'s already-`Prototype`,
  real-run-tested observation discipline and `PROP-0001`'s already-
  `ACCEPTED` evidence rules — nothing here needs a new ADR or Proposal
  accepted first.
- **Requires no execution runtime**: human-invoked, exactly like every
  other real task in this session including `DL-001` and `DL-002`
  themselves — does not depend on `3-EVENT-CLASSIFICATION.md`'s named
  trigger gap being closed first.
- **Reversible**: read-only; the pilot's only possible output is a
  Report and, if warranted, a Recommendation — nothing it produces can
  itself change any repository.
- **Measurable**: directly comparable against two existing baselines —
  `DL-001`'s five real findings (does the new schema reproduce them?)
  and `AG-001/RUN-0001`'s own report (does re-scoping to include a
  Recommendation step lose any of `AG-001`'s existing discipline?).
- **Produces objective evidence**: every observation carries a citation,
  per the schema's own `Evidence` field — no observation without one.

## What the pilot does not do

It does not test whether the agent can run unattended — `DL-002`
already established that no trigger mechanism exists to test this
against, and this pilot does not depend on one. It does not create the
agent's actual `CONTRACT.md`/`ROLE.md`/etc. — that remains a separate,
later Draft-stage decision, contingent on this pilot's own result. It
does not touch any repository outside `discovery-lab` — narrower than
`DL-001`'s own five-repository scope, deliberately, since the pilot's
purpose is to validate the *schema and loop*, not to re-run the full
Ecosystem Health Review.

## Procedure, in brief

1. Confirm access to `discovery-lab`'s current content (already
   available in this session).
2. Apply the Observation Model schema to the two named subjects above.
3. Produce one Report per `5-REPORTING-SPECIFICATION.md`'s format.
4. Route any Recommended Action through the same independent-reviewer
   pattern `EXEC-001` already used (a fresh, memoryless Agent
   instance) as the pilot's Formal Gate — with the same partial-
   independence caveat `EXEC-001/5-REVIEWER-RECORD.md` already names,
   not silently improved on here.
5. Present the Report and any Gate-passed Recommendation to a human for
   a real, dated decision — exactly `EXEC-001`'s own precedent.
6. Do not proceed past step 5 regardless of the decision — the pilot
   ends at Human, per the Observation Loop's own terminal property.

This procedure is not executed by this proposal — it is specified for
a human to authorize separately, consistent with "No implementation"
per this task's own Status.
