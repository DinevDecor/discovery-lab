# Deliverable 2 — Comparative Matrix: Observation Agent vs Reality Sensor 001

Per `EXEC-009` Phase 0. Every row is drawn directly from the two
tools' own committed source (`observation-agent/src/observation_agent/`,
`reality-sensor/src/reality_sensor/`) and their `CONTRACT.md`/`README.md`
files as they exist on `main` today (`acf281f`) — not from memory of
having built them, re-verified by reading the files in this pass.
Where the two genuinely diverge rather than merely looking different,
the divergence is stated plainly — this matrix is the evidence base
Deliverable 3's promotions must trace back to, per `EXEC-009`'s own
"every shared component must have evidence from at least two
independent implementations" rule (which cuts both ways: it also
means a component *without* two-implementation evidence must not be
promoted).

| Dimension | Observation Agent 001 | Reality Sensor 001 |
|---|---|---|
| **Domain** | Internal: this ecosystem's own 5 repositories | External: the public AI ecosystem (foundation models, agent infra, dev platforms, research) |
| **Source of truth** | The filesystem itself, read directly (`scanner.walk_files`, `os.walk`) | A human/AI-executor-supplied `raw-captures` JSON file — the tool never reads the internet itself |
| **Capture mechanism** | Synchronous, internal, deterministic — the same repository state always yields the same walk | Asynchronous relative to processing, external, non-deterministic — a real web page can change between two fetches; deliberately isolated so it can't leak into the deterministic pipeline (see `reality-sensor/ARCHITECTURE.md`) |
| **Is capture code shared with processing?** | Yes — `scanner.py` is checked-in, tested, part of the same package as `cli.py` | **No** — capture is explicitly outside this package's own source, by design; `tests/test_safety.py` fails the build if a network client ever appears in `src/reality_sensor/` |
| **Configuration** | `config.json` — `repos: [{name, path, state_file_candidates}]`, `excluded_dirs`, `excluded_paths`, extension lists. `config.ci.json` is a second, CI-only variant. | `config/source-registry.json` — `sources: [{name, url, trust_level, category, domain}]`, `search_budget`. `config/relevance-gate.json` — `rules: [{project, keywords}]` |
| **Config loading pattern** | `dataclasses` + `json.loads`, no third-party dependency, no dynamic discovery | Same pattern, same constraint, independently arrived at |
| **Finding/Signal schema** | `Observation`: `event, evidence, verification_method, confidence, possible_interpretation, recommended_action, human_needed, check_name` (8 fields, no persistent identity) | `Signal`: `signal_id, timestamp, source, source_trust, category, affected_capability, affected_projects, evidence, summary, practical_impact, confidence, urgency, recommended_action` (13 fields) plus internal bookkeeping (`key, first_seen, last_seen, times_seen`) |
| **Evidence model** | `Evidence: repo, file_path, line_number, quoted_text` + `.citation()` | `Evidence: source_name, source_url, source_trust, quoted_text` + `.citation()` |
| **Confidence vocabulary** | `MATCH` / `MISMATCH` / `INSUFFICIENT_EVIDENCE` — a **verification** outcome (did the file's own claim match reality?) | `HIGH` / `MEDIUM` / `LOW` / `INSUFFICIENT_EVIDENCE` — a **trust** outcome (how much should this be believed?) — a different question with a different vocabulary, not a renamed version of the same thing |
| **Trust classification** | **Absent.** No concept of source trust exists or is needed — a repository file's content either matches its own claim or it doesn't; there is no "was this PRIMARY or COMMUNITY" question for internal filesystem facts | **Central.** 6-level `TrustLevel` vocabulary, with an explicit hard rule (never `HIGH` from `COMMUNITY` alone) directly governing confidence |
| **Duplicate detection** | **Absent.** Each check produces at most one `Observation` per distinct fact (one broken link, one stale file); there is no "multiple articles about one event" problem in filesystem scanning | **Central.** `dedup.py` clusters raw captures describing the same real-world event via category + keyword-overlap, so "8 clusters from 10 captures" is a normal, expected outcome |
| **Cross-run identity / persistence model** | **Ephemeral, key-based diff.** `report.py`'s `_observation_key()` computes `check_name::file_path::event`; `last_run_observations.json` is fully **overwritten** each run; New/Repeated/Resolved are computed by set-comparing keys against the previous snapshot. **No stable, long-lived ID is ever minted.** | **Persistent, ID-based registry.** `registry.py` mints `RS-000N` and reuses it by content-derived `key` (mirroring `headquarters/recommendation.py`'s `HQ-000N` pattern, not anything in Observation Agent); a signal **accumulates** `times_seen`, growing evidence, and never-downgrading confidence across runs |
| **Relevance gating** | **Absent.** A finding is always "about" the repository it was found in; no cross-project relevance question exists | **Central.** `relevance.py` gates every signal against 5 named Discovery Lab projects, falling back to `WATCH` |
| **Report output** | `observation-report-<ts>.md` (Summary/New/Repeated/Resolved/Risk Changes/Confidence/Evidence Links/Recommended Actions/Human Decisions Required) + `execution-log-<ts>.md` + `last_run_observations.json` snapshot | `daily-ai-reality-brief-<ts>.md` + `weekly-ai-intelligence-brief-<ts>.md` + `signal-registry.json` (the durable artifact — no execution log) |
| **Report rendering pattern** | Hand-built Markdown string assembly (`report.py`'s `render_report`), one function per report | Same pattern, two render functions (`brief.py`'s `render_daily_brief`/`render_weekly_brief`) |
| **CLI shape** | `run_observation_agent.py` (thin `sys.path` shim) → `cli.main(argv)` → `argparse` → orchestration function (`run_all_checks`) kept separate from I/O, printing a short summary | Identical shape: `run_reality_sensor.py` → `cli.main(argv)` → `argparse` → orchestration function (`run_once`) kept separate from I/O, printing a short summary |
| **Safety enforcement** | `tests/test_safety.py`: static scan for forbidden patterns (`subprocess.`, `os.remove(`, `.commit(`, `.push(`, `.merge(`, …), write-mode-`open()` calls restricted to an explicit allow-list of modules, a self-check proving the detector isn't vacuous | **Same detector, same structure, same self-check**, extended with one new check unique to this tool: no network-client reference anywhere in `src/` |
| **Safety allow-list** | `{report.py, cli.py}` | `{cli.py, registry.py}` |
| **Test suite size** | 58 tests (`main`, post-`EXEC-006`) | 61 tests |
| **Required test categories exercised** | Regression (feedback-loop-specific), safety, per-check correctness | Source validation, malformed feeds, duplicate suppression, evidence enforcement, trust classification, fact-vs-interpretation separation, stable IDs, repeated-run stability, empty-result handling, read-only, Headquarters compatibility, self-generated-report regression |
| **Operational cadence** | Scheduled (GitHub Actions, daily `06:00 UTC`) *and* human-invoked | Human/executor-invoked only; no scheduling exists or is proposed |
| **Headquarters consumption** | `headquarters/src/headquarters/collector.py::collect_observation_agent` reads the latest report + log directly, regex-parses the Confidence line and the Human Decisions Required section — **actually wired in** | `signal-registry.json` proven structurally compatible (`tests/test_headquarters_compatibility.py`) but **not wired into `collector.py`** — a real, current asymmetry, not a design difference |
| **`CONTRACT.md` shape** | Scope of authority / Rights / Responsibilities / Safety / Executor independence / Revocation | Same section set, same order, same phrasing conventions — independently arrived at, then visibly converged |
| **Version** | v0.2 | v0.1 |

## What this matrix already tells us, before Deliverable 3

Six of the eighteen dimensions above show **genuine, purpose-level
divergence, not merely cosmetic difference**: Trust Classification,
Duplicate Detection, Confidence vocabulary, cross-run identity model,
Relevance gating, and whether capture is even part of the checked-in
package. Each of these exists in exactly one of the two tools, for a
reason traceable to the domain (internal filesystem facts don't need
trust scoring or event clustering; external evidence does). Per
`EXEC-009`'s own Anti-Abstraction Rule, none of these six qualify as
"proven common" from this comparison alone — see Deliverable 3 for
how each is actually treated.

Conversely, five dimensions show **real convergence arrived at
independently**: the config-loading pattern, the CLI shape, the
Evidence-plus-citation structure, the Markdown-report-rendering
pattern, and — most strongly — the safety-enforcement detector, which
is not just similar but has already been *copy-adapted* twice
(`headquarters/tests/test_safety.py` from `observation-agent`'s;
`reality-sensor/tests/test_safety.py` from both). This is the
strongest evidence base in the whole comparison for extraction.
