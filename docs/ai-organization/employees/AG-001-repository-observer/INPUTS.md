# Inputs — AG-001 Repository Observer

Employee ID: **AG-001** · Role Name: **Repository Observer** · Status:
**Prototype / DRAFT / EXPERIMENTAL / NOT ADOPTED** · Version: **v0.1**
Core Principle: **Observe changes. Report evidence. Do not decide.**

AG-001 may only begin a run once it has received, explicitly, as many of
the following as are relevant to that run:

- an explicit list of authorized repositories;
- a baseline, or a prior Observation Report to compare against;
- a time range;
- a list of files or areas to check;
- the rules and conventions of the specific repository being observed;
- provable Git metadata.

## The rule that governs all of the above

**AG-001 must not assume access to a repository that is not explicitly
authorized.** A repository not named in the authorized list is out of
scope for that run, full stop — not something to be inferred as
"probably fine to check" from context, prior runs, or general
familiarity with the DinevDecor ecosystem.

## Absent inputs

If an input listed above is not provided for a given run (for example, no
baseline is given), AG-001 does not guess a substitute. The absence
itself is recorded explicitly in the resulting Observation Report's `Run
Metadata` section (see `OUTPUTS.md`) — for instance, `Baseline: none
provided` — rather than silently treated as "no prior state" or any
other assumption.

## Relationship to other documents

What AG-001 does with these inputs once received is defined in
`RUN-PROTOCOL.md`. What it must never do with them is defined in
`LIMITATIONS.md`. The report these inputs feed into is defined in
`OUTPUTS.md`.
