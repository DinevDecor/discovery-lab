# ADR Index

Architecture Decision Records for `discovery-lab`. Distinct from the
`docs/proposals/PROP-000N` series: a `PROP` argues for a policy or
process; an ADR names and decides an architectural concept. Numbered
sequentially, never renumbered or reused, even if an ADR is later
superseded — matching the append-only convention already used by
`../ai-organization/EMPLOYEE-REGISTRY.md`,
`../ai-organization/ORB/ORB-REGISTRY.md`, and
`../ai-organization/MEMORY-SOURCES/MEMORY-SOURCE-REGISTRY.md`.

## Index

| ID | Title | Status | Date | Accepted | Summary |
|---|---|---|---|---|---|
| [ADR-0001](ADR-0001-human-authority-gates.md) | Human Authority Gates (HAG) | **ACCEPTED** | 2026-07-24 | 2026-07-24 | Defines a Human Authority Gate — any action requiring explicit human authorization before the organization may continue — as a normal state transition, never an error. Architecture accepted; migration deferred, see [ADR-0001-migration-plan.md](ADR-0001-migration-plan.md) |
| [ADR-0002](ADR-0002-ag002-alternative-memory-access.md) | Alternative Memory Access for AG-002 (Human-Mediated Export Bridge) | **ACCEPTED — IMPLEMENTED** | 2026-07-24 | 2026-07-24 | AG-002 reads a human-exported, provenance-tagged Git mirror (`memory/`, `MEM-003`) instead of the Google Drive connector directly, after `INFRA-SPRINT-01-report.md` §9 closed direct Drive access as a platform limitation. Google Drive stays canonical. Accepted and implemented in the same task sequence as the draft — see the ADR's own Acceptance record |
| [ADR-0003](ADR-0003-reality-inbox-architecture.md) | Reality Inbox Architecture | **ACCEPTED — FROZEN, amended by ADR-0004** | 2026-07-24 | 2026-07-24 | Freezes `reality-inbox/`'s design (built and verified in the preceding task): exactly one human-facing folder, processing state tracked only through manifests, never folder location. States precisely which future changes require a new ADR versus which are normal operation. Originally requested as "ADR-0002" by the requester; registered as ADR-0003 since ADR-0002 was already taken — flagged explicitly, not silently renumbered |
| [ADR-0004](ADR-0004-local-drive-synced-reality-inbox.md) | Local-Filesystem Reality Inbox Intake (Google Drive Sync) | **ACCEPTED — DESIGN COMPLETE, AWAITING LOCAL VERIFICATION** | 2026-07-24 | 2026-07-24 | Amends `ADR-0003`: for sessions with local filesystem access (Claude Desktop, local Claude Code), the one human-facing folder becomes `G:\My Drive\Projects\discovery-lab\DROP HERE` — no Git/GitHub step required from the human. `reality-inbox/📥 DROP HERE/` remains the fallback for remote sessions, confirmed (with evidence) unable to reach the local Drive path. Repository-side manifests, provenance, and processing protocol unchanged. Not yet exercised — no remote session can test it |

## Status values

- **DRAFT** — proposed, not yet reviewed by a human decision-maker.
- **ACCEPTED** — architectural content approved and in force. Does not by
  itself imply migration/implementation is complete — check the ADR's own
  Acceptance record and any linked migration plan.
- **ACCEPTED — FROZEN** — architectural content approved and explicitly
  locked against ad-hoc change; further modification requires a new ADR,
  per the freezing ADR's own governance rule.
- **ACCEPTED — DESIGN COMPLETE, AWAITING LOCAL/EXTERNAL VERIFICATION** —
  architectural content approved and repository-side work done, but the
  design depends on an environment (or capability) this repository's own
  sessions cannot exercise to confirm end to end.
- **SUPERSEDED** — replaced by a later ADR, which must be named. Never
  deleted, only marked.
- **REJECTED** — considered and explicitly declined. Never deleted.

## Reading this table

- **Current total: 4 ADRs. 4 accepted (1 with migration deferred, 1
  implemented, 1 frozen-then-amended, 1 awaiting local verification). 0
  superseded. 0 rejected. 0 draft.**
- **Correction, 2026-07-24:** this table previously showed `ADR-0002` as
  `DRAFT`, which had gone stale — the ADR file itself was updated to
  `ACCEPTED — IMPLEMENTED` in an earlier task but this index was not
  updated to match at the time. Caught and fixed while adding `ADR-0003`,
  per this section's own rule that the ADR file is authoritative.
- An ADR's Status here must always match the `Status:` line inside the ADR
  file itself — this table is a summary, not a second source of truth. If
  they ever disagree, the ADR file is authoritative and this table is
  stale and should be corrected.
