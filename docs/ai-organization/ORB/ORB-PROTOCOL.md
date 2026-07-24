# ORB — Organizational Review Board — Protocol

**Status: DRAFT / Experimental Process.** Version v0.1. Date: 2026-07-24.

## What ORB is

**ORB is not a new employee.** It has no Employee ID, no entry in
`../EMPLOYEE-REGISTRY.md`, no `CONTRACT.md`, no assigned Executor of its
own, and does not appear anywhere under `../employees/`. It is an
**organizational process** — a defined, repeatable procedure for
independently reviewing how an AI employee's specific run or output
actually performed, against that employee's own contract.

**Naming note.** "ORB" is used here as **Organizational Review Board**.
This expansion is this prototype's own naming choice — it was not
stated in the instruction that requested this directory, and is
recorded here as an interpretation, not a confirmed fact.

## Why this exists

`../HIRING-LIFECYCLE-DRAFT.md` already requires, for every stage
transition any Role goes through, "independent review of a sample of
the resulting reports — someone other than the Role's own Executor
checking the reports for accuracy and boundary compliance," alongside a
documented account of gaps and false positives, and an explicit human
decision. That document names the requirement but does not define how
such a review is actually conducted. **ORB-PROTOCOL.md is that
definition.** It does not modify `../HIRING-LIFECYCLE-DRAFT.md` — it
implements a step that document already requires, without changing a
word of it.

## Who may conduct a review — "the Reviewer"

Any human, or any AI Executor **other than** the Executor who performed
the run under review. Independence between conduct and review is a hard
requirement, not a preference — the same discipline
`../../proposals/PROP-0001-discovery-lab-boundaries.md` already
describes for `generative-discovery-engine`'s own actor-independence
rules.

**"Reviewer" is a procedural function, not an organizational Role.**
Performing a review does not require an Employee ID, does not create
one, and does not make the Reviewer a new employee of AI Organization.
There is no `CONTRACT.md` for "the Reviewer" — this document is the
only governing text for that function.

## What ORB reviews, and what it does not

ORB reviews **conduct**: whether a specific completed run, by a specific
employee, actually followed that employee's own `CONTRACT.md`,
`ROLE.md`, and `LIMITATIONS.md` (where the reviewed employee is
AG-001-shaped; the same principle applies to any future Role's
equivalent documents).

ORB does **not** review whether the employee's own contract, role
definition, or metrics are good architecture. Evaluating or changing a
Role's own defining documents is a governance action, and governance is
explicitly out of ORB's scope (see Explicit Prohibitions below). ORB
takes the contract as given and asks only whether conduct matched it.

## The six mandatory questions

Every ORB Review must answer all six, in this order, using
`ORB-REVIEW-TEMPLATE.md`:

1. **Was the contract honored?**
2. **Did the employee exceed its authority?**
3. **Are there unsupported claims?**
4. **Did it deliver real value?**
5. **Did a new organizational lesson emerge?**
6. **Is a new Investigation required instead of a direct change?**

No question may be skipped. If a question cannot be meaningfully
answered from the available evidence, the correct verdict is
`INSUFFICIENT EVIDENCE` (or the equivalent for that question — see
`ORB-REVIEW-TEMPLATE.md`), not a guess and not an omission.

Questions 1–3 are compliance-shaped: they check the reviewed run
against fixed, already-written rules (the contract, the limitations,
and the evidence standard the reviewed employee itself claims to
follow), and should be answerable primarily by citation. Question 4 is
evaluative by nature — ORB is deliberately permitted to judge whether a
run produced real value, which is different from AG-001's own strict
"observe only, never decide" mandate, because judgment is the entire
reason ORB exists. Questions 5 and 6 look outward from the specific run,
toward the organizational model itself and toward whether a finding
deserves a fuller, separate Investigation rather than being acted on
directly inside this review.

## Procedure

1. **Select the subject.** Name the specific employee (by Employee ID)
   and the specific artifact being reviewed — one run, one report, or a
   clearly bounded set of them. A review with no named subject is not
   valid.
2. **Confirm reviewer independence.** The Reviewer records, in the
   review itself, that they are not the Executor who produced the
   reviewed artifact. If this cannot be confirmed, the review does not
   proceed.
3. **Read the standard.** The Reviewer reads the subject employee's
   `CONTRACT.md`, `ROLE.md`, and `LIMITATIONS.md` in full — these are
   the fixed standard the review is conducted against, not something
   the review may reinterpret.
4. **Read the artifact.** The Reviewer reads the specific run or report
   under review in full, including its own stated evidence.
5. **Answer all six questions**, each with a verdict from the fixed
   vocabulary in `ORB-REVIEW-TEMPLATE.md` and a citation-backed
   explanation. A verdict without evidence is not a valid answer.
6. **File the completed review.** Once conducted, a review is expected
   to be filed at `ORB/reviews/ORB-NNNN-<subject-slug>.md` (a
   `reviews/` directory is created only once a first real review exists
   to put in it — none is created by this document, matching the same
   discipline already used for `../employees/AG-001-repository-
   observer/runs/`, which was not created until `RUN-0001` actually
   ran).
7. **Register it.** The review is added as one row in
   `ORB-REGISTRY.md`. Entries are append-only — never edited or removed
   after being added, only superseded by a later review if one is
   conducted.

## Boundaries this procedure must never cross

- An ORB Review never modifies the reviewed employee's own files —
  `CONTRACT.md`, `ROLE.md`, `INPUTS.md`, `OUTPUTS.md`, `LIMITATIONS.md`,
  `CHECKLIST.md`, `METRICS.md`, `RUN-PROTOCOL.md`, `PROMPT.md`, or
  `STATUS.yaml` — under any circumstance, regardless of what the review
  finds.
- An ORB Review never changes a Role's status, and never edits
  `STATUS.yaml` directly. A status change remains a separate, explicit
  human decision, recorded with a reason, exactly as
  `../HIRING-LIFECYCLE-DRAFT.md` already requires — an ORB Review is
  evidence that decision can be based on, not the decision itself.
- An ORB Review never modifies any governance document —
  `../HIRING-LIFECYCLE-DRAFT.md`, `../ORGANIZATION-DRAFT.md`,
  `../EMPLOYEE-REGISTRY.md`, `../README.md`, or anything under
  `../../proposals/` or `../../investigations/`.

## Explicit prohibitions

ORB, as a process, does not:

- create new employees, or add rows to `../EMPLOYEE-REGISTRY.md`;
- modify AG-001 or any other Role's files;
- modify any governance document;
- automate itself — no scheduling, no trigger, no unattended execution;
  every review is conducted deliberately, once, by a named Reviewer;
- decide a status change on its own — that authority is not ORB's, per
  `../HIRING-LIFECYCLE-DRAFT.md`'s own "who may run the process, and
  who may not decide it" rule, which applies to ORB exactly as it
  applies to any other review activity Discovery Lab conducts;
- treat its own verdicts as accepted fact. An ORB Review's verdicts are
  a proposed assessment. Nothing in an ORB Review is final until a
  human acts on it — the same discipline Principle 0 already states for
  the rest of Discovery Lab ("Discovery Lab never creates truth... it
  only observes, compares, and identifies inconsistencies, and proposes
  next steps... Discovery Lab itself never accepts, finalizes, or
  applies any of these proposals" — `../../proposals/
  PROP-0001-discovery-lab-boundaries.md`).

## Disambiguation note

"Review" is used here in a third, distinct sense from two other uses
already present in this ecosystem:

- **KOD's "Under Review"** is a stage in a Research Session's own
  lifecycle (`Draft → Active Investigation → Ready for Evaluation →
  Under Review → Accepted/Rejected/Archived`), governed by KOD's own
  Research Guardian and Research Engine, and evaluates whether a
  **knowledge claim** is valid.
- **generative-discovery-engine's Critical Review** (`contracts/
  critical-reviewer.md`, `docs/critical-reviews/CR-NNNN`) evaluates
  whether a **discovery method** survives adversarial stress-testing
  before it may be validated.
- **An ORB Review** evaluates whether a specific **AI employee's
  conduct on a specific run** matched that employee's own contract. It
  makes no claim about knowledge, and no claim about discovery methods.

None of these three is a substitute for either of the others, and this
document claims no authority over KOD's or generative-discovery-
engine's own review processes.
