# Contract — Observation Agent 001 (`observation-agent/`)

Version: **v0.2** (implements `AGENT-001` v1.0; built under `EXEC-002`,
activated on a schedule under `EXEC-003`)
Core Principle: **Observe. Report evidence. Do not decide, do not act.**

This is a **tool contract**, not an Employee Role contract. `EXEC-002`
explicitly forbade adding governance or starting a new review cycle for
this task, so this deliberately does not instantiate a new Employee ID
or the full `CONTRACT.md`/`STATUS.yaml`/`HISTORY.md`/`ROLE.md` document
set used under `docs/ai-organization/employees/`. If this tool is later
formalized into a Role (e.g. a successor to `AG-001`, or a new
Employee ID), that is a separate, later, human-authorized decision —
not implied or pre-approved by this document.

## Scope of authority

Read-only observation of the repositories listed in `config.json` (a
human-invoked run) or `config.ci.json` (the scheduled run — see
README's "CI Limitations": only `discovery-lab` itself is reachable
from the scheduled workflow today, by design, not by omission). No
authority beyond producing a report is granted, whether invoked by a
human running `run_observation_agent.py` directly or by the daily
GitHub Actions schedule in `.github/workflows/observation-agent.yml`.
The schedule is itself scoped to `contents: read` only and never
performs any action beyond running the agent and uploading its output
as a workflow artifact — it does not grant this tool any authority the
human-invoked path didn't already have. `DL-002`'s wider finding that
no *other* action anywhere in this ecosystem is triggered by anything
but a human message is otherwise unaffected: this schedule produces
reports, never actions.

## Rights

- The right to report `INSUFFICIENT_EVIDENCE` whenever a check cannot
  fully resolve a question mechanically, without this being treated as
  a defect in the tool (see README's Limitations section).
- The right to have a check's finding disputed or corrected by a human
  without that requiring a change to this contract.

## Responsibilities

- Produce exactly one report per run, in the format defined by
  `AGENT-001`'s Reporting Specification (Summary, New Observations,
  Repeated Findings, Resolved Findings, Risk Changes, Confidence,
  Evidence Links, Recommended Actions, Human Decisions Required).
- Cite evidence — repository, file path, line number where available,
  quoted text — for every finding.
- Never claim a single aggregate score across repositories or checks
  (`PROP-0001`'s explicit rule).
- Never take a write action against any observed repository, under any
  circumstance.

## Safety

Enforced by `tests/test_safety.py`, not just stated here: no source
file outside `report.py`/`cli.py` may open a file in a writing mode,
and no source file anywhere may invoke `subprocess`, `os.remove`,
`shutil.rmtree`, `.commit(`, `.push(`, `.merge(`, or equivalent. Both
constraints are checked by scanning the actual source text, with a
self-check proving the detector catches real violations rather than
passing vacuously.

## Executor independence

This contract binds the tool, not whoever runs it. Any human or
automated process invoking `run_observation_agent.py` operates under
the same scope and safety constraints; nothing here depends on a
specific AI model or invoking party.

## Revocation and change

This tool may be modified, extended with new checks, or retired at any
time by direct repository change — it is source code under normal
version control, not a ceremonial Role requiring a lifecycle process.
A change that would grant it any write capability against an observed
repository is out of scope for this contract entirely and would
require a new, explicit human decision and a new safety review, not a
routine edit.
