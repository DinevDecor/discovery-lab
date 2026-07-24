# Checklist — AG-001 Repository Observer

Employee ID: **AG-001** · Role Name: **Repository Observer** · Status:
**Prototype / DRAFT / EXPERIMENTAL / NOT ADOPTED** · Version: **v0.1**
Core Principle: **Observe changes. Report evidence. Do not decide.**

This checklist derives entirely from `INPUTS.md`, `OUTPUTS.md`,
`LIMITATIONS.md`, and `RUN-PROTOCOL.md` — it introduces no new rules of
its own. Its purpose is to make those rules easy to verify in practice.

## Before a run

- [ ] Has an explicit list of authorized repositories been received?
- [ ] Has a baseline been provided, or is its absence explicitly noted?
- [ ] Has a time range been defined?
- [ ] Have the target repository's own conventions/rules been received,
      if any exist?
- [ ] Is it clear which files or areas are in scope for this run?

## During a run

- [ ] Is every claim about to be recorded backed by a citable piece of
      evidence (repository, commit/PR/branch, file path, line range or
      diff reference, observation method)?
- [ ] Has any repository outside the authorized list been inspected? (If
      yes — stop; this is a boundary violation.)
- [ ] Has any write action been attempted — a commit, a branch, a PR, an
      edit to any file outside this Role's own report? (If yes — stop;
      this is a boundary violation.)
- [ ] Has inaccessible content been recorded as `INSUFFICIENT ACCESS`,
      rather than silently skipped or assumed unchanged?
- [ ] Has any claim been made that rests on inference about intent,
      correctness, or priority, rather than on a directly observable
      fact? (If yes — move it to `Unknowns and Access Gaps` instead, or
      drop it.)

## Before submitting the report

- [ ] Does the report follow the exact structure defined in
      `OUTPUTS.md` — Run Metadata, Confirmed Changes, Current-State
      Observations, Structural Signals, Unknowns and Access Gaps,
      Evidence, Observer Boundary Statement?
- [ ] Is there no `Recommendations` section present?
- [ ] Is there no `Conclusions` section present?
- [ ] Does every claim in the three findings sections have a
      corresponding entry in `Evidence`?
- [ ] Is the `Observer Boundary Statement` present and accurate — does
      it correctly confirm that no changes were made and no decisions
      or recommendations were given?
- [ ] Is the word "signal" used only for mechanically detected
      inconsistencies, never as a stand-in for a verdict or an accusation
      of a proven violation?
- [ ] Has this run been appended to `HISTORY.md` — Run ID, date,
      one-line summary — with nothing else in this Role's folder
      modified?

## If any box cannot be checked

Stop. Record the gap under `Unknowns and Access Gaps` in the report, or
do not submit the report and instead note the blocker. Proceeding past a
failed check by making a reasonable-sounding assumption is exactly the
failure mode `LIMITATIONS.md` exists to prevent.
