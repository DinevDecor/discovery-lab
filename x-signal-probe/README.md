# X Signal Probe v0.1

A small, bounded, read-only experiment. Not a new Discovery Lab source, not a
production integration. See `CONTRACT.md` for the hard boundary.

## The one question this probe answers

> Does X carry unique, early, and economically significant observations that
> Discovery Lab's current public-source set does not already find?

Nothing else. It does not decide whether X becomes a permanent source; that is a
separate, later, explicit human decision if (and only if) this probe's evidence
supports it.

## Hypothesis (pre-registered, frozen)

Written before the first API call. **Not edited after seeing results**:

> Public X posts contain recurring first-person reports of emerging operational or
> economic pain that provide incremental evidence beyond Discovery Lab's current
> public-source set.

## Search strategy

`config/queries.json` holds 25 pre-registered queries across the 14 signal families
from the task brief (unexpected cost/bill, cannot control/predict usage, manual
workaround, repeated failure, blocked workflow, waiting/queue/capacity, compliance
burden, unavailable infrastructure, forced workaround, tool fragmentation,
API/platform restriction, agent/AI operational failure, cloud/compute cost surprise,
business process bottleneck). Each query targets problem language / economic
consequence / workaround language, not trending keywords, and excludes retweets and
non-English text at the query level (`-is:retweet lang:en`).

**Frozen after run 1.** A later change to search strategy is a new file
(`queries.iteration-2.json`, etc.) referenced from a new changelog entry below, never
an edit to `queries.json` in place — so a query change is always visible as a
recorded experimental iteration, never a silent rewrite of what was actually tested.

### Changelog

- 2026-08-18 — `queries.json` created, 25 queries, run 1 not yet executed.

## Storage design (why no post text is ever persisted)

X's Developer Agreement requires honoring content deletion/edits and restricts
off-platform redistribution of full post text without the live interactive context.
A public git repository has no deletion-propagation mechanism, so **no raw X post
text, quote, or excerpt is ever written to disk by this package** — not to
`data/probe-observations.jsonl`, not to the rendered report, not to a workflow
artifact (v1 uploads only `data/` and `reports/`, which by construction never
contain post text).

Full post text exists **transiently, in memory, only for the duration of one probe
run** — used by the mechanical filters (`filters.py`) and the existing-source
similarity check (`existing_sources.py`) — then discarded. What gets persisted is a
reference/provenance layer only:

`source="x"` · `post_id` · `canonical_url` (`https://x.com/i/status/<post_id>` — X's
generic, username-independent permalink form, so no author handle needs to be
captured just to make a post referenceable) · `created_at` · `retrieved_at` ·
`query_id` · `query_family` · `text_hash` (SHA-256 of normalized text, for dedupe and
audit, never the text itself) · `probe_version` · `api_version` · `classification` ·
`matched_existing_observation_id` (when applicable).

**Author identifier omitted.** Neither dedupe (post_id is sufficient) nor
provenance/verification (canonical_url is sufficient — a human can open it directly)
actually needs an author id or handle, so per data minimization none is stored.

If raw-content persistence is ever needed for reproducibility, that's a separate,
explicit human decision with its own compliance design — not something this probe
backs into by accident.

`tests/test_secret_never_persisted.py` proves this dynamically: it runs the probe
against fake post text containing a distinctive marker and a fake bearer token, then
asserts neither string appears in any file the run wrote.

## Dedupe — three tiers, never conflated

1. **Duplicate retrieval** (`dedupe.py`) — the same `post_id` found by more than one
   pre-registered query in this run.
2. **Existing-source duplication** (`existing_sources.py`) — the same underlying
   problem already present in Discovery Lab via a different source/URL, checked by
   lexical similarity against `constraint-archaeology-agents/data/observations.jsonl`
   and `capability-observatory/data/observations.jsonl` (read-only). Different
   wording of an already-known pain does **not** count as independent evidence.
3. **Genuinely incremental** — passes both of the above, plus the mechanical
   retweet/marketing filters. These become "candidates for independent
   corroboration" in the report — reviewed by a human, never auto-promoted.

This is deliberately *not* the same-mechanism gate (`ca_agents.same_mechanism_gate`)
— no judge, no model call, no merge into any CA anomaly.

## Evaluation

Each run's report (`reports/x-signal-probe-<date>.md`) states: posts fetched, unique
posts, retrieval duplicates, filtered (retweet), filtered (marketing/spam-like),
already represented by existing sources, genuinely incremental candidates, API
errors, and — only if a per-post cost is explicitly configured — estimated cost,
cost per usable observation, cost per incremental observation. If cost is not
configured, those fields say so; they are never invented (`evaluator.py`).

`automated_signal` (`PASS_CANDIDATE` / `FAIL_CANDIDATE` / `INSUFFICIENT_DATA`) is a
**mechanical label, not the final verdict** — see `evaluator.py`'s documented
thresholds (`MIN_POSTS_FOR_VERDICT`, `MIN_INCREMENTAL_FOR_PASS_CANDIDATE`,
`MIN_INCREMENTAL_RATIO_FOR_PASS_CANDIDATE`). A genuine PASS/FAIL/INSUFFICIENT DATA
conclusion requires a human to review the listed candidates by their `canonical_url`.

## The adversarial question: earlier, or just more visible?

This probe does not automate an "earlier" claim. Where a genuinely-incremental
candidate is later manually corroborated against another independent public source,
compare `created_at` on both sides explicitly before saying X was earlier. Absent
that explicit comparison, "X found it" is not evidence "X found it first."

## Bounds (see `CONTRACT.md`; enforced in `client.py`/`probe.py`)

| Bound | Default |
|---|---|
| Pre-registered queries | 25 (`config/queries.json`) |
| Max results per query | 10 |
| Max pages per query | 1 (no pagination beyond page 1) |
| Max posts per run (global cap) | 200 |
| Max retries per query | 2, fixed backoff (2s, 4s), only on 429/5xx |

## Running it

Manual only. `python3 run_x_signal_probe.py` reads `X_BEARER_TOKEN` from the
environment and fails clearly (no fallback) if it is absent. In CI, this only ever
runs via `.github/workflows/x-signal-probe.yml`'s `workflow_dispatch` trigger — no
schedule exists yet, and the first real run against the live API requires an
explicit human trigger.

## Tests

Offline and deterministic — no live X API call anywhere in `tests/`. HTTP is mocked
via `client.search_recent`'s injectable `transport`/`sleep_fn` parameters (same
pattern as `ca_agents.collector`'s Product Hunt tests). Covers: missing-secret
behavior, bounded pagination/retries, API failure handling, the three dedupe tiers,
the mechanical filters, the evaluator's verdict thresholds, and — dynamically — that
neither the bearer token nor raw post text ever appears in any file the probe wrote.
