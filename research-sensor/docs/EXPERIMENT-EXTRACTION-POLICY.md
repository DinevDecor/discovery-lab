# Experiment Extraction Policy

`EXEC-010`, verbatim: *"For every high-value paper identify: at least
one possible experiment; expected benefit; uncertainty; prerequisites;
validation idea. Do not generate implementation plans. Generate only
research opportunities."*

## What counts as "high-value"

`experiments.py::is_high_value(affected_projects, confidence)`:

- `affected_projects == [Project.WATCH]` → never high-value. A signal
  that has not named a concrete Discovery Lab project has not yet
  answered "why should Discovery Lab care?" and therefore cannot be
  high-value regardless of confidence.
- Otherwise, high-value iff `confidence` is `HIGH` or `MEDIUM`.
  `LOW`/`INSUFFICIENT_EVIDENCE` signals are still registered (a human
  may still want to see them) but never carry `possible_experiments` —
  the sensor does not stretch weak evidence into a "research
  opportunity."

## Where experiment content comes from

`experiments.py::build_experiments` **only ever assembles pre-existing
`possible_experiment_notes` supplied at capture time** into the
structurally-required shape. It never invents, expands, or infers
content the capture step did not already provide. A note missing any
of the 5 required keys (`description`, `expected_benefit`,
`uncertainty`, `prerequisites`, `validation_idea`) is dropped —
skipped, not fatal, and never filled in with invented text. See
`tests/test_experiments.py::test_incomplete_note_is_dropped_not_invented`.

## Why this cannot become an implementation plan

The `PossibleExperiment` dataclass (`models.py`) has **exactly** these
5 fields — no field exists for a file path, a code snippet, a task
list, or a step-by-step plan. This is a structural guarantee, not a
convention: see
`tests/test_experiments.py::test_experiment_never_contains_implementation_plan_fields`,
which asserts the dataclass's own field set is exactly the 5 required
keys, nothing more.

## Worked example (from this run's real capture)

Only one of the 6 real signals in
`validation-dataset/raw-captures-2026-06-25-to-2026-07-25.json` reached
`MEDIUM`/`HIGH` confidence with a named project (`RES-0006`, the
DeepMind "Conjecture Machines" piece, `Trust Engine`) — see
`docs/VALIDATION-REPORT.md`. Its one experiment note:

> **Description**: Add an explicit "validation cost"/"refutation cost"
> field to Research Signals surfaced to Headquarters, flagging when a
> research opportunity has no clear low-cost validation path.
> **Expected benefit**: Lets human reviewers triage opportunities by
> how cheaply they can be checked, not just by how interesting the
> idea sounds.
> **Uncertainty**: Unclear whether "validation cost" generalizes across
> Discovery Lab's own very different domains.
> **Prerequisites**: A working, domain-scoped definition of "validation
> cost."
> **Validation idea**: Manually re-score the existing registry for
> validation cost and see whether it changes reviewer priorities.

Note what this is not: no file to edit, no function to write, no
sprint plan — a direction to investigate, honestly stated as
uncertain, exactly as `EXEC-010` requires.

The other 5 real signals are all `LOW` confidence (single `PREPRINT`
evidence) and correctly carry `possible_experiments: []` — this is the
policy working as designed, not a gap.
