# Phase 2 — Independent Pattern Extraction

Per `META-001`. Recurring structures identified across `PHASE1-BLIND-
CLASSIFICATION.md`'s six groups, **without reference to `RI-0002`**.
No synthesis, no naming against a theory — simply which mechanisms
repeat, in which groups, cited to the specific document text.

## P1 — AI proposes, only a human commits/approves/merges

- Group A: Kernel Review returns `PASS`, but "Headquarters commits the
  status change... the Git commit is the authoritative record."
- Group C: "Trust mutation requires: Proposal → Approval → Applied
  Update." A proposal "is advisory. It is not approval."
- Group D: "AI writes drafts; a human commits. No AI output changes
  confirmed state" (stated as architectural principle 1, first in the
  list).
- Group E: `INV-4`, named explicitly: "Only the human: accepts an ADR,
  authorizes merge, resolves drift, changes the protocol."
- Group F: `ADR-0001`'s Human Authority Gate; `GOVERNANCE.md`'s
  "Discovery Lab does not freeze itself."
- Group B: not addressed (the four Research Kernel documents specify
  engine behavior, not operator authority).

## P2 — Exactly one authoritative representation; disagreement is not auto-resolved

- Group A: "Whenever multiple representations of the same information
  exist, exactly one representation is authoritative," with a stated
  precedence order for conflicts.
- Group C: Trust Memory is the one compressed authoritative state;
  raw prediction/review records are preserved separately as evidence for
  it, not competing with it.
- Group D: "two planes, physically separated" — relational truth
  (Postgres) vs. raw evidence (Object Storage), with an explicit
  citation link between them (`evidence_id + offset`).
- Group E: two-layer Authority model (Normative Authority vs.
  Operational Reality), with the explicit rule "no automatic winner
  exists between these layers" — a mismatch is a named state
  (`Architecture–Implementation Drift`), not silently resolved.
- Group F: `ARCHITECTURE-MAP.md`'s `Knowledge Base` as the target single
  authoritative store (not yet populated, stated honestly).
- Group B: implicit only — the Research Engine's traceability
  requirement presupposes a single evaluated record per hypothesis, not
  stated as a named principle the way Groups A/C/D/E state it.

## P3 — Explicit, named uncertainty/failure states, never silently resolved

- Group A: `BLOCKED` + the specific violated criterion, cited from the
  contract.
- Group B: `RESEARCH_GUARDIAN`'s six fixed outputs (`Valid Process`
  through `Constitutional Violation`); `RESEARCH_ENGINE_CONTRACT`'s
  explicit Failure Conditions requiring the engine to stop rather than
  guess.
- Group C: `UNKNOWN` (with explicit rules for when it may/may not be
  used — "must not be used to avoid classifying an observable failure")
  and `INSUFFICIENT_EVIDENCE` (an allowed, non-error Trust Update
  Proposal result).
- Group D: an `unresolved` list, always displayed — "silently dropping
  them is the most dangerous failure mode" (paraphrased from source).
- Group E: `Architecture–Implementation Drift` as a named first-class
  state — "the shame is unnoticed drift," not the drift itself.
- Group F: `ADR-0001`'s four-category Organizational Principle,
  distinguishing real engineering failures from expected non-failure
  states requiring a human action.

## P4 — Role separation: no single actor holds two conflicting functions

- Group A: a Writer Matrix (one writer per artifact type); Kernel Review
  is distinct from Headquarters, which drafts.
- Group B: three distinct engines with explicitly non-overlapping
  authority — `INVESTIGATION_ENGINE` organizes and "never evaluates
  conclusions"; `RESEARCH_ENGINE` evaluates and "never decides what is
  true"; `RESEARCH_GUARDIAN` checks process integrity and "never
  protects an idea."
- Group C: the five-step Review Workflow is composed of steps each with
  "a separate responsibility"; the Proposal Quality Gate is explicitly
  distinct from approval authority.
- Group E: `INV-5`, named explicitly: "Executor ≠ critic ≠ gatekeeper ≠
  arbiter... no role combines two of these functions in one artifact."
- Group F: at least four distinct senses of "review" kept deliberately
  separate (ORB's conduct review, AG-003's own Knowledge Review, KOD's
  Under Review, GDE's Critical Review), each with its own disambiguation
  note in its governing document.
- Group D: present but weaker — ownership (one named person per object)
  is about accountability, not about separating conflicting functions
  the way the other five groups state it.

## P5 — Versioned, immutable, append-only historical record

- Group A: "Registry artifacts are reconciled to Git history, never the
  reverse"; the Git commit itself is the record of acceptance.
- Group C: `score_snapshots` exists specifically as a "Historical audit
  trail"; Review Immutability rule — "do not overwrite history to match
  later conclusions."
- Group D: Evidence is immutable by storage-level policy, not
  application convention alone; hashed at ingestion (`SHA-256`) "to
  prove it was not altered."
- Group E: "ADRs are append-only: an accepted ADR is not substantively
  edited, it is replaced (`superseded by 00MM`)."
- Group F: the append-only registry convention already standing
  elsewhere in this repository (`EMPLOYEE-REGISTRY.md`, `ORB-REGISTRY.md`,
  `MEMORY-SOURCE-REGISTRY.md`), independently echoed here.
- Group B: not addressed directly in the four documents read.

## P6 — A numeric threshold gates escalation tier, but never authorizes the final action itself

- Group C: `Experience Quality Score` (`0–100`) maps to `IGNORE` /
  `LOG_ONLY` / `PROPOSE` / `ESCALATE` — explicitly, "Even `CRITICAL`
  does not mean automatic trust mutation."
- Group D: a configurable `confidence` threshold on AI-extracted fields
  — below it, the field cannot be bulk-confirmed, requiring an
  individual click; the threshold gates *review friction*, not
  acceptance.
- Not observed structured this specifically in Groups A, B, E, F — those
  groups gate on a binary (`PASS`/`BLOCKED`) or a categorical status,
  not a numeric score mapped to tiers. Recorded as a narrower pattern,
  present in exactly two groups, not a majority one.

## P7 — "Process over conclusion" stated as an explicit, named principle

- Group B: `RESEARCH_ENGINE` — "It never protects conclusions. It
  protects the research process"; `RESEARCH_GUARDIAN` — "It never
  protects an idea... protects the process."
- Group C: "Reality is the final arbiter of trust" appears, close to
  verbatim, in both `trust_engine_architecture.md`'s core principles and
  `review_protocol_v1.md`'s stated principle.
- Group E: the Kernel/Reviewer split is explicitly framed as form
  (Kernel: "Is the contract satisfied?") vs. substance (Reviewer: "How
  will this break?") — two different senses of scrutiny, kept apart on
  purpose; the Research Flow section states the *path* to a conclusion
  (rejected hypotheses, dead ends) is preserved as knowledge in its own
  right, not only the conclusion.
- Group A: present but weaker — `ADR-0007`'s "Architecture precedes
  implementation" is a process-ordering principle, not explicitly a
  "process over conclusion" epistemic claim the way B/C/E state it.
- Group D: present but domain-shifted — "Raw evidence is immutable...
  every interpretation points to the evidence" functions similarly
  (interpretation is never trusted over the underlying record) but is
  phrased as an evidentiary rule, not a research-philosophy statement.
- Group F: not stated as its own named principle in `GOVERNANCE.md`/
  `ARCHITECTURE-MAP.md` directly, though the Adversarial Review /
  Reality Stress Test lifecycle stages structurally enact it.

## Summary count (mechanisms found in how many of the six groups)

| Pattern | Groups exhibiting it | Count |
|---|---|---|
| P1 — AI proposes, human commits | A, C, D, E, F | 5 / 6 |
| P2 — one authoritative representation | A, C, D, E, F (B implicit only) | 5 / 6 |
| P3 — named uncertainty states, never silent | A, B, C, D, E, F | 6 / 6 |
| P4 — role separation | A, B, C, E, F (D weaker) | 5 / 6 |
| P5 — versioned immutable history | A, C, D, E, F | 5 / 6 |
| P6 — numeric threshold gates tier, not action | C, D only | 2 / 6 |
| P7 — process over conclusion, named | B, C, E strongly; A, D, F weaker/implicit | 3 strong / 6 |

This table is purely descriptive at this stage — no comparison to
`RI-0002` has been made yet. See `PHASE3-META-THEORY-COMPARISON.md`.
