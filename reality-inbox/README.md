# Reality Inbox

**Status: DRAFT / EXPERIMENTAL v1. Core architecture FROZEN per
[`../docs/adr/ADR-0003-reality-inbox-architecture.md`](../docs/adr/ADR-0003-reality-inbox-architecture.md)
(2026-07-24) — the single-`📥 DROP HERE/`-folder design and
manifest-only state tracking may not be changed ad hoc; see that ADR
before proposing a structural change.**
Created: 2026-07-24, implementing the "Create the Reality Inbox" task, as
simplified by that task's own final instruction: one folder for humans,
everything else is the agent's job.

## The whole human workflow

1. Keep the original file in Google Drive. It stays there — Google Drive
   remains the long-term original archive.
2. When agent work is needed on a file, copy it into
   **`📥 DROP HERE/`**. That is the only folder you ever need to know
   about. You never choose between "incoming," "processing," "accepted,"
   or anything else — that decision was removed from the human workflow
   on purpose.
3. An agent (AG-002, today) validates and processes it: creates a
   manifest, checks it's readable, checks for duplicates, classifies
   sensitivity, and works out which project/agent it's for.
4. The resulting knowledge is written into the appropriate project
   memory or ledger — in this repository, that means `../memory/` (the
   operational mirror built for AG-002) and/or the Memory Source
   Registry, per what the file turns out to contain.
5. Google Drive remains the long-term original archive throughout — the
   Reality Inbox never claims to replace it, and nothing here is deleted
   from Drive as a side effect of any of this.

**The human never decides where a file goes after step 2.** Routing,
validation, provenance, archiving, and knowledge extraction are the
agent's responsibility, not the human's.

## What the other folders are (not for humans to choose between)

- **`manifests/`** — one record per file ever dropped, created by the
  agent/steward at intake time, updated as processing completes. See
  `PROCESSING-PROTOCOL.md` for the exact schema.
- **`processed/`** — where the agent moves a file's original, unmodified
  copy once handling is complete, regardless of outcome (accepted,
  rejected, or blocked — the manifest records which). Not a folder a
  human chooses to put something in.
- **`fixtures/`** — synthetic test files only, for verifying this
  pipeline itself. Never real evidence.
- **`INDEX.md`** — current inventory, agent-maintained, for anyone who
  wants to see what's here without reading every manifest.

## Architecture

```
Google Drive                    memory/ (this repository's operational
(human archive,      ─────►     mirror — see ../memory/) +
long-term storage)              Memory Source Registry
      │                          ▲
      │  human copies a file            │ agent writes validated,
      ▼                                  │ provenance-preserving
📥 DROP HERE/    ──────────────────────►  output here after
(Reality Inbox —                          processing
 operational intake,
 Git-tracked)
```

- **Google Drive = human archive and long-term storage.** Unchanged by
  this task.
- **Reality Inbox (this folder) = operational intake for agent work.**
  Not a second archive, not authoritative, not a place knowledge is
  claimed to be verified just because it passed through here.
- **`../memory/` and the Memory Source Registry = validated outputs
  after processing.** The Reality Inbox feeds them; it does not replace
  them, and `../memory/`'s own `inbox/` (from the prior task) is
  superseded by this folder as the actual human-facing drop point — see
  `../memory/inbox/README.md`.

## What this is not

- Not a second source of truth. A file having a manifest, or having been
  processed, is not the same as its extracted content being verified
  true — see `PROCESSING-PROTOCOL.md`, "No claim of verified truth."
- Not a place for bulk uploads. One file, one manifest, one deliberate
  human action.
- Not yet cross-repository. This lives in `discovery-lab`; `project-memory`
  and other repositories are not wired to it yet, despite being named as
  intended future consumers — recorded honestly as unbuilt, not silently
  assumed.

## Relationship to AG-002

AG-002's default operational source is now this folder (see
`../docs/ai-organization/employees/AG-002-discovery-archaeologist/
INPUTS.md`, updated by this task). AG-002 reads only manifested files —
never unrelated repository content — and stops with `BLOCKED` when a
file's provenance or manifest integrity is insufficient. Full protocol:
`PROCESSING-PROTOCOL.md`.
