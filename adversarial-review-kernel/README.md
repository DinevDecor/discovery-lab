# Adversarial Review Kernel v0.1

Stage 4 of the autonomous multi-model knowledge system. Consumes the two real,
already-durably-persisted `IndependentAnalysisArtifact` records Stage 3B wrote for
one run, has each provider blindly falsify the OTHER provider's analysis against the
source evidence floor only, and runs a pure deterministic function over the results
to produce one ADVANCE / WATCH / REJECT `JudgmentArtifact`. No LLM is ever the final
judge. See `CONTRACT.md`.

## What this is

- `src/adversarial_review_kernel/models.py` — `Disagreement`, `FalsificationFinding`,
  `FalsificationArtifact`, `JudgmentArtifact`. The four-way classification vocabulary
  (`SUPPORTED_BY_SOURCE`, `CHALLENGED_BY_SOURCE`, `INSUFFICIENT_DATA`,
  `SCHEMA_AMBIGUITY`) and the three judgment statuses (`ADVANCE`, `WATCH`, `REJECT`).
- `src/adversarial_review_kernel/identity.py` — deterministic ids from
  `(run_id, critic_provider)` and `(run_id)` only.
- `src/adversarial_review_kernel/disagree.py` — `extract_disagreements`: a pure `!=`
  diff between the two analyses. Never decides which side is correct.
- `src/adversarial_review_kernel/redact.py` — `redact_for_critic`: strips the
  critic's own value out of each disagreement before it is ever shown to that
  critic — the enforcement point for "Claude must not see Claude's own value".
- `src/adversarial_review_kernel/prompts.py` — the Falsifier prompt template: real
  source evidence, the verbatim `PROFILE_PROMPT` template text, the analysis under
  review, and the redacted disagreement fields — nothing else.
- `src/adversarial_review_kernel/falsify.py` — the only module that imports
  `ca_agents`/`gpt_mechanism_judge`/`blind_analysis_kernel`. `run_claude_falsifier
  (packet, gpt_analysis, gpt_artifact_id, disagreements)` and `run_gpt_falsifier
  (packet, claude_analysis, claude_artifact_id, disagreements)` — neither has a
  parameter for the critic's own analysis or the other Falsifier's output.
- `src/adversarial_review_kernel/judgment.py` — `decide(...)`: the deterministic
  Judge. Zero model or network calls. REJECT requires a material
  `CHALLENGED_BY_SOURCE` finding with no counter-`SCHEMA_AMBIGUITY` on the same
  field; material `SCHEMA_AMBIGUITY` caps at WATCH; `INSUFFICIENT_DATA` never
  contributes to REJECT.
- `src/adversarial_review_kernel/validator.py` / `ledger.py` — artifact-shape
  validation and append-only, idempotent-by-id persistence, matching every prior
  stage's own ledger convention.
- `run_stage4_job.py` — CLI with six roles (`select`, `disagree`, `claude-falsify`,
  `gpt-falsify`, `judge`, `persist`), one per GitHub Actions job. `judge` refuses
  (non-zero exit) to proceed if the two Falsifiers' `input_packet_sha256` differ, or
  if either falsification's `target_artifact_id` does not match the analysis it was
  supposed to critique.
- `.github/workflows/stage4-adversarial-review.yml` — `workflow_dispatch`-only. Five
  jobs: `select-disagreements` → `{claude-falsify, gpt-falsify}` (no `needs:` on
  each other) → `deterministic-judge` (`needs: [claude-falsify, gpt-falsify]`) →
  `persist-to-git` (`needs: [deterministic-judge]`, the only job with `permissions:
  contents: write`, the only job that ever runs `git push`).

## Running it locally (offline pieces)

```
python3 run_stage4_job.py select --run-id 32142997999 \
  --claude-out claude-analysis.json --gpt-out gpt-analysis.json
python3 run_stage4_job.py disagree --claude-artifact claude-analysis.json \
  --gpt-artifact gpt-analysis.json --out disagreements.json
python3 run_stage4_job.py claude-falsify --gpt-artifact gpt-analysis.json \
  --disagreements disagreements.json --anomaly-id ANOM-0001 --run-id 32142997999 \
  --out claude-falsification.json                                    # requires ANTHROPIC_API_KEY
python3 run_stage4_job.py gpt-falsify --claude-artifact claude-analysis.json \
  --disagreements disagreements.json --anomaly-id ANOM-0001 --run-id 32142997999 \
  --out gpt-falsification.json                                       # requires OPENAI_API_KEY
python3 run_stage4_job.py judge --claude-artifact claude-analysis.json \
  --gpt-artifact gpt-analysis.json --disagreements disagreements.json \
  --claude-falsification claude-falsification.json --gpt-falsification gpt-falsification.json \
  --out judgment.json
python3 run_stage4_job.py persist --claude-falsification claude-falsification.json \
  --gpt-falsification gpt-falsification.json --judgment judgment.json
```

Without the relevant key set, `claude-falsify`/`gpt-falsify` fail loudly (non-zero
exit, uncaught `LLMError`/`OpenAIError`) — by design, per `CONTRACT.md`. `persist`
never calls git itself — it only writes `data/falsifications.jsonl` and
`data/judgments.jsonl` locally; `git add`/`commit`/`push` are the calling workflow
step's job.

## Running the real adversarial review

Trigger `Stage 4 Adversarial Review (manual only)` via `workflow_dispatch` in GitHub
Actions, with both `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` configured as repository
secrets, and `run_id` set to the real, already-persisted Stage 3B run to adjudicate
(default `32142997999`). This does NOT re-run or replace the original analyses —
`select-disagreements` reads them read-only out of `blind-analysis-kernel/data/
analyses.jsonl`. If either falsification job's key is missing, that job fails loudly
rather than substituting a fallback. If Git persistence fails, `persist-to-git`
fails and the whole run is not considered successful, even though both model calls
succeeded — see `CONTRACT.md`'s "Hard boundary" section.

## Tests

```
python3 -m unittest discover -s tests -v
```

All tests are offline and deterministic. `tests/test_falsify_blindness.py` proves
the cross-falsification blindness invariant against real, already-committed run
`32142997999` data (mocked `call_claude`/`call_openai`, no real network call), using
synthetic marker values where a real-data coincidence (GPT's own real `carrier`
value happens to equal the raw evidence packet's `current_carrier` field — itself
evidence of the real schema ambiguity) would otherwise make a naive substring check
unreliable. `tests/test_judgment.py` exercises every branch of the deterministic
Judge by hand-constructed `FalsificationArtifact`s — no model call needed, since
`decide()` is a pure function over already-computed data.
`tests/test_workflow_isolation.py` statically parses the real workflow YAML to prove
job isolation and the `persist-to-git` write boundary, mirroring
`blind-analysis-kernel/tests/test_workflow_isolation.py` exactly.
`tests/test_cli.py` covers the `judge`/`persist` subcommands' structural-integrity
gates and idempotent, append-only, no-git-call behavior directly.
