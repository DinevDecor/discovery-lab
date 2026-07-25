# Discovery Lab — Validation History (AG-002 / AG-003, through Release 1.0)

A chronological, append-only record. Entries are never edited or removed
once written — only appended, per the same convention already used in
both Roles' own `HISTORY.md` files. All dates are 2026-07-24; this
repository's entire history to date happened within one calendar day,
across many separate sessions and tasks.

## 1. AG-002 Discovery Archaeologist created (v0.1)

Commit `01656e5`. Full document set created (`CONTRACT.md`, `ROLE.md`,
`INPUTS.md`, `OUTPUTS.md`, `LIMITATIONS.md`, `CHECKLIST.md`,
`METRICS.md`, `RUN-PROTOCOL.md`, `PROMPT.md`, `STATUS.yaml`,
`HISTORY.md`). Status set to `prototype`, not the "production-ready"
wording of the requesting task, to preserve `HIRING-LIFECYCLE-DRAFT.md`'s
lifecycle discipline — the first internal-review-shaped decision in this
Role's history, made at creation, not after the fact.

## 2. PILOT-RUN-0001 (real, first run)

Immediately after creation. Source: the `project-memory` archive.
Recovered 7 ideas, 4 repeated themes, 5 idea-evolution timelines, 2
forgotten ideas, 4 candidate investigations, 2 contradictions, 6 open
questions. `runs_completed: 1`.

## 3. PILOT-RUN-0002, first attempt — correctly BLOCKED

Commit `a8031c6`. The named diary source could not be reached (Google
Drive MCP connector, `-32003` approval gate). The run halted at Stage 1
per its own Stop rule rather than substituting a different source. No
Recovery Report produced; `runs_completed` not incremented — a real
negative result, not smoothed over.

## 4. Infrastructure Sprint 01 and ADR-0001 (Human Authority Gates)

The `-32003` blocker was diagnosed as a platform limitation, not a
defect in this repository. `ADR-0001` introduced the Human Authority
Gate concept and a four-category Organizational Principle, accepted
2026-07-24 (architecture only; migration explicitly deferred).

## 5. AG-002 memory access resolved; `MIRROR-VERIFY-0001`

Commit `0e12c85`. `ADR-0002` (Human-Mediated Export Bridge) accepted and
implemented; `memory/` established. Verified via `MIRROR-VERIFY-0001`
against a labeled synthetic fixture — the pipeline mechanics were real,
the content was not. `runs_completed: 2`.

## 6. Reality Inbox created; `ADR-0003` freeze; `REALITY-VERIFY-0001`

The organization-wide intake layer (`reality-inbox/`) built and
verified, then frozen as architecture (`ADR-0003`) with an explicit
change-governance rule. `REALITY-VERIFY-0001` verified the full cycle
against a labeled synthetic fixture. `runs_completed: 3`.

## 7. `ADR-0004` — local-Drive-synced intake, correctly BLOCKED on verification

Local-filesystem intake designed and accepted as architecture; one real
verification attempt from a remote session correctly returned `BLOCKED`
at its first precondition (no local filesystem bridge exists in a remote
container) — including a documented negative result (`mkdir` succeeding
is not evidence of Drive access) recorded specifically so it could not
be mistaken for progress.

## 8. PILOT-RUN-0002, real diary — partial, by design

Commit `44def99`. The real diary arrived via GitHub upload (commit
`a3d4dcb`) into `reality-inbox/📥 DROP HERE/`. Processed as `RI-0002`.
Four organizational entries read and extracted; the run **paused**
rather than reading 58 personal entries without explicit policy
guidance — a genuine human-decision point, not a technical block.
`runs_completed: 4`.

## 9. "AG-002 Personal Diary Processing Policy" decided

A human decision: AG-002 may read the entire diary; personal content is
not automatically knowledge; extract only durable knowledge with
minimum necessary quotation; never stop processing for personal content.

## 10. PILOT-RUN-0002 completed

Commit `8240cf4`. All 77 diary entries read under the new policy: 19
organizational entries extracted with citations (including `RT-3`'s
five-appearance "nature as a library of architectures," the single
strongest repeated-idea signal in the archive), 47 personal entries
correctly screened to `NO KNOWLEDGE EXTRACTED`, 6 empty, 5
originally-ambiguous entries resolved. `RI-0002.status: COMPLETED`.
`runs_completed` not incremented again (completion of the same run, not
a new one).

## 11. AG-003 Knowledge Curator designed (v0.1) — internal review

Commit `e0bd346`. Full document set created against an explicit "DRAFT —
architecture only" constraint, including the Knowledge Object spec
(exact required fields, a concrete confidence formula), a two-track
lifecycle (`status` formal/human-gated, `maturity` informal/automatic),
a seven-type relationship ontology, non-automatic promotion rules, a new
"Knowledge Review" proposal-content review process (distinct from ORB's
conduct review, KOD's Under Review, and GDE's Critical Review), and a
nine-stage curation protocol. Internal design review consisted of
cross-checking every new document against AG-001's and AG-002's own
established conventions (evidence rules, escalation values, boundary
lists) before any adversarial pass began.

## 12. Adversarial self-review — 3 defects found and fixed

`docs/proposals/AG-003-knowledge-curator-walkthrough/
ADVERSARIAL-REVIEW-0001.md`, same commit. Conducted by the same session
that designed the architecture (disclosed, not hidden — flagged as the
review's own most important limitation). **Found and fixed during the
review itself**:

| # | Defect | Fix |
|---|---|---|
| 1 | `confidence` had no reproducible formula | Added a concrete multiplicative formula to `KNOWLEDGE-OBJECT-SPEC.md` |
| 2 | Knowledge Merge Proposal reversibility was asserted, not mechanized | Added `merged_from_ko` provenance tagging to `OUTPUTS.md`/`LIFECYCLE.md` |
| 3 | `derived_from` was defined twice (lineage field vs. relationship type) with no sync rule | Added an explicit "deliberately not synced" rule to `KNOWLEDGE-OBJECT-SPEC.md` |

**Recorded as open, not fixed in that review** (four further findings —
see item 15 below for what the Reality Stress Test did and did not
resolve of these):

| # | Finding |
|---|---|
| 4 | `maturity: Convergent`'s "independent source" test is exploitable by re-scanning the same source in a second run |
| 5 | The `Validated → Core` 90-day/3-run threshold is admittedly invented, unexercised |
| 6 | `CI-NNNN` numbering shared with AG-002 has no collision-prevention mechanism |
| 7 | The walkthrough's own "isolated node" Gap Report claim was asserted from a manual read, not a computed graph (only one Knowledge Object was built end-to-end) |

Verdict: **APPROVE WITH OPEN ITEMS** — explicitly not independent.

## 13. First worked-example walkthrough

Same commit. Demonstrated the architecture against `PILOT-RUN-0002`
(inline, not filed to a real store): `KO-0001`, a declined merge
proposal (`KMP-0001`), a flagged relationship proposal (`REL-0001`), a
one-step Core Principle Proposal (`CPP-0001`), a declined contradiction
escalation (`CONTRADICTION-CHECK-0001.md`), a Knowledge Evolution Report
(`KEV-0001`), and a Gap Report (`GAP-0001`). `runs_completed: 0`
(demonstration, not a run — updated for real at item 15).

## 14. Real intent stated: falsify, not confirm

The Reality Stress Test task was explicitly framed as a falsification
exercise ("the goal is to falsify AG-003, not to prove it correct"),
distinct in kind from the design-time adversarial review, which tested
the architecture against its own single source of origin.

## 15. AG-003 Reality Stress Test — 3 defects found and fixed, 1 coverage note recorded

Commit `652db3d`. Four structurally different real datasets, real
AG-002 → AG-003 runs (except dataset 1, re-audited not re-run):

| Dataset | Source | Real files | Verdict |
|---|---|---|---|
| 1 — Personal diary | `PILOT-RUN-0002` (existing) | 77 entries | PASS (re-audit) |
| 2 — Project documentation | This repository's own `docs/adr/ADR-0001`–`ADR-0004` | 4 | PASS |
| 3 — Research/investigation | `kod` repository (`EX-0001`, `ART-0001`, `kod`'s own `ADR-0001`–`0003`, `KNOWLEDGE_OBJECT_TEMPLATE.md`) | 7 | PASS |
| 4 — Operational material | `trust-engine` repository (audit, migration, review reports) | 3 | PASS |

**Found and fixed**:

| # | Defect | Dataset | Fix |
|---|---|---|---|
| F-1 | `supersedes` couldn't express a real "amends one property, leaves rest unchanged" relationship (`ADR-0004`/`ADR-0003`) | 2 | Scoped `supersedes` to a named property in `RELATIONSHIP-ONTOLOGY.md` |
| F-2 | `maturity`'s "one source" was undefined at file-vs-repository granularity | 3 | Added a source-granularity rule to `KNOWLEDGE-OBJECT-SPEC.md` |
| F-3 | No cycle check for `supersedes`/`depends_on` proposals | 1 (found via active reasoning, no actual instance) | Added a cycle check to `CURATION-PROTOCOL.md` Stage 5 |

**Recorded as a coverage note, not fixed** (no architecture change):

| # | Finding |
|---|---|
| F-4 | Two concrete relationships (`RI-15`↔`RI-1`/`RI-2`, `RI-7` `derived_from` `RI-5`) the first walkthrough's one-Knowledge-Object scope had missed — confirms item 12's finding 7 was real, does not change the architecture |

**Deliberate traps, all handled correctly**: two near-empty KOD sources
yielded no fabricated content; a Latin/Cyrillic `M1`/`М1` data-identity
collision in a real trust-engine audit was correctly recognized as one
finding, not a false duplicate/merge case.

`runs_completed`: AG-002 `4 → 7`, AG-003 `0 → 3` (the diary re-audit is
not counted as a new run for either Role).

**Freeze recommendation returned**: `READY WITH MINOR CHANGES` — the
three `F-1`/`F-2`/`F-3` corrections are those changes, applied in the
same commit that reported them.

## 16. A discrepancy this document is recording honestly, found while writing it

Writing this ledger side by side with item 12's still-open finding 4 and
item 15's `F-2` fix surfaced a real inconsistency, not previously
noticed: `F-2`'s fix to `KNOWLEDGE-OBJECT-SPEC.md` states `Convergent`
is satisfied by *"two separate repositories/archives, **or two separate
AG-002 runs over the same one**"* — the second clause permits exactly
the re-scan loophole item 12's finding 4 flagged as exploitable (a
second run over unchanged material inflating `maturity` without new
evidence). `F-2` closed the file-granularity ambiguity it was written
for; it did not close, and was never intended to close, finding 4's
separate concern. **Not fixed as part of this freeze** — this release's
own task explicitly forbids redesign ("do not introduce new features"),
and a real fix here (most likely: requiring a run to cover materially
new source content, not just a new run ID, before counting toward
`Convergent`) is itself a small design decision that deserves its own
evidence-linked pass, not a rushed edit folded into a governance freeze.
Recorded here, and carried into `RELEASE-1.0.md`'s "Known limitations"
and `LESSONS-FROM-V1.md`, specifically so it is not lost.

## 17. Release 1.0 — final freeze decision

This document, `RELEASE-1.0.md`, `GOVERNANCE.md`, `ARCHITECTURE-MAP.md`,
and `LESSONS-FROM-V1.md` produced; both Roles' `STATUS.yaml` and
document-set headers updated to `version: 1.0`, `status: frozen`;
`EMPLOYEE-REGISTRY.md` updated. Freeze accepted 2026-07-24 via direct
task instruction, per `RELEASE-1.0.md`'s own Acceptance line.
