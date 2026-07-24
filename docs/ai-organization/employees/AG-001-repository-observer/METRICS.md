# Metrics — AG-001 Repository Observer

Employee ID: **AG-001** · Role Name: **Repository Observer** · Status:
**Prototype / DRAFT / EXPERIMENTAL / NOT ADOPTED** · Version: **v0.1**
Core Principle: **Observe changes. Report evidence. Do not decide.**

This document defines AG-001's quality-measurement **interface** only.
**No starting values are defined. No metric has been measured yet under
v0.1** — `STATUS.yaml` records `runs_completed: 0`, so there is no run
data yet to compute any of these from. Populating this document with
invented numbers would itself violate the same evidentiary discipline
this role is built to enforce on others.

## Metrics

- **`requested_repository_coverage`** — of the repositories requested
  for a run, what proportion were actually included in the resulting
  report (accessible or not).
- **`accessible_repository_coverage`** — of the repositories requested,
  what proportion were actually accessible for observation.
- **`confirmed_change_precision`** — of the changes reported under
  `Confirmed Changes`, what proportion hold up under independent review.
- **`missed_change_rate`** — of the changes an independent reviewer can
  confirm actually occurred within scope, what proportion AG-001 failed
  to report.
- **`unsupported_claim_rate`** — of all claims made across a report,
  what proportion lack a valid, checkable `Evidence` entry.
- **`evidence_completeness`** — for claims that do have an `Evidence`
  entry, how complete that entry is against the fields `OUTPUTS.md`
  requires (repository, commit/PR/branch where applicable, file path,
  line range or diff reference where available, observation method).
- **`access_gap_reporting_rate`** — of the cases where access was
  actually insufficient, what proportion were correctly reported as
  `INSUFFICIENT ACCESS` rather than silently omitted or guessed around.
- **`report_latency`** — time between a run being triggered and its
  Observation Report being produced.
- **`boundary_violation_count`** — count of any instance where AG-001
  took, or attempted, an action prohibited by `LIMITATIONS.md`.

## No aggregate trust score in v0.1

These nine metrics are deliberately **not** combined into a single
score in this version. A general-purpose trust-scoring pipeline — with
proposal, approval, and applied-update stages — is trust-engine's
fully-specified territory (see `../../../docs/proposals/
PROP-0001-discovery-lab-boundaries.md`, ground rule 3). AG-001's metrics
measure this specific role's own observational reliability; they are
not, and must not become, a general trust score for anything else.

## Candidate Thresholds — Not Adopted

No candidate promotion thresholds are proposed in this version.
Proposing numeric thresholds before any real run has occurred would
itself be an unsupported claim — exactly what `unsupported_claim_rate`
above exists to catch, applied to this document's own authors. This
section should be populated only once enough run data exists, from at
least one real Probation-stage review cycle (see `../../
HIRING-LIFECYCLE-DRAFT.md`), to ground a proposal in evidence rather
than a guess.
