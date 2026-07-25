# Architecture — Reality Intelligence Sensor 001

`EXEC-008`'s implementation. Read this before the source — it explains
the one design decision everything else in this package follows from.

## Position in the ecosystem

```
External Reality
      │
      ▼
Reality Sensor 001        (this package)
      │
      ▼
Signal Registry            reality-sensor/reports/signal-registry.json
      │
      ▼
Observation Layer          (Observation Agent's own scope is unchanged —
      │                     this sensor does not extend or alter it)
      ▼
Headquarters                reads the registry as one more named artifact,
      │                     exactly like it already reads Observation
      │                     Agent's reports/, the Recommendation Ledger,
      │                     ADR directories, and the project registry —
      │                     see "Headquarters compatibility" below.
      ▼
Human Decision
```

The sensor never writes to Headquarters, never calls it, never invokes
anything downstream of itself. It produces one artifact — the Signal
Registry, plus two human-readable briefs rendered from it — and stops.
Whether or how Headquarters actually reads that artifact is a Headquarters-
side decision, unchanged by this task (`EXEC-008` explicitly says
"Integrate into the current Discovery Lab architecture," not "modify
Headquarters' architecture").

## The one decision everything else follows from

`EXEC-008` requires two things that are in real tension:

1. **Continuously observe the external AI ecosystem** — foundation
   model releases, agent infrastructure, developer platforms, research.
   That is inherently a live-internet activity.
2. **Repeated identical executions remain stable** — "3 identical
   repeated executions… same signals, same IDs, same evidence… stable
   reports," verified the same way `EXEC-006`'s regression tests verify
   Observation Agent: byte-for-byte reproducible output from the same
   input.

No software can satisfy both at once *in a single step*. Real web pages
change, CDNs serve slightly different content on retry, rate limits
vary, and — per this ecosystem's own established safety discipline —
neither `observation-agent/` nor `headquarters/` has ever made a single
network call from their own checked-in source (`headquarters/tests/
test_safety.py` statically forbids `requests.`, `urllib.request`,
`httpx.`, `http.client` outright). Adding live, autonomous network
fetching directly into a tested, checked-in module would be the first
break of that discipline in this entire engagement, and it would make
the reproducibility requirement above impossible to satisfy honestly —
a test that reruns a live fetch and asserts identical output would
either be lying (mocking the network and calling that "real") or
flaky (occasionally failing because the internet changed).

**Resolution: split capture from processing**, the same separation any
real sensor/ETL pipeline uses between ingest and transform:

- **Capture** (external, point-in-time, *not* required to be
  repeatable) — a human or an AI executor acting under this task's own
  authorization fetches the fixed Source Registry's URLs (via whatever
  read-only tool that executor has — in this implementation, `WebFetch`/
  `WebSearch`, the same tools already used for read-only research
  throughout this engagement) and writes what was found into a
  **raw-captures file**: plain JSON, one entry per fetched source, no
  interpretation, no scoring, no deduplication — see `docs/
  SIGNAL-SCHEMA.md`'s "Raw Capture" section for the exact shape.
- **Process** (internal, checked-in, deterministic, tested) — this
  package's entire Python source. It never touches a network. It reads
  a raw-captures file from local disk and *only* from local disk,
  applies the Trust Policy, the Relevance Gate, duplicate clustering,
  the Evidence Discipline, and Confidence Rules, updates the Signal
  Registry (idempotently — see below), and renders the two briefs.
  Run this step three times against the same raw-captures file and the
  output is byte-identical by construction, because every step is a
  pure function of that one file's content.

This is not a workaround for a missing capability — it is the correct
shape for a testable sensor. `tests/test_safety.py` enforces it the
same way the other two tools' safety tests enforce their own
boundaries: it statically scans this package's own source for any
network-client reference and fails the build if one is ever added,
exactly mirroring `headquarters/tests/test_safety.py`'s existing check.

## Package layout

```
config/source-registry.json    -> Domains A-D's fixed source list, each
                                   with a name, url, trust_level, category
config/relevance-gate.json     -> keyword -> project mapping (the 5 named
                                   Discovery Lab projects), extensible
                                   without a code change
src/reality_sensor/
  models.py     -> Signal, Evidence, RawCapture dataclasses; the closed
                   TrustLevel/Category/Confidence/Urgency vocabularies
  config.py     -> loads source-registry.json + relevance-gate.json
  trust.py      -> Trust Policy: confidence capping by evidence trust level
  relevance.py  -> Relevance Gate: which of the 5 projects, or WATCH
  dedup.py      -> clusters raw captures describing one real-world event
                   into one Signal with multiple Evidence entries
  registry.py   -> idempotent RS-000N persistent IDs, same key-reuse
                   pattern as headquarters/src/headquarters/
                   recommendation.py's HQ-000N (times_seen/last_seen
                   instead of times_proposed/last_proposed)
  brief.py      -> Daily AI Reality Brief + Weekly AI Intelligence Brief
  cli.py        -> orchestrates one execution: load raw captures ->
                   dedup -> relevance gate -> trust/confidence -> update
                   registry -> render briefs -> write reports/
run_reality_sensor.py          -> convenience entry point, same pattern
                                   as run_observation_agent.py /
                                   run_headquarters.py
tests/                          -> see docs/VALIDATION-REPORT.md for how
                                   each of EXEC-008's 12 required test
                                   categories is covered
docs/
  SIGNAL-SCHEMA.md              -> the 13-field Signal model + Raw
                                    Capture shape, in full
  TRUST-POLICY.md               -> the 6 trust levels + confidence rules
  SOURCE-REGISTRY.md            -> the fixed source list, human-readable
  VALIDATION-REPORT.md          -> the 3x-repeated + 1 live run results
  KNOWN-LIMITATIONS.md
validation-dataset/             -> the fixed, committed raw-captures file
                                    used for the 3x repeated-run proof
reports/                        -> this tool's own output, never
                                    anywhere else (signal-registry.json,
                                    daily/weekly briefs) — enforced by
                                    tests/test_safety.py
```

## Headquarters compatibility

`headquarters/src/headquarters/collector.py` already reads several
independent artifacts this way — a specific file at a specific,
pre-configured path, never a directory walk. `signal-registry.json` is
built to be read the same way: valid JSON, one flat list of Signal
records, each with the 13 documented fields, no nested surprises. A
future Headquarters change wiring `collector.py` to optionally read it
(the way it already optionally reads Observation Agent's `reports/`)
would be a small, additive change — not attempted here, since
`EXEC-008` says not to redesign the existing ecosystem and does not
list a Headquarters code change among its required deliverables.
`tests/test_headquarters_compatibility.py` proves the registry is
structurally readable by the same tolerant-parsing style
`headquarters/src/headquarters/parsing.py` already uses, without
importing or modifying any Headquarters module.

## What this is not

Per `EXEC-008`'s own Explicitly Out of Scope list: no autonomous
browsing (capture is a bounded, fixed-budget, executor-invoked step,
never a background process this package starts itself); no automatic
coding; no project creation; no autonomous decisions; no repository
modification; no Research/Decision Intelligence; no tender or market
monitoring; no calendar integration. The sensor's only output is
evidence, exactly as `AGENT-001`'s Observation Model and `EXEC-004`'s
Headquarters contract already established for this ecosystem — this
package extends that discipline to a new evidence source, not a new
kind of authority.
