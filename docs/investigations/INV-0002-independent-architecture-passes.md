# INV-0002 — Three Independent Architecture Passes + Synthesis

Status: DRAFT (investigation record — diagnosis only, no proposed solution)
Date: 2026-07-24
Author: Implementer session (Claude Code)

## Method

Three completely independent, read-only architecture reviews were run as
isolated agent sessions, each with no visibility into the other two or
into any prior Discovery Lab work. Each pass read only its assigned
repository (KOD, generative-discovery-engine, or trust-engine), answered
a fixed set of 8 questions grounded in that repository's own files, and
was explicitly instructed not to compare, not to propose what Discovery
Lab should be, and not to make any recommendation. A fourth pass — the
synthesis at the end of this document — was performed only after all
three independent reports were complete, and is the first place any
cross-repository comparison happens.

This document is diagnosis only. Proposed mandate variants, a
recommendation, the information-flow map, and the first experiment are in
`docs/proposals/PROP-0001-discovery-lab-boundaries.md` (revised).

---

## PASS A — KOD (independent, read-only)

**1. Primary mission.** "KOD does not protect ideas. KOD protects honest
research" (`Core/CONSTITUTION.md`). A domain-agnostic research
methodology whose founding axiom is "Reality is the final arbiter of
knowledge" (Constitutional Principle C2). `ADR-0001`: "KOD is the
methodology... No product defines KOD. KOD defines the products."

**2. Unit of work.** The **Research Session** — "the primary unit of
investigation inside KOD," grouping Observations, Questions, Hypotheses,
Evidence, Decisions, and Outcomes for one objective. Within it, the
**Knowledge Object** is the atomic unit (Observation, Question,
Hypothesis, Evidence, Principle). KOD's own docs flag this as not fully
settled: `Knowledge/RS-0003_FUNDAMENTAL_ENTITY_OF_KOD.md` is an open,
unaccepted research question about whether a more primitive entity
exists.

**3. Knowledge it owns.** A strict split (`Core/DOMAIN_MODEL.md`) between
the **Knowledge Domain** (Observation, Question, Hypothesis, Evidence,
Principle, Decision, Outcome) and the **Research Domain** (Research
Session, Investigation, Experiment, Evaluation, Review, Research
Journal). Plus the Constitution, ADRs, and Registry that govern KOD
itself, and the Knowledge Graph ("the structural memory of KOD") and
Research Journal ("the permanent memory of KOD... Nothing is deleted").

**4. Must never belong there.** Objective truth-determination ("The
Research Engine never decides what is true. It decides whether the
research process has been sufficiently completed" —
`Foundations/RESEARCH_ENGINE.md`); deletion of research history
(append-only, Constitution C4); protected/immune ideas (Constitution C7:
"No hypothesis, principle or model is immune from questioning"); AI
acting as "oracle, judge, or authority" (`CONSTITUTION.md`); conclusions
without process.

**5. Lifecycle.** Observation → Question → Hypothesis → Prediction →
Reality → Evidence → Confidence Update → Principle → Decision → Outcome →
(new) Observation, executed through Investigation Engine ("never
evaluates conclusions") → Research Engine (classifies, requires
falsification) → Research Guardian (process-compliance check) → Research
Journal (append-only log) → Knowledge Graph.

**6. Architectural invariants.** Method-over-conclusions (C1),
reality-as-arbiter (C2), full traceability (C3), preserved history (C4),
self-correction (C5), separated knowledge states (C6), no protected ideas
(C7); specification-before-implementation (`ADR-0003`); single-source-of-
truth precedence ordering (`ADR-0009`); reproducibility ("the same
Research Session evaluated twice... should produce the same result" —
`RESEARCH_ENGINE_CONTRACT.md`).

**7. Explicit boundaries.** "KOD is not an AI model. KOD is not a
programming language. KOD is not a software framework"
(`Core/README.md`). Products (Trust Engine, Regime AI) are explicitly
downstream/application-layer: "Trust Engine is the first practical
implementation of KOD's methodology" (`Products/TrustEngine/
KOD_MAPPING.md`). No autonomous agent-to-agent messaging — only via
version-controlled artifacts (`ADR-0009`).

**8. Duplication risk (per KOD's own claims).** Anything that re-derives
its own Constitution, its own Observation→Principle knowledge lifecycle,
or its own Research-Guardian-equivalent falsification/traceability
enforcement duplicates KOD's core, explicitly protected function.

---

## PASS B — generative-discovery-engine (independent, read-only)

**1. Primary mission.** "Develop and experimentally validate methods
that can systematically discover new business models, scientific
hypotheses, engineering solutions, and system architectures"
(`README.md`). Core rule: "No discovery method is accepted or used
operationally before surviving independent critical review and
pre-registered validation."

**2. Unit of work.** The **discovery method**, moving through a fixed
ladder (`CONTEXT.md`): hypothesis generator → discovery method →
validated method → real business/scientific solution (the last tier
explicitly outside GDE's current scope — "this project currently has
items in the first two categories only").

**3. Knowledge it owns.** The record of method-validation attempts
(methods, critical reviews, protocols, pre-registered experiments,
results, verdicts) in `registry/`; the validation protocol itself
(`docs/protocols/RVS-00-validation-kernel.md`, a 21-section epistemic
kernel); accepted repository knowledge traceable to a human-approved
`registry/DECISIONS.md` entry; six role contracts (`contracts/`).

**4. Must never belong there.** Proof the method works before validation
("This repository does not contain proof that the Minimal Constraints
Method works. It contains the record of the attempt to find out" —
`README.md`); unmaterialized chat conclusions (`ADR-0001`: "ChatGPT and
Claude conversations are working memory only"); AI-finalized decisions
("AI models cannot independently accept scientific or architectural
decisions" — `ADR-0001`); post-hoc-adjusted validation criteria
("Validation criteria are frozen before results are seen" —
`CONTRIBUTING.md`); findings mixed into the changelog ("This is a log of
repository state, not of research findings" — `CHANGELOG.md`).

**5. Lifecycle.** Observed phenomenon → operational definition →
candidate method → critical review → pre-registered validation →
PASS/PARTIAL/FAIL → controlled discovery use → independent evaluation →
repository knowledge (`README.md`), gated through 8 sequential ROADMAP
phases (currently stalled in Phase 1, RVS-00 unfrozen). Governing roles:
Critical Reviewer, Experiment Designer, Protocol Keeper, Librarian,
Reality Checker, Discovery Agent (currently DISABLED).

**6. Architectural invariants.** No operational use without a recorded
PASS/scoped-PARTIAL; human-only finalization; frozen criteria (RVS-00
§21 "Threshold Freeze Rule"); necessity≠sufficiency always labeled;
UNDECIDABLE never silently collapsed (RVS-00 §1); run-integrity
classification (NULL/INVALID/VALID RUN) before any scientific outcome;
no re-execution against a "burned" holdout (§11); actor independence;
no overgeneralization beyond tested scope (§5).

**7. Explicit boundaries.** "Not an idea generator" — explicitly
contrasted with a system optimizing for "volume and novelty of output"
(`CONTEXT.md`). Discovery Agent is DISABLED and forbidden to
self-activate. Reviews cannot rewrite what they review
(`contracts/critical-reviewer.md`). Results are not self-graded or
reclassified after the fact (`docs/results/README.md`).

**8. Duplication risk (per GDE's own claims).** Any system that
"generates candidates and treats them as validated/usable" duplicates
GDE's core reason for existing — not idea generation, but the
adversarial validation-kernel and role-separated governance apparatus
that turns a plausible method into evidence.

---

## PASS C — trust-engine (independent, read-only)

**1. Primary mission.** Not prediction — selection: "The deeper purpose
of Trust Engine is not prediction. It is selection"
(`trust_engine_foundation_review.md`). Founding idea: "Trust is not a
property of a model. Trust is compressed memory of how a model performed
in a specific context against reality" (`trust_engine_architecture.md`).

**2. Unit of work.** A reviewed prediction/decision tied to a context:
Prediction → Reality → Review → Structured Experience → Trust Update
Proposal → Approval → Applied Update → Trust Memory → Future Selection.

**3. Knowledge it owns.** Layered, explicitly-typed memory: Trust Memory
(predictions/reviews/error profiles/scores); a three-tier Trust Score
Taxonomy — FOUNDATION_TRUST, DOMAIN_TRUST, CONTEXTUAL_TRUST
(`trust_score_identity_architecture.md`); Error Profiles as a first-class
taxonomy equal in importance to trust scores; separated Observation
Memory ("What facts...") vs. Evidence Memory ("What conclusions...")
(`observation_architecture_v1.md`); Mechanism Trust Memory (trust in
causal explanations); Meta Trust Memory (trust in its own internal
mechanisms — Selector, Experience Engine, Proposal Quality Gate, Trust
Update Engine); an immutable Applied Update Ledger.

**4. Must never belong there.** Observations must never contain
interpretation ("Never: rewrite observations... replace observations
with interpretation" — `observation_architecture_v1.md`); no component
except the single Proposal→Approval→Applied-Update gate may mutate trust
("Reviews never modify Trust Scores... Reviews only create structured
evidence" — `review_protocol_v1.md`); CONTEXTUAL_TRUST must never mutate
FOUNDATION_TRUST/DOMAIN_TRUST; model trust and mechanism trust must stay
separate ("Do not mix model reliability with mechanism reliability" —
`meta_trust_layer_architecture.md`); no mechanism, including its own, is
privileged/exempt from validation ("No privileged models... No
privileged mechanisms").

**5. Lifecycle.** Two parallel, structurally identical lifecycles (model
trust; mechanism/meta trust), both gated through: Observation → Outcome
Review (TRUE/PARTIAL/FALSE/UNKNOWN against a locked rule) → Error
Classification → Experience Quality Score (0–100) → Proposal Quality
Gate (IGNORE/LOG_ONLY/PROPOSE/ESCALATE) → Trust Update Proposal → Human
Approval → Applied Update (the sole mutation boundary, exact-once,
bounded ±3 in v1, ledgered) → Trust Memory → Selection.

**6. Architectural invariants.** Reality is the final arbiter (most
repeated principle in the repo); a single mutation gate — nothing else
may mutate trust; score-identity discipline ("No proposal should be
applied unless `proposal.score_base_type == applied_update.
target_score_type`"); exact-once/bounded/ledgered/reversible mutation;
drift protection (blocked if live score diverged from proposal
snapshot); no privileged mechanisms; trust is always contextual, never
universal; immutable history; "Development is not accumulation of
experience. Development is selection of experience"
(`development_architecture_v1.md`).

**7. Explicit boundaries.** "Not a predictor... Trust Engine v1 should
avoid producing a single universal leaderboard"
(`trust_engine_architecture.md`). Advisory only at every governed layer
— "Even CRITICAL does not mean automatic trust mutation"
(`proposal_quality_gate_architecture.md`); human approval remains
required regardless of signal priority. "Trust does not equal truth.
Trust does not equal confidence" (`mechanism_trust_architecture_v1.md`).

**8. Duplication risk (per trust-engine's own claims).** Any system that
independently builds a context-scoped, evidence-gated trust-mutation
pipeline with score-identity discipline and an immutable ledger, or a
self-evaluating meta-layer applying the same scrutiny to its own
mechanisms, duplicates this repository's core claimed contribution.

**Classification.** A mix, weighted toward specification. Roughly 60+
architecture/spec/plan/review markdown files versus 15 `.py` modules
(~8,000 lines). The implemented code demonstrably covers the base Trust
Layer (predictions, reviews, error profiles, decision audit, outcome
tracking, the proposal/approval/applied-update pipeline, a live
Streamlit+SQLite MVP). The entire Mechanism Trust and Meta Trust Layer
apparatus — mechanism catalog, mechanism evidence, mechanism trust
score, mechanism selection/validation engines, meta trust memory/
operating loop — exists **only as architecture documents**, with no
corresponding `.py` files anywhere in the repository.

---

## Phase 4 — Synthesis (first cross-repository comparison in this document)

### Overlaps

- KOD's Research Domain (Investigation, Experiment, Evaluation, Review)
  and GDE's method-validation pipeline (critical review → pre-registered
  validation → verdict) are structurally similar — both gate a claim
  through adversarial review before acceptance — but scoped differently:
  GDE validates *discovery methods* specifically; KOD is domain-agnostic
  over any knowledge claim. Neither repository cross-references the
  other; this overlap is currently unmanaged rather than actively
  conflicting.
- Trust Engine is an **acknowledged, intentional** overlap with KOD:
  KOD's own `Products/TrustEngine/KOD_MAPPING.md` states "Trust Engine is
  the first practical implementation of KOD's methodology." Trust
  Engine's Observation→Evidence→Experience→Proposal→Approval→Applied-
  Update pipeline is structurally a specialization of KOD's
  Observation→Hypothesis→Evidence→Decision→Outcome cycle. Not a
  duplication risk as long as Trust Engine does not also attempt to
  redefine KOD's Constitution or knowledge-lifecycle terms independently.
- GDE and Trust Engine independently reinvented the same governance
  pattern — human-only finalization before any claim is accepted (GDE:
  `registry/DECISIONS.md`, ADR-0001; Trust Engine: Approval → Applied
  Update) — without referencing each other. Convergent evidence of a
  shared ecosystem norm, not a conflict between the two repositories.

### Gaps

- None of the three repositories has any documented awareness of the
  other two, of `discovery-lab`, or of `project-memory`. Each is
  strictly inward-facing: KOD governs its own knowledge lifecycle, GDE
  its own method-validation pipeline, Trust Engine its own trust-scoring
  loop. (The one exception is KOD's one-directional claim that Trust
  Engine is its downstream product — not a two-way relationship.)
- No repository, including project-memory, verifies whether its own
  self-reported status still matches its actual committed content.
  `trust-engine`'s own docs never flag its 60-doc/15-module gap as a
  tracked discrepancy anywhere in the repository — this investigation is
  the first place it is recorded.

### Ownership conflicts

None are currently active (no shared artifact or repository is
contested by two owners). Two prospective conflict vectors, both
purely about how a *future* Discovery Lab mandate could create a
conflict that does not exist today:

1. **Terminology.** "Observation," "Evidence," "Hypothesis,"
   "Experiment," and "Review" are simultaneously load-bearing,
   specifically-defined terms in KOD (Knowledge Domain), Trust Engine
   (Observation/Evidence Memory, Structured Experience, Review Protocol),
   and GDE (pre-registered Experiment, Critical Review). Any Discovery
   Lab mandate reusing these words as its own first-class artifact types
   would collide with all three simultaneously, not just one.
2. **Authority.** All three repositories independently converge on the
   same invariant: only a human, through that repository's own
   registered process, finalizes anything (KOD's Research
   Engine/Guardian non-authority over truth; GDE's ADR-0001 "AI may
   draft, propose, and recommend... may not finalize"; Trust Engine's
   "Human approval remains required for trust mutations"). Any Discovery
   Lab mandate must inherit this same invariant toward every repository
   it touches, not only toward its own artifacts.

### Possible location for Discovery Lab

The one position none of the three repositories occupies is
**outward-facing, cross-repository, pre-formal verification** — sitting
upstream of all three repositories' own intake points (KOD's
Investigation Engine, GDE's candidate-method review, Trust Engine's
prediction pipeline), and across the boundary none of the three look
across at all. This is a sharper, better-evidenced version of the same
conclusion reached in `INV-0001`: the trust-engine spec-vs-implementation
gap discovered during this very pass is itself a live instance of
exactly the kind of finding that outward-facing role would exist to
surface, and none of the three repositories' own governance apparatus is
positioned to find it internally.

This synthesis is the basis for the mandate variants proposed in
`docs/proposals/PROP-0001-discovery-lab-boundaries.md`.
