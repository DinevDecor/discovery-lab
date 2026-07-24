# Infrastructure Sprint 01 — Permanent Access to Project Memory (Google Drive)

**Status: CLOSED — PLATFORM LIMITATION (Google Drive connector path).
Definition of Done: NOT PASS, and not achievable via this path in this
client.** Alternative architecture proposed, not implemented — see
`../../adr/ADR-0002-ag002-alternative-memory-access.md`.
Date: 2026-07-24. Triggered by: AG-002 `PILOT-RUN-0002`, blocked at Stage 1
(`../employees/AG-002-discovery-archaeologist/HISTORY.md`, `../../../CHANGELOG.md`,
both dated 2026-07-24). Closed after a live approval test — see §9.

This is an infrastructure problem, not an AG-002 problem, per the task that
requested this sprint. Nothing in `AG-002` or in Discovery Lab's governance
documents (`FOUNDING-CHARTER.md`, `PROP-0001`–`PROP-0003`, `ORB/`) is
modified by this sprint. The only additive change outside this file is one
new row in `MEMORY-SOURCE-REGISTRY.md` (`MEM-002`), which that registry's
own Governance table already permits.

---

## 1. Infrastructure Report

### 1.1 What currently works

- The Google Drive connector is installed and authenticated at the
  organization level. Verbatim, from `ListConnectors`:
  ```
  {"name":"Google Drive","directoryUuid":"b89f7865-a755-4f86-8062-c3bd651740ce",
   "installedServerId":"6c0f8fb6-a9fa-4d9a-a3ba-6f2c09324710",
   "installState":"connected","connected":true,"enabledInChat":true}
  ```
  `connected: true` and `enabledInChat: true` mean OAuth is complete and the
  connector's tools are loaded into this session.
- The MCP transport to the connector itself connects successfully. Verbatim,
  from `mcp-logs-Google-Drive/2026-07-24T08-22-20-924Z.jsonl`:
  ```
  "Successfully connected (transport: http) in 323ms"
  "Connection established with capabilities: {"hasTools":true,"hasPrompts":true,...}"
  ```
- Every non-Google-Drive tool used in this session (Bash, Read, Write, Edit,
  Git, the GitHub MCP server) has worked throughout this sprint and every
  prior task with no approval friction.

### 1.2 What is blocked

Every call to every Google Drive MCP tool made in this session fails, with
no exceptions found:

| Attempt | Tool | Result |
|---|---|---|
| 1 | `search_files` (`title contains 'oneDay 6'`) | `MCP error -32003` |
| 2 | `search_files` (`title contains 'Project Memory'`) | `MCP error -32003` |
| 3 | `list_recent_files` | `MCP error -32003` |
| 4 (this sprint) | `list_recent_files` (re-check) | `MCP error -32003` |

Two distinct tools, four distinct calls, both across `PILOT-RUN-0002` and
this sprint's own re-check — same error every time, each failing in `0s`
(i.e. rejected before any Drive API round trip, not a timeout).

### 1.3 Why it is blocked (evidence)

Verbatim from `mcp-logs-6c0f8fb6-a9fa-4d9a-a3ba-6f2c09324710/2026-07-24T10-59-19-902Z.jsonl`:

```
"Tool 'search_files' failed after 0s: MCP error -32003: MCP tool call requires approval"
"Tool 'search_files' returned -32003 needs_approval (tool_name=mcp__Google_Drive__search_files) — surfacing retroactive approval card"
"Tool 'list_recent_files' failed after 0s: MCP error -32003: MCP tool call requires approval"
"Tool 'list_recent_files' returned -32003 needs_approval (tool_name=mcp__Google_Drive__list_recent_files) — surfacing retroactive approval card"
```

This is a **per-tool, per-session, human-interactive consent gate**, applied
specifically to org-level "Directory"-origin connectors (the request headers
for this connector include `X-MCP-Server-Origin: directory`, distinct from a
project's own `.mcp.json`-defined servers). It sits in front of the Drive
API itself — no Drive scope or quota was ever checked, because the call
never got past this gate.

Ruled out, with evidence:

- **Not a network/TLS/proxy problem.** `/root/.ccr/README.md` documents this
  session's HTTPS egress proxy and its failure modes (cert errors, 403/407,
  etc.); none of those apply here — the MCP transport log shows a clean
  connect in 323ms, and the failure is a JSON-RPC application error
  (`-32003`), not a transport error.
- **Not a missing OAuth authorization.** `ListConnectors` shows
  `connected: true` at the org level.
- **Not a missing connector.** The connector is installed
  (`installState: "connected"`) and its tools are loaded in this session
  (`enabledInChat: true`).
- **Not a repository (`discovery-lab` or `project-memory`) configuration
  issue.** Checked `.claude/settings.json`-equivalent files
  (`/root/.claude/launcher-settings.json`, `/home/claude/.claude/launcher-settings.json`):
  both set `"permissions": {"allow": ["Skill"]}` only. The Claude Code CLI's
  own `enabledMcpjsonServers`/`disabledMcpjsonServers` settings (found via
  inspection of the installed CLI package) govern project-defined
  `.mcp.json` servers only — they do not apply to an org Directory
  connector like this one, so there is no repository-level setting that
  could fix or break this.
- **Not a Drive API scope problem.** The block occurs before any Drive API
  call is attempted; a scope error would surface differently (and later,
  after `0s` would not be the failure time).

### 1.4 Which component is responsible

The approval gate lives in the session layer that mediates calls to
org "Directory"-origin MCP connectors — the traffic is routed through
`api.anthropic.com/v2/ccr-sessions/<session>/mcp?...&mcp_url=https://drivemcp.googleapis.com/...`,
outside both the `discovery-lab` and `project-memory` repositories. It is a
**platform-level safety control on the Claude Code / claude.ai session**,
not a Discovery Lab or Memory Source Registry defect, and not something a
commit to either repository can change.

### 1.5 The exact missing capability

**Missing MCP approval** — specifically: first-use, per-tool, human-interactive
approval of the Google Drive connector's tool calls in this session. The
approval card the platform surfaces after a blocked call has never been
approved, because this task ran unattended (no human was present in the
live conversation at the moment each card was surfaced to click it).

### 1.6 Open risk this report cannot resolve from inside the session

It is **not verified** whether a human's approval, once granted, is:

- **(a)** scoped to this one session only (meaning every future unattended
  AG-002 run, and every future Routine, would hit the same block and need a
  fresh human click), or
- **(b)** persistent for the connector across sessions (meaning one approval
  genuinely makes this permanent, as the sprint's objective requires).

This cannot be determined without a human actually granting approval once
and a second, independent session then being tested against the same
connector. This is flagged explicitly rather than assumed away — see the
Connection Plan, step 5, and the Verification Procedure.

**Superseded, 2026-07-24 (see §9):** the live approval test performed after
this report was first written found a more fundamental result than (a)/(b)
above anticipated. Petko granted approval ("Allow once") while a session
was live and watching; the *very next* call in the *same* session still
returned `-32003`, identically. The session-scoped-vs-persistent question
this section posed turned out to be moot — the approval flow does not
establish a standing grant even within the session where it was granted,
let alone across sessions. See §9 for the full evidence and conclusion.

---

## 2. Permanent Architecture

```
Google Drive (Project Memory)
        │
        │  Stage 0 — Platform Tool Approval  (NEW — see 2.1)
        │  one-time, human, per connector/session; gates every call below
        ▼
Memory Source Registry           (MEMORY-SOURCE-PROTOCOL.md, unmodified)
   Stage 1 Lookup
   Stage 2 Selection & Authorization
   Stage 3 Resolution
   Stage 4 Verification
        │
        ▼
AI Organization                  (Stage 5 — Read-only Access, unmodified)
        │
   ┌────┼─────────────┐
   ▼    ▼              ▼
AG-001  AG-002    future employees
```

No layer here is new *governance*: Stages 1–6 are exactly the Connection
Protocol already defined in `MEMORY-SOURCE-PROTOCOL.md`, unmodified by this
sprint. What this sprint adds is naming the precondition that sits in front
of Stage 1 and was, until now, implicit and undocumented.

### 2.1 Stage 0 — Platform Tool Approval (finding, not a protocol edit)

The existing Connection Protocol assumes that once a source is looked up
(Stage 1) and authorized (Stage 2), Resolution (Stage 3) is a mechanical
act. Sprint 01 shows this assumption is incomplete for connectors of
`type: google_drive`: a human must also grant one-time, platform-level tool
approval, independent of and prior to anything the Registry itself
controls. This is recorded here as a **finding**, in the same
"record, don't silently fix" discipline already used for
`../FOUNDING-CHARTER.md`'s Candidate Conflicts — formally amending
`MEMORY-SOURCE-PROTOCOL.md` to add a Stage 0 is a separate, human-gated
change this sprint does not make.

### 2.2 No hardcoded paths

`MEM-002` (added below) uses the `google_drive` locator shape already
defined in the Protocol (`drive_or_shared_drive` / `folder_path_or_id`), not
a filesystem path. Its `folder_path_or_id` is honestly `UNKNOWN` until Stage
1 Lookup can actually run (see Connection Plan, step 2) — inventing an ID
now would violate the same discipline that kept `PILOT-RUN-0001` from
inventing diary content.

### 2.3 No duplicated memory

Google Drive remains the sole store of the diary archive. Nothing is
cached, copied, or mirrored into `discovery-lab` or `project-memory` by this
sprint or by the Connection Plan below. Every future AG-002 run reads the
source live via Stage 5, exactly as `project-memory/archive/` already is
for `MEM-001`.

---

## 3. Connection Plan

| # | Owner | Prerequisite | Action | Expected result | Verification method |
|---|---|---|---|---|---|
| 1 | **Petko** (repository/session owner — human) | None | Grant approval for the Google Drive connector's pending tool-call request(s) in this session (see §5 for the exact action) | `mcp__Google_Drive__*` calls stop returning `-32003` | Re-run `list_recent_files`; a normal file listing (not an error) is PASS |
| 2 | Implementer session (steward) | Step 1 | Run `search_files` for `title contains 'oneDay 6'` / `title contains 'Project Memory'` to resolve the diary archive's real Drive file/folder ID | A concrete, stable `folder_path_or_id` | `get_file_metadata` on that ID returns real metadata |
| 3 | Implementer session (steward) | Step 2 | Update `MEM-002`'s registry entry: fill in `locator.folder_path_or_id`, `status: unverified → active`, set `last_verified` (Registry Stage 4 — "a mechanical check, not a judgment call", per existing Protocol) | Registry reflects one real, resolvable Google Drive source | `git diff` touches only that row; `last_verified` matches the check date |
| 4 | AG-002 (Executor of the run) | Step 3 | Re-run AG-002 `PILOT-RUN-0002`, citing `MEM-002` as the authorized source per `INPUTS.md` | A full `runs/PILOT-RUN-0002-recovery-report.md` conforming to `OUTPUTS.md` | File exists; every finding cited; Archaeologist Boundary Statement present; `HISTORY.md` updated |
| 5 | Petko | Step 4 passed once | Confirm, via a second, independent session (e.g. a Routine-triggered run) calling a Google Drive tool without a fresh manual click, whether the Step-1 approval persisted | Either "permanent" (open risk 1.6(b) resolved) or "session-scoped" (1.6(a) confirmed — must be repeated per session) | The second session's first Drive call either succeeds or returns `-32003` again; either outcome is reported back honestly, not assumed |

Step 5 is the honest core of "permanent": nothing in this sprint can
guarantee permanence without that empirical check, because the mechanism
that gates approval is opaque to the session experiencing the block.

**Result, 2026-07-24 (see §9): step 1 was attempted for real — twice, in
two different ways — and did not resolve.** Steps 2–5 were never reached;
they remain correct *as a plan*, but are understood, as of §9, to require
a source-access path other than this Google Drive connector as currently
gated in this client. Superseding proposal:
`../../adr/ADR-0002-ag002-alternative-memory-access.md`.

---

## 4. Verification Procedure — PASS test

**PASS** requires all five, in one continuous, unattended AG-002 run, with
no manual copying of diary content into either repository by a human at any
point:

1. AG-002 (or its steward) looks up `MEM-002` in the Registry (Stage 1) —
   not an ad hoc, freshly-typed source description.
2. The source resolves and verifies reachable (Stages 3–4): at least one
   real Drive call (e.g. `get_file_metadata`) returns real data, not
   `-32003`.
3. The diary is read in full via `read_file_content` / `download_file_content`
   (Stage 5, strictly read-only).
4. `runs/PILOT-RUN-0002-recovery-report.md` is produced, conforming to
   `OUTPUTS.md`'s exact section list, every Recovered Idea / Repeated Theme
   / Contradiction / Candidate Investigation carrying a real citation
   (diary date, quote), and the Archaeologist Boundary Statement is present
   and true.
5. `git diff` on the diary source itself (if it is ever cloned/resolved
   into a checkable form) shows zero changes — the source was read, never
   modified.

**FAIL** on any of: a `-32003`/`needs_approval` error at any point in the
chain; any citation without a real diary date/path/quote; any content not
traceable to an actual diary entry; any edit to the diary.

**Current status: NOT PASS — closed as a platform limitation, not a
pending human action.** Precondition 2 (source resolves and verifies
reachable) was tested directly, with a human present granting approval in
real time, and did not clear. This is no longer "blocked on Connection
Plan step 1 awaiting a human"; see §9.

---

## 5. Human Action Required

**Result: performed, did not resolve — see §9.** Petko approved the
surfaced card ("Allow once" — the only option that was available/used;
this section's preference for a broader "always allow" grant was not
tested because no such option was exercised). The card was approved
correctly; the very next call, in the same session, still returned
`-32003`. This section is kept as-written, unedited, as the historical
record of what was tried — not as still-outstanding guidance.

- **Which permission:** Approval of this session's pending Google Drive
  tool-call request(s) — the "approval card" the Claude Code client
  surfaces after a blocked call (log evidence: `"surfacing retroactive
  approval card"`, quoted in full in §1.3).
- **Where:** In the same Claude Code conversation/session that ran
  `PILOT-RUN-0002` and this sprint (session id
  `18a7c453-3ad9-51a7-b7f4-cb98f3846755`). Open this session in whichever
  Claude Code client (web, desktop, or mobile) shows it, and look for a
  Google Drive tool-approval prompt attached to the `search_files` /
  `list_recent_files` calls. If no card is visible directly in the
  transcript, check **claude.ai → Settings → Connectors → Google Drive**
  for a permission control on this connector (e.g. an "ask before every
  use" vs. "always allow" toggle) — this exact UI location is inferred from
  the log's own wording ("approval card"), not independently confirmed from
  inside this session, and is flagged as inference here rather than
  presented as verified fact.
- **Why:** The connector is authenticated and loaded
  (`connected: true`, `enabledInChat: true`), but each individual tool call
  still requires one-time human consent, and no human was present when the
  cards were surfaced during this unattended task.
- **What to click:** "Approve" on the surfaced Google Drive tool-call
  card(s). If the UI offers a scope choice, choose the option that covers
  *future* calls from this connector (not a single one-off approval) —
  AG-002 needs this to work unattended, across future runs and Routines,
  which is the entire point of this sprint.
- **Expected result:** The next `mcp__Google_Drive__*` call — in this
  session, and ideally in any future one — returns real Drive data instead
  of `MCP error -32003`. Please also tell the Implementer session whether
  the approval had to be granted once (persistent) or shows signs of being
  per-session, so Connection Plan step 5 can be confirmed rather than
  assumed.

---

## 6. Constraints honored

- AG-002 not redesigned; no file under `../employees/AG-002-discovery-archaeologist/`
  touched by this sprint.
- Discovery Lab's governing documents (`FOUNDING-CHARTER.md`,
  `PROP-0001`–`PROP-0003`, `ORB/`, `MEMORY-SOURCE-PROTOCOL.md`) not
  modified — the Stage 0 gap in §2.1 is recorded as a finding, not applied
  as a silent edit.
- No temporary workaround attempted: no local caching or copying of Drive
  content, no bypass of the approval gate, no substitution of another
  source for the diary.

## 7. Process rule now in effect

Recorded per the requester's explicit instruction: from this sprint
forward, a `BLOCKED` result from any Discovery Lab agent is not followed by
"retry," but by "diagnose the root cause and eliminate it" as the very next
task. This sprint is the first applied instance of that rule. The rule
itself is recorded here as a now-followed practice — formalizing it into
`../FOUNDING-CHARTER.md` or `../HIRING-LIFECYCLE-DRAFT.md` would be a
governance change, which is a separate, human-gated step this sprint does
not take.

## 8. Five Whys — Root Cause Classification

Each step below is restricted to what §1 already established with evidence
or what is directly on record elsewhere in this repository — no new claims
are introduced here.

**Symptom** — the outward, user-visible failure:
`PILOT-RUN-0002` returned `BLOCKED — Diary archive exists but is not
accessible from the current execution environment.` No Recovery Report was
produced.

1. **Why did AG-002 return `BLOCKED`?**
   Because every Google Drive MCP tool call it (or its steward) made —
   `search_files` ×2, `list_recent_files` ×2 — returned `MCP error -32003:
   MCP tool call requires approval`. Stage 1 (Historical Sources / Lookup)
   never reached the source, so nothing downstream could run.
   → **Technical cause.**

2. **Why did those calls require approval and fail?**
   Because the Google Drive connector is an org "Directory"-origin
   connector, and the platform gates every one of its tools behind a
   one-time, human-interactive "approval card" per session — independent
   of the connector's own authenticated/connected state (`connected: true`,
   `enabledInChat: true`, per §1.1). This gate sits in front of the Drive
   API itself; nothing about the query, the tool chosen, or the retry count
   changes the outcome.
   → **Technical cause** (the mechanism itself).

3. **Why was that approval never granted?**
   Because this task executed as an unattended session — a task delivered
   and run without a human live in the conversation at the moment each
   approval card was surfaced. The platform's only path to satisfy this
   gate is a human clicking "Approve" in an active client; an automated or
   scheduled run has no such path available to it.
   → **Infrastructure cause**: the gate is interactive-only, and
   Discovery Lab has no automated or pre-authorized path through it for
   unattended runs.

4. **Why does Discovery Lab's infrastructure let a mission be assigned
   against a source that was never confirmed reachable?**
   Because the Memory Source Registry's Stage 4 (Verification) is not a
   hard precondition for Stage 2 (Selection & Authorization) — nothing in
   `MEMORY-SOURCE-PROTOCOL.md` or in AG-002's own `INPUTS.md` stops a
   `status: unverified` entry (or, before this sprint, an entry that did
   not exist at all) from being named as "the sole authorized source" for
   a real mission. `MEM-002` itself was created at `status: unverified`
   and could, as written today, still be cited as an authorized source
   before anyone confirms Stage 0/Stage 4 actually pass.
   → **Infrastructure cause**: a process gap in the Registry's own
   Connection Protocol — verification is defined but not enforced before
   authorization.

5. **Why does that process gap exist — why is there no rule requiring
   verification before authorization, and no one responsible for closing
   it?**
   Because no human or Curator has ever been assigned standing ownership
   of external-connector access for Discovery Lab. This is not a new
   finding: AG-002's own `STATUS.yaml` already lists `permanent
   organizational owner` under `open_governance_questions`, unresolved
   since AG-002's creation. Verification (Registry Stage 4) and platform
   approval (the Stage 0 gate found in §2.1) both require a human to *act*
   — and with no one assigned to own that class of action, there is no
   one whose job it is to grant it before a mission is issued, only
   someone who can be asked reactively, once, after a run already failed.
   → **Governance cause — and the first cause under human organizational
   control.** Stopping here: nothing past this point is a technical or
   infrastructure fact to keep decomposing; it is a human ownership
   decision Discovery Lab has not yet made.

### Classification summary

| Layer | Finding |
|---|---|
| Symptom | AG-002 `PILOT-RUN-0002` returned `BLOCKED`, no report produced |
| Technical cause | Every Google Drive tool call returns `MCP error -32003: MCP tool call requires approval`, regardless of tool or query |
| Infrastructure cause | (a) The approval gate is interactive-only with no unattended/automated path through it; (b) the Registry's Stage 4 Verification is not enforced as a precondition for Stage 2 Selection & Authorization |
| Governance cause (root, human-controlled) | No human or Curator holds standing ownership of external-connector approval and source verification — an open question already on record in `../employees/AG-002-discovery-archaeologist/STATUS.yaml` and never assigned |

### Smallest permanent fix

Two actions, both small, both already-defined mechanisms — no new
employee, no new document set, no redesign of AG-002 or the Connection
Protocol:

1. **One human click** (§5 of this report, unchanged by this analysis):
   Petko approves the pending Google Drive tool-call request once. This
   resolves the technical and immediate infrastructure cause for this
   specific connector.
2. **One ownership assignment, closing the governance cause:** Petko (or a
   named Curator) is recorded as the standing owner of Registry Stage 4
   Verification and of granting platform-level connector approvals, and a
   single rule is adopted: **a Registry entry may not be cited as an
   authorized source in a Role's `INPUTS.md` while its `status` is
   `unverified`.** This is a one-line policy addition to existing,
   already-built infrastructure (the Registry's `status` field and
   Governance table already exist in `MEMORY-SOURCE-PROTOCOL.md`) — it
   requires no new stage, no new document, and no automation. It converts
   Stage 4 from an aspirational step into an enforced gate, which is what
   would have caught this sprint's root cause *before* a mission was
   issued rather than after it failed.

Both actions are recommended, not applied — adopting rule 2 is a
governance change to `MEMORY-SOURCE-PROTOCOL.md`'s Governance table, which
this sprint does not make unilaterally, consistent with §6.

## 9. Final Conclusion — Platform Limitation, Not a Project Failure

Recorded 2026-07-24, after a live approval test conducted with Petko
present and actively granting approval in real time — the strongest test
this sprint could run, and the one that closes the question §1.6 and §3
step 5 left open.

### 9.1 What was actually tested

Three distinct rounds, beyond the four calls already logged in §1.2:

1. **Re-check, unattended** (this sprint's continuation): `list_recent_files`
   and `search_files`, both `-32003`, connector state unchanged.
2. **Immediately after Petko clicked "Allow once"**: `list_recent_files`
   then `search_files`, both `-32003` again, with the log repeating the
   same `"...surfacing retroactive approval card"` pattern for the new
   calls — i.e. each new call generates its *own* fresh card, rather than
   consuming a standing grant.
3. **A single, minimal call issued while Petko was actively watching and
   approving**, specifically to test whether a call could be caught
   "in flight" and resumed after approval: `list_recent_files`, pageSize 1.
   Result: `"failed after 0s"` — identical to every prior attempt. The `0s`
   timing is itself evidence: the call is rejected before any Drive API
   round trip is possible, which means it never reaches a "pending" state
   an out-of-band approval could attach to. The approval card is generated
   *after* the rejection ("retroactive"), not *during* a live request.

### 9.2 Conclusion

| Field | Value |
|---|---|
| Connector status | **CONNECTED** |
| Organization authorization | **COMPLETE** |
| Per-call approval flow | **NON-RESUMABLE / RETROACTIVE** |
| Unattended Google Drive access | **NOT SUPPORTED IN THIS CLIENT** |
| `MEM-002` operational status | **BLOCKED BY PLATFORM APPROVAL MODEL** |

This is recorded as a **platform limitation** — not a project failure, and
not a missing OAuth authorization. Every layer this repository, AG-002, or
the Memory Source Registry controls is correct and working as designed:
the connector is authenticated, the transport connects, the Registry
entry exists and is honestly marked `unverified`, and AG-002's own Stop
rule was followed at every step. The unresolved layer — a per-call
approval mechanism that manufactures a fresh, retroactive card for every
new call instead of establishing any standing grant, even within one live
session with a human actively approving — sits entirely outside this
repository's or this session's control, per §1.4.

### 9.3 What this changes going forward

- **No further Google Drive retries will be attempted** against this
  connector in this client, per explicit instruction. Retrying would not
  produce new information: §9.1's round 3 establishes that *even a human
  actively watching and approving in real time* cannot make a call
  succeed, which is a stronger and more conclusive result than any further
  unattended retry could add.
- `MEM-002` remains in the Registry, `status: unverified`, with its notes
  updated to point here rather than to a still-pending action (see
  `MEMORY-SOURCE-REGISTRY.md`).
- An alternative architecture for AG-002 is proposed, not implemented, in
  `../../adr/ADR-0002-ag002-alternative-memory-access.md` — keeping Google
  Drive as the human-maintained canonical source while giving AG-002 a
  source type it can already access reliably.

## Definition of Done

**NOT PASS — closed as a platform limitation, per §9.** The infrastructure
was diagnosed with evidence, the permanent architecture is specified, and
the Connection Plan was tested for real, including a live approval
attempt — and did not clear. This sprint does not end in "waiting on a
human action"; it ends in a conclusion this repository cannot engineer
its way past. `ADR-0002-ag002-alternative-memory-access.md` is the
proposed next step, not yet authorized to implement.
