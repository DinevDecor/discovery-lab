# ADR-0001 Migration Plan — Human Authority Gates

Status: **PLANNED / NOT STARTED**
Date: 2026-07-24
Authorizes: nothing by itself. This document plans the implementation of
`ADR-0001-human-authority-gates.md` §8; it does not execute any step in
it. Per the acceptance decision: *"Do not begin the migration yet."*
Execution of any step below requires a separate, future, explicit
authorization.

## How to read this document

Four migration items were named in `ADR-0001-human-authority-gates.md`
§8 when the ADR was drafted. This plan expands each into ordered,
verifiable steps — owner, prerequisite, action, expected result,
verification — in the same format `INFRA-SPRINT-01-report.md`'s
Connection Plan already used. No step here has been performed. This
document's own completion criterion is that it exists and is accurate,
not that any migration has happened.

---

## Migration Item 1 — AG-002 terminology (`RUN-PROTOCOL.md`, `INPUTS.md`)

Decide whether `INSUFFICIENT ACCESS` and `BLOCKED` should be replaced by,
or mapped onto, the HAG report format (ADR-0001 §4).

| Step | Owner | Prerequisite | Action | Expected result | Verification |
|---|---|---|---|---|---|
| 1.1 | Petko | ADR-0001 accepted (done) | Decide the mapping: does every `INSUFFICIENT ACCESS` / `BLOCKED` case become a HAG report, or only the subset that is actually a human-authorization gate (some `INSUFFICIENT ACCESS` cases — e.g. a source that was simply never created — are not HAGs at all)? | A short decision recorded (e.g. as an addendum to this plan or a new note) distinguishing "missing source" from "gated source" | The recorded decision names both cases explicitly and gives at least one example of each from this repository's own history (`PILOT-RUN-0001`'s missing diary vs. `PILOT-RUN-0002`'s gated Drive connector qualify as one of each) |
| 1.2 | Implementer session (steward) | 1.1 | Draft the actual edit to `RUN-PROTOCOL.md`'s Stop rule and `INPUTS.md`'s rule, adding HAG-report language where 1.1 decided it applies, without removing the existing `INSUFFICIENT ACCESS` case for genuinely missing sources | A reviewable diff against both files | `git diff --check` clean; every new cross-reference verified with `realpath`/`test -f` per this repository's existing discipline |
| 1.3 | Petko | 1.2 | Review and approve the diff | Files updated in AG-002's own directory for the first time since its creation | `git log` shows the commit; `HISTORY.md` gets an entry recording the protocol change (append-only, per existing convention) |

## Migration Item 2 — Memory Source Registry schema migration

Replace the single `status` field with the two independent axes
(Connectivity, Authority) from ADR-0001 §5, and resolve §5.2's open
question (where `deprecated` fits).

| Step | Owner | Prerequisite | Action | Expected result | Verification |
|---|---|---|---|---|---|
| 2.1 | Petko or a designated Curator | ADR-0001 accepted (done) | Resolve §5.2: is `deprecated` a third orthogonal `lifecycle` field, or a fifth `Authority` value? | A decision recorded in this plan or a follow-up note | Decision is unambiguous enough that 2.2 can be written without further judgment calls |
| 2.2 | Implementer session (steward) | 2.1 | Draft the schema edit to `MEMORY-SOURCE-PROTOCOL.md` (schema table, per-type locator shapes unaffected) and `SOURCE-REGISTRATION-TEMPLATE.md` | A reviewable diff | `git diff --check` clean; template's placeholder fields still all present and consistent with the new schema |
| 2.3 | Implementer session (steward) | 2.2 | Re-express `MEM-001` and `MEM-002` in `MEMORY-SOURCE-REGISTRY.md` under the new two-axis schema, using the worked mapping already given in ADR-0001 §5.1 (`MEM-001`: Connected/Authorized; `MEM-002`: Connected/Pending Human Approval) | Registry entries carry `connectivity` and `authority` fields instead of `status` | Both old and new values are traceable — no information is silently dropped in the rewrite (e.g. `MEM-002`'s `unverified` note about the `-32003` evidence is preserved, not deleted) |
| 2.4 | Petko | 2.3 | Review and approve | Registry now reflects ADR-0001's architecture in practice, not just in the ADR's own worked example | `git log` on `MEMORY-SOURCE-REGISTRY.md` shows the migration commit |

## Migration Item 3 — HAG Log

Create an append-only log of HAG encounters, mirroring
`EMPLOYEE-REGISTRY.md` / `ORB-REGISTRY.md` / `MEMORY-SOURCE-REGISTRY.md`'s
existing convention, to hold reports in the ADR-0001 §4 format.

| Step | Owner | Prerequisite | Action | Expected result | Verification |
|---|---|---|---|---|---|
| 3.1 | Implementer session (steward) | **At least one real HAG has actually been reported** under the ADR-0001 §4 format (not before — creating this file ahead of a first real entry would repeat the "no invented starting values" mistake `MEMORY-SOURCE-PROTOCOL.md` already argues against) | Create `docs/adr/HAG-LOG.md` seeded with that one real entry | A registry file with exactly one real, evidence-backed row | Every field in ADR-0001 §4 (Resource / Requested action / Blocking authority / Evidence / Exact human action / Expected result / Resume point) present and cited |
| 3.2 | Whoever encounters a HAG thereafter (human or AI employee) | 3.1 | Append a new entry per encounter | Log grows append-only, never edited retroactively | `git log -p` on the file shows only additions, no rewritten history, matching the same discipline already used elsewhere in this repository |

**Item 3's own prerequisite is the reason this plan does not schedule a
date for it** — it is gated on real evidence this plan cannot manufacture,
not on Petko's authorization alone.

## Migration Item 4 — Automatic resume (ADR-0001 §3, item 6)

"Resume automatically after authorization if possible" — no mechanism for
this exists anywhere in this repository or in the session tooling it runs
on.

| Step | Owner | Prerequisite | Action | Expected result | Verification |
|---|---|---|---|---|---|
| 4.1 | Petko | ADR-0001 accepted (done) | Determine whether automatic resume is even possible from *this* repository's side, or whether it depends entirely on platform capabilities outside discovery-lab's control (per `INFRA-SPRINT-01-report.md` §1.4, the approval gate itself lives in the session/platform layer, not in this repository) | A scoping answer: "buildable here," "requires a platform capability we don't have," or "requires a capability that exists but isn't wired up" | The answer is falsifiable — it names a specific mechanism (e.g. a Routine re-fired on a schedule, per `list_triggers`/`create_trigger`) or specific platform gap, not a general aspiration |
| 4.2 | Implementer session (steward) | 4.1 concludes "buildable here" | Design (not build) the specific mechanism | A short design note | Reviewed by Petko before any code/automation is written, consistent with `MEMORY-SOURCE-PROTOCOL.md`'s existing rule that this kind of infrastructure is "not an automated connector" without explicit governance sign-off |

This item is the least defined of the four and is likely to reveal, on
investigation, that it is bounded by the same platform layer
`INFRA-SPRINT-01-report.md` already found responsible for the approval
gate itself — flagged here rather than assumed solvable.

---

## Sequencing note

Items 1 and 2 are independent of each other and of Item 4. Item 3 cannot
start before a real HAG is reported under the new format — which could
happen as early as the very next Google Drive access attempt, if it is
still gated when re-tried (see `INFRA-SPRINT-01-report.md` and the
Infrastructure Sprint 01 continuation this ADR's acceptance also
authorized). No step in this plan is scheduled to begin until Petko gives
that separate, future authorization referenced at the top of this
document.
