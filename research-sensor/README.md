# Research Reality Sensor 001

`EXEC-010`'s implementation: the second **External Evidentiary Sensor**
in the Discovery Lab ecosystem (per `EXEC-009`'s two-family model,
after `reality-sensor/`), dedicated to scientific research relevant to
`KOD`, `Generative Discovery Engine`, and the wider Discovery Lab
ecosystem. It is a research **opportunity detector**, not a literature
summarizer — every registered signal must answer "why should Discovery
Lab care?", not just "what does the paper say?" See `ARCHITECTURE.md`
for the full design and `CONTRACT.md` for its operating contract.

## The one thing to understand before anything else

This package's own Python source **never makes a network call** —
enforced by `tests/test_safety.py`, not just documented. Capture (the
actual internet-fetching step) and processing (clustering, trust
policy, confidence scoring, experiment extraction, registry, briefs)
are deliberately split, the same reasoning `reality-sensor/ARCHITECTURE.md`
gives in full and this package's own `ARCHITECTURE.md` restates for
this domain.

## How to run it

Step 1 — capture (external, point-in-time; a human or an AI executor
performs this against the fixed `config/source-registry.json` list,
respecting its `processing_budget`, and writes a raw-captures JSON file
— see `docs/RESEARCH-SCHEMA.md`'s "`RawPaperCapture`" section for the
exact shape):

```
# no command to run - this is a research/fetch step, not code in this
# package. See
# validation-dataset/raw-captures-2026-06-25-to-2026-07-25.json
# for a real, worked example.
```

Step 2 — process (this package, fully deterministic, no dependencies
beyond the Python 3 standard library):

```
cd research-sensor
python3 run_research_sensor.py --captures path/to/raw-captures.json
```

Optional flags:

```
python3 run_research_sensor.py \
  --captures path/to/raw-captures.json \
  --source-registry config/source-registry.json \
  --relevance-gate config/relevance-gate.json \
  --reports-dir reports
```

Each run writes exactly three files, all inside `reports/`:
`research-registry.json` (the machine-readable artifact — see
"Headquarters compatibility" below), `daily-research-brief-<timestamp>.md`,
and `weekly-research-intelligence-report-<timestamp>.md`. Re-running
against the same registry is idempotent: a signal already registered
has its `times_seen`/`last_seen`/evidence updated in place, never
duplicated — see `docs/VALIDATION-REPORT.md`.

## What it does

1. **Loads** a raw-captures file (`capture.py`) — malformed entries are
   skipped with a reason, never fatal.
2. **Validates sources** against `config/source-registry.json`
   (`cli.py`) — a capture from an unlisted source is kept but flagged;
   a capture claiming a trust level the Registry disagrees with is
   corrected, Registry wins.
3. **Clusters** raw captures proposing or supporting the same research
   idea (`dedup.py`) — same domain, shared idea keyword, transitive —
   so multiple papers behind one idea become one signal with multiple
   evidence entries, never duplicate signals.
4. **Scores confidence** (`trust.py`) — publication quality, peer
   review status, and independent corroboration drive confidence;
   `COMMUNITY_HINT`-only evidence can never produce an accepted signal
   at all, not even at `LOW` — see `docs/TRUST-POLICY.md`.
5. **Gates relevance** (`relevance.py`) against the 5 named Discovery
   Lab projects via a config-driven keyword mapping
   (`config/relevance-gate.json`) — no match means `WATCH`, never
   forced relevance.
6. **Extracts possible experiments** (`experiments.py`) for high-value,
   non-`WATCH` signals only — structurally incapable of producing an
   implementation plan; see `docs/EXPERIMENT-EXTRACTION-POLICY.md`.
7. **Assigns persistent `RES-000N` IDs** and updates the Research
   Signal Registry idempotently (`registry.py`).
8. **Renders** the Daily Research Brief (this run's new/updated
   signals) and the Weekly Research Intelligence Report (everything
   active in the last 7 days, plus a non-prioritizing "Top Research
   Opportunity" pointer) (`brief.py`).

Every registered signal follows the 14-field Research Signal Model
`EXEC-010` specifies — see `docs/RESEARCH-SCHEMA.md`.

## Configuration

`config/source-registry.json` lists every source this sensor is
allowed to be told about, each with a fixed `source_trust`, plus a
`processing_budget` cap and `window_days`. Add or remove a source by
editing this file; nothing in the code needs to change. See
`docs/SOURCE-REGISTRY.md` for the human-readable list.

`config/relevance-gate.json` maps keywords to the 5 named Discovery
Lab projects (`KOD`, `Discovery Lab`, `Trust Engine`, `Generative
Discovery Engine`, `Dinev Assistant`). Also config-driven, also
editable without a code change. Its current keyword sets are a
first-draft heuristic — see `docs/KNOWN-LIMITATIONS.md`.

## Headquarters compatibility

`research-registry.json` is a flat JSON list, each entry a plain object
with the 14 documented schema fields plus provenance — readable the
same tolerant way `headquarters/src/headquarters/collector.py` already
reads every other artifact it consumes. `tests/test_headquarters_compatibility.py`
proves this structurally. Wiring an actual `collector.py` change to
read it is a small, additive, separate task — not attempted here, per
`EXEC-009`'s instruction not to redesign Headquarters.

## Safety guarantees

This sensor is technically read-only in its checked-in source: no
network client, no write outside its own `reports/` directory, no
commit/push/merge/subprocess call anywhere. Enforced by
`tests/test_safety.py`, including a self-check proving the detector
actually catches real violations.

## Limitations

See `docs/KNOWN-LIMITATIONS.md` for the full, honest list — including
which real sources blocked direct `WebFetch` during this task's own
validation pass (stricter than `reality-sensor/` encountered), the
resulting reliance on `WebSearch`-indexed abstract text rather than
directly re-verified primary-source text, and three honest
date-precision caveats.

## Provenance

Implements `EXEC-010 — Research Reality Sensor 001`. See
`ARCHITECTURE.md` for the full design, `docs/VALIDATION-REPORT.md` for
the 3x-repeated + 1 live run results, and `CONTRACT.md` for the tool's
operating contract.
