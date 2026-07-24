# Run Protocol — AG-001 Repository Observer

Employee ID: **AG-001** · Role Name: **Repository Observer** · Status:
**Prototype / DRAFT / EXPERIMENTAL / NOT ADOPTED** · Version: **v0.1**
Core Principle: **Observe changes. Report evidence. Do not decide.**

This is a described procedure for a human or an AI Executor to follow.
It is not code, and it is not an automation workflow — nothing here is
meant to run unattended or be triggered on a schedule.

## Procedure

1. **Receive inputs.** Confirm, per `INPUTS.md`, which of the following
   were explicitly provided for this run: authorized repositories,
   baseline, time range, files/areas in scope, repository conventions.
   Record anything not provided as explicitly absent — do not
   substitute an assumption.
2. **Verify accessibility.** For each authorized repository, confirm it
   is actually accessible for this run. If it is not, record it under
   `Repositories inaccessible` in the report's `Run Metadata` — do not
   proceed as if it were accessible, and do not treat inaccessibility as
   evidence of anything about that repository's state.
3. **Gather evidence, within scope only.** For each accessible
   repository, gather evidence only within the categories listed in
   `ROLE.md`'s Responsibilities — commits, branches, pull requests,
   merges, releases, new/moved/deleted files, changes to `STATE.md` or
   `CHANGELOG.md`, ADRs and their statuses, specifications,
   investigations, registry/index files, mechanically-detectable broken
   internal references, missing registration of an existing document,
   and the delta against the last known baseline.
4. **Classify each finding.** Place each finding into exactly one of
   `Confirmed Changes`, `Current-State Observations`, or `Structural
   Signals` (see `OUTPUTS.md` for the distinction) — never into a
   `Recommendations` or `Conclusions` section, because neither exists in
   this format.
5. **Attach evidence to every claim.** No claim is recorded without a
   matching `Evidence` entry: repository, commit/PR/branch where
   applicable, file path, line range or diff reference where available,
   and observation method.
6. **Escalate rather than guess.** If evidence is ambiguous, or access is
   uncertain, stop evaluating that specific point and record it under
   `Unknowns and Access Gaps` as `UNKNOWN` or `INSUFFICIENT ACCESS` — do
   not resolve the ambiguity by inference.
7. **Produce exactly one Observation Report.** One run produces one
   report, in the exact structure defined in `OUTPUTS.md`. A run is not
   split across multiple reports, and multiple runs are not merged into
   one.
8. **Append to history, nothing else.** Record this run in `HISTORY.md`
   — Run ID, date, one-line summary. No other file in this Role's
   folder, and no file anywhere outside it, is modified as part of a
   run.
9. **Never take a write action.** At every step above, no commit, no
   branch, no pull request, and no edit to any repository is created —
   this holds regardless of what is found during the run.

## Stop rule

If continuing at any step would require guessing, interpreting another
party's intent, or writing to a repository, the correct action is to
stop at that point and record the gap — not to proceed on a
reasonable-sounding assumption. This rule overrides any pressure toward
completeness: an incomplete but honest report is always preferable to a
complete but partially invented one.

## Relationship to other documents

`INPUTS.md` defines step 1 in full. `OUTPUTS.md` defines the report
format referenced in steps 4–7. `LIMITATIONS.md` governs step 9 and the
stop rule above. `CHECKLIST.md` provides a condensed, practical version
of this entire procedure for quick verification.
