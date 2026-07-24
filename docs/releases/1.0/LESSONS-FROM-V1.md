# Lessons from v1 — AG-002 / AG-003

Written at Release 1.0 (`RELEASE-1.0.md`), drawing on the full record in
`VALIDATION-HISTORY.md`. This is a synthesis document, not a governance
one — nothing here is binding; `GOVERNANCE.md` is where a lesson becomes
a rule.

## Mistakes made

- **A recurring off-by-one relative-path bug** (`../../` where `../../../`
  was needed, or vice versa, depending on a file's actual folder depth)
  was caught independently at least three separate times across
  different run reports before this release, and again during this
  release's own drafting. The fix was never "be more careful" — it was
  making `realpath -m` + `test -f` verification a mechanical,
  non-optional pre-commit step. A lesson about process, not attention
  span: the same category of mistake recurred until the check became
  automatic rather than a thing to remember.
- **`confidence` was shipped without a formula**, and Knowledge Merge
  Proposal "reversibility" was asserted without a mechanism, in AG-003's
  first draft. Both are the same underlying mistake: describing a
  property qualitatively and treating the description as if it were
  already a specification. Caught by the adversarial review, not by the
  original design pass — a real design pass, however careful, does not
  reliably catch its own unstated assumptions.
- **A fix reopened an adjacent, previously-flagged issue.** The Reality
  Stress Test's `F-2` correction (clarifying what counts as "one
  source" for `maturity`) used wording — *"two separate AG-002 runs over
  the same [repository]"* — that satisfies the adversarial review's
  earlier, separately-flagged finding 4 (a re-scan of unchanged material
  inflating `maturity`). Nobody intended to reopen finding 4; it happened
  because the two findings were adjacent in subject matter but were
  fixed in different sessions without cross-checking against each
  other's exact wording. Recorded in `VALIDATION-HISTORY.md` item 16,
  left unfixed in this freeze on purpose. Lesson: a fix's own wording
  needs to be checked against every other open finding touching the same
  field, not just the one finding it was written for.
- **A stale cross-reference almost shipped**: AG-003's `METRICS.md` still
  said *"AG-003 has had no real run as of v0.1"* after the Reality
  Stress Test had already given it three. Caught while preparing this
  freeze, not automatically — nothing in the architecture flags a
  document that quotes `STATUS.yaml`'s old value instead of reading it
  live. A real, low-severity instance of the same general class of
  mistake as the path bug: prose that duplicates a fact instead of
  pointing at its one source of truth will eventually drift from it.

## Architectural decisions that proved correct

- **"Propose, never impose."** Every governance boundary in AG-003's
  design — no automatic merge, promotion, or contradiction resolution —
  held with zero violations across four structurally different real
  datasets, including three datasets deliberately built to tempt a
  violation (two hallucination traps, one false-merge trap). This is the
  single most validated claim in this entire release, and the design
  decision `GOVERNANCE.md` now treats as the default for any future Role
  touching recovered or curated knowledge, not something to reconsider
  case by case.
- **Separating `status` (formal, human-gated) from `maturity` (informal,
  automatic).** This distinction was designed before any real data
  existed to justify it, and then turned out to matter in practice more
  than once — `KO-0001` and `KO-S3-01` both needed to be describable as
  "recurs a lot, not yet formally trusted" without those being the same
  field.
- **Mandatory `Provenance` citation on every artifact.** This is what
  made the Reality Stress Test possible to conduct rigorously at all —
  every claim in every Knowledge Object, proposal, and report could be
  traced back to one exact Recovery Report finding, which is what let
  this release's own reviewers (the same session, disclosed as a
  limitation, but still checking) verify or falsify each one directly
  against source text instead of trusting a summary.
- **Reusing AG-002's escalation vocabulary** (`INSUFFICIENT ACCESS`,
  `INSUFFICIENT EVIDENCE`, `UNKNOWN`, `BLOCKED`) instead of inventing a
  parallel set for AG-003. One value, `BLOCKED`, was reused verbatim;
  no new value was needed beyond it. Fewer distinct escalation states
  across Roles means fewer chances to use the wrong one.
- **Writing terminology disambiguation before ever touching the real
  content it disambiguates against.** AG-003's `ROLE.md` distinguished
  its own Knowledge Object from KOD's `Registry`/`Knowledge Graph`/
  `confidence` at design time, speculatively, based only on what AG-002
  had recovered secondhand from a diary. The Reality Stress Test then
  read KOD's actual `KNOWLEDGE_OBJECT_TEMPLATE.md` for the first time —
  real, not secondhand — and the disambiguation held without
  modification. Writing the boundary early and testing it late is a
  pattern worth repeating.

## Discarded ideas

- **An eighth relationship type for "amends."** Considered when `F-1`
  surfaced (`ADR-0004` amending one property of `ADR-0003`), rejected in
  favor of scoping the existing `supersedes` type to a named property.
  The narrower fix covered the real case without growing the ontology —
  a smaller change was preferred once it was confirmed to actually work,
  not chosen by default.
- **A separate `CI-NNNN` namespace for AG-003.** Considered at design
  time, deferred — no volume problem has materialized (the Reality
  Stress Test minted only five new numbers, `CI-6`–`CI-10`, without
  incident). Recorded as an open governance question rather than solved
  speculatively; building the collision-prevention mechanism before a
  collision has ever happened would be exactly the premature-abstraction
  error `HIRING-LIFECYCLE-DRAFT.md` already declined to make for
  candidate tiers.
- **Per-category Knowledge registries** (separate Ideas/Principles/
  Hypotheses/Decisions/Research-Questions folders), as the original
  diary-processing task's own taxonomy suggested. Discarded in favor of
  AG-002's existing Recovery Report section structure, which already
  covers the same ground under different names (Recovered Ideas ≈
  ideas/principles/hypotheses, Open Questions ≈ research questions) —
  recorded as a real, stated gap against the literal original ask, not
  silently substituted, but not built either, since the substitute
  covers the same ground.

## Principles that survived reality

- **Never invent a citation.** Held across every run, including under
  three deliberate traps designed specifically to tempt fabrication.
- **A repeated appearance is evidence, never noise to collapse.**
  Duplicate preservation held throughout — including the one case
  (`KMP-S3-01`) where the correct call was to *recommend* a merge, not
  just decline one, confirming the restraint isn't a one-way bias.
- **Preserve an existing `INSUFFICIENT EVIDENCE` marking; never
  escalate it past what the original evidence supports.** Tested
  directly (`CONTRADICTION-CHECK-0001.md`, the `NORM`/confidence
  tension) and by construction (the `M1`/`М1` case, correctly recognized
  as one finding about an audited system, not a contradiction between
  two of AG-003's own claims).
- **Cross-repository observation, without writing back, is workable in
  practice, not just on paper.** `PROP-0001`'s Principle 0 and `INV-0002`'s
  precedent were tested for the first time by an actual downstream Role
  (not just an architecture pass) in the Reality Stress Test, reading
  real `kod` and `trust-engine` content and changing neither repository.

## Recommendations for future agents

1. **Require a Reality Stress Test against at least two structurally
   different real sources before any freeze** — not just the one source
   that motivated the Role's creation. `F-1` and `F-2` were both
   invisible to a design process validated only against the diary; they
   became visible the moment a header-linked document set and a
   multi-file corpus were introduced. This is now `GOVERNANCE.md`'s
   mandatory lifecycle, not a suggestion.
2. **When fixing a finding, check its wording against every other open
   finding touching the same field**, not just the finding that
   motivated the fix — see "Mistakes made," above, on `F-2`.
3. **Write terminology disambiguation against neighbor-repo vocabulary
   at Draft time, speculatively, then re-test it against real content
   once available** — repeat the pattern that worked for AG-003/KOD for
   any future Role that touches generative-discovery-engine's or
   trust-engine's own reserved words.
4. **Default new Roles to "propose, never impose"** for any function
   that touches recovered or curated knowledge, rather than treating it
   as a design choice to re-argue each time.
5. **Keep escalation vocabulary shared and minimal** across Roles;
   introduce a new value only once a real situation has shown the
   existing set genuinely cannot express it (as `BLOCKED` was, and as
   AG-003's reuse of the full existing set, without needing new values
   beyond it, was).
6. **Choose new ID-scheme prefixes to avoid collision with prefixes
   already used elsewhere in the ecosystem** (this release deliberately
   avoided `CR-NNNN` for Contradiction Reports, since
   generative-discovery-engine already uses it for Critical Reviews) —
   check the neighbor repositories' own vocabulary before naming
   anything new, not just this repository's own.
