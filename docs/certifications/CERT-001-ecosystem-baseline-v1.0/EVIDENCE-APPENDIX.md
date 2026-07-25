# CERT-001 — Evidence Appendix

Every `[EV-NN]` marker used in
[`CERT-001-Ecosystem-Baseline-v1.0.md`](./CERT-001-Ecosystem-Baseline-v1.0.md)
resolves to an entry below. Each entry states the exact command or
file location used, and — where a command was actually run for this
certification — its real output. All commands were run read-only
against a `git worktree` of `origin/main`, never against the shared
working directory's own branch checkout, so nothing here could have
modified any repository. The worktree was removed after use; `git
status --short` was confirmed clean on all 5 ecosystem repositories
both before and after this certification's evidence-gathering runs
(see `[EV-17]`).

---

### [EV-01] `main` branch commit history

Command: `git log origin/main --oneline`

```
8726ac1 Activate Ecosystem Headquarters v1.0 (narrow scope, EXEC-004)
428e18f Activate Observation Agent 001 (narrow scope, EXEC-002/EXEC-003)
7531956 Initial commit
```

`main` had exactly 3 commits as of original certification (2026-07-25).
Everything else in this repository's history — including `EXEC-005`
and `EXEC-006` — lived only on `claude/prop-0002-discovery-intake` and
had not been merged. **Update**: a 4th commit, `12f82fd`, has since
been added to `main` via the authorized `EXEC-006` deployment — see
`[EV-21]`.

### [EV-02] Commits ahead of `main`

Command: `git log origin/main..claude/prop-0002-discovery-intake --oneline | wc -l`

Result: 40 commits ahead, none merged to `main`, spanning the full
engagement history from `1f9317b` (initial architecture recovery)
through `1217473` (EXEC-006 Human Acceptance record).

### [EV-03] Observation Agent test suite on `main`

Commands, run against a `git worktree add <tmp> origin/main` checkout:

```
cd <worktree>/observation-agent/tests
python3 -m unittest discover -s . -p "test_*.py"
```

Result at original certification: `Ran 45 tests in 0.025s` — `OK`. Test
files present on `main` at that time: `test_broken_references.py`,
`test_ci_activation.py`, `test_orphan_files.py`,
`test_registry_check.py`, `test_report.py`, `test_safety.py`,
`test_stale_state.py`, `test_status_history_consistency.py` (8 files).
**Update**: after the `EXEC-006` deployment, `main` has 58 tests across
10 files — see `[EV-21]`.

### [EV-04] Headquarters test suite on `main`

Same worktree, `cd <worktree>/headquarters/tests`:

```
python3 -m unittest discover -s . -p "test_*.py"
```

Result: `Ran 111 tests in 0.038s` — `OK`. 13 test files present.

### [EV-05] Safety self-check, both tools, on `main`

```
cd <worktree>/observation-agent/tests && python3 -m unittest test_safety -v
```
→ 5/5 passing: `test_at_least_the_expected_write_call_exists`,
`test_forbidden_patterns_actually_detect_violations`,
`test_no_forbidden_call_anywhere_in_source`,
`test_source_never_references_git_command`,
`test_write_mode_file_opens_only_in_allowed_modules`.

```
cd <worktree>/headquarters/tests && python3 -m unittest test_safety -v
```
→ 6/6 passing: the same 5, plus
`test_source_never_calls_github_or_network_apis`.

Both `test_safety.py` scan their own tool's actual source text for
forbidden patterns (`subprocess.`, `os.remove(`, `shutil.rmtree(`,
`.commit(`, `.push(`, `.merge(`) and restrict writing-mode file opens
to a named module allow-list, verified by reading the detector's own
source: `observation-agent/tests/test_safety.py` and
`headquarters/tests/test_safety.py`.

### [EV-06] Scheduled workflow file, on `main`

File: `.github/workflows/observation-agent.yml` (present on `main`,
confirmed via the `git worktree` checkout).

Key content, read directly:

```yaml
on:
  schedule:
    - cron: "0 6 * * *"
  workflow_dispatch: {}
permissions:
  contents: read
```

`working-directory: observation-agent`, `run: python3
run_observation_agent.py --config config.ci.json --reports-dir
reports-ci`. `actions/checkout@v4` called with
`persist-credentials: false`. No `issues`, `pull-requests`, or `write`
permission appears anywhere in the file (confirmed by reading it in
full, 60+ lines).

`config.ci.json` on `main` (read directly): `discovery-lab` path `..`
(the workflow's own checkout root, given
`working-directory: observation-agent`); the other 4 repositories use
placeholder paths that do not exist in the CI runner's filesystem, so
they resolve to Observation Agent's existing, already-tested
"repository path does not exist → SKIP" behavior, not a crash.

### [EV-07] `CONTRACT.md` and `README.md` content, both tools, on `main`

- `observation-agent/CONTRACT.md`: `Version: v0.2`, "Core Principle:
  Observe. Report evidence. Do not decide, do not act.", Scope of
  Authority section, Safety section referencing `test_safety.py`.
- `headquarters/CONTRACT.md`: `Version: v1.0`, "Core Principle:
  Observe. Understand. Prioritize. Explain. Recommend. Never act.",
  the full "Human Authority Boundary (EXEC-004 §9, verbatim scope)"
  section quoted in full at `[EV-19]`.
- `headquarters/README.md`, `## Architecture` section: the 11-module
  pipeline (`collector.py` → `drift.py` → `opportunity.py` →
  `inconsistency.py` → `health.py` → `portfolio.py` →
  `prioritizer.py` → `recommendation.py` → `history.py` → `brief.py`
  → `cli.py`), and `## What it consumes`: a table of every named
  artifact path Headquarters reads, explicitly stating it "never
  re-walks a repository the way observation-agent does."
- Both `README.md` files' own stated check/module lists were used
  directly to write Section 2 and Section 3 of the main certification
  document — no check or module not named in these files is claimed
  as operational.

### [EV-08] `PROP-0001` ratification status

File: `docs/proposals/PROP-0001-discovery-lab-boundaries.md`, line 3:

```
Status: **ACCEPTED — Variant B (Ecosystem Observatory) adopted, 2026-07-25.**
```

File: `docs/proposals/PROP-0001-ratification-package/9-RATIFICATION-RECORD.md`
— Decision: `ACCEPT`, Variant B, Decision Maker: Petko Dinev, Date:
2026-07-25, verbatim message quoted: `"ACCEPT"`.

### [EV-09] Neither tool is an Employee Role

Command: `grep -i "observation\|headquarters" docs/ai-organization/EMPLOYEE-REGISTRY.md`

Result: no match. Both `CONTRACT.md` files state explicitly this is a
deliberate choice, not an oversight ("this is a tool contract, not an
Employee Role contract").

### [EV-10] `discovery-lab` absent from the ecosystem's own registry

Command: `grep -i "discovery-lab" /home/user/project-memory/PROJECT_REGISTRY.md`

Result: no match ("NOT FOUND"). This is also independently surfaced by
Headquarters itself as a live Governance Issue inconsistency in its
own Executive Brief output (verified during this certification's
evidence-gathering run, `[EV-13]`).

### [EV-11] PR and real-run history, from `CHANGELOG.md`

- `CHANGELOG.md:358`: "Opened PR #8 (`claude/activate-observation-agent`
  → `main`)" — merged as `428e18f`.
- `CHANGELOG.md:84`: "Opened PR #9, merged (squash) to `main` as
  `8726ac1`."
- `EXEC-003`'s recorded real run: `workflow_dispatch` on `main`,
  "run completed in 10 seconds, conclusion: success," console output
  "Scanned 1 repositories, skipped 4. 2 total observations (2 new, 0
  repeated, 0 resolved)," artifact `observation-agent-report-1`
  uploaded (2,311 bytes, 90-day retention).
- `EXEC-005`'s recorded real run: scheduled run #2
  (`https://github.com/DinevDecor/discovery-lab/actions/runs/30148534238`),
  `conclusion: success`, artifact `observation-agent-report-2`
  uploaded (2,310 bytes).

This certification did not independently re-query the live GitHub
Actions dashboard; it relies on the workflow file's committed content
(`[EV-06]`) and these two previously-recorded, independently confirmed
outcomes. See the main document's Section 7, "Unknown."

### [EV-12] Test suite on the unmerged `EXEC-006` branch

Command, run this session against `claude/prop-0002-discovery-intake`
(commit `1217473`):

```
cd observation-agent/tests && python3 -m unittest discover -s . -p "test_*.py"
```

Result: `Ran 58 tests in 0.039s` — `OK`. New/changed test files versus
`main`: `test_scanner.py` (new, 5 tests), `test_broken_references.py`
(added `TestSelfReferentialFeedbackLoop`, 3 tests),
`test_cli_stability.py` (new, 3 tests, including the negative control
`test_without_the_exclusion_the_bug_reproduces`), `test_ci_activation.py`
(added `TestExcludedPathsEquivalence`, 2 tests). Headquarters' suite is
unchanged by `EXEC-006` (still 111, not re-verified redundantly here
since no Headquarters file was touched — confirmed via
`git diff origin/main..claude/prop-0002-discovery-intake --stat -- headquarters/`
showing no output for source files, only `reports/` runtime artifacts
which are excluded from every commit).

### [EV-13] Real ecosystem runs performed during `EXEC-006` and this certification

Commands (dev branch, `claude/prop-0002-discovery-intake`, after the
`EXEC-006` fix):

```
cd observation-agent && python3 run_observation_agent.py   # x2-3, back to back
cd headquarters && python3 run_headquarters.py
```

Representative results (most recent, after `STATE.md`/`CHANGELOG.md`
were updated for `EXEC-006`):

```
Scanned 5 repositories, skipped 0.
37 total observations (7 new, 32 repeated, 0 resolved).
```
then, immediately rerun with zero repository content changed:
```
Scanned 5 repositories, skipped 0.
37 total observations (0 new, 37 repeated, 0 resolved).
```

Headquarters, same session:
```
Overall Health: 70%
Top recommendation: HQ-0001 — discovery-lab: two files both claim ADR-0001 (score 6)
```

After each run, `headquarters/reports/history.json`,
`headquarters/reports/recommendation-log.json`, and
`observation-agent/reports/last_run_observations.json` (all tracked
files) were reverted via `git checkout --`, and untracked
run-artifact files (dated report/log/brief Markdown files,
`__pycache__/`) were removed — confirmed via `git status --short`
returning to exactly the intended source/doc changeset before each
commit (`[EV-17]`).

### [EV-14] `EXEC-005`'s measured feedback-loop numbers

Source: `docs/investigations/INV-0004-ecosystem-operational-validation.md`
and `STATE.md`'s `EXEC-005` paragraph (both written at the time of
that execution, cross-referenced here, not re-derived).

- New false-positive observations across 3 unchanged-input local runs:
  `2 → 10 → 58`.
- "Human Decisions Required" list length across the same 3 runs:
  `35 → 45 → 103`.
- `Overall Health` across the same 3 runs: `71% → 70% → 67%`.
- `HQ-0001` across the same 3 runs: identical score (6), identical
  evidence, `times_proposed` correctly incrementing `2 → 3 → 4`, no
  duplicate ID ever created.
- Confirmed absent from the CI/scheduled path in the same execution
  (ephemeral runner, no memory between runs, always starts from a
  fresh checkout).

### [EV-15] `HQ-0001`'s underlying evidence

Command: `ls docs/adr/`

Result includes both `ADR-0001-human-authority-gates.md` and
`ADR-0001-migration-plan.md` — two files that both parse as ADR ID
`0001`, the exact fact `HQ-0001` cites. Confirmed present on `main`
(these files predate both narrow merges and were never touched by
either).

### [EV-16] `EXEC-006` commits and Human Acceptance

Commits on `claude/prop-0002-discovery-intake`:
- `0e4acad` — "EXEC-006: fix self-referential feedback-loop defect
  (narrow maintenance)" — 17 files changed.
- `1217473` — "Record Human Acceptance — EXEC-006 (Verdict: PASS)" —
  2 files changed (`STATE.md`, `CHANGELOG.md`).

At original certification, neither commit was an ancestor of
`origin/main` — confirmed by `[EV-01]`/`[EV-02]` showing `main`'s HEAD
was still `8726ac1`, predating both. **Update**: the content of
`0e4acad` (excluding `STATE.md`/`CHANGELOG.md`, which do not exist on
`main`) is now part of `main` via the squash-merged deployment commit
`12f82fd` — see `[EV-21]`.

### [EV-17] Repository-integrity checks

Command, run repeatedly throughout `EXEC-003` through `EXEC-006` and
this certification:

```
git -C /home/user/project-memory status --short
git -C /workspace/kod status --short
git -C /workspace/discovery-lab status --short
git -C /workspace/generative-discovery-engine status --short
git -C /workspace/trust-engine status --short
```

Result, every time this was run after a tool execution (including
immediately before this certification's own commit): the 4
cross-referenced repositories return empty output (clean);
`discovery-lab` returns only the intended source/doc changeset for
whatever task was in progress — never leftover run artifacts, which
were always identified and either reverted (tracked files) or deleted
(untracked files) before committing.

### [EV-18] Recommendation Ledger status

File: `docs/investigations/RECOMMENDATION-LEDGER.md`.

Command: `grep -A2 "^status" docs/investigations/RECOMMENDATION-LEDGER.md`

Result: 6 entries (`REC-0001` through `REC-0006`), every one
`status: PROPOSED`. None have been advanced to `ACCEPTED`,
`REJECTED`, or `PENDING_NO_RESPONSE` by either tool or by this
certification.

### [EV-19] Headquarters' Human Authority Boundary, verbatim

File: `headquarters/CONTRACT.md`, section `## Human Authority Boundary
(EXEC-004 §9, verbatim scope)`:

> Headquarters MUST NOT, under any circumstance:
> - modify any repository;
> - create a commit;
> - edit the Registry, an ADR, or any governance document;
> - accept an architectural proposal;
> - create or merge a pull request;
> - change any project's state file automatically.
>
> Every output is advisory only. A recommendation reaching
> `status: accepted` in `reports/recommendation-log.json` happens
> because a human edited `reports/recommendation-decisions.json` by
> hand — never because this tool decided its own recommendation was
> good enough to act on.

Quoted directly from the file on `main`, not paraphrased.

### [EV-20] Safety-detector self-check

Test: `test_forbidden_patterns_actually_detect_violations`, present in
both `observation-agent/tests/test_safety.py` and
`headquarters/tests/test_safety.py`, confirmed passing in `[EV-05]`.
This test constructs a deliberately-violating fixture and asserts the
detector actually flags it — proving the forbidden-pattern scan is a
real check, not a vacuously-passing no-op.

---

## Evidence added for the CERT-001 verdict update (2026-07-25)

The entries below were gathered after Petko's "Human Decision —
CERT-001" authorized the narrow `EXEC-006` deployment. They document
that deployment and its required post-deployment verification —
per that decision, no other certification content was rewritten
beyond what these two entries and the corrections to `[EV-01]`,
`[EV-03]`, and `[EV-16]` above required.

### [EV-21] `EXEC-006` deployment to `main`

Branch built off `origin/main` via `git worktree add ... -b
claude/exec-006-narrow-deploy origin/main`. Populated with exactly 15
files (`git show claude/prop-0002-discovery-intake:<path>` for each),
deliberately excluding `STATE.md` and `CHANGELOG.md` (dev-branch
narrative, absent from `main`):

```
observation-agent/README.md
observation-agent/config.ci.json
observation-agent/config.json
observation-agent/src/observation_agent/checks/broken_references.py
observation-agent/src/observation_agent/checks/orphan_files.py
observation-agent/src/observation_agent/checks/registry_check.py
observation-agent/src/observation_agent/checks/stale_state.py
observation-agent/src/observation_agent/checks/status_history_consistency.py
observation-agent/src/observation_agent/cli.py
observation-agent/src/observation_agent/config.py
observation-agent/src/observation_agent/scanner.py
observation-agent/tests/test_broken_references.py
observation-agent/tests/test_ci_activation.py
observation-agent/tests/test_cli_stability.py
observation-agent/tests/test_scanner.py
```

Verified in isolation before pushing:
- `git status --short` on the branch showed exactly these 15 files,
  nothing else.
- `python3 -m unittest discover -s . -p "test_*.py"` in
  `observation-agent/tests/`: `Ran 58 tests in 0.035s` — `OK`.
- `python3 -m unittest test_safety -v`: 5/5 passing.
- `headquarters/` confirmed untouched:
  `git diff origin/main..claude/exec-006-narrow-deploy --stat --
  headquarters/` produced no output.

Committed as `7e07361` on `claude/exec-006-narrow-deploy`, pushed,
opened as **PR #10** ("Fix Observation Agent self-observation
feedback-loop defect (EXEC-006, narrow scope)"), squash-merged to
`main` as **`12f82fd`**. Confirmed via
`git fetch origin main && git log origin/main --oneline`:

```
12f82fd Fix Observation Agent self-observation feedback-loop defect (narrow scope, EXEC-006)
8726ac1 Activate Ecosystem Headquarters v1.0 (narrow scope, EXEC-004)
428e18f Activate Observation Agent 001 (narrow scope, EXEC-002/EXEC-003)
7531956 Initial commit
```

### [EV-22] Post-deployment verification (5 of 5 required checks)

All commands run against a fresh `git worktree` of the new
`origin/main` HEAD (`12f82fd`), using `config.json`'s real absolute
repository paths — code from the freshly-deployed `main`, data from
the live 5-repository ecosystem, exactly as the `EXEC-004` deployment
was originally validated.

1. **Real Observation Agent run**: `python3 run_observation_agent.py`
   → `Scanned 5 repositories, skipped 0. 37 total observations (37
   new, 0 repeated, 0 resolved).`
2. **Real Headquarters run**: `python3 run_headquarters.py` →
   `Overall Health: 71%` / `Top recommendation: HQ-0001 —
   discovery-lab: two files both claim ADR-0001 (score 6)`.
3. **Repeated local executions stable**: `run_observation_agent.py`
   run 2 more times with no repository content changed in between →
   `37 total observations (0 new, 37 repeated, 0 resolved)` both
   times. Sequence: `37 → 37 → 37`, 0 new after the first run.
4. **CI execution unchanged**: `python3 run_observation_agent.py
   --config config.ci.json --reports-dir reports-ci` (from
   `observation-agent/`, matching the workflow's own
   `working-directory`) → `Scanned 1 repositories, skipped 4. 0 total
   observations (0 new, 0 repeated, 0 resolved).` Then `python3
   ci_summary.py reports-ci` → `STATUS: PARTIAL` with the expected
   "one or more configured repositories were not accessible... Expected
   in CI" message — identical classification behavior to every prior
   CI run on record [EV-11].
5. **`HQ-0001` sole recommendation, unchanged**: confirmed directly in
   the Headquarters run above and in the rendered Executive Brief's
   "Most Important Recommendation" section — same ID, same score (6),
   same evidence as every prior real run [EV-13, EV-14].

After verification, the worktree was removed; `git status --short`
confirmed on all 5 ecosystem repositories (empty on the 4
cross-referenced repositories, clean on `discovery-lab` beyond the
intended deployment) both before and after — no repository was left
modified by this verification pass [EV-17].
