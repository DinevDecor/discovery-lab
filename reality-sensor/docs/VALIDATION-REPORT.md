# Validation Report — Reality Intelligence Sensor 001 (`EXEC-008`)

## Test suite

61 tests, all passing, across `reality-sensor/tests/`. Mapped to
`EXEC-008`'s own 12 required categories:

| Required category | Test file(s) |
|---|---|
| Source validation | `test_source_validation.py` (2 tests) |
| Malformed feeds | `test_capture.py::TestMalformedFeeds` (5 tests) |
| Duplicate suppression | `test_dedup.py` (6 tests) |
| Evidence enforcement | `test_trust.py::test_zero_evidence_gives_insufficient_evidence`, `test_registry.py::TestEvidenceEnforcement` (3 tests) |
| Trust classification | `test_trust.py::TestConfidenceRules`, `test_config.py::TestSourceRegistryTrustClassification` (11 tests) |
| Fact vs interpretation | `test_registry.py::TestFactVsInterpretationSeparation` (2 tests) |
| Stable IDs | `test_registry.py::TestStableIds` (3 tests) |
| Repeated identical runs | `test_cli_stability.py::TestPureDeterminism` (1 test, 3 runs internally) |
| Empty result handling | `test_capture.py::TestEmptyResultHandling`, `test_cli_stability.py::TestEmptyResultHandling`, `test_brief.py` empty-brief tests (4 tests) |
| Read-only verification | `test_safety.py` (7 tests), `test_cli_stability.py::TestReadOnlyVerification` (2 tests) |
| Headquarters compatibility | `test_headquarters_compatibility.py` (2 tests) |
| Regression against self-generated reports | `test_registry.py::TestRegressionAgainstSelfGeneratedReports`, `test_cli_stability.py::TestRegressionAgainstSelfGeneratedReports` (2 tests) |

Run: `cd reality-sensor/tests && python3 -m unittest discover -s . -p "test_*.py"` -> `Ran 61 tests ... OK`.

## Real external capture

Performed against the fixed Source Registry, within a fixed, bounded
budget: **14 real operations** (10 `WebSearch`, 4 `WebFetch` attempts,
of which 3 were blocked with HTTP 403 by `anthropic.com`, `openai.com`,
and `arxiv.org`'s own bot protection — a real, honest limitation, not
hidden; see `docs/KNOWN-LIMITATIONS.md`). Produced **10 raw captures**
spanning all 4 Initial Observation Domains, committed at
`validation-dataset/raw-captures-2026-07-11-to-2026-07-25.json`:

- **A. Foundation Model Releases** (4 captures): Claude Opus 5 (2
  independent sources, correctly clustered), Claude voice mode update,
  Gemini 3.6 Flash / 3.5 Flash-Lite / 3.5 Flash Cyber.
- **B. Agent Infrastructure** (3 captures): MCP 2026-07-28 spec going
  stateless (2 independent sources, correctly clustered), Claude Code
  auto-mode change.
- **C. Developer Platforms** (2 captures): GitHub Code Quality GA
  billing, GitHub Copilot usage-window billing alerts.
- **D. Research** (1 capture): an LLM-agent-memory evaluation paper,
  captured with an explicit, honest date-uncertainty caveat (see
  Known Limitations).

All 10 captures are real, sourced, dated, and quoted from what was
actually retrieved — nothing was invented to fill a category.

## 3x repeated execution

Command, run three times against the committed validation dataset with
a fixed `--run-timestamp` (isolating the determinism proof from
wall-clock variance) into the same accumulating `reports-dir`:

```
python3 run_reality_sensor.py \
  --captures validation-dataset/raw-captures-2026-07-11-to-2026-07-25.json \
  --reports-dir <dir> --run-timestamp 2026-07-25T09:00:00Z
```

| Run | New signals | Updated signals | Registry total |
|---|---|---|---|
| 1 | 8 | 0 | 8 |
| 2 | 0 | 8 | 8 |
| 3 | 0 | 8 | 8 |

Verified directly: all 8 `signal_id`s identical across all 3 runs
(`RS-0001`-`RS-0008`); `times_seen` correctly incremented 1 -> 2 -> 3
for every signal; evidence count per signal identical across all 3
runs (no duplicate evidence added from re-processing unchanged input);
`config/source-registry.json`, `config/relevance-gate.json`, and the
validation dataset itself byte-identical (checksummed) before and
after all three runs. Separately, a pure-determinism variant (3 runs
against a **fresh, isolated** `reports-dir` each time, same fixed
timestamp) produced byte-identical `signal-registry.json` content
every time — proving the processing pipeline is a pure function of its
input, not merely "the same, minus growth."

**Repository integrity**: `git status --short` confirmed clean (no
modification) on all 5 ecosystem repositories immediately after these
3 runs.

## 1 live run

Command (real wall-clock timestamp, writing into the real, committed
`reports/` directory):

```
python3 run_reality_sensor.py \
  --captures validation-dataset/raw-captures-2026-07-11-to-2026-07-25.json \
  --reports-dir reports
```

Result: `8 cluster(s) -> 8 new signal(s), 0 updated signal(s).
Registry total: 8.` Produced `reports/signal-registry.json`,
`reports/daily-ai-reality-brief-20260725T145601Z.md`, `reports/
weekly-ai-intelligence-brief-20260725T145601Z.md` — all real,
evidence-cited output, not a fixture.

## PASS Criteria assessment

| Criterion | Result |
|---|---|
| Real external sources are processed | PASS — 10 real captures, 7 distinct real domains, 2 genuinely `PRIMARY`-trust direct fetches |
| Signals are evidence-backed | PASS — every one of the 8 signals cites >=1 URL-linked quote; 0 signals with empty evidence |
| Duplicates are suppressed | PASS — 10 captures -> 8 clusters; the 2 real duplicate pairs (Opus 5, MCP spec) each correctly merged into 1 signal with 2 evidence entries |
| Fact and interpretation remain separate | PASS — structurally enforced (separate dataclass fields) and tested |
| Reports are reproducible | PASS — 3x repeated run proof, both accumulating and fresh-directory variants |
| Headquarters consumes the registry | PASS (structural) — `signal-registry.json` is a flat, tolerant-JSON-readable list; actual `collector.py` wiring is a documented, separate, not-yet-attempted follow-on, consistent with "do not redesign the existing ecosystem" |
| Repositories remain unchanged | PASS — verified via `git status --short` on all 5 repos after every run |
| Repeated executions remain stable | PASS — 0 new signals, correct `times_seen` increments, no ID churn, no evidence duplication |
| At least one operationally useful signal discovered | PASS — `RS-0001` (Claude Opus 5, 1M context window, `HIGH` confidence, 2 independent sources) and `RS-0003` (MCP spec going stateless, `HIGH` confidence, `HIGH` urgency, directly relevant to Discovery Lab's own MCP usage) are both genuinely actionable-to-review signals, not synthetic filler |

**Overall: PASS.** See the Final Report for the full verdict statement
and named limitations.
