# Contract — X Signal Probe v0.1 (`x-signal-probe/`)

Core Principle: **Bounded, read-only, probe-only. Answer one pre-registered question.
Never a production source.**

This is a **tool contract**, matching the precedent of `observation-agent/CONTRACT.md`
and `business-candidate-analyst/CONTRACT.md` — not a governance/Employee Role contract.

## Position (or rather, lack of one) in the pipeline

```
X API  ──▶  x-signal-probe (isolated)  ──▶  probe-observations.jsonl + report
```

This package has **no position in the Discovery Lab pipeline**. It does not sit
between any two existing stages, is never invoked by `run_daily_pipeline.py`, and
is never invoked by `constraint-archaeology-daily.yml`. Its own workflow
(`.github/workflows/x-signal-probe.yml`) is `workflow_dispatch`-only and entirely
separate.

## Pre-registered hypothesis

See `README.md`'s "Hypothesis" section for the frozen text. It was written before
the first API call and must not be edited after results are seen.

## Scope of authority

Read-only against the X API (X API v2 recent-search endpoint) and read-only against
two already-published Discovery Lab files, for its own existing-source-duplication
check only:

- `constraint-archaeology-agents/data/observations.jsonl`
- `capability-observatory/data/observations.jsonl`

No authority beyond producing its own output is granted:

- `x-signal-probe/data/probe-observations.jsonl` (append-only, probe-only)
- `x-signal-probe/reports/x-signal-probe-<date>.md`

Every path this tool ever opens in a writing mode lives under `x-signal-probe/`
itself, and only `probe.py` (the observation ledger) and `report.py` (the run
report) ever open a file in a writing mode — enforced by `tests/test_safety.py`,
not just this document.

## Hard boundary — this tool MUST NOT

- write to, or otherwise touch, any Constraint Archaeology file
  (`constraint-archaeology-agents/data/**`, `.../reports/**`) or any Business
  Candidate Analyst file — read-only against two of CA's own data files, for
  duplication-checking only, never a write;
- be invoked by, or invoke, `run_daily_pipeline.py` or
  `constraint-archaeology-daily.yml` — there is no code path in either direction;
- feed X-derived observations into CA promotion, BCA promotion, any lifecycle state
  change, or any Claim/Trust ledger — X results stay probe-only observations,
  permanently, unless a separate, explicit human decision changes this contract;
- import `ca_agents` or `business_candidate_analyst` — enforced statically by
  `tests/test_safety.py`;
- call a language model of any kind — classification (retweet/marketing filters,
  the three dedupe tiers, the PASS/FAIL-candidate label) is fully deterministic,
  so "the model liked this post" can never be why a candidate advances;
- persist X post text, a quote, or an author handle/id anywhere it writes —
  `data/probe-observations.jsonl` and the report carry reference/provenance fields
  only (`post_id`, `canonical_url`, `text_hash`, timestamps, `query_id`/`family`,
  `classification`) — enforced by `tests/test_safety.py`'s static field check and
  `tests/test_secret_never_persisted.py`'s dynamic check on both the bearer token
  and post text;
- upload raw X post text as a GitHub Actions artifact in v1 — the workflow uploads
  only `data/` and `reports/`, which by construction never contain post text;
- echo `X_BEARER_TOKEN`, or any other secret, into logs, files, or artifacts;
- fabricate an API-cost figure — cost fields are `null`/"not computed" unless a
  `--cost-per-post-usd` value is explicitly supplied for that run;
- fall back to a hardcoded credential, or silently continue, when
  `X_BEARER_TOKEN` is missing — it must fail the run clearly;
- run on a schedule before a human has reviewed at least one successful bounded
  manual run — `.github/workflows/x-signal-probe.yml` is `workflow_dispatch` only;
- commit anything to the repository from its workflow — outputs are uploaded as a
  short-retention build artifact, the same pattern `observation-agent.yml` uses,
  never a `git commit`/`git push` step;
- retry without bound, or paginate without bound — `max_pages`, `max_results`,
  `max_posts_per_run`, and retry count are all hard caps, never removed or made
  "unlimited" by a config change without a new, explicit human decision;
- claim an X-derived observation is "earlier" than another public source without
  an explicit side-by-side timestamp comparison in the report.

## Rights

- The right to return zero genuinely-incremental candidates for a run. Finding
  something is not a goal this tool optimizes for.
- The right to classify a candidate as `existing_source_duplicate` on a lexical
  match even when its wording differs from the existing observation — different
  text is not independent evidence (CLAUDE.md).
- The right to leave `automated_signal` at `INSUFFICIENT_DATA` whenever the sample
  is smaller than its documented floor (`evaluator.MIN_POSTS_FOR_VERDICT`).
- The right to omit author identifiers, handles, or any other field not actually
  needed for provenance or dedupe (data minimization).

## Responsibilities

- Cite `canonical_url` for every candidate the report lists, so a human can verify
  it directly against the live post — never asserting the post's content itself.
- Record every API/HTTP/rate-limit/billing failure truthfully in the run's error
  list; never let a probe-run failure propagate into, or block, the daily pipeline.
- Keep the pre-registered query set (`config/queries.json`) frozen once a real run
  has happened against it; a later change to search strategy is a new file
  (`queries.iteration-2.json`, etc.) plus a README changelog entry, never a silent
  edit in place.
- Report the automated PASS/FAIL-candidate label as a mechanical signal only, and
  say so in the report itself — a genuine verdict requires human review.

## Executor independence

This contract binds the tool, not whoever runs it — same precedent as
`observation-agent/CONTRACT.md`.

## Human Quality Audit (Run 1) — additional boundary

`audit/README.md` documents a separate, one-off audit of Run 1's
`candidate_incremental` observations. It inherits every rule above and adds:

- selection (`select_audit_sample.py`) is a pure function over already-persisted
  metadata — never the X API, never `config/queries.json`;
- rehydration (`review_audit_sample.py` / `audit_client.py`) makes **exactly one**
  X API request, against the ID-lookup endpoint only — never `search_recent`,
  never a fallback search, never a second lookup call;
- a selected post the API does not return is recorded once as `UNAVAILABLE` and is
  **never replaced** by drawing another post;
- rehydrated post text is never written to a file, git commit, CI log, or chat
  transcript — `review_audit_sample.py` is local-reviewer-only by design, not by
  incidental limitation;
- the reviewer never sees the automated `classification`, a running tally, or
  other reviewers' verdicts while reviewing.

## Revocation and change

This tool may be modified, extended, or retired at any time by direct repository
change. A change that would grant it write access to any Constraint Archaeology or
Business Candidate Analyst file, a code path into `run_daily_pipeline.py`, a model
call, persistence of raw X post text, or a move to scheduled (non-manual) execution
is out of scope for this contract entirely and needs a new, explicit human decision.
