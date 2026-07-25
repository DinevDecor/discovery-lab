# Deliverable 2 — Selected Execution Pilot

Per `ARCH-003` Phase 2.

## Selected: **C1 — Promote `KO-S3-01` via `CPP-S3-01`**

## Why this is the right first experiment

**It isolates the one question the Mission actually asks.** The
Mission is to prove or disprove that `Unified Coordination Model v1.0`
can govern real execution — not to test `AG-003`'s merge logic, its
relationship ontology, or its investigation-authorization boundary.
`C1` is the only candidate whose object count is exactly one, whose
field change is exactly one (`status`), and whose gating logic is
already fully reasoned inside the proposal itself. Every other
candidate bundles the execution question together with a second,
unrelated judgment call (merge correctness, relationship-type
correctness, evidence-strength correctness) that would confound the
result.

**It requires zero new prerequisite artifacts.** `C2`, `C3`, and `C4`
all require materializing objects that were never independently filed
— an ungated step with no proposal, no review, and no human decision
behind it, which would mean the pilot quietly performs an unreviewed
action before its own first Formal Gate even runs. `C1` has no such
gap: `KO-S3-01` and `CPP-S3-01` are both already complete, both
already real, and nothing about them depends on any other undecided
artifact.

**It has the cleanest possible failure mode.** If `C1` cannot be
executed without inventing a new mechanism, that is a direct,
unambiguous answer to the Mission question for the single narrowest
case available — exactly the "smallest possible experiment" the Mission
calls for. A failure on `C2`–`C4` would leave open whether the failure
was about execution or about a different, unrelated architectural
judgment.

**It closes a real, already-named open question.** `AG-003`'s own
`STATUS.yaml` lists "whether a real Knowledge Base store
(`memory/knowledge-objects/`) should be created now" as an open
governance question. This pilot is the direct, minimal way to answer
it — not a new question invented for this task.

**It carries the lowest blast radius of any candidate.** Per
`1-CANDIDATE-PILOT-ANALYSIS.md`'s ranking, `C1` scores highest on both
measurability and reversibility and lowest on risk and complexity —
the correct profile for a first pilot under a Mission that explicitly
says the goal is not to build a general Execution Layer.

## What selecting `C1` does not do

It does not test merges, relationships, or investigation
authorization — `C2`–`C4` remain real, real-proposal candidates for a
possible second pilot, not discarded by this choice, only sequenced
after it.
