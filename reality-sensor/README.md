# Reality Intelligence Sensor 001

`EXEC-008`'s implementation: the first external reality sensor in the
Discovery Lab ecosystem. It observes the external AI ecosystem
(foundation model releases, agent infrastructure, developer platforms,
research), normalizes what it finds into structured, evidence-cited
Signals, and exposes them to Headquarters via a machine-readable
Signal Registry. It is a sensor — it never decides, never acts, and
never bypasses Headquarters. See `ARCHITECTURE.md` for the full design
and `CONTRACT.md` for its operating contract.

## The one thing to understand before anything else

This package's own Python source **never makes a network call** —
enforced by `tests/test_safety.py`, not just documented. Capture (the
actual internet-fetching step) and processing (clustering, trust
policy, confidence scoring, registry, briefs) are deliberately split.
See `ARCHITECTURE.md`'s "The one decision everything else follows
from" section for exactly why — in short, it's the only way to satisfy
both "observe live reality" and "repeated executions are identical,"
at once, honestly.

## How to run it

Step 1 — capture (external, point-in-time; a human or an AI executor
performs this against the fixed `config/source-registry.json` list,
respecting its `search_budget`, and writes a raw-captures JSON file —
see `docs/SIGNAL-SCHEMA.md`'s "Raw Capture" section for the exact
shape):

```
# no command to run — this is a research/fetch step, not code in this
# package. See validation-dataset/raw-captures-2026-07-11-to-2026-07-25.json
# for a real, worked example.
```

Step 2 — process (this package, fully deterministic, no dependencies
beyond the Python 3 standard library):

```
cd reality-sensor
python3 run_reality_sensor.py --captures path/to/raw-captures.json
```

Optional flags:

```
python3 run_reality_sensor.py \
  --captures path/to/raw-captures.json \
  --source-registry config/source-registry.json \
  --relevance-gate config/relevance-gate.json \
  --reports-dir reports
```

Each run writes exactly three files, all inside `reports/`:
`signal-registry.json` (the machine-readable artifact — see
"Headquarters compatibility" below), `daily-ai-reality-brief-
<timestamp>.md`, and `weekly-ai-intelligence-brief-<timestamp>.md`.
Re-running against the same registry is idempotent: a signal already
in the registry has its `times_seen`/`last_seen`/evidence updated in
place, never duplicated — see `docs/VALIDATION-REPORT.md`.

## What it does

1. **Loads** a raw-captures file (`capture.py`) — malformed entries are
   skipped with a reason, never fatal.
2. **Validates sources** against `config/source-registry.json`
   (`cli.py`) — a capture from an unlisted source is kept but flagged;
   a capture claiming a trust level the Registry disagrees with is
   corrected, Registry wins.
3. **Clusters** raw captures describing the same real-world event
   (`dedup.py`) — same category, shared capability keyword, transitive
   — so "multiple articles about one release" become one Signal with
   multiple Evidence entries, never duplicate Signals.
4. **Scores confidence and urgency** (`trust.py`) — the one hard rule
   `EXEC-008` states explicitly: confidence can never be `HIGH` from
   `COMMUNITY`-trust evidence alone.
5. **Gates relevance** (`relevance.py`) against the 5 named Discovery
   Lab projects via a config-driven keyword mapping
   (`config/relevance-gate.json`) — no match means `WATCH`, never
   forced relevance.
6. **Assigns persistent `RS-000N` IDs** and updates the Signal Registry
   idempotently (`registry.py`) — same pattern as Headquarters'
   `HQ-000N` recommendation IDs.
7. **Renders** the Daily AI Reality Brief (this run's new/updated
   signals) and the Weekly AI Intelligence Brief (everything in the
   registry active in the last 7 days) (`brief.py`).

Every Signal follows the 13-field Signal Model `EXEC-008` specifies —
see `docs/SIGNAL-SCHEMA.md`. Every source is classified into one of 6
fixed Trust Levels — see `docs/TRUST-POLICY.md`.

## Configuration

`config/source-registry.json` lists every source this sensor is
allowed to be told about, each with a fixed `trust_level` and
`category`, plus a `search_budget` cap. Add or remove a source by
editing this file; nothing in the code needs to change. See
`docs/SOURCE-REGISTRY.md` for the human-readable list.

`config/relevance-gate.json` maps keywords to the 5 named Discovery
Lab projects (`KOD`, `Discovery Lab`, `Trust Engine`, `Generative
Discovery Engine`, `Dinev Assistant`). Also config-driven, also
editable without a code change. Its current keyword sets are a
first-draft heuristic grounded in what little each project's own
README/`PROJECT_STATE.md` actually says — see `docs/
KNOWN-LIMITATIONS.md`.

## Headquarters compatibility

`signal-registry.json` is a flat JSON list, each entry a plain object
with the 13 documented Signal fields — readable the same tolerant way
`headquarters/src/headquarters/collector.py` already reads every other
artifact it consumes (a specific, pre-configured file, `json.loads`,
no custom parser). `tests/test_headquarters_compatibility.py` proves
this structurally. Wiring an actual `collector.py` change to read it
is a small, additive, separate task — not attempted here, since
`EXEC-008` says not to redesign the existing ecosystem and does not
list a Headquarters code change among its required deliverables.

## Safety guarantees

This sensor is technically read-only in its checked-in source: no
network client, no write outside its own `reports/` directory, no
commit/push/merge/subprocess call anywhere. Enforced by
`tests/test_safety.py`, not just asserted — including a self-check
proving the detector actually catches real violations.

## Limitations

See `docs/KNOWN-LIMITATIONS.md` for the full, honest list — including
the relevance gate's naive keyword-substring matching (it can match a
project's own name if mentioned in prose, not only a topically
meaningful signal), the capture step's dependence on an executor with
real web access, and which real sources blocked direct fetching during
this task's own validation pass.

## Provenance

Implements `EXEC-008 — Reality Intelligence Sensor 001`. See
`ARCHITECTURE.md` for the full design, `docs/VALIDATION-REPORT.md` for
the 3x-repeated + 1 live run results, and `CONTRACT.md` for the tool's
operating contract.
