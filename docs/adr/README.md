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
| [ADR-0002](ADR-0002-ag002-alternative-memory-access.md) | Alternative Memory Access for AG-002 (Human-Mediated Export Bridge) | **DRAFT** | 2026-07-24 | — | Proposes AG-002 read a human-exported Git mirror of the Google Drive diary instead of the connector directly, after `INFRA-SPRINT-01-report.md` §9 closed direct Drive access as a platform limitation (non-resumable per-call approval). Google Drive stays canonical; not implemented, flags a self-critical tension with the Registry's "no duplicated memory" principle for Petko to resolve |

## Status values

- **DRAFT** — proposed, not yet reviewed by a human decision-maker.
- **ACCEPTED** — architectural content approved and in force. Does not by
  itself imply migration/implementation is complete — check the ADR's own
  Acceptance record and any linked migration plan.
- **SUPERSEDED** — replaced by a later ADR, which must be named. Never
  deleted, only marked.
- **REJECTED** — considered and explicitly declined. Never deleted.

## Reading this table

- **Current total: 2 ADRs. 1 accepted. 0 superseded. 0 rejected. 1 draft
  awaiting decision.**
- An ADR's Status here must always match the `Status:` line inside the ADR
  file itself — this table is a summary, not a second source of truth. If
  they ever disagree, the ADR file is authoritative and this table is
  stale and should be corrected.
