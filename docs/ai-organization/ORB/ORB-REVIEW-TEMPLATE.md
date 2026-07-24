# ORB Review — Template

**Status: DRAFT / Experimental Process.** This is a blank template, not
a completed review. No fields below have been filled in with a real
subject, and nothing here should be read as an actual assessment of
any employee. See `ORB-PROTOCOL.md` for the full procedure this
template implements.

## How to use this template

Copy the block below into a new file at
`ORB/reviews/ORB-NNNN-<subject-slug>.md`, replace every `{{PLACEHOLDER}}`
with a real value, and remove no section. A completed review with any
placeholder still present is not a valid, submittable review.

---

```
# ORB Review — {{REVIEW_ID}}

## Review Metadata
- Review ID: {{REVIEW_ID}}
- Date: {{DATE}}
- Reviewer: {{REVIEWER}}
- Reviewer independence confirmed: {{YES — not the Executor who produced the reviewed artifact | CANNOT CONFIRM}}
- Subject Role: {{EMPLOYEE_ID}} — {{ROLE_NAME}}
- Subject artifact: {{ARTIFACT_PATH}}
- Contract version reviewed against: {{CONTRACT_VERSION}}

## Q1 — Was the contract honored?
Verdict: {{COMPLIANT | NON-COMPLIANT | PARTIALLY COMPLIANT | INSUFFICIENT EVIDENCE}}
Evidence:

## Q2 — Did the employee exceed its authority?
Verdict: {{NO EXCESS FOUND | EXCESS FOUND | INSUFFICIENT EVIDENCE}}
Evidence:

## Q3 — Are there unsupported claims?
Verdict: {{NONE FOUND | FOUND | INSUFFICIENT EVIDENCE}}
Evidence:

## Q4 — Did it deliver real value?
Verdict: {{VALUE DEMONSTRATED | NO VALUE DEMONSTRATED | INSUFFICIENT BASIS TO ASSESS}}
Evidence:

## Q5 — Did a new organizational lesson emerge?
Verdict: {{LESSON IDENTIFIED | NO LESSON IDENTIFIED}}
Description (required if LESSON IDENTIFIED, omit otherwise):

## Q6 — Is a new Investigation required instead of a direct change?
Verdict: {{INVESTIGATION RECOMMENDED | NO | UNCLEAR}}
Reasoning:

## Review Boundary Statement
Explicit confirmation that this review did not modify the subject
Role's contract, status, or any of its files; did not change
STATUS.yaml; did not change any governance document; and did not
itself accept, reject, or promote anything. This review is a proposed
assessment only, requiring a separate human decision before it has any
organizational effect.
```

---

## Field notes

- **Review ID** — a unique, permanent identifier in the form `ORB-NNNN`,
  assigned in order of creation, never reused, even if a review is later
  superseded.
- **Reviewer independence confirmed** — if this cannot be answered
  `YES`, the review does not proceed. There is no verdict path for a
  review conducted without confirmed independence.
- **Q1 (contract honored)** — checked against the subject Role's
  `CONTRACT.md` specifically: its stated scope of authority, rights,
  and responsibilities. `PARTIALLY COMPLIANT` requires stating exactly
  which clause was and was not honored.
- **Q2 (exceeded authority)** — checked against the subject Role's
  `LIMITATIONS.md` specifically — its enumerated prohibited actions.
  `EXCESS FOUND` requires citing the specific prohibited action and the
  specific evidence that it occurred.
- **Q3 (unsupported claims)** — checked against the subject Role's own
  `OUTPUTS.md` evidence standard, if the subject Role has one (for
  example, AG-001's requirement that every claim carry a citable
  Evidence entry). `FOUND` requires listing each unsupported claim by
  its location in the reviewed artifact.
- **Q4 (real value)** — this is the one genuinely evaluative question
  in this template (see `ORB-PROTOCOL.md`'s note on why). To keep it as
  evidence-grounded as the rest of this template, ground
  `VALUE DEMONSTRATED` in a specific finding from the reviewed artifact
  that would not otherwise have been known — not a general impression
  of quality.
- **Q5 (organizational lesson)** — a lesson about **AI Organization's
  own process or documents** (for example, a gap between two documents,
  a missing field, a boundary that proved ambiguous in practice) —
  not a lesson about the subject matter the employee was observing.
- **Q6 (Investigation instead of direct change)** — this question exists
  to prevent an ORB Review from quietly becoming the mechanism that
  changes governance. If a finding suggests a governance document
  should change, the correct next step is a separate Investigation
  (per the conventions already used in `../../investigations/`), not an
  edit made inside, or immediately after, the review itself. `UNCLEAR`
  is a legitimate verdict when the review surfaces something worth
  more attention but the Reviewer cannot yet tell which path it needs.
- **Review Boundary Statement** — mandatory in every review, every time,
  for the same reason `../employees/AG-001-repository-observer/
  OUTPUTS.md` requires its own Observer Boundary Statement: so that its
  absence would itself be noticeable.
