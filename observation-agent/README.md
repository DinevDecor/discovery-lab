# Observation Agent 001

`EXEC-002`'s implementation of the `AGENT-001` proposal
(`docs/proposals/AGENT-001-observation-agent/`): a small, human-invoked,
read-only tool that scans the ecosystem's five in-scope repositories
(per `PROP-0001` Variant B) for mechanically detectable inconsistencies
and produces an evidence-cited Markdown report. It does not decide
anything and does not write to any repository it observes.

## What it does

Each run walks every configured repository and runs five checks:

- **`broken_references`** — Markdown `[text](path)` links whose target
  does not resolve to a real file.
- **`orphan_files`** — zero-byte files.
- **`stale_state`** — a declared state-file date far older than every
  other file's modification time in the repo (`INSUFFICIENT_EVIDENCE`,
  not `MISMATCH` — see Limitations).
- **`status_history_consistency`** — a `STATUS.yaml`'s `runs_completed`
  count against the number of `## YYYY-MM-DD — RUN-N`-shaped headings
  in its sibling `HISTORY.md` (`INSUFFICIENT_EVIDENCE` — see
  Limitations).
- **`registry_check`** — markdown-table rows whose Status column reads
  as `ACTIVE`-shaped with no in-row citation (always
  `INSUFFICIENT_EVIDENCE` — this check can only flag a candidate for
  review, never confirm a contradiction).

Every finding follows the `AGENT-001` Observation Model: `Event`,
`Evidence`, `Verification Method`, `Confidence`
(`MATCH`/`MISMATCH`/`INSUFFICIENT_EVIDENCE`), `Possible
Interpretation`, `Recommended Action`, `Human Needed?`. There is no
step after Human — this tool never acts on its own findings, and
nothing in this codebase is capable of doing so (enforced by
`tests/test_safety.py`, not just documented).

Consistent with `PROP-0001`: the report never produces a single
aggregate score across repositories or checks.

## How to run it

```
cd observation-agent
python3 run_observation_agent.py
```

No dependencies beyond the Python 3 standard library. Optional flags:

```
python3 run_observation_agent.py --config path/to/config.json --reports-dir path/to/reports
```

Each run writes exactly three files, all inside `reports/`:
`observation-report-<timestamp>.md`, `execution-log-<timestamp>.md`,
and `last_run_observations.json` (a snapshot used to diff the next run
against this one — new findings, repeated findings, and resolved
findings are reported separately).

## Configuration

`config.json` lists the repositories to scan by absolute path. Add or
remove a repository by editing this file; nothing in the code needs to
change. A repository whose configured path does not exist on disk is
skipped, not treated as an error (see the report's own Skipped list
and the execution log). `config.ci.json` is a second, separate config
used only by the scheduled GitHub Actions run — see "Scheduled
Activation" and "CI Limitations" below.

## Scheduled Activation (`EXEC-003`)

Per `DL-002`'s finding that no ratified trigger/scheduling mechanism
existed anywhere in this ecosystem, `EXEC-003` activated one for this
tool specifically: `.github/workflows/observation-agent.yml`, a
GitHub Actions workflow that runs the unmodified agent automatically.

- **Mechanism**: GitHub Actions, chosen because it is repository-native
  and can be configured with genuinely read-only permissions — no
  separate service, credential store, or daemon needed.
- **Schedule**: once daily, `06:00 UTC` (cron `0 6 * * *`, the
  workflow's `on.schedule` block). To change it, edit that one line
  and push — no other change is needed.
- **Manual run**: GitHub → this repository → **Actions** tab →
  **Observation Agent 001** → **Run workflow**. This uses the exact
  same job the schedule uses (`workflow_dispatch` on the same
  workflow file), so a manual run is a faithful test of what the
  schedule will do.
- **Permissions**: `contents: read`, declared at both the workflow
  level and the job level, and nothing else — no `issues`, no
  `pull-requests`, no `write` of any kind, anywhere in the file.
  `actions/checkout` is called with `persist-credentials: false`, so
  no token is even left on disk for the job to (mis)use after
  checkout. No repository secret is required for the workflow to run
  at all (see CI Limitations for what a secret would additionally
  unlock).
- **Artifact location**: every run — scheduled or manual — uploads
  `observation-agent/reports-ci/` (the report, the execution log, and
  the run's JSON snapshot) as a workflow artifact named
  `observation-agent-report-<run number>`, retained 90 days, visible
  under that run's **Summary** page in the Actions tab.
- **Failure behavior**: the workflow's run step fails (turns the
  Actions run red) only if the agent itself cannot complete — a real
  crash, not a finding. `MISMATCH` and `INSUFFICIENT_EVIDENCE`
  findings are expected output, never a failure. A short **Run
  Summary** (`SUCCESS` / `PARTIAL` / `FAILURE`, plus the Confidence
  breakdown) is published to the Actions run's own Job Summary by
  `ci_summary.py`, so the outcome is visible without opening the
  artifact. `PARTIAL` covers both "a repository was skipped" (expected
  every run, see CI Limitations) and "a check itself errored" (not
  expected — worth reading the execution log if it appears).
- **Disabling the schedule immediately**: GitHub → **Actions** tab →
  **Observation Agent 001** → **⋯** menu → **Disable workflow**. This
  takes effect immediately, requires no commit, and is fully
  reversible from the same menu. Editing or deleting the `schedule:`
  block in the workflow file is an equivalent, code-level alternative,
  but the UI toggle is faster for an urgent stop.
- **How a human transfers an accepted finding into the Recommendation
  Ledger**: this tool never writes to the Ledger itself — that is a
  deliberate safety boundary, not an oversight (see Safety
  guarantees). To act on a finding: open the report artifact from the
  relevant run, decide whether the finding is worth recording, and if
  so, add a new entry to
  `docs/investigations/RECOMMENDATION-LEDGER.md` by hand, following
  its existing schema (`recommendation_id`, `source_investigation` —
  cite the specific report filename and run — `destination_repository`,
  `date_proposed`, `status: PROPOSED`, `summary`). This is the same
  manual process `STRATEGIC-001` used to populate the Ledger's first
  entries; the scheduled agent only ever supplies evidence for that
  human step, never performs it.

## Safety guarantees

This agent is technically read-only. It does not commit, push, merge,
edit, rewrite, or delete anything in any repository it observes; the
only files it ever writes are the three files above, inside its own
`reports/` directory.

This is enforced, not just asserted: `tests/test_safety.py` statically
scans every source file for forbidden patterns (`subprocess.`,
`os.remove(`, `shutil.rmtree(`, `.commit(`, `.push(`, `.merge(`, and
more) and for any file opened in a writing mode outside the two
modules (`report.py`, `cli.py`) allowed to write this agent's own
output — and includes a self-check proving the detector actually
catches real violations, not just passes vacuously.

## Limitations

These are documented scope boundaries, not bugs to be silently
tightened away — each was chosen deliberately to avoid the tool
overclaiming certainty it doesn't have:

- **`broken_references`** only recognizes Markdown `[text](path)`
  links, not bare inline-code paths or other reference styles. This
  trades recall for precision: a check that flags every string that
  merely looks like a path would produce far more false positives.
- **`stale_state`** reports `INSUFFICIENT_EVIDENCE`, never `MISMATCH`,
  because file modification times are known to be unreliable in
  shallow clones and after certain git operations (a lesson this
  session learned firsthand investigating `kod` during `DL-001`).
- **`status_history_consistency`** only recognizes a "run entry" when
  a `RUN-N`-shaped token is the *primary subject* of a heading,
  immediately after the date and dash (e.g. `## 2026-07-24 —
  RUN-0001`, `## 2026-07-24 — PILOT-RUN-0002 ...`). This precision was
  necessary: a looser pattern produced a real false positive against
  the live `AG-001` role, where a bug-fix entry's *prose* incidentally
  mentioned a run number. The tightened pattern still cannot recognize
  run identifiers that don't use a literal "RUN-" token (e.g.
  `MIRROR-VERIFY-0001`) or headings that bundle several run IDs into
  one heading (e.g. `STRESS-RUN-0003, -0004, -0005`) — both confirmed
  against the live `AG-002` role. Recognizing those would require
  semantic judgment, not mechanical counting, so a count mismatch is
  reported as `INSUFFICIENT_EVIDENCE` for human review, never asserted
  as a confirmed defect.
- **`registry_check`** can only detect the *absence* of an in-row
  citation next to an `ACTIVE`-shaped status. It has no way to verify
  whether a cited or uncited claim is actually true, so it always
  reports `INSUFFICIENT_EVIDENCE`.
- **Self-review problem**: this tool, like every deliverable in this
  session, was built and evaluated by the same kind of agent it
  reports on. It has no independent reviewer. This is disclosed, not
  solved — consistent with how `ARCH-001`, `EXEC-001`, `DL-002`, and
  `AGENT-001` each already disclosed the same unresolved limitation.
- **Trigger/scheduling mechanism**: resolved by `EXEC-003` for this
  tool specifically (see Scheduled Activation above) — this no longer
  describes a gap for the Observation Agent itself. `DL-002`'s wider
  finding — that no *other* action anywhere in this ecosystem is
  triggered by anything but a human message — is unaffected; this
  workflow only ever produces a report, never an action.

### CI Limitations (why the schedule only fully scans `discovery-lab`)

All 5 configured repositories
(`project-memory`, `kod`, `discovery-lab`, `generative-discovery-engine`,
`trust-engine`) are separate, **private** repositories in the same
GitHub org. `actions/checkout`'s default `GITHUB_TOKEN` only has read
access to the repository the workflow itself runs in
(`discovery-lab`) — it cannot check out the other 4 without an
additional credential, because GitHub does not extend a workflow's
default token across private repositories, even within the same org,
without an explicit grant.

Getting that access would require either:

1. A fine-grained personal access token scoped to **read-only**
   `contents` on the other 4 repos, stored as a repository secret and
   referenced by the workflow's checkout steps for those repos; or
2. Each of the other 4 repos' own **Settings → Actions → General →
   Access** page explicitly allowing `discovery-lab`'s workflows to
   read them.

Both are provisioning/administrative actions on repositories this
session has no path to configure (secret creation and cross-repo
Actions-access settings are both write/admin-level operations on
those repositories, not read-only observation) — exactly the
situation the task's own Security requirements anticipated: *"Do not
use credentials with write access unless technically unavoidable. If
unavoidable, stop and report the blocker rather than proceeding."*
Rather than escalate to a write-capable credential to force full
coverage, the scheduled workflow does what it safely can with zero
additional credentials: it fully scans `discovery-lab` and reports the
other 4 as `SKIP`ped, using the agent's existing, already-tested
"repository path does not exist" failure-safe behavior (see
`config.ci.json`) — not a new workaround, the same mechanism a human
run already relies on when a configured repository isn't cloned
locally.

**Full 5-repository coverage remains available today** the way it
always has: a human running `python3 run_observation_agent.py` (the
default `config.json`) in an environment where all 5 repositories are
already checked out side by side, exactly as `EXEC-002`'s original
run and this task's own validation both did. Extending the *scheduled*
run to all 5 repositories is a separate, later, human-authorized step
(provisioning one of the two credentials above) — named here as a
remaining human action, not attempted.

## Provenance

Implements `docs/proposals/AGENT-001-observation-agent/` under tasks
`EXEC-002` (build) and `EXEC-003` (schedule). See `CONTRACT.md` for
the tool's operating contract.
