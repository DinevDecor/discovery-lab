# Knowledge Object KO-0001

Demonstration object — not filed to a real Knowledge Base (see
`README.md`). Format per `../../ai-organization/employees/
AG-003-knowledge-curator/KNOWLEDGE-OBJECT-SPEC.md`.

```yaml
id: KO-0001
title: "Nature as a library of architectures"
status: Draft
first_seen: "2026-06-25"
last_seen: "2026-07-11"
occurrences: 5
confidence: 0.4
maturity: Recurring
derived_from: []
supported_by: []
contradicted_by: []
related_objects: []
candidate_investigations: []
provenance:
  - report: "../../ai-organization/employees/AG-002-discovery-archaeologist/runs/PILOT-RUN-0002-recovery-report.md"
    finding_id: RI-5
    date: "2026-06-25"
    citation: >
      KOD-RESEARCH-METHOD-NATURAL-ARCHITECTURES-001, confidence 0.82 (a
      GRIF's own field - see confidence note below). Method: strip
      organism-specific traits from radically different organisms to
      find a candidate fundamental process.
  - report: "../../ai-organization/employees/AG-002-discovery-archaeologist/runs/PILOT-RUN-0002-recovery-report.md"
    finding_id: RT-3
    date: "2026-06-26"
    citation: >
      A reflective restatement - the search shifts from "the smallest
      thing the world is built from" to "the simplest processes."
  - report: "../../ai-organization/employees/AG-002-discovery-archaeologist/runs/PILOT-RUN-0002-recovery-report.md"
    finding_id: RT-3
    date: "2026-06-27"
    citation: >
      A fuller rewrite of the same method, adding a structured
      "Atlas of Architectures" template.
  - report: "../../ai-organization/employees/AG-002-discovery-archaeologist/runs/PILOT-RUN-0002-recovery-report.md"
    finding_id: RT-3
    date: "2026-07-10"
    citation: "Echoed as \"Distributed Architectures and the Emergence of Wholes.\""
  - report: "../../ai-organization/employees/AG-002-discovery-archaeologist/runs/PILOT-RUN-0002-recovery-report.md"
    finding_id: RT-3
    date: "2026-07-11"
    citation: "Echoed again as \"From local interactions to coordination.\""
```

## Why `occurrences: 5`, not fewer

AG-002's own Repeated Theme RT-3 already counted these as five
independent restatements, across five distinct diary dates, spanning a
month. AG-003 does not re-split or re-merge that count — it is carried
forward exactly as AG-002 recorded it (`CURATION-PROTOCOL.md` Stage 2).

## Why `maturity: Recurring`, not `Convergent`

`../../ai-organization/employees/AG-003-knowledge-curator/
KNOWLEDGE-OBJECT-SPEC.md` requires `Convergent` to span **at least two
independent sources or two independent Recovery Report runs**. All five
citations here come from the same diary archive (`oneDay 6.zip`), read
in a single AG-002 run (`PILOT-RUN-0002`). Five restatements within one
source, however striking, is `Recurring`, not `Convergent` — this is a
deliberate, conservative reading, not an oversight; see
`CPP-0001-nature-as-library-draft-to-candidate.md` for what this means
for promotion.

## Confidence note

`confidence: 0.4` is computed per `KNOWLEDGE-OBJECT-SPEC.md`'s formula:
`citation_factor (1.0, all 5 citations exact and checkable) *
diversity_factor (0.4, single source / single AG-002 run) *
contradiction_factor (1.0, no open Contradiction Report) = 0.4`. This is
**not** the same value as RI-5's own GRIF `confidence: 0.82` field, which
is KOD's internal assessment of that one GRIF document, preserved
verbatim in this object's `provenance` (first entry) rather than merged
into `KO-0001`'s own `confidence` (`ROLE.md`'s Terminology note;
`KNOWLEDGE-OBJECT-SPEC.md`'s "Confidence" rule).
