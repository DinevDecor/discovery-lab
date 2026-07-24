# ADR-0003 — Reality Inbox Architecture

Status: **ACCEPTED — FROZEN**
Date: 2026-07-24
Accepted: 2026-07-24, by Petko, via a direct freeze order ("Create
ADR-0002 — Reality Inbox Architecture... Freeze the current Reality
Inbox design"). **Numbering note:** the requesting task named this
"ADR-0002," but that ID is already taken by
`ADR-0002-ag002-alternative-memory-access.md` (ACCEPTED — IMPLEMENTED,
2026-07-24, the Human-Mediated Export Bridge for `memory/`). Per this
index's own rule ("Numbered sequentially, never renumbered or reused,
even if an ADR is later superseded" — `../adr/README.md`), this document
is registered as **ADR-0003** instead. Flagged here rather than silently
renumbering the existing ADR-0002 or silently complying with a
conflicting number.
Author: Implementer session (Claude Code)
Depends on / builds on: `ADR-0002-ag002-alternative-memory-access.md`
(ACCEPTED — the sibling decision this one follows, for `memory/` rather
than `reality-inbox/`), `../ai-organization/MEMORY-SOURCES/
INFRA-SPRINT-01-report.md` §11 (the implementation and verification
record this ADR freezes), `../../reality-inbox/README.md` and
`../../reality-inbox/PROCESSING-PROTOCOL.md` (the design being frozen)

## How to read this document

This ADR does not introduce a new design — `reality-inbox/` was already
built and verified (§11, `REALITY-VERIFY-0001`) in the immediately
preceding task. What this ADR does is **freeze** that design as the
organization's ratified architecture and establish that changing it is
no longer an ad-hoc edit — it requires a new ADR. No file under
`reality-inbox/` is modified by this document except the two small
"frozen" status markers described in §4, which make the freeze
discoverable at the point someone might otherwise edit the structure
without realizing a governance step is required first.

---

## 1. Context

`reality-inbox/` was built and verified PASS in the task immediately
preceding this one (`../ai-organization/MEMORY-SOURCES/
INFRA-SPRINT-01-report.md` §11): a single, organization-wide,
human-facing intake folder, with all processing state tracked
internally through manifests rather than through a taxonomy of folders
the human has to navigate. That design itself was arrived at by
simplification — the requesting task's own first draft specified a
7-folder structure (`incoming/processing/accepted/rejected/manifests/
fixtures/INDEX.md`) and replaced it, in the same message, with the
single-folder version actually built.

Without a freeze, nothing stops a future task from re-introducing
folder-based routing, adding a second human-facing folder "for
convenience," or otherwise eroding the single-decision-point design one
small change at a time — the exact failure mode ADRs exist to prevent.

## 2. Decision

**Freeze the current Reality Inbox design as documented in
`reality-inbox/README.md` and `reality-inbox/PROCESSING-PROTOCOL.md`.**
Specifically, these two architectural properties are now fixed
architecture, not implementation detail:

1. **The human-facing interface is exactly one folder:**
   `reality-inbox/📥 DROP HERE/`. A human never chooses between
   destinations. Any design that asks a human to pick a folder, tag, or
   category at drop time is a violation of this ADR, not a valid
   evolution of it.
2. **Processing state is tracked only through manifests**
   (`reality-inbox/manifests/`), never through which folder a file
   physically sits in. `processed/` holds every handled file
   regardless of outcome (`ACCEPTED`, `REJECTED`, `BLOCKED`,
   `ARCHIVED`) — the manifest's `status` field is the single source of
   truth for where a file stands, not its filesystem location.

## 3. Governance rule

**Future changes to the properties in §2 require a new ADR, not an
ad-hoc modification.** This is scoped narrowly, so the rule is
enforceable rather than aspirational:

### Requires a new ADR

- Adding a second human-facing folder, or any human-facing choice at
  drop time.
- Moving processing-state tracking out of manifests (e.g. re-encoding
  status via folder structure).
- Changing the manifest schema's required fields in
  `PROCESSING-PROTOCOL.md`.
- Changing who is authorized to perform the mechanical processing steps
  (currently: human or steward, never AG-002 itself, per
  `INPUTS.md`/`LIMITATIONS.md`).
- Removing or weakening any of the File handling rules in
  `PROCESSING-PROTOCOL.md` (no overwrites, no silent renames, no
  auto-deletion, duplicates never treated as new evidence).

### Does not require a new ADR (normal operation, unaffected by this freeze)

- Processing real files through the existing procedure — dropping,
  manifesting, filing. This ADR freezes the *architecture*, not the act
  of using it.
- Adding manifest entries, `INDEX.md` rows, or `processed/` files as
  real intake happens.
- Writing an actual large-file size policy, since
  `PROCESSING-PROTOCOL.md` already names that as an open gap to be
  filled, not a frozen absence — filling a documented gap is not the
  same as changing a frozen property.
- Extending Reality Inbox use to another repository (`project-memory`
  or others), as long as it uses the same single-folder,
  manifest-tracked design — that is adoption, not architectural change.

## 4. Making the freeze discoverable

Two files get a one-line status marker pointing back here, so the freeze
is visible at the point someone would otherwise edit the structure:

- `reality-inbox/README.md`
- `reality-inbox/PROCESSING-PROTOCOL.md`

No other content in either file changes.

## 5. What this ADR does not do

- Does not change anything about how `reality-inbox/` actually works —
  the design is frozen as-is, not modified.
- Does not freeze `memory/` (`ADR-0002`'s territory) or the Memory
  Source Registry's schema (`ADR-0001-migration-plan.md`'s territory) —
  scoped to `reality-inbox/` only.
- Does not define a process for *proposing* a change (e.g. who reviews
  a future ADR that touches this design) beyond what `docs/adr/README.md`
  already establishes for any ADR.

## Definition of Done

**ACCEPTED — FROZEN.** The two architectural properties in §2 are fixed;
§3 states exactly what does and does not require a new ADR to change,
so this freeze is enforceable rather than symbolic.
