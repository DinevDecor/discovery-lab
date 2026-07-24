# Repository Operational Memory

**Status: DRAFT / EXPERIMENTAL v1 (manual import only).**
Created: 2026-07-24, in response to `../docs/ai-organization/MEMORY-SOURCES/
INFRA-SPRINT-01-report.md` §9 closing direct Google Drive access as a
platform limitation, and `../docs/adr/ADR-0002-ag002-alternative-memory-access.md`
(ACCEPTED), which this structure implements.

## What this is

This is **not** a copy of Google Drive. It is a small, purpose-scoped,
agent-readable mirror — holding only the specific files an AI employee
(currently AG-002) needs for active work, imported one at a time, by a
human, on demand. See `PROVENANCE-SYNC-SPEC.md` for exactly what "mirror"
does and does not mean here, and why this is not a second source of truth.

## What this is not

- Not a bulk export of Google Drive.
- Not a live sync — nothing here updates itself.
- Not authoritative. If this mirror and Google Drive ever disagree, Google
  Drive wins — see `PROVENANCE-SYNC-SPEC.md`, "No second source of truth."
- Not a replacement for Google Drive's role as the canonical,
  human-maintained archive — see `../docs/ai-organization/MEMORY-SOURCES/
  INFRA-SPRINT-01-report.md` §10 for that decision, recorded explicitly.

## Structure

```
memory/
├── inbox/          — where a human places a freshly exported file,
│                      before it has been validated or filed
├── journal/         — filed, validated mirror copies of diary/journal-type
│                      source content
├── decisions/        — filed, validated mirror copies of decision-record-
│                      type source content (empty until a real one exists —
│                      not seeded ahead of evidence)
├── observations/      — findings AG-002 (or another Role) extracts while
│                      reading a filed source; not itself mirrored content
├── source-manifest.md — append-only log of every import: provenance,
│                      hash, verification status
├── PROVENANCE-SYNC-SPEC.md — the metadata schema and synchronization
│                      rules every mirrored file must follow
├── IMPORT-PROCEDURE.md — the step-by-step manual import process
└── README.md          — this file
```

Each subfolder carries its own short `README.md` explaining what belongs
in it — none are seeded with placeholder or invented content.

## Relationship to the Memory Source Registry

This structure is registered as `MEM-003` in
`../docs/ai-organization/MEMORY-SOURCES/MEMORY-SOURCE-REGISTRY.md`, using
the same `git_repository` locator shape already proven for `MEM-001`. A
Role does not read this folder directly by convention alone — it looks it
up in the Registry first, per the existing Connection Protocol
(`MEMORY-SOURCE-PROTOCOL.md`), exactly as for any other source.

## Relationship to AG-002

AG-002's own `RUN-PROTOCOL.md`, `INPUTS.md`, `OUTPUTS.md`, `LIMITATIONS.md`,
and `CHECKLIST.md` are **unmodified** by this structure. AG-002 reads a
filed, provenance-tagged file under `journal/` or `decisions/` exactly as
it already reads `project-memory/archive/` (`MEM-001`) — no new capability
was added to the Role. The mechanical work of importing and filing a file
(§`IMPORT-PROCEDURE.md`) is performed by a human or the Implementer
session acting as steward, consistent with AG-002's own `INPUTS.md`
("AG-002 may only begin a run once it has received an explicit list of
authorized historical sources") — AG-002 does not discover, fetch, or file
its own sources.
