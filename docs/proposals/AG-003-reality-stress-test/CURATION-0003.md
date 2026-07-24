# AG-003 Curation Pass — Dataset 2 (Project Documentation)

Source: `../../ai-organization/employees/AG-002-discovery-archaeologist/
runs/STRESS-RUN-0003-recovery-report.md`. Per `CURATION-PROTOCOL.md`
Stages 1–9.

## Knowledge Objects created

### KO-S2-01 — Human Authority Gate (HAG)

```yaml
id: KO-S2-01
title: "Human Authority Gate (HAG)"
status: Draft
first_seen: "2026-07-24"
last_seen: "2026-07-24"
occurrences: 1
confidence: 0.4   # citation_factor 1.0 * diversity_factor 0.4 (single source, ADR-0001) * contradiction_factor 1.0
maturity: Emerging   # 1 occurrence — below Recurring's 2+ threshold
derived_from: []
supported_by: []
contradicted_by: []
related_objects:
  - {ko_id: KO-S2-02, type: depends_on}   # RI-6 (Export Bridge) explicitly applies the HAG concept
related_objects_pending: []
candidate_investigations: []
provenance:
  - report: "../../ai-organization/employees/AG-002-discovery-archaeologist/runs/STRESS-RUN-0003-recovery-report.md"
    finding_id: RI-1
    date: "2026-07-24"
    citation: "ADR-0001 §2: a Human Authority Gate is any action requiring explicit human authorization before the organization may continue; crossing one is a normal state transition, never an error."
```

**Note on `maturity: Emerging`, occurrences: 1**: `RI-2` (Standard Agent
Behavior) and `RI-3` (four-category principle) are **not** treated as
additional occurrences of `KO-S2-01` — they are related-but-distinct
ideas (a behavior protocol and a classification scheme that both *use*
the HAG concept, not restatements of the HAG definition itself). This is
a deliberate test of over-counting: an eager curator could inflate
`occurrences` to 3 by treating every mention of "HAG" as a new
occurrence of the same claim. `KNOWLEDGE-OBJECT-SPEC.md`'s `occurrences`
rule requires distinct citations of the *same claim*, not co-occurring
related claims — `RI-2` and `RI-3` are curated as their own Knowledge
Objects (`KO-S2-03`, `KO-S2-04`, not filed in full here for space) with
`supports` or `related_objects` edges to `KO-S2-01`, not folded into its
count.

### KO-S2-02 — Human-Mediated Export Bridge

```yaml
id: KO-S2-02
title: "Human-Mediated Export Bridge"
status: Draft
first_seen: "2026-07-24"
last_seen: "2026-07-24"
occurrences: 1
confidence: 0.4
maturity: Emerging
derived_from: []
supported_by: []
contradicted_by: []
related_objects:
  - {ko_id: KO-S2-01, type: depends_on}
candidate_investigations: []
provenance:
  - report: "../../ai-organization/employees/AG-002-discovery-archaeologist/runs/STRESS-RUN-0003-recovery-report.md"
    finding_id: RI-6
    date: "2026-07-24"
    citation: "ADR-0002 §2: a human periodically exports Drive content into a Git-tracked location; AG-002 reads it exactly as it reads MEM-001."
```

### KO-S2-03 — Reality Inbox freeze (two fixed properties)

```yaml
id: KO-S2-03
title: "Reality Inbox freeze: single folder + manifest-only state"
status: Draft
first_seen: "2026-07-24"
last_seen: "2026-07-24"
occurrences: 1
confidence: 0.4
maturity: Emerging
derived_from: []
supported_by: []
contradicted_by: []
related_objects:
  - {ko_id: KO-S2-04, type: SEE_FINDING_REL-S2-01}   # see below — this edge is exactly what exposed the ontology gap
candidate_investigations: []
provenance:
  - report: "../../ai-organization/employees/AG-002-discovery-archaeologist/runs/STRESS-RUN-0003-recovery-report.md"
    finding_id: RI-8
    date: "2026-07-24"
    citation: "ADR-0003 §2: exactly one human-facing folder; processing state tracked only through manifests, never folder location."
```

### KO-S2-04 — Local-Drive-synced intake amendment

```yaml
id: KO-S2-04
title: "Local-Drive-synced Reality Inbox intake (two operating modes)"
status: Draft
first_seen: "2026-07-24"
last_seen: "2026-07-24"
occurrences: 1
confidence: 0.4
maturity: Emerging
derived_from: []
supported_by: []
contradicted_by: []
related_objects:
  - {ko_id: KO-S2-03, type: SEE_FINDING_REL-S2-01}
candidate_investigations: []
provenance:
  - report: "../../ai-organization/employees/AG-002-discovery-archaeologist/runs/STRESS-RUN-0003-recovery-report.md"
    finding_id: RI-11
    date: "2026-07-24"
    citation: "ADR-0004 §3: primary human-facing folder becomes a local Drive-synced path for reachable sessions; reality-inbox/DROP HERE kept as fallback."
```

## Relationship Proposal REL-S2-01 — the finding that exposed a real ontology gap

**Source Knowledge Object**: `KO-S2-04` (local-Drive-synced intake).
**Target Knowledge Object**: `KO-S2-03` (Reality Inbox freeze).

**Evidence**: `ADR-0004`'s own header states, verbatim: *"Amends:
`ADR-0003-reality-inbox-architecture.md`... This ADR does not violate
that freeze silently — it is the 'new ADR' `ADR-0003` §3 itself
requires before changing that property."* `ADR-0003`'s own text (as
amended) confirms: *"This ADR's §2, property 1... is amended, not
overridden... The property itself... is unchanged; only which
filesystem it lives on depends on which session is running."*

**Attempted type selection, against `RELATIONSHIP-ONTOLOGY.md`'s seven
types:**

- **Not `supersedes`** — `supersedes` requires B to be *"the version
  that should now be treated as current"* for *"the same underlying
  claim,"* with A *"no longer the going-forward statement."* But only
  **one of `KO-S2-03`'s two properties** (the single-folder-location
  claim) is revised — the other (manifest-only state tracking) is
  completely untouched and remains fully current. Applying `supersedes`
  to the whole object would misrepresent property 2 as superseded when
  it is not.
- **Not `derived_from`** — `KO-S2-04` does not extract or recombine
  `KO-S2-03`'s content into a new, independently-standing claim; it
  modifies one specific, named property of `KO-S2-03` in place, while
  `KO-S2-03` continues to be cited as the still-frozen architecture.
- **Not `depends_on`** — `KO-S2-04`'s validity is not merely
  *conditional* on `KO-S2-03` remaining true; `KO-S2-04` actively
  changes one of `KO-S2-03`'s own stated properties. `depends_on`
  describes a one-way reliance, not an edit.
- **Not `supports`, `contradicts`, `inspired`, or `alternative_to`** —
  none fit even loosely; `KO-S2-04` is neither corroborating evidence,
  a logical incompatibility, a source of inspiration for an unrelated
  claim, nor a competing alternative to `KO-S2-03`.

**Finding**: none of the seven relationship types in
`RELATIONSHIP-ONTOLOGY.md` cleanly describes what the source itself
calls "amend" — a later document that revises **one specific, named
property** of an earlier Knowledge Object while explicitly leaving the
rest of that object unchanged and current. This is a real,
source-declared relationship shape (not inferred, not hypothetical) that
this run's evidence shows the ontology cannot express without either
overclaiming (forcing `supersedes` onto the whole object, which the
source explicitly says is wrong — `ADR-0003`'s own amended text states
the freeze is *"amended, not violated"*) or underclaiming
(`depends_on`, which loses the fact that `KO-S2-04` actively changes
`KO-S2-03`, not merely relies on it).

**Recommendation**: do not force a type. File this relationship as
`INSUFFICIENT EVIDENCE` **against the ontology, not against the
source** — the source's own claim is completely clear; what is
insufficient is `RELATIONSHIP-ONTOLOGY.md`'s current type set for
expressing it precisely. See `REALITY-STRESS-TEST-REPORT.md`
finding **F-1** and the resulting correction.

## What did NOT happen (a deliberate negative check)

`ADR-0003`'s own header states the requesting task named it "ADR-0002,"
which collides with the ID (not the content) of `ADR-0002-ag002-
alternative-memory-access.md`. This curation pass checked whether this
collision should produce a Knowledge Merge Proposal between `KO-S2-02`
(built from the real `ADR-0002`) and `KO-S2-03` (built from `ADR-0003`,
the document that was *almost* misnumbered "ADR-0002"). **No merge
proposal is warranted and none is filed**: the collision was in a
*requested* label that was never actually assigned — `ADR-0003`'s own
text resolved it before either AG-002 or AG-003 ever saw the documents,
and the two Knowledge Objects' actual content (an export-bridge decision
vs. a Reality Inbox freeze) shares no overlapping claim. This is
recorded explicitly as a checked-and-declined case, per the same
discipline `CONTRADICTION-CHECK-0001.md` used in the first walkthrough —
finding a surface-level ID collision and correctly not treating it as a
content collision.

## Provenance

`../../ai-organization/employees/AG-002-discovery-archaeologist/runs/
STRESS-RUN-0003-recovery-report.md`, `RI-1`, `RI-6`, `RI-8`, `RI-10`,
`RI-11`.
