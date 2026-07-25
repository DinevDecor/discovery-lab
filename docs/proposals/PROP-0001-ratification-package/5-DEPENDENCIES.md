# Deliverable 5 — Dependencies

What `PROP-0001`'s ratification depends on, and what depends on it.
Both directions checked directly against real files, not inferred.

## What `PROP-0001` itself depends on

- `docs/investigations/INV-0001-discovery-lab-mandate.md` — the
  baseline diagnosis. `PROP-0001`'s own header: "Depends on... read
  those first; this document proposes solutions only."
- `docs/investigations/INV-0002-independent-architecture-passes.md` —
  the three independent architecture passes (KOD, GDE, trust-engine)
  the current revision's variants were rebuilt from. Both are
  investigation documents, not governance instruments — nothing about
  ratifying `PROP-0001` requires re-accepting them, since they are
  diagnosis, not proposal.

## What currently depends on `PROP-0001` remaining unresolved, or on its resolution

- **`docs/ai-organization/FOUNDING-CHARTER.md`** (`DRAFT`) — its own
  header states it "does not create a new governance layer — every
  principle below either restates something already established in
  `ORGANIZATION-DRAFT.md`, `HIRING-LIFECYCLE-DRAFT.md`, or
  `PROP-0001-discovery-lab-boundaries.md`." Its own standing is
  explicitly downstream of `PROP-0001`'s.
- **`docs/ai-organization/ORGANIZATION-DRAFT.md`** and
  **`HIRING-LIFECYCLE-DRAFT.md`** (both `DRAFT`) — the organizational
  scaffolding `AG-002`/`AG-003` operate inside; neither claims
  independence from `PROP-0001`'s mandate question.
- **`docs/ai-organization/EMPLOYEE-REGISTRY.md`** — `AG-002` and
  `AG-003` are recorded as `Prototype (not adopted)` on the
  organizational-trust axis; that axis is governed by
  `HIRING-LIFECYCLE-DRAFT.md`, itself downstream of `PROP-0001`.
- **`docs/ai-organization/GOVERNANCE.md`** (`ACCEPTED`, but governing
  only the *architecture-stability* axis) — `ARCH-002`'s `G5` and this
  package's Deliverable 1 both note that `discovery-lab`'s
  `GOVERNANCE.md`-ratified Formal Gate and Human Final Authority
  instances, though independently `ACCEPTED` in their own right, still
  operate *inside* a repository whose mandate to exist and operate at
  all remains `DRAFT`.
- **`project-memory/PROJECT_REGISTRY.md`** — `PROP-0001`'s own
  "Unresolved questions" explicitly defers adding `discovery-lab` as a
  registry row until the mandate is no longer `DRAFT`. This is the one
  concrete, external, already-identified action a ratification
  decision directly unblocks or continues to block.
- **The Recommendation Ledger interface** (`PROP-0001`'s own
  §"Recommendation quality") — explicitly "not populated until at
  least one recommendation exists to track," which itself requires
  `Ecosystem Health Review v0.1` to run, which requires a ratified
  mandate to authorize running it at all.
- **`Ecosystem Health Review v0.1`** (`PROP-0001`'s own first
  experiment) — fully specified, zero files created, cannot begin
  under Discovery Lab's own Principle 0 without an accepted mandate
  authorizing it.
- **`G2`'s Unified Control Plane Specification** (`DRAFT — Candidate
  for Adoption`) — not blocked by `PROP-0001` for its own adoption
  decision, but its reconciliation work assumed `discovery-lab`'s
  `GOVERNANCE.md`-based mechanisms as one of three ratified inputs;
  `G2`'s own closing note already flags this as a live, carried-forward
  dependency, not newly discovered here.

## What is explicitly NOT a dependency

- `ARCH-001`, `ARCH-002`, `ARCH-003`, `EXEC-001`, and `G2` are all
  independent architectural review, analysis, specification, and
  execution work — none of them required `PROP-0001` to be ratified to
  be valid as evidence or as completed tasks in their own right, and
  none of them is retroactively invalidated by either a ratification or
  a rejection of `PROP-0001`. What changes is only the *organizational
  standing* of the repository the work was performed inside, not the
  factual content of the work itself.
- `AG-001`'s existing `Prototype` status and single `ORB` review are
  unaffected either way — `GOVERNANCE.md` itself states plainly it "is
  not applied backward to invalidate a Role that predates it."
