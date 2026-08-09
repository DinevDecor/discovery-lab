# Constraint Archaeology Agents — MVP

A three-stage daily anomaly-discovery pipeline:

`public founder/business discussions -> Sensor Agent -> Evidence Memory -> Constraint Archaeologist -> daily brief`

It is deliberately **not** an idea generator. The Sensor is forbidden to recommend startups; Memory is forbidden to evaluate; the Archaeologist is forbidden to invent evidence.

## What runs today

- Hacker News newest stories via the public Algolia endpoint.
- Lobsters newest public stories via its JSON feed.
- DEV/Forem public posts from configured discussion/startup tags via the public articles API.
- Configured public Reddit community feeds when reachable.
- Product Hunt newest launches via the official GraphQL v2 API (requires `PRODUCT_HUNT_TOKEN`).
- Five configured public Discourse forums, newest-topics-first.
- Cross-source/crosspost duplicate detection, so a story reposted across sources can't inflate independent-source counts.
- Claude extraction of evidence-grounded operational observations.
- Persistent JSONL observation memory.
- Deterministic clustering into anomaly dossiers.
- Constraint Archaeology v0.5 evaluation only after an anomaly has evidence from 3 independent sources.
- `KILL / WATCH / INVESTIGATE` daily report.

The collector is deliberately multi-source. A blocked or unavailable community is recorded as an error in the daily report but does not stop the pipeline. Reddit is therefore a supplementary sensor, not a single point of failure.

## Capture budget is source-balanced, not first-come-first-served

`run_daily.py --max-captures` (default 80) bounds how many fetched captures reach the
sensor each day. Every source is still fetched in full (subject to its own per-source
`limit` in `config/sources.json`), but admission into that shared 80-item budget is a
round-robin draw across sources (`ca_agents/budget.py`), not a slice of the
source-order-concatenated list. Before this existed, `HN(40) + Lobsters(30) + one DEV
tag(25)` alone exceeded 80, so every source configured after them — all of Reddit,
Product Hunt, and every Discourse forum — silently received zero captures in every real
run, regardless of whether their own fetch succeeded. Their historical zero-observation
count was **starvation, not a signal-quality finding** — see
`tests/test_budget.py::test_reproduces_real_sources_json_shape` and
`tests/test_collector.py::test_high_volume_early_source_cannot_starve_product_hunt_or_discourse`
for the regression coverage. The daily report's new "Source telemetry" table shows
`fetched`/`admitted`/`observations`/`duplicates`/`errors` per source so this can't go
unnoticed again.

## Source adapter access notes

### Product Hunt

- **Access method:** official GraphQL v2 API (`https://api.producthunt.com/v2/api/graphql`).
  There is no public, unauthenticated endpoint for post listings any more — the old v1 REST
  API is retired. A request needs a **developer token** from an OAuth application registered
  at `https://www.producthunt.com/v2/oauth/applications`, passed as `PRODUCT_HUNT_TOKEN`.
  Without it, `collect_product_hunt` raises `CollectorError` — it never returns an empty
  list pretending nothing shipped today.
- **Rate limits:** PH enforces a complexity-based quota per token (documented as roughly a
  few thousand points per 15-minute window at the time this was written); this adapter's
  default `limit: 20` with 3 comments per post per run stays well under any plausible quota.
  Exact current numbers should be re-checked against `https://api.producthunt.com/v2/docs`
  before raising the request volume — this session could not reach that page to confirm
  (see "Sandbox network note" below).
- **What is captured:** product name, tagline, and up to 3 top comment bodies, folded into
  one Capture per post. **Vote counts and comment counts are read from the API response but
  never written into a Capture or Observation field** — popularity has no path into evidence
  strength anywhere in this adapter.
- **Evidence class:** Product Hunt is a **solution/emerging-market signal**, not a firsthand
  problem report — a maker's launch copy describes the pain they claim to solve, not a
  reporter's own experience of it. `ca_agents.sensor.cap_confidence_for_source` structurally
  caps confidence for `source == "product_hunt"` at 0.55 regardless of what the LLM extractor
  returns, and the sensor's system prompt tells it to treat PH text as marketing framing.
  This is enforced in code, not just requested in a prompt.

### Discourse

- **Access method:** each forum's own public JSON API — `<base>/latest.json?order=created`
  for newest-first topic listing, `<base>/t/<id>.json` for the topic detail (opening post +
  first reply). No authentication needed for public categories; this is Discourse's standard,
  documented `.json` suffix convention, not a scrape.
- **Sampling:** `order=created`, i.e. newest-by-creation-time — never `order=default`
  (activity/popularity) and never filtered by a pre-set problem-keyword list, per the task's
  requirement that Discourse sampling stay orthogonal to popularity and to what we're hoping
  to find.
- **Rate limits:** Discourse's out-of-the-box default is roughly 60 requests/minute per IP
  for anonymous JSON API access (site admins can lower or raise it). At `limit: 20` topics
  per forum per day, this adapter's request volume (~21 requests/forum/run: 1 listing + 20
  topic-detail calls) is trivial against that budget.
- **Chosen panel (5 forums, deliberately different domains):**

  | Forum | `community` | Domain |
  |---|---|---|
  | `discuss.python.org` | `python` | programming language / dev tooling |
  | `community.home-assistant.io` | `home-assistant` | home automation / consumer IoT |
  | `community.openai.com` | `openai-devs` | AI/ML developer tooling |
  | `forum.level1techs.com` | `level1techs` | PC hardware / enthusiast |
  | `community.fly.io` | `fly-io` | cloud infrastructure / hosting |

  All five are known Discourse instances with public categories, chosen for domain spread
  (language runtime, IoT/hardware, AI tooling, enthusiast hardware, cloud infra) so a
  cross-domain same-mechanism match means something. **Their live reachability could not be
  verified from this session** (see below) — this is a documented gap, not a claim of a
  completed check.
- **Evidence class:** an ordinary forum source, same standing as HN/Lobsters/DEV/Reddit — a
  Discourse topic is typically the poster's own account of a problem, not vendor copy, so it
  is not confidence-capped the way Product Hunt is. Each forum keeps its own
  `discourse:<community>` source label and is never merged with another forum.

### Cross-source/crosspost duplicate detection

`ca_agents/dedup.py` groups Captures that are the same underlying story republished across
sources — same canonical URL, or near-duplicate title (token Jaccard ≥ 0.72) from two
*different* sources — into a shared `story_group`. `memory.rebuild_anomalies` then counts a
second observation sharing a `story_group` already present in an anomaly as evidence (kept
in `observation_ids` for audit) but **not** as a new independent source. Same-source
near-duplicates are deliberately left to same-mechanism clustering, not this layer — a forum
having two similar threads is not a crosspost. See `tests/test_dedup.py` and
`tests/test_memory.py::test_crosspost_does_not_inflate_independent_sources`.

### Sandbox network note (this session only)

This session's outbound network is restricted to an organization allowlist. A direct probe
(`curl` to `api.producthunt.com` and to all five Discourse hosts) returned `403` at the
egress proxy with reason `connect_rejected: gateway answered 403 to CONNECT (policy denial)`
— confirmed for **every** existing source too (HN, Lobsters, DEV, Reddit), not just the new
ones. This is a fact about this session's network policy, not a finding about Product Hunt's
or these forums' own availability. The real probe in this PR ran the actual adapter code
against the real endpoints and recorded exactly what came back — a `CollectorError` for the
missing Product Hunt token, and a `URLError` (blocked tunnel) for each Discourse forum —
rather than fabricating sample output.

## Run

Python 3.11+, no third-party dependencies.

```bash
export ANTHROPIC_API_KEY=...
export PRODUCT_HUNT_TOKEN=...  # optional - Product Hunt is skipped with a recorded error if unset
python3 run_daily.py
```

Outputs live only under `data/` and `reports/`.

## GitHub Actions

`.github/workflows/constraint-archaeology-daily.yml` runs the pipeline daily and commits only generated `data/` and `reports/` artifacts back to its branch. Add repository secret `ANTHROPIC_API_KEY` before enabling the workflow. Optionally add `PRODUCT_HUNT_TOKEN` to enable the Product Hunt adapter — without it, Product Hunt is recorded as a source error each run and every other source is unaffected.

## Important MVP limitations

- Product Hunt requires a `PRODUCT_HUNT_TOKEN` (official OAuth developer token); without one it records a source error and fetches nothing, by design — see "Source adapter access notes" above.
- Indie Hackers is still not fetched — it has no public API or documented `.json`-style access at all, unlike Product Hunt (official GraphQL) or Discourse (per-forum JSON API), so scraping it would mean the same "don't scrape blindly" risk this file already warned about.
- Discourse forum reachability and the exact producthunt.com/v2/docs rate-limit numbers could not be re-verified from a sandboxed session with restricted network egress (see "Sandbox network note" above); re-check before raising request volume in production.
- Reddit can rate-limit or block hosted runners; failures are recorded in the report and do not abort the run.
- DEV tag quality varies, so evidence still has to survive independent-source clustering before Constraint Archaeology evaluates it.
- Clustering is intentionally simple in v0.1. The LLM never controls persistent IDs or the evidence threshold.
- This package lives under Discovery Lab for the MVP. It can be split into a dedicated repository after the pipeline proves useful.
