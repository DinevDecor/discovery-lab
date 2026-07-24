# AI Organization — Employee Registry

**Status: DRAFT.** This registry lists every organizational Role ever
created under AI Organization, at any status, including retired ones.
Entries are never deleted — only updated in place, per the append-only
convention already used elsewhere in `discovery-lab`
(`docs/investigations/`, `CHANGELOG.md`).

| Employee ID | Role Name | Status | Version | Location | Executor | Created | Origin Reference |
|---|---|---|---|---|---|---|---|
| AG-001 | Repository Observer | Prototype (not adopted) | v0.1 | `docs/ai-organization/employees/AG-001-repository-observer/` | unassigned | 2026-07-24 | `employees/AG-001-repository-observer/ROLE.md` §Origin |
| AG-002 | Discovery Archaeologist | Prototype (not adopted) — **FROZEN 1.0** | 1.0 | `docs/ai-organization/employees/AG-002-discovery-archaeologist/` | unassigned | 2026-07-24 | `employees/AG-002-discovery-archaeologist/ROLE.md` §Origin |
| AG-003 | Knowledge Curator | Prototype (not adopted) — **FROZEN 1.0** | 1.0 | `docs/ai-organization/employees/AG-003-knowledge-curator/` | unassigned | 2026-07-24 | `employees/AG-003-knowledge-curator/ROLE.md` §Origin |

## Reading this table

- **Status** reflects the current stage in `HIRING-LIFECYCLE-DRAFT.md`'s
  candidate lifecycle (`Candidate → Prototype → Probation → Trusted →
  Retired`). A status here is a summary; the authoritative, detailed
  state for each Role is its own `STATUS.yaml`.
- **"FROZEN" is a second, independent axis, not a lifecycle stage** —
  added 2026-07-24 per `GOVERNANCE.md` and `../releases/1.0/
  RELEASE-1.0.md`. It describes architectural stability (this Role's
  governing documents passed an internal review, an adversarial review,
  and a real Reality Stress Test, and are not expected to change without
  new evidence) — it is deliberately **not** the same claim as
  `Trusted` on the adoption axis. A Role can be `FROZEN` and still
  `Prototype (not adopted)` at the same time, as AG-002 and AG-003 both
  are here; freezing the architecture is not an adoption decision.
- **Executor** records who or what currently performs the Role, or
  `unassigned` if no one currently does. Per the core organizational
  principle, changing the Executor does not require a new row or a new
  Employee ID.
- **Origin Reference** points to where that Role's origin story — why it
  was proposed, by whom, and from what discussion — is recorded in full.

## Current total

3 Roles recorded. 0 Trusted. 0 Retired. 2 Frozen (AG-002, AG-003 — see
`../releases/1.0/RELEASE-1.0.md`).
