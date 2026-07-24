# Memory Source Registry

**Status: DRAFT / Experimental Process.** This registry lists every
external memory source ever registered, at any status, including
deprecated ones. Entries are never deleted — only appended or updated
in place, per the same append-only convention already used in
`../EMPLOYEE-REGISTRY.md` and `../ORB/ORB-REGISTRY.md`. See
`MEMORY-SOURCE-PROTOCOL.md` for the full schema, Connection Protocol,
and governance this table implements.

## Entries

### MEM-001

```
source_id: MEM-001
name: project-memory archive
type: git_repository
locator:
  repository: project-memory
  owner: DinevDecor
  path_within_repo: archive/
  ref: main
access_requirements: read-only Git fetch access
status: active
steward: Implementer session (Claude Code)
added: 2026-07-24
last_verified: 2026-07-24
notes: >
  The only source actually scanned in AG-002's PILOT-RUN-0001
  (../employees/AG-002-discovery-archaeologist/runs/
  PILOT-RUN-0001-recovery-report.md). Verified reachable and readable
  as of that run — four documents inside this path were read in full.
  Registered here after the fact, honestly, not in advance of evidence.
```

### MEM-002

```
source_id: MEM-002
name: Project Memory diary archive (Google Drive)
type: google_drive
locator:
  drive_or_shared_drive: UNKNOWN
  folder_path_or_id: UNKNOWN
access_requirements: read-only Google Drive API scope, gated behind a
  per-call platform tool-call approval that this client cannot satisfy
  in a resumable way (see INFRA-SPRINT-01-report.md, section 9 -
  confirmed a platform limitation, not a missing scope or missing
  authorization)
status: unverified
steward: Implementer session (Claude Code)
added: 2026-07-24
last_verified: null
notes: >
  Named by the requesting task as "Project Memory -> Archive -> oneDay
  6.zip". Lookup was attempted nine times across three tasks
  (PILOT-RUN-0002, Infrastructure Sprint 01, and a live approval test
  conducted with Petko actively granting approval in real time), via
  two distinct tools (search_files, list_recent_files) - every attempt
  returned "MCP error -32003: MCP tool call requires approval" before
  any Drive API call was reached, including the call made while
  approval was being actively granted. Closed, 2026-07-24, as a
  platform limitation (INFRA-SPRINT-01-report.md section 9): connector
  status CONNECTED, organization authorization COMPLETE, per-call
  approval flow NON-RESUMABLE / RETROACTIVE, unattended Google Drive
  access NOT SUPPORTED IN THIS CLIENT. No further retries planned.
  drive_or_shared_drive and folder_path_or_id remain honestly UNKNOWN -
  Lookup never succeeded, so none was invented. An alternative
  architecture for AG-002 is proposed, not yet implemented, in
  ../../adr/ADR-0002-ag002-alternative-memory-access.md - Google Drive
  remains the intended canonical source if a working access path is
  ever found; this entry is not deprecated, only blocked.
```

## Reading this table

- **Current total: 2 sources registered. 1 active. 0 deprecated. 1
  unverified.**
- `MEM-002` is the first `google_drive`-type entry — see
  `MEMORY-SOURCE-PROTOCOL.md`, "What this document does not do," which
  is now partially superseded by this addition (a `google_drive` entry
  now exists, though still unverified — the Protocol document itself is
  not edited by this addition).
- `KOD`, `generative-discovery-engine`, and `trust-engine` are not
  registered, despite being technically accessible in this session from
  unrelated earlier work — none has actually been used as a memory
  source by any Role yet. See `MEMORY-SOURCE-PROTOCOL.md` for the
  reasoning.
