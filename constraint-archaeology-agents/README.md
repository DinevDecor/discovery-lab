# Constraint Archaeology Agents — MVP

A three-stage daily anomaly-discovery pipeline:

`public founder/business discussions -> Sensor Agent -> Evidence Memory -> Constraint Archaeologist -> daily brief`

It is deliberately **not** an idea generator. The Sensor is forbidden to recommend startups; Memory is forbidden to evaluate; the Archaeologist is forbidden to invent evidence.

## What runs today

- Hacker News newest stories via the public Algolia endpoint.
- Lobsters newest public stories via its JSON feed.
- DEV/Forem public posts from configured discussion/startup tags via the public articles API.
- Configured public Reddit community feeds when reachable.
- Claude extraction of evidence-grounded operational observations.
- Persistent JSONL observation memory.
- Deterministic clustering into anomaly dossiers.
- Constraint Archaeology v0.5 evaluation only after an anomaly has evidence from 3 independent sources.
- `KILL / WATCH / INVESTIGATE` daily report.

The collector is deliberately multi-source. A blocked or unavailable community is recorded as an error in the daily report but does not stop the pipeline. Reddit is therefore a supplementary sensor, not a single point of failure.

## Run

Python 3.11+, no third-party dependencies.

```bash
export ANTHROPIC_API_KEY=...
python3 run_daily.py
```

Outputs live only under `data/` and `reports/`.

## GitHub Actions

`.github/workflows/constraint-archaeology-daily.yml` runs the pipeline daily and commits only generated `data/` and `reports/` artifacts back to its branch. Add repository secret `ANTHROPIC_API_KEY` before enabling the workflow.

## Important MVP limitations

- Product Hunt and Indie Hackers are not yet fetched because reliable automated access should be implemented source-by-source rather than scraped blindly.
- Reddit can rate-limit or block hosted runners; failures are recorded in the report and do not abort the run.
- DEV tag quality varies, so evidence still has to survive independent-source clustering before Constraint Archaeology evaluates it.
- Clustering is intentionally simple in v0.1. The LLM never controls persistent IDs or the evidence threshold.
- This package lives under Discovery Lab for the MVP. It can be split into a dedicated repository after the pipeline proves useful.
