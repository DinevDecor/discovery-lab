# Recovery Report — STRESS-RUN-0003

**STATUS: COMPLETE.** Real run, dataset 2 of the "AG-003 Reality Stress
Test" task (`../../../../proposals/AG-003-reality-stress-test/
REALITY-STRESS-TEST-REPORT.md`): "Project documentation (ADR, SPEC,
Protocols)." Source: `reality-inbox/` intake `RI-0003`
(`../../../../../reality-inbox/manifests/RI-0003.md`) — this
repository's own four Architecture Decision Records.

## Run Metadata

- Run ID: `STRESS-RUN-0003`
- Timestamp: 2026-07-24
- Sources requested: `RI-0003` (4 files, all authorized)
- Sources scanned: 4 of 4 — `ADR-0001-human-authority-gates.md`,
  `ADR-0002-ag002-alternative-memory-access.md`,
  `ADR-0003-reality-inbox-architecture.md`,
  `ADR-0004-local-drive-synced-reality-inbox.md`
- Sources inaccessible: none
- Manifest check: `RI-0003` confirmed present with complete provenance
  before any file was read

## Executive Summary

Four real governance documents, all dated the same day (2026-07-24),
recovered 14 findings: the Human Authority Gate (HAG) concept and its
required behaviors, a four-category Organizational Principle, a
two-axis Registry extension (proposed, not yet applied to the real
Registry), a Human-Mediated Export Bridge decision, a Reality Inbox
freeze with an explicit change-governance rule, and the local-Drive
intake amendment with its own negative "mkdir is not evidence" finding.
Three self-documented cross-document relationships were found stated
directly in the sources' own headers (`Depends on`, `Amends`), not
inferred from prose — a different evidentiary situation than the diary
dataset, where every relationship had to be inferred. One real,
source-declared naming collision was found (`ADR-0003`'s own header
explains it was requested as "ADR-0002" but registered as `ADR-0003` to
avoid colliding with the existing `ADR-0002-ag002-alternative-memory-
access.md`). No confirmed contradictions — every apparent tension in
this dataset (see "Contradictions" below) turned out to be explicitly,
textually self-reconciled by the documents themselves.

## Recovered Ideas

### RI-1 — Human Authority Gate (HAG)

- `ADR-0001-human-authority-gates.md` §2: *"A Human Authority Gate is
  any action that requires explicit human authorization before the
  organization may continue... Crossing a HAG is never considered an
  error. It is a normal state transition."*

### RI-2 — Standard Agent Behavior, six steps

- `ADR-0001` §3: stop immediately; preserve accumulated work; record the
  exact reason; specify the minimal human action required; wait; resume
  automatically after authorization if possible. *"No retries. No
  workarounds. No duplicated data."*

### RI-3 — Four-category Organizational Principle

- `ADR-0001` §6: Technical failure / Infrastructure limitation /
  Governance boundary / Human Authority Gate. *"Only the first two are
  engineering problems. The latter two are expected operational
  states."*

### RI-4 — Two-axis Registry extension (proposed, not applied)

- `ADR-0001` §5: every external resource gains two independent states —
  Connectivity (Connected/Disconnected) and Authority (Authorized/
  Pending Human Approval/Denied/Unknown). §5.1 applies this
  retroactively to `MEM-001`/`MEM-002` *"for illustration only — not
  applied to the actual Registry file by this ADR."*

### RI-5 — Open question: where does `deprecated` fit the two-axis model

- `ADR-0001` §5.2: the existing schema's `deprecated` value is a
  lifecycle/retirement flag, not a live-state observation, and does not
  map cleanly onto either axis. Explicitly left unresolved, not decided.

### RI-6 — Human-Mediated Export Bridge

- `ADR-0002-ag002-alternative-memory-access.md` §2: a human periodically
  exports diary content from Google Drive into a Git-tracked location
  (`memory/`, per the Acceptance block); AG-002 reads it exactly as it
  already reads `MEM-001`. No new AG-002 capability required.

### RI-7 — Self-critical tension: "no duplicated memory"

- `ADR-0002` §4: *"A Git mirror of Drive content is, plainly, a
  duplicate."* Explicitly not resolved unilaterally — flagged for the
  requester to weigh, with an argument for an exception (archival,
  point-in-time snapshot of closed historical evidence) and an argument
  against (no such exception exists in writing yet) both stated.

### RI-8 — Reality Inbox freeze, two fixed properties

- `ADR-0003-reality-inbox-architecture.md` §2: (1) the human-facing
  interface is exactly one folder (`reality-inbox/📥 DROP HERE/`); (2)
  processing state is tracked only through manifests, never through
  which folder a file physically sits in.

### RI-9 — Explicit change-governance rule

- `ADR-0003` §3: a fixed list of what requires a new ADR to change
  (adding a second human-facing folder; moving state tracking out of
  manifests; changing the manifest schema's required fields; changing
  who may perform mechanical processing; weakening file-handling rules)
  versus what does not (ordinary processing, adding manifest/`INDEX.md`
  entries, writing a large-file policy, extending Reality Inbox use to
  another repository under the same design).

### RI-10 — Self-documented numbering collision, flagged not hidden

- `ADR-0003`'s own header: the requesting task named it "ADR-0002," but
  that ID was already taken by `ADR-0002-ag002-alternative-memory-
  access.md`; per the ADR index's own sequential-numbering rule, this
  document was registered as `ADR-0003` instead, with the conflict
  stated in the document's own header rather than silently renumbering
  the existing `ADR-0002` or silently complying with the conflicting
  number.

### RI-11 — Local-Drive-synced intake decision

- `ADR-0004-local-drive-synced-reality-inbox.md` §3: primary human-facing
  folder becomes `G:\My Drive\Projects\discovery-lab\DROP HERE` for
  sessions that can reach it; `reality-inbox/📥 DROP HERE/` is kept,
  unchanged, as the fallback for sessions that cannot (§3.1's two-mode
  table). Framed explicitly as amending, not violating, `ADR-0003`'s
  freeze.

### RI-12 — Diagnostic evidence: this session cannot reach `G:\`

- `ADR-0004` §2: concrete commands and their real output (`mount | grep
  -iE 'cifs|smb|nfs|9p|drvfs'` → no output; `env | grep -iE
  'drive|winuser...'` → no output; `rclone` binary present but not on
  `PATH`). Conclusion stated as structural, not a permission gap: *"this
  session runs inside a remote, ephemeral Linux container... a
  completely different computer from the one running Google Drive for
  Desktop."*

### RI-13 — Negative finding: `mkdir` succeeding is not evidence of Drive access

- `ADR-0004` §6: `mkdir -p "/mnt/g/My Drive/..."` returned exit code 0,
  but this is explicitly recorded as **not** evidence of Google Drive
  access — an ordinary, disconnected local directory, deleted
  immediately (`rm -rf /mnt/g`) specifically so it could not be mistaken
  by a future reader for a working bridge.

### RI-14 — Two independent Google Drive limitations, explicitly not conflated

- `ADR-0004` §1: the MCP connector's non-resumable per-call approval gate
  (`ADR-0002`'s and `INFRA-SPRINT-01-report.md` §9's territory) and this
  session's total lack of any local-filesystem bridge to the user's
  machine (`ADR-0004`'s own territory) are stated as two independent
  problems — even a working connector would not resolve a local Windows
  path, since it speaks the Drive API, not local paths.

## Repeated Themes

### RT-1 — "Record the tension, don't silently resolve it"

- `ADR-0001` §5.2 (the `deprecated` open question), `ADR-0002` §4 (the
  "no duplicated memory" tension), `ADR-0003`'s own header (the
  numbering collision) — a recurring discipline appearing once in each
  of three separate documents: when a document's own decision creates a
  tension with an existing principle or a naming conflict, the tension
  is written down explicitly rather than quietly worked around.

### RT-2 — "Governance" used in two senses, self-reconciled in the source

- `ADR-0001` §6.1 explicitly reconciles two different uses of the word
  "governance" within this repository's own material: Infrastructure
  Sprint 01's *"governance cause"* (an organizational ownership gap,
  fixable) versus this ADR's own *"Governance boundary"* category (an
  intentional, permanent boundary, not to be engineered away). Recorded
  here as a Repeated Theme (a self-aware terminology note), **not** as a
  Contradiction — the source itself resolves the collision in the same
  paragraph it raises it; see "Contradictions" below for why this
  distinction matters for this run specifically.

## Idea Evolution (Discovery Timeline)

All four sources are dated the same calendar day (2026-07-24) — unlike
`PILOT-RUN-0002`'s diary (a month-plus span), this dataset has
effectively no time axis to show evolution *over*. What it has instead
is an explicit **dependency order**, stated directly in each document's
own header, not inferred:

- `ADR-0001` (Human Authority Gates) — no stated dependency within this
  set; the foundational document.
- `ADR-0002` — header: *"Depends on / builds on: `ADR-0001-human-
  authority-gates.md`"*.
- `ADR-0003` — header: *"Depends on / builds on: `ADR-0002-ag002-
  alternative-memory-access.md`"*.
- `ADR-0004` — header: *"Amends: `ADR-0003-reality-inbox-architecture.md`"*,
  and separately *"Depends on: `../ai-organization/MEMORY-SOURCES/
  INFRA-SPRINT-01-report.md` §9"* (a source outside this run's scope,
  cited but not read here).

This is recorded descriptively; whether AG-003 should treat a
source-declared `Depends on`/`Amends` statement differently from an
inferred relationship is addressed in the Curation pass
(`../../../../proposals/AG-003-reality-stress-test/
CURATION-0003.md`).

## Forgotten Ideas

**None applicable.** All four sources are same-day documents; "forgotten
idea" detection requires a time gap in which an idea could have been
dropped without a documented successor, which this dataset structurally
does not have enough time span to show. Recorded as a category with no
signal, not as a category checked and found empty — a real, honest
distinction this run surfaces that `PILOT-RUN-0002` (a month-plus
archive) did not need to make.

## Candidate Investigations

*(Recommended only — no Investigation file created, per `LIMITATIONS.md`;
numbered continuing AG-002's own global sequence — `PILOT-RUN-0002`
used `CI-1` through `CI-5`.)*

- **CI-6** — whether `RI-5`'s open question (where `deprecated` fits the
  two-axis Registry model) has been resolved anywhere since `ADR-0001`
  was accepted. Out of this run's scope to check (would require reading
  `MEMORY-SOURCE-REGISTRY.md`, not part of `RI-0003`), but worth a human
  or a future AG-002 run confirming — `MEMORY-SOURCE-REGISTRY.md`'s own
  "Reading this table" section (not re-read in this run, per scope
  discipline) was previously observed to describe the two-axis migration
  as **NOT STARTED**, which would mean `RI-5`'s question is also still
  open, but this run does not confirm that first-hand and does not cite
  it as fact.

## Contradictions

**None confirmed.** Two candidates were checked and both resolved as
documented, self-aware statements, not live disagreements:

1. `RT-2`'s two senses of "governance" — resolved by `ADR-0001` §6.1
   itself, in the same document, same section.
2. Whether `ADR-0001`'s HAG reclassification of the Google Drive
   `-32003` signal (a "normal state transition," not a failure)
   contradicts `ADR-0002`/`INFRA-SPRINT-01-report.md`'s framing of the
   same signal as a "platform limitation" — resolved by `ADR-0001` §6.1's
   own reconciliation: the approval gate itself reclassifies to a HAG,
   while the *downstream* gaps (no auto-resume, no assigned owner) remain
   genuine Infrastructure limitations. Both classifications describe
   different aspects of the same incident, not competing claims about the
   same aspect.

This is a real, checked result specific to this dataset, not an
assumption that governance documents never contradict each other.

## Open Questions

- `RI-5`'s `deprecated` placement question (also `CI-6`).
- Whether `ADR-0001` §5's two-axis Registry proposal was ever applied in
  practice — out of scope to confirm in this run (see `CI-6`).
- Whether `ADR-0004`'s local workflow has since been exercised for real
  by a local session — out of scope to confirm in this run (this dataset
  contains only `ADR-0004` itself, not any later verification record).

## Recovery Queue

1. **`CI-6`** — see above.
2. Consider a future recovery run over `MEMORY-SOURCE-REGISTRY.md` and
   `ADR-0001-migration-plan.md` specifically, to close `CI-6` and this
   run's other out-of-scope Open Questions with first-hand evidence
   rather than recollection.

## Evidence

All four sources, in `reality-inbox/processed/stress-test-project-docs/`:
`ADR-0001-human-authority-gates.md`, `ADR-0002-ag002-alternative-memory-
access.md`, `ADR-0003-reality-inbox-architecture.md`, `ADR-0004-local-
drive-synced-reality-inbox.md` — quoted or cited above under the
Recovered Idea / Repeated Theme entry matching each. `reality-inbox/
manifests/RI-0003.md` — full provenance and `sha256` hashes for all four.

## Archaeologist Boundary Statement

No source document was modified — all four files were read only, from
read-only copies in `reality-inbox/processed/stress-test-project-docs/`,
hash-verified against the live `docs/adr/` originals at copy time
(`RI-0003.md`). No content was invented — every Recovered Idea traces to
an exact quotation or a precise paraphrase of a stated decision, section,
or diagnostic command output. No duplicate was removed. No idea is
asserted as true, good, or worth pursuing beyond what each source itself
states about its own status (`ACCEPTED`, `ACCEPTED — FROZEN`, etc. —
reported as the source's own claim, not verified independently). The two
Contradiction candidates were actually checked against the source text,
not assumed absent. `RI-0003.status` is `COMPLETED` — all 4 files read in
full; none were long enough to leave a plausible "deeper pass would find
more" caveat the way `PILOT-RUN-0002`'s largest diary entries did.
