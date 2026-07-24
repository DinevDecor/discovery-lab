# Relationship Ontology — AG-003 Knowledge Curator

Employee ID: **AG-003** · Role Name: **Knowledge Curator** ·
Status: **Prototype / DRAFT / EXPERIMENTAL / NOT ADOPTED** · Version:
**v0.1**

Seven relationship types, and only these seven. Every edge in the
relationship graph must use exactly one of them (a pair of Knowledge
Objects may carry more than one edge between them if genuinely
warranted, e.g. both `supports` and `inspired`, but never an
unclassified or freeform edge). Every edge must be **explainable**: a
Relationship Proposal that cannot state, in one sentence, why the chosen
type fits better than each confusable alternative is not valid
(`OUTPUTS.md`).

## The seven types

1. **`supports`** — Knowledge Object A provides independent evidence
   that reinforces B, without A being logically required for B to hold.
   Removing A weakens confidence in B but does not invalidate it.
2. **`contradicts`** — A and B cannot both be true as currently stated.
   Symmetric. Never carries a proposed resolution (`OUTPUTS.md`,
   Contradiction Reports).
3. **`depends_on`** — B's validity is conditional on A remaining true. If
   A is later contradicted or retired, B's own status should be
   reconsidered by a human — AG-003 flags this exposure but does not act
   on it.
4. **`inspired`** — A prompted the creation or direction of B, but B is a
   genuinely distinct idea, not a revision or extraction of A's own
   content. Directional, one-time (describes origin, not ongoing
   support).
5. **`supersedes`** — B is a later, revised version of the same
   underlying claim as A, and is the version that should now be treated
   as current; A remains on record but is no longer the going-forward
   statement. Directional.
6. **`derived_from`** — B was built by extracting, narrowing, or
   recombining part of A's own content (as a relationship-graph edge,
   distinct from the top-level lineage field of the same name in
   `KNOWLEDGE-OBJECT-SPEC.md`, which records merge lineage specifically).
   A remains independently valid; B is not a replacement for it.
7. **`alternative_to`** — A and B address the same problem or niche as
   competing, mutually non-exclusive candidates — neither replaces the
   other, and both may remain open simultaneously. Symmetric.

## Disambiguation table (confusable pairs)

| Pair | The distinguishing question |
|---|---|
| `derived_from` vs. `inspired` | Does B reuse A's actual content/structure (derived_from), or did A merely prompt B's existence while B stands on its own content (inspired)? |
| `derived_from` vs. `supersedes` | Does A still stand as independently valid after B exists (derived_from), or has B replaced A as the current statement of the same claim (supersedes)? |
| `supports` vs. `depends_on` | If A were removed, does B merely lose a piece of corroborating evidence (supports), or does B stop being a coherent claim at all (depends_on)? |
| `contradicts` vs. `alternative_to` | Can A and B both remain true and open at once (alternative_to), or is it logically impossible for both to hold (contradicts)? |
| `supersedes` vs. `contradicts` | Is B a *revision* of the same claim by the same reasoning lineage, explicitly moving it forward (supersedes), or are A and B independent claims that happen to conflict (contradicts)? |

A Relationship Proposal touching any pair in this table must cite the
distinguishing question directly, not merely assert a type.

## Graph explainability rule

"The graph must remain explainable" (the task's own requirement) means:
for any two connected Knowledge Objects, a human must be able to read
the single Relationship Proposal that created that edge and understand,
without consulting AG-003 further, exactly why that type (and not a
confusable alternative) was chosen, and what citation supports it. A
relationship inferred purely from graph shape (e.g. "these two are often
cited together") without a stated reason is not a valid proposal — see
`../../../proposals/AG-003-knowledge-curator-walkthrough/
ADVERSARIAL-REVIEW-0001.md` for a worked stress-test of this rule.

## Relationship to other documents

`related_objects`, `supported_by`, and `contradicted_by` on a Knowledge
Object (`KNOWLEDGE-OBJECT-SPEC.md`) are populated only from accepted
Relationship Proposals (`OUTPUTS.md`) using the types defined here.
