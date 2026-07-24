# AI Organization — Hiring Lifecycle (DRAFT)

**Status: DRAFT — candidate lifecycle only, not adopted, not binding on
any Role until a human decision applies it.**

## Candidate stages

```
Candidate → Prototype → Probation → Trusted → Retired
```

No `Senior` or `Architect` tier is defined at this time, because there
is no evidence yet that either is necessary — adding them now would be
the same premature-abstraction error `PROP-0001` already identified and
avoided elsewhere in this repository. Additional tiers may be proposed
later, but only in response to an actual demonstrated need, not
speculatively.

- **Candidate** — a Role exists only as a proposed idea; no files have
  necessarily been written yet.
- **Prototype** — the Role's full document set exists (contract, role
  definition, inputs, outputs, limitations, checklist, metrics, run
  protocol, prompt, status, history), but it has not yet been run for
  real. This is AG-001's current stage.
- **Probation** — the Role has been run for real, a defined number of
  times, and its output is under active independent review.
- **Trusted** — the Role has passed probation review and a human has
  explicitly approved advancing it.
- **Retired** — the Role is no longer active. Its files and registry
  entry are preserved, not deleted, for provenance.

## Requirements to move between stages

Every transition, in either direction, requires all of the following
before it may be recorded:

1. A defined number of real runs completed (the specific number is set
   per-Role, not fixed globally by this document).
2. Independent review of a sample of the resulting reports — someone
   other than the Role's own Executor checking the reports for accuracy
   and boundary compliance.
3. A documented account of any gaps and false positives found during
   that review, however small.
4. An explicit human decision to advance (or not advance) the Role.
5. A recorded reason for the decision, kept as part of the Role's own
   `HISTORY.md`.

No transition may be recorded on the basis of run volume alone, and no
transition may be recorded without a human decision — an AI executor
completing runs is not sufficient by itself to advance its own role's
status.

## Who may run the process, and who may not decide it

Discovery Lab may design and conduct the review process described above
— proposing what to check, running the sample review, and drafting a
recommendation. Discovery Lab must not, on its own, declare any Role
`Trusted`. That decision belongs to a human, following Discovery Lab's
own Principle 0 ("Discovery Lab never creates truth... Discovery Lab
itself never accepts, finalizes, or applies any of these proposals").

## Open governance question

**Who holds the final authority to appoint a Role — to move it from
Candidate to Prototype, or to approve a Trusted promotion — across the
DinevDecor ecosystem as a whole, is not decided by this document.** This
is recorded as an explicit open question, not resolved here, and not
assumed to default to any particular repository or person.

## Retirement

A Retired Role's folder and registry entry are kept exactly as they were
at retirement, for provenance — nothing is deleted. A retirement, like
any other transition, requires a recorded human decision and reason.
