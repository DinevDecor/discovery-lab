# X Signal Probe run

Probe-only observations. Not read by, and never promoted into, Constraint Archaeology, Business Candidate Analyst, or any Claim Ledger - see CONTRACT.md.

## Bounds used this run
- queries_configured: 25
- max_results_per_query: 10
- max_pages_per_query: 1
- max_posts_per_run: 200
- max_retries_per_query: 2

## Metrics
- posts fetched: 111
- unique posts (newly admitted this run): 3
- cross-run duplicates (already in the ledger from a prior run): 108
- retrieval duplicates (repeated within this run): 0
- filtered (retweet): 0
- filtered (marketing/spam-like): 0
- already represented by existing sources: 0
- genuinely incremental candidates: 3
- API errors: 0
- estimated cost (USD): not computed - no cost-per-post configured for this run
- cost per usable observation (USD): n/a
- cost per incremental observation (USD): n/a

## Automated signal: PASS_CANDIDATE
3 genuinely incremental candidates out of 3 unique posts - requires human corroboration review, not a final PASS

**This is a mechanical label, not a final PASS/FAIL/INSUFFICIENT DATA verdict.** A genuine conclusion requires a human to review the incremental candidates below against their live canonical URLs, including whether X was actually earlier than another independent public source or just more visible.

## Candidates for independent corroboration

No post text is stored or shown here by design (data-minimization rule, CONTRACT.md) - open each canonical URL directly to review the post.

| post_id | canonical_url | query_family | created_at | retrieved_at |
|---|---|---|---|---|
| 2090197493598593071 | https://x.com/i/status/2090197493598593071 | repeated_failure | 2026-08-19T22:01:31.000Z | 2026-08-20T09:52:08.062527+00:00 |
| 2090065531059462492 | https://x.com/i/status/2090065531059462492 | compliance_burden | 2026-08-19T13:17:08.000Z | 2026-08-20T09:52:08.062527+00:00 |
| 2090376168533082413 | https://x.com/i/status/2090376168533082413 | forced_workaround | 2026-08-20T09:51:30.000Z | 2026-08-20T09:52:08.062527+00:00 |
