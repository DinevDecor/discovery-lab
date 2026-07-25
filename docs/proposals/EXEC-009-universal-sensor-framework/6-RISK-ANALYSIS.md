# Deliverable 6 — Risk Analysis

Per `EXEC-009`'s required categories: over-abstraction, future
incompatibilities, performance, governance implications.

## Over-abstraction

- **Risk**: a future team, once a `sensor-framework/` package exists,
  treats its optional layers as mandatory by convention even though
  this specification marks them optional — "everyone else uses Trust
  Classification, so the new Calendar sensor should too" pressure,
  regardless of fit. This is the single most likely way this proposal
  could still produce the outcome it's trying to prevent.
  **Mitigation**: `4-ADAPTER-CONTRACT.md` requires each sensor's own
  `CONTRACT.md` to state which optional layers it uses *and why* —
  making "we didn't need it" a visible, normal, documented choice
  rather than a silent omission someone later "fixes."
- **Risk**: the Core Finding fields (Deliverable 4) drift toward
  becoming a de facto mandatory schema because it's easier to copy the
  table than to think about what a new domain actually needs.
  **Mitigation**: the table is explicitly sourced from genuine overlap
  found in exactly two implementations, not designed forward; a third
  sensor's own Normalization step is still free to diverge from it if
  its domain's own "description of what was found" doesn't map
  cleanly — the contract requires a superset relationship, not field-
  for-field identity.
- **Risk (already observed, not hypothetical)**: this task's own
  source material (`EXEC-009`'s target-form diagram) already
  over-abstracted once, presenting Trust Classification, Deduplication,
  and Signal Registry as universal layers before any second sensor
  existed to test that claim against. `1-FRAMEWORK-SPECIFICATION.md`'s
  revision is the direct mitigation, but it's worth naming plainly:
  the temptation to generalize from one good example is real and this
  review needed to actively correct for it, not just avoid it in the
  abstract.

## Future incompatibilities

- **Risk**: a future external/evidentiary sensor's domain doesn't fit
  the "Trust Classification + Deduplication + Signal Registry, all
  three or none" pattern cleanly — e.g. a Markets sensor might need
  Deduplication (many articles about one price move) without needing
  persistent Signal Registry identity (yesterday's price move isn't
  worth tracking once today's exists). The framework's optional-layer
  model already accommodates picking a subset, but the *combinations*
  haven't been tested by a real third implementation.
  **Mitigation**: none needed pre-emptively — this is precisely why
  `EXEC-009` itself excludes building new sensors now; the framework's
  optional-layer independence (each is a separate module, not a
  package deal) is the structural answer, to be validated when a real
  third sensor is actually built.
- **Risk**: Confidence-vocabulary non-unification (deliberately kept
  domain-specific per Deliverable 4) makes any future *cross-sensor*
  aggregation in Headquarters harder, since `MISMATCH` and `LOW`
  aren't comparable values. This is a real, accepted cost of the
  Anti-Abstraction Rule, not an oversight.
  **Mitigation**: out of scope to solve here (`EXEC-009` excludes
  redesigning Headquarters); named so a future Headquarters-side task
  inherits the tradeoff explicitly rather than discovering it by
  surprise. Headquarters' own `PROP-0001`-inherited rule against a
  single aggregate score already suggests forced comparability across
  domains was never the goal anyway.
- **Risk**: the Core Finding table's `human_needed` row already notes
  a real gap — Reality Sensor has no literal boolean field, unlike
  Observation Agent. A future sensor copying the table verbatim could
  propagate the gap rather than resolve it.
  **Mitigation**: named explicitly in Deliverable 4 rather than
  silently harmonized; a future sensor should decide this field on its
  own merits.

## Performance

- **Risk**: none identified as material. Every component considered
  for promotion (safety scanning, config loading, CLI shimming, report
  rendering) is already lightweight, pure-stdlib, and runs in
  milliseconds in both existing sensors (`Ran 58 tests in 0.061s`,
  `Ran 61 tests in 0.048s` — full suites, not just the relevant
  modules). A shared framework package adds, at most, one more import
  boundary; no component under consideration does I/O beyond what
  each sensor already does to its own `reports/` directory.
  **Mitigation**: not needed at this stage. Worth re-examining only if
  a future sensor's own capture volume (e.g. a Markets sensor
  processing large feeds) stresses the optional Deduplication layer's
  current O(n²) pairwise-comparison clustering algorithm
  (`reality-sensor/src/reality_sensor/dedup.py::cluster`) — fine for
  Reality Sensor's current ~10-capture validation runs, untested at
  scale.

## Governance implications

- **Risk**: introducing a shared framework package creates a new kind
  of dependency this ecosystem hasn't had before — a change to
  `sensor-framework/`'s Safety module could, in principle, affect
  every sensor that adopted it, unlike today where each tool's safety
  test is fully independent and a mistake in one cannot silently
  weaken another.
  **Mitigation**: this is exactly why `5-MIGRATION-PLAN.md` treats
  adoption as sensor-by-sensor and optional, not automatic, and why
  each sensor configures its own forbidden-pattern additions and
  write-allow-list rather than inheriting a single fixed policy — a
  regression in the shared module's *core* detector would still need
  to be caught by each adopting sensor's own test suite, the same
  self-check discipline (`test_forbidden_patterns_actually_detect_
  violations`) already required per-tool today, simply now importable
  rather than re-typed.
- **Risk**: "the framework" becoming a place decisions get made
  implicitly — e.g., a future contributor adds a new mandatory layer
  to the shared package without going through the same evidence-based
  promotion discipline this task used, because "it's just a code
  change to an internal library," not a new EXEC task.
  **Mitigation**: named as a process risk, not a technical one — the
  Anti-Abstraction Rule and the two-implementation evidence bar this
  task applied should be treated as standing policy for the framework
  package specifically, not a one-time review; a natural candidate for
  a short, durable note in the framework's own future `CONTRACT.md`
  when it is built (a documentation recommendation, not something this
  task implements).
- **No change to Human Authority Boundary anywhere.** Every promoted
  and every optional component reviewed here is either enforcement
  (Safety) or plumbing (config/CLI/reporting/registry mechanics) —
  none of them touch decision-making, and the framework does not
  introduce any new capability for a sensor to act rather than report.
  This was verified directly against `1-FRAMEWORK-SPECIFICATION.md`'s
  Required Design Constraints, not merely asserted.
