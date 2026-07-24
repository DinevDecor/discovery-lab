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
- Proposed a smallest-possible first experiment ("Ecosystem Health Review
  v0.1", not yet run) to test the recommended mandate before committing
  further.
- Updated `STATE.md` to reflect `MANDATE_DRAFTING` phase. No ADR was
  created or accepted; no architecture was invented.

## 2026-07-24 (independent architecture passes)

- Ran three completely independent, isolated, read-only architecture
  reviews — one each over KOD, generative-discovery-engine, and
  trust-engine — each answering a fixed 8-question diagnostic with no
  visibility into the other two passes or into prior discovery-lab work.
  Recorded verbatim, plus a fourth cross-repository synthesis pass run
  only afterward, in
  `docs/investigations/INV-0002-independent-architecture-passes.md`.
- The trust-engine pass found a previously undocumented gap: roughly
  60+ architecture/spec documents but only 15 implemented Python
  modules, with entire subsystems (Mechanism Trust Layer, Meta Trust
  Layer) fully specified but never built.
- Rewrote `docs/proposals/PROP-0001-discovery-lab-boundaries.md` (revision
  2) with three variants that are genuinely distinct in entry criteria,
  exit criteria, deletion mechanics, and governance burden — not
  cosmetic renamings of the same design — each specifying its
  relationship to KOD, generative-discovery-engine, trust-engine, and
  project-memory individually.
- Recommendation unchanged in substance (Ecosystem Observatory, still
  not accepted) but now backed by the trust-engine gap as a live example
  of the role's value, with explicit reasons Variants A and C were not
  selected and a list of assumptions still requiring validation.
- Added a full information-flow map (Reality → Observation → Candidate
  investigation → Experiment → Evidence → Review/falsification →
  Decision → Graduation/rejection/deletion → Destination repository)
  with per-transfer source/destination/artifact/approval-gate/provenance
  specifications, and marked the Experiment stage explicitly dormant
  under the recommended variant.
- Defined "Ecosystem Health Review v0.1" as the proposed first
  experiment — fixed scope, frozen review criteria, a defined output
  schema and PASS/PARTIAL/FAIL/INSUFFICIENT rubric, a stop rule, and
  named conditions under which its result would invalidate the
  recommended mandate. Not implemented; no agent created; no recurring
  monitoring scheduled.
- Ran a self-critique pass (hidden duplication, vague ownership,
  irreversible scope growth, circular information flows, missing
  deletion rules, unsupported recommendations) and fixed two findings:
  added a terminology disambiguation note against KOD's "Investigation"
  concept, and added an `archive/` consolidation path to Variant B's
  deletion rules to bound long-term accumulation. Still no ADR created
  or accepted; still no architecture invented or implemented.
