# Phase 1 — Blind Classification

Per `META-001`. Each source group classified strictly on its own terms,
in its own vocabulary, without cross-referencing other groups or the
`RI-0002` meta-theory (not yet revealed at this stage — see
`../AG-003-meta-theory-RI-0002/FINAL-VERDICT.md`, read only after this
phase and Phase 2 were written). **A methodological caveat, stated
honestly rather than hidden**: true blindness is not fully achievable —
the same analyst who wrote the `RI-0002` synthesis is performing this
classification, and cannot literally un-know it. What is achievable, and
what was actually done, is *procedural* discipline: no `RI-0002`
vocabulary (`Kernel`, `Breaker Mode`, `Evidence Ladder`,
`Generation-Validation Separation`) is used below, no document is
compared to another in this phase, and each classification is grounded
only in that document's own stated content. This limitation is treated
as a real Phase 4 falsification consideration, not swept aside.

**Source of the "Dinev Assistant architecture" gap**: confirmed
`INSUFFICIENT ACCESS`, not re-attempted — the same conclusion the
Reality Stress Test's `RI-0005.md` already reached, citing the separate
`project-memory` repository's `notes/
2026-07-19-dinev-decor-systems-location-check.md`, an exhaustive,
already-completed investigation.

---

## Group A — KOD Architecture Decision Records (`ADR-0005`, `0006`, `0007`, `0009`)

- **Dominant architectural principles**: architecture precedes
  implementation ("Domain precedes persistence. Runtime precedes UI.
  Research precedes AI." — `ADR-0007`); one authoritative repository per
  fact ("Whenever multiple representations of the same information
  exist, exactly one representation is authoritative" — `ADR-0009`);
  incremental structural discipline as the codebase grows (`ADR-0005`,
  `0006` — package structure, runtime root).
- **Validation mechanisms**: a named review step (`Kernel Review`) that
  must return `PASS` before an ADR moves from `Draft` to `Accepted`
  (`ADR-0009`); an explicit precedence order when artifacts disagree
  (Git commits/tests first, then ADRs, then Registry, then Sprint docs,
  then Handoffs last).
- **Knowledge flow**: `Draft → Kernel Review → Accepted`, recorded by a
  Git commit as "the authoritative record of acceptance" (`ADR-0009`);
  separately, `Domain Object → responsibility → lifecycle →
  relationships → implementation` (`ADR-0007`).
- **Decision structure**: roles are "architectural contracts, not
  conversations" (`ADR-0009`); each artifact type has exactly one
  Writer (a named Matrix); Headquarters writes ADRs, Software Lab writes
  code and tests, Kernel Review reviews.
- **Human/AI boundary**: "Human-mediated message passing is the current
  implementation and is explicitly recognized as part of the
  architecture" (`ADR-0009`) — agents do not communicate directly; a
  human transfers Handoffs between sessions.
- **Failure handling**: "If Kernel Review returns BLOCKED, the ADR
  remains in Draft until revised and re-reviewed" (`ADR-0009`) — no
  silent failure state; a Handoff "is never evidence and never replaces
  repository state."

## Group B — KOD Research Kernel specifications (`RESEARCH_ENGINE`, `RESEARCH_GUARDIAN`, `RESEARCH_ENGINE_CONTRACT`, `INVESTIGATION_ENGINE`)

- **Dominant architectural principles**: strict separation of
  *organizing* an investigation from *evaluating* it (`INVESTIGATION_
  ENGINE` "never evaluates conclusions... structures the investigation"
  vs. `RESEARCH_ENGINE` "never decides what is true... decides whether
  the research process has been sufficiently completed"); a third,
  separate role (`RESEARCH_GUARDIAN`) that checks *process integrity*
  specifically, distinct from both.
- **Validation mechanisms**: `RESEARCH_ENGINE_CONTRACT` states explicit,
  numbered guarantees ("Every hypothesis has a unique identifier...
  Every promotion is justified... No conclusion is accepted without
  passing the required methodology") and explicit Failure Conditions
  ("must stop evaluation if... reasoning cannot be reconstructed");
  `RESEARCH_GUARDIAN` outputs one of six fixed states (`Valid Process`,
  `Process Incomplete`, `Missing Evidence`, `Missing Competing
  Hypotheses`, `Traceability Failure`, `Constitutional Violation`).
- **Knowledge flow**: `Research Question → Research Session →
  Observations → Hypotheses → Evidence → Ready for Evaluation`
  (`INVESTIGATION_ENGINE`) `→` one of `Needs More Research / Candidate
  Principle / Verified Principle / Rejected / Archived`
  (`RESEARCH_ENGINE`).
- **Decision structure**: `RESEARCH_ENGINE` is "accountable to the
  Constitution," not to any individual; every decision must record
  "Competing hypotheses considered" — plurality of hypotheses is a
  structural requirement, not a courtesy.
- **Human/AI boundary**: not addressed directly in these four documents
  — they specify engine *behavior*, not who operates the engines.
  Recorded as `not addressed`, not assumed.
- **Failure handling**: `RESEARCH_ENGINE_CONTRACT`'s "Success Criteria"
  is a determinism requirement ("The same Research Session evaluated
  twice under the same methodology should produce the same result") —
  failure is framed as non-reproducibility, a distinct framing from
  Group A's `PASS`/`BLOCKED` gate.

## Group C — Trust Engine architecture (`trust_engine_architecture.md`, `review_protocol_v1.md`, `proposal_quality_gate_architecture.md`)

- **Dominant architectural principles**: "Trust is not a property of a
  model. Trust is compressed memory of how a model performed in a
  specific context against reality" — context-specificity and
  non-universality of trust as a stated axiom; "Development is not
  accumulation of experience. Development is selection of experience"
  (`proposal_quality_gate_architecture.md`).
- **Validation mechanisms**: a fixed, five-step `Review Workflow`
  (`Outcome Review → Error Classification → Experience Assessment →
  Proposal Assessment → Trust Update Proposal`), each step with its own
  required fields and forbidden actions ("Completing a later step must
  not alter the result of an earlier step silently"); a numeric
  `Experience Quality Score` gate (`0–100`) mapping to four fixed
  outputs (`IGNORE`, `LOG_ONLY`, `PROPOSE`, `ESCALATE`).
- **Knowledge flow**: `Prediction → Reality → Review → Structured
  Experience → Trust Update Proposal → Approval → Applied Update →
  Trust Memory → Future Selection` (`review_protocol_v1.md`'s own
  closing diagram).
- **Decision structure**: reviews are explicitly barred from causing
  effects: "Reviews never modify Trust Scores. Reviews never apply
  Trust Updates. Reviews only create structured evidence." A gate
  ("Proposal Quality Gate") separately decides whether a review's output
  is even worth turning into a proposal — a second filter before any
  human sees it.
- **Human/AI boundary**: "Trust mutation requires: Proposal → Approval
  → Applied Update" — every path to changing the system's stored trust
  state passes through an explicit approval step, named but not
  attributed to "human" specifically in these three documents (recorded
  as `implicit, not stated as human` — a real ambiguity, not resolved by
  assumption).
- **Failure handling**: an explicit `UNKNOWN` outcome status exists,
  with rules for when it may and may not be used ("must not be used to
  avoid classifying an observable failure"); `INSUFFICIENT_EVIDENCE` is
  one of four allowed Trust Update Proposal results, not an error state.

## Group D — Project Memory: Handover system architecture (installer/dispatcher domain)

- **Dominant architectural principles**: numbered, explicit
  "Architectural Principles" section, e.g. "AI writes drafts; a human
  commits. No AI output changes confirmed state" (principle 1);
  "Readiness is calculated, never entered" (principle 2); "Raw evidence
  is immutable and stored separately from interpretations" (principle
  4). This is a **commercial field-operations system** (installer
  handovers, readiness for a return visit), not a research or AI-
  governance system at all.
- **Validation mechanisms**: every AI-produced field carries a
  `confidence` value; below a configurable threshold, the field is
  visually flagged and cannot be bulk-confirmed, requiring an individual
  click; an `unresolved` list of un-mapped items is always shown,
  described as deliberate ("silently dropping them is the most
  dangerous failure mode").
- **Knowledge flow**: `CallRecordingReceived/EvidenceUploaded →
  transcription → Context Package assembly → LLM extraction (strict
  JSON schema) → InterpretationDraftReady → review queue`.
- **Decision structure**: "Every object has a named owner at every
  moment... never 'the organization,' always a person" (principle 5);
  a `Clause` (a condition) is explicitly distinguished from a `Task` (an
  activity) — "a completed task does not close a condition; only
  evidence closes it" (principle 3).
- **Human/AI boundary**: explicit and repeated: "What AI never decides:
  readiness, Go/No-Go, closing conditions, scheduling, sending anything
  to a client or supplier" — a named, closed list of decisions withheld
  from AI entirely, stronger than a general "human approves" rule.
- **Failure handling**: `HandoverMissing` is a named event fired when a
  handover has not reached `accepted` status by a configurable hour —
  absence of a required state transition is itself a monitored,
  alertable condition, not merely an unhandled case.

## Group E — Project Memory: AI Collaboration Architecture and Protocol

- **Dominant architectural principles**: seven numbered "Fundamental
  Invariants," explicitly ranked above ordinary practice — e.g. `INV-2`
  "Chat is not truth... has authority zero"; `INV-5` "Separation of
  powers: Executor ≠ critic ≠ gatekeeper ≠ arbiter... no role combines
  two of these functions in one artifact"; `INV-7` "Minimalism — a new
  artifact type, role, status, or rule is introduced only against
  documented, repeated friction."
- **Validation mechanisms**: a named `Kernel Governance Layer`,
  explicitly *not* a coordinator, answering exactly one question ("Does
  this artifact satisfy the applicable Review Contract — yes or no?"),
  returning only `PASS` or `BLOCKED` plus the exact violated criterion;
  an explicit "anti-theater clause": twenty consecutive `PASS` results
  is treated as a signal the review contract is too weak, not as
  success.
- **Knowledge flow**: `IDEA → docs/notes (DRAFT, 30-day TTL) →
  docs/specs or docs/research (DRAFT → REVIEW) → docs/adr (DRAFT →
  REVIEW → ACCEPTED) → GitHub Issues → Implementation`.
- **Decision structure**: an explicit two-layer "Authority and Truth"
  model — Normative Authority (`Protocol → Accepted ADR → Approved Spec
  → Issue`) vs. Operational Reality (`Code in main → Tests → Runtime
  behavior`) — with the explicit rule "no automatic winner exists
  between these layers"; a mismatch is a named first-class state
  (`Architecture–Implementation Drift`), not an error to hide.
  A four-role minimum (Architect/Researcher, Reviewer/Breaker,
  Implementer, Kernel), justified by `INV-5`.
- **Human/AI boundary**: `INV-4`, "Human final authority — only the
  human: accepts an ADR, authorizes merge, resolves drift, changes the
  protocol." A full "Authority Matrix" table makes this explicit,
  action by action, for AI role / Reviewer / Kernel / Human separately.
- **Failure handling**: "Architecture–Implementation Drift is not a
  first-class state's shame — the shame is *unnoticed* drift" (own
  wording, translated); a fixed, three-way resolution ("the code is
  wrong," "the ADR is stale," or "both are partially right") is
  required, always ending in a new or superseding ADR, never a silent
  reconciliation. A named "Kernel theater" failure mode is explicitly
  anticipated and given its own countermeasure (the anti-theater
  clause, above).

## Group F — Discovery Lab's own architecture (`GOVERNANCE.md`, `ARCHITECTURE-MAP.md`; `ADR-0001` reused from the Reality Stress Test, flagged)

*(Reuse disclosure: `docs/adr/ADR-0001-human-authority-gates.md` was
already read and curated in the Reality Stress Test, for a different
analytical question — AG-003's own architectural robustness, not
cross-domain philosophy testing. Reusing it here is a real limitation on
this group's independence, addressed directly in Phase 4.)*

- **Dominant architectural principles**: a mandatory, ordered lifecycle
  before any component may be marked stable (`Idea → Draft → Internal
  Review → Adversarial Review → Reality Stress Test → Freeze
  Recommendation → FROZEN`); architectural stability is explicitly a
  *different axis* from organizational trust ("Freeze vs. adoption");
  `ADR-0001`'s Human Authority Gate concept — crossing one "is never
  considered an error. It is a normal state transition."
- **Validation mechanisms**: an Adversarial Review stage required to
  find and either fix or explicitly record defects before any freeze;
  a Reality Stress Test stage required to run against real, structurally
  different data, explicitly to falsify, not confirm.
- **Knowledge flow**: `Reality → AG-002 (recovery) → Recovered Knowledge
  → AG-003 (curation) → Knowledge Base` (`ARCHITECTURE-MAP.md`'s own
  pipeline diagram).
- **Decision structure**: `GOVERNANCE.md`'s versioning rules
  distinguish bug fix / clarification / minor revision / major revision
  / deprecation, each requiring a different amount of process; a major
  revision requires the full lifecycle again, not a shortcut.
- **Human/AI boundary**: explicit throughout — "Discovery Lab does not
  freeze itself... the same 'who may run the process, and who may not
  decide it' rule applies identically here" (`GOVERNANCE.md`); `ADR-0001`
  §3's required agent behavior on encountering a Human Authority Gate:
  "Stop immediately... Wait... No retries. No workarounds."
- **Failure handling**: `ADR-0001`'s four-category Organizational
  Principle (Technical failure / Infrastructure limitation / Governance
  boundary / Human Authority Gate) — only the first two are "engineering
  problems," the latter two are "expected operational states," not
  failures to eliminate.
