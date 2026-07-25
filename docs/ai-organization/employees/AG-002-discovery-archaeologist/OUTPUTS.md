# Outputs — AG-002 Discovery Archaeologist

Employee ID: **AG-002** · Role Name: **Discovery Archaeologist** ·
Status: **FROZEN** · Version:
**1.0**
Core Principle: **Recover what was recorded. Cite where. Draw no
conclusions.**

Every run produces exactly **one** Recovery Report, in this format:

```
# Recovery Report

## Run Metadata
- Run ID:
- Timestamp:
- Sources requested:
- Sources scanned:
- Sources inaccessible:

## Executive Summary
## Recovered Ideas
## Repeated Themes
## Idea Evolution (Discovery Timeline)
## Forgotten Ideas
## Candidate Investigations
## Contradictions
## Open Questions
## Recovery Queue
## Evidence
## Archaeologist Boundary Statement
```

## Hard rules about this format

- **Every entry under Recovered Ideas, Repeated Themes, Idea Evolution,
  Forgotten Ideas, Contradictions, and Candidate Investigations must
  carry at least one citation** in the Evidence section — a claim
  without one is not valid under this format.
- **"Candidate Investigations" proposes; it does not create.** Naming a
  candidate here is not the same as opening an Investigation under
  `docs/investigations/` — that remains a separate, human-gated act.
- **Duplicates are never merged away.** If the same idea appears in
  three sources, all three are cited under Repeated Themes — this is
  not redundancy to be trimmed, it is the finding itself.
- **No idea is asserted as true, good, or worth pursuing.** Recovered
  Ideas and Forgotten Ideas describe *that* something was recorded and
  *where* — never whether it was right.
- **Contradictions distinguish two cases explicitly:** a live,
  unresolved disagreement between sources, versus a documented,
  self-aware revision (a later source explicitly superseding an earlier
  one). Conflating the two misrepresents the historical record.
- **Recovery Queue** lists clusters that appear to warrant further
  attention, addressed to a human or Curator — it is a proposal list,
  never an automatic trigger for anything.
- **The Archaeologist Boundary Statement is mandatory every time** —
  explicit confirmation that no source was modified and no content was
  invented, mirroring AG-001's own Observer Boundary Statement.

## Relationship to other documents

The procedure that produces this report is the Recovery Protocol
(`RUN-PROTOCOL.md`). What AG-002 may investigate is in `ROLE.md`'s
Responsibilities. A practical pre/during/post-run checklist is in
`CHECKLIST.md`.
