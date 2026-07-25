# Deliverable 7 — Success Metrics

Each metric measurable from the recommended pilot alone, without
requiring a second run.

| Metric | Definition | How measured in the pilot |
|---|---|---|
| True findings | Observations a human confirms as real (`MISMATCH` correctly identified) | The `AG-001` `STATUS.yaml` mismatch is a known-true positive going in — the pilot must find it, or the schema has already failed its first test |
| False positives | Observations flagged `MISMATCH` that a human determines are not real problems | Counted directly from the human decision in pilot step 5 |
| Human acceptance rate | Of Recommended Actions, the fraction accepted vs. rejected — same metric `PROP-0001`'s own Recommendation Ledger specifies, same naming caveat inherited: *not* a measure of objective correctness, only of whether governance agreed | Computed from the one pilot run's Recommended Action(s) |
| Time to produce | Wall-clock time to complete the loop for the two named subjects | Directly observable during the pilot |
| Critical issues detected | Count of findings a human independently judges high-severity | Compared against `DL-001`'s own Risk section (`project-memory`'s registry contradiction was rated High there) |
| Noise ratio | Findings a human judges trivial or irrelevant, divided by total findings | Directly countable from the pilot's Report |
| Schema completeness | Whether `DL-001`'s five real findings can each be re-expressed in the 7-field schema without information loss | Direct comparison, field by field |
| Formal Gate value-add | Whether the independent-reviewer pass (pilot step 4) changes, narrows, or confirms the Recommendation before it reaches the human | Directly observable — compare the Recommendation's wording before and after the Gate step |

## What is deliberately not a metric here

An "ecosystem health score" or any single number aggregating findings
across subjects — `PROP-0001`'s own explicit prohibition on a
cross-repository aggregate applies with equal force to a
cross-observation aggregate within one report; forcing one would
misrepresent qualitatively different findings the same way it would
misrepresent structurally different repositories.
