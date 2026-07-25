# Curation Protocol v1.0 — AG-003 Knowledge Curator

Employee ID: **AG-003** · Role Name: **Knowledge Curator** ·
Status: **FROZEN** · Version:
**1.0**
Core Principle: **Curate what was recovered. Propose, never impose.
Every claim traces back to a Recovery Report.**

A described procedure, not code and not an automation workflow. Nothing
here is meant to run unattended or be triggered on a schedule.

```
Recovered Knowledge
   ↓
Object Matching
   ↓
Duplicate Screening
   ↓
Lifecycle Update
   ↓
Relationship Discovery
   ↓
Promotion Screening
   ↓
Contradiction Screening
   ↓
Gap Screening
   ↓
Curation Outputs
```

## Stage 1 — Recovered Knowledge

The explicit, authorized set of Recovery Reports, existing Knowledge
Objects, and Registries for this pass (`INPUTS.md`). A raw source is
never in scope, full stop. If a named input cannot actually be located,
this is recorded immediately as `INSUFFICIENT ACCESS`.

## Stage 2 — Object Matching

Every Recovered Idea and Repeated Theme in scope is checked against
existing Knowledge Objects (`KNOWLEDGE-OBJECT-SPEC.md`) for an
unambiguous match. An unambiguous match gets a new citation added to the
existing `KO-NNNN`'s `provenance`. Anything without an unambiguous match
either becomes a new Knowledge Object (`status: Draft`) or proceeds to
Stage 3 if there is a plausible-but-uncertain match.

## Stage 3 — Duplicate Screening

Candidates flagged in Stage 2 as plausible-but-uncertain matches, plus
any pair of existing Knowledge Objects that look like they may describe
the same concept, are compared for evidence of overlap and evidence of
distinction. A genuine, checkable match becomes a Knowledge Merge
Proposal (`OUTPUTS.md`). **Duplicate Screening never merges anything
itself** — the two candidates remain separate Knowledge Objects until a
human accepts the proposal.

## Stage 4 — Lifecycle Update

For every Knowledge Object touched in Stages 2–3, `first_seen`,
`last_seen`, `occurrences`, `confidence`, and `maturity` are
recalculated per `KNOWLEDGE-OBJECT-SPEC.md` and `LIFECYCLE.md`. `status`
is never touched at this stage — that is Stage 6.

## Stage 5 — Relationship Discovery

Knowledge Objects in scope are compared pairwise (or against the
existing relationship graph, for a large Knowledge Base) for candidate
typed relationships from the fixed ontology (`RELATIONSHIP-ONTOLOGY.md`).
A candidate that cannot be explained against the disambiguation table is
downgraded to `INSUFFICIENT EVIDENCE` and left for a future pass, not
forced into the nearest-sounding type.

**Cycle check, `supersedes`/`depends_on` only** — added 2026-07-24 per
the Reality Stress Test's finding F-3
(`../../../proposals/AG-003-reality-stress-test/
REALITY-STRESS-TEST-REPORT.md`): before proposing a new `supersedes` or
`depends_on` edge, check whether adding it would close a cycle with
already-accepted edges of the *same* type (`A supersedes B supersedes
... supersedes A`, or the `depends_on` equivalent). Both types encode a
one-directional authority claim ("B is now current, not A" / "B requires
A"), which a cycle makes incoherent — there is no well-defined "current"
version or dependency root inside a loop. `supports` and
`alternative_to` are unaffected by this check; they remain coherent even
when mutual. If a cycle would result, the new edge is not proposed as
stated — it is filed as `INSUFFICIENT EVIDENCE` and surfaced in a Gap
Report for a human to determine which existing edge in the cycle is
actually wrong, rather than silently adding a third, equally
unresolvable claim.

## Stage 6 — Promotion Screening

Every Knowledge Object whose `maturity` changed in Stage 4 is checked
against `PROMOTION-RULES.md`'s thresholds for its *next* `status` step
only. A threshold met produces a Core Principle Proposal. A threshold
not met produces nothing — Promotion Screening does not report "not yet
promotable" as an output; silence is the correct result for a Knowledge
Object that simply isn't ready.

## Stage 7 — Contradiction Screening

Knowledge Objects sharing a topic, or connected by a `contradicts`
candidate edge from Stage 5, are checked for logical incompatibility. A
confirmed incompatibility produces a Contradiction Report. **This stage
never proposes a resolution**, and it never escalates past an
`INSUFFICIENT EVIDENCE` marking AG-002 already recorded for the same
underlying tension — it may only note, in the report, that the tension
persists.

## Stage 8 — Gap Screening

The Knowledge Objects and relationship graph in scope are examined for
missing evidence, isolated objects (few or no relationships), weakly
connected clusters, and open Candidate Investigations not yet followed
up. A genuine gap produces a Gap Report, citing any existing `CI-NNNN`
by reference rather than minting a duplicate.

## Stage 9 — Curation Outputs

All artifacts produced in Stages 2–8 are assembled and written per
`OUTPUTS.md`'s formats. Nothing here modifies a Recovery Report, and
nothing here writes directly to an accepted `status` field.

## Stop rule

If continuing at any stage would require inventing a citation, acting on
a proposal instead of merely producing it, or overriding an existing
`INSUFFICIENT EVIDENCE` marking, the correct action is to stop and record
the gap — never to proceed on a reasonable-sounding assumption.

## Relationship to other documents

`INPUTS.md` governs Stage 1. `KNOWLEDGE-OBJECT-SPEC.md` and
`LIFECYCLE.md` govern Stages 2 and 4. `RELATIONSHIP-ONTOLOGY.md` governs
Stage 5. `PROMOTION-RULES.md` governs Stage 6. `OUTPUTS.md` governs Stage
9 in detail. `LIMITATIONS.md` governs the stop rule. `CHECKLIST.md` gives
a condensed practical version of this whole procedure.
