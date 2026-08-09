# discovery-lab

Constraint Archaeology pipeline + the shared Reality Observatory it is growing into.

## What this repo does

A daily multi-agent pipeline:

```
public sources
  -> Sensor Agent
  -> observations.jsonl
  -> anomaly clustering
  -> same-mechanism gate
  -> Constraint Archaeology v0.5
  -> adversarial review
  -> WATCH / INVESTIGATE / KILL
```

Constraint Archaeology is **not** the system. It is the first specialised analyst
on top of a shared observational infrastructure. See
`docs/architecture/reality-observatory-v0.1.md`.

## Frozen artifacts — never modify without an explicit unfreeze instruction

- `docs/method/constraint-archaeology-v0.4-spec.md`
- `docs/method/constraint-archaeology-v0.5-patch.md`
- `docs/method/blind-discovery-protocol-2026.md`
- `docs/method/blind-discovery-2026-move1.md`
- everything under `docs/method/controls/`
- the fixtures in `tests/test_same_mechanism_gate.py`

These are evidence, not code. Editing them destroys the validation record.
If a change looks necessary, say so and stop — do not make it.

## Project rules

- **Method version is 0.5 and does not move.** Adapter and analyst versions move.
  Every Constraint Archaeology output carries `method_version="0.5"` and a separate
  `analyst_version` for the adapter. This is what lets infrastructure evolve without
  silently changing the method.
- **`findings.jsonl` is append-only.** Never read-modify-write it. A newer result is a
  NEW record, never an edit. No deletions.
- **All gate outcomes persist:** `MERGED`, `RELATED_DISTINCT`, `UNRESOLVED`. A refused
  merge is the most informative output the pipeline has produced so far.
- **No historical backfill of `findings.jsonl`.** A retroactively generated Finding is
  not equivalent to one recorded at the time. That distinction is the whole point.
- **Snapshot files remain runtime truth.** `observations.jsonl`, `anomalies.json`,
  `latest-evaluations.json`, the daily report. Do not migrate readers.
- **Provenance is truthful or absent.** `derived_from` references records actually used.
  Never fabricate provenance to satisfy a schema. If the code cannot expose it, say so.
- **Model-generated content is never evidence.** Findings are `origin="generated"` and
  are not admissible as resolution evidence for an expectation.
- **`INSUFFICIENT DATA` is a valid result.** So is a refused merge, a KILL, and a day
  with no output. Daily output is not a goal; compounding memory is.
- **Similarity is not same mechanism.** Two anomalies merge only if each one's own repair
  removes the other's failure, in both directions. Group by what must change, never by
  how the pain is worded.

## Working conventions

- On integration tasks: inspect the tree and show the proposed write points **before**
  editing anything, then wait for confirmation. Do not assume file names.
- Tests are offline and deterministic. No network, no model calls in tests.
- Ledger writes are wrapped in `try/except` and must never break the daily run.
- Prefer removing a component over generalising it.

## Layout

```
docs/method/          frozen methodology, protocols, control reports
docs/architecture/    Reality Observatory design
docs/decisions/       ADRs (none written yet; 5 candidates listed)
docs/reviews/         adversarial reviews of candidates
constraint-archaeology-agents/
tests/
```
