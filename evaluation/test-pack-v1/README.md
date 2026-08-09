# Constraint Archaeology Test Pack v1

First systematic end-to-end measurement of the real same-mechanism gate
(`constraint-archaeology-agents/src/ca_agents/same_mechanism_gate.py`) against
10 pre-labeled synthetic pairs, spanning software, medicine, aviation,
logistics, finance, construction, manufacturing, and maintenance.

This is **not** a task to improve the method. It measures whether the gate
correctly distinguishes `SAME_MECHANISM`, `RELATED_DISTINCT`, and
`UNRESOLVED`, and whether it recognizes the same mechanism across unrelated
domains. See `report.md` for the findings; the headline is **7/10 correct, 0
false merges, 3 false splits, 0% SAME_MECHANISM recall** in this run.

## Why this directory is isolated

Nothing here touches production state:

- `constraint-archaeology-agents/data/observations.jsonl`, `anomalies.json`,
  `latest-evaluations.json`, `findings.jsonl` — **untouched**.
- `constraint-archaeology-agents/src/ca_agents/same_mechanism_gate.py` and
  every other frozen document under `docs/method/` and
  `tests/test_same_mechanism_gate.py` — **untouched**.
- All 10 test pairs are synthetic `GateAnomaly` objects constructed only in
  `ground-truth.json`, never written into any production ledger or snapshot.

## Files

| File | Role |
|---|---|
| `ground-truth.json` | 10 pairs with pre-declared expected verdict/edge, written and frozen **before** any execution. Not modified after the run. |
| `judge_cache.json` | Verbatim responses from the independent judge calls used for this run (see "Judge substitution" below). Never edited after collection. |
| `run_test_pack.py` | Harness. Imports `gate_pair`, `same_mechanism`, `profile_anomaly`, `PROFILE_PROMPT`, `COUNTERFACTUAL_PROMPT` directly from the real, unmodified gate module and replays `judge_cache.json` through the exact same prompt templates the production judge would receive. Writes `results.json`. |
| `results.json` | Actual output of the run: per-case verdict/edge, mechanism profiles, counterfactuals, reasons, confidence, pass/fail. |
| `report.md` | Metrics, per-question findings, and per-FAIL diagnosis (observation / evidence / expected / actual / failure location / likely cause). No fixes applied. |

Reproduce with:

```bash
cd evaluation/test-pack-v1
python3 run_test_pack.py
```

## Judge substitution — read this before trusting the numbers

The production judge (`ca_agents.mechanism_judge.ClaudeMechanismJudge`) calls
the real Anthropic API and requires `ANTHROPIC_API_KEY`. That key is **not
available** in this evaluation sandbox, and the task instructions explicitly
forbid a fake/scripted judge for the main run (scripted judges are for unit
tests only, e.g. `ScriptedJudge` in the frozen fixtures).

The closest faithful substitute available here: for every `profile()` and
`counterfactual()` call the real gate code would make, a **fresh, isolated
Claude subagent** was spawned with only that single formatted prompt (the
literal `PROFILE_PROMPT`/`COUNTERFACTUAL_PROMPT` text from
`same_mechanism_gate.py`) as its entire task — no visibility into the paired
case, no visibility into the ground truth, no memory of any other call. This
preserves the `JudgeProtocol` contract (independent profiling, symmetric
blind counterfactual testing) at the mechanism level, not just by convention.
`judge_cache.json` holds the raw, unedited outputs; `run_test_pack.py` proves
they are wired to the exact prompts the production code generates by
importing and formatting the real templates rather than hand-keying strings.

This is a genuine measurement, not a mock — but it is **not** a measurement
of `ClaudeMechanismJudge` specifically. `report.md` §10 recommends the
smallest next experiment to isolate whether the observed bias belongs to the
gate's decision rule or to this judge substitution.

## Follow-up: production-judge validation

That follow-up experiment was run: the same 10 frozen pairs through the real
`ca_agents.mechanism_judge.ClaudeMechanismJudge` (actual Anthropic API,
`claude-sonnet-4-5`), via a temporary, narrowly-scoped GitHub Actions
workflow (`.github/workflows/test-pack-v1-production-judge.yml`, now reverted
to inert `workflow_dispatch`) that reused the repo's existing
`ANTHROPIC_API_KEY` secret. See:

- `run_test_pack_production.py` — harness, same unmodified gate functions
- `results-production-judge.json` — raw output (model/provider info in `run_metadata`)
- `production-judge-comparison.md` — side-by-side isolated-vs-production table,
  metrics, per-case diagnostics, and a `GATE_DEFECT` / `JUDGE_ARTIFACT` / `MIXED`
  / `INSUFFICIENT_DATA` classification

Headline: **6/10 correct, 0 false merges (both runs), 2 false splits (down from
3), but 2 new incorrectly-resolved UNRESOLVED cases** that did not occur with
the isolated substitute — the production judge is measurably less willing to
self-report low confidence on thin evidence than the substitute was.

## Distribution

- 3 × SAME_MECHANISM (all cross-domain; one — TP-01 — deliberately across
  strongly different domains with unrelated vocabulary, software ↔ hospital)
- 4 × RELATED_DISTINCT (including the mandatory false-positive trap, TP-04:
  "fact doesn't exist yet" vs "fact exists but was never transmitted")
- 2 × UNRESOLVED (genuinely thin evidence, not merely "hard")
- 1 × adversarial near-match (TP-07: same domain, deliberately shared
  vocabulary, designed to tempt a false merge)

7 of the 10 pairs are cross-domain.
