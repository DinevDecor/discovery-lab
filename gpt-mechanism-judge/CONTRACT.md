# Contract — GPT Mechanism Judge v0.1 (`gpt-mechanism-judge/`)

Core Principle: **Satisfy the existing `JudgeProtocol` boundary with a second
provider. Nothing more.**

This is a **tool contract**, matching the precedent of `observation-agent/CONTRACT.md`
and `case-claim-kernel/CONTRACT.md` — not a governance/Employee Role contract.

## Origin

Stage 2 of the AUTONOMOUS MULTI-MODEL KNOWLEDGE SYSTEM (Phase 0 reuse archaeology,
response only). Phase 0 found that `ca_agents.same_mechanism_gate.JudgeProtocol`
already existed as a provider-agnostic, two-method interface, unused by any second
implementation. This package is the first real second implementation, and stops
exactly there — no dispatch, no comparison, no Falsifier, no Judge, no router.

## Scope of authority

`src/gpt_mechanism_judge/` (the library: `openai_client.py`, `judge.py`,
`attribution.py`) has **zero import dependency on `ca_agents`, `case_claim_kernel`,
or any other package** — `OpenAIMechanismJudge` satisfies `JudgeProtocol` structurally
(Python `Protocol` is duck-typed), never by importing it. This is what "genuinely
thin adapter" means in practice: the library is usable standing completely alone.

`run_stage2_acceptance.py`, and only that one file, imports
`ca_agents.same_mechanism_gate` (`GateAnomaly`, `gate_pair`) and
`case_claim_kernel.identity` (`make_case_id`) — because proving "the real,
unmodified `gate_pair()` accepts this judge" requires calling the real function.
That import is the boundary under test, not an internal detail being bypassed.

Reads only two already-published CA files, read-only:
`constraint-archaeology-agents/data/anomalies.json`,
`constraint-archaeology-agents/data/observations.jsonl`.

Writes nothing to disk. This package has no ledger, no data directory, no persisted
state — `run_stage2_acceptance.py` prints its report to stdout only.

## Hard boundary — this tool MUST NOT

- modify `constraint-archaeology-agents/src/ca_agents/same_mechanism_gate.py`, or
  any other CA/BCA source file, ever. Stage 2 either fits through the existing
  `JudgeProtocol` boundary unmodified, or it reports
  `THIN ADAPTER HYPOTHESIS: FALSIFIED` — it does not force a change to make itself fit.
- hardcode, log, or persist `OPENAI_API_KEY` anywhere — the key is read from the
  environment inside `call_openai()` on every call and appears only in that one
  request's `Authorization` header. Enforced by `tests/test_safety.py`'s static scan
  and `tests/test_openai_client.py`'s dynamic check that no exception message or log
  line ever contains the key value.
- dispatch two providers against the same case, compare their outputs, run a
  Falsifier, run a Judge, write to any lifecycle state, promote anything, or persist
  an artifact anywhere — all explicitly out of scope for this stage.
- put provider identity inside a Case's or a Claim's semantic identity
  (`case_claim_kernel.identity`, Stage 1, untouched). `AttributedAnalysis` carries
  `provider`/`model` alongside a `source_case_id`, never folded into it.
- silently swallow a transport failure (`OpenAIError` — missing key, HTTP/network
  error) as if it were "the model said nothing useful." Only a genuinely
  malformed/unparseable response body degrades to the gate's existing
  undecidable/insufficient-data shapes — exactly the split
  `ca_agents.mechanism_judge.ClaudeMechanismJudge` already established.
- fabricate a real-provider run result. `run_stage2_acceptance.py` reports
  `NOT RUN — SECRET REQUIRED` verbatim when `OPENAI_API_KEY` is absent, never a
  synthetic success.

## Rights

- The right to report `NOT RUN — SECRET REQUIRED` instead of a fabricated result
  when no credential is available — a correct, honest, and complete outcome for this
  stage, not a defect to work around.
- The right to return `{}` from `.profile()` or `{"removes_failure": None, ...}` from
  `.counterfactual()` on a malformed model response — the gate's own existing
  evidence-floor and undecidable-counterfactual checks already turn either into
  `INSUFFICIENT_DATA`/`UNRESOLVED`, so this is a correct pass-through, not a defect.

## Responsibilities

- Document the exact default model name (`openai_client.DEFAULT_MODEL`) and note
  that it should be reconfirmed against OpenAI's current model list before any real
  spend, rather than silently trusting a hardcoded guess.
- Record `provider`, `model`, `created_at`, and `source_case_id`/`source_artifact_ids`
  on every `AttributedAnalysis` — never a partial attribution.
- Keep `OpenAIMechanismJudge`'s `SYSTEM` prompt and error-handling contract aligned
  with `ClaudeMechanismJudge`'s, so a difference in gate outcome reflects a real
  difference between providers, not a difference in how each was asked.

## Executor independence

This contract binds the tool, not whoever runs it — same precedent as
`observation-agent/CONTRACT.md`.

## Revocation and change

This tool may be modified, extended, or retired at any time by direct repository
change. A change that would grant it write access to any CA/BCA file or any lifecycle
state, a persisted ledger, blind dispatch, a Falsifier/Judge role, or automatic
promotion of anything is out of scope for this contract entirely and needs a new,
explicit human decision.
