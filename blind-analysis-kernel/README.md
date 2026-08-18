# Blind Analysis Kernel v0.1

Stage 3 of the autonomous multi-model knowledge system. True blind two-provider
dispatch: one immutable evidence packet, two isolated analysis jobs (Claude, GPT),
neither able to see the other's output until a separate merge/reveal step. See
`CONTRACT.md`.

## What this is

- `src/blind_analysis_kernel/packet.py` — `EvidencePacket`: the one immutable input
  both providers consume. Closed field set (no analysis-shaped field can sneak in).
- `src/blind_analysis_kernel/models.py` — `IndependentAnalysisArtifact`: the one
  output shape, one per (run_id, provider).
- `src/blind_analysis_kernel/identity.py` — deterministic `artifact_id` from
  `(run_id, provider)` only — never from case identity or analysis content.
- `src/blind_analysis_kernel/dispatch.py` — the only module that imports
  `ca_agents`/`case_claim_kernel`/`gpt_mechanism_judge`. `run_claude_analysis(packet)`
  and `run_gpt_analysis(packet)` each take ONLY the packet.
- `src/blind_analysis_kernel/ledger.py` — append-only persistence, never overwrites,
  never dedupes two providers' analyses of the same run into one artifact.
- `run_stage3_job.py` — CLI with four roles (`prepare`, `claude`, `gpt`, `merge`),
  one per GitHub Actions job.
- `.github/workflows/stage3-blind-dispatch.yml` — `workflow_dispatch`-only. Four
  jobs: `prepare-input` → `{claude-analysis, gpt-analysis}` (no `needs:` on each
  other) → `merge-reveal` (`needs: [claude-analysis, gpt-analysis]`).

## Running it locally (offline pieces)

```
python3 run_stage3_job.py prepare --anomaly-id ANOM-0001 --run-id local-test --out packet.json
python3 run_stage3_job.py claude --packet packet.json --out claude-analysis.json   # requires ANTHROPIC_API_KEY
python3 run_stage3_job.py gpt --packet packet.json --out gpt-analysis.json          # requires OPENAI_API_KEY
python3 run_stage3_job.py merge --claude-artifact claude-analysis.json --gpt-artifact gpt-analysis.json
```

Without the relevant key set, `claude`/`gpt` fail loudly (non-zero exit, uncaught
`LLMError`/`OpenAIError`) — by design, per `CONTRACT.md`.

## Running the real blind dispatch

Trigger `Stage 3 Blind Dispatch (manual only)` via `workflow_dispatch` in GitHub
Actions, with both `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` configured as repository
secrets. If either is missing, that job fails loudly rather than substituting a
fallback.

## Tests

```
python3 -m unittest discover -s tests -v
```

All tests are offline and deterministic. `tests/test_dispatch_blindness.py` proves
the blindness invariant against a packet built from real, already-committed CA data
(mocked `call_claude`/`call_openai`, no real network call).
`tests/test_workflow_isolation.py` statically parses the real workflow YAML to prove
job isolation.
