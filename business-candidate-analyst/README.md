# Business Candidate Analyst

A downstream, read-only analyst over Constraint Archaeology's published evidence:

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
python3 run_business_candidate_analyst.py
```

Reads from `../constraint-archaeology-agents/data` by default (`--ca-data-dir` to
override), writes to `./data` and `./reports`. Safe to re-run: idempotent on
unchanged evidence (see `tests/test_registry.py`).

```bash
python3 -m unittest discover -s tests
```

67+ offline, deterministic tests. No network, no model calls, no fixtures larger than
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
