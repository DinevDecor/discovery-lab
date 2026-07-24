# Reality Inbox

**Status: DRAFT / EXPERIMENTAL v1. Core architecture FROZEN per
[`../docs/adr/ADR-0003-reality-inbox-architecture.md`](../docs/adr/ADR-0003-reality-inbox-architecture.md)
(2026-07-24), amended per
[`../docs/adr/ADR-0004-local-drive-synced-reality-inbox.md`](../docs/adr/ADR-0004-local-drive-synced-reality-inbox.md)
(2026-07-24) — the single-folder design and manifest-only state tracking
may not be changed ad hoc; see those ADRs before proposing a structural
change.**
Created: 2026-07-24, implementing the "Create the Reality Inbox" task, as
simplified by that task's own final instruction: one folder for humans,
everything else is the agent's job.

## The whole human workflow — depends on which folder you can reach

**If you're using Claude Desktop or a local Claude Code session** (the
normal case for ordinary intake, per `ADR-0004`):

1. Keep the original file in Google Drive — it stays there, synced by
   Google Drive for Desktop.
2. Copy it into **`G:\My Drive\Projects\discovery-lab\DROP HERE`**. That
   is the only folder you ever need to know about — an ordinary folder
   on your own computer, not a Git upload.
3. Tell the agent to process it.
4. The agent imports it into this repository (manifest, provenance,
   processing, Git commit) on your behalf — no GitHub step is left for
   you to do.
5. Your original file stays exactly where you put it, untouched — the
   agent copies it into the repository, it never moves or deletes your
   copy.

**If you're using a remote/web Claude Code session** (like the one that
built this structure) — confirmed by `ADR-0004` §2 to have no access to
your local machine or Google Drive at all — the fallback is the
git-tracked folder instead:

1. Keep the original file in Google Drive.
2. Copy it into **`reality-inbox/📥 DROP HERE/`** inside this repository
   (via a local git clone, or GitHub's web upload).
3. Tell the agent to process it.
4. Same processing as above from that point on.

Either way: **the human never decides where a file goes past step 2.**
Routing, validation, provenance, archiving, and knowledge extraction are
the agent's responsibility, not the human's, and which of the two
folders above is "the" folder for you is a fact about which session
you're running, never a choice you make per file.

## What the other folders are (not for humans to choose between)

- **`manifests/`** — one record per file ever dropped, created by the
  agent/steward at intake time, updated as processing completes,
  including a new `intake_mode` field (`local-drive-sync` or
  `repo-tracked-fallback`) recording which of the two folders above the
  file actually came through. See `PROCESSING-PROTOCOL.md` for the exact
  schema.
- **`processed/`** — where the agent files a working copy once handling
  is complete, regardless of outcome (accepted, rejected, or blocked —
  the manifest records which). From `📥 DROP HERE/` (repo-tracked
  fallback), this is a **move** — that copy only ever existed in Git.
  From `G:\My Drive\...\DROP HERE` (local mode), this is a **copy** —
  the original stays on the user's Drive-synced disk, untouched
  (`ADR-0004` §3.2). Not a folder a human chooses to put something in
  either way.
- **`fixtures/`** — synthetic test files only, for verifying this
  pipeline itself. Never real evidence.
- **`INDEX.md`** — current inventory, agent-maintained, for anyone who
  wants to see what's here without reading every manifest.

## Architecture

```
                              memory/ (this repository's operational
                 ─────►       mirror — see ../memory/) +
                              Memory Source Registry
                                     ▲
                                     │ agent writes validated,
                                     │ provenance-preserving
                                     │ output here after processing
                                     │
      ┌──────────────────────────────┴──────────────────────────────┐
      │                                                               │
G:\My Drive\...\DROP HERE          reality-inbox/📥 DROP HERE/
(local mode — Claude Desktop /     (remote-session fallback —
 local Claude Code; original       Git-tracked; ADR-0004 confirmed
 file stays here, never moved)     this is unreachable from a remote
      │                            session)
      │ human copies a file into whichever one their session can reach
      ▼
  Google Drive
  (human archive, long-term storage — unchanged either way)
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
- **Not yet verified in local mode.** The `G:\My Drive\...\DROP HERE`
  workflow (`ADR-0004`) is designed and documented but has never actually
  run — no remote session can create or test it (`ADR-0004` §2). The
  repo-tracked fallback (`📥 DROP HERE/`) remains the only mode actually
  exercised end to end, via `REALITY-VERIFY-0001`.
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
