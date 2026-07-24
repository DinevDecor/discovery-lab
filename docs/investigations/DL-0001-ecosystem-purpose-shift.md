# DL-0001 — Ecosystem Purpose Shift

**Status: CANDIDATE HYPOTHESIS — not accepted, not verified, not tested.**
Type: Investigation (Discovery Lab candidate-hypothesis record — new "DL-"
series, distinct from the "INV-" series)
Date recorded: 2026-07-24
Custodian: Discovery Lab. This document is the sole place this idea is
recorded until it is verified, revised, or retired.

## What this document is not

- **Not an ADR.** No decision has been made about anything. Nothing here
  may be cited as an accepted architectural decision.
- **Not a specification.** Nothing here describes something to build.
- **Not a KOD Hypothesis object.** KOD's own Knowledge Domain defines
  "Hypothesis" as a specific, tracked Knowledge Object with its own
  lifecycle inside a Research Session (`KOD/Foundations/HYPOTHESIS.md`:
  "a proposed explanation, relationship or prediction that can be tested
  against reality"), registered in `KOD/Knowledge/HYPOTHESIS_REGISTRY.md`.
  This document does **not** create, modify, or imply an entry in that
  registry. The word "hypothesis" is used here only in the plain,
  colloquial sense — an unverified idea under consideration — per ground
  rule 1 of `docs/proposals/PROP-0001-discovery-lab-boundaries.md`, which
  requires exactly this kind of explicit disambiguation whenever
  Discovery Lab uses a word KOD already owns as a first-class concept. If
  this idea is ever formalized as a testable claim inside KOD's own
  Knowledge Domain, that is KOD's decision to make through its own
  process, not something this document does on KOD's behalf.
- **Not applied anywhere.** No other repository — KOD,
  generative-discovery-engine, trust-engine, or project-memory — was
  read, modified, or notified in the course of recording this. This
  document does not change, and does not propose changing, anything
  outside `discovery-lab`.
- **Not a revision of PROP-0001.** The mandate proposal, its
  recommendation, and its "Ecosystem Health Review v0.1" experiment are
  unaffected by this document. Nothing here is treated as new evidence
  for or against that recommendation.

## Origin

Recorded verbatim, as provided directly to this session on 2026-07-24,
attributed as the origin of the idea:

> During the architectural discussion that led to Discovery Lab's
> mandate, an unexpected observation emerged. We initially described the
> ecosystem as a knowledge-management architecture. While mapping the
> responsibilities of KOD, Trust Engine, Discovery Lab, Project Memory
> and Generative Discovery Engine, we observed that all of them
> ultimately contribute to improving decisions rather than accumulating
> knowledge. This observation was not a design goal but an inference
> drawn during the discussion.

No earlier or fuller record of this discussion exists in this
repository, `project-memory`, or any other repository inspected during
`INV-0002`. This paragraph is the entire known origin record. Nothing
about it has been elaborated, extended, or reinterpreted below beyond
what is stated in this section.

## The candidate hypothesis, stated precisely

**KOD, Trust Engine, Discovery Lab, Project Memory, and
generative-discovery-engine, despite differing in domain and mechanism,
may share a common terminal purpose — improving the quality of future
decisions — for which each repository's own primary output (knowledge,
trust scores, investigation findings, coordinated task state, validated
discovery methods) is an *instrumental* product, not the *terminal* one.**

Stated as a falsifiable claim: if this is true, every one of the five
repositories' own stated mission, read in its own words, should
ultimately terminate in language about choosing, selecting, deciding, or
acting — not merely about knowing, recording, or preserving.

## Arguments in favor

Grounded only in citations already gathered during `INV-0002` (plus one
already-known project-memory citation), not in new reading performed for
this document:

- **Trust Engine** states this almost exactly, in its own words:
  "The deeper purpose of Trust Engine is not prediction. It is
  selection." ... "This shifted the project from raw prediction tracking
  to context-aware model selection." (`trust_engine_foundation_review.md`,
  per `INV-0002` PASS C). Its entire pipeline terminates in "Future
  Selection," not in a knowledge store.
- **generative-discovery-engine** defines its own four-tier ladder as
  terminating in "a real business or scientific solution... confirmed
  independently of the method that proposed it" (`CONTEXT.md`) — i.e., a
  validated *method* is explicitly a means, not the end; the end is an
  actual outcome in the world, which implies a decision or action was
  taken on it.
- **KOD's own Knowledge Lifecycle** does not terminate at "Principle" —
  it continues: "...Principle → Decision → Outcome → New Observation"
  (`Core/KNOWLEDGE_LIFECYCLE.md`, per `INV-0002` PASS A). Knowledge, in
  KOD's own diagram, is not the last stage; Decision and Outcome come
  after it, and the cycle only closes by returning to Observation through
  an Outcome — implying the knowledge exists to be spent on a decision,
  not merely stored.
- **project-memory** describes its own `PROJECT_STATE.md` as covering
  "the collaboration control plane, active pilots, and **cross-project
  execution**" (`PROJECT_REGISTRY.md`, "Scope distinction") — execution
  and coordination of action across projects, not knowledge storage for
  its own sake.
- **Discovery Lab's own recommended mandate** (`PROP-0001`, Variant B)
  names its own principal failure mode as becoming "a passive audit
  archive nobody acts on" — i.e., Discovery Lab's own designers already
  treat an investigation's value as contingent on it changing a
  downstream decision, not on its being true in isolation.

## Arguments against / tension

An honest counter-reading of the same evidence, in the spirit of
`generative-discovery-engine`'s own Critical Reviewer discipline ("the
job is to find the reasons a method might be wrong"):

- **KOD's Constitution frames knowledge as having standing value
  independent of any decision.** Constitutional Principle C4 —
  "Preservation of Research History" — states that rejected hypotheses
  and failed predictions "are valuable knowledge and must never be
  erased," even though, by definition, a rejected hypothesis will never
  drive a future decision in its own right. If knowledge were purely
  instrumental to decisions, a permanently-rejected hypothesis would have
  no reason to be preserved once its decision-relevance is exhausted —
  yet KOD insists on preserving it anyway.
- **KOD's own mission statement is phrased in terms of knowledge and
  research integrity, not decisions**: "KOD does not protect ideas. KOD
  protects honest research" (`CONSTITUTION.md`); "Reality is the final
  arbiter of **knowledge**" (Principle C2) — the terminal noun in KOD's
  own founding language is knowledge, not decision. This does not
  disprove the hypothesis (a system can value knowledge's integrity while
  still ultimately deploying it toward decisions), but it means the
  hypothesis is, at best, a *reading* of KOD's structure rather than
  something KOD states about itself directly.
- **The observation covers only five repositories, selected because they
  were the ones already being discussed**, not because they were sampled
  to test this idea. `SketchUp-DDF` and `dinevdecor.github.io` — both
  known to exist in the same account (per
  `project-memory/notes/2026-07-19-dinev-decor-systems-location-check.md`)
  — were not considered at all, and may not fit the pattern.

## Potential impact if verified

Stated as conditional implications only — none of these are proposed,
decided, or acted on by this document:

- The ecosystem might be more accurately described, going forward, as a
  **decision-improvement architecture** with knowledge as an intermediate
  artifact, rather than as a "knowledge-management architecture" as
  originally assumed in the discussion that produced this observation.
- Discovery Lab's own `acceptance_rate` metric (defined, not implemented,
  in `PROP-0001`'s "Recommendation quality" section) would gain a
  sharper interpretation: an accepted proposal would represent a
  decision-improvement signal specifically, not merely a
  knowledge-correctness signal — a refinement to consider *if and when*
  that metric is ever actually implemented, not a change to make now.
- It could eventually be read as a mild argument for tighter, deliberate
  cross-repository awareness (since `INV-0002` found none of the five
  currently reference each other) — but this document does not propose
  that; it only names it as a possible future implication, for someone
  else to weigh later.

## Potential impact if falsified

Equally worth stating, for balance:

- If the fixed-criteria check below finds most repositories' own
  terminal language is about knowledge/preservation rather than
  decisions, that would support the ecosystem's original framing
  (knowledge-management architecture) over this hypothesis, and this
  document should be marked REJECTED rather than left open indefinitely.
- It would mean Discovery Lab's own Ecosystem Observatory role should
  continue to measure itself primarily by evidentiary accuracy (is the
  finding true?), not by downstream decision impact — the framing
  `PROP-0001` already uses, unchanged.

## Proposed experiment (not run by this document)

**DL-0001-EXP-1 (proposed only).** For each of the five repositories
named in the origin observation, independently extract one directly
quoted sentence — the repository's own stated terminal goal or success
condition, from its own foundational document (Constitution, Manifesto,
README, or CONTEXT) — and classify it as:

- **(D) decision/action-oriented** — terminal language about choosing,
  selecting, deciding, or acting;
- **(K) knowledge-oriented** — terminal language about knowing,
  preserving, or recording;
- **(A) ambiguous / both**, if the sentence genuinely supports either
  reading without a citable tiebreaker.

**Fixed rule, frozen before running:** the classification must be made
from a single verbatim quote per repository, chosen *before* looking at
how it will classify, to avoid picking whichever sentence confirms the
hypothesis. **Stop rule:** one classification pass per repository, no
re-selection of a different quote if the first one doesn't fit.

**Verdict rule:** if 4 or 5 of 5 classify as (D), the hypothesis gains
support and should move from CANDIDATE to a more developed status (still
short of ACCEPTED, which requires a human decision). If 2 or fewer
classify as (D), the hypothesis is not supported by this pass and should
be marked REJECTED or revised. 3-of-5 or any (A) majority is
INCONCLUSIVE — the hypothesis stays CANDIDATE, unresolved either way.

This experiment is **proposed only**. It has not been run as part of
recording this document — doing so was intentionally left for a separate
step, consistent with how `PROP-0001`'s "Ecosystem Health Review v0.1"
was itself defined without being executed in the same document that
defined it.

## Custodianship note

Discovery Lab holds this idea in CANDIDATE form only. It is not used to
justify, revise, or inform any other document in this repository —
including `PROP-0001`'s recommendation — unless and until DL-0001-EXP-1,
or an equivalent check, is actually run, reviewed, and its result
recorded back into this file. Until then, this document's only function
is preservation: keeping the idea, its origin, and its arguments intact
and traceable, per Principle 0 — Discovery Lab does not create truth, it
only holds candidate ideas until someone verifies them.
