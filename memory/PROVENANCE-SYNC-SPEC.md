# Provenance & Synchronization Specification — Repository Operational Memory

Status: DRAFT / EXPERIMENTAL v1
Date: 2026-07-24
Implements: `../docs/adr/ADR-0002-ag002-alternative-memory-access.md`
(ACCEPTED)

## Synchronization rule

- **Google Drive = human-maintained archive.** It remains the canonical
  source of truth for anything mirrored here. Nothing in this repository
  changes that.
- **`memory/` = agent-readable operational mirror.** A working copy of
  *only* the files currently needed for active agent work — never a goal
  in itself to make complete.
- **Every mirrored file must retain source provenance** — the metadata
  block defined below, with no field silently omitted. A file with
  incomplete provenance is not considered validated (see
  `IMPORT-PROCEDURE.md`).
- **No silent overwrites.** Re-importing a file that already exists under
  its filed path is not a normal update — it must go through the same
  import procedure as a new file, produce a new `source-manifest.md`
  entry (not an edit of the old one), and note explicitly what changed.
  Git history is the record of every version; nothing here force-replaces
  a prior import in place.
- **No claim of completeness.** This mirror never asserts "we have
  everything from Drive" or "this is a full copy of X." Each
  `source-manifest.md` entry, and `README.md`'s own framing, are explicit
  that this is a partial, purpose-scoped set — coverage is stated as "N
  files imported for reason Y," never as "synchronized" or "complete."
- **Unresolved divergence is reported, not guessed.** If it is ever
  unclear whether a mirrored file still matches its Drive source (e.g. no
  way to re-check `source_modified_at` against the live file), that
  uncertainty is recorded as `verification_status: UNKNOWN` or
  `DIVERGENCE UNCONFIRMED` in the manifest — never silently assumed
  current.
- **The mirror is not a second source of truth.** If Google Drive and this
  mirror ever visibly disagree (a human notices the live Drive file has
  changed since import), Google Drive is authoritative. The mirror's copy
  is marked stale, not treated as an equally valid alternate version.

## Provenance metadata — minimum required fields

Every mirrored file carries this block (as YAML front matter at the top
of the file) **and** a matching row in `source-manifest.md`:

```yaml
source_system:       # e.g. google_drive, SYNTHETIC_TEST_FIXTURE
source_path:          # human-readable path/name at the source, as given
                       #   by whoever performed the export
source_file_id:        # the source's own stable identifier, if one exists;
                       #   UNKNOWN if the export method didn't preserve one
source_modified_at:     # last-modified time at the source, if known;
                       #   UNKNOWN if not provided by the export
mirrored_at:            # date this copy was filed into memory/ (agent- or
                       #   steward-observed, always known)
mirror_method:          # e.g. "manual export + human placement in inbox/"
content_hash:           # sha256 of the file content as filed (steward- or
                       #   agent-computed, always known)
verification_status:     # HUMAN-ATTESTED | AGENT-VERIFIED | UNKNOWN —
                       #   see "Verification status values" below
```

### Verification status values

- **`AGENT-VERIFIED`** — the field was independently computed or checked
  by the agent/steward doing the import (e.g. `content_hash`,
  `mirrored_at`).
- **`HUMAN-ATTESTED`** — the field was supplied by the human performing
  the export and taken on their word, because the agent has no
  independent way to confirm it (e.g. `source_modified_at`,
  `source_file_id` for a source the agent cannot itself reach — this is
  the honest case for every Google-Drive-sourced import today, since
  direct Drive access remains blocked per `INFRA-SPRINT-01-report.md` §9).
- **`UNKNOWN`** — neither agent-verified nor human-attested; the field
  could not be established. Never left blank without this label.

This distinction matters precisely because direct Drive verification is
unavailable: this mirror must never imply a field was independently
checked against Drive when it was only ever asserted by a human.

## What this spec does not do

- Does not define automatic synchronization — see `IMPORT-PROCEDURE.md`;
  v1 is manual only, by explicit instruction.
- Does not grant this mirror any authority Google Drive doesn't also have
  — see "The mirror is not a second source of truth," above.
- Does not apply retroactively to anything outside `memory/` — `MEM-001`
  (`project-memory/archive/`) is a different kind of source (a live Git
  fetch, not a manual mirror) and is unaffected.
