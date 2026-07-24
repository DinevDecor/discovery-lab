# History — AG-002 Discovery Archaeologist

Employee ID: **AG-002** · Role Name: **Discovery Archaeologist** ·
Status: **Prototype / DRAFT / EXPERIMENTAL / NOT ADOPTED** · Version:
**v0.1**

This is an append-only log. Entries are never edited or removed once
written — only new entries are added, at the bottom.

## 2026-07-24 — Role created

AG-002 v0.1 prototype created: full document set (`CONTRACT.md`,
`ROLE.md`, `INPUTS.md`, `OUTPUTS.md`, `LIMITATIONS.md`, `CHECKLIST.md`,
`METRICS.md`, `RUN-PROTOCOL.md` — the Recovery Protocol v0.1 —
`PROMPT.md`, `STATUS.yaml`, this file). Status set to
`prototype` rather than the "production-ready" language used in the
task that requested this Role, to preserve `../../
HIRING-LIFECYCLE-DRAFT.md`'s existing lifecycle discipline — recorded
explicitly, not applied silently.

## 2026-07-24 — PILOT-RUN-0001

First real run executed, immediately after creation. Scope: the
Project Memory archive (`project-memory/archive/`) plus current-state
files in the same repository, for comparison. The "diary archive" named
in the requesting task could not be located anywhere accessible and was
recorded as `INSUFFICIENT ACCESS`, not substituted. Report:
`runs/PILOT-RUN-0001-recovery-report.md`. Recovered: 7 ideas, 4 repeated
themes, 5 idea-evolution timelines, 2 forgotten ideas, 4 candidate
investigations (none created), 2 contradictions (one documented
revision, one principle/outcome gap), 6 open questions.

## 2026-07-24 — PILOT-RUN-0002 (blocked at Stage 1, no report produced)

Second real run requested. Unlike PILOT-RUN-0001, exactly one source
was authorized this time, with no substitution permitted: a diary
archive at Google Drive, "Project Memory → Archive → oneDay 6.zip" (or
its already-extracted folder at the same location). Stage 1 (Historical
Sources / Lookup, `RUN-PROTOCOL.md`) was attempted by three distinct
methods in this session — `search_files` (`title contains 'oneDay
6'`), `search_files` (`title contains 'Project Memory'`), and
`list_recent_files` — all against the Google Drive MCP connector. All
three calls returned identically: `MCP error -32003: MCP tool call
requires approval`. No file, folder, or metadata was ever retrieved.
No source was ever reached, so no candidate could be discovered, no
citation linked, and no clustering performed — the run halted at Stage
1 per `RUN-PROTOCOL.md`'s Stop rule and the requesting task's own
instruction, rather than substituting Project Memory or any other
source. No Recovery Report exists for this run; producing one would
have misrepresented zero actual scanning as a completed pilot.
Reported to the requester verbatim as: `BLOCKED — Diary archive exists
but is not accessible from the current execution environment.` No
source document was read, modified, or invented. `runs_completed` in
`STATUS.yaml` was not incremented — no run was actually completed.

## 2026-07-24 — MIRROR-VERIFY-0001 (pipeline verification, not a real
recovery mission)

After `../../MEMORY-SOURCES/INFRA-SPRINT-01-report.md` §9 closed direct
Google Drive access as a platform limitation (a live approval test,
conducted with Petko actively granting approval in real time, still
failed with `MCP error -32003` on the very next call), a repository
operational memory mirror (`memory/`, registered as `MEM-003`) was built
per `../../../adr/ADR-0002-ag002-alternative-memory-access.md`
(ACCEPTED). This run verified AG-002 can read that mirror end to end,
using a source that has never touched Google Drive: a labeled synthetic
test fixture (`memory/journal/SYNTHETIC-TEST-journal-0001.md`),
fabricated and clearly marked as such throughout, since no real,
accessible content exists yet to test against. Full run report:
`runs/MIRROR-VERIFY-0001-recovery-report.md`. Recovered: 1 idea (a
fabricated "standing observatory" concept), 1 repeated theme, 1
idea-evolution entry, 0 forgotten ideas, 0 candidate investigations
(none proposed — the content is synthetic), 0 contradictions. Extracted
finding also written to `memory/observations/
MIRROR-VERIFY-0001-observation-0001.md`. Source file unmodified;
Archaeologist Boundary Statement confirms no invented content beyond
what the labeled-synthetic source itself contains. This is a genuine,
real execution of the Recovery Protocol's mechanics (Stages 1–7 all
actually performed) against fabricated content — distinct from
`PILOT-RUN-0002`, which remains unattempted against the real diary.
`runs_completed` in `STATUS.yaml` **is** incremented for this entry,
since the run itself was real, even though its source content was not;
performance/quality fields are left untouched, pending independent
review, per `CHECKLIST.md`.

## 2026-07-24 — Reality Inbox integration + REALITY-VERIFY-0001

The "Create the Reality Inbox" task established
`../../../../reality-inbox/` as an organization-wide, human-facing
intake layer (one drop folder, `📥 DROP HERE/` — the human never
chooses where a file goes; an agent/steward handles manifesting,
validation, and routing). This Role's own files received small,
additive edits, not a redesign: `INPUTS.md` gained a "Default
operational source: the Reality Inbox" section; `LIMITATIONS.md` gained
a new bullet (no scanning unrelated repository content as memory) and a
fourth mandatory escalation value, `BLOCKED` (a Reality Inbox source
reachable but with insufficient manifest/provenance); `RUN-PROTOCOL.md`
Stage 1 and `CHECKLIST.md` each gained a short Reality Inbox check.
`ROLE.md`, `OUTPUTS.md`, `CONTRACT.md`, `METRICS.md`, and `PROMPT.md`
were not touched.

Verification run `REALITY-VERIFY-0001`
(`runs/REALITY-VERIFY-0001-recovery-report.md`) exercised the full
cycle for real: a labeled synthetic fixture
(`reality-inbox/fixtures/SYNTHETIC-TEST-note-0001.md`) was placed in
`📥 DROP HERE/`, manifested (`reality-inbox/manifests/RI-0001.md`,
`intake_id: RI-0001`), moved to `reality-inbox/processed/`, and read by
AG-002 only after its manifest's `status: ACCEPTED` and provenance were
confirmed (per the new Stage 1 check) — not assumed. Recovered: 1 idea,
0 repeated themes (single appearance), 0 forgotten ideas, 0 candidate
investigations, 0 contradictions. Finding written to
`../../../../memory/observations/
REALITY-VERIFY-0001-observation-0001.md`. Source file unmodified;
Archaeologist Boundary Statement confirms the manifest was checked
before reading, not after. Distinct from `MIRROR-VERIFY-0001` (verified
`memory/`, not the Reality Inbox) and from the still-unattempted, still
-blocked `PILOT-RUN-0002`. `runs_completed` in `STATUS.yaml`
incremented again (`2 → 3`) — a second genuine run, again against
labeled synthetic content since no real evidence has entered the
Reality Inbox yet. AG-001 was reviewed for a compatibility need and
found not to require one — recorded in
`../../MEMORY-SOURCES/MEMORY-SOURCE-REGISTRY.md`'s `MEM-004` entry, not
silently skipped.

## 2026-07-24 — PILOT-RUN-0002, for real (partial)

The real diary named all the way back at this Role's creation
("Project Memory → Archive → oneDay 6.zip") arrived — not via any Drive
mechanism ever built, but through a direct GitHub upload
(commit `a3d4dcb`) landing in `reality-inbox/📥 DROP HERE/`, which this
session merged in. Processed as Reality Inbox intake `RI-0002`
(`reality-inbox/manifests/RI-0002.md`, `intake_mode: GITHUB_UPLOAD` — a
real value discovered in production use, added to
`../../../../reality-inbox/PROCESSING-PROTOCOL.md`'s schema alongside
the two previously defined). The archive (77 dated entries, 2025-10-18
to 2026-07-22) turned out to be genuinely mixed: personal content (life
philosophy, family, dreams, finances — 58 of 77 entries) and, from
2026-06-22 onward, a distinct cluster of structured KOD research
artifacts ("GRIF" documents).

This run — finally, genuinely `PILOT-RUN-0002` — read four of those
organizational entries in full and recovered 9 ideas, 2 repeated themes,
1 idea-evolution timeline (4 linked steps across 6 days), 0 forgotten
ideas, 3 candidate investigations (none created), 0 confirmed
contradictions (1 tension recorded as `INSUFFICIENT EVIDENCE` instead),
and 4 open questions — full report:
`runs/PILOT-RUN-0002-recovery-report.md`. **The run deliberately did not
process the 58 personal entries** — reading and git-committing verbatim
quotations of deeply personal content (family, named individuals,
finances, dreams) without explicit guidance was judged a genuine
human-decision point, not a technical block, and the run paused there
rather than either fabricating restraint by skipping silently or
overriding it by extracting anyway. `RI-0002`'s `status` remains
`PROCESSING`, not `ACCEPTED` — this is an honest, partial state, not a
finished one. `runs_completed` in `STATUS.yaml` incremented (`3 → 4`) —
the run was real and substantial, even though incomplete.

## 2026-07-24 — PILOT-RUN-0002 completed, under a new decided policy

Petko decided the "AG-002 Personal Diary Processing Policy": AG-002 is
authorized to read the entire diary, including personal entries, but
personal content does not automatically become recorded knowledge — only
durable knowledge (ideas, principles, hypotheses, observations,
recurring patterns, decisions, experiments, research questions,
methodology) is extracted, with minimum necessary quotation and full
provenance; an entry with none is recorded as `NO KNOWLEDGE EXTRACTED`
and processing continues without stopping.

Under this policy, this run read the remaining 73 entries: 15 more
organizational entries plus 4 originally-`AMBIGUOUS` entries resolved
as organizational on an actual read, and all 47 personal entries (1
originally-`AMBIGUOUS` entry resolved as personal). Real findings
recovered from the newly-read organizational content: a formal "KOD
Research Protocol v1.0" (an Evidence Ladder, Convergence Mode, Breaker
Mode), a cluster of six `VALIDATED`-state methodology GRIFs at
confidence up to `1.00`, a three-layer knowledge architecture proposal
(Obsidian / KOD Registry / AI), the diary's first **Trust Engine**
content (a Historical Analogy Engine — comparing market regimes by
constraint-similarity, not chart shape), a self-identity GRIF stating
KOD's "only sacred rule," a documented negative-knowledge research
result (eight candidate properties explicitly rejected, two survived
adversarial testing), a hypothesis on AI as a "second-order sensor," an
economic principle on knowledge crystallization, and a newly-named
project concept, "Reality Observatory." The diary's single most
repeated idea — "nature as a library of architectures" — was confirmed
restated five independent times across a month, the strongest
evidentiary signal in the whole archive of what its author considered
most important. All 47 personal entries were read in full and correctly
yielded no extractable knowledge — a real, checked result, not an
assumption; one entry (`20260623`, a book-idea list) was a genuinely
close call and is recorded with its reasoning shown, not silently
folded into the rest.

Full report (substantially rewritten to reflect completion, not just
appended to): `runs/PILOT-RUN-0002-recovery-report.md`. `RI-0002`'s
`status` is now `COMPLETED` — every entry read at an appropriate depth,
though the report's own Archaeologist Boundary Statement states plainly
that the largest organizational entries likely contain further findings
a deeper future pass could still extract; "completed" is not claimed to
mean "exhaustive." A relationship-graph artifact and per-category
Knowledge registries (Ideas/Principles/Hypotheses/Decisions/Research
Questions, as the original task's taxonomy asked for) were recommended
in the Recovery Queue but not built this run — recorded as a real gap
against the literal ask, not silently substituted. `runs_completed` in
`STATUS.yaml` is not incremented again for this entry — it is the
completion of the same `PILOT-RUN-0002` already counted, not a new run.

## 2026-07-24 — STRESS-RUN-0003, -0004, -0005 (AG-003 Reality Stress Test)

Three new real recovery runs, requested as part of the "AG-003 Reality
Stress Test" task — validating AG-003 against real source material
structurally different from the diary. Each run read a small,
manifested Reality Inbox intake (`RI-0003`, `RI-0004`, `RI-0005`) using
a new, real `intake_mode` value, `SESSION-LOCAL-REPO-COPY` (added to
`../../../../reality-inbox/PROCESSING-PROTOCOL.md`'s schema, same
precedent as `GITHUB_UPLOAD`): files copied from other repositories
already accessible in this session's workspace (this repository's own
`docs/adr/`, and the separate `kod` and `trust-engine` repositories),
never a human drop.

- **`STRESS-RUN-0003`** (`runs/STRESS-RUN-0003-recovery-report.md`):
  this repository's own four ADRs. Recovered 14 findings, 2 repeated
  themes, one self-documented ID-numbering collision (`ADR-0003`'s own
  header), and three source-declared cross-document dependencies
  (`Depends on`/`Amends` headers) — a different evidentiary situation
  than every prior run, where all relationships had to be inferred from
  prose.
- **`STRESS-RUN-0004`** (`runs/STRESS-RUN-0004-recovery-report.md`):
  seven real files from `kod` (read as an external, observed source
  only, per `../../../../proposals/PROP-0001-discovery-lab-
  boundaries.md` Principle 0 — nothing written back to `kod`). Recovered
  7 findings including one strong repeated theme (three independent
  "research over conclusions" statements) and one probable near-
  duplicate ("reality is the final arbiter," two documents). Two
  deliberately near-empty sources (an excavation progress tracker at 0%,
  a blank Knowledge Object template) correctly yielded almost no
  extracted content, not fabricated content.
- **`STRESS-RUN-0005`** (`runs/STRESS-RUN-0005-recovery-report.md`):
  three real operational reports from `trust-engine` (also read as an
  external, observed source only). Recovered a real, unresolved
  Latin/Cyrillic model-ID data collision and a real audit-then-migration
  sequence, with the migration correctly read as *excluding* the
  audit's flagged bad rows rather than fixing them — a distinction
  verified against the report's own row counts, not assumed from its
  `PASS` label.

All three runs, plus a fresh adversarial re-audit of the existing
`PILOT-RUN-0002` diary material, fed the AG-003 Reality Stress Test
Report (`../../../../proposals/AG-003-reality-stress-test/
REALITY-STRESS-TEST-REPORT.md`), which found three real gaps in AG-003's
architecture (not in AG-002's) and one coverage/completeness note — see
that report and AG-003's own `HISTORY.md` for the curation-side detail.
`runs_completed` in `STATUS.yaml` incremented by 3 (`4 → 7`) — three
real, distinct runs.

## 2026-07-24 — Release 1.0: FROZEN

Per an explicit "Discovery Lab — Freeze Release 1.0" task (governance,
not development — no redesign, no new feature). Status advanced
`prototype, v0.1` → `frozen, v1.0`, on the strength of the validation
record above: an internal design review, an adversarial self-review, and
a real Reality Stress Test across four structurally different real
datasets, all summarized in `../../../releases/1.0/
VALIDATION-HISTORY.md`. `adoption_status` remains `not_adopted` and is
unchanged by this freeze — see `STATUS.yaml`'s `freeze_note` and
`../../GOVERNANCE.md`, "Freeze vs. adoption": architectural stability and
organizational trust are deliberately independent axes. Full release
record: `../../../releases/1.0/RELEASE-1.0.md`.
