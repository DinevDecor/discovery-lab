# Run-1 Human Quality Audit

A separate, bounded, one-off audit of Run 1's `candidate_incremental` observations
(108 of 109). Purpose: determine whether `candidate_incremental` actually
corresponds to useful Discovery Lab signal, since a 108/109 automatic-classification
rate is suspiciously high and may reflect the mechanical filters under-catching
noise rather than 108 genuinely strong signals. See `../CONTRACT.md` for the
package-wide boundary this audit inherits (no CA/BCA/Ledger/Trust Engine, no
schedule, no promotion, no text persistence).

This directory holds only the audit's own outputs — always metadata/verdicts,
never X post text:

- `run1-sample-<timestamp>.json` — the frozen, pre-registered 20-post selection.
- `run1-verdicts-<timestamp>.jsonl` — the human reviewer's A–E answers, append-only.
- `run1-audit-report.md` — computed rates, counts, and the pre-registered decision.

## Selection

`select_audit_sample.py` reads Run 1's real `data/probe-observations.jsonl`
(already downloaded from the Run-1 workflow artifact — this script never touches
the X API or `config/queries.json`), filters to `classification ==
"candidate_incremental"`, and freezes exactly 20 IDs **before** any rehydration.

**Algorithm** (`src/x_signal_probe/audit_selection.py`, `SELECTION_ALGORITHM_VERSION
= "0.1"`):

1. Group candidates by `query_family`; sort family names alphabetically.
2. Within each family, sort candidates by `post_id` ascending (a purely structural
   key, unrelated to content) — fixes the pre-shuffle order.
3. Apportion 20 slots across families by the largest-remainder method, proportional
   to each family's actual candidate count, capped at `MAX_PER_FAMILY = 3` — unless
   too few families hold any candidates for that cap to reach 20 at all, in which
   case the cap rises to `ceil(20 / n_families_present)` (`compute_effective_cap`),
   still fully deterministic and decided before any draw.
4. For each family with quota `q`, draw `q` items without replacement via
   `random.Random(f"{seed}|{family}").sample(...)`.
5. Sort the final 20 by `post_id` for stable file output (cosmetic only — does not
   affect which posts were chosen).

**Seed:** defaults to the SHA-256 of the `probe-observations.jsonl` file itself —
content that was fixed when Run 1 completed, before this audit was designed, so
the seed cannot have been chosen after seeing which posts it would select.

The frozen sample file records: `audit_id`, `run_id`, `selection_algorithm_version`,
`seed`, `target_sample_size`, `base_max_per_family`, `effective_max_per_family`,
`total_candidate_pool`, `families_present`, `selection_timestamp`, and the 20
selected entries (`post_id`, `query_family`, `query_id`, `canonical_url`,
`created_at`, `retrieved_at` — no `classification`, no text).

## Unavailable posts — pre-registered now, before any rehydration

If the X API ID lookup does not return a selected post (deleted, suspended,
protected, or otherwise not found), that post is recorded once, immediately, as
`availability = "UNAVAILABLE"` with every rubric field (`A`–`E`) also set to
`"UNAVAILABLE"` (`audit_models.unavailable_verdict`). It is **never replaced** by
drawing another post, and never silently dropped from the file. `audit_report.py`
treats `UNAVAILABLE` as *not-YES* on every rubric question — the rate denominator
stays fixed at 20 regardless of how many posts are unavailable, so unavailability
drags rates down rather than making a run with several dead links look artificially
cleaner than one with none.

## Rehydration

`review_audit_sample.py` makes **exactly one** X API request: the tweets
ID-lookup endpoint (`GET /2/tweets?ids=...`, `src/x_signal_probe/audit_client.py`),
covering all 20 frozen IDs in a single batched call (the endpoint accepts up to
100). `audit_client.py` never imports `client.search_recent`; `audit_review.py` and
`review_audit_sample.py` don't either — `tests/test_audit_safety.py` makes this a
build failure if it ever becomes false. No fallback search, no second lookup, no
retry with a different/smaller ID batch.

## How the reviewer sees content without permanent persistence

**Run `review_audit_sample.py` yourself, locally, in your own terminal — not
inside a hosted assistant session.** The script:

1. Fetches all 20 posts' text in one call, held only in local Python variables.
2. Prints each available post's text to your terminal, one at a time.
3. Prompts you for A–E and an optional note ("your own words only — do not paste
   the post text").
4. Appends only the resulting `AuditVerdict` (no text field exists on that type —
   see `audit_models.py`) to `run1-verdicts-*.jsonl`, flushing immediately.
5. Drops its only reference to the fetched text at the end of each loop iteration.

Nothing under this design ever writes X post text to a file, a git commit, a CI
log, or a chat transcript. Running the same script inside a hosted chat session
would make the fetched text part of *that session's own transcript* — a real,
separate persistence surface with its own retention, outside this repository's
control — which is exactly why this step is local-only by design, not a technical
limitation of the code itself.

**Where / how long / who / how it disappears / why compliant:** text exists only
in the reviewer's local process memory and terminal scrollback, for the duration
of one review pass (minutes); only the person running the script sees it; the
process exiting clears it, nothing was ever serialized; this is equivalent to a
human opening each post directly (which `canonical_url` alone would already allow,
without any API call) — the batched API call only saves 20 manual browser clicks,
it does not create a new copy anywhere that outlives the review pass.

## Blinding

The reviewer sees the content needed for A–E and nothing else. Specifically never
shown: the automated evaluator's `classification` (dropped from the frozen sample
file entirely — every entry is `candidate_incremental` by construction, so showing
it would be a no-op here, but it's dropped on principle for when this pattern is
reused where it wouldn't be); any running tally of YES/NO counts while reviewing
(the verdicts file is write-only during the loop, never read back); other
reviewers' verdicts (same write-only guarantee — a future multi-reviewer pass would
still never read prior rows mid-session). Rates, counts, and the decision are
computed only by `render_audit_report.py`, a separate script run after all 20 are
recorded — never live during review.

## Decision thresholds (pre-registered, unchanged from the task that specified
this audit)

Based on `e_corroboration_worthy == "YES"` count out of the fixed 20:

| Count | Decision |
|---|---|
| ≤ 4 | `FAIL` — too much noise for the current query/filter design; do not integrate or schedule |
| 5–9 | `INSUFFICIENT_DATA_ITERATE` — real signal, but current search/filter design is too weak; do not integrate or schedule; a later Query Iteration 2 may be justified |
| ≥ 10 | `PASS_CANDIDATE` — at least half the sample deserves independent corroboration; still not authorization to integrate or schedule |

No outcome of this audit authorizes integrating, scheduling, or promoting X to a
production Discovery Lab source. The next gate, if any, is actual independent
corroboration of a smaller subset.
