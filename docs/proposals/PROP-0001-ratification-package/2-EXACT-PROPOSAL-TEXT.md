# Deliverable 2 — Exact Proposal Text

Per this task's rule ("не пренаписвай... не създавай нова версия"),
nothing below is paraphrased. The operative provisions — the frame
(Principle 0) and the actual recommendation being put up for
ratification — are quoted verbatim, with exact section references
into `docs/proposals/PROP-0001-discovery-lab-boundaries.md`. The full
document (918 lines: three variants in full, the recommendation
reasoning, the information-flow map, the Recommendation Ledger
interface, the first-experiment design, the self-critique, and the
full Adversarial Review record) is not reproduced a second time here —
duplicating it would risk a transcription drift between two "sources
of truth" for the same text, which this task's own Definition of Done
forbids ("без промяна на съдържанието му"). This deliverable exists so
the ratifying decision can be read against the exact operative words
without needing to first locate them inside the 918-line document.

## Principle 0 (verbatim, from the source document)

> **Discovery Lab never creates truth. It only observes, compares, and
> identifies inconsistencies, and proposes next steps — an experiment,
> a correction, or a question — for the owning repository to accept or
> reject through its own governance. Discovery Lab itself never
> accepts, finalizes, or applies any of these proposals.**

## The Recommendation (verbatim, from the source document, §"Recommendation (proposed, not accepted)")

> **Recommended: Variant B — Ecosystem Observatory, alone, for now.**

With four supporting points, quoted exactly:

> **1. Evidence basis.** Three independent lines of evidence support
> this, all drawn from `INV-0001` and `INV-0002`:
> - Two concrete precedents of Observatory-shaped work already
>   happening in practice, ad hoc, with nowhere proper to live
>   (`project-memory/notes/2026-07-19-dinev-decor-systems-location-
>   check.md` and `project-memory/notes/2026-07-24-discovery-lab-
>   recovery.md`).
> - All three independently-reviewed repositories (KOD, GDE,
>   trust-engine) are strictly inward-facing — none has any documented
>   awareness of the other two, of discovery-lab, or of project-memory
>   (`INV-0002` synthesis, "Gaps").
> - The independent trust-engine pass itself produced a live example
>   of Observatory-shaped value during this very investigation: a
>   genuine, previously-undocumented 60-document/15-module
>   specification-vs-implementation gap, found by simply reading the
>   repository's own files against each other — proving the role's
>   usefulness empirically, not just by argument.
>
> **2. Why Variant A was not selected.** No repository has *requested*
> prototyping help... Adopting Variant A now would be building capacity
> for a need that is speculative rather than observed.
>
> **3. Why Variant C was not selected.** C's added governance burden...
> is only justified if the observatory→lab feedback loop is actually
> valuable, which cannot be established until Variant B alone has run
> at least once.
>
> This recommendation is not an acceptance. It requires a human
> decision before any variant governs how discovery-lab is actually
> used.

## What "accepting the recommendation" would concretely mean

Per the source document's own §"Are the three variants genuinely
distinct?" and Variant B's own definition: read-only, cross-repository
status-checking; owned artifacts limited to dated investigation
reports ending in `confirmed`/`contradicted`/`insufficient evidence`;
prohibited from producing any code, prototype, Hypothesis, discovery
method, or trust score; every finding routed as a proposal only, never
applied directly to any repository outside `discovery-lab` itself;
governed by the fixed entry/exit/deletion rules and the first-experiment
design (`Ecosystem Health Review v0.1`) already fully specified in the
source document's own text — none of it re-specified or altered here.

## Exact location of every provision this package references

| Provision | Section in the source document |
|---|---|
| Shared ground rules (6 rules, apply to all variants) | `## Shared ground rules (apply to all three variants)` |
| Variant A definition | `## Variant A — Experiment Laboratory` |
| Variant B definition | `## Variant B — Ecosystem Observatory` |
| Variant C definition | `## Variant C — Combined Lab + Observatory` |
| Recommendation and its reasoning | `## Recommendation (proposed, not accepted)` |
| Disambiguation note (terminology) | `## Disambiguation note (terminology collision, per ground rule 1)` |
| Information-flow map + transfer specs | `## Proposed information-flow map` |
| Recommendation Ledger interface (unimplemented) | `## Recommendation quality: interface definition only (not implemented)` |
| First experiment (`Ecosystem Health Review v0.1`) | `## First experiment: Ecosystem Health Review v0.1` |
| Self-critique against named failure modes | `## Self-critique` |
| Full Adversarial Review record, verdict, and applied changes | `## Adversarial Review — vFinal` |
| Unresolved questions | `## Unresolved questions` |
