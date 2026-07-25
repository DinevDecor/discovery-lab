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
and the execution log).

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
- **No trigger/scheduling mechanism.** Per `DL-002`'s finding, none
  exists anywhere in this ecosystem. This tool is invoked by a human
  running a command; it does not run itself.

## Provenance

Implements `docs/proposals/AGENT-001-observation-agent/` under task
`EXEC-002`. See `CONTRACT.md` for the tool's operating contract.
