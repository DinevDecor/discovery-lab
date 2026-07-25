# Deliverable 6 — Success Metrics

Per `ARCH-003` Phase 6. Each metric is binary or directly countable —
no metric here requires subjective judgment to evaluate.

| # | Metric | Pass condition |
|---|---|---|
| M1 | Gate completion | All six `REVIEW-PROTOCOL.md` questions answered, each with an explicit verdict (`SOUND`/`UNSOUND`/`INSUFFICIENT EVIDENCE`) — zero skipped |
| M2 | Reviewer independence | The Knowledge Review names its Reviewer and explicitly records that this Reviewer did not produce `CPP-S3-01` |
| M3 | No bypassed human authorization | Exactly one Human Decision record exists, is attributable to a named human, and its timestamp/commit precedes any execution write |
| M4 | Full traceability | Every artifact produced cites its immediate predecessor: filed object → Human Decision → Knowledge Review → `CPP-S3-01` → `STRESS-RUN-0004-recovery-report.md`, an unbroken chain, checkable by inspection alone |
| M5 | Reproducibility | A second, independent party, given only the same inputs (`CPP-S3-01`, the specs, the Recovery Report), could re-derive the same six gate verdicts from the same evidence — not that they necessarily reach the same Human Decision, which is a human's prerogative, not a computation |
| M6 | No architectural improvisation | Zero new components, roles, fields, directories, or file-naming conventions appear anywhere in the pilot's output beyond what `3-EXECUTION-SPECIFICATION.md` already named in advance |
| M7 | Minimal diff | If accepted, the filed `KO-S3-01.md` differs from its `CURATION-0004.md` source in exactly one field (`status`) |
| M8 | Scope containment | No file outside the three named artifacts (`KR-0001-cpp-s3-01.md`, the Human Decision record, `KO-S3-01.md`) is created or modified |
| M9 | Clean reversibility | The entire pilot's output can be removed by a single `git revert` with zero effect on any pre-existing file |

## Reading the metrics together

`M1`–`M4` and `M9` test whether the *governance* mechanisms (Formal
Gate, Human Final Authority, traceability) actually held under a real
case — these are expected to pass, since they draw on the same
mechanisms `AG-003`'s Reality Stress Test already validated (all four
datasets `PASS`). `M6` and `M7` test the *execution* step specifically
— the part of the pilot with no precedent anywhere in the ecosystem
(`ARCH-002` `G1`) — and are the metrics most likely to reveal a real
limitation, if one exists. `M5` is the hardest to satisfy honestly,
given this session's own repeatedly-flagged self-review limitation
(`ARCH-001` `R4`); a pilot run by the same session/persona throughout
should report `M5` as unverifiable, not assume it passes.

## What counts as overall pilot success

All nine metrics pass, **and** the Go/No-Go judgment in
`8-GO-NO-GO-RECOMMENDATION.md` is re-examined against the actual run,
not assumed from this specification alone. A pilot where the Human
Decision is `Reject` or `Defer` can still score all nine metrics —
rejection is a valid, successful exercise of Human Final Authority, not
a metric failure. Metric failure means the *mechanism* broke, not that
the *proposal* was turned down.
