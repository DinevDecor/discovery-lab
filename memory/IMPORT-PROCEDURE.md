# Manual Import Procedure — Repository Operational Memory

Status: DRAFT / EXPERIMENTAL v1 (manual only — no automatic Google Drive
synchronization, by explicit instruction)
Date: 2026-07-24
Implements: `../docs/adr/ADR-0002-ag002-alternative-memory-access.md`
(ACCEPTED)

## Who does what

This procedure is performed by a **human, or the Implementer session
acting as steward** — not by AG-002 or any other Role. This matches
AG-002's own `INPUTS.md` ("AG-002 may only begin a run once it has
received an explicit list of authorized historical sources") — a Role
consumes an already-authorized, already-filed source; it does not
discover, fetch, or file its own sources. "The agent" in step 3 below
means the steward performing this procedure, not AG-002 itself.

## Steps

### 1. Export

A human exports or copies the selected file from its source system (e.g.
Google Drive) by whatever means already works for them — a download, a
copy-paste, an explicit "export" action. This step happens entirely
outside this repository and outside any MCP tool call; it does not depend
on the blocked Drive connector at all.

### 2. Place in inbox

The exported file is placed, unmodified, into `memory/inbox/`. At this
point it carries no provenance metadata yet — it is a raw drop, not yet a
mirrored source.

### 3. Validate and file

The steward:

1. Confirms the file is genuinely present and readable in `inbox/`.
2. Computes `content_hash` (sha256) directly — this is always
   `AGENT-VERIFIED`.
3. Records `mirrored_at` as today's date — always `AGENT-VERIFIED`.
4. Asks the human (or uses what the human already supplied at export
   time) for `source_system`, `source_path`, `source_file_id`, and
   `source_modified_at`. Any field the human cannot supply is recorded as
   `UNKNOWN`, never guessed. Fields taken on the human's word are marked
   `HUMAN-ATTESTED`, per `PROVENANCE-SYNC-SPEC.md`.
5. Determines the correct destination folder (`journal/`, `decisions/`,
   or a future category) based on the file's actual content — not
   assumed from its filename.
6. Prepends the full provenance metadata block (YAML front matter) to the
   file and moves it from `inbox/` into the destination folder. `inbox/`
   is left empty again once filing is complete — it is a transit point,
   not storage.

### 4. Record in the manifest

The steward appends one new entry to `memory/source-manifest.md`,
matching the schema `source-manifest.md` itself defines — never editing a
prior entry in place (see `PROVENANCE-SYNC-SPEC.md`, "No silent
overwrites").

### 5. Registry check

If this is the first import establishing that `MEM-003` (or a future
mirror source) is genuinely reachable and readable, the steward updates
that Registry entry's verification fields in
`../docs/ai-organization/MEMORY-SOURCES/MEMORY-SOURCE-REGISTRY.md` — this
is Registry Stage 4 Verification, a mechanical check, not a judgment call,
per the existing Connection Protocol.

## What this procedure does not cover

- **No automatic Google Drive synchronization.** Every import starts with
  a human performing step 1 by hand. Building an automated connector to
  this repository's `memory/` folder is explicitly out of scope for v1.
- **No bulk import.** This procedure describes importing one file at a
  time, deliberately — importing many files at once as a batch is not
  covered here and is not what this v1 is for (see
  `PROVENANCE-SYNC-SPEC.md`, "No claim of completeness").
- **No re-validation on a schedule.** Nothing here re-checks a filed
  file's provenance later; if that is ever needed, it is a distinct,
  undesigned future capability, not silently assumed to exist.
