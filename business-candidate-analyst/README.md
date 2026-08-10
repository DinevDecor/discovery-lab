# Business Candidate Analyst

A downstream, read-only analyst over Constraint Archaeology's published evidence, with
two conceptually separate analytical modes sharing one registry:

- **Mode A — New Opportunity Discovery** (`analyst.py`): missing function / unmet need
  → business candidate. `candidate_type = NEW_MARKET`.
- **Mode B — Legacy Business Rearchitecture** (`rearchitecture/`): existing business →
  historical constraint → whether that constraint still binds → candidate.
  `candidate_type = OLD_BUSINESS_REARCHITECTURE`. See "Mode B" section below.

```
Sources -> Captures -> Observations -> Anomalies -> Constraint Archaeologist
                                            |
                                            v
                          Business Candidate Analyst -> Business Candidate Registry
```

It reads `constraint-archaeology-agents/data/{observations.jsonl,anomalies.json,
latest-evaluations.json}` and produces its own registry
(`data/candidate_events.jsonl`, `data/candidates.json`) plus a dated report under
`reports/`. It never writes to Constraint Archaeology's files, never calls a model,
and never touches the network — see `CONTRACT.md` and `tests/test_safety.py`.

## Why fully deterministic, not model-assisted

The task this package implements explicitly forbids promoting a candidate because a
pattern "sounds like a good startup idea." The most direct way to guarantee that is to
never let a model score or classify candidates at all: every dimension in
`dimensions.py` and every lifecycle rule in `lifecycle.py` is a plain keyword/structural
heuristic over fields the Sensor Agent already extracted (`pain`, `current_carrier`,
`failure_mode`, `confidence`, ...). This also means the offline test suite needs no
`ANTHROPIC_API_KEY` and the real run below needed no network access either.

## Run

```bash
python3 run_business_candidate_analyst.py          # runs Mode A, then Mode B
python3 run_business_candidate_analyst.py --skip-mode-b   # Mode A only
```

Reads from `../constraint-archaeology-agents/data` by default (`--ca-data-dir` to
override), writes to `./data` and `./reports`. Safe to re-run: idempotent on
unchanged evidence for both modes (see `tests/test_registry.py`,
`tests/test_rearchitecture_integration.py`). Mode B reads whatever registry state
Mode A just wrote and continues its `BC-XXXX` id sequence — the two modes never
allocate colliding candidate ids.

```bash
python3 -m unittest discover -s tests
```

106 offline, deterministic tests. No network, no model calls, no fixtures larger than
a handful of synthetic observations.

## The fourteen evaluation dimensions

`dimensions.py` answers every item the task requires, each as `EVIDENCED` (with the
`observation_id`s actually used) or `INSUFFICIENT_DATA`: underlying job/problem, pain
severity, economic/financial consequence, frequency/repetition, identifiable buyer,
current workaround, why existing solutions fail, potential product/function (see
below), willingness-to-pay evidence, scalability, evidence diversity, independent
observation/source count, contradictory evidence, confidence/evidence quality.

`potential_product_function` is explicitly marked **framing, not evidence** in its own
`DimensionResult.note` — it is a paraphrase of the Sensor Agent's own
`hidden_function_hint`, never an invented pitch, and `lifecycle.py` never uses it as a
gating condition for any state transition. This is the concrete guard against
"promoted because it sounds like a good idea."

## Lifecycle: WATCH → VALIDATING → INVESTIGATE → PROMISING, plus REJECTED

State is **recomputed from current evidence on every run**, not a ratchet — see
`lifecycle.py`'s module docstring. A candidate can rise (strengthened) or fall
(weakened) as evidence accumulates or as Constraint Archaeology's own anomaly
membership changes; the append-only event log means neither direction erases the
record of what was true before.

| Transition | Requires |
|---|---|
| create at WATCH | `identifiable_buyer`, `current_workaround`, `why_solutions_fail` all EVIDENCED |
| → VALIDATING | ≥2 distinct sources AND `economic_consequence` EVIDENCED |
| → INVESTIGATE | ≥3 distinct sources (matches Constraint Archaeology's own `--min-independent-sources` default) AND `willingness_to_pay` EVIDENCED AND no contradiction observed |
| → PROMISING | `willingness_to_pay`, `economic_consequence`, `scalability` all EVIDENCED AND `pain_severity == SEVERE` |
| → REJECTED | every Constraint Archaeology evaluation (`latest-evaluations.json`) backing this candidate returned `KILL`, and at least one anomaly has actually been evaluated. This is the **only** implemented rejection trigger — heuristic contradiction markers are surfaced in the report but never auto-reject on their own; a keyword match is too weak a signal to justify rejection by itself. |

All thresholds live in `config/thresholds.json`, not scattered as magic numbers in
code, so the rubric is inspectable without reading source.

## Deduplication: same underlying opportunity, not same wording

`signature.py` classifies each group of observations into a `buyer_bucket`
(`api_consumer` / `operator`) and a `function_class` (six generic, domain-agnostic
buckets: `resource_visibility`, `trust_dispute`, `access_gating`, `workaround_labor`,
`state_recovery`, `capacity_timing`) via small fixed keyword taxonomies — the same
style as `ca_agents.memory.classify_function`, independently implemented so this
package has zero import dependency on `ca_agents`.

Two groups merge into one Business Candidate only if:

1. **Same source URL** (short-circuit) — two observations extracted from the literal
   same capture are not independent evidence of two opportunities, they're one piece
   of evidence read twice. Always merges.
2. Otherwise: `buyer_bucket` AND `function_class` both match (neither the `unknown` /
   `unclassified` fallback), **and** the two groups' text hits at least
   `min_shared_function_keywords` (2) of the *same specific* keywords from the matched
   function_class's own list — not merely the same bucket. A generic-word Jaccard
   floor on workaround/failure wording is available as a fallback path.

Grouping compares each new anomaly against every existing group's **anchor** — the
observations of the first anomaly that founded that group — never against the group's
full accumulated text. See "False-positive controls" below for why.

## False-positive controls (what the real run caught, and how it's addressed)

Building this iteratively against the real corpus caught two real precision bugs
before they shipped — recorded here because the task asked for a false-positive
controls section, not because the fixes are theoretical:

1. **Snowballing pooled comparison.** An early version compared each new anomaly
   against a group's *entire accumulated* text. As a group grew, its accumulated
   keyword-hit set grew too, making it steadily more likely that an unrelated anomaly
   would coincidentally share one generic word (e.g. "cost") with the pool. On the
   real corpus this merged a grid-curtailment/battery-storage anomaly and a
   private-GPU-hardware-procurement anomaly into an "AI inference cost" candidate.
   Fix: compare against a single fixed anchor observation set per group, never the
   growing pool (`analyst.py::_build_groups`).
2. **Substring-duplicated taxonomy keywords inflating the shared-keyword count.**
   `config/thresholds.json`'s keyword lists originally included both a word and its own
   inflection (`manual`/`manually`, `credit`/`credits`, `cost`/`costs`, ...). Because
   `manual` is already a substring of `manually`, a single occurrence of "manually"
   silently satisfied a `min_shared_function_keywords=2` bar on its own — letting
   "manually re-explaining project context to an AI tool," "manually analyzing
   compiler output," and "manually resolving invoice mismatches" merge into one
   candidate purely because they all use the word "manually." Fix: every taxonomy list
   is deduplicated so no entry is a literal substring of another entry in the same
   bucket (substring matching still catches the inflected forms; see thresholds.json's
   `_comment_taxonomy_dedup`).

Both are exercised by regression tests: `test_signature.py::
test_refuses_merge_on_single_shared_keyword_alone`,
`test_analyst_integration.py::test_never_merges_across_different_function_classes_despite_shared_buyer_bucket`.

**Known remaining limitation, accepted deliberately:** anchor-only comparison means a
genuine A–B–C chain, where B shares vocabulary with both A and C but A and C share
nothing directly, will not fully merge — the middle anomaly does not "bridge" the two
ends. This is read as the gate correctly declining a merge it cannot itself evidence,
not a bug to route around; `ca_agents.same_mechanism_gate` accepts the same tradeoff
for the same reason (comparing against a representative observation, not a pooled
cluster). Concretely, this is why the real run below produced **three separate**
WATCH candidates for the AI-usage/cost/quota theme rather than one merged candidate —
each pair is tightly evidenced, but the deterministic gate would not connect all three
without inventing a stronger link than the text supports.

The buyer/function-class taxonomies are also necessarily coarse (2 × 6 buckets over
146 real anomalies) — false merges within a bucket are structurally possible even
after these fixes, which is exactly why every merge decision is written into
`merge_reasons` in the registry event, not just applied silently. Any merge can be
audited back to the specific keywords or URL that justified it.

## The seed question: AI usage / quota / credit / cost observability

The task asked whether existing evidence justifies creating this theme as a WATCH
candidate, without hard-coding it as a preferred hypothesis. Running the analyst
against the real corpus (146 anomalies, 157 observations, as of 2026-08-10) answers
this from evidence, not from the prompt: **yes**, and it surfaces as three distinct,
evidence-grounded WATCH candidates rather than one:

- **BC-0004** (`api_consumer` / `resource_visibility`) — two Hacker News observations
  from the same article, on developers absorbing LLM inference costs with no
  real-time visibility into token consumption before the bill arrives.
- **BC-0038** (`api_consumer` / `trust_dispute`) — two `discourse:openai-devs`
  observations, on a customer unable to get vendor billing telemetry to explain a
  credit deduction, and a related metering-verification report.
- **BC-0039** (`api_consumer` / `resource_visibility`) — two more
  `discourse:openai-devs` observations, on manually tracking remaining quota
  percentage and needing to time-shift usage around opaque reset cycles.

None of the three reached VALIDATING, and the reason is worth stating precisely
because it is the same "independent sources" discipline Constraint Archaeology itself
applies: each candidate has 2 *observations*, but both come from the same URL (the
Sensor Agent extracted two Observations from one Capture), so `evidence_diversity`
reports only **1 distinct source** per candidate — below VALIDATING's 2-source floor.
BC-0038 and BC-0039 already have `economic_consequence` and `willingness_to_pay`
EVIDENCED; source diversity, not economic evidence, is what's missing. A second,
independently-sourced report of the same specific pain would be enough to advance
either one.

They deliberately were **not** merged into one candidate — see "False-positive
controls" above for exactly why the deterministic gate stops at three.

## Mode B — Legacy Business Rearchitecture

The question this mode exists to answer, per the task verbatim: **"What historical
constraint shaped this business, and does that constraint still exist today?"** AI is
deliberately just one of sixteen possible enablers (`config/rearchitecture_thresholds.
json`'s `enabler_taxonomy`) — cheaper sensors, smartphones, GPS, cloud infra, robotics,
better materials, cheaper energy, faster logistics, digital payments, standardization,
regulation change, demographic change, consumer behavior, financing models, cheaper
compute, and AI, weighted identically. Nothing in this mode assumes AI caused anything.

### Why this needed a different design than Mode A

Mode A works because Constraint Archaeology's Sensor Agent already extracts exactly
the fields Mode A's rubric needs (`pain`, `current_carrier`, `failure_mode`) from
present-tense pain reports. Mode B asks a harder question — a *historical causal*
claim ("why did this structure exist, and is that reason gone") — that raw tech-forum
text rarely states explicitly. Before writing any code, the real corpus was grepped
for constraint-shaped language; almost nothing existed (`used to`, `historically`,
`no longer necessary`, etc. — 9 coincidental hits, none of them real business
narratives). A handful of genuine business/industry observations existed (solar-grid
curtailment vs. battery storage cost, aircraft manufacturing capacity, mobile app
payment adoption in India, vending-machine site selection) and became the ground truth
this whole mode's taxonomy was validated against, the same way Mode A's taxonomy was
validated against real observations before being trusted.

### The eight-item checklist and the three-valued evidence scale

`rearchitecture/dimensions.py` answers: existing business/job-to-be-done, historical
constraint, evidence the constraint existed, evidence it may be weakened, legacy
structure, proposed rearchitecture, why now, potential economic effect. Every claim is
`OBSERVED` (the text itself states it), `INFERRED` (a structural pattern matched
without explicit causal language), or `INSUFFICIENT_DATA` — a three-valued scale,
not Mode A's binary `EVIDENCED`/`INSUFFICIENT_DATA`, because collapsing OBSERVED and
INFERRED together would hide exactly the distinction the lifecycle depends on.
`proposed_rearchitecture` is explicitly **framing only** (mirrors Mode A's
`potential_product_function`) — a templated hypothesis, never itself evidence, never a
gating condition.

**The most important honesty case this mode has to get right**: text mentioning the
old constraint is not evidence it has weakened. A real observation about Japanese
solar curtailment states, in the industry insider's own words, *"the batteries
everyone suggests aren't free"* — an explicit argument that the old constraint
(battery storage cost) **still binds**. `taxonomy.py` keeps `still_binding_markers`
and `weakening_markers` as separate marker sets so this case reports
`evidence_constraint_weakened: INSUFFICIENT_DATA` with the note *"text argues the
constraint is STILL binding, not weakened — this is not a gap to fill, it is evidence
against the candidate"*, rather than false-positiving on the mere mention of batteries.

### Lifecycle and the no-AI-bias rule

Same five states as Mode A, reused rather than duplicated, but every rung is stricter
because historical-causal evidence is harder to confirm than a present-tense pain
report:

| Transition | Requires |
|---|---|
| create at WATCH | `historical_constraint` at least INFERRED AND `legacy_structure` OBSERVED |
| → VALIDATING | `historical_constraint` OBSERVED AND `evidence_constraint_weakened` at least INFERRED AND **at least one non-AI enabler identified** |
| → INVESTIGATE | `evidence_constraint_weakened` OBSERVED AND `why_now` OBSERVED AND `potential_economic_effect` OBSERVED AND **at least one non-AI enabler identified** |
| → PROMISING | entire evidence chain OBSERVED (nothing merely INFERRED) AND ≥2 distinct sources |
| → REJECTED | same trigger as Mode A: every evaluated Constraint Archaeology anomaly backing this candidate returned `KILL` |

The no-AI-bias rule lives in `lifecycle.py`, not `dimensions.py`, because it is a
**lifecycle** decision, not an evidence-quality one: `why_now` can honestly be
OBSERVED with "ai" as the only enabler in the text — that's an accurate reading. What
must not happen is treating that alone as sufficient to advance past WATCH. Both
required regression tests live in `tests/test_rearchitecture_lifecycle.py::
NoAIBiasTests`: a candidate with **zero** AI-related evidence reaches VALIDATING on a
non-AI enabler (`test_no_ai_bias_positive_case_reaches_validating_with_zero_ai_
evidence`), and an otherwise-identical candidate whose only enabler evidence is "AI
could automate this" is capped at WATCH with an explicit gap
(`test_ai_only_justification_is_not_sufficient`). A third test confirms AI is not
disqualifying when it appears *alongside* a real structural enabler — only "AI alone"
is refused.

### Grouping: simpler than Mode A, and why

Two anomalies group into one Mode B candidate only when they share an observation
URL (`rearchitecture/analyst.py::_build_groups`, a union-find over shared URLs) — not
Mode A's buyer/function signature gate. A historical-constraint claim is grounded in
one narrative source; it isn't a pattern expected to recur worded differently across
independent sources the way a business opportunity is. Concretely: the real corpus's
solar-curtailment story was split by Constraint Archaeology's own mechanism gate into
two separate anomalies (`ANOM-0067`, `ANOM-0101`) — different technical failure
mechanisms, same article. Mode B's URL grouping recombines them into one candidate;
Mode A's dedup logic would not (nor should it — they're not a recurring business
pattern across sources).

### False-positive controls specific to Mode B

Iterating against the real corpus caught a second, distinct class of false positive
from Mode A's: **bare single-word technical homonyms**. `agent` collided with "AI
agent" (this corpus's single most common phrase) and false-positived a dozen unrelated
dev-tool observations into `intermediation_trust`. `branch` collided with git/code
"branch" (a SAT-solver optimization post was misclassified `physical_presence` via
"branch and bound"). `buffer` collided with HTTP request buffering. `broker` collided
with MQTT message brokers. Fix: removed the bare ambiguous words, kept or added
multi-word phrases (`branch network`, `branch office`, `business broker`) that don't
collide with tech vocabulary. Regression tests:
`test_rearchitecture_taxonomy.py::test_physical_presence_requires_specific_phrase_
not_bare_branch`, `::test_intermediation_trust_does_not_fire_on_bare_agent`.

**Residual risk, reported honestly per the task's request**: several WATCH-level
candidates in the real run below (e.g. `continuous_oversight` classifications on
"coordinating multiple AI agent sessions," "AI agent regression testing") are
semantically real pattern matches (the text does describe manual coordination because
state isn't continuously observable) but describe **dev-tool UX friction, not an
existing business/industry** in the sense the task means. The taxonomy cannot
currently distinguish "this text describes a business" from "this text describes a
programming task that happens to use business-shaped words." Nothing in the lifecycle
promotes these past WATCH (they all lack `evidence_constraint_weakened` and `why_now`
entirely), so the blast radius is contained to the weakest, most-visibly-caveated
state — but a human reviewing the WATCH list should expect to discard some of these as
not-really-business-stories, not treat WATCH membership alone as a signal of quality.

## Limitations

- Keyword-based classification is coarse and will misclassify some observations (e.g.
  a small number of tie-breaks between generically-worded taxonomy buckets).
- `scalability` is a weak heuristic (≥2 sources AND ≥2 named vendors in a small fixed
  vendor list) — it under-detects scalability that doesn't happen to name a
  competing vendor in the observation text.
- `min_shared_function_keywords=2` trades recall for precision deliberately (see
  above); some genuinely-related pairs that only share one specific keyword will stay
  separate candidates rather than merge.
- No historical backfill: candidates are only ever created going forward from the
  first run that produced `data/candidate_events.jsonl`, mirroring
  `constraint-archaeology-agents/FINDINGS_LEDGER.md`'s own no-backfill rule.
- Mode B's `constraint_taxonomy` (seven categories) and `enabler_taxonomy` (sixteen
  categories) are, like Mode A's, necessarily coarse keyword buckets over a corpus that
  is overwhelmingly dev/tech content, not business-history writing — see Mode B's
  "false-positive controls" section for the concrete residual risk this produces and
  why the lifecycle's stricter bars contain it.

## Review questions (Mode B)

1. **Can Mode B be implemented meaningfully with the current deterministic
   architecture?** Partially, and unevenly across the eight fields. `legacy_structure`
   and `existing_business_or_jtbd` are as reliable as Mode A's equivalent fields
   (direct reuse of Sensor Agent extraction). `historical_constraint` and `why_now`
   are meaningful *when they fire OBSERVED* (explicit causal/change language), which
   the real run shows happens for genuine cases (the India-payments candidate) — but
   the INFERRED case (pattern matched, no stated reason) is a much weaker signal that
   a human should treat as a hypothesis prompt, not a finding. `evidence_constraint_
   weakened`'s still-binding-vs-weakening distinction works well and was the single
   most important honesty check to get right. Nothing here required an LLM call, and
   per the task's instruction not to force one, none was added — but this is a
   narrower, more caveated result than Mode A's, not an equally strong one.
2. **Are heuristics producing semantic false positives?** Yes, two distinct classes,
   both described above with real examples and both mitigated: (a) bare-word
   technical/business homonyms (`agent`, `branch`, `buffer`, `broker`) before the
   taxonomy cleanup — fixed; (b) genuine structural-pattern matches on text that
   describes dev-tool friction rather than an actual business/industry — not fully
   fixable with keyword matching alone, contained by capping these at WATCH since they
   never produce `evidence_constraint_weakened` or `why_now` evidence.
3. **Candidates found in the real corpus** (146 anomalies, 157 observations, as of
   2026-08-10): **12 candidates**, all `WATCH` except one `VALIDATING`. See
   `reports/business-candidates-2026-08-10.md`'s "Legacy Business Rearchitecture
   Candidates" section for the full eleven-field breakdown of each. Zero were forced;
   95 anomaly groups were considered and rejected at the WATCH bar for lack of any
   structural-constraint pattern.
4. **Which candidates genuinely depend on an expired/weakening constraint rather than
   generic "automation"?** One: **BC-0058**, the mobile-app-payments-in-India candidate
   (`payment_or_market_access`) — `historical_constraint` OBSERVED, `evidence_
   constraint_weakened` OBSERVED, enablers `digital_payments` + `demographic_change`,
   zero AI involvement anywhere in its evidence. It is the only candidate in the real
   run whose full chain (constraint existed → constraint weakened → non-AI enabler
   named) is OBSERVED rather than INFERRED, which is why it is the only one to reach
   VALIDATING. The solar-curtailment and aircraft-manufacturing candidates have
   OBSERVED historical constraints but explicitly do **not** have weakening evidence
   (the former argues the opposite) — correctly capped at WATCH, not silently dropped.
5. **What evidence is missing?** For the VALIDATING candidate: a second,
   independently-sourced report of the same specific constraint (only one source,
   `hacker_news`) and any explicit cost/speed/margin/etc. language (`potential_
   economic_effect` is its only INSUFFICIENT_DATA field). For the WATCH-level
   candidates: overwhelmingly, `evidence_constraint_weakened` and `why_now` — the
   corpus documents present-tense pains and, occasionally, why a legacy structure
   exists, but essays explaining *why a known constraint is going away* are rare in
   forum/HN-style content. This is a property of the source corpus, not a fixable gap
   in the code.
6. **Should Mode B remain inside this agent or become a separate agent later?**
   Remain inside, for now. It shares the registry, candidate-id space, provenance
   model, and safety boundary with Mode A, and reuses Mode A's `evidence_reader.py`
   and `rejection_trigger` outright — splitting it out today would duplicate all of
   that infrastructure for a mode that produced 12 candidates from one corpus pass.
   Revisit if Mode B's own taxonomy grows enough (more constraint categories, a
   genuinely different grouping strategy) that it stops being a thin sibling of Mode A
   and starts needing its own release cadence or its own data-quality guarantees.
