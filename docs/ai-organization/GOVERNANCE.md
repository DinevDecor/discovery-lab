# AI Organization — Governance (Freeze Lifecycle)

**Status: ACCEPTED, 2026-07-24**, via direct task instruction ("Discovery
Lab — Freeze Release 1.0"), the same acceptance pattern used for
`ADR-0001`–`ADR-0004`. Formalizes the lifecycle AG-002 and AG-003 both
actually went through on their way to `../releases/1.0/RELEASE-1.0.md` —
this document generalizes real precedent, it does not invent an
untested process.

## Relationship to `HIRING-LIFECYCLE-DRAFT.md`

**This document and `HIRING-LIFECYCLE-DRAFT.md` govern two different,
independent axes, and neither substitutes for the other.**

- `HIRING-LIFECYCLE-DRAFT.md` governs **organizational trust**: whether a
  Role is `Candidate → Prototype → Probation → Trusted → Retired`. That
  axis requires real run volume, independent review, and an explicit
  human adoption decision.
- **This document governs architectural stability**: whether a Role's
  own governing documents (`CONTRACT.md`, `ROLE.md`, and everything else
  in its folder) are settled enough to stop changing without new
  evidence. A Role can be `FROZEN` on this axis while remaining
  `Prototype (not adopted)` on the other — exactly AG-002's and AG-003's
  status as of Release 1.0. Freezing a Role's architecture is not an
  adoption decision, and this document confers no adoption authority.

## The mandatory lifecycle

Every future Discovery Lab agent (a new `AG-NNN` Role, or a major
revision to an existing one — see "Versioning," below) must pass through
every stage below, in order, before it may be marked `FROZEN`. No stage
may be skipped, and no stage may be self-certified by the same act that
produced the artifact under review.

```
Idea
  ↓
Draft
  ↓
Internal Review
  ↓
Adversarial Review
  ↓
Reality Stress Test
  ↓
Freeze Recommendation
  ↓
FROZEN
```

1. **Idea** — a Role is proposed: a mission, a boundary against
   neighboring Roles and neighboring ecosystem projects (KOD,
   generative-discovery-engine, trust-engine), and an explicit list of
   what it must never do. Not yet any files.
2. **Draft** — the Role's full document set is written (at minimum:
   `CONTRACT.md`, `ROLE.md`, `INPUTS.md`, `OUTPUTS.md`, `LIMITATIONS.md`,
   `CHECKLIST.md`, `METRICS.md`, `PROMPT.md`, `STATUS.yaml`,
   `HISTORY.md`, plus whatever role-specific specification documents the
   Role's own mission requires — AG-003's `KNOWLEDGE-OBJECT-SPEC.md`,
   `LIFECYCLE.md`, `RELATIONSHIP-ONTOLOGY.md`, `PROMOTION-RULES.md`,
   `REVIEW-PROTOCOL.md`, and `CURATION-PROTOCOL.md` are the precedent
   for what "role-specific" means). Status: `prototype`, version `0.1`.
3. **Internal Review** — the Draft is checked against this repository's
   own already-established discipline: evidence rules, escalation
   values, boundary/limitation lists, terminology disambiguation against
   KOD/GDE/trust-engine's reserved words (`PROP-0001` ground rule 1).
   May be performed by the same session that wrote the Draft — this
   stage is a consistency check against fixed, external precedent, not
   an adversarial search for the Draft's own novel defects.
4. **Adversarial Review** — an active attempt to find defects the Draft
   introduces on its own terms: unreproducible formulas, unmechanized
   claims, internally inconsistent field definitions, missing
   disambiguation. Must produce a written record of every defect found,
   whether fixed immediately or left open, and a stated verdict.
   Independence from the Draft's author is preferred but, per precedent
   (`ADVERSARIAL-REVIEW-0001.md`), not required to proceed — a
   same-session review must **disclose** that fact as a limitation of
   its own verdict, not omit it.
5. **Reality Stress Test** — the Role is actually run (not
   demonstrated) against **real** data from **more than one structurally
   different source**, with an explicit goal of falsifying the
   architecture, not confirming it. Must actively hunt for the specific
   failure modes relevant to the Role's own function (for a recovery/
   curation Role: hallucinated findings, false merges, missed
   contradictions, confidence inflation, circular relationships,
   duplicated provenance — see `../proposals/
   AG-003-reality-stress-test/REALITY-STRESS-TEST-REPORT.md` for the
   worked precedent). Every defect found must be fixed with a minimal,
   evidence-linked correction, or explicitly recorded as an accepted,
   named limitation — never silently dropped.
6. **Freeze Recommendation** — the Reality Stress Test concludes with
   exactly one of `READY FOR FROZEN`, `READY WITH MINOR CHANGES`, or
   `NOT READY`. This is Discovery Lab's own proposal, per Principle 0 —
   it does not, by itself, change any Role's `status` field. A
   `NOT READY` verdict returns the Role to Draft; `READY WITH MINOR
   CHANGES` requires the named changes applied and re-verified before
   proceeding; only `READY FOR FROZEN` (or a verified `READY WITH MINOR
   CHANGES`) may proceed to the next stage.
7. **`FROZEN`** — an explicit human decision (a direct instruction, or a
   recorded acceptance in the same pattern as `ADR-0001`–`ADR-0004`)
   accepts the Freeze Recommendation. Only this step changes a Role's
   `status` field to `frozen` and its `version` to the next major number
   (`1.0` for a first freeze). Discovery Lab does not freeze itself —
   the same "who may run the process, and who may not decide it" rule
   `HIRING-LIFECYCLE-DRAFT.md` already states for `Trusted` applies
   identically here.

## Versioning

`MAJOR.MINOR` (e.g. `0.1` pre-freeze, `1.0` at first freeze, `1.1` for a
minor revision, `2.0` for a major revision). No patch/build number —
this repository has never needed one, and adding one without a
demonstrated need would repeat the premature-abstraction error
`HIRING-LIFECYCLE-DRAFT.md` already declined to make for candidate
tiers.

### Bug fixes

A correction to a place where the Role's own governing documents
disagreed with themselves, or with reality, in a way the Draft never
intended (a broken relative path, a stale cross-reference, a value that
no longer matches `STATUS.yaml`). **No version bump, no lifecycle
re-entry** — corrected in place, recorded in `HISTORY.md`, cited to the
specific inconsistency found. Precedent: this release's own correction
of AG-003 `METRICS.md`'s stale "no real run as of v0.1" line to match
actual `STATUS.yaml` history.

### Clarifications

A wording change that makes an existing rule easier to apply correctly
without changing what the rule actually requires (e.g. adding a worked
example, tightening an ambiguous sentence). **No version bump.** If a
clarification reveals the existing rule was actually ambiguous enough to
produce different real behavior depending on reading — as `F-1`/`F-2`/
`F-3` did during the Reality Stress Test — it is a **minor revision**
(below), not a clarification, because real behavior changed, even if the
document's stated intent did not.

### Minor revisions (version bump: `X.Y → X.(Y+1)`)

A change that fixes a real, evidence-linked defect (per an Adversarial
Review or Reality Stress Test) without changing the Role's `CONTRACT.md`
scope, its Responsibilities list, or its Explicit prohibitions list.
Precedent: `F-1`, `F-2`, `F-3` from the Reality Stress Test — each a
targeted correction to one document's own internal rule, none touching
what AG-003 is authorized to do. **Requires**: the specific evidence
that motivated the change, cited inline in the corrected document (as
`F-1`–`F-3` are); no full Reality Stress Test re-run is required, but
the specific corrected mechanism should be re-verified against the
evidence that exposed it.

### Major revisions (version bump: `X.0 → (X+1).0`)

A change to `CONTRACT.md`'s Scope of authority, the Role's
Responsibilities list, its Explicit prohibitions, its Inputs, or its
Outputs — anything that changes what the Role is authorized to do, not
merely how precisely it does it. **Requires the full lifecycle again**,
starting at Draft — a major revision is a new Draft of the same Role,
not a patch. A `FROZEN` Role under major revision reverts to `prototype`
status for the revision's duration; the prior frozen version remains on
record, unedited, per "Deprecation," below.

### Deprecation

A `FROZEN` Role (or version) may be marked `DEPRECATED` by an explicit,
recorded human decision — never inferred from disuse, never a side
effect of a newer version's freeze. `DEPRECATED` is a note on the
architecture-stability axis, independent of `HIRING-LIFECYCLE-DRAFT.md`'s
own `Retired` (the adoption-axis equivalent) — a Role's files and
`STATUS.yaml` are preserved exactly as they were, per that document's
own retirement rule; nothing is deleted. If a successor version exists,
the deprecated version's `STATUS.yaml` gains a `superseded_by` pointer
to it; if none exists, the deprecation stands on its own.

## What this document does not do

- It does not itself freeze, adopt, retire, or deprecate any Role — it
  defines the process; a human decision executes each transition.
- It does not modify `HIRING-LIFECYCLE-DRAFT.md`, ORB's protocol, or
  AG-003's own `REVIEW-PROTOCOL.md` — each governs its own thing, cited
  here, not restated or overridden.
- It does not retroactively require AG-001 (still `Prototype`, never
  stress-tested) to pass this lifecycle to remain as it is — this
  document governs future freezes and future major revisions; it is not
  applied backward to invalidate a Role that predates it.
