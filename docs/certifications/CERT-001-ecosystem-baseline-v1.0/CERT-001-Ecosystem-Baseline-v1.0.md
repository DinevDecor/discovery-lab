# CERT-001 — Ecosystem Baseline Certification v1.0

**Status**: CERTIFICATION — not a development, implementation, or
architecture task. No repository was modified to produce this
document beyond adding this certification itself and its evidence
appendix.

**Certification date**: 2026-07-25
**Certifying scope**: the `discovery-lab` ecosystem's operational
tooling as actually deployed on `main`, cross-referenced against the
5-repository ecosystem it observes (`project-memory`, `kod`,
`discovery-lab`, `generative-discovery-engine`, `trust-engine`).
**Evidence**: every claim below cites an `[EV-NN]` marker resolved in
[`EVIDENCE-APPENDIX.md`](./EVIDENCE-APPENDIX.md) — exact commands,
file paths, commit hashes, and line numbers, independently
reproducible by any reviewer with access to this repository.

---

## 1. Executive Summary

**Purpose**: `discovery-lab` is an *Ecosystem Observatory* (`PROP-0001`
Variant B, `ACCEPTED` `2026-07-25` [EV-08]) — a read-only layer that
observes four other repositories (`project-memory`, `kod`,
`generative-discovery-engine`, `trust-engine`) plus itself, surfaces
mechanically-detectable inconsistencies with cited evidence, and
produces exactly one prioritized, explainable recommendation per run —
without ever modifying anything it observes and without ever acting on
its own recommendations. It does not build software, does not
architect other repositories, and does not make decisions; every
output terminates at a human.

**Current maturity**: two operational tools exist and are both merged
to `main` — **Observation Agent 001** (v0.2, read-only repository
scanner, scheduled daily via GitHub Actions [EV-06]) and **Ecosystem
Headquarters v1.0** (human-invoked interpretation and prioritization
layer that consumes Observation Agent's output and other ecosystem
artifacts, never re-scanning repositories itself [EV-07]). Both are
covered by passing automated test suites — 45 tests (Observation
Agent) and 111 tests (Headquarters), 156 total, verified directly
against the `main` branch commit for this certification [EV-03, EV-04]
— including a statically-enforced, self-verifying safety check in each
tool that no source file can write, delete, commit, push, or merge
anything outside the tool's own `reports/` directory [EV-05].

**Operational readiness**: Observation Agent runs unattended on a
daily GitHub Actions schedule against `discovery-lab` itself (the only
repository reachable from CI without an additional credential this
ecosystem has chosen not to provision — see Known Limitations),
confirmed by two independently recorded successful runs [EV-11].
Headquarters is human-invoked only — it has never been scheduled, and
scheduling it is explicitly out of scope for this baseline (see Future
Evolution). Both tools have been run for real against the live
5-repository ecosystem multiple times, most recently during this
certification's own evidence-gathering pass [EV-13].

**Certification verdict**: **PARTIALLY CERTIFIED** — see Section 14
for the precise, evidence-scoped reasoning. In short: every safety,
human-authority, and recommendation-correctness guarantee this
baseline claims holds on `main` today, verified directly, with no
exception found. One specific, precisely-bounded, non-safety defect
(a self-referential observation feedback loop under repeated local/
manual combined-tool operation) is present in the `main`-branch code
as currently deployed; it degrades a downstream display metric only,
never recommendation identity or safety, and a validated fix already
exists on an unmerged branch awaiting a routine human merge decision
[EV-16]. This is why the verdict is *partial* rather than unqualified.

---

## 2. Certified Architecture

The architecture actually running, as deployed on `main`:

```
Reality
  ↓  (5 repositories' own files: state files, ADRs, registries,
  ↓   markdown links, STATUS.yaml/HISTORY.md pairs — [EV-01])
Observation Agent  (read-only scan, 5 mechanical checks, evidence-cited report)
  ↓  (observation-agent/reports/ — latest report + execution log)
Ecosystem Headquarters  (interprets Observation Agent's output + other
  ↓   named ecosystem artifacts; never re-scans a repository itself — [EV-07])
Human Decision  (Petko Dinev; the only party who can accept, reject,
  ↓   defer, or act on any finding or recommendation)
Repository Updates  (made by a human, or by an AI executor acting
     under explicit human instruction in a separate session/task —
     never automatically by either tool)
```

Only components that exist as running code on `main` appear above.
No planned agent, no roadmap item, and no unmerged capability is
represented as part of this architecture (see Section 13 for what is
explicitly *not* included here).

---

## 3. Operational Components

### Observation Agent 001

- **Purpose**: read-only, human-invoked (and, for `discovery-lab`
  itself, scheduled) scanner that runs 5 mechanical consistency checks
  across the ecosystem's repositories and produces an evidence-cited
  Markdown report with run-over-run diffing. Never decides or acts.
- **Repository**: `discovery-lab/observation-agent/`.
- **Operational status**: ACTIVE — merged to `main` at commit
  `428e18f` [EV-01]; scheduled daily at `06:00 UTC` plus manual
  `workflow_dispatch`, `contents: read` only [EV-06]; two independently
  confirmed successful real runs on record [EV-11].
  **Note**: `main`'s current code does not include `EXEC-006`'s
  self-observation fix (see Section 7, Section 14) — that fix exists,
  tested and validated, on an unmerged branch [EV-16].
- **Version**: `v0.2` (implements `AGENT-001` v1.0, built `EXEC-002`,
  scheduled `EXEC-003`) [EV-07].
- **Evidence**: 45/45 tests passing on `main` [EV-03]; safety
  self-check passing (5/5 tests, including a test that proves the
  forbidden-pattern detector actually detects real violations, not
  just passing vacuously) [EV-05]; workflow file present and correct
  on `main` [EV-06]; `CONTRACT.md` present, states scope and safety
  boundary [EV-07].

### Ecosystem Headquarters v1.0

- **Purpose**: human-invoked interpretation and prioritization layer.
  Consumes Observation Agent's latest report plus a fixed set of named
  ecosystem artifacts (state files, the Recommendation Ledger, ADR
  listings, the project registry, `docs/proposals/`); computes 8
  documented health metrics, one Portfolio entry per configured
  repository, 6 Strategic Drift checks, 3 DRAFT-only Opportunity
  heuristics, and a 5-category Inconsistency classification; selects
  **exactly one** recommendation per run via a fully transparent
  scoring rubric; never re-scans a repository the way Observation
  Agent does [EV-07].
- **Repository**: `discovery-lab/headquarters/`.
- **Operational status**: ACTIVE, human-invoked only — merged to
  `main` at commit `8726ac1` [EV-01]; not scheduled (out of scope for
  this baseline, see Section 13). Run for real against the live
  5-repository ecosystem multiple times, most recently during this
  certification's own evidence-gathering [EV-13].
- **Version**: `v1.0` (implements `EXEC-004`, extended by `EXEC-004`'s
  Additional Execution Directive for Inconsistency Classification)
  [EV-07].
- **Evidence**: 111/111 tests passing on `main` [EV-04]; safety
  self-check passing (6/6 tests, including a network/HTTP-client
  detector `observation-agent` does not have) [EV-05]; `CONTRACT.md`
  present, containing a verbatim, enumerated Human Authority Boundary
  (Section 5, Section 10 below) [EV-07, EV-19].

No other component is certified as operational. `PROP-0001`'s own
ratification (`ACCEPTED`, Variant B, `2026-07-25` [EV-08]) is the
governance precondition both tools were built under, not itself a
running component.

---

## 4. Validation History

### EXEC-003 — Activate Observation Agent 001

- **Objective**: give Observation Agent a trigger/scheduling mechanism
  (`DL-002`'s finding that none existed anywhere in the ecosystem),
  narrowly scoped to this one tool.
- **Outcome**: GitHub Actions workflow built, tested, and — after an
  explicit human narrow-merge decision — merged to `main` (`428e18f`,
  PR #8) [EV-01, EV-11]. A real `workflow_dispatch` run and a real
  scheduled run were each independently confirmed successful [EV-11].
- **Major findings**: private-repository cross-repo access is not
  available to the default `GITHUB_TOKEN` without an explicit,
  administrative credential grant this session had no path to
  provision — resolved by scoping the schedule to `discovery-lab`
  only and documenting the other 4 repositories as an intentional,
  named `SKIP`, not a silent gap.
- **Defects discovered**: one, in Observation Agent's own
  `status_history_consistency` check (a bug-fix `HISTORY.md` entry's
  prose incidentally matched the "run heading" regex).
- **Defects resolved**: the same one, same task — regex tightened to
  require the run token be the heading's primary subject; regression
  test added.
- **Certification impact**: established the first scheduled,
  unattended, read-only ecosystem component. Baseline component.

### EXEC-004 — Ecosystem Headquarters v1.0

- **Objective**: build a strategic interpretation layer on top of
  Observation Agent's evidence — health, portfolio, drift, opportunity,
  prioritization, one recommendation per run, full explainability,
  never self-approving.
- **Outcome**: built, tested (111 tests), run for real, then — after
  an explicit human narrow-merge decision — merged to `main`
  (`8726ac1`, PR #9) [EV-01, EV-11]. First real recommendation:
  `HQ-0001` (discovery-lab's duplicate `ADR-0001` — two files both
  parse as that ID [EV-15]).
- **Major findings**: the Attention Engine's scoring rubric
  consistently ranked a small, evidence-confirmed, mechanical defect
  (`HQ-0001`) above 6 pre-existing Ledger proposals and 3 DRAFT
  opportunities — validating the "finish before expand" guiding
  principle operationally, not just as a stated value.
- **Defects discovered**: none in this execution itself; a later
  Additional Execution Directive extended the tool with Inconsistency
  Classification and replaced two hard-coded per-repo lookups with
  generic, bounded discovery, in the same task.
- **Defects resolved**: n/a (extension, not a bug fix).
- **Certification impact**: established the second operational
  component and the human-authority precedent both tools now share
  verbatim (Section 10).

### EXEC-005 — Ecosystem Operational Validation

- **Objective**: validate the *combined* operation of both tools under
  real conditions — explicitly no new features, no architectural
  redesign, evidence-gathering only.
- **Outcome**: 3 full local Observation Agent → Headquarters pairs run
  back-to-back plus 1 confirmed real scheduled GitHub Actions run on
  `main` [EV-11]. Delivered as
  `docs/investigations/INV-0004-ecosystem-operational-validation.md`.
  No code was changed in this execution.
- **Major findings**: recommendation **selection** is robust to
  repeated-run noise — `HQ-0001` stayed the sole, stable recommendation
  (score 6, identical evidence) across all 3 runs, because the
  Attention Engine reads the Recommendation Ledger and Headquarters'
  own Drift/Opportunity findings, never Observation Agent's raw
  observations directly.
- **Defects discovered**: **one real defect** — a self-referential
  feedback loop. Both tools' `reports/` directories live inside
  `discovery-lab`, one of the 5 scanned repositories; each local run's
  own output became the next local run's new input. Root cause: two
  literal examples of `[text]` immediately followed by `(path)` syntax
  in `observation-agent/README.md`'s own prose, indistinguishable by
  the `broken_references` check from a real link. Measured: 2 → 10 →
  58 new false-positive observations and 35 → 45 → 103 "Human
  Decisions Required" list items across 3 unchanged-input runs; Overall
  Health degraded 71% → 70% → 67% as a consequence. Confirmed absent
  from the CI/scheduled path (ephemeral, no memory between runs).
- **Defects resolved**: none in this execution — explicitly
  evidence-gathering only, per the task's own instruction; the defect
  was named and documented, not fixed.
- **Certification impact**: this execution is the direct source of
  Section 7's central Operational limitation and Section 8's accepted
  risk. It did not change any certified component's committed code.

### EXEC-006 — Narrow Maintenance: Self-Observation Defect Fix

- **Objective**: fix only the self-referential feedback-loop defect
  EXEC-005 found and its direct consequences — explicitly not a new
  agent, no architectural redesign, no full health-model recalibration.
- **Outcome**: implemented and merged to `claude/prop-0002-discovery-
  intake` (commits `0e4acad`, `1217473`) [EV-16] — **not yet merged to
  `main`**. Human Acceptance recorded: "EXEC-006 / Verdict: PASS," no
  reservations [EV-16].
- **Major findings**: while documenting the fix, the same `[text]`-
  immediately-followed-by-`(path)` adjacency pattern was reintroduced
  three times in new prose describing the defect itself — caught and
  reworded before commit, reverified against the actual detection
  regex.
- **Defects discovered**: the self-inflicted documentation recurrence
  above (caught and fixed in the same task, before commit); and,
  separately, the observation that `STATE.md`, `CHANGELOG.md`, and
  `INV-0004` itself independently contain the same `[text]`/`(path)`-
  shaped prose pattern, describing this very defect — named as
  out-of-scope, not fixed.
- **Defects resolved**: the feedback loop itself. A new,
  path-segment-aware, configurable `excluded_paths` mechanism now
  excludes each tool's own `reports/` directory from scanning; both
  `README.md` examples reworded. Verified via 58/58 passing tests
  (up from 45) [EV-12] and 3 repeated real runs against the live
  5-repository ecosystem holding flat with 0 new observations after
  the first run (versus the prior 2 → 10 → 58 compounding) [EV-13];
  `HQ-0001` reconfirmed as Headquarters' sole recommendation,
  unaffected [EV-13].
- **Certification impact**: **this is the pivotal fact for this
  certification's verdict.** The fix is real, tested, and validated —
  but it lives on a branch, not on `main`. The `main`-branch baseline
  being certified here still carries the defect EXEC-005 found. See
  Section 7 and Section 14.

---

## 5. Safety Certification

All four claims below were verified directly against `main` for this
certification, not assumed from prior narrative.

- **Read-only guarantees**: both tools' `tests/test_safety.py`
  statically scan their own actual source text for forbidden patterns
  (`subprocess.`, `os.remove(`, `shutil.rmtree(`, `.commit(`,
  `.push(`, `.merge(`, and — Headquarters only — any HTTP/network
  client call) and restrict file-opens in a writing mode to an
  explicit, named allow-list of modules (`report.py`/`cli.py` for
  Observation Agent; `cli.py`/`recommendation.py`/`history.py` for
  Headquarters) [EV-05]. Both suites include a self-check
  (`test_forbidden_patterns_actually_detect_violations`) proving the
  detector catches a real violation rather than passing vacuously
  [EV-20]. All safety tests pass on `main`: 5/5 (Observation Agent),
  6/6 (Headquarters) [EV-05].
- **Human authority preserved**: every output of both tools terminates
  in a file inside the tool's own `reports/` directory or a Markdown
  report; neither tool has any code path that reads
  `reports/recommendation-decisions.json` and then writes to any other
  repository. Headquarters' `CONTRACT.md` states this as a normative,
  enumerated boundary verbatim (Section 10 below, [EV-19]).
- **Repository integrity**: this certification's own evidence-gathering
  pass — 3 real Observation Agent runs, 1 real Headquarters run,
  against the live 5-repository ecosystem — was followed by
  `git status --short` on all 5 repositories, confirming zero
  modification to any of them beyond the tools' own `reports/`
  directories, which were then reverted to their pre-run committed
  state [EV-13, EV-17]. This is the same verification method used at
  the end of every prior execution (`EXEC-003` through `EXEC-006`)
  [EV-17].
- **No autonomous modification capability**: neither tool's
  `CONTRACT.md` grants any authority beyond producing a report;
  Headquarters' `Recommendation Evaluation` mechanism can only ever
  read a human-edited decision file, never write one [EV-19]. The
  Recommendation Ledger's 6 `PROPOSED` entries remain `PROPOSED` —
  none have been silently marked accepted by either tool [EV-18].

---

## 6. Regression Certification

- **Regression suites**: `observation-agent/tests/` (8 files on
  `main`) and `headquarters/tests/` (13 files on `main`), both
  `unittest`-based, both including a dedicated `test_safety.py`.
- **Current test counts (as deployed on `main`, verified directly for
  this certification)**: Observation Agent 45 tests, Headquarters 111
  tests — **156 total, all passing** [EV-03, EV-04].
- **Current test counts (on the unmerged `EXEC-006` branch, not yet
  part of the certified `main` baseline)**: Observation Agent 58 tests
  (+13: `test_scanner.py`, `TestSelfReferentialFeedbackLoop`,
  `test_cli_stability.py`, `TestExcludedPathsEquivalence`),
  Headquarters unchanged at 111 — 169 total [EV-12].
- **Operational validation**: beyond unit tests, both tools have been
  run against the real, live 5-repository ecosystem multiple times
  across `EXEC-002`, `EXEC-004`, `EXEC-005`, and this certification's
  own evidence pass — not only against synthetic fixtures [EV-13].
- **Known regression protections**: `test_safety.py`'s self-check
  guards against the safety detector silently becoming vacuous
  [EV-20]; `EXEC-006`'s new tests include a negative control
  (`test_without_the_exclusion_the_bug_reproduces`) proving the
  feedback-loop regression tests exercise a real fix, not an
  already-impossible scenario [EV-12].

---

## 7. Known Limitations

Only limitations directly observed in this repository's own evidence
are listed. None are inferred or assumed.

### Operational

- **The `main`-branch baseline being certified here still contains the
  self-referential feedback-loop defect `EXEC-005` found.** The fix
  (`EXEC-006`) is real, tested, and validated, but exists only on
  `claude/prop-0002-discovery-intake`, not on `main` [EV-01, EV-16].
  Under repeated local/manual combined-tool operation with unchanged
  repository content, the currently-deployed code will still compound
  new false-positive observations run over run, as measured in
  `EXEC-005` (2 → 10 → 58) [EV-14]. It does **not** affect the
  scheduled CI path (ephemeral, no memory between runs) [EV-06, EV-14].
- The scheduled GitHub Actions run currently covers `discovery-lab`
  only; the other 4 configured repositories are skipped by design, not
  by omission, because the default `GITHUB_TOKEN` cannot read private
  repositories outside the one the workflow runs in without an
  additional, administrative credential grant not provisioned in this
  ecosystem [EV-06].

### Architectural

- Headquarters' Portfolio Engine reports `Dependencies` as
  `INSUFFICIENT_EVIDENCE` for every entry — v1.0 does not parse a
  cross-repository dependency graph [EV-07].
- Headquarters' Strategic Drift Detector implements 6 of the
  categories named at design time; the remainder are documented as
  out of `v1.0` scope, not silently skipped [EV-07].
- `stale_state` and `registry_check` (Observation Agent) can only ever
  report `INSUFFICIENT_EVIDENCE`, never `MISMATCH` — both are
  mechanically incapable of confirming a contradiction, only of
  flagging a candidate for human review, by explicit design [EV-07].

### Governance

- `discovery-lab` itself is not listed in
  `project-memory/PROJECT_REGISTRY.md` [EV-10] — a real,
  Headquarters-flagged Governance Issue, unresolved as of this
  certification.
- No independent reviewer role exists for `discovery-lab`'s own
  investigation or tool-build reports; every certified component in
  this document was built and evaluated by the same kind of agent it
  now certifies. This is disclosed, not solved, consistent with every
  prior execution in this ecosystem naming the same unresolved
  limitation.
- Neither Observation Agent nor Headquarters is listed in
  `docs/ai-organization/EMPLOYEE-REGISTRY.md` — both are deliberately
  scoped as tool contracts (`CONTRACT.md`), not Employee Roles, and
  each `CONTRACT.md` states this explicitly [EV-09].

### Data Quality

- `STATE.md`, `CHANGELOG.md`, and `INV-0004` itself independently
  contain their own pre-existing `[text]`/`(path)`-shaped prose
  examples describing the `EXEC-005`/`EXEC-006` defect. These are
  real, stable, non-compounding matches against ordinary content —
  not a recurrence of the `reports/`-directory feedback loop — and
  were named but explicitly left unfixed by `EXEC-006` as out of that
  task's narrow scope [EV-16].

### Unknown

- This certification did not independently re-query GitHub's live
  Actions dashboard for the workflow's current enabled/run-history
  state; it relies on the workflow file's committed content on `main`
  [EV-06] and two previously-recorded, independently confirmed
  successful run outcomes in `CHANGELOG.md` [EV-11]. Whether the
  schedule has continued to fire successfully on every occurrence
  since the last recorded run is, honestly, unverified by this
  certification pass.

---

## 8. Accepted Risks

Only risks explicitly accepted by a recorded human decision are listed.

- **The `EXEC-005` feedback-loop defect's downstream consequences**:
  Petko's "Human Acceptance — EXEC-005" explicitly accepted the defect
  as real and confirmed it affects observation cleanliness, the
  Human-Decision list size, and the displayed Overall Health metric —
  but does **not** affect recommendation identity, ranking,
  deduplication, or read-only safety — and explicitly stated this was
  **not** a reason to roll back Headquarters. Verdict recorded: "PASS
  WITH A NAMED LIMITATION." [EV-14]
- **Scheduled coverage limited to `discovery-lab`**: accepted as of
  `EXEC-003`'s Human Acceptance, which confirmed the cross-repository
  credential-provisioning deferral exactly as executed, without
  requiring further tool or process changes [EV-11].
- **`registry.py`'s correction staying off `main`**: accepted as of
  `EXEC-003`'s Human Acceptance — deferred until
  `INV-0003`/`RECOMMENDATION-LEDGER.md` are independently reviewed and
  accepted, not treated as blocking [EV-11].
- **`AG-002`/`AG-003`'s `INSUFFICIENT_EVIDENCE` run-count findings**:
  accepted as of `EXEC-003`'s Human Acceptance — explicitly, no
  further parser work was requested [EV-11].
- **Not implementing `HQ-0001`**: accepted as of the `EXEC-004`
  Deployment Human Decision — advisory analysis only, the fix itself
  intentionally left to a separate human decision [EV-11].

---

## 9. Certification Metrics

| Metric | Value | Evidence |
|---|---|---|
| Monitored (configured) repositories | 5 (`project-memory`, `kod`, `discovery-lab`, `generative-discovery-engine`, `trust-engine`) | [EV-13] |
| Repositories reachable by the *scheduled* CI run | 1 (`discovery-lab`); other 4 documented `SKIP` by design | [EV-06] |
| Operational agents/tools certified | 2 (Observation Agent 001, Ecosystem Headquarters v1.0) | Section 3 |
| Validation executions to date | 4 (`EXEC-003`, `EXEC-004`, `EXEC-005`, `EXEC-006`) | Section 4 |
| Successful narrow-scope deployments to `main` | 2 (`428e18f`, `8726ac1`) | [EV-01] |
| Regression tests passing on `main` | 156 (45 + 111) | [EV-03, EV-04] |
| Regression tests passing on the unmerged `EXEC-006` branch | 169 (58 + 111) | [EV-12] |
| Confirmed successful real Observation Agent runs (CI) | 2 (`workflow_dispatch` at `EXEC-003`; scheduled run #2 at `EXEC-005`) | [EV-11] |
| Confirmed successful real local combined-tool run pairs | 4+ (3 at `EXEC-005`, 3 more during `EXEC-006`/this certification) | [EV-13, EV-14] |
| Recommendation stability across all recorded real runs | `HQ-0001`, score 6, identical evidence, every time (`EXEC-004` first appearance through this certification's own run) | [EV-13, EV-14] |
| Read-only executions with zero repository modification confirmed | Every recorded run to date (verified by `git status --short` each time) | [EV-17] |
| Recommendation Ledger entries, status | 6, all `PROPOSED`, none silently advanced | [EV-18] |

---

## 10. Human Authority Boundary

This section is normative — it states what the certified components
*cannot* do, not an aspiration.

**Neither Observation Agent nor Headquarters may, under any
circumstance:**

- modify any repository it observes;
- create, amend, or push a commit;
- open, merge, or comment on a pull request;
- edit the Recommendation Ledger, an ADR, a registry, or any other
  governance document;
- accept, reject, or otherwise change the status of any proposal,
  recommendation, or architectural decision;
- change any project's state file automatically;
- act on its own report or recommendation in any way.

This is Headquarters' `CONTRACT.md`'s own verbatim Human Authority
Boundary (`EXEC-004` §9) [EV-19], and it is a strict superset of what
Observation Agent's own `CONTRACT.md` independently states — the
narrower tool has never had *any* of these capabilities to begin with,
having been built read-only from `EXEC-002` onward [EV-07].

**The only party who can act on either tool's output is a human.** A
recommendation reaches `status: accepted` in
`headquarters/reports/recommendation-log.json` only because a human
edited `headquarters/reports/recommendation-decisions.json` by hand —
never because either tool decided its own output was good enough to
act on [EV-19]. Both `CONTRACT.md` files state that any future change
granting either tool write capability is explicitly out of scope for
the current contract and would require a new, explicit human decision
and a new safety review — not a routine code edit [EV-07].

---

## 11. Operational Invariants

Properties expected never to change without explicit human approval,
each supported by current implementation evidence:

- **Read-only execution.** Enforced by a static, self-verifying test
  in both tools (`test_safety.py`), not merely documented [EV-05,
  EV-20].
- **Recommendation-only governance.** Headquarters selects exactly one
  recommendation per run and never a ranked list — enforced by
  construction in `brief.py`, which only ever renders one recommendation
  under "Most Important Recommendation" [EV-07].
- **Human approval before repository modification.** No code path in
  either tool writes to any repository outside its own `reports/`
  directory [EV-05]; every Ledger entry stays `PROPOSED` until a human
  changes it by hand [EV-18].
- **Narrow deployment discipline.** Both merges to `main` to date were
  built on a fresh branch off `main`, isolated to the minimal file set,
  verified via `git status --short` and a passing test suite in
  isolation before merge — not the full engagement-history branch
  [EV-01, EV-11].
- **Evidence before recommendation.** Every Observation Agent finding
  cites repository, file, line number, and quoted text where available
  [EV-07]; every Headquarters recommendation, Drift finding,
  Opportunity, and Inconsistency cites its own supporting evidence
  [EV-07]; `INSUFFICIENT_EVIDENCE` is reported explicitly rather than a
  guess being asserted as fact, in both tools, by design [EV-07].
- **No single aggregate score.** Neither tool ever produces one number
  claiming to summarize the whole ecosystem's health across
  repositories or checks — enforced by its own test in Observation
  Agent; Headquarters' 8-metric Health Engine keeps each metric
  separate and explains its own formula in the rendered brief [EV-07].

---

## 12. Baseline Fingerprint

**Baseline identifier**: `CERT-001-ecosystem-baseline-v1.0`
**Certification date**: 2026-07-25

| Element | Identity |
|---|---|
| Certified repository | `discovery-lab`, `main` branch |
| Certified `main` commit | `8726ac1` (HEAD at certification time) [EV-01] |
| Certified initial commit | `7531956` |
| Certified component: Observation Agent | `observation-agent/`, v0.2, merged at `428e18f` |
| Certified component: Ecosystem Headquarters | `headquarters/`, v1.0, merged at `8726ac1` |
| Certified workflow | `.github/workflows/observation-agent.yml`, `contents: read`, daily `0 6 * * *` + `workflow_dispatch` [EV-06] |
| Certified governance precondition | `PROP-0001`, `ACCEPTED`, Variant B (Ecosystem Observatory), 2026-07-25 [EV-08] |
| Certified test baseline | 156 tests passing (45 + 111) on the certified commit [EV-03, EV-04] |
| Cross-referenced (observed, not certified) repositories | `project-memory`, `kod`, `generative-discovery-engine`, `trust-engine` |
| Known unmerged fix (not part of this baseline) | `EXEC-006` self-observation fix, commits `0e4acad`/`1217473` on `claude/prop-0002-discovery-intake` [EV-16] |

Any future certification (e.g. `CERT-002`) that includes the
`EXEC-006` merge, a scheduling change for Headquarters, or any new
component will supersede this fingerprint, not silently replace it —
this document remains the historical Baseline v1.0 record.

---

## 13. Future Evolution

Areas expected to evolve, named without proposing implementation:

- Broader observation coverage — scheduled scanning of the other 4
  repositories, currently blocked only by credential provisioning, not
  by architecture.
- Improved health model — `Overall Health`'s current 4-metric mean and
  the `Observation Cleanliness` metric's sensitivity to unresolved
  documentation-level false positives (Section 7, Data Quality) are
  named as areas a future recalibration could address; none is
  undertaken here.
- Portfolio intelligence — a cross-repository dependency-graph parser,
  currently absent (`Dependencies` stays `INSUFFICIENT_EVIDENCE` for
  every entry).
- Richer dependency reasoning — the remaining Strategic Drift
  categories named at `EXEC-004` design time but not implemented in
  `v1.0`.
- Whether either tool is formalized into a full Employee Role, and
  whether Headquarters is ever scheduled, both remain named, explicitly
  deferred, human-authorized decisions — not committed to any
  direction here.
- Merging `EXEC-006`'s validated fix to `main` — a routine merge
  decision, already unblocked, not undertaken as part of this
  certification (see Constraints).

---

## 14. Certification Verdict

### Verdict: **PARTIALLY CERTIFIED**

### Reasoning

**What is fully certified, without qualification, evidence-verified
directly against `main`:**

- Both tools' read-only safety guarantee — statically enforced, not
  merely claimed, self-checked against a real violation [EV-05, EV-20].
- The Human Authority Boundary — verbatim, enumerated, and consistent
  with every code path examined [EV-19].
- Recommendation correctness and stability — `HQ-0001` has never
  changed identity, score, or evidence across every real run recorded,
  including the runs performed during this certification itself
  [EV-13, EV-14].
- The scheduled CI path — unaffected by the one known defect, because
  it is ephemeral and has no memory between runs [EV-06, EV-14].
- Test coverage and narrow-deployment discipline — 156/156 tests
  passing on the certified commit, both merges independently isolated
  and verified before merge [EV-01, EV-03, EV-04, EV-11].

**What is not fully certified:**

- The `main`-branch code, as currently deployed, still exhibits the
  self-referential feedback-loop defect `EXEC-005` measured under
  repeated local/manual combined-tool operation — the exact usage
  pattern each tool's own `README.md` documents as a supported way to
  run it. This is a real defect in the currently-deployed baseline,
  not a hypothetical or future concern: it was measured compounding
  2 → 10 → 58 new false positives across 3 unchanged-input runs
  [EV-14]. A complete, tested, validated fix exists — but it has not
  been merged to `main`, so it is not part of the baseline this
  certification is evaluating [EV-16].

**Why this is "partially," not "not," certified**: the defect never
once compromised safety, human authority, or recommendation
correctness in any recorded run — including the very runs that
measured it. It is precisely bounded to a downstream display metric
(`Observation Cleanliness`, `Overall Health`) under one specific
operational mode, already understood, already fixed on a validated
branch, and blocked only on a routine merge decision — not a redesign,
not further investigation, not new engineering.

**Why this is not simply "certified"**: doing so would represent the
`main`-branch baseline as free of a defect it demonstrably still has,
which the certification's own success criteria ("no future work is
represented as operational," "another reviewer could independently
verify the baseline") do not permit. A reviewer who clones `main`
today and runs both tools locally, repeatedly, against unchanged
content will reproduce the compounding behavior `EXEC-005` measured —
this is directly, mechanically reproducible, not a matter of
interpretation.

### What would upgrade this to CERTIFIED (unqualified)

Merging `EXEC-006`'s already-validated fix to `main` through the same
narrow-merge discipline both prior components used — itself a routine,
low-risk, separately-authorized human decision, not new work.

---

*This document and its evidence appendix are the complete `CERT-001`
deliverable. No repository other than the addition of these two files
was modified to produce this certification.*
