# ADR-0002 — Alternative Memory Access for AG-002 (Human-Mediated Export Bridge)

Status: **ACCEPTED — IMPLEMENTED**
Date: 2026-07-24
Accepted: 2026-07-24, by Petko, via a direct implementation order ("Task —
Resolve AG-002 Memory Access Blocker") rather than a separate approve/amend
round on this draft. Concrete design decisions this order made, resolving
§5's open questions: location = `discovery-lab/memory/` (open question 1);
cadence = manual, on-demand import for v1, no background sync (open
question 2); the §4 tension is resolved by instruction, not by silent
default — "do not duplicate the entire Google Drive. Store only the files
required for active agent work": **bounded, purpose-scoped mirroring is
authorized; wholesale duplication remains prohibited.** See
`../ai-organization/MEMORY-SOURCES/INFRA-SPRINT-01-report.md` §10 for the
implementation record.
Author: Implementer session (Claude Code)
Depends on / builds on: `ADR-0001-human-authority-gates.md` (ACCEPTED —
the HAG concept this proposal applies), `../ai-organization/MEMORY-SOURCES/
INFRA-SPRINT-01-report.md` §9 (the closed platform-limitation finding this
proposal responds to)

## How to read this document

This ADR was **drafted and accepted in the same work sequence**: Petko's
next message after the draft was a direct order to implement it, not a
separate accept/reject decision — so acceptance and implementation are
recorded together here rather than as two dated events. What follows below
this point (§1–§6) is the **original draft text, unedited**, preserved as
the record of what was proposed; the Acceptance block above and
`INFRA-SPRINT-01-report.md` §10 record what was actually built, which
refines but does not contradict this draft (e.g. the exact `memory/`
folder names came from the implementation order, not from §3 below, which
only said "a Git-tracked location").

---

## 1. Problem

`INFRA-SPRINT-01-report.md` §9 closed with a platform limitation, tested
as thoroughly as this environment allows: Google Drive's connector is
authenticated and connected, but its per-call approval flow is
non-resumable and retroactive — even a human actively granting approval in
real time could not get one call through. Unattended Google Drive access
is **not supported in this client**, not because of anything wrong in
`discovery-lab`, AG-002, or the Memory Source Registry.

AG-002 still needs a reliable source to run against. Waiting indefinitely
for the platform layer to change is not a plan.

## 2. Decision (proposed)

Introduce a **Human-Mediated Export Bridge**: Google Drive remains the
canonical, human-maintained store of the diary archive, but AG-002 does
not read it directly. Instead, a human periodically (or on demand)
exports the specific content AG-002 needs into a Git-tracked location,
which AG-002 reads exactly the way it already, successfully, reads
`MEM-001` (`project-memory/archive/`, verified reachable in `PILOT-RUN-0001`).

This does not require AG-002 to gain any new capability. It requires
exactly one new capability of the *organization*: a repeatable, low-effort
human export step.

### 2.1 Why this is the minimal option

Two other approaches were considered and are recorded here as
**not recommended as the minimal fix**, not silently discarded:

- **A service-account or API-key-based Drive access path**, bypassing the
  interactive connector entirely. This could, in principle, avoid the
  per-call approval gate altogether — but it requires provisioning new
  credentials and infrastructure outside this repository's or this
  session's control, has not been verified as possible in this
  environment at all, and is a materially bigger lift than exporting a
  file. Worth revisiting *if* the export-bridge workflow proves too
  manual a burden long-term, but not the minimal choice today.
- **Waiting for a platform fix.** `INFRA-SPRINT-01-report.md` §1.4 already
  established the approval gate lives entirely outside this repository's
  control; there is no work discovery-lab can do to hasten a platform
  change, and no evidence one is coming.

### 2.2 How this maps onto Human Authority Gates (ADR-0001)

This proposal does not eliminate the Human Authority Gate the diary
represents — a human must still authorize AG-002's access to it. It
relocates *where* that HAG is crossed: instead of once per tool call
(currently impossible to satisfy, per §9), it is crossed once per export
— a single, deliberate, human-initiated action, which is exactly the kind
of "normal state transition" ADR-0001 §2 describes, just moved to a point
in the workflow this client can actually support.

## 3. What the bridge looks like, concretely

1. **A human** (Petko, or a future Curator) exports the current diary
   content from Google Drive — by any means that already works for them
   (Drive's own UI, a download, whatever they already use) — and commits
   it into a Git-tracked location. Which repository/path is an open
   question for Petko to decide (§5), not resolved here.
2. **A new Registry entry, `MEM-003`** (not created by this document),
   `type: git_repository`, using the exact same schema shape `MEM-001`
   already uses. `access_requirements: read-only Git fetch access` — the
   same access AG-002 has already exercised successfully, zero new
   capability required.
3. **AG-002 reads `MEM-003`** through its existing, unmodified
   `RUN-PROTOCOL.md` and `INPUTS.md` — the same Stage 1–7 procedure
   already used for `MEM-001` in `PILOT-RUN-0001`. No change to AG-002
   itself.
4. **A `last_exported` convention**, parallel to the Registry's existing
   `last_verified` field, records the vintage of each export, so any
   Recovery Report produced from `MEM-003` can honestly state what
   snapshot it analyzed — consistent with AG-002's own
   `OUTPUTS.md` Run Metadata fields.

## 4. Self-critical note — tension with an existing principle

`MEMORY-SOURCE-PROTOCOL.md`'s Governance section and
`INFRA-SPRINT-01-report.md` §2.3 both state **"no duplicated memory"** as
an architectural principle. A Git mirror of Drive content is, plainly, a
duplicate. This proposal does not pretend otherwise, and does not resolve
this tension unilaterally — it is flagged here, in the same
"record, don't silently fix" discipline used throughout this repository,
for Petko to weigh explicitly:

- **Argument for an exception:** the diary is described, throughout
  AG-002's own design, as immutable historical evidence — a closed record,
  not a live operational system. `PILOT-RUN-0001`'s and `PILOT-RUN-0002`'s
  framing both treat it as something to be read as of a point in time, not
  synced continuously. A periodic snapshot may be a materially different
  case from the live, queryable sources "no duplicated memory" was written
  to prevent proliferating.
- **Argument against:** "no duplicated memory" doesn't currently carve out
  that exception anywhere in writing, and creating one by precedent
  (rather than by an explicit governance decision) is exactly the kind of
  silent scope-creep this repository's discipline exists to prevent.

This proposal recommends Petko decide explicitly whether archival,
point-in-time snapshots of closed historical sources are an intended
exception to "no duplicated memory," rather than this ADR quietly
establishing one.

## 5. Open questions this proposal leaves for Petko

1. **Where does the export live?** A new folder in `project-memory`
   (alongside the existing `archive/`), a new folder in `discovery-lab`,
   or a separate repository — not decided here.
2. **Who performs the export, and how often?** A one-time export (matching
   AG-002's "immutable historical evidence" framing) may be sufficient; a
   recurring cadence is also possible if the Drive source keeps growing.
   Not decided here.
3. **Does §4's tension get resolved by exception, by declining this
   proposal, or by some third design not yet considered?**

## 6. What this document did not do, as originally drafted

*(preserved verbatim from the draft; superseded by the Acceptance block
above and by `INFRA-SPRINT-01-report.md` §10, which record what was
actually implemented)*

- Does not create `MEM-003`.
- Does not perform any export.
- Does not modify AG-002, `MEMORY-SOURCE-PROTOCOL.md`,
  `MEMORY-SOURCE-REGISTRY.md`, or any governance document.
- Does not mark `MEM-002` deprecated — Google Drive remains the intended
  canonical source if a working, unattended access path is ever found;
  this proposal is a bridge, not a replacement of intent. (This point
  still holds after implementation: `MEM-002` is reclassified, not
  deprecated — see `INFRA-SPRINT-01-report.md` §10.)

## Definition of Done

**ACCEPTED AND IMPLEMENTED.** Superseded from "done when it accurately
describes a design" (the draft's original criterion) to "done when the
design is built and verified" — see `INFRA-SPRINT-01-report.md` §10 for
the full implementation and verification record, including the completion
verdict.
