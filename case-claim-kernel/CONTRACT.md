# Contract — Case/Claim Identity Kernel v0.1 (`case-claim-kernel/`)

Core Principle: **Wrap already-published records with a stable, deterministic,
cross-package identity. Never merge, infer, decide, dispatch, or promote.**

This is a **tool contract**, matching the precedent of `observation-agent/CONTRACT.md`,
`x-signal-probe/CONTRACT.md`, and `constraint-change-observatory/CONTRACT.md` — not a
governance/Employee Role contract.

## Origin

Stage 1 of the AUTONOMOUS MULTI-MODEL KNOWLEDGE SYSTEM reuse archaeology (Phase 0
audit, response only, not committed to this repo). Phase 0 found that a CASE/CLAIM
identity layer was the one genuinely missing primitive a future multi-model loop
would need that no existing package provides, and that everything else the audit
covered — second model provider, blind dispatch, Falsifier, Judge, router, outcome
resolution, Trust Engine integration, Grok Scout, Headquarters changes — was
explicitly out of scope for this slice. This package is exactly that slice, stopped
exactly where the task said to stop.

## Scope of authority

Reads only two already-published, already-real files, in read mode only, via plain
`json.load` (never by importing `ca_agents` or `business_candidate_analyst`):

- `constraint-archaeology-agents/data/anomalies.json`
- `business-candidate-analyst/data/candidates.json`

Writes only to its own `case-claim-kernel/data/artifacts.jsonl` (append-only).

## Hard boundary — this tool MUST NOT

- open any file under `constraint-archaeology-agents/`, `business-candidate-analyst/`,
  or any other package's directory in a writing mode, ever — enforced by
  `tests/test_safety.py`, not just this document.
- import `ca_agents` or `business_candidate_analyst` — the same "read data, never
  code, across packages" rule `constraint_change_observatory/CONTRACT.md` already
  holds itself to, enforced here the same way.
- edit or delete a line in `data/artifacts.jsonl`, ever. It is append-only; a
  re-wrap of the same source record is a no-op (same `artifact_id`), never a rewrite.
- infer, merge, cluster, or otherwise decide that two different source records are
  "the same" thing. Every `case_id` wraps exactly one already-named source record
  (`anomaly_id` or `candidate_id`) — see `identity.py`'s module docstring for why
  this is refused by construction, not by policy.
- call a language model, make a network call, or read any secret/credential — there
  is no code path here that could.
- fabricate a Claim's evidence. An empty `evidence` list is written through exactly
  as the source `DimensionResult` recorded it, with a truthful note explaining why,
  never invented content.
- dispatch a second model, run a Falsifier or Judge, change any CA/BCA lifecycle
  state, write to `findings.jsonl`, or otherwise perform any capability Stage 1 was
  explicitly told not to build. Those remain out of scope for this contract entirely.

## Rights

- The right to produce zero Claims for a wrapped Case when the source record itself
  carries no claim-shaped content yet (e.g. an unevaluated Constraint Archaeology
  Anomaly with no matching Evaluation) — an empty claim list is a correct result, not
  a defect.
- The right to be re-run against the same source record on any later day and produce
  byte-identical `case_id`/`claim_id` values every time.

## Responsibilities

- Preserve every source id (`anomaly_id`, `candidate_id`, and every `observation_id`
  a source record already names) unchanged and inspectable in the wrapped output.
- Cite `derived_from` truthfully for every envelope — the source record id for a
  Case, the actual evidence ids for a Claim — never a fabricated or guessed value.
- Keep `Case`, `Claim`, and `ArtifactEnvelope` as the only three objects this package
  defines. Adding a fourth (an analysis, a decision, an outcome) is out of scope for
  this contract and needs a new, explicit human decision — the same standard
  `business-candidate-analyst/CONTRACT.md` already holds itself to.

## Executor independence

This contract binds the tool, not whoever runs it — same precedent as
`observation-agent/CONTRACT.md`.

## Revocation and change

This tool may be modified, extended, or retired at any time by direct repository
change. A change that would grant it write access to any other package's directory,
a model call, an inference/merge capability across two source records, or a fifth
object beyond Case/Claim/ArtifactEnvelope is out of scope for this contract entirely
and needs a new, explicit human decision.
