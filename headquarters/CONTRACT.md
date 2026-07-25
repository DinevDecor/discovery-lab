# Contract — Ecosystem Headquarters v1.0 (`headquarters/`)

Version: **v1.0** (implements `EXEC-004`)
Core Principle: **Observe. Understand. Prioritize. Explain. Recommend. Never act.**

This is a **tool contract**, not an Employee Role contract — same
precedent as `observation-agent/CONTRACT.md`. `EXEC-004` did not ask
for a new Employee ID or the full `docs/ai-organization/employees/`
document set, so this deliberately does not instantiate one. If
Headquarters is later formalized into a Role, that is a separate,
later, human-authorized decision.

## Scope of authority

Read-only interpretation of artifacts already produced elsewhere in
the ecosystem — Observation Agent reports, the Recommendation Ledger,
state files, ADR listings, the project registry, `docs/proposals/`.
Headquarters never re-scans a repository the way observation-agent
does; every path it reads is a specific, pre-configured artifact
location. No authority beyond producing an Executive Brief and a
persistent recommendation log (both inside its own `reports/`
directory) is granted, whether invoked directly by a human or (in a
future, separately-authorized phase) on a schedule.

## Human Authority Boundary (EXEC-004 §9, verbatim scope)

Headquarters MUST NOT, under any circumstance:

- modify any repository;
- create a commit;
- edit the Registry, an ADR, or any governance document;
- accept an architectural proposal;
- create or merge a pull request;
- change any project's state file automatically.

Every output is advisory only. A recommendation reaching
`status: accepted` in `reports/recommendation-log.json` happens because
a human edited `reports/recommendation-decisions.json` by hand — never
because this tool decided its own recommendation was good enough to
act on.

## Rights

- The right to report `INSUFFICIENT_EVIDENCE` for any metric, finding,
  or Portfolio field it cannot mechanically support, without that
  being treated as a defect (see README's Limitations).
- The right to have any finding, score, or recommendation disputed or
  corrected by a human without requiring a change to this contract.

## Responsibilities

- Select exactly one recommendation per run — never a list, never a
  ranked top-N. Every other candidate considered is shown for
  transparency only, explicitly not as a secondary priority list.
- Cite evidence — repository, file, and specific claim — for every
  metric, Portfolio field, Drift finding, Opportunity, and
  Recommendation.
- Assign persistent `HQ-000N` identifiers and never silently drop or
  renumber one that already exists.
- Never claim a recommendation is accepted, implemented, useful,
  obsolete, or incorrect without a human-recorded decision behind that
  claim.

## Safety

Enforced by `tests/test_safety.py`, reusing the same detector
`observation-agent/tests/test_safety.py` established: no source file
outside `cli.py`/`recommendation.py`/`history.py` may open a file in a
writing mode, no source file anywhere may invoke `subprocess`,
`os.remove`, `shutil.rmtree`, `.commit(`, `.push(`, `.merge(`, a
network/HTTP client, or equivalent — checked by scanning the actual
source text, with a self-check proving the detector catches real
violations rather than passing vacuously.

## Executor independence

This contract binds the tool, not whoever runs it. Any human or
automated process invoking `run_headquarters.py` operates under the
same scope and safety constraints; nothing here depends on a specific
AI model or invoking party.

## Revocation and change

This tool may be modified, extended with new checks, or retired at any
time by direct repository change — source code under normal version
control, not a ceremonial Role requiring a lifecycle process. A change
that would grant it any write capability against an observed
repository, or any capability to act on its own recommendations, is
out of scope for this contract entirely and would require a new,
explicit human decision and a new safety review, not a routine edit.
