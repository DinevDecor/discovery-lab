# Constraint Change Observatory — Design v0.1

**Status:** design + research probe. No collector, no agent, no scheduled workflow.
**Role:** ideation engineer + system architect, per the task. Nothing here is implemented.
**Does not touch:** `constraint-archaeology-agents/`, `docs/method/`, PR #23, the daily pipeline.
**Companion file:** `docs/constraint-change-observatory-probe.md` — four worked examples.

---

## 1. Purpose

PR #23's Mode B (Legacy Business Rearchitecture) tried to answer *"what historical
constraint shaped this business, and does that constraint still exist today?"*
directly from forum/HN-style text. Its own README is explicit about the result: the
corpus answers *"what hurts now"* reasonably well and *"what structurally changed"*
almost never. The one field that matters most for Mode B —
`evidence_constraint_weakened` — was the field most often stuck at
`INSUFFICIENT_DATA`, and the one case where the corpus spoke to it at all (Japanese
solar-grid curtailment, *"the batteries everyone suggests aren't free"*) was a
document arguing the constraint **still binds**, not that it weakened.

The gap is not a keyword-coverage problem. Present-tense pain reports are not the
right *evidence class* to answer a longitudinal, comparative question
(`then_value` vs. `now_value`, for a claim that must hold over years). No amount of
better regex over Hacker News threads manufactures a 2001-vs-2021 cost curve that
doesn't exist in that corpus.

The Constraint Change Observatory is a separate evidence stream whose only job is to
answer, with provenance: **did this specific constraint, on this specific activity,
materially change — and how do we know?** It is deliberately narrower than Mode B.
It does not look at pain. It does not propose businesses. It produces a record that
Mode B (or anything else) *could* later read as one input among several — never in
this task.

## 2. What this is not

- Not a business-idea generator. Not a market-opportunity detector. Not an
  investment or "PROMISING business" signal. If a record's write-up starts to read
  like a pitch, that content does not belong in this schema.
- Not a replacement for Constraint Archaeology. CA answers "does a structural
  opportunity exist, and who would hold the value." This Observatory answers "did
  the constraint that explains the current structure actually change." Different
  question, different evidence, different failure mode if conflated.
- Not an autonomous agent, sensor, or scheduled job. The stop rule for this task
  is explicit and this document honors it: prove the evidence model can be
  populated reliably by a person doing directed research, before anything about
  automating that research is even considered.

## 3. Core model

```
THEN                    CHANGE                        NOW
constraint materially    something structural          constraint may be:
shaped how an activity   happened: tech, cost,          - weakened
had to be organized      regulation, standard,          - still binding
                          material, infrastructure,      - shifted
                          behavior, scale, ...           - inverted
                                                          - INSUFFICIENT_DATA
```

A record is a claim about this specific chain for one constraint on one activity —
not a general statement that "the world changed." The chain must be reconstructable
from cited evidence at each arrow, or the arrow is marked `INSUFFICIENT_DATA`
instead of assumed.

Downstream inference — *pain + weakened constraint + surviving legacy structure ⇒
rearchitecture candidate* — belongs to something else, later, outside this
Observatory. This document does not perform that inference and the schema below
has no field for it.

## 4. What counts as a constraint

Not just technological ceilings. Candidate families (non-exhaustive, extendable
without a schema change since it's a `payload` value, not a structural field):

cost · latency · bandwidth · compute · storage · energy · battery density/cost ·
material properties · manufacturing capability · minimum economic scale · labor
availability/cost · expertise scarcity · information scarcity · search cost ·
transaction cost · coordination cost · verification cost · trust · identity ·
geographic distance · logistics speed/cost · inventory uncertainty · capital
requirements · financing access · regulation · licensing · standards/interoperability
· distribution access · communication · measurement/observability · consumer
behavior · demographics · infrastructure availability.

AI is not privileged as a family or as a driver. It is one entry in the driver list
below, weighted identically to the other fifteen-plus entries — the same design
choice Mode B already made for its enabler taxonomy, and for the same reason: a
schema that special-cases AI produces AI-flavored answers regardless of what the
evidence says.

## 5. Structural change drivers

technological improvement · commoditization · falling component prices ·
infrastructure deployment · new standards · regulation change · new materials ·
manufacturing improvements · logistics improvements · new financial infrastructure ·
new distribution channels · behavioral change · demographic change · economies of
scale · open-source availability · increased reliability · improved measurement ·
smartphones/GPS/connectivity · robotics · cloud infrastructure · AI · other
evidenced structural change (free text, but must cite).

These are a controlled vocabulary for the `change_driver.category` field, not a set
of pre-approved conclusions — a record does not get to claim a driver it can't cite.

## 6. Constraint-state taxonomy — the load-bearing part

Five states. The fifth is not a fallback bucket to minimize; it is expected to be
the modal outcome early on, and a design that produces mostly `WEAKENED` records
should be treated as a bug, not a success metric.

| State | Meaning | What must be true to assert it |
|---|---|---|
| `WEAKENED` | The constraint materially eased on at least one dimension. | Cited then/now comparison, both instances of the *same* underlying constraint on the *same* activity. |
| `STILL_BINDING` | Evidence explicitly says the limitation remains material. | A source stating the constraint currently holds — not silence, an actual current statement. |
| `SHIFTED` | One bottleneck eased; a different one now binds in its place. | Evidence for the easing *and* evidence naming the new bottleneck. Both required — one without the other is `WEAKENED` or `INSUFFICIENT_DATA`, not `SHIFTED`. |
| `INVERTED` | Former scarcity is now abundance, and the abundance itself creates a new bottleneck (e.g. an attention/verification/trust problem downstream of cheap supply). | Evidence of the reversal plus evidence of the new bottleneck it creates. |
| `INSUFFICIENT_DATA` | Something sounds newer/better, but there is no cited link showing the *original* constraint moved. | Default. Assigning any other state requires meeting its bar above; failing to meet it does not fall through to `WEAKENED`. |

**The battery reference failure mode, generalized as a hard rule:** a source stating
that adjacent technology exists or improved is never sufficient, on its own, to
justify `WEAKENED`. The record must cite a source that speaks to *this* constraint's
*current* state, not merely to progress somewhere nearby. `STILL_BINDING` is not an
edge case to handle gracefully — it is the state the schema exists to protect
against being silently overwritten.

## 7. Evidence discipline: OBSERVED / INFERRED / INSUFFICIENT_DATA

Every field that makes a causal or comparative claim carries its own evidence
status, independently — a record can be `historical_constraint: OBSERVED` and
`current_constraint_state: INSUFFICIENT_DATA` at the same time, and that is a
complete, useful, honest record, not a partial failure.

- **OBSERVED** — a cited source states the claim directly (a number, a rule text, a
  dated statement of cause).
- **INFERRED** — a reasonable structural inference bridges cited facts, but no single
  source states the conclusion outright (e.g., two independently-cited price points
  imply a ratio; no source states "this constraint eased," but the numbers do).
- **INSUFFICIENT_DATA** — the missing link, named as such, not smoothed over.

**Never silently convert INFERRED into OBSERVED**, including on a later revision of
the same record — a strengthened INFERRED claim gets a new record with `SUPERSEDES`,
carrying its own evidence status, not an in-place upgrade. This mirrors the repo's
existing rule for `findings.jsonl`: a newer result is a new record.

### Mapping onto the Reality Observatory primitives

`docs/architecture/reality-observatory-v0.1.md` already defines six primitives
(Capture, Observation, Entity, Expectation, Finding, Link) and this Observatory
should reuse them rather than invent parallel ones — reuse over generalization,
per the same document's own rejected-primitives table.

- External research sources (a government dataset page, a `federalreservehistory.org`
  essay, a NHGRI cost table, a standards-body PDF) are **Captures**: `source`,
  `address`, `fetched_at`, content hash. This is a *separate* Evidence Store from
  Constraint Archaeology's — CA's Capture stream stays sensor-fed and untouched;
  the Observatory's is human-directed research, and the two must not be mixed into
  one trust pool, since they have different collection processes and different
  failure modes.
- The specific then/now numbers, rule texts, and dated statements pulled from those
  Captures are **Observations**: `kind=measurement` (a price, a capacity, a rate) or
  `kind=statement` (a regulatory rule, a stated cause, a stated current limitation).
- A populated Constraint Change Record is a **Finding**: `kind=constraint_change_record`,
  `derived_from` = the Observation ids actually used, `origin=captured` never
  `generated` (no field in this schema may be filled from a model's own synthesis
  and counted as evidence — see §12).
- `constraint_id` continuity across records (a correction, a strengthened claim, a
  reversal) is a **Link**: `SUPERSEDES`, exactly as Findings already work elsewhere
  in this repo.

This is a **manually-authored Finding stream**, not a new store, not a new writer
class, and not a change to who may write to the existing Evidence Store — only the
Analyst Host's contract (§9 of the architecture doc: pure function over a bounded
bundle, output rejected if it cites an id outside the bundle) applies here too.

## 8. Proposed schema — Constraint Change Record

Adapted from the task's proposed field list, reshaped to the repo's append-only /
`derived_from` / `SUPERSEDES` conventions rather than implemented as given, per
CLAUDE.md's instruction to prefer repository convention over a prescribed schema
where they diverge.

```
ConstraintChangeRecord {
  record_id            string     # stable per constraint+activity; new insight = new record + SUPERSEDES, never an edit
  protocol_version      "ccov0.1" # this design's version, independent of CA's method_version — same discipline as adapter_version
  superseded_by         record_id | null

  constraint_family     enum (§4 list, extensible)
  domain                string    # free text, e.g. "genomic diagnostics", "retail banking"
  constrained_activity  string    # the specific process/decision this constraint bore on — same S0 granularity discipline as CA: name who pays, who decides, what breaks

  historical_constraint {
    statement            string
    evidence_status       OBSERVED | INFERRED | INSUFFICIENT_DATA
  }
  historical_evidence    [ { observation_id, citation, value, unit, as_of_date } ]

  historical_adaptation {
    statement             string | null
    evidence_status        OBSERVED | INFERRED | INSUFFICIENT_DATA   # INSUFFICIENT_DATA if no historical evidence — never invented for plausibility
  }

  change_driver {
    category               enum (§5 list, extensible)
    statement               string
    evidence_status          OBSERVED | INFERRED | INSUFFICIENT_DATA
  }
  change_evidence         [ { observation_id, citation, value, unit, as_of_date } ]

  current_constraint_state  WEAKENED | STILL_BINDING | SHIFTED | INVERTED | INSUFFICIENT_DATA
  current_evidence         [ { observation_id, citation, value, unit, as_of_date } ]

  constraint_delta         { <dimension>: DeltaDimension, ... }   # §9, optional per dimension, never a single scalar

  replacement_constraint {
    family                 enum (§4 list) | null
    statement               string | null
    evidence_status          OBSERVED | INFERRED | INSUFFICIENT_DATA
  } | null                  # null only when current_constraint_state is not SHIFTED/INVERTED

  first_seen              timestamp   # recorded_at of the first record for this constraint_id lineage
  last_updated            timestamp   # recorded_at of this record
  # deliberately NO single "confidence" scalar across the whole record — see §7:
  # each sub-claim already carries its own evidence_status, and blending them
  # into one number is exactly the false precision the architecture doc's Trust
  # view already refuses to produce (reality-observatory-v0.1.md §6)

  provenance               [ capture_id ]   # every id in *_evidence must resolve to one of these; violation = invalid record, not a warning
  unresolved_questions     [ string ]       # what a next research pass would need to check
  analyst                  string           # who/what produced this record — human, and say so; no LLM synthesis counts as evidence (§12)
}
```

Deliberate departures from the task's literal field list:

- **No single `confidence` field.** The architecture doc already rejected a stored
  Trust scalar for exactly this reason (§6 of that doc): a blended number hides the
  breakdown that matters. Each sub-claim's `evidence_status` carries the honest
  signal; a record-level confidence would just be a worse copy of information
  already present per-field.
- **`constraint_id` is not a bare field but the identity a `record_id` lineage
  shares under `SUPERSEDES`** — matching how `Entity` versioning and `Expectation`
  correction already work in this repo, rather than inventing a third correction
  mechanism.
- **`first_seen`/`last_updated` are `recorded_at` values, not `observed_at`.** The
  historical evidence they cite can be decades old; the record's own age is a
  separate axis and conflating them is the exact bug §3 of the architecture doc
  calls "the classic mistake."

## 9. Constraint Delta — multidimensional, not a scalar

The task asks explicitly whether a single "Constraint Delta" score is warranted.
**No.** A constraint can move on cost, speed, accessibility, reliability, scale,
geographic reach, skill requirement, capital requirement, and regulatory burden
*independently and in different directions at once* — the solar-PV probe example
below is the clean case: module cost fell >99% (huge cost delta) while installation
labor cost fell only modestly and regulatory/interconnection burden barely moved at
all (near-zero delta on two other dimensions of the *same* constraint transition).
Collapsing that into one number would report "constraint mostly gone," which is
false for the dimension — soft cost — that now dominates.

```
DeltaDimension {
  then_value      number | null
  now_value        number | null
  unit             string
  ratio            number | null       # now/then where both are numeric; null if not computable
  magnitude_class  ORDER_OF_MAGNITUDE(>=10x) | MULTIPLE_X(2-10x) | INCREMENTAL(<2x) | DIRECTION_ONLY | INSUFFICIENT_DATA
  evidence_ids     [ observation_id ]
}
```

`constraint_delta` is a map from dimension name (cost, speed, accessibility,
reliability, scale, geographic_reach, skill_requirement, capital_requirement,
regulatory_burden — extendable) to `DeltaDimension`, populated only where evidence
exists. No universal numeric threshold is hard-coded: `magnitude_class` buckets are
descriptive, not a pass/fail gate, exactly per the task's instruction not to invent
one. A record with a 20x cost delta and a `STILL_BINDING` regulatory dimension is
not a contradiction — it's precisely adversarial case B (§13), and is the kind of
record this design is supposed to produce, not suppress.

## 10. Temporal model

Constraint change is inherently longitudinal; a pile of present-day documents,
however numerous, cannot establish it. The design preserves, structurally:

- **what was true** — `historical_evidence`, dated.
- **when it was true** — each evidence item's own `as_of_date`, not the record's
  `first_seen`.
- **what changed** — `change_evidence`, dated, distinct from both the historical and
  current evidence lists even when they overlap in time.
- **when it changed** — the change driver's own dated evidence, which may predate
  or postdate the record itself by years; the record documents a change, it does not
  need to be contemporaneous with it.
- **what is true now** — `current_evidence`, dated as close to `last_updated` as the
  source allows, and re-checked (a new record, `SUPERSEDES`-linked) rather than
  assumed to remain valid indefinitely.

As in the Expectation Ledger, an `as_of` query should be able to reconstruct "what
did we believe about this constraint on date D" by walking `SUPERSEDES` chains
capped at D — no field is corrected in place, ever.

## 11. Source strategy — where can this evidence actually come from

Rated separately for **THEN/CHANGE** evidence quality (does the source give a dated,
citable then-vs-later comparison) and **NOW** evidence quality (does the source say
anything about whether the constraint is *currently* binding) — this split is the
single most important finding of the probe (§15, and see the full probe file for
detail): they are not the same sourcing problem.

| Source class | THEN/CHANGE quality | NOW quality | Notes |
|---|---|---|---|
| Historical price/performance datasets (NHGRI cost-per-genome, Our World in Data curves, IRENA/Bloomberg NEF energy series) | **Strong** — exactly built for dated comparison | Weak alone — the curve's most recent point is not the same as "is this still a bottleneck for the activity" | Best for `historical_evidence`/`change_evidence`; rarely sufficient alone for `current_constraint_state` |
| Government statistics (BLS, Census, FCC, FDIC) | Strong, often the *only* rigorous THEN source | Moderate — recent releases can serve as current evidence if recent enough | Watch reporting lag; an old release is historical evidence even if uncited as such |
| Standards bodies (ISO, IEEE, telecom/banking regulators' own histories) | Strong for dating *when a rule/standard changed* | Strong for `regulation`/`standards` family specifically — the current rule text is directly citable as NOW evidence | Best-fit source class for the regulatory/institutional family |
| Regulatory records / legislative history (Federal Reserve History essays, statute text, agency rule dockets) | Strong | Strong — current statute/rule text is itself the NOW observation | Same strength as standards bodies; often the same institution |
| Scientific/engineering datasets (peer-reviewed learning-curve studies, NREL benchmark reports) | Strong | Moderate-to-strong when a recent benchmark report exists (e.g. NREL's ongoing solar soft-cost series) | Watch for lab-only results being reported without a deployment qualifier — adversarial case E |
| Industry datasets / analyst reports | Moderate — often proprietary or paywalled, harder to cite fully | Moderate — usually the freshest NOW-adjacent source available | Cite what's publicly summarized; mark INSUFFICIENT_DATA rather than paraphrase a paywall |
| Public procurement records | Moderate | Moderate | Under-explored in this probe; plausible for cost/capital-requirement dimensions, not tested |
| Manufacturer specifications | Weak for THEN unless archived | Strong for NOW cost/capability of a specific component | Good for `constraint_delta.cost`/`.scale`, weak on its own for narrative causation |
| Infrastructure statistics (deployment counts, coverage maps) | Strong | Strong | Directly evidences `infrastructure_deployment` driver and current reach |
| Trade data | Not tested in this probe | Not tested | Plausible for logistics/geographic-distance family; flag as unexplored |
| Labor/productivity data (BLS, OECD) | Strong | Strong | Best-fit for labor availability/cost and expertise-scarcity families |
| Archived documentation (old catalogs, old regulatory filings, newspaper archives) | Strong, and often the *only* way to get a genuine THEN number | Not applicable by definition | Irreplaceable for pre-digital-era THEN evidence |
| Credible longitudinal datasets generally (Our World in Data, FRED) | Strong | Weak alone, same caveat as row 1 | Excellent aggregator/re-publisher of primary series — cite the underlying primary source where the aggregator names one |

**The key asymmetry, stated plainly:** THEN and CHANGE evidence is abundant and
well-archived — this is a solved sourcing problem for most constraint families.
**NOW evidence — specifically, evidence that the *original* constraint is currently
weak, still binding, or replaced — is the scarce half.** It requires a source that
speaks in the present tense to the *original* bottleneck, not a source that speaks
to progress on something adjacent. Regulatory/standards-body sources are the
strongest NOW class found in this probe because the current rule text *is* the NOW
observation, with no inference gap. Reddit/HN/Discourse-style sources (the existing
Constraint Archaeology corpus) were explicitly not assumed sufficient per the task,
and the probe confirms why: they can evidence that a constraint exists (present
pain), but essays that narrate *why a known constraint went away* are exactly the
content Mode B's README already reports as nearly absent from that corpus.

## 12. False-positive controls

The single most important negative rule, stated as a hard gate rather than
guidance:

> **`new technology exists` does NOT imply `old constraint disappeared`.** A record
> may not move `current_constraint_state` to `WEAKENED` on `change_evidence` alone.
> It requires `current_evidence` that speaks to the *original* constraint's present
> state. No `current_evidence` present ⇒ `current_constraint_state =
> INSUFFICIENT_DATA`, full stop, regardless of how strong the change evidence is.

This is checked structurally, not by review discipline alone: a record with a
populated `change_evidence` list and an empty `current_evidence` list is invalid at
`WEAKENED`/`SHIFTED`/`INVERTED` — those three states each require at least one
`current_evidence` citation; only `STILL_BINDING` and `INSUFFICIENT_DATA` may have
an empty `current_evidence` list (and `STILL_BINDING` still needs at least one
citation stating the limitation persists).

Additional controls:

- **Origin discipline.** `origin=generated` content (an LLM's own paraphrase or
  synthesis) is never eligible to fill `*_evidence` lists, exactly as
  `reality-observatory-v0.1.md` §2 rule 4 already requires for the whole
  architecture. This document's own probe (§15 / probe file) was written by an
  agent, which is precisely why every claim in it is tagged and cited rather than
  asserted — the tagging discipline is the control, not a disclaimer bolted on
  after the fact.
- **INFERRED is not a route around missing NOW evidence.** INFERRED requires cited
  facts that *jointly* imply the claim (e.g., two dated price points implying a
  ratio). It does not license "a related field improved, so this one probably did
  too" — that is speculation, which has no field in this schema and does not get
  written down as if it were evidence.
- **`replacement_constraint` requires its own citation**, distinct from the
  citation that established the original constraint weakened. Naming a plausible
  replacement without evidence for it is exactly the kind of pattern-matched
  plausibility this schema exists to refuse — see `proposed_rearchitecture` in Mode
  B, which is explicitly framing-only for the same reason; this schema has no
  framing-only field at all, since it produces no proposal.
- **Lab-only and reliability caveats are first-class**, not something a general
  confidence field is expected to silently discount (adversarial cases E, F below).

## 13. Adversarial analysis

| Case | Test | How the schema/taxonomy handles it |
|---|---|---|
| **A** | Tech improves but business architecture already adapted → no latent-opportunity implication | This Observatory does not draw the "implication" at all — that inference lives downstream, outside this system, by design (§3). But the record itself should show it: `historical_adaptation` populated with the pre-existing workaround, dated *before* the formal `change_driver`. Probe example: bank holding companies used multi-bank-holding-company structures to approximate interstate banking years before Riegle-Neal (1994) formalized it — the adaptation predates the regulatory change, which the record shows plainly rather than implying anything about it. |
| **B** | Cost falls 20× but regulation remains binding → shifted, not disappeared | `constraint_delta.cost` can show a 20× ratio while `current_constraint_state = STILL_BINDING` if the record's `current_evidence` cites the still-active rule. Nothing in the schema forces cost improvement to propagate into the state field — they're independent per §9/§12. Probe example: remote/networked banking technology matured well before 1994 while McFadden Act branching restrictions remained the binding constraint until the statute itself changed. |
| **C** | AI can perform a task but customers legally require a licensed human → labor/expertise constraint has not disappeared | `replacement_constraint.family = expertise_scarcity` or `regulation`/`licensing`, with its own citation (e.g., CLIA/clinical-genetics licensure requirements), while `historical_constraint`'s original family (e.g., `cost` of sequencing) is correctly marked `WEAKENED` — the schema lets one dimension weaken while a *different* constraint family remains fully binding on the same activity, which is exactly `SHIFTED`, not `WEAKENED`. Probe example: DNA sequencing cost. |
| **D** | Component becomes cheap but installation/service remains expensive → identify replacement constraint | This is the multidimensional case §9 exists for: `constraint_delta.cost` (module price) shows order-of-magnitude improvement while `constraint_delta` has no comparably strong entry for labor/regulatory dimensions, and `current_constraint_state = SHIFTED` with `replacement_constraint` citing soft-cost/installation-labor evidence. Probe example: solar PV. |
| **E** | New capability exists only in lab conditions → do not classify as broadly weakened | `current_evidence` sourced from a peer-reviewed or lab-context source must be tagged with its deployment context; a record whose only `current_evidence` is lab-context evidence should default to `INSUFFICIENT_DATA` for real-world `current_constraint_state`, with an `unresolved_questions` entry naming the deployment gap explicitly, rather than reading "works in principle" as "constraint gone in practice." Not covered by a full worked example in this probe (flagged as untested, not resolved). |
| **F** | New tech is cheaper but substantially less reliable → preserve the reliability constraint | `constraint_delta.cost` and `constraint_delta.reliability` are separate dimensions; a record can show a strong cost improvement and a negative or `INSUFFICIENT_DATA` reliability delta simultaneously, with `current_constraint_state = SHIFTED` (cost eased, reliability now binds). Probe example: early-2000s VoIP was dramatically cheaper than long-distance calling but had citable call-quality/jitter/reliability problems that a pure cost record would miss. |
| **G** | A constraint genuinely disappears, zero AI involvement → must be detected normally | The driver taxonomy (§5) treats AI as one entry among 20+; nothing in scoring or state assignment references AI specially, so a record with `change_driver.category = regulation_change` and full OBSERVED evidence reaches `WEAKENED` exactly the same way an AI-driven record would. All four probe examples are zero-AI and reach populated states on that basis alone — this is closer to a demonstration than a hypothetical. |

## 14. Relationship to Constraint Archaeology and Business Candidate Analyst

**Constraint Archaeology:** untouched. No file under `constraint-archaeology-agents/`,
`docs/method/`, or any gate/threshold/source-allocation logic is read for write
purposes by this design, and none is proposed to change. If this Observatory is ever
built, it is a wholly separate Evidence Store and Analyst, connected to nothing CA
already owns.

**Business Candidate Analyst:** independence is structural, not just a stated
intention. The schema in §8 has no field for a product, a market, a business name,
an investment signal, or a "PROMISING" verdict — there is nowhere in the record to
write one, which is a stronger boundary than a review checklist. A Constraint Change
Record should read as useful evidence even to someone who has never heard of a
"business candidate" — it answers "did this constraint change," full stop.

**Future (explicitly not this task):** Mode B could eventually consume Constraint
Change Records as one more input to the `evidence_constraint_weakened` field
(currently its weakest, most `INSUFFICIENT_DATA`-heavy field per its own README) —
a Finding this Observatory produces would sit in Mode B's `EvidenceBundle` exactly
like a C3 `capability_price_shift` Finding sits in Constraint Archaeology's, per
the architecture doc's Analyst contract (§9 of that doc). No wiring for this exists
and none is added here.

## 15. Real-world probe — summary

Four examples, worked in full (with citations) in
`docs/constraint-change-observatory-probe.md`: one technological (DNA sequencing
cost), one economic/infrastructure (long-distance telephony cost), one
regulatory/institutional (US interstate bank branching), one non-AI structural
(solar PV module cost). All four are zero-AI, satisfying adversarial case G by
construction; the set collectively exercises adversarial cases A, B, C, D, F (E is
flagged untested, not resolved — see §13).

**Finding, in one sentence:** THEN and CHANGE evidence populated cleanly and
quickly from public, well-archived sources for all four; NOW evidence — specifically
whether the *original* constraint is currently weak, still binding, or replaced —
took materially more research effort per example and, for two of the four, only
reached `SHIFTED` rather than a clean `WEAKENED` once a genuinely current source was
required. That asymmetry (§11) is the load-bearing result of this probe.

## 16. Recommendation: **BUILD** — smallest possible slice

Reasoning:

- The evidence model is populable. All four probe examples reached a real,
  cited, non-`INSUFFICIENT_DATA` `current_constraint_state`, including two `SHIFTED`
  and not four uniform `WEAKENED` — meaning the taxonomy differentiated rather than
  flattened, which was the main risk worth testing before committing to it.
- The scarce half (NOW evidence) is scarce but not absent — it clusters
  reliably in a specific, identifiable source class (regulatory/standards-body
  current text, recent government/engineering benchmark reports), not scattered
  unpredictably. That's buildable process knowledge, not a dead end.
- But: four hand-researched examples, each taking real, non-trivial directed
  search, is not evidence that this scales to an autonomous collector, and the task's
  stop rule is correct to block that jump. What's proven is narrower: a *person*
  doing directed research *can* populate this schema honestly. Whether a scheduled
  agent can do the NOW-evidence half at comparable quality is untested and should
  stay untested until the manual version has enough volume to know what "comparable
  quality" even means here.

This is a **MODIFY-shaped BUILD**: build the schema and the discipline, not a
pipeline.

## 17. Smallest viable implementation slice (proposed, not built here)

1. `docs/architecture/constraint-change-observatory-v0.1.md` — promote this design
   from a proposal to the adopted architecture note, same status as
   `reality-observatory-v0.1.md`, once a human has reviewed it (this task does not
   self-adopt its own design).
2. A single append-only file, `constraint-change-observatory/data/records.jsonl` —
   one `ConstraintChangeRecord` (§8) per line, `SUPERSEDES`-linked, hand-authored.
   No sensor. No scheduler. No LLM call in the write path — a human (or an agent
   working in a single directed research session, exactly as this probe was
   produced) fills the schema and cites sources, the same way `docs/reviews/` entries
   are hand-authored today.
3. A **schema validator only** — a small script that rejects a record violating the
   structural rules already stated as hard gates in §12 (e.g., `WEAKENED` without a
   `current_evidence` citation) and checks `provenance` actually contains every
   `observation_id` cited. This is validation, not collection — it has no network
   access and no model call, consistent with "Tests are offline and deterministic."
4. Populate 10–15 more records by the same manual process as this probe, across a
   deliberately wider set of constraint families than the four here (labor/expertise,
   trust/identity, and logistics are untested by this probe and should be prioritized
   next).
5. **Revisit point, not a target:** after that batch, re-answer §11's question —
   does the THEN/CHANGE-vs-NOW asymmetry hold, or was it an artifact of choosing four
   examples with unusually good regulatory-history documentation? Only after that
   re-check does it make sense to discuss any automation, and even then: automating
   *retrieval* of candidate sources for a human to evaluate is a much smaller,
   much safer next step than automating the *judgment* of `current_constraint_state`
   itself, which is where the honesty burden of this whole design actually lives.

Do not build past step 3 in this task, per the task's own stop rule.

## 18. Open risks

- **Selection bias in what gets researched.** A human choosing which constraints to
  investigate will gravitate toward stories with a satisfying arc. Nothing in this
  design corrects for that; it's a §11-source-strategy problem for a future
  iteration (a driver taxonomy sampled deliberately rather than a topic list chosen
  by whoever's writing that week), not a schema problem.
- **Regulatory/standards-body strength may not generalize.** Three of four probe
  examples leaned on institutions with unusually good self-published history
  (Federal Reserve History, NHGRI, IRENA/OWID). Constraint families without an
  equivalent institution (e.g., informal labor-market norms, consumer behavior)
  may show the THEN/CHANGE-vs-NOW asymmetry far more sharply, or may simply be
  much harder to research at all — untested by this probe.
- **"Current" is a moving target.** A record's `current_evidence` is only current as
  of its own `last_updated`; nothing in this design re-checks records automatically,
  which is intentional (no scheduler, per the stop rule) but means staleness is a
  known, accepted cost of the manual-slice approach, not a solved problem.
- **This document is itself `origin=generated` content about generated content's own
  limits** — it was written by an agent. Per §12/§7, none of its own prose counts as
  evidence for anything; only the cited sources in the probe file do. A human review
  pass before step 1 of §17 is not optional.
