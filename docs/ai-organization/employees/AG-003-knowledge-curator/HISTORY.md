# History — AG-003 Knowledge Curator

Employee ID: **AG-003** · Role Name: **Knowledge Curator** ·
Status: **Prototype / DRAFT / EXPERIMENTAL / NOT ADOPTED** · Version:
**v0.1**

This is an append-only log. Entries are never edited or removed once
written — only new entries are added, at the bottom.

## 2026-07-24 — Role designed (architecture only, no implementation)

AG-003 v0.1 prototype designed per an explicit "DRAFT — architecture
only" task: full document set (`CONTRACT.md`, `ROLE.md`, `INPUTS.md`,
`OUTPUTS.md`, `LIMITATIONS.md`, `CHECKLIST.md`, `METRICS.md`,
`KNOWLEDGE-OBJECT-SPEC.md`, `LIFECYCLE.md`, `RELATIONSHIP-ONTOLOGY.md`,
`PROMOTION-RULES.md`, `REVIEW-PROTOCOL.md`, `CURATION-PROTOCOL.md`,
`PROMPT.md`, `STATUS.yaml`, this file). Status set to `prototype`,
matching AG-001's and AG-002's own lifecycle discipline. No run of
AG-003 has occurred — `runs_completed: 0`.

A worked-example walkthrough was produced at
`../../../proposals/AG-003-knowledge-curator-walkthrough/`, demonstrating
the architecture against AG-002's one completed real run
(`../AG-002-discovery-archaeologist/runs/
PILOT-RUN-0002-recovery-report.md`): a Knowledge Merge Proposal (two
candidate KOD-architecture descriptions, RI-8 and RI-12), a Relationship
Proposal (RI-11's methodology cluster and the separately-named
"Cognitive Sovereignty" line), a Core Principle Proposal (RT-3's
five-appearance "nature as a library of architectures" idea, proposed
one step, Draft → Candidate Principle, explicitly not further), a
Contradiction check that declined to file a Contradiction Report and
explained why (preserving AG-002's own `INSUFFICIENT EVIDENCE` marking
on the NORM/confidence tension rather than escalating it), a Knowledge
Evolution Report (RT-4's four-revision Recursive Adaptive Response
chain), and a Gap Report (folding in AG-002's existing `CI-4`/`CI-5` by
reference, plus one new AG-003-level structural observation about
weakly-connected Knowledge Objects that a linear Recovery Report
wouldn't surface on its own).

The architecture was then reviewed adversarially against itself —
`../../../proposals/AG-003-knowledge-curator-walkthrough/
ADVERSARIAL-REVIEW-0001.md` — before this Role was reported complete.
See that file for the recorded findings, both fixed and left open.

## 2026-07-24 — AG-003 Reality Stress Test (first real curation passes)

The architecture's first **real** curation passes (not demonstrations):
three new real AG-002 recovery runs — `STRESS-RUN-0003` (this
repository's own four ADRs), `STRESS-RUN-0004` (seven real files from
the separate `kod` repository), `STRESS-RUN-0005` (three real reports
from the separate `trust-engine` repository) — each curated in full
(`../../../proposals/AG-003-reality-stress-test/CURATION-0003.md`,
`CURATION-0004.md`, `CURATION-0005.md`), plus a fresh adversarial
re-audit of the existing diary dataset
(`DATASET-1-REAUDIT.md`). `runs_completed` incremented `0 → 3` (the
re-audit is not counted as a fourth run, matching AG-002's own
precedent of not double-counting a re-examination pass).

Requested explicitly as a falsification exercise, not a confirmation
one. Result: the architecture's **governance layer held without
exception** across four structurally different real datasets (a
narrative diary, header-linked governance documents, an undated
multi-file research corpus, and dense tabular audit data) — no
automatic merge, promotion, or contradiction resolution occurred
anywhere, no citation was invented, and two deliberate hallucination
traps (a near-empty excavation progress file, a blank Knowledge Object
template) both correctly yielded no fabricated content. The
**relationship- and maturity-detection layers did not fully
generalize**: three real, evidence-linked gaps were found — `F-1`
(`RELATIONSHIP-ONTOLOGY.md`'s `supersedes` type could not honestly
express a real source's own "amends one property, leaves the rest
unchanged" relationship), `F-2` (`KNOWLEDGE-OBJECT-SPEC.md`'s
`maturity` field did not define what counts as "one source" when a
corpus spans multiple files in one repository), and `F-3` (no cycle
check existed for `supersedes`/`depends_on` proposals, found through
active adversarial reasoning, not from an actual cycle in any dataset).
All three were fixed with small, targeted corrections, each cited
directly to its originating piece of evidence — see
`../../../proposals/AG-003-reality-stress-test/
REALITY-STRESS-TEST-REPORT.md` for the full trail. A fourth finding,
`F-4` (two concrete relationships the first walkthrough's own limited
scope had missed), was recorded as a coverage note, not an architecture
defect — no file was changed for it.

Freeze recommendation returned by the stress test: **READY WITH MINOR
CHANGES** — the three corrections above are those changes, already
applied. `known_missed_findings` in `STATUS.yaml` updated to record
`F-1`–`F-4` by name, not left at "unknown."

## 2026-07-24 — Release 1.0: FROZEN

Per an explicit "Discovery Lab — Freeze Release 1.0" task (governance,
not development — no redesign, no new feature). Status advanced
`prototype, v0.1` → `frozen, v1.0`, on the strength of the validation
record above. `adoption_status` remains `not_adopted` and is unchanged
by this freeze — see `STATUS.yaml`'s `freeze_note` and
`../../GOVERNANCE.md`, "Freeze vs. adoption." One real, unresolved
inconsistency between two validation passes was caught while preparing
this freeze (not before): the Reality Stress Test's own `F-2` fix
incidentally restates, rather than closes, the adversarial review's
earlier finding 4 (a `maturity: Convergent` re-scan loophole) — recorded
honestly, left unfixed in this freeze since fixing it would be a new
architecture change this release's own task forbids; see
`../../../releases/1.0/VALIDATION-HISTORY.md` item 16 and
`LESSONS-FROM-V1.md`. Full release record:
`../../../releases/1.0/RELEASE-1.0.md`.
