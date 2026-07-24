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

## Reading this table

- **Current total: 1 source registered. 1 active. 0 deprecated. 0
  unverified.**
- No `google_drive`-type entry exists yet — see
  `MEMORY-SOURCE-PROTOCOL.md`, "What this document does not do."
- `KOD`, `generative-discovery-engine`, and `trust-engine` are not
  registered, despite being technically accessible in this session from
  unrelated earlier work — none has actually been used as a memory
  source by any Role yet. See `MEMORY-SOURCE-PROTOCOL.md` for the
  reasoning.
