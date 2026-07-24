# Source Manifest — Repository Operational Memory

**Status: DRAFT / EXPERIMENTAL v1.** Append-only log of every file ever
imported into `memory/`, matching the same convention already used by
`../docs/ai-organization/EMPLOYEE-REGISTRY.md`,
`../docs/ai-organization/ORB/ORB-REGISTRY.md`, and
`../docs/ai-organization/MEMORY-SOURCES/MEMORY-SOURCE-REGISTRY.md`.
Entries are never edited or deleted once written — a re-import or update
gets a new entry, not a rewrite of the old one (see
`PROVENANCE-SYNC-SPEC.md`, "No silent overwrites").

## Entry schema

Each entry carries the full provenance block from `PROVENANCE-SYNC-SPEC.md`
plus the filed destination path:

```
entry_id:              # sequential, MIRROR-NNN, never reused
filed_path:              # where the file now lives, e.g. memory/journal/...
source_system:
source_path:
source_file_id:
source_modified_at:
mirrored_at:
mirror_method:
content_hash:
verification_status:
imported_by:             # who performed the import (human name, or
                        #   "Implementer session (Claude Code)" as steward)
notes:
```

## Entries

### MIRROR-001

```
entry_id: MIRROR-001
filed_path: memory/journal/SYNTHETIC-TEST-journal-0001.md
source_system: SYNTHETIC_TEST_FIXTURE
source_path: N/A — authored directly, not exported from any real system
source_file_id: N/A
source_modified_at: N/A
mirrored_at: 2026-07-24
mirror_method: synthetic fixture authored directly by the Implementer
  session for pipeline verification; not an export from Google Drive or
  any other real source
content_hash: sha256:aa75e30c1edc6e4df6cbb793dcc0ad2f91ba7b2be84f2c9a3d89b6b1c0ee8407
verification_status: AGENT-VERIFIED
imported_by: Implementer session (Claude Code), acting as steward
notes: >
  Deliberately labeled synthetic test fixture, not a real import - see
  the in-file warning banner and
  ../docs/ai-organization/MEMORY-SOURCES/INFRA-SPRINT-01-report.md
  section 10. Used to verify the memory/ pipeline (inbox -> validate ->
  file -> manifest) and AG-002's read path against MEM-003 end to end,
  in the absence of any real, accessible Google Drive content. Hash
  computed on the raw file exactly as placed in inbox/, before the
  provenance block was prepended in journal/.
```

## Reading this table

- **Current total: 1 file imported. 0 real imports, 1 synthetic test
  fixture.**
- This manifest's first entry is a labeled synthetic fixture, not a real
  Google Drive import, because direct Drive access remains blocked (see
  `../docs/ai-organization/MEMORY-SOURCES/INFRA-SPRINT-01-report.md` §9).
  It exists to prove the pipeline mechanism works, not to claim any real
  content has been mirrored yet.
