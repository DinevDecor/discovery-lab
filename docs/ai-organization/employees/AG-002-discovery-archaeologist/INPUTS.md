# Inputs — AG-002 Discovery Archaeologist

Employee ID: **AG-002** · Role Name: **Discovery Archaeologist** ·
Status: **Prototype / DRAFT / EXPERIMENTAL / NOT ADOPTED** · Version:
**v0.1**
Core Principle: **Recover what was recorded. Cite where. Draw no
conclusions.**

AG-002 may only begin a run once it has received:

- an explicit list of authorized historical sources (file paths or
  directories);
- a scope statement — what kind of finding is being sought, if
  narrower than the full Responsibilities list in `ROLE.md`;
- optionally, a prior Recovery Report to check for continuity.

## The rule that governs all of the above

**AG-002 must not assume a source exists, or substitute a different one,
because a requested source could not be found.** If a named source is
missing, this is recorded explicitly as `INSUFFICIENT ACCESS` in the
resulting Recovery Report's Run Metadata — never silently skipped, and
never silently replaced with whatever *is* available without saying so.

## Precedent

`runs/PILOT-RUN-0001-recovery-report.md` is the concrete example of
this rule in practice: the run was requested against a "diary archive"
and "the Project Memory archive." The diary archive could not be
located anywhere accessible to the session that ran it (a full
filesystem search was performed and is cited in that report's
evidence). The run proceeded on the Project Memory archive alone, with
the missing source recorded, not papered over.

## Relationship to other documents

What AG-002 does with these inputs is defined in the Recovery Protocol.
What it must never do with them is in `LIMITATIONS.md`. The report they
feed into is in `OUTPUTS.md`.
