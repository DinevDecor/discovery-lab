# Reality Inbox — Processing Protocol

Status: DRAFT / EXPERIMENTAL v1
Date: 2026-07-24

## Who does this

The mechanical steps below (detect, hash, validate, file, move) are
performed by a **human or the Implementer session acting as steward** —
not by AG-002 itself. This matches the same Role-boundary precedent
already established for `../memory/IMPORT-PROCEDURE.md`: AG-002's
`INPUTS.md` requires an explicit, already-authorized source; it does not
discover, fetch, hash, or file its own sources. AG-002's actual work
begins once a file has a valid manifest with `status: ACCEPTED` — see
step 9 onward.

## Manifest schema

One manifest file per intake, stored in `manifests/`, named
`<intake_id>.md` (or `.yaml`) with this content:

```yaml
intake_id:              # sequential, RI-NNNN, never reused
original_filename:        # exactly as dropped, never altered
source_system:             # e.g. google_drive, SYNTHETIC_TEST_FIXTURE
source_path:                 # human-supplied, as given at drop time
source_file_id:                # source's own stable ID if known; UNKNOWN if not
uploaded_by:                     # who dropped the file
uploaded_at:                      # date/time dropped into 📥 DROP HERE/
content_type:                      # detected file type
content_hash:                       # sha256, agent-computed
sensitivity:                         # see "Sensitivity classification" below
intended_project:                     # which project this is for, if known; UNKNOWN if not
intended_agent:                        # which agent should process it, if known
status:                                  # one of the Allowed statuses, below
verification_status:                      # HUMAN-ATTESTED | AGENT-VERIFIED | UNKNOWN,
                                          #   per field, matching ../memory/PROVENANCE-SYNC-SPEC.md
notes:
# Supplementary fields, required to satisfy the Provenance rule (below)
# and step 11 (record all produced outputs) — not in the task's minimum
# list, added because those requirements can't be met without them:
processing_agent:                          # who/what processed the file (e.g. AG-002)
processed_at:                               # date processing completed
outputs:                                     # list of files/records produced
  # e.g. - ../../memory/observations/....md
  #      - ../../docs/.../MEMORY-SOURCE-REGISTRY.md (MEM-NNN entry)
```

### Allowed statuses

`INCOMING` · `VALIDATING` · `PROCESSING` · `ACCEPTED` · `REJECTED` ·
`BLOCKED` · `ARCHIVED`

### Sensitivity classification

A free-text judgment made at intake (step 6, below) — e.g.
`non-sensitive`, `contains-personal-data`, `unknown-pending-review`. Not
a closed enum in v1; recorded honestly, including as `UNKNOWN` when the
steward cannot tell from the file alone.

## Processing protocol — the 12 steps

For each file:

1. **Detect file type.**
2. **Calculate a content hash** (sha256).
3. **Check for duplicates** — compare against every existing manifest's
   `content_hash`. A duplicate is never treated as new evidence (see
   "File handling rules," below) — it is recorded as `REJECTED`, with a
   note pointing at the original `intake_id`.
4. **Create the manifest**, `status: INCOMING → VALIDATING`.
5. **Verify the file is readable** (opens, parses as its detected type).
6. **Classify sensitivity.**
7. **Identify the intended project and agent** — from context, or
   `UNKNOWN` if it cannot be determined yet.
8. **Move the original from `📥 DROP HERE/` to `processed/`**,
   `status → PROCESSING`. The file itself is never renamed on this move
   — `original_filename` in the manifest is the permanent record if it
   ever needs to be (see "File handling rules").
9. **Process it without modifying the original** — this is where AG-002
   (or another Role) actually reads the file and does its own work, per
   its own existing Recovery Protocol, unmodified by this document.
10. **Write the extracted result** to the correct Registry, Ledger,
    observation, or project document — in this repository, that is
    `../memory/observations/` and/or the Memory Source Registry, per
    what the content turns out to be.
11. **Record all produced outputs in the manifest** (`outputs:`,
    `processing_agent:`, `processed_at:`).
12. **Set final status**: `ACCEPTED`, `REJECTED`, or `BLOCKED`. The file
    stays in `processed/` regardless of which — nothing is deleted (see
    "File handling rules").

## Provenance rule

Every extracted claim must preserve a link back to:

- the `intake_id`;
- the original file (`original_filename`, `content_hash`);
- the source system (`source_system`, `source_path`, `source_file_id`);
- the location inside the source, where possible (a section, line, or
  quotation — the same discipline AG-002's own `OUTPUTS.md` already
  requires for a Recovery Report);
- the processing agent (`processing_agent`);
- the processing date (`processed_at`).

**No agent may present extracted knowledge as verified truth merely
because it passed through the Reality Inbox.** A manifest and a
processing record are evidence of *what was done*, not a judgment that
the content is correct — the same distinction AG-002's own
`LIMITATIONS.md` already draws between recovery and verification.

## File handling rules

- Do not commit secrets, credentials, API keys, or personal identifiers
  unnecessarily. If a dropped file appears to contain any, sensitivity is
  classified accordingly (step 6) and processing stops pending explicit
  human review — not processed further automatically.
- Do not place large audio, video, archives, or binary datasets directly
  in Git without an explicit size policy. **No size policy exists yet**
  in this v1 — until one is approved, a large binary file is recorded as
  `BLOCKED` with a manifest-only entry (an external reference, if one is
  known) rather than committed.
- For large files: store only a manifest and external reference until a
  storage policy is approved — same rule, stated explicitly.
- Do not overwrite incoming files. A file already at a given `processed/`
  path is never silently replaced — a re-drop of the same content is
  caught by step 3 (duplicate check) before it gets that far.
- Do not silently rename files without preserving the original name in
  the manifest — `original_filename` is permanent even if a file is
  later given a different name on disk for any reason.
- Do not delete rejected files automatically. `REJECTED` files remain in
  `processed/`, exactly like `ACCEPTED` ones — status lives in the
  manifest, not in whether the file still exists.
- Do not treat duplicate files as new evidence — see step 3.

## Relationship to `../memory/`

This protocol is the front door; `../memory/IMPORT-PROCEDURE.md` (from
the prior task) is now the *downstream* filing step for content that
belongs in the long-lived operational mirror (`../memory/journal/`,
`../memory/decisions/`). Not every Reality Inbox intake needs to go that
far — some produce only an observation (`../memory/observations/`)
without the source file itself being separately filed into `memory/`.
`../memory/inbox/` itself is superseded by `📥 DROP HERE/` as the actual
human-facing drop point — see `../memory/inbox/README.md`.
