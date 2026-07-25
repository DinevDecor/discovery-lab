# Validation Report — Research Reality Sensor 001 (`EXEC-010`)

## Test suite

67 tests, all passing, across `research-sensor/tests/`. Mapped to
`EXEC-010`'s own 12 required categories:

| Required category | Test file(s) |
|---|---|
| Source validation | `test_source_validation.py` (2 tests), `test_config.py::TestSourceRegistryTrustClassification` (4 tests) |
| Duplicate detection | `test_dedup.py` (5 tests) |
| Evidence separation (fact vs. interpretation) | `test_registry.py::TestEvidenceSeparation` (3 tests) |
| Research registry stability | `test_registry.py::TestResearchRegistryStabilityAndRegression` (2 tests) |
| Stable IDs | `test_registry.py::TestStableIds` (3 tests) |
| Repeatability | `test_cli_stability.py::TestPureDeterminism` (1 test, 3 runs internally) |
| Read-only verification | `test_safety.py` (7 tests), `test_cli_stability.py::TestReadOnlyVerification` (2 tests) |
| Headquarters compatibility | `test_headquarters_compatibility.py` (2 tests) |
| Regression | `test_cli_stability.py::TestRegressionAgainstSelfGeneratedReports` (1 test) |
| Experiment extraction structure | `test_experiments.py::TestExperimentExtractionStructure` (5 tests), `TestHighValueGating` (3 tests) |
| Project relevance | `test_relevance.py` (4 tests) |
| WATCH classification | `test_relevance.py::test_no_match_falls_back_to_watch_class`, `test_registry.py`, `test_experiments.py::test_watch_only_is_never_high_value` |

Additional coverage beyond the 12 named categories: `test_trust.py` (9
tests, confidence-rule enforcement including the COMMUNITY-hint-alone
rule), `test_brief.py` (5 tests), `test_capture.py` (6 tests, malformed
feed handling), `test_cli_stability.py::TestEmptyResultHandling` (1
test).

Run: `cd research-sensor/tests && python3 -m unittest discover -s . -p "test_*.py"` → `Ran 67 tests ... OK`.

## Real external capture

Performed against the fixed Source Registry, within the fixed 30-day
window (2026-06-25 to 2026-07-25) and a fixed processing budget of 30:
**14 real operations** (12 `WebSearch`, 2 `WebFetch` attempts — both
blocked with HTTP 403; see Known Limitations). Produced **7 raw
captures**, committed at
`validation-dataset/raw-captures-2026-06-25-to-2026-07-25.json`,
spanning all 5 Primary Observation Domains:

- **A. AI for Scientific Discovery** (1 capture): "Rethinking
  Scientific Discovery in the Agentic Era" (arXiv, PREPRINT).
- **B. Multi-Agent Research** (2 captures): "Cache Merging as a
  Convergent Replicated State for Multi-Agent Latent Reasoning" and
  "What LLM Agents Say When No One Is Watching" (both arXiv, PREPRINT,
  correctly kept as separate signals — different research ideas,
  despite sharing a domain).
- **C. Knowledge Systems** (1 capture): "REAL: A Reasoning-Enhanced
  Graph Framework for Long-Term Memory Management of LLMs" (arXiv,
  PREPRINT).
- **D. Validation Methodology** (2 captures): Google DeepMind's
  "Conjecture Machines" policy piece (SECONDARY source,
  NOTABLE_LAB_PREPRINT — the one MEDIUM-confidence signal in this
  dataset) and a Hacker News discussion on benchmark exploitation
  (COMMUNITY, COMMUNITY_HINT — correctly excluded from the registry;
  see below).
- **E. Cognitive Architectures** (1 capture): "Cognitive-structured
  Multimodal Agent for Multimodal Understanding, Generation, and
  Editing" (arXiv, PREPRINT).

All 7 captures are real, sourced, dated (with 3 honest date-precision
caveats — see Known Limitations), and quoted from what was actually
retrieved via `WebSearch` — nothing was invented to fill a domain or
project slot.

## Real processing result

`captures_loaded: 7`, `captures_skipped: 0`, `clusters: 7` (no exact
duplicates found in this real window — an honest observation, not a
gap; the dedup mechanism itself is fully exercised by `test_dedup.py`'s
synthetic cases), `discovery_hints_skipped: 1` (the Hacker News item —
`build_signal` correctly returned `None` for a COMMUNITY_HINT-only
cluster, per Trust Policy), `new_signals: 6`, `registry_total: 6`,
`validation_warnings: []` (every real source was already in the fixed
Registry).

| research_id | Domain | Confidence | Affected projects |
|---|---|---|---|
| RES-0001 | AI for Scientific Discovery | LOW | Generative Discovery Engine |
| RES-0002 | Multi-Agent Research | LOW | Discovery Lab, Dinev Assistant |
| RES-0003 | Multi-Agent Research | LOW | Discovery Lab |
| RES-0004 | Knowledge Systems | LOW | KOD |
| RES-0005 | Cognitive Architectures | LOW | KOD, Dinev Assistant |
| RES-0006 | Validation Methodology | **MEDIUM** | Trust Engine |

Only RES-0006 reached `MEDIUM`/`HIGH` confidence with a named project,
so it is the only signal carrying a `possible_experiments` entry — see
`docs/EXPERIMENT-EXTRACTION-POLICY.md` for why this is policy working
correctly, not a shortfall.

## 3x repeated execution

Command, run three times against the committed validation dataset with
a fixed `run_timestamp` (isolating the determinism proof from
wall-clock variance):

```
python3 -c "
from research_sensor.cli import run_once
run_once('validation-dataset/raw-captures-2026-06-25-to-2026-07-25.json',
          'config/source-registry.json', 'config/relevance-gate.json',
          '<dir>', run_timestamp='2026-07-25T00:00:00Z')
"
```

Run against **three fresh, isolated `reports-dir`s** (pure-determinism
variant): `research-registry.json` content byte-identical across all 3
runs — verified with `diff`, no differences reported.

Separately run **three times into the same accumulating `reports-dir`**
(regression variant, via `tests/test_cli_stability.py`, already part of
the passing suite): `times_seen` correctly incremented 1 → 2 → 3 for
the one signal in that test's fixture, `research_id` stable
(`RES-0001`), registry stayed flat at 1 entry across all 3 runs — no
duplicate registration from reprocessing unchanged input.

**Repository integrity**: `git status --short` on `discovery-lab`
confirmed no file outside `research-sensor/` (itself untracked, being
this task's own new package) was modified after any of the repeated
runs.

## 1 live run

Command (real wall-clock timestamp, writing into the real, committed
`reports/` directory):

```
python3 -c "
from research_sensor.cli import run_once
run_once('validation-dataset/raw-captures-2026-06-25-to-2026-07-25.json',
          'config/source-registry.json', 'config/relevance-gate.json',
          'reports', run_timestamp='2026-07-25T16:00:00Z')
"
```

Result: `7 clusters → 6 new signal(s), 0 updated signal(s), 1 discovery
hint(s) not registered. Registry total: 6.` Produced
`reports/research-registry.json`,
`reports/daily-research-brief-20260725T160000Z.md`,
`reports/weekly-research-intelligence-report-20260725T160000Z.md` —
all real, evidence-cited output, not a fixture. `git status --short`
confirmed no repository file outside `research-sensor/` was touched.

## PASS Criteria assessment

| Criterion | Result |
|---|---|
| Real research processed | PASS — 7 real captures, 5 domains, real `WebSearch`-sourced abstracts and dates |
| Provenance preserved | PASS — every registered signal's `evidence` list cites `source_url` + `quoted_abstract`; structurally proven by `test_headquarters_compatibility.py` and `test_registry.py::TestEvidenceSeparation` |
| Duplicates merged | PASS (mechanism proven) — no real duplicate pair occurred in this window (honest, not engineered); `test_dedup.py` proves the merge behavior directly |
| Project relevance explicit | PASS — every registered signal names either a real project or `WATCH`; none forced |
| At least one valuable opportunity discovered | PASS — RES-0006 (DeepMind "Conjecture Machines," MEDIUM confidence, Trust Engine, one concrete possible experiment) |
| Headquarters compatibility demonstrated | PASS (structural) — flat, tolerant-JSON-readable list; `headquarters/` untouched |
| Repositories unchanged | PASS — verified via `git status --short` after every run |
| Repeatability proven | PASS — byte-identical fresh-dir runs, correct `times_seen` growth on accumulating runs |

**Overall: PASS.** See the Final Report for the full verdict statement
and named limitations.
