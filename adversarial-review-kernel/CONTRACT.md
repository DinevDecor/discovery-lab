# Contract — Adversarial Review Kernel v0.1 (`adversarial-review-kernel/`)

Core Principle: **Difference is a fact, not a verdict. A model may falsify a claim
against the source evidence floor. Only a pure function decides the outcome.**

This is a **tool contract**, matching the precedent of `case-claim-kernel/CONTRACT.md`,
`gpt-mechanism-judge/CONTRACT.md`, and `blind-analysis-kernel/CONTRACT.md` — not a
governance/Employee Role contract.

## Origin

Stage 4 of the AUTONOMOUS MULTI-MODEL KNOWLEDGE SYSTEM. Consumes the two real,
already-durably-persisted `IndependentAnalysisArtifact` records Stage 3B wrote to
`blind-analysis-kernel/data/analyses.jsonl` for one run, and produces a deterministic
ADVANCE / WATCH / REJECT `JudgmentArtifact` — the smallest adversarial-review layer
that can sit on top of Stage 3's blind dispatch without becoming a free-form LLM
boss. Stops at "one deterministic decision, durably persisted" — no router, no
autonomous scheduling, no CA/BCA lifecycle change, no rewrite of the ambiguous
`carrier` schema. See the task's own §13 STOP boundary.

## Scope of authority

`src/adversarial_review_kernel/{models,identity,disagree,redact,prompts,validator,
ledger,judgment}.py` have **zero import dependency on `ca_agents`, `case_claim_kernel`,
`gpt_mechanism_judge`, or `blind_analysis_kernel`** — enforced by `tests/test_safety.py`.

`src/adversarial_review_kernel/falsify.py`, and only that module, imports across
packages: `ca_agents.llm.call_claude` and `gpt_mechanism_judge.openai_client
.call_openai` (the raw provider TRANSPORT functions, not `ClaudeMechanismJudge`/
`OpenAIMechanismJudge`, whose `SYSTEM` prompt is hardcoded to mechanism-profiling and
not swappable — this is the same two providers, a different task-specific prompt) and
`blind_analysis_kernel.dispatch.build_packet`/`blind_analysis_kernel.packet
.EvidencePacket` (to rebuild the same real evidence floor Stage 3 itself reads, not a
new evidence representation). This is the cross-falsification dispatch boundary
itself, matching `blind_analysis_kernel.dispatch`'s own precedent exactly.

`judgment.py` is the deterministic Judge. It contains **no model call, no network
call, no import of `ca_agents`/`gpt_mechanism_judge`/`blind_analysis_kernel`** —
checked by `tests/test_judgment.py::NoModelOrNetworkCallTests`. `decide()` is a pure
function: its entire input is already-computed structured data (a `Disagreement`
list and two `FalsificationArtifact`s); its output depends on nothing else.

Reads only two already-published, read-only sources: `blind-analysis-kernel/data/
analyses.jsonl` (Stage 3B's durable ledger) and `constraint-archaeology-agents/data/
{anomalies.json,observations.jsonl}` (the same real evidence floor Stage 3 uses to
build its `EvidencePacket`).

`select`/`disagree`/`claude-falsify`/`gpt-falsify`/`judge` write only to files the
caller names via `--out`/`--*-out` — never to any CA/BCA/blind-analysis-kernel path.
Only the `persist` subcommand writes `adversarial-review-kernel/data/
{falsifications.jsonl,judgments.jsonl}` (append-only, via `ledger.py`), and only on
the runner's own local, throwaway filesystem — never to Git. Only the
`persist-to-git` GitHub Actions job (`contents: write` — the only job in the
workflow with that permission) has those files committed and pushed to the default
branch. `persist` itself never calls git — the calling workflow step owns `git
add`/`commit`/`push`, exactly like `blind_analysis_kernel`'s own `persist`.

## Hard boundary — this tool MUST NOT

- modify `same_mechanism_gate.py`, `mechanism_judge.py`, `llm.py`, `openai_client.py`,
  `blind_analysis_kernel/dispatch.py`, or `blind_analysis_kernel/packet.py` —
  content-hash-pinned in `tests/test_safety.py::PinnedFilesUntouchedTests`.
- change CA/BCA lifecycle state, or write to any CA/BCA ledger — checked structurally:
  only `ledger.py` may open a file in a writing mode anywhere in this package
  (`tests/test_safety.py::NoWriteModeOutsideLedgerTests`), and `ledger.py` itself
  never even mentions a CA/BCA/blind-analysis-kernel data path
  (`tests/test_safety.py::NeverWritesToCaBcaOrBlindAnalysisLedgerTests`).
- let a Falsifier see the critic's own prior original analysis, or the other
  Falsifier's output. `run_claude_falsifier(packet, gpt_analysis, gpt_artifact_id,
  disagreements)` has no parameter through which Claude's own original analysis or
  GPT's Falsifier output could arrive; `run_gpt_falsifier` is the mirror image —
  checked structurally (`inspect.signature`) in
  `tests/test_falsify_blindness.py::FalsifierSignatureTests`, and behaviorally with
  synthetic markers in the same file's `RealRunFalsificationBlindnessTests`.
  `redact.redact_for_critic` is the second half of this guarantee: it strips the
  critic's own value out of a raw `Disagreement` before any prompt is ever built,
  since a raw `Disagreement` carries both providers' values.
- let `extract_disagreements`/`redact_for_critic` make a semantic judgment. Both are
  pure structural functions — a `!=` diff and a strip, respectively — proven by
  `tests/test_disagree.py::NoSemanticDecisionTests` (the `Disagreement` dataclass has
  no verdict-shaped field, and the extractor's signature takes no evidence
  parameter at all).
- let the deterministic Judge be, or become, an LLM. `judgment.py` makes zero model
  or network calls, by construction and by static test
  (`tests/test_judgment.py::NoModelOrNetworkCallTests`). The only thing a model may
  ever do in this package is falsify (classify one field of the analysis it was
  shown), never decide the final ADVANCE/WATCH/REJECT outcome.
- let `SCHEMA_AMBIGUITY` be treated as a hard falsification, a model failure, or
  grounds for REJECT. A material `SCHEMA_AMBIGUITY` finding on any field caps the
  judgment at WATCH regardless of every other field — checked in
  `tests/test_judgment.py::WatchTests` including the case where one Falsifier calls
  a field `CHALLENGED_BY_SOURCE` while the other calls the SAME field
  `SCHEMA_AMBIGUITY` (does not reject — an ambiguous-schema field cannot
  simultaneously be a clean hard falsification).
- let `INSUFFICIENT_DATA` ever produce REJECT. The only guard around
  `reject_triggers.append(...)` in `judgment.py` checks `CHALLENGED_BY_SOURCE`
  only — statically proven never to mention `INSUFFICIENT_DATA` on that line, in
  `tests/test_judgment.py::InsufficientDataNeverRejectTests`.
- invent a REJECT condition merely so all three outcomes are reachable. The one
  REJECT rule this package implements (`CHALLENGED_BY_SOURCE`, `material=True`, no
  counter-`SCHEMA_AMBIGUITY` on the same field) uses only vocabulary the task itself
  defines, and is exercised by real synthetic unit tests
  (`tests/test_judgment.py::RejectTests`) — it is not decorative.
- let a Falsifier's malformed/unparseable/missing-field response silently permit
  ADVANCE. `falsify.py::_build_findings` degrades any parse/format ambiguity to
  `INSUFFICIENT_DATA` with `material=True` — fail CONSERVATIVE, toward WATCH, never
  toward ADVANCE.
- mutate `blind-analysis-kernel/data/analyses.jsonl` or either original analysis
  dict in place. Both original `IndependentAnalysisArtifact` records are read-only
  inputs throughout this package; `findings.jsonl`-style append-only discipline
  applies equally here (`falsifications.jsonl`/`judgments.jsonl` are both
  append-only, idempotent-by-id, never rewritten — `tests/test_ledger.py`).
- give the `claude-falsify` or `gpt-falsify` GitHub Actions job a `needs:` entry
  naming the other — only `deterministic-judge` may depend on both. Statically
  checked in `tests/test_workflow_isolation.py` by parsing the real workflow YAML.
- let any job other than `persist-to-git` declare `permissions: contents: write` or
  run `git push`. Statically checked in
  `tests/test_workflow_isolation.py::PersistToGitWriteBoundaryTests`.
- force-push, or give up silently on a push conflict. `persist-to-git` retries a
  bounded number of times (`git pull --rebase` between attempts) and fails the job
  (`exit 1`) if it still cannot push, matching Stage 3B's own precedent exactly.
- let `persist-to-git` read `ANTHROPIC_API_KEY`/`OPENAI_API_KEY` — it never calls a
  model, only durably records artifacts two other jobs already produced.
- stage anything beyond `adversarial-review-kernel/data/falsifications.jsonl` and
  `adversarial-review-kernel/data/judgments.jsonl` in the persistence commit.
- schedule this workflow. `workflow_dispatch` only.

## Rights

- The right to persist a REJECT, a WATCH, or a schema ambiguity finding as the most
  informative output this stage has produced so far — a refused advance is not a
  failure of the pipeline, matching `blind-analysis-kernel/CONTRACT.md`'s own
  "disagreement is valid and valuable" precedent, extended one layer further.
- The right to report `INSUFFICIENT DATA` (via `INSUFFICIENT_DATA` findings that cap
  the judgment at WATCH) rather than fabricate a resolved reading when the source
  evidence genuinely does not settle a disputed field.

## Responsibilities

- Report the exact `input_packet_sha256` both Falsifiers actually consumed on both
  `FalsificationArtifact`s, and refuse to judge (`SystemExit`, via
  `run_stage4_job.py cmd_judge`) if they disagree, or if either falsification's
  `target_artifact_id` does not match the analysis it was actually supposed to have
  critiqued — the same "both providers, one immutable input, verified not merely
  asserted" invariant Stage 3 established, applied fresh to Stage 4's own packet.
- Keep the four-way classification vocabulary (`SUPPORTED_BY_SOURCE`,
  `CHALLENGED_BY_SOURCE`, `INSUFFICIENT_DATA`, `SCHEMA_AMBIGUITY`) exactly as the
  task defines it — `SCHEMA_AMBIGUITY` is never collapsed into "model disagreement"
  or "falsification"; it names a genuinely distinct condition (the `PROFILE_PROMPT`
  contract itself being ambiguous, not either model being wrong).

## Executor independence

This contract binds the tool, not whoever runs it — same precedent as
`observation-agent/CONTRACT.md`.

## Revocation and change

This tool may be modified, extended, or retired at any time by direct repository
change. A change that would let the deterministic Judge become a model call,
schedule this workflow automatically, grant write access to any CA/BCA/
blind-analysis-kernel file, rewrite `PROFILE_PROMPT`/`same_mechanism_gate.py` to
resolve the `carrier` ambiguity, or let `claude-falsify`/`gpt-falsify` see each
other's output before both finish is out of scope for this contract entirely and
needs a new, explicit human decision.
