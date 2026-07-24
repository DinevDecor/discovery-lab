# AG-003 Reality Stress Test — Report

Status: **DRAFT VALIDATION**, complete. Goal per the requesting task:
falsify AG-003, not confirm it. This report records what actually broke,
what held, and what was changed — with every change linked to a specific
piece of evidence from a specific dataset, per the task's own "Important
Rule."

## Test matrix actually run

| # | Category (as requested) | Real source used | Files | Why this source |
|---|---|---|---|---|
| 1 | Personal diary | `oneDay 6.zip` (already completed, `RI-0002`) | 77 entries | Pre-existing; re-audited here, not re-run |
| 2 | Project documentation (ADR/SPEC/Protocol) | This repository's own `docs/adr/ADR-0001`–`ADR-0004` | 4 | Real, in-repo, explicit header-declared dependencies |
| 3 | Research notes/investigations (GRIF, Discovery documents) | `kod` repository: `EX-0001` case+progress, `ART-0001`, `kod`'s own `ADR-0001`–`ADR-0003`, `KNOWLEDGE_OBJECT_TEMPLATE.md` | 7 | Real external research artifacts; includes deliberately near-empty sources and KOD's own real Knowledge Object schema |
| 4 | Operational material | `trust-engine`: audit report, migration report, feature review | 3 | Real audit/migration/review reports — closest accessible analog to "project logs"; see below for what was not accessible |

**Voice transcripts, meeting notes, and "Dinev Assistant" outputs are
confirmed `INSUFFICIENT ACCESS`** in this environment — not a gap in
this test's effort. The separate `project-memory` repository's
`notes/2026-07-19-dinev-decor-systems-location-check.md` is a real, prior,
already-exhaustive investigation (repository search, `add_repo`
attempts, and a direct `git clone` fallback, across two separate passes)
that found no audio, transcript, meeting-note, or "Dinev Assistant"
content anywhere reachable from this account. Re-attempting the same
search here would not produce new evidence, per that note's own "Access
Blocker" section — so this test used the closest real, accessible
operational-material analog instead (trust-engine's own reports) rather
than fabricating transcripts or meeting notes to fill the category.

No fifth dataset was added — three real source classes (discovery-lab's
own governance docs, `kod`, `trust-engine`) already gave enough
structural diversity (narrative diary, header-linked ADRs, undated
research artifacts, dense tabular audit data) to stress the architecture
meaningfully without diluting effort across a fourth, weaker source.

## Per-dataset results

### Dataset 1 — Personal diary

**Verdict: PASS.** Re-audit only (no new AG-002/AG-003 run — the
existing `PILOT-RUN-0002` and first walkthrough already covered this
material in depth). Full detail: `DATASET-1-REAUDIT.md`.

- **Weaknesses found**: `F-3` (no cycle check for directional
  relationship types — a general architectural gap, not diary-specific);
  `F-4` (the first walkthrough only built one Knowledge Object
  end-to-end, so two real, source-evidenced relationships — `RI-15`
  citing the Kernel, `RI-7` deriving from `RI-5`'s method — were never
  actually proposed; the gap was already disclosed in general terms,
  this re-audit made it concrete).
- **Discovered defects**: none specific to this dataset beyond `F-3`/
  `F-4`, both cross-cutting.
- **Suggested corrections**: `F-3` fixed (see "Corrections applied,"
  below). `F-4` is a coverage/completeness note, not a logic defect — no
  architecture change follows from it; it is a reminder that a real
  Knowledge Base build needs to cover a dataset's full finding set, not
  a sample.
- **Confidence**: **High** — the deepest-tested dataset by far (77
  entries, an existing full walkthrough, plus this re-audit).

### Dataset 2 — Project documentation

**Verdict: PASS.** Real run: `STRESS-RUN-0003-recovery-report.md` →
`CURATION-0003.md`.

- **Weaknesses found**: `F-1` — none of `RELATIONSHIP-ONTOLOGY.md`'s
  seven types could honestly express `ADR-0004`'s own stated relationship
  to `ADR-0003` ("amends... the property itself is unchanged; only which
  filesystem it lives on depends on which session is running" — a
  partial, single-property revision, not a whole-object supersession,
  dependency, or extraction).
- **Discovered defects**: `F-1`, a real ontology-completeness gap,
  surfaced specifically because this dataset (unlike the diary) contains
  *source-declared* relationships (`Depends on` / `Amends` headers)
  precise enough to show the ontology's boundary.
- **Suggested corrections**: `F-1` fixed (see below).
- **Confidence**: **High** for the specific finding (the source text is
  unambiguous and was quoted directly); **Moderate** for this dataset's
  overall coverage (only 4 files, each read once, no promotion or
  contradiction case with real stakes — the ADRs were too well-disciplined
  by this repository's own existing conventions to produce a contradiction
  or false-duplicate case, which is itself informative but limits how
  hard this dataset could stress those two specific mechanisms).

### Dataset 3 — Research notes/investigations (KOD)

**Verdict: PASS.** Real run: `STRESS-RUN-0004-recovery-report.md` →
`CURATION-0004.md`.

- **Weaknesses found**: `F-2` — `KNOWLEDGE-OBJECT-SPEC.md`'s `maturity`
  definition did not specify what counts as "one source" when a corpus
  spans multiple files scanned in one run, a genuine ambiguity the
  diary (unambiguously one archive) never exposed.
- **Discovered defects**: `F-2`. Two deliberate traps in this dataset
  (a near-empty excavation progress file, a blank Knowledge Object
  template) were both handled correctly — no hallucinated content, no
  fabricated Knowledge Object from a bare schema. One genuine near-
  duplicate (`"reality is the final arbiter"`, two documents) was
  correctly identified and, unlike the first walkthrough's `KMP-0001`,
  correctly recommended **for** merging — confirming the merge logic is
  not systematically biased toward "always decline."
- **Suggested corrections**: `F-2` fixed (see below).
- **Confidence**: **High** — this dataset produced the richest set of
  distinct test conditions (hallucination-avoidance, a positive merge
  recommendation, a cross-repository naming-collision check, an
  undated-source handling check, and `F-2` itself).

### Dataset 4 — Operational material (trust-engine)

**Verdict: PASS.** Real run: `STRESS-RUN-0005-recovery-report.md` →
`CURATION-0005.md`.

- **Weaknesses found**: none at the AG-003 architecture level. One
  deliberate trap (a Latin/Cyrillic `M1`/`М1` data-identity collision
  *inside the audited system*, not between two of AG-003's own
  Knowledge Objects) was correctly recognized as a single finding, not
  mistaken for two duplicate Knowledge Objects needing a merge proposal
  — the specific "false merge proposal" failure mode this dataset was
  built to test did not occur.
- **Discovered defects**: none new. This dataset also surfaced a real
  **AG-002-level** rigor point (not an AG-003 architecture defect): a
  migration report's `PASS`/`0 failed checks` had to be read carefully
  to confirm it meant "the migration script correctly excluded known-bad
  rows," not "the audit's underlying data-quality issues were fixed" —
  a genuine over-inference risk that was checked and avoided, worth
  recording as a positive result under pressure rather than a defect.
- **Suggested corrections**: none.
- **Confidence**: **Moderate** — only 3 files, and this dataset did not
  exercise a promotion proposal or a genuine contradiction case (none
  existed in the material); its main contribution was the false-merge
  trap and the audit/migration distinction, both of which held.

## Cross-Dataset Analysis

**Does AG-003 behave consistently across all four document types? No —
not fully, and the inconsistency has an identified, specific cause, not
a diffuse one.**

The **governance layer** — never merges, never promotes, never resolves
a contradiction, never invents a citation, always produces a proposal a
human must act on — behaved identically and without exception across
all four structurally different datasets (narrative diary, header-linked
governance documents, undated multi-file research corpus, dense tabular
audit data). No boundary violation occurred anywhere in this test.

The **relationship- and maturity-detection layers** did not generalize
cleanly, because real source material presents the evidence those layers
need in at least three structurally different shapes, and the
architecture (designed and first tested against the diary alone) had
only been proven against one of them:

1. **Diary (dataset 1)**: relationships inferred from narrative
   repetition and elapsed time — the shape the architecture was
   originally designed against.
2. **Governance documents (dataset 2)**: relationships **explicitly
   declared** in source headers (`Depends on`, `Amends`) — a stronger
   evidentiary situation than inference, but one that exposed `F-1`
   because the ontology's seven types were built with inferred,
   whole-object relationships in mind, not source-declared, partial-scope
   ones.
3. **Research corpus (dataset 3)**: relationships inferred from logical
   presupposition across **multiple files in one repository**, exposing
   `F-2` — a granularity question ("what is one source?") that a
   single-archive diary could never have raised.
4. **Operational reports (dataset 4)**: relationships inferred from
   **shared structural identifiers** (exact table names) rather than
   prose or headers — a third inference shape that worked without
   incident, but was explicitly flagged at lower confidence
   (`REL-S4-01`) precisely because it is the least textually direct of
   the three inference methods tested.

**Architectural cause**: `RELATIONSHIP-ONTOLOGY.md` and
`KNOWLEDGE-OBJECT-SPEC.md` were both written and adversarially reviewed
against a single, richly-narrative source (the diary) before this
stress test. That review was genuinely rigorous within its own scope
(the first `ADVERSARIAL-REVIEW-0001.md` found and fixed three real
defects), but a single source, however deeply tested, cannot expose a
gap that only becomes visible when a *structurally different* source is
introduced — `F-1` and `F-2` are exactly this kind of gap: neither was
inconsistent with anything the diary showed; both are cases the diary
was structurally incapable of showing.

**Minimal corrections proposed and applied** (all three below are
already reflected in the architecture files as of this report, each with
an inline citation back to this document):

- **`F-1`** — `RELATIONSHIP-ONTOLOGY.md`'s `supersedes` type now
  explicitly supports being scoped to a named property rather than an
  entire Knowledge Object, with a stated requirement that a scoped
  proposal name the specific property. This resolves `ADR-0004`/
  `ADR-0003`'s case without adding an eighth type — the conservative
  option, chosen over a new type because the existing `supersedes`
  semantics ("a later, revised version of the same underlying claim")
  already fit once scope is made explicit.
- **`F-2`** — `KNOWLEDGE-OBJECT-SPEC.md`'s `maturity` field now states a
  source-granularity rule: one repository/archive scanned in one run is
  one source, regardless of file count. Resolves `KO-S3-01`'s ambiguity
  conservatively, consistent with `KO-0001`'s existing precedent, rather
  than introducing a new counting rule.
- **`F-3`** — `CURATION-PROTOCOL.md` Stage 5 now requires a cycle check
  before proposing a `supersedes` or `depends_on` edge, specifically
  because these two types (unlike the other five) encode a one-
  directional authority claim that a cycle would make incoherent. Found
  through active adversarial reasoning about the task's own "circular
  relationships" failure category, not from an actual instance in any
  dataset — recorded honestly as a structural gap closed pre-emptively,
  not a bug that produced a wrong output anywhere in this engagement.

**`F-4`** (concrete missing relationships in the first walkthrough) is
explicitly **not** treated as requiring an architecture change — it is a
coverage/completeness fact about how much of `PILOT-RUN-0002`'s material
the first walkthrough actually turned into Knowledge Objects (one, by
design, for a demonstration), not a defect in what the architecture
allows or forbids.

## Freeze Recommendation

**READY WITH MINOR CHANGES.**

Not `READY FOR FROZEN`, because three real, evidence-linked gaps were
found in this test (`F-1`, `F-2`, `F-3`) — freezing before they were
fixed would have locked in known, reproducible ambiguity. Not
`NOT READY`, because every governance boundary (the part of the
architecture that actually matters most — never merge/promote/resolve
automatically, never invent, never lose provenance) held without
exception across four structurally different real datasets, and all
three found gaps were narrow, specification-level clarifications
(a type-scoping rule, a source-granularity rule, a cycle check) rather
than redesigns — each fixed in a few lines, each traceable to one exact
piece of evidence, none contradicting or walking back any prior decision.

The minor changes are the three corrections already applied and
described above; no further changes are recommended before a freeze
decision, though `F-4`'s coverage point means a frozen architecture
should still expect its *first real production Knowledge Base build* to
surface further, currently-unknown gaps once it covers a dataset's full
finding set rather than a sample — freezing the architecture is not the
same claim as declaring the Knowledge Base itself complete.

## Provenance

Recovery reports: `../../ai-organization/employees/
AG-002-discovery-archaeologist/runs/STRESS-RUN-0003-recovery-report.md`,
`STRESS-RUN-0004-recovery-report.md`, `STRESS-RUN-0005-recovery-report.md`,
and the existing `PILOT-RUN-0002-recovery-report.md`. Curation passes:
`CURATION-0003.md`, `CURATION-0004.md`, `CURATION-0005.md`,
`DATASET-1-REAUDIT.md`. Manifests: `../../../../reality-inbox/manifests/
RI-0003.md`, `RI-0004.md`, `RI-0005.md`, `RI-0002.md`.
