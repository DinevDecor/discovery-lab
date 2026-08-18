# Contract — Blind Analysis Kernel v0.1 (`blind-analysis-kernel/`)

Core Principle: **Same immutable input to two isolated providers. Reveal only
after both are done. Nothing more.**

This is a **tool contract**, matching the precedent of `case-claim-kernel/CONTRACT.md`
and `gpt-mechanism-judge/CONTRACT.md` — not a governance/Employee Role contract.

## Origin

Stage 3 of the AUTONOMOUS MULTI-MODEL KNOWLEDGE SYSTEM (Phase 0 reuse archaeology,
response only). Builds true blind two-provider dispatch on top of Stage 1's
case/claim identity and Stage 2's proven-thin `JudgeProtocol` boundary. Stops at
"two independently produced, persisted artifacts exist" — no comparison, no
Falsifier, no Judge, no router, no lifecycle change. See §10 of the task.

## Scope of authority

`src/blind_analysis_kernel/{models,identity,packet,validator,ledger}.py` have
**zero import dependency on `ca_agents`, `case_claim_kernel`, `gpt_mechanism_judge`,
or `business_candidate_analyst`** — enforced by `tests/test_safety.py`.

`src/blind_analysis_kernel/dispatch.py`, and only that module, imports all three:
`ca_agents.same_mechanism_gate` (`GateAnomaly`, `profile_anomaly`, `PROFILE_PROMPT` —
unmodified), `ca_agents.mechanism_judge.ClaudeMechanismJudge` (unmodified),
`case_claim_kernel.identity.make_case_id` (Stage 1, unmodified), and
`gpt_mechanism_judge.judge.OpenAIMechanismJudge` (Stage 2, unmodified). This is the
blind-dispatch boundary itself, not an internal detail being bypassed.

Reads only two already-published CA files, read-only:
`constraint-archaeology-agents/data/{anomalies.json,observations.jsonl}`.

Writes only to `blind-analysis-kernel/data/analyses.jsonl` (append-only), and only
via `ledger.py`.

## Hard boundary — this tool MUST NOT

- modify `same_mechanism_gate.py`, `mechanism_judge.py`, `JudgeProtocol`, or any file
  in `gpt-mechanism-judge/` or `case-claim-kernel/` — content-hash-pinned in
  `tests/test_safety.py`.
- let `run_claude_analysis`/`run_gpt_analysis` accept any parameter beyond the one
  immutable `EvidencePacket` — checked structurally in
  `tests/test_dispatch_blindness.py` (`inspect.signature`). Neither function has, or
  could have, a code path to the other provider's result.
- give `EvidencePacket` a field shaped like a verdict, confidence, profile, or any
  other analysis output — `packet.py`'s field set is closed and tested
  (`tests/test_packet.py`).
- let a missing `ANTHROPIC_API_KEY`/`OPENAI_API_KEY` degrade into
  `INSUFFICIENT_DATA` or a fabricated result. The GitHub Actions job fails with
  `exit 1`; `dispatch.py`'s functions let `LLMError`/`OpenAIError` propagate
  uncaught. Never substitute one provider's credential or output for the other's.
- give the `claude-analysis` or `gpt-analysis` GitHub Actions job a `needs:` entry
  naming the other — only `merge-reveal` may depend on both. Statically checked in
  `tests/test_workflow_isolation.py` by parsing the real workflow YAML.
- use `actions/cache` for a model output, or write either analysis job's result to a
  path the other job could read before `merge-reveal` runs — isolated handoff is via
  `actions/upload-artifact`/`download-artifact` only, each job's own named artifact.
- overwrite or dedupe two different providers' analyses of the same run into one
  artifact — `identity.make_analysis_artifact_id(run_id, provider)` guarantees
  distinct ids; `ledger.py` is append-only.
- schedule this workflow. `workflow_dispatch` only, per task instructions — adding a
  `schedule:` trigger is out of scope for this contract entirely.
- semantically compare, rank, or combine the two revealed analyses, run a Falsifier
  or Judge over them, or change any CA/BCA lifecycle state — `merge-reveal`'s own
  script (`run_stage3_job.py merge`) stops at printing structural facts (do the ids
  differ, do the source case ids match, do the input hashes match) and persisting
  both artifacts. That is the STOP boundary (task §10); Stage 4 consumes what this
  package produces.

## Rights

- The right to report a workflow run's real-provider result as blocked/failed rather
  than fabricate success when a secret is missing — a correct, honest outcome for
  this stage, matching Stage 2's own `NOT RUN — SECRET REQUIRED` precedent at the
  script level, and a hard job failure at the GitHub Actions level.
- The right to persist two artifacts that disagree with each other. Disagreement is
  the point, not a defect (task §6: "Disagreement is valid and valuable").

## Responsibilities

- Report the exact SHA-256 of the evidence packet both providers actually consumed,
  on both artifacts, so agreement between `input_packet_sha256_claude` and
  `input_packet_sha256_gpt` is independently verifiable from the persisted record
  alone, not merely asserted.
- Keep `Case`/`Claim` semantic identity (`case_claim_kernel.identity`, Stage 1)
  completely untouched by which provider analyzed a case — `source_case_ids` is
  always a reference, never a place provider identity could leak in (mirrors
  `gpt_mechanism_judge.attribution`'s own rule, Stage 2 §0 correction).

## Executor independence

This contract binds the tool, not whoever runs it — same precedent as
`observation-agent/CONTRACT.md`.

## Revocation and change

This tool may be modified, extended, or retired at any time by direct repository
change. A change that would schedule this workflow automatically, add a semantic
comparison/Falsifier/Judge step, grant write access to any CA/BCA file or lifecycle
state, or let one analysis job's `needs:` reach the other is out of scope for this
contract entirely and needs a new, explicit human decision.
