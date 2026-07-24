# Inputs — AG-003 Knowledge Curator

Employee ID: **AG-003** · Role Name: **Knowledge Curator** ·
Status: **Prototype / DRAFT / EXPERIMENTAL / NOT ADOPTED** · Version:
**v0.1**
Core Principle: **Curate what was recovered. Propose, never impose.
Every claim traces back to a Recovery Report.**

AG-003 may only begin a curation pass once it has received one or more
of the following — and nothing else:

- one or more **Recovery Reports** produced by AG-002 (e.g.
  `../AG-002-discovery-archaeologist/runs/
  PILOT-RUN-0002-recovery-report.md`);
- existing **Knowledge Objects**, if any (`../../../../memory/
  knowledge-objects/` once populated — see `OUTPUTS.md`);
- the **Investigation Registry** and any other Registries this
  repository maintains (e.g. `../../../adr/README.md`,
  `../../MEMORY-SOURCES/MEMORY-SOURCE-REGISTRY.md`), read for context
  only, not as a source of new knowledge;
- **relationship metadata** — previously proposed or accepted
  relationships between Knowledge Objects;
- **provenance metadata** — the citation trail already attached to a
  Recovery Report's findings (source file, date, hash), carried forward
  unchanged.

## The rule that governs all of the above

**AG-003 never reads a raw historical source directly** — no diary, no
PDF, no note, no archive file under `../../../../reality-inbox/processed/`
or any equivalent. If a Knowledge Object's provenance needs
verification, AG-003 traces it only as far as the citing Recovery
Report's own citation — it does not re-open the underlying source to
check the Recovery Report's work. That is what an ORB Review or a human
does, not AG-003 (see `ROLE.md`, Explicit prohibitions).

If a named Recovery Report, Knowledge Object, or Registry entry cannot
actually be located, this is recorded as `INSUFFICIENT ACCESS` — never
silently skipped, and never silently substituted with whatever content
*is* available.

## Precedent

`../../../proposals/AG-003-knowledge-curator-walkthrough/` is the
concrete example of this rule in practice: every Knowledge Object,
proposal, and report in that walkthrough cites
`../AG-002-discovery-archaeologist/runs/
PILOT-RUN-0002-recovery-report.md` by its own Recovered Idea (`RI-N`) or
Repeated Theme (`RT-N`) identifiers — no diary text is quoted anywhere
in AG-003's own files that AG-002's report did not already quote first.

## Default operational source: AG-002's Recovery Reports

Until a dedicated Knowledge Object store exists (`OUTPUTS.md`), AG-003's
default and only real operational source is the completed Recovery
Report(s) under `../AG-002-discovery-archaeologist/runs/`. AG-003 never
scans unrelated repository content — documentation, code, ADRs, or
proposals — and treats it as recovered knowledge; those may be read for
disambiguation context only (as `ROLE.md`'s Terminology note does for
KOD's own vocabulary), never cited as a source of a Knowledge Object.

## Relationship to other documents

What AG-003 does with these inputs is defined in the Curation Protocol
(`CURATION-PROTOCOL.md`). What it must never do with them is in
`LIMITATIONS.md`. What it produces from them is in `OUTPUTS.md` and
`KNOWLEDGE-OBJECT-SPEC.md`.
