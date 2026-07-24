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
connectivity: CONNECTED
agent_access: HUMAN-INTERACTIVE / NOT AGENT-OPERATIONAL
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
  Lookup never succeeded, so none was invented. Reclassified 2026-07-24
  (connectivity/agent_access fields added) per the "Resolve AG-002
  Memory Access Blocker" task: Google Drive stays registered and stays
  the human-facing canonical archive, but is no longer treated as a
  source any Role reads directly - see MEM-003 for the operational
  path, and INFRA-SPRINT-01-report.md section 10 for the decision
  record. Not deprecated - a human can still open and read this
  archive; it is simply not agent-operational in this client.
```

### MEM-003

```
source_id: MEM-003
name: Repository operational memory mirror (discovery-lab/memory/)
type: git_repository
locator:
  repository: discovery-lab
  owner: DinevDecor
  path_within_repo: memory/
  ref: main
access_requirements: read-only Git fetch access (identical to MEM-001 -
  no new capability required of any Role)
status: active
connectivity: CONNECTED
agent_access: AGENT-OPERATIONAL — PRIMARY FOR AG-002
steward: Implementer session (Claude Code)
added: 2026-07-24
last_verified: 2026-07-24
notes: >
  Implements ../../adr/ADR-0002-ag002-alternative-memory-access.md
  (ACCEPTED). A small, purpose-scoped, human-maintained Git mirror -
  not a bulk copy of Google Drive, per that ADR's own constraint
  ("do not duplicate the entire Google Drive. Store only the files
  required for active agent work"). Populated via manual import only
  (memory/IMPORT-PROCEDURE.md) - no automatic Drive synchronization
  exists or is planned for v1. Every filed file carries full
  provenance metadata (memory/PROVENANCE-SYNC-SPEC.md) and a
  memory/source-manifest.md entry. VERIFIED 2026-07-24 via
  MIRROR-VERIFY-0001
  (../employees/AG-002-discovery-archaeologist/runs/
  MIRROR-VERIFY-0001-recovery-report.md): AG-002 discovered this
  source, read a filed file in full, preserved its provenance,
  extracted one finding, wrote the result to
  memory/observations/MIRROR-VERIFY-0001-observation-0001.md, and did
  not modify the source - all per its existing, unmodified Recovery
  Protocol. The verified file was a labeled synthetic test fixture, not
  real content (no real content has been imported yet) - status is
  promoted to active/primary because the *mechanism* is proven, not
  because any real historical material has been mirrored. See
  INFRA-SPRINT-01-report.md section 10 for the full verification
  record and completion verdict. Superseded as AG-002's *default*
  source, 2026-07-24 (see MEM-004) - MEM-003 remains active as the
  downstream "Knowledge/Registry/Ledger" layer, not the front door.
```

### MEM-004

```
source_id: MEM-004
name: Reality Inbox (discovery-lab/reality-inbox/)
type: git_repository
locator:
  repository: discovery-lab
  owner: DinevDecor
  path_within_repo: reality-inbox/
  ref: main
access_requirements: read-only Git fetch access (identical to MEM-001/
  MEM-003 - no new capability required of any Role)
status: active
connectivity: CONNECTED
agent_access: AGENT-OPERATIONAL — DEFAULT SOURCE FOR AG-002
steward: Implementer session (Claude Code)
added: 2026-07-24
last_verified: 2026-07-24
notes: >
  Implements the "Create the Reality Inbox" task. The organization-wide,
  human-facing intake layer: a human drops a file into
  reality-inbox/DROP HERE/ (one folder, no routing decision required of
  the human) and an agent/steward handles everything else - manifest
  creation (reality-inbox/manifests/), duplicate/readability/sensitivity
  checks, processing, and filing into reality-inbox/processed/. Not a
  second archive and not a source of truth by itself - see
  reality-inbox/PROCESSING-PROTOCOL.md, "No claim of verified truth."
  AG-002's INPUTS.md, LIMITATIONS.md, RUN-PROTOCOL.md, and CHECKLIST.md
  were all given small, additive edits (not a redesign) establishing
  this as AG-002's default operational source, gated on manifest
  status: ACCEPTED, with a new BLOCKED escalation value for insufficient
  provenance. VERIFIED 2026-07-24 via REALITY-VERIFY-0001
  (../employees/AG-002-discovery-archaeologist/runs/
  REALITY-VERIFY-0001-recovery-report.md): a labeled synthetic fixture
  was dropped, manifested (RI-0001), processed, read by AG-002, one
  finding extracted and written to
  memory/observations/REALITY-VERIFY-0001-observation-0001.md, and the
  source left unmodified. No real content has been processed yet - only
  the mechanism is proven, same honesty as MEM-003's own verification.
  Relationship to MEM-003: this is the front door; memory/ (MEM-003)
  remains the downstream filed/validated layer content can land in.
  AG-001 was reviewed for a compatibility update and found not to need
  one - it observes discovery-lab's own repository structure, not
  external evidence, so this task made no changes to it.
  AMENDED 2026-07-24 per
  ../../adr/ADR-0004-local-drive-synced-reality-inbox.md
  (ACCEPTED - design complete, awaiting local verification):
  reality-inbox/DROP HERE/ (this entry's git-tracked folder) is now the
  documented fallback for sessions without local filesystem access
  (confirmed via mount/env checks that this session has none); the
  primary human-facing folder for local sessions (Claude Desktop, local
  Claude Code) is a local path outside this repository entirely -
  "G:\My Drive\Projects\discovery-lab\DROP HERE" - which this or any
  other remote session cannot create, populate, or verify. This
  locator/access_requirements block still describes the git_repository
  side (manifests/, processed/, fixtures/) which is unchanged and
  unaffected by which folder fed it.
```

## Reading this table

- **Current total: 4 sources registered. 3 active. 0 deprecated. 1
  unverified.**
- `MEM-002` is the first `google_drive`-type entry — see
  `MEMORY-SOURCE-PROTOCOL.md`, "What this document does not do," which
  is now partially superseded by this addition (a `google_drive` entry
  now exists, though still unverified — the Protocol document itself is
  not edited by this addition).
- **`connectivity` and `agent_access` are new, minimal fields**, added
  only to `MEM-002` and `MEM-003` so far — a small, pragmatic step, not
  the full two-axis `Connectivity`/`Authority` schema migration
  `ADR-0001-human-authority-gates.md` §5 describes and
  `ADR-0001-migration-plan.md` Item 2 still lists as **NOT STARTED**.
  `MEMORY-SOURCE-PROTOCOL.md`'s core schema table is unmodified by this
  addition; these two fields are recorded here as an ad hoc extension,
  not a protocol change.
- `KOD`, `generative-discovery-engine`, and `trust-engine` are not
  registered, despite being technically accessible in this session from
  unrelated earlier work — none has actually been used as a memory
  source by any Role yet. See `MEMORY-SOURCE-PROTOCOL.md` for the
  reasoning.
