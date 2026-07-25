# Inputs — AG-002 Discovery Archaeologist

Employee ID: **AG-002** · Role Name: **Discovery Archaeologist** ·
Status: **FROZEN** · Version:
**1.0**
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

## Default operational source: the Reality Inbox

Added 2026-07-24, per the "Create the Reality Inbox" task. AG-002's
**default operational source is `../../../../reality-inbox/`** (the
Reality Inbox — see `../../../../reality-inbox/README.md` and
`../../../../reality-inbox/PROCESSING-PROTOCOL.md`), not the raw
repository. Concretely:

- AG-002 may only process a Reality Inbox file that has a **manifest**
  in `reality-inbox/manifests/` with `status: ACCEPTED` and a
  complete provenance block. A file without one, or with insufficient
  provenance (missing fields, unresolved sensitivity, a content-hash
  mismatch), is not a valid source — see `LIMITATIONS.md`'s `BLOCKED`
  escalation value.
- AG-002 **never scans unrelated repository content as memory.** The
  Reality Inbox (manifested files) and the previously-established
  `../../../../memory/` mirror (`MEM-003` et al., registered in
  `../../MEMORY-SOURCES/MEMORY-SOURCE-REGISTRY.md`) remain the only
  source classes AG-002 treats as historical evidence — not
  `discovery-lab`'s own documentation, code, or any other file it
  happens to have read access to.
- This does not relax the rule above ("an explicit list of authorized
  historical sources") — it specifies *where that list is drawn from*
  by default, the same way the Memory Source Registry did for
  `project-memory/archive/` (`MEM-001`) in an earlier task.

## Relationship to other documents

What AG-002 does with these inputs is defined in the Recovery Protocol.
What it must never do with them is in `LIMITATIONS.md`. The report they
feed into is in `OUTPUTS.md`.
