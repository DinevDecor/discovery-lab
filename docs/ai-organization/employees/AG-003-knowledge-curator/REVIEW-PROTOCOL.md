# Review Protocol — AG-003 Knowledge Curator (Knowledge Review)

**Status: FROZEN, as part of AG-003 v1.0** (`../../../releases/1.0/
RELEASE-1.0.md`).
Version 1.0. Date: 2026-07-24 (drafted); frozen 2026-07-24.

## What Knowledge Review is

**Knowledge Review is not a new employee.** Like ORB
(`../../ORB/ORB-PROTOCOL.md`), it has no Employee ID, no `CONTRACT.md`,
no assigned Executor of its own, and does not appear under
`../../employees/`. It is an **organizational process** — a defined,
repeatable procedure for independently checking whether a specific
AG-003 proposal or report is sound, before a human decides what to do
with it.

## Why this exists, and why it is not ORB

`CONTRACT.md`'s Review Protocol section requires AG-003's proposals to
be reviewable, but ORB reviews **conduct** — whether an employee's run
followed its own contract (`../../ORB/ORB-PROTOCOL.md`, "What ORB
reviews, and what it does not"). A Knowledge Merge Proposal or a Core
Principle Proposal can be conduct-compliant (every rule in `ROLE.md` was
followed) while still being wrong on the merits — two Knowledge Objects
that look like duplicates might genuinely not be, or a promotion
threshold might be met on paper while the underlying evidence is
thinner than it looks. Knowledge Review checks the **content** of a
proposal; ORB, separately and additionally, may still review AG-003's
**conduct** in producing it. The two are complementary, not
substitutes — a single proposal could, in principle, receive both.

## Who may conduct a review — "the Knowledge Reviewer"

Any human, or any AI Executor **other than** the Executor who produced
the proposal under review. Independence is a hard requirement, matching
ORB's own rule and the same actor-independence discipline
`../../../proposals/PROP-0001-discovery-lab-boundaries.md` describes for
generative-discovery-engine. "Knowledge Reviewer" is a procedural
function, not an organizational Role — no Employee ID, no `CONTRACT.md`
of its own.

## The six mandatory questions

Every Knowledge Review must answer all six, in this order:

1. **Does every claim in the proposal trace to a real, checkable
   citation** in the named Recovery Report(s)?
2. **Does the proposal invent anything** — a fact, a date, a
   relationship, a confidence value — not actually present in its cited
   sources?
3. **Is the chosen action (merge / relationship / promotion /
   contradiction / gap) still only a proposal**, or has AG-003 acted on
   it directly somewhere in the repository?
4. **For a Relationship Proposal**: does the stated type survive the
   disambiguation table in `RELATIONSHIP-ONTOLOGY.md` against every
   confusable alternative?
5. **For a Core Principle Proposal**: does the evidence actually meet
   the specific threshold in `PROMOTION-RULES.md` for the one step
   proposed — no more, no less?
6. **Does this proposal, or the reasoning inside it, surface something
   that belongs in a separate Investigation** rather than being decided
   inside this review?

No question may be skipped. If a question cannot be meaningfully
answered from the available evidence, the correct verdict is
`INSUFFICIENT EVIDENCE`, not a guess and not an omission — the same
discipline `../../ORB/ORB-PROTOCOL.md` already holds itself to.

## Procedure

1. **Select the subject.** Name the specific proposal or report being
   reviewed (its ID, e.g. `KMP-0001`) and the Knowledge Object(s) it
   concerns. A review with no named subject is not valid.
2. **Confirm reviewer independence.** The Knowledge Reviewer records, in
   the review itself, that they did not produce the proposal under
   review.
3. **Read the standard.** The Reviewer reads `KNOWLEDGE-OBJECT-SPEC.md`,
   `RELATIONSHIP-ONTOLOGY.md`, `PROMOTION-RULES.md`, and `OUTPUTS.md` —
   whichever apply to the proposal's kind — as the fixed standard.
4. **Read the cited Recovery Report(s)** the proposal claims to derive
   from, in full, not only the excerpted quotation inside the proposal.
5. **Answer all six questions**, each with a verdict (`SOUND`,
   `UNSOUND`, or `INSUFFICIENT EVIDENCE`) and a citation-backed
   explanation.
6. **File the completed review** at `../../../proposals/
   AG-003-knowledge-curator-walkthrough/reviews/KR-NNNN-<subject-slug>.md`
   once a first real review exists to put there (a `reviews/` directory
   is not created speculatively, matching ORB's and AG-001's own
   precedent of not creating a `runs/`-style directory before it is
   needed).
7. **Record the outcome.** A Knowledge Review's verdict is itself only a
   recommendation — nothing is final until a human acts on it, exactly
   as ORB's own reviews and AG-002's Recovery Queue already work. A
   human may accept, reject, or defer the underlying proposal regardless
   of the review's verdict, though doing so against a Knowledge Review's
   explicit `UNSOUND` finding should itself be recorded, not silent.

## Boundaries this procedure must never cross

- A Knowledge Review never modifies the proposal it reviews, the
  Knowledge Object(s) it concerns, or any Recovery Report.
- A Knowledge Review never itself changes a `status` field, executes a
  merge, or accepts a relationship — it recommends; a human decides.
- A Knowledge Review never modifies `../../employees/
  AG-003-knowledge-curator/`'s own governing files (`ROLE.md`,
  `CONTRACT.md`, etc.) — exactly as ORB never modifies AG-001's or
  AG-002's.

## Disambiguation note

"Review" now has **four** distinct senses in this ecosystem, not three —
`../../ORB/ORB-PROTOCOL.md`'s own Disambiguation note already lists
KOD's "Under Review" (validates a KOD knowledge claim), generative-
discovery-engine's Critical Review (stress-tests a discovery method
before validation), and ORB Review (checks an employee's conduct on a
run against its own contract). **Knowledge Review**, defined here, is
the fourth: it checks whether a specific AG-003 **proposal's content** —
not an employee's conduct, not a KOD claim, not a discovery method — is
evidentially sound before a human acts on it. None of the four is a
substitute for any other, and this document claims no authority over
the other three.
