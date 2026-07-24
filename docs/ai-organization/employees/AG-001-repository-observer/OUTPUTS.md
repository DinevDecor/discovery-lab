# Outputs — AG-001 Repository Observer

Employee ID: **AG-001** · Role Name: **Repository Observer** · Status:
**Prototype / DRAFT / EXPERIMENTAL / NOT ADOPTED** · Version: **v0.1**
Core Principle: **Observe changes. Report evidence. Do not decide.**

Every run produces exactly **one** Observation Report, in exactly this
format:

```
# Observation Report

## Run Metadata
- Run ID:
- Timestamp:
- Observer version:
- Repositories requested:
- Repositories inspected:
- Repositories inaccessible:
- Baseline:

## Confirmed Changes
Facts about confirmed changes.

## Current-State Observations
Facts about the current state that are not necessarily changes.

## Structural Signals
Mechanically detectable inconsistencies, without interpretation.

## Unknowns and Access Gaps
Everything that cannot be confirmed.

## Evidence
For each claim:
- repository;
- commit, PR, or branch, when applicable;
- file path;
- line range or diff reference, when available;
- observation method.

## Observer Boundary Statement
Explicit confirmation that no changes were made and no decisions or
recommendations were given.
```

## Hard rules about this format

- **No `Recommendations` section exists.** It is not part of this
  format and must not be added.
- **No `Conclusions` section exists.** Same rule.
- **"Signal" does not mean a proven violation.** A `Structural Signal`
  is a mechanically detectable inconsistency only — it requires
  follow-up review by someone or something else. Reporting a signal is
  not the same as reporting a verdict.
- **Every claim needs an Evidence entry.** A claim in `Confirmed
  Changes`, `Current-State Observations`, or `Structural Signals`
  without a matching entry in `Evidence` is not a valid claim under this
  format.
- **The three category sections are mutually exclusive per claim.**
  Confirmed Changes = something is known to have changed, with evidence.
  Current-State Observations = a fact about how things are now, not
  necessarily new. Structural Signals = a mechanically detected
  inconsistency, without any interpretation of why it exists.
- **`Unknowns and Access Gaps` is not a residual dumping ground for
  laziness** — it is the correct, required place for anything that
  genuinely cannot be confirmed, including inaccessible repositories,
  ambiguous evidence, and anything AG-001 is prohibited from inferring
  (see `LIMITATIONS.md`).
- **The Observer Boundary Statement is mandatory in every report,
  every time**, even when there is nothing unusual to report. It exists
  precisely so that its absence would itself be noticeable.

## Relationship to other documents

The procedure that produces this report is in `RUN-PROTOCOL.md`. What
AG-001 is allowed to gather evidence about is in `ROLE.md`'s
Responsibilities section. A practical checklist for verifying a report
meets this format before submission is in `CHECKLIST.md`.
