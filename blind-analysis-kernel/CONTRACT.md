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

Stage 3B (durable Git persistence) extends this: the two artifacts and a run
manifest are durably committed to Git-tracked files after merge-reveal verifies
structural integrity, so the knowledge system's institutional-memory backbone is
Git itself, not a GitHub Actions build artifact with a retention window. Nothing
about the STOP boundary above changes — persistence is recording, not judgment.

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

`prepare`/`claude`/`gpt`/`merge` write only to `blind-analysis-kernel/data/
analyses.jsonl` (append-only, via `ledger.py`) on the runner's own local, throwaway
filesystem — never to Git. Only the `persist` subcommand, invoked only by the
`persist-to-git` GitHub Actions job (`contents: write` — the only job in the
workflow with that permission), writes `blind-analysis-kernel/data/analyses.jsonl`
and `blind-analysis-kernel/data/runs.jsonl` and has those files committed and
pushed to the default branch. `persist` itself never calls git — the calling
workflow step owns `git add`/`commit`/`push`, so `persist`'s own behavior stays
fully unit-testable offline like every other subcommand.

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
  differ, do the source case ids match, do the input hashes match). That is the
  STOP boundary (task §10); Stage 4 consumes what this package produces.
- let any job other than `persist-to-git` declare `permissions: contents: write` or
  run `git push` — every other job (`prepare-input`, `claude-analysis`,
  `gpt-analysis`, `merge-reveal`) explicitly declares `contents: read`. Statically
  checked in `tests/test_workflow_isolation.py::PersistToGitWriteBoundaryTests`.
- persist a structurally broken pair. `persist` re-runs the same integrity checks
  `merge` already ran (matching `input_packet_sha256`, matching `source_case_ids`,
  distinct `artifact_id`) before writing anything, and refuses (non-zero exit) if
  they disagree — defense in depth, not reliance on `merge` having run first.
- force-push, or give up silently on a push conflict. `persist-to-git` retries a
  bounded number of times (`git pull --rebase` between attempts) and fails the job
  (`exit 1`) if it still cannot push — a successful model call followed by failed
  Git persistence is never reported as a successful run (task §6).
- let `persist-to-git` read `ANTHROPIC_API_KEY`/`OPENAI_API_KEY` — it never calls a
  model, only durably records artifacts two other jobs already produced.
- stage anything beyond `blind-analysis-kernel/data/analyses.jsonl` and
  `blind-analysis-kernel/data/runs.jsonl` in the persistence commit — no CA/BCA
  path, no other file, ever appears in that `git add`.

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
