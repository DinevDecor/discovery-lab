# Lifecycle Definition — AG-003 Knowledge Curator

Employee ID: **AG-003** · Role Name: **Knowledge Curator** ·
Status: **Prototype / DRAFT / EXPERIMENTAL / NOT ADOPTED** · Version:
**v0.1**

Every Knowledge Object has exactly two lifecycle tracks, moving at
different speeds, governed by different rules. Conflating them is the
single most likely design mistake in this Role — see
`../../../proposals/AG-003-knowledge-curator-walkthrough/
ADVERSARIAL-REVIEW-0001.md`, finding on this exact risk.

## Track 1 — `status` (formal, human-gated, slow)

```
Draft → Candidate Principle → Validated Principle → Core Principle
```

- Starts at `Draft` the moment a Knowledge Object is created.
- Advances **only** one step at a time, **only** via an accepted Core
  Principle Proposal (`PROMOTION-RULES.md`, `OUTPUTS.md`). AG-003 never
  sets this field directly, and never skips a step.
- Can move only forward under this lifecycle. A `status` demotion (e.g.
  after a Contradiction Report undermines a `Validated Principle`) is
  possible but is itself a separate human decision, not something
  AG-003 proposes automatically as a side effect of filing a
  Contradiction Report — a Contradiction Report only reports; any
  consequence for `status` is a distinct, later act.
- Is the field a human or a Curator reads to know "how settled is this
  idea, formally."

## Track 2 — `maturity` (informal, automatic, continuous)

```
Emerging → Recurring → Convergent → Entrenched
```

- Recomputed every time a new citation is added to `provenance` — no
  approval needed, per `KNOWLEDGE-OBJECT-SPEC.md`'s field rules.
- Can move backward as well as forward in principle (e.g. if a citation
  is later found to be miscounted and removed) — this is expected
  behavior for a signal, not a violation, unlike a `status` reversal.
- Is evidence a Core Principle Proposal cites; it is never, by itself,
  sufficient justification — `PROMOTION-RULES.md` sets the actual bar.

## Why two tracks, not one

A Knowledge Object can be highly `Convergent` or even `Entrenched` in
`maturity` (recurs constantly, well-cited) while still sitting at
`status: Draft` because no human has reviewed it yet — `maturity` is a
description of the evidence; `status` is a description of organizational
trust placed in that evidence. The reverse is also possible in principle
(a `status: Validated Principle` object stops recurring in newer
material and its `maturity` signal goes quiet) — `LIFECYCLE.md` treats
this as informative, not as an automatic demotion trigger.

## Full lifecycle of a Knowledge Object, start to end

1. **Creation** — a Recovery Report finding (a Recovered Idea or
   Repeated Theme) has no matching Knowledge Object yet. AG-003 creates
   `KO-NNNN` at `status: Draft`, `maturity` computed from the finding's
   own occurrence count in that report.
2. **Growth** — a later Recovery Report (a new AG-002 run, or a new
   source) cites the same concept again. `occurrences`, `last_seen`, and
   `maturity` update; `first_seen` and `status` do not change.
3. **Duplicate check** — if a new finding looks like it might already be
   covered by an existing Knowledge Object, AG-003 does not silently
   fold it in — it either adds a citation to the same KO (if the match is
   unambiguous and same-concept) or files a Knowledge Merge Proposal (if
   there is genuine doubt about identity, per `OUTPUTS.md`).
4. **Relationship discovery** — as other Knowledge Objects accumulate,
   AG-003 proposes typed relationships (`RELATIONSHIP-ONTOLOGY.md`)
   between them.
5. **Promotion consideration** — once `maturity` and cross-source
   evidence meet a `PROMOTION-RULES.md` threshold, AG-003 may file a
   Core Principle Proposal for exactly the next `status` step.
6. **Contradiction exposure** — if a later Knowledge Object cannot both
   be true alongside this one, AG-003 files a Contradiction Report. The
   Knowledge Object's own fields are not altered by this report; only a
   later human decision might act on it.
7. **Merge (if accepted)** — if a human accepts a Knowledge Merge
   Proposal, the constituent Knowledge Objects' IDs are retired (not
   deleted — see "What a merge does to IDs" below) and their citations
   are consolidated under a new or designated surviving `KO-NNNN`, with
   `derived_from` recording the lineage.
8. **Retirement** — a Knowledge Object is never deleted. A retired
   object (superseded by a merge, or by a `supersedes` relationship from
   a later object) keeps its file, its ID, and its full provenance —
   only its standing as "current" changes, exactly as `HIRING-LIFECYCLE-
   DRAFT.md`'s Role-retirement discipline already works for employees.

## What a merge does to IDs

An accepted Knowledge Merge Proposal never deletes a `KO-NNNN`. The
merged-away objects are marked retired, pointing (via `derived_from` on
the new or surviving object) to their own IDs. Every `provenance` entry
moved into the surviving object keeps a `merged_from_ko` tag recording
which retired object it came from (`OUTPUTS.md`'s Knowledge Merge
Proposal format, "Reversibility statement") — without this tag, pooling
two objects' citations into one list would make an exact later split
impossible to reconstruct; with it, any external reference to a retired
ID still resolves to real content, and the merge remains reversible by
construction, not merely by promise.

## Relationship to other documents

The concrete field definitions this lifecycle operates on are in
`KNOWLEDGE-OBJECT-SPEC.md`. The exact promotion thresholds for Track 1
are in `PROMOTION-RULES.md`. The procedure that walks a Knowledge Object
through this lifecycle during a pass is `CURATION-PROTOCOL.md`.
