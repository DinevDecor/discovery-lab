# Project Tool Radar — contract

Purpose: preserve high-signal external software/tool discoveries that may save build time or materially inform an active DinevDecor project.

This stream is **not** Business Candidate Analyst evidence and must never change CA/BCA lifecycle state. It is a separate derived operational stream.

## Source

Current intake source: Product Hunt Daily / The Leaderboard emails available through the user's Gmail connection.

The source email is retained by `source_email_id`, timestamp and subject. Product descriptions are source-facing text; project-fit fields are derived analysis and must not be presented as external evidence.

## Storage

`data/tool_signals.jsonl` is append-only. One line = one product mention evaluated against the current project context.

Identity is `signal_id = tool:<source_email_id>:<normalized-product-name>`.

Duplicate rule: the same `(source_email_id, product)` pair must never be appended twice. A product mentioned in a later newsletter may create a new signal because it is a new dated source event.

Earlier lines are never edited or deleted. Corrections are new lines with `supersedes_signal_id`.

## Required fields

- `signal_id`
- `source_email_id`
- `source_email_ts`
- `source_subject`
- `product`
- `source_description`
- `project_fit_en`, `project_fit_bg`
- `use_type` — one of `USE_NOW`, `CHEAP_TEST`, `COMPETITIVE_ARCHAEOLOGY`, `WATCH`, `IGNORE`
- `build_vs_buy_en`, `build_vs_buy_bg`
- `why_it_matters_en`, `why_it_matters_bg`
- `cheapest_test_en`, `cheapest_test_bg`
- `risk_overlap_en`, `risk_overlap_bg`
- `verdict_en`, `verdict_bg`
- `recorded_at`

`source_url` is optional and may be stored only when it is directly present in the source email. Do not invent or reconstruct URLs.

## Automation boundary

The daily Project Tool Radar may append to **only** `tool-radar/data/tool_signals.jsonl`.

It may not:
- modify CA/BCA, Stage 1–4, Ground Truth or Trust Engine records;
- install/buy a product;
- migrate a repository or source of truth;
- create a permanent agent/platform;
- turn a tool recommendation into evidence for a business candidate.

A failed write must be reported; it must never be silently replaced by fabricated persistence.

## Mobile Console

The Mobile Console treats Tool Radar as read-only derived operational data. It does not write back to this stream.