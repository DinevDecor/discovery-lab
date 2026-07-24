# ADR-0004 — Local-Filesystem Reality Inbox Intake (Google Drive Sync)

Status: **ACCEPTED — DESIGN COMPLETE, AWAITING LOCAL VERIFICATION**
(one remote verification attempt on 2026-07-24 correctly returned
`BLOCKED` at the first precondition — see §6; still awaiting a real
local attempt)
Date: 2026-07-24
Accepted: 2026-07-24, by Petko, via a direct redesign order ("We
optimized for the repository instead of the user... Redesign the Reality
Inbox so that its primary location is a normal folder on my Google
Drive"), refined in the same exchange into an exact target path
(`G:\My Drive\Projects\discovery-lab\DROP HERE`) and an explicit
fallback instruction if this session cannot reach it.
Author: Implementer session (Claude Code)
Amends: `ADR-0003-reality-inbox-architecture.md` (ACCEPTED — FROZEN).
That ADR froze `reality-inbox/📥 DROP HERE/` (a folder *inside the git
repository*) as "the human-facing interface." This ADR does not violate
that freeze silently — it is the "new ADR" ADR-0003 §3 itself requires
before changing that property, triggered correctly rather than
worked around.
Depends on: `../ai-organization/MEMORY-SOURCES/INFRA-SPRINT-01-report.md`
§9 (a *different*, already-closed Google Drive limitation — disambiguated
in §1 below, not conflated with it), `reality-inbox/PROCESSING-PROTOCOL.md`
(kept, unchanged in substance)

## How to read this document

This ADR was drafted and accepted in the same exchange, matching
`ADR-0001` and `ADR-0003`'s pattern. Unlike those two, its central design
**cannot be verified from the session that wrote it** — this remote
session has no access to the user's local machine or Google-Drive-synced
folder, confirmed with evidence in §2. The design is therefore recorded
as accepted and ready to execute, not as implemented-and-tested. §5 states
exactly what remains to be verified, by whom, and where.

---

## 1. Problem, precisely — and why it is not the same problem as §9

The prior work in this repository (`INFRA-SPRINT-01-report.md` §9,
`ADR-0002`, `ADR-0003`) solved a *different* Google Drive problem: the
Google Drive **MCP connector** (an API-based tool AG-002 or a steward
could call) turned out to have a non-resumable, retroactive per-call
approval gate, closed as a platform limitation. The fixes built since
then (`memory/`, `reality-inbox/`) both worked around that by making the
human perform an **upload into the Git repository** (drop a file, commit,
push, or upload via GitHub's web UI) — a real fix for the MCP problem,
but one that (per this task's own framing) optimized for the repository's
convenience, not the user's: it required GitHub interaction for every
single file.

This ADR addresses that second, distinct complaint. It is not a Drive
API/OAuth/approval problem at all — it does not touch the MCP connector,
does not retry it, and does not depend on it being fixed. It is a
question of **which filesystem the human-facing folder lives on**:
inside the Git repository (requiring a Git-aware action to add a file),
or on the user's own computer, inside a folder Google Drive for Desktop
already keeps synced to Drive for them — requiring nothing more than an
ordinary file copy.

## 2. Diagnostic: can this session reach `G:\My Drive\...`?

Checked directly, not assumed, before deciding anything:

```
$ git rev-parse --show-toplevel && realpath .
/workspace/discovery-lab

$ df -h .
/dev/vda   252G  7.1G   30G  20%  /

$ mount | grep -iE 'cifs|smb|nfs|9p|drvfs'
(no output)

$ find / -maxdepth 2 -iname "*drive*"
/proc/driver          # kernel driver directory, unrelated

$ env | grep -iE 'drive|winuser|userprofile|smb'
(no output)

$ rclone listremotes   # rclone binary present at /opt/rclone but not on PATH
bash: rclone: command not found
```

**Conclusion: this session cannot reach `G:\My Drive\Projects\
discovery-lab\DROP HERE`, and the reason is structural, not a permission
or configuration gap to fix.** This session runs inside a remote,
ephemeral Linux container (`CLAUDE_CODE_REMOTE=true`) — a completely
different computer from the one running Google Drive for Desktop and
presenting `G:\`. There is no network filesystem mount, no drive-letter
concept on Linux, no rclone remote configured, and no other bridge of any
kind between this container and the user's machine. This is **not** the
Drive MCP connector's `-32003` approval problem (§1) — even if that
connector worked perfectly, it speaks the Drive API (file IDs), not local
Windows paths, so it would never have resolved `G:\...` either; the two
limitations are independent and this ADR does not conflate them.

**One clarification worth recording:** if the Drive MCP connector's
approval gate were ever resolved, files inside a Drive-synced folder
*are* also reachable via the Drive API by folder/file name — the local
path and the API path are two views of the same underlying Drive content.
That path remains closed per §9 regardless; it is not what this ADR
relies on.

## 3. Decision

**The primary human-facing intake folder becomes a local filesystem
path, not a Git-tracked repository folder — for any session that can
actually reach it:**

```
G:\My Drive\Projects\discovery-lab\DROP HERE
```

This is the **only** folder the human uses for ordinary intake, per the
explicit instruction. The repository-side machinery is **unchanged**:
`reality-inbox/manifests/`, `reality-inbox/processed/`,
`reality-inbox/fixtures/`, `reality-inbox/INDEX.md`, and
`reality-inbox/PROCESSING-PROTOCOL.md`'s 12-step procedure, provenance
schema, and file-handling rules all continue to apply exactly as
`ADR-0003` froze them — only *where step 1 begins* changes.

### 3.1 Two operating modes (both real, neither hidden from the other)

| | Can reach `G:\My Drive\...`? | Primary intake folder |
|---|---|---|
| **Local** — Claude Desktop, or Claude Code run directly on the user's machine | Yes | `G:\My Drive\Projects\discovery-lab\DROP HERE` |
| **Remote** — this session, or any Claude Code Remote / web session | No (§2) | `reality-inbox/📥 DROP HERE/` (unchanged from `ADR-0003`, kept as the documented fallback, not deleted) |

`ADR-0003`'s freeze is **amended, not violated**: "the human-facing
interface is exactly one folder" now means exactly one folder *per
reachable filesystem* — never a choice the human makes, only a fact
about which session is running. `ADR-0003` itself remains on record,
unedited, with a pointer to this amendment.

### 3.2 The local workflow, as specified

1. The human copies a file into
   `G:\My Drive\Projects\discovery-lab\DROP HERE`.
2. The human tells the (locally-running) agent to process it.
3. The agent — running with real access to both the local filesystem and
   the Git repository, which only a local session has — performs
   `PROCESSING-PROTOCOL.md`'s existing 12 steps unchanged: detect type,
   hash, duplicate-check, manifest, verify readable, classify
   sensitivity, identify project/agent, **copy** (not move) into
   `reality-inbox/processed/`, process, extract, record, set final
   status. The `git add` / `git commit` / `git push` of the manifest and
   processed copy are the agent's job, performed as part of processing —
   not a separate action the human takes.
4. **The original remains preserved**: it is *copied* from the Drive
   folder into `reality-inbox/processed/`, never moved — the file stays
   in `G:\My Drive\Projects\discovery-lab\DROP HERE` (and therefore in
   Drive) exactly as the human left it, satisfying "the original remains
   preserved" without relying on Drive itself being touched by any
   automation.
5. **No manual GitHub step is required from the human** at any point —
   upload, commit, and push are all performed by the agent as part of
   step 3, on the human's instruction, not as a separate task handed back
   to them.

### 3.3 One new manifest field

`PROCESSING-PROTOCOL.md`'s manifest schema gains one small, additive
field to record which mode an intake came through — necessary to keep
provenance honest across two now-possible origins, not a redesign of the
schema:

```yaml
intake_mode: local-drive-sync | repo-tracked-fallback
```

## 4. What stays exactly as `ADR-0003` froze it

- The manifest schema's existing required and supplementary fields.
- The 12-step processing protocol's substance (only step 1's starting
  point changes, per mode).
- The file-handling rules: no secrets committed unnecessarily, no
  uncontrolled large binaries, no overwrites, no silent renames, no
  auto-deletion, duplicates never treated as new evidence.
- `reality-inbox/📥 DROP HERE/` itself — kept, not deleted, as the
  documented remote-session fallback.
- AG-002's `INPUTS.md`/`LIMITATIONS.md`/`RUN-PROTOCOL.md`/`CHECKLIST.md`
  integration from the prior task — AG-002 still reads from
  `reality-inbox/` (via manifested, `ACCEPTED`-status entries in
  `processed/`), regardless of which mode filed them there.

## 5. What remains unverified, and by whom

This session cannot create `G:\My Drive\Projects\discovery-lab\DROP
HERE`, cannot place a file in it, and cannot run the local workflow —
all of §3.2 requires a session running on the user's own machine (Claude
Desktop, or `claude` CLI run locally) with that folder actually present
and syncing. **No fabricated verification is recorded here.** What this
ADR delivers from a remote session is the design, the repository-side
documentation, and the manifest schema extension — ready for the first
real local run to exercise, the same way `reality-inbox/` itself was
ready for `REALITY-VERIFY-0001` before that run actually happened.

## 6. Verification attempt log (2026-07-24, this session, result: BLOCKED)

Requested: run the full local-verification cycle from this session.
Attempted in good faith rather than declined outright, with exact
evidence recorded either way — same discipline as every prior Google
Drive attempt in this repository.

**Re-confirmed this is still the identical remote container** from §2,
fresh, not assumed carried over:
```
hostname                                → vm
CLAUDE_CODE_REMOTE                      = true
CLAUDE_CODE_CONTAINER_ID                = container_01T4iigk7CVPKUrCE3TAbvc2--claude_code_remote--9e8649
CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE     = cloud_default
ls /mnt/                                → only "skills" (unrelated, read-only tooling mount)
mount | grep cifs\|smb\|nfs\|9p\|drvfs\|fuse   → nothing
env | grep -i drive\|winuser\|userprofile\|smb → nothing
```

**One important negative result, recorded explicitly so it is never
mistaken for progress:** attempting `mkdir -p "/mnt/g/My Drive/Projects/
discovery-lab/DROP HERE"` **succeeded** (exit code 0) and the directory
appeared to exist afterward. This is **not evidence of Google Drive
access.** Linux will create any arbitrary directory path on a writable
filesystem regardless of what it's named — `mkdir` has no concept of
"Google Drive" and cannot fail in a way that reveals whether a path is
meaningfully connected to anything. The directory it created was an
ordinary, empty, disconnected folder on this container's own ephemeral
local disk (`/dev/vda`), coincidentally sharing a name with the real
target — never networked to Google's servers or the user's computer, and
containing no real diary file, because none could reach it. **Deleted
immediately** (`rm -rf /mnt/g`) once this was established, so no
misleading artifact was left in the filesystem for a future reader to
mistake for a working bridge.

**Consequence for steps 3 onward of the requested cycle:** "confirm read
and write," "place or detect one real diary file," "copy the original,"
and every step after them are moot — there is no real folder to read
from, no real diary file reachable, and copying the fabricated
look-alike directory's (empty) contents would not be copying anything
real. None of those steps were performed on fabricated data; they were
correctly not attempted once the precondition failed.

**Status not changed to `VERIFIED`** — per the requester's own
instruction ("only if the full cycle succeeds") and per this
repository's standing discipline against claiming synchronization or
access that has not happened.

## Definition of Done

**ACCEPTED — design complete, documented, and repository-side pieces in
place; end-to-end verification requires a session with local filesystem
access and has not happened yet.** One real verification attempt was
made from this (remote) session on 2026-07-24 and correctly returned
**BLOCKED** at the first precondition (§6) — not a failure of the
design, a confirmation that this session is not the right one to run it.
Not claimed as `IMPLEMENTED` or `VERIFIED` — that status is earned only
by a real local run, per §5.
