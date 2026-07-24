# Memory Source Registry — Protocol

**Status: DRAFT / Experimental Process.** Version v0.1. Date: 2026-07-24.

## What this is

**Not a new employee.** It has no Employee ID, no entry in
`../EMPLOYEE-REGISTRY.md`, no `CONTRACT.md`, no assigned Executor —
matching the same framing already used for `../ORB/`. It is
**infrastructure**: a registry of external memory sources (a Google
Drive, a Git repository, a future source type) that a Role like AG-002
may be authorized to read from, plus the protocol for going from a
registry entry to actually-readable content in a given session, without
ever hardcoding a path into the registry, a Role's own files, or this
protocol itself.

**AG-002 is unchanged by this document.** No file under
`../employees/AG-002-discovery-archaeologist/` is modified here. This
is deliberate: AG-002's `INPUTS.md` already requires "an explicit list
of authorized historical sources" for every run, and that requirement
is not touched. What this document adds is a place that list can now be
*drawn from* — a future run may cite Registry entries when specifying
authorized sources, instead of the source list being invented ad hoc
each time. Actually wiring AG-002 (or any Role) to consult this
registry by default is a separate, future migration step, not performed
here — see "What this document does not do," below.

## The problem this solves

`PILOT-RUN-0001` (`../employees/AG-002-discovery-archaeologist/runs/
PILOT-RUN-0001-recovery-report.md`) used one real source,
`project-memory/archive/`, named directly in the task that requested
the run. That works once. It does not scale: every future run would
otherwise require re-discovering, re-describing, and re-typing out
source locations from scratch, with no shared record of what sources
exist, what type they are, or whether they were ever actually verified
reachable. A registry replaces "ask a human to redescribe the world
every time" with "look up what is already known to exist."

## Why paths are never hardcoded here

A local filesystem path (for example, `/home/user/project-memory/
archive/`) is a fact about *one session's* environment — where
something happens to be mounted, right now, in this container. It is
not a fact about the source itself, and it will not be true in a
different session, a different environment, or six months from now.
Storing a literal filesystem path in the registry would silently break
the moment the environment changes, and nobody would notice until a
run failed against a path that used to work.

The registry instead stores a **stable locator**: a description of
*where the source actually lives* in terms that do not depend on any
one session's mount layout — a Git repository name and a path relative
to its root; a Drive folder's own identifier; whatever the equivalent
stable reference is for a future source type. Turning a stable locator
into an actual, readable local path is a separate act — **Resolution**
(Stage 3 below) — performed fresh, per session, and never written back
into the registry.

## Registry schema

Each entry in `MEMORY-SOURCE-REGISTRY.md` has these fields:

| Field | Meaning |
|---|---|
| `source_id` | Unique, permanent ID, form `MEM-NNN`, sequential, never reused even if the entry is later deprecated. |
| `name` | A human-readable label. |
| `type` | The kind of source. Not a closed set — `git_repository` and `google_drive` are defined below; a new type may be added through the governance process in this document, not invented ad hoc by a Role mid-run. |
| `locator` | A stable, environment-independent reference — see per-type shapes below. **Never a literal local filesystem path.** |
| `access_requirements` | An abstract description of what class of permission is needed (e.g. "read-only Git fetch access," "read-only Drive API scope") — never an actual credential, token, or secret. |
| `status` | `active`, `inactive`, `deprecated`, or `unverified`. This is an availability/lifecycle flag, not a reliability score — see "What this registry is not," below. |
| `steward` | Who added or currently maintains this entry. |
| `added` | Date the entry was created. |
| `last_verified` | Date the locator was last confirmed to actually resolve, or `null` if never verified. |
| `notes` | Free text. |

### Locator shape per type

- **`git_repository`** — `{ repository: <name, e.g. "project-memory">, owner: <account, e.g. "DinevDecor">, path_within_repo: <relative path, or "/" for the whole repository>, ref: <branch or tag, default "main"> }`.
- **`google_drive`** — `{ drive_or_shared_drive: <name>, folder_path_or_id: <stable Drive identifier> }`. No entry of this type exists yet in the registry — see "What this document does not do."
- **Future types** — must define an equivalently stable, non-path locator shape as part of being added; see Governance.

## Connection Protocol

The path from a registry entry to actually-readable content, for a
given run, in a given session:

### Stage 1 — Lookup

A Role (or a human acting on its behalf) consults
`MEMORY-SOURCE-REGISTRY.md` for sources matching a need — by `type`,
`name`, or free-text search of `notes`. A source is never assumed to
exist, or assumed reachable, without being looked up here first.

### Stage 2 — Selection & Authorization

A human, or an authorized Curator (the same procedural function already
defined in `../../proposals/PROP-0002-discovery-intake-system.md` §5),
explicitly selects which looked-up registry entries are in scope for
this specific run. This selection becomes the "authorized sources" list
that a Role's own `INPUTS.md` already requires — the registry changes
*where that list comes from*, not the rule that it must be explicit.
Lookup alone (Stage 1) never authorizes anything by itself.

### Stage 3 — Resolution

For this session only, each authorized entry's stable `locator` is
turned into an actual, readable local reference (a clone path, a
mounted folder, an API handle — whatever the environment provides).
This resolved reference is **session-scoped and disposable**: it is
never written back into the registry, and a different session may
resolve the same `locator` to a completely different local path without
that being any kind of inconsistency.

### Stage 4 — Verification

Confirm the resolved source is actually reachable and matches the
registry's `type` expectations (for example: a `git_repository` entry
actually clones; a `path_within_repo` actually exists in that
checkout). On success, `last_verified` is updated in the registry. This
is registry maintenance, not part of any specific Role's run output.

### Stage 5 — Read-only Access

Whatever Role consumes the resolved source does so strictly read-only.
This protocol does not grant any Role more access than its own
`LIMITATIONS.md` already allows — AG-002's prohibition on editing a
historical source, for example, is not relaxed or reinterpreted by
anything here. The Connection Protocol's job is to make sure the
*connection itself* never offers write access in the first place, not
to rely solely on the Role's own discipline once connected.

### Stage 6 — Disconnection

At the end of a run, session-scoped access (a clone, a mounted folder,
an API session) is torn down. No persistent credential, token, or
mount is left active because one run happened to need it.

## Governance

| Action | Who may do it |
|---|---|
| Add a new registry entry | A human, or an authorized Curator, with a `steward` and `added` date recorded. |
| Verify an existing entry (Stage 4) | Anyone conducting Stage 3–4 of a real run — a mechanical check, not a judgment call. |
| Deprecate an entry | A human, with a reason recorded. The entry is marked `deprecated`, never deleted — matching the append-only convention already used in `../EMPLOYEE-REGISTRY.md` and `../ORB/ORB-REGISTRY.md`. |
| Add a new source `type` | A human, following the same disciplined-change principle `../FOUNDING-CHARTER.md` §4 already states for this repository generally: propose it, do not silently start using an unlisted type mid-run. |

## What this registry is not

- **Not a trust or reliability score for sources.** `status` is an
  availability flag (active/inactive/deprecated/unverified), not a
  scored judgment of how much a source should be trusted. A
  context-scoped trust-scoring mechanism is trust-engine's fully
  specified territory (`../../proposals/
  PROP-0001-discovery-lab-boundaries.md`, ground rule 3); this registry
  does not build a competing one.
- **Not a credential store.** `access_requirements` describes what kind
  of access is needed in the abstract; it never contains an actual
  secret, token, or password.
- **Not an automated connector.** Resolution (Stage 3) and Verification
  (Stage 4) are described as procedures a human or Executor follows
  deliberately, each time, not as a scheduled or triggered process. No
  code, and no GitHub Action, is created by this document.

## What this document does not do

- It does not modify AG-002, or any other Role, to actually consult
  this registry. That is a future, separate migration step.
- It does not register a Google Drive source. No such source has
  actually been checked or verified in this session for this purpose;
  inventing one would be exactly the kind of fabrication this
  repository's own discipline (and the task that created AG-002)
  explicitly rejects. The `google_drive` type is defined, ready, and
  unused.
- It does not register `KOD`, `generative-discovery-engine`, or
  `trust-engine`, even though clones of them happen to be accessible in
  this session from unrelated earlier work. None of them has actually
  been used as a memory source by any Role. Registering them now would
  be adding entries ahead of evidence, which `METRICS.md`-style
  discipline elsewhere in this repository (e.g. AG-001's own
  `../employees/AG-001-repository-observer/METRICS.md`, "no invented
  starting values") already argues against.

## Disambiguation notes

- **"Memory," here, means an external data repository a Role may read
  from** (a Git repository, a Drive folder) — it is **not**
  trust-engine's "Trust Memory," "Observation Memory," "Meta Trust
  Memory," or any of that repository's own structured, trust-scored
  memory layers, and it does not claim any authority over what those
  terms mean there.
- **"Source," here, is a registered, typed, verifiable external system**
  — distinct from `PROP-0002-discovery-intake-system.md`'s Discovery
  Ledger `source` field, which is a loose, free-text description of
  where one Ledger Entry came from (e.g. "AG-001 RUN-0001 finding #7").
  A future Ledger Entry's `source` field could plausibly *reference* a
  `MEM-NNN` registry entry by ID when applicable — but that would be a
  change to `PROP-0002`, which this document does not make; it is
  recorded here only as an open integration question.
- **"Registry"** follows the exact convention already established by
  `../EMPLOYEE-REGISTRY.md` and `../ORB/ORB-REGISTRY.md` — an
  append-only Markdown table, no dedicated index-generation tooling, no
  new pattern introduced.
