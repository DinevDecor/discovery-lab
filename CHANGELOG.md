# Changelog

## 2026-07-24

- Verified remote access to `DinevDecor/discovery-lab` (previously untested;
  distinct from the earlier KOD/trust-engine/SketchUp-DDF access check).
- Confirmed the remote repository contained only an auto-generated
  `README.md` ("# discovery-lab") and a single "Initial commit" — no other
  branches, pull requests, issues, or tags.
- Searched the local workspace (the `project-memory` repository in full,
  `/home/user`, `/workspace`, `/root`, and recently modified files) for a
  previously exported "architectural draft" for discovery-lab. None was
  found.
- Established baseline repository structure (`README.md`, `CONTEXT.md`,
  `STATE.md`, `CHANGELOG.md`, `docs/notes/`) documenting confirmed facts
  only, without inventing architecture.
- Added a provenance/recovery note
  (`docs/notes/2026-07-24-recovery-investigation.md`) recording the search
  performed and its outcome.
- Opened draft PR #1 (`claude/recover-discovery-lab` → `main`) with this
  work. A companion investigation note recording the same findings from
  the `project-memory` side is at
  `project-memory/notes/2026-07-24-discovery-lab-recovery.md`.

## 2026-07-24 (mandate drafting)

- Inspected KOD (`Core/`, `Foundations/`, `Knowledge/`, `Core/Registry/`)
  and generative-discovery-engine (`README`, `CONTEXT`, `STATE`, `adr/`,
  `contracts/`, `registry/`, `docs/protocols/RVS-00-validation-kernel.md`)
  to identify what each already owns, to avoid duplicating either.
- Recorded the inspection and diagnosis (overlaps, gaps, ownership risks,
  dumping-ground risk) in
  `docs/investigations/INV-0001-discovery-lab-mandate.md`.
- Proposed three mandate variants — Experiment Laboratory, Ecosystem
  Observatory, Combined Lab + Observatory — with allowed/prohibited
  artifacts, lifecycle, relationships, advantages, and failure modes for
  each, in `docs/proposals/PROP-0001-discovery-lab-boundaries.md`.
- Recommended (not accepted) the Ecosystem Observatory variant, on the
  grounds that it is the only variant with directly observed precedent
  (this session's own recovery investigation and the 2026-07-19 Dinev
  Decor evidence check, both previously done ad hoc in
  `project-memory/notes/`).
- Proposed a smallest-possible first experiment (INV-0002, not yet run) to
  test the recommended mandate before committing further.
- Updated `STATE.md` to reflect `MANDATE_DRAFTING` phase. No ADR was
  created or accepted; no architecture was invented.
