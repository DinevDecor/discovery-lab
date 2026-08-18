# GPT Mechanism Judge v0.1

Stage 2 of the autonomous multi-model knowledge system. Proves that
`ca_agents.same_mechanism_gate.JudgeProtocol` — the existing, already-real interface
`ClaudeMechanismJudge` implements — is a genuinely thin boundary a second model
provider can satisfy without any change to `same_mechanism_gate.py`.

Not blind dispatch, not cross-model comparison, not a Falsifier or Judge, not a
router, not persistence. See `CONTRACT.md`.

## What this is

- `src/gpt_mechanism_judge/openai_client.py` — raw OpenAI Chat Completions transport
  (stdlib `urllib.request` only, mirrors `ca_agents/llm.py`'s shape exactly).
- `src/gpt_mechanism_judge/judge.py` — `OpenAIMechanismJudge`, two methods
  (`.profile()`, `.counterfactual()`), same signatures and error-handling contract as
  `ca_agents.mechanism_judge.ClaudeMechanismJudge`. Satisfies `JudgeProtocol`
  structurally — this module has zero import dependency on `ca_agents`.
- `src/gpt_mechanism_judge/attribution.py` — `AttributedAnalysis`: wraps a
  `MechanismProfile`/`GateDecision` with `provider`/`model`/`created_at`/
  `source_case_id`/`source_artifact_ids`. Not a ledger — nothing here persists.
- `run_stage2_acceptance.py` — loads two real, already-committed CA anomalies, builds
  the real `GateAnomaly` pair, and calls the real, unmodified `gate_pair()` with an
  `OpenAIMechanismJudge`.

## Running the acceptance script

```
OPENAI_API_KEY=... python3 run_stage2_acceptance.py
```

Without `OPENAI_API_KEY` set, it still builds and prints everything computable
offline (the real anomaly pair, both case_ids, provider/model that would be used) and
reports `"real_provider_run": "NOT RUN — SECRET REQUIRED"` — not a fabricated result.

## Tests

```
python3 -m unittest discover -s tests -v
```

All tests are offline and deterministic — `call_openai` is mocked/patched throughout,
exactly like `constraint-archaeology-agents/tests/test_mechanism_judge.py` mocks
`call_claude`. No test in this package makes a real network call.
