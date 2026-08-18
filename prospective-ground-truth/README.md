# Prospective Ground-Truth Stream v0.1

The empirical substrate the Ground-Truth Ablation & Kill Test needed and didn't have
(`experiments/ground-truth-kill-test-001/`: 0 valid / 13 excluded, `INSUFFICIENT
DATA`). A protocol for registering real cases *now*, before their outcome is known,
so a future kill test — or later model calibration, or later Trust Engine
integration, none of which are built here — has genuine T0→T1 pairs to work with.
See `CONTRACT.md`.

This package builds **no autonomy**. It is four durable concepts (`T0Freeze`,
`ExpectedResolution`, `ProspectiveCase`, `Resolution`) over two append-only ledgers, a
validator, and a three-command manual CLI.

## What this is

- `src/prospective_ground_truth/models.py` — `T0EvidenceItem`, `T0Freeze`,
  `ExpectedResolutionWindow`, `ExpectedResolution`, `ProspectiveCase`, `Resolution`.
  `ProspectiveCase.status` is never stored as mutable data — it is always derived
  (`ledger.derive_status`) from whether a `Resolution` exists for that case.
- `src/prospective_ground_truth/identity.py` — deterministic ids:
  `prospective_case_id` from `(domain, proposition, t0_cutoff)` only (never from
  evidence content, so it survives a differently-worded re-derivation of the same
  real freeze point); `resolution_id` from `(prospective_case_id, outcome,
  resolved_at)`.
- `src/prospective_ground_truth/packet.py` — `compute_packet_sha256(t0_cutoff,
  evidence)`, the same canonical-JSON + sha256 approach
  `blind_analysis_kernel.packet.packet_sha256` already uses, applied to this
  package's own T0Freeze shape (no cross-package import — see `CONTRACT.md`).
- `src/prospective_ground_truth/validator.py` — every hard rule from the protocol as
  an actual checked violation, not just a convention: post-T0 evidence rejected,
  resolution criteria required before a case is valid, packet hash internally
  consistent, `resolver_type` can never be a bare model call, outcomes claiming
  something about reality require real T1 evidence and a named authoritative source.
- `src/prospective_ground_truth/ledger.py` — `CaseLedger` (`data/cases.jsonl`) and
  `ResolutionLedger` (`data/resolutions.jsonl`), both append-only and idempotent by
  id, structurally unable to touch each other's file. `rebuild_snapshot()` replays
  both into `data/cases.json`, a fully-rebuilt view, never hand-edited.
- `run_prospective_ground_truth.py` — three roles: `register` (freeze T0 + the
  pre-registered resolution criteria in one atomic step — they cannot be split
  across two commands without risking a case existing with unregistered criteria),
  `resolve` (append a T1 `Resolution`; refuses with `SystemExit` if the case was
  never registered), `report` (read-only snapshot printout).

## Registering a case

Write a JSON file (see `tests/test_cli.py`'s `_case_input()` for the exact shape, or
`data/cases.jsonl` after the first real registration below) with `domain`,
`proposition`, `decision_relevance`, `t0_cutoff`, `t0_evidence` (a list of
`{artifact_id, citation, source_url, captured_at, quote_or_summary}`),
`resolution_question`, `expected_resolution_window` (`{earliest, latest}`),
`resolution_sources_expected`, `positive_condition`, `negative_condition`,
`ambiguous_condition`, then:

```
python3 run_prospective_ground_truth.py register --input case.json
```

Re-running the exact same input is idempotent (no duplicate line). A structural
violation (post-T0 evidence, a blank resolution condition, a resolution window that
opens before T0) is refused with `SystemExit` and nothing is written.

## Recording a resolution, once reality answers

```
python3 run_prospective_ground_truth.py resolve --input resolution.json
```

with `prospective_case_id`, `resolved_at`, `outcome` (`POSITIVE`/`NEGATIVE`/
`AMBIGUOUS`/`EXPIRED_UNRESOLVED`/`INVALIDATED`), `t1_evidence_artifact_ids`,
`authoritative_source_type`, `resolution_rationale`, `resolver_type` (`human` or
`model_assisted_human_confirmed` — never a bare model call). Refuses if
`prospective_case_id` was never registered.

## Checking status

```
python3 run_prospective_ground_truth.py report
```

Read-only. Prints every case with its derived `status`
(`OPEN`/`AWAITING_OUTCOME`/`RESOLVED`/`EXPIRED_UNRESOLVED`/`INVALIDATED`) and every
resolution on record.

## Tests

```
python3 -m unittest discover -s tests -v
```

All tests are offline and deterministic — no model or network call anywhere in this
package, checked structurally in `tests/test_safety.py`, not just documented.
