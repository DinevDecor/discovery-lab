# Blind Analysis Kernel v0.1

Stage 3 of the autonomous multi-model knowledge system. True blind two-provider
dispatch: one immutable evidence packet, two isolated analysis jobs (Claude, GPT),
neither able to see the other's output until a separate merge/reveal step, then
(Stage 3B) durable Git persistence of both artifacts plus a run manifest. See
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
- `src/blind_analysis_kernel/ledger.py` — append-only persistence of both artifacts,
  never overwrites, never dedupes two providers' analyses of the same run into one.
- `src/blind_analysis_kernel/manifest.py` — Stage 3B: `RunManifest` +
  `RunManifestLedger`, the smallest additional record needed to tie one Claude
  artifact and one GPT artifact to the same run, workflow run id, and repository
  commit — without duplicating either artifact's own content.
- `run_stage3_job.py` — CLI with five roles (`prepare`, `claude`, `gpt`, `merge`,
  `persist`), one per GitHub Actions job. `merge` and `persist` both refuse (non-zero
  exit) to proceed if the two providers' artifacts disagree on `input_packet_sha256`,
  `source_case_ids`, `run_id`, or share an `artifact_id`.
- `.github/workflows/stage3-blind-dispatch.yml` — `workflow_dispatch`-only. Five
  jobs: `prepare-input` → `{claude-analysis, gpt-analysis}` (no `needs:` on each
  other) → `merge-reveal` (`needs: [claude-analysis, gpt-analysis]`) →
  `persist-to-git` (`needs: [merge-reveal]`, the only job with `permissions:
  contents: write`, the only job that ever runs `git push`).

## Running it locally (offline pieces)

```
python3 run_stage3_job.py prepare --anomaly-id ANOM-0001 --run-id local-test --out packet.json
python3 run_stage3_job.py claude --packet packet.json --out claude-analysis.json   # requires ANTHROPIC_API_KEY
python3 run_stage3_job.py gpt --packet packet.json --out gpt-analysis.json          # requires OPENAI_API_KEY
python3 run_stage3_job.py merge --claude-artifact claude-analysis.json --gpt-artifact gpt-analysis.json
python3 run_stage3_job.py persist --claude-artifact claude-analysis.json --gpt-artifact gpt-analysis.json \
  --workflow-run-id local-test --head-sha $(git rev-parse HEAD)
```

Without the relevant key set, `claude`/`gpt` fail loudly (non-zero exit, uncaught
`LLMError`/`OpenAIError`) — by design, per `CONTRACT.md`. `persist` never calls git
itself — it only writes `data/analyses.jsonl` and `data/runs.jsonl` locally; `git
add`/`commit`/`push` are the calling workflow step's job (see the `persist-to-git`
job in the workflow file for the exact commands, including its bounded-retry
`git pull --rebase` loop).

## Running the real blind dispatch

Trigger `Stage 3 Blind Dispatch (manual only)` via `workflow_dispatch` in GitHub
Actions, with both `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` configured as repository
secrets. If either is missing, that job fails loudly rather than substituting a
fallback. If Git persistence fails (e.g. a push conflict that outlives the bounded
retry), `persist-to-git` fails and the whole run is not considered successful, even
though both model calls succeeded — see `CONTRACT.md`'s "Hard boundary" section.

## Tests

```
python3 -m unittest discover -s tests -v
```

All tests are offline and deterministic. `tests/test_dispatch_blindness.py` proves
the blindness invariant against a packet built from real, already-committed CA data
(mocked `call_claude`/`call_openai`, no real network call).
`tests/test_workflow_isolation.py` statically parses the real workflow YAML to prove
job isolation, and its `PersistToGitWriteBoundaryTests` class proves the Stage 3B
write boundary (only `persist-to-git` has `contents: write`, only it runs `git
push`, it never sees a model secret, its retry is bounded and never force-pushes).
`tests/test_cli_persist.py` and `tests/test_manifest.py` cover the `persist`
subcommand and the run-manifest ledger directly, including the idempotent-rerun and
structural-integrity-refusal paths.
