# INV-0004 — Ecosystem Operational Validation

Task: `EXEC-005 — Ecosystem Operational Validation`.
Date: 2026-07-25.
Scope: validate the *combined* operation of Observation Agent 001 and
Ecosystem Headquarters v1.0 under real operating conditions. No code
in either tool was modified for this task — this is an evidence
report, not an implementation task. Where this report identifies a
real defect, it is recorded and explained, not fixed (per EXEC-005's
own explicit instruction: "Do not implement those improvements yet").

## Architecture in Operation

```
                         ┌─────────────────────┐
   5 configured repos ──▶│  Observation Agent   │──▶ observation-agent/reports/
   (read-only scan)      │  (the sensor)        │    (report, execution log,
                         └─────────────────────┘     JSON snapshot)
                                                              │
                                                              ▼
                         ┌─────────────────────┐
   RECOMMENDATION-LEDGER │  Ecosystem           │──▶ headquarters/reports/
   PROJECT_REGISTRY.md   │  Headquarters        │    (Executive Brief,
   ADR dirs, state files │  (the interpreter)   │     recommendation-log.json,
   docs/proposals/  ────▶│                      │     history.json)
                         └─────────────────────┘
```

Both tools are human-invoked (or, for Observation Agent alone,
GitHub-Actions-scheduled on `main`). Neither tool triggers the other —
"combined operation" in this validation means a human runs Observation
Agent, then runs Headquarters, in sequence, with no manual editing of
any output file in between. That sequence was executed four times
across this validation (three full local pairs, one CI-only
Observation Agent run), with zero manual intervention on the data
itself between or during runs.

## Execution Log

All four executions ran against the real, live 5-repository ecosystem
(or, for the CI run, the real `discovery-lab` repository via its
scheduled workflow). No repository outside each tool's own `reports/`
directory was modified in any execution — confirmed via `git status
--short` on all 5 repositories after every run.

| # | Mechanism | Time (UTC) | Observation Agent | Headquarters |
|---|---|---|---|---|
| 1 | Manual, local | 06:58:27–06:59:28 | 0.19s · 34 obs. (2 new, 32 repeated) | 0.08s · Health 71% · **HQ-0001** (score 6) |
| 2 | Manual, local, unchanged inputs | 06:59:36–07:00:03 | 0.13s · 44 obs. (10 new, 34 repeated) | 0.06s · Health 70% · **HQ-0001** (score 6) |
| 3 | Manual, local, unchanged inputs | 07:00:14–07:00:22 | 0.15s · 102 obs. (58 new, 44 repeated) | 0.07s · Health 67% · **HQ-0001** (score 6) |
| 4 | **Scheduled** (GitHub Actions `workflow_dispatch` on `main`) | 07:00:52–07:01:05 | ~5s (incl. checkout/setup) · 2 obs. (2 new, discovery-lab-only scope) | not run in CI (no Headquarters schedule exists — see Limitations) |

Execution 4's real run: [https://github.com/DinevDecor/discovery-lab/actions/runs/30148534238](https://github.com/DinevDecor/discovery-lab/actions/runs/30148534238) — `conclusion: success`, artifact `observation-agent-report-2` uploaded (2,310 bytes).

## Recommendation History

Across all three local runs, Ecosystem Headquarters produced **exactly
one** recommendation each time, and it was the **same** recommendation
every time:

| Run | HQ ID | Title | Score | `times_proposed` after this run |
|---|---|---|---|---|
| 1 | HQ-0001 | discovery-lab: two files both claim ADR-0001 | 6 | 2 |
| 2 | HQ-0001 | discovery-lab: two files both claim ADR-0001 | 6 | 3 |
| 3 | HQ-0001 | discovery-lab: two files both claim ADR-0001 | 6 | 4 |

**No duplicate recommendation was ever created.** The persistent
`HQ-000N` identifier scheme worked exactly as designed: the same
underlying finding (`finding-duplicate-adr-discovery-lab-0001`) was
recognized as recurring and reused its existing ID each time, rather
than minting `HQ-0002`, `HQ-0003`, etc. This held even while the
Observation Agent's own output was growing rapidly noisier (see
below) — because Headquarters' candidate pool is built only from the
Recommendation Ledger's `PROPOSED` entries and its own Drift/
Opportunity findings, **not** from Observation Agent's raw
observations directly. The growing noise from Execution 2–3 did not
leak into recommendation selection.

**Recommendation stability with unchanged inputs**: the *selected*
recommendation (`HQ-0001`, score 6) was perfectly stable across all
three runs — the top-line output a human would act on did not change.
A downstream metric, `Overall Health`, was **not** perfectly stable
(71% → 70% → 67%) despite no real ecosystem change — this is explained
below (§ Detected Issues) and is a real, if secondary, finding.

## Detected Issues

### Issue 1 — Self-referential feedback loop in local, human-invoked runs (real defect, confirmed)

**What happens**: both `observation-agent/reports/` and
`headquarters/reports/` live *inside* the `discovery-lab` repository,
one of the five repositories Observation Agent scans. Each local run
writes new report files into its own `reports/` directory; the *next*
local run then scans those newly-written files as ordinary repository
content, alongside everything else.

**Confirmed root cause**: `broken_references` scans every `.md` file
for `[text](path)`-shaped substrings and checks whether `path`
resolves. Both tools' own documentation (`observation-agent/README.md`
lines 14 and 151) contains literal *prose examples* of that exact
syntax — e.g. `` Markdown `[text](path)` links whose target `` — used
to explain the check, not as real links. The check cannot distinguish
"this is a real link" from "this is documentation showing the link
syntax," so it flags these two lines as broken references. When a
report is generated, its own body quotes the offending line
verbatim (as evidence), which means the *report itself* now also
contains that same flagged substring — and the next run finds it
there too, in a newly-created file, and reports it as "new."

**Measured growth across three consecutive runs with zero real
ecosystem change**:

| Run | New observations | Total observations | `Human Decisions Required` items in the Headquarters brief |
|---|---|---|---|
| 1 | 2 | 34 | 35 |
| 2 | 10 | 44 | 45 |
| 3 | 58 | 102 | 103 |

All 10 of Run 2's "new" observations, and the large majority of Run
3's 58, were `broken_references` findings whose evidence path was
inside `observation-agent/reports/` or `headquarters/reports/` —
i.e., artifacts from the *previous* run(s), not real repository
content. This is compounding: each run's own report additionally
quotes prior runs' flagged lines, so the false-positive count grows
faster than linearly the more local runs accumulate without the
`reports/` directories being cleared.

**Not present in the scheduled (CI) path.** Execution 4, run via
GitHub Actions, showed none of this growth (2 new, 0 repeated — a
clean baseline). CI always starts from a fresh checkout of only
committed files; `reports-ci/` is never committed, so each CI run has
no memory of previous runs' output to re-observe. The feedback loop is
specific to **repeated local, human-invoked runs that don't clear
their own output directory** — a real, but scoped, operational
limitation.

**Downstream effect on Headquarters**: Headquarters does not create
new recommendations from this noise (see Recommendation History,
above), but it does surface the growing count in two visible places:
`Observation Cleanliness` (and therefore `Overall Health`, which
dropped 71% → 67% over three runs with zero real change) and the
`Human Decisions Required` list (35 → 45 → 103 items). A human
skimming only the headline "Overall Health" number or the length of
"Human Decisions Required" between two local runs could mistake this
artifact for real ecosystem degradation.

### Issue 2 — `Overall Health` is not fully stable under repeated runs (consequence of Issue 1)

The Success Criteria ask that "outputs remain stable across repeated
runs with unchanged inputs." The **recommendation** met that bar
exactly. The **Overall Health metric** did not, for the reason above —
its `Observation Cleanliness` sub-score is computed from Observation
Agent's latest report, which was not actually reporting on unchanged
inputs by Run 2 (its own Run 1 output had become new input). This is
not a bug in Headquarters' own arithmetic — the formula is followed
correctly and reproducibly given its actual inputs — it is a
consequence of Issue 1 upstream.

### Non-issue, checked and ruled out — HQ ID collisions or duplicate IDs

Explicitly verified: `recommendation-log.json` contains exactly one
record after all three runs, `HQ-0001`, with `times_proposed`
incrementing correctly (2 → 3 → 4) and `first_proposed` unchanged.
Duplicate-recommendation risk was a named concern in EXEC-005's
Observation Period requirements; it was checked directly and not
found.

## Operational Limitations (observed, not new — restated with fresh evidence)

- **Local human-invoked runs are not idempotent** if the `reports/`
  directories are left to accumulate (Issue 1, above) — this is new,
  concrete evidence for a limitation that was not previously measured.
- **Headquarters has no schedule of its own.** Only Observation Agent
  is activated via GitHub Actions (`EXEC-003`). Execution 4 in this
  report is therefore an Observation-Agent-only scheduled data point;
  "scheduled combined operation" (both tools run automatically in
  sequence) has not yet been exercised for real, because it doesn't
  exist yet. This is the same gap `headquarters/STATE.md`/`README.md`
  already name as a separate, later, human-authorized decision — this
  validation did not change that.
- **CI's Observation Agent scope stays discovery-lab-only** (`EXEC-003`'s
  known, documented limitation) — Execution 4 confirms this directly:
  "Scanned 1 repositories, skipped 4."
- **Recommendation selection is robust to Observation Agent's own
  noise, but Health/visibility metrics are not** — a real, newly
  precise distinction this validation surfaced (see Issue 2).

## Improvement Opportunities (named, not implemented — per EXEC-005)

- Exclude each tool's own `reports/` directory from the *other* tool's
  and its *own* future scans, or exclude `observation-agent/reports/`
  and `headquarters/reports/` from `broken_references`'/`orphan_files`'
  scope specifically — would directly resolve Issue 1. Not implemented
  here.
- Reword the two literal `[text](path)` syntax examples in
  `observation-agent/README.md` to avoid the exact bracket-paren shape
  the regex matches (e.g. `[text](path)` → "square-bracket,
  parenthesis link syntax") — a smaller, narrower fix for the same
  root cause. Not implemented here.
- A documented convention (e.g. "clear or archive local `reports/`
  output before re-running") for human operators, until either of the
  above is implemented.
- Scheduling Headquarters itself (mirroring `EXEC-003`) would let
  "combined operation, scheduled" actually be exercised for real,
  rather than only assembled from one scheduled leg (Observation
  Agent) and manual runs (Headquarters). A separate, later,
  human-authorized decision, as already noted in both tools' own
  documentation.

## Success Criteria — Assessed

| Criterion | Result |
|---|---|
| Both agents operate together without manual intervention between them (other than triggering the run) | **PASS** — verified across 3 full local pairs; no file was hand-edited between Observation Agent and Headquarters in any run |
| Headquarters consistently produces explainable recommendations | **PASS** — same recommendation, same score, same full evidence/reasoning/impact/dependencies/confidence/risk breakdown, all 3 runs |
| Outputs remain stable across repeated runs with unchanged inputs | **PARTIAL** — the recommendation itself was perfectly stable; `Overall Health` was not, due to Issue 1 (a real, now-documented cause, not random noise) |
| The system remains read-only | **PASS** — confirmed via `git status --short` on all 5 repositories after every execution; both tools only ever wrote inside their own `reports/` directories, exactly as contracted |

**Overall determination**: not a clean PASS on all four criteria as
literally stated — the third criterion is PARTIAL, with a precisely
identified, scoped, real cause (Issue 1) rather than an unexplained
instability. Recommend treating this as **PASS WITH A NAMED
LIMITATION** rather than a blocking FAIL: the actual decision-facing
output (the one recommendation a human would act on) was stable and
correct throughout; a secondary display metric was not, and the report
explains exactly why and exactly how large the effect was.

## Provenance

Produced under `EXEC-005 — Ecosystem Operational Validation`. No
change was made to `observation-agent/` or `headquarters/` source
code, tests, or configuration during this task. All report/log/
snapshot files generated during the four validation executions were
inspected for evidence and then removed (they were local, untracked,
or reverted to their pre-validation committed state) — this report is
the durable record of what they showed, not a raw dump of the
generated files themselves.
