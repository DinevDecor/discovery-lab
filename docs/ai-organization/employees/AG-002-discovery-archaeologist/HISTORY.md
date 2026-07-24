# History — AG-002 Discovery Archaeologist

Employee ID: **AG-002** · Role Name: **Discovery Archaeologist** ·
Status: **Prototype / DRAFT / EXPERIMENTAL / NOT ADOPTED** · Version:
**v0.1**

This is an append-only log. Entries are never edited or removed once
written — only new entries are added, at the bottom.

## 2026-07-24 — Role created

AG-002 v0.1 prototype created: full document set (`CONTRACT.md`,
`ROLE.md`, `INPUTS.md`, `OUTPUTS.md`, `LIMITATIONS.md`, `CHECKLIST.md`,
`METRICS.md`, `RUN-PROTOCOL.md` — the Recovery Protocol v0.1 —
`PROMPT.md`, `STATUS.yaml`, this file). Status set to
`prototype` rather than the "production-ready" language used in the
task that requested this Role, to preserve `../../
HIRING-LIFECYCLE-DRAFT.md`'s existing lifecycle discipline — recorded
explicitly, not applied silently.

## 2026-07-24 — PILOT-RUN-0001

First real run executed, immediately after creation. Scope: the
Project Memory archive (`project-memory/archive/`) plus current-state
files in the same repository, for comparison. The "diary archive" named
in the requesting task could not be located anywhere accessible and was
recorded as `INSUFFICIENT ACCESS`, not substituted. Report:
`runs/PILOT-RUN-0001-recovery-report.md`. Recovered: 7 ideas, 4 repeated
themes, 5 idea-evolution timelines, 2 forgotten ideas, 4 candidate
investigations (none created), 2 contradictions (one documented
revision, one principle/outcome gap), 6 open questions.

## 2026-07-24 — PILOT-RUN-0002 (blocked at Stage 1, no report produced)

Second real run requested. Unlike PILOT-RUN-0001, exactly one source
was authorized this time, with no substitution permitted: a diary
archive at Google Drive, "Project Memory → Archive → oneDay 6.zip" (or
its already-extracted folder at the same location). Stage 1 (Historical
Sources / Lookup, `RUN-PROTOCOL.md`) was attempted by three distinct
methods in this session — `search_files` (`title contains 'oneDay
6'`), `search_files` (`title contains 'Project Memory'`), and
`list_recent_files` — all against the Google Drive MCP connector. All
three calls returned identically: `MCP error -32003: MCP tool call
requires approval`. No file, folder, or metadata was ever retrieved.
No source was ever reached, so no candidate could be discovered, no
citation linked, and no clustering performed — the run halted at Stage
1 per `RUN-PROTOCOL.md`'s Stop rule and the requesting task's own
instruction, rather than substituting Project Memory or any other
source. No Recovery Report exists for this run; producing one would
have misrepresented zero actual scanning as a completed pilot.
Reported to the requester verbatim as: `BLOCKED — Diary archive exists
but is not accessible from the current execution environment.` No
source document was read, modified, or invented. `runs_completed` in
`STATUS.yaml` was not incremented — no run was actually completed.
