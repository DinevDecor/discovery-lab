# Internal Adversarial Review ADVERSARIAL-REVIEW-0001 — AG-003 Architecture

Subject: the AG-003 Knowledge Curator architecture in full
(`../../ai-organization/employees/AG-003-knowledge-curator/`), tested
against this walkthrough (`../AG-003-knowledge-curator-walkthrough/`) as
its concrete case. Conducted per the requesting task's own completion
condition: *"Return: PASS / PARTIAL / BLOCKED only after the
architecture survives an internal adversarial review."*

**Reviewer stance**: this review was conducted by the same session that
designed the architecture, immediately after design — not by an
independent Reviewer, human or AI. This is disclosed, not hidden: a
genuinely independent review would be stronger, and this is recorded as
an explicit residual gap below, not smoothed over. What follows is a
real attempt to find actual weaknesses, not a formality.

## Findings — fixed during this review

1. **`confidence` had no reproducible formula.** The first draft of
   `KNOWLEDGE-OBJECT-SPEC.md` described `confidence` only qualitatively
   (three "visible factors"), and the walkthrough's `KO-0001` asserted
   `0.55` without showing how that number was reached — two curators
   given the same inputs could not have reproduced it. **Fixed**: a
   concrete multiplicative formula
   (`citation_factor * diversity_factor * contradiction_factor`) was
   added to `KNOWLEDGE-OBJECT-SPEC.md`, and `KO-0001` was recalculated to
   `0.4` to match. The formula's own weights are flagged as this
   design's own invented starting point, not external precedent —
   consistent with how `PROMOTION-RULES.md` already flags its 90-day
   threshold.
2. **Merge reversibility was asserted, not mechanized.** `OUTPUTS.md`'s
   first draft claimed a Knowledge Merge Proposal is "reversible by
   construction" without specifying what data would actually let a human
   split a merged object back into its parts — pooling two objects'
   `provenance` lists into one, with nothing marking which entry came
   from which original object, would make an exact reversal impossible
   once the merge had happened. **Fixed**: `OUTPUTS.md` and
   `LIFECYCLE.md` now require a `merged_from_ko` tag on every carried-over
   `provenance` entry, which is what actually makes reversal possible,
   not just claimed.
3. **`derived_from` was defined twice with no stated relationship between
   the two definitions.** `KNOWLEDGE-OBJECT-SPEC.md` used `derived_from`
   both as a top-level lineage field and, via `RELATIONSHIP-ONTOLOGY.md`,
   as one of the seven relationship-graph edge types — with no rule for
   whether accepting one should update the other. Left unresolved, this
   would have let the two silently drift apart on any real Knowledge
   Base of nontrivial size. **Fixed**: `KNOWLEDGE-OBJECT-SPEC.md` now
   states explicitly that the two are deliberately not kept in sync,
   with a one-line test for which field a reader should consult for
   which question.

## Findings — recorded as open, not fixed here

4. **`maturity: Convergent`'s "independent source" test is exploitable.**
   `KNOWLEDGE-OBJECT-SPEC.md` requires two independent Recovery Reports
   *or* two independent AG-002 runs to reach `Convergent`. Nothing in
   this architecture stops a second AG-002 run from re-scanning the same
   diary archive a second time and counting as a second "independent
   run" under a literal reading — which would let `maturity` (and
   therefore promotion eligibility) inflate without any genuinely new
   evidence. This is a real loophole, not a hypothetical one: AG-002's
   own history already shows re-runs happening in practice
   (`MIRROR-VERIFY-0001`, `REALITY-VERIFY-0001`,
   `PILOT-RUN-0002`'s own two-session structure). **Left open**: closing
   it properly needs a notion of source identity (a content hash or
   equivalent, which `reality-inbox/manifests/` already tracks per file)
   distinguishing "a second run over new material" from "a second run
   over the same material" — worth a v0.2 revision to
   `KNOWLEDGE-OBJECT-SPEC.md`, not designed here to keep this pass
   focused on the architecture the task actually asked for.
5. **The `Validated → Core` numeric threshold (90 days / 3 runs) is
   admittedly invented.** Already flagged in `PROMOTION-RULES.md` itself
   at time of writing, restated here because an adversarial review
   should not let a self-flagged gap count as resolved just because it
   was disclosed. No Knowledge Object in the current walkthrough gets
   close to this threshold, so it has not been exercised even once.
6. **Shared `CI-NNNN` numbering with AG-002 has no allocation mechanism.**
   `OUTPUTS.md` and `STATUS.yaml` both state Candidate Investigations
   continue AG-002's existing sequence rather than starting a competing
   one — correct in principle, but nothing in either Role's architecture
   actually prevents two concurrent sessions (one running AG-002, one
   running AG-003) from independently minting the same next number. This
   walkthrough's own `GAP-0001` avoided the problem by minting none — a
   real test of collision handling did not occur. **Left open**,
   recorded in `STATUS.yaml`'s `open_governance_questions`.
7. **`GAP-0001`'s "zero-degree node" claim is asserted, not computed.**
   The walkthrough built exactly one full `KO-NNNN` (`KO-0001`); `RI-13`
   and `RI-18`'s isolation was determined by a human-style read of
   `PILOT-RUN-0002-recovery-report.md`, not by actually constructing
   Knowledge Objects for all 19 organizational findings and computing
   graph degree. The claim is very likely correct on inspection, but this
   walkthrough does not prove it the way a real Knowledge Base with a
   real relationship graph would. Recorded honestly rather than
   presented as more rigorous than it is.
8. **This repository now has four distinct senses of "Review"** — KOD's
   Under Review, generative-discovery-engine's Critical Review, ORB
   Review, and this Role's Knowledge Review. Each is disambiguated in
   its own governing document, but four overlapping terms is a real,
   accumulating cognitive load on any future contributor, not fully
   solved by writing four separate disambiguation notes. Accepted as a
   trade-off of adding a fourth necessarily-distinct process, not treated
   as fixable within this task's scope.
9. **This review is not independent.** Stated at the top, repeated here
   for emphasis: the design session and the review session are the same
   session. Every finding above is real, but a genuinely independent
   Reviewer — human or a different AI Executor — could plausibly find
   issues this review missed precisely because it was not looking with
   fresh eyes. A first genuine, independent Knowledge Review of AG-003's
   own architecture (not merely of a future proposal it produces) is not
   something this Role's own `REVIEW-PROTOCOL.md` currently covers —
   `REVIEW-PROTOCOL.md` reviews AG-003's *proposals*, not AG-003's *own
   design*. That would be ORB's territory in principle (conduct/design
   review of a Role), but no ORB Review of AG-003 has been requested or
   performed.

## Verdict

**APPROVE WITH OPEN ITEMS** — not a clean pass, and not blocked. Three
concrete design defects (findings 1–3) were found and fixed during this
review, which is itself evidence the review was substantive rather than
pro forma. Four further gaps (findings 4, 6, 7, 8) are real and
recorded, not fatal to a DRAFT/Prototype architecture whose own
`CONTRACT.md` already states no run has occurred. Finding 5 is a
self-disclosed placeholder, unexercised. Finding 9 — the review's own
lack of independence — is the most important one to carry forward: a
future genuine ORB or human review of this Role's design, not just of
its future output, is recommended before any promotion past Prototype.

## Provenance

This review's subject is the full AG-003 document set and this
walkthrough folder, both created in this same task. Its factual claims
about AG-002's history (re-runs, `CI-4`/`CI-5`) trace to
`../../ai-organization/employees/AG-002-discovery-archaeologist/
HISTORY.md` and `runs/PILOT-RUN-0002-recovery-report.md`.
