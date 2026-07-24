# Knowledge Object Specification — AG-003 Knowledge Curator

Employee ID: **AG-003** · Role Name: **Knowledge Curator** ·
Status: **Prototype / DRAFT / EXPERIMENTAL / NOT ADOPTED** · Version:
**v0.1**

A Knowledge Object is `discovery-lab`'s own curated unit of recovered
knowledge. It is not a copy of, and has no relationship to, KOD's own
`GRIF` document format, KOD's `Registry`, or KOD's `Knowledge Graph` —
see `ROLE.md`'s Terminology note. A Knowledge Object exists only because
AG-002 recovered something citable; it is never created from nothing.

## ID scheme

`KO-NNNN`, a flat, sequential, append-only identifier — never reused,
never renumbered, even if a Knowledge Object is later merged away (its
ID is retired, not recycled, so every reference to it anywhere else
remains valid — see `LIFECYCLE.md`, "What a merge does to IDs").

## Fields (exact set, per the requesting task)

```yaml
id:                       # KO-NNNN
title:                    # short human-readable name for the concept
status:                   # Draft | Candidate | Validated | Core
first_seen:               # date of the earliest citation supporting this KO
last_seen:                # date of the most recent citation supporting this KO
occurrences:               # count of distinct citations across all supporting Recovery Reports
confidence:                 # AG-003's own curation-confidence, 0.0-1.0 (see "Confidence")
maturity:                  # Emerging | Recurring | Convergent | Entrenched (see "Maturity")
derived_from:               # list of KO-NNNN this object was built from, if any
supported_by:                # list of KO-NNNN whose relationship to this one is `supports`
contradicted_by:             # list of KO-NNNN whose relationship to this one is `contradicts`
related_objects:             # list of {ko_id, relationship_type} for the other 5 ontology types
candidate_investigations:     # list of CI-NNNN generated or cited against this KO
provenance:                  # list of {report, finding_id, date, citation}
```

## Field-by-field rules

- **`id`** — assigned once, at creation, never changed.
- **`title`** — a short gloss of the concept, not a verbatim quotation
  of any source text (avoids the personal-data and over-quotation
  discipline AG-002 already applies to Recovery Reports).
- **`status`** — the **formal**, human-gated lifecycle stage. Changes
  only via an accepted Core Principle Proposal (`PROMOTION-RULES.md`).
  Never set directly by AG-003. Starts at `Draft` on creation.
- **`first_seen` / `last_seen`** — dates of the earliest and most recent
  citation in `provenance`, not dates AG-003 estimates or infers. If a
  cited Recovery Report itself records a date discrepancy (as
  `PILOT-RUN-0002-recovery-report.md`'s Open Questions does for
  `20260629`), the discrepancy is carried into the Knowledge Object's own
  provenance note, not silently resolved.
- **`occurrences`** — a plain count of `provenance` entries. Distinct
  restatements within the *same* source entry count once each only if
  AG-002 itself recorded them as separate citations; AG-003 does not
  re-split a single AG-002 citation into multiple occurrences.
- **`confidence`** — AG-003's own assessment (0.0–1.0) of how
  well-evidenced this Knowledge Object is. Computed as
  `citation_factor * diversity_factor * contradiction_factor`, so any
  factor at `0` drives the whole value to `0` rather than being averaged
  away:
  - `citation_factor` — `1.0` if every `provenance` entry is a checkable
    citation to a real Recovery Report finding; `0.0` if any entry is
    not (an uncitable Knowledge Object should not carry a reassuring
    confidence value at all).
  - `diversity_factor` — `0.4` for a single source / single Recovery
    Report run, `0.7` for two, `1.0` for three or more independent
    sources or runs — deliberately capping single-source evidence below
    the halfway point, matching `maturity`'s own `Recurring`/`Convergent`
    distinction below.
  - `contradiction_factor` — `1.0` with no open Contradiction Report
    naming this object, `0.5` with one open and unresolved, `0.0` with
    one that a human has confirmed rather than merely reported.
  Worked: `KO-0001` (5 citations, all checkable, single source, no
  contradiction) = `1.0 * 0.4 * 1.0 = 0.4`. This spec's own earlier draft
  used `0.55` for `KO-0001` from a qualitative estimate, before this
  formula was written — corrected to `0.4` in
  `../../../proposals/AG-003-knowledge-curator-walkthrough/
  KO-0001-nature-as-library-of-architectures.md` to match. **This is
  never the same number as a cited GRIF's own `confidence` field** —
  where one exists, it is preserved verbatim inside the matching
  `provenance` entry, not averaged or folded into this field (`ROLE.md`,
  Terminology note). The formula's own weights (`0.4`/`0.7`/`1.0`, the
  three-way multiplication) are this design's own invented starting
  point, not derived from any external precedent — flagged here exactly
  as `PROMOTION-RULES.md` flags its own 90-day threshold, open to human
  revision before any real proposal relies on it.
- **`maturity`** — an **informal**, continuously-recomputable signal,
  distinct from `status`. Four ordered values:
  - `Emerging` — 1 occurrence, single source.
  - `Recurring` — 2+ occurrences, still a single underlying source
    document or archive.
  - `Convergent` — 2+ occurrences spanning at least two independent
    Recovery Reports or two genuinely distinct historical sources.
  - `Entrenched` — `Convergent`, sustained over a duration threshold
    (see `PROMOTION-RULES.md`'s time-span rule).
  `maturity` updates automatically as new citations are added — it
  requires no human approval, unlike `status`. A high `maturity` is
  evidence a Core Principle Proposal may cite; it is not itself a
  promotion.
  **Source-granularity rule** — added 2026-07-24 per the Reality Stress
  Test's finding F-2 (`../../../proposals/AG-003-reality-stress-test/
  REALITY-STRESS-TEST-REPORT.md`): "one source" means **one originating
  repository, archive, or document collection scanned in one AG-002
  run** — not one file. Three citations drawn from three different files
  within the same repository, in the same run (e.g. `kod`'s
  `EX-0001_CASE.md`, `ART-0001.md`, and its own `ADR-0002.md`, all
  scanned in one `STRESS-RUN-0004` pass) count as **one** source for this
  purpose, same as five citations from five entries in one diary archive
  count as one source. `Convergent` requires citations from **two
  separate repositories/archives, or two separate AG-002 runs over the
  same one** — never satisfied by file count alone within a single run
  over a single repository.
- **`derived_from`** — set only when this Knowledge Object was built by
  an accepted Knowledge Merge Proposal, or when it is explicitly a
  refinement/extraction of another KO's content. Empty for a
  freshly-created object with no such lineage. **Sync rule**: this
  top-level field is the authoritative record of merge lineage only
  (which retired `KO-NNNN`s this object absorbed, per `LIFECYCLE.md`'s
  `merged_from_ko` tagging). An accepted `derived_from`-typed
  Relationship Proposal (`RELATIONSHIP-ONTOLOGY.md`) is recorded
  separately, only in `related_objects` below, and does **not** also get
  written here — the two are deliberately not kept in sync, because they
  answer different questions ("what was this object built *from*, by
  merge" vs. "what does this object *relate to*, without being built
  from it"). A reader checking lineage reads this field; a reader
  checking relationships reads `related_objects`.
- **`supported_by`** / **`contradicted_by`** — denormalized views of the
  `supports` and `contradicts` relationship types (`RELATIONSHIP-ONTOLOGY.md`),
  kept for quick lookup. The relationship graph itself (Relationship
  Proposals, once accepted) is the source of truth; these two fields are
  derived from it, not maintained independently.
- **`related_objects`** — every accepted relationship of the other five
  ontology types (`depends_on`, `inspired`, `supersedes`, `derived_from`
  as a *relationship* rather than lineage, `alternative_to`), each tagged
  with its type. `derived_from` appears both as a top-level lineage field
  (above) and, where relevant, as a typed entry here — the top-level
  field is authoritative for "what this object was built from"; the
  relationship-graph entry is authoritative for graph traversal.
- **`candidate_investigations`** — `CI-NNNN` identifiers, always
  continuing AG-002's existing sequence (`OUTPUTS.md`). Never a new
  numbering scheme.
- **`provenance`** — the non-negotiable field. Every other field's value
  must be reconstructable from this list alone. An entry with fields
  populated but an empty or incomplete `provenance` list is not a valid
  Knowledge Object under this spec.

## Where Knowledge Objects are stored

`../../../../memory/knowledge-objects/KO-NNNN.md`, one file per object,
once a real Knowledge Base exists. This design task did not create that
directory or populate it with real objects from `memory/`; the worked
example (`../../../proposals/AG-003-knowledge-curator-walkthrough/`)
demonstrates the format inline, in the proposals folder, precisely so it
is not mistaken for an accepted, filed Knowledge Base — see
`STATUS.yaml`'s open governance question on this point.

## Relationship to other documents

Lifecycle transitions (how `status` and `maturity` move, and what
counts as "a lifecycle") are in `LIFECYCLE.md`. Relationship types for
`related_objects` are in `RELATIONSHIP-ONTOLOGY.md`. The concrete
threshold rules for `status` promotion are in `PROMOTION-RULES.md`.
