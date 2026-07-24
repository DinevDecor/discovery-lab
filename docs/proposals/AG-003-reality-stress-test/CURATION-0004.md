# AG-003 Curation Pass — Dataset 3 (Research/Investigation, KOD)

Source: `../../ai-organization/employees/AG-002-discovery-archaeologist/
runs/STRESS-RUN-0004-recovery-report.md`. Per `CURATION-PROTOCOL.md`
Stages 1–9.

## Knowledge Objects created

### KO-S3-01 — "Research process matters more than conclusions"

```yaml
id: KO-S3-01
title: "The research process matters more than its conclusions"
status: Draft
first_seen: "unknown-within-2026-07-24-snapshot"   # see maturity note below
last_seen: "unknown-within-2026-07-24-snapshot"
occurrences: 3
confidence: 0.4   # citation_factor 1.0 * diversity_factor 0.4 * contradiction_factor 1.0 — see maturity note
maturity: Recurring   # NOT Convergent — see Finding F-2 below
derived_from: []
supported_by: []
contradicted_by: []
related_objects: []
candidate_investigations: []
provenance:
  - report: "../../ai-organization/employees/AG-002-discovery-archaeologist/runs/STRESS-RUN-0004-recovery-report.md"
    finding_id: RT-1
    date: "unknown (EX-0001_CASE.md carries no date)"
    citation: "\"the objective is not to preserve conclusions... is to preserve intellectual evolution\""
  - report: "../../ai-organization/employees/AG-002-discovery-archaeologist/runs/STRESS-RUN-0004-recovery-report.md"
    finding_id: RT-1
    date: "unknown (ART-0001.md carries no date)"
    citation: "\"The research process is more important than conclusions.\""
  - report: "../../ai-organization/employees/AG-002-discovery-archaeologist/runs/STRESS-RUN-0004-recovery-report.md"
    finding_id: RT-1
    date: "unknown (KOD ADR-0002.md carries no date)"
    citation: "\"KOD does not protect ideas. KOD protects honest research.\""
```

**Finding F-2 (maturity/source-granularity gap)**: `PROMOTION-RULES.md`
requires `maturity: Convergent` to span *"at least two independent
sources or two independent Recovery Report runs, not just multiple
restatements within one archive scanned once."* `KO-S3-01`'s three
citations come from **three different files** (`EX-0001_CASE.md`,
`ART-0001.md`, KOD's `ADR-0002.md`) but **one AG-002 run**
(`STRESS-RUN-0004`) over **one repository** (`kod`). Is that "two
independent sources," because the three claims live in three separate
documents with no stated authorship link between them — or is it "one
archive scanned once," the same situation `KO-0001`
(`../AG-003-knowledge-curator-walkthrough/
KO-0001-nature-as-library-of-architectures.md`) was correctly kept at
`Recurring` for, despite five citations, because all five came from one
diary? **`KNOWLEDGE-OBJECT-SPEC.md`'s `maturity` definition does not say
what counts as one "source" at the right granularity** — a whole
repository, or an individual file within it. This is a real,
reproducible gap the diary-only walkthrough never exposed, because the
diary was unambiguously one source (one zip archive). Resolved here
**conservatively, consistent with the `KO-0001` precedent**: `KO-S3-01`
is kept at `Recurring`, not `Convergent` — treating "one repository,
scanned in one run" as one source regardless of how many files it
spans, the same rule already implicit in `KO-0001`'s treatment. See
`REALITY-STRESS-TEST-REPORT.md` finding **F-2** and the resulting
correction to `KNOWLEDGE-OBJECT-SPEC.md`.

**Missing `first_seen`/`last_seen` note**: none of the three source
files carries a date (unlike the diary's per-entry dates or this
repository's own ADR headers). `first_seen`/`last_seen` are recorded as
`unknown-within-2026-07-24-snapshot` — the date this run copied the
files — rather than invented. This is itself a data-quality
characteristic of this dataset, distinct from datasets 1 and 2, both of
which had real per-item dates.

## Knowledge Merge Proposal KMP-S3-01 — "Reality is the final arbiter" (recommends MERGE)

**Candidate Knowledge Objects**: "Reality is the final arbiter of trust"
(`ART-0001`) and "Reality remains the final arbiter" (KOD `ADR-0002`).

**Evidence of overlap**: near-identical wording ("reality," "final
arbiter"), both asserted as a foundational, unqualified principle (not
hedged, not attributed to a further source), both within the same
repository's small corpus.

**Evidence of distinction**: `ART-0001`'s version is explicitly scoped
("of trust"); `ADR-0002`'s version appears in a passage about AI systems
not acting as final authorities over *research conclusions*, not
explicitly about "trust" as a named concept — the scope words differ,
and neither document cross-references the other.

**Assessment**: unlike `KMP-0001` in the first walkthrough (where
evidence of distinction was strong — different layer counts, different
concrete scope), here the evidence of distinction is thin: "trust" and
"AI systems must defer to reality over their own conclusions" are
plausibly the same underlying epistemic stance viewed from two angles,
not two different claims. The wording overlap is high enough, and the
distinguishing detail vague enough, that treating these as two separate
Knowledge Objects risks exactly the fragmentation the task's own failure
list names ("one idea split across multiple documents").

**Proposed unified object (if accepted)**: "Reality is the final
arbiter (of research validity / of trust)" — title deliberately keeps
both framings rather than picking one, since neither source is clearly
more authoritative.

**Reversibility statement**: both original citations are tagged
`merged_from_ko: KO-S3-02a` / `KO-S3-02b` respectively in the unified
object's `provenance` (per `OUTPUTS.md`'s `merged_from_ko` mechanism,
added in the prior adversarial review) — fully reversible.

**Recommendation**: **MERGE** — the opposite recommendation from
`KMP-0001`'s worked example, deliberately included in this stress test
to confirm AG-003's merge logic is not systematically biased toward
either "always merge" or "never merge," but genuinely evaluates each
case's own evidence of overlap versus distinction.

## Declined curation actions (deliberate restraint checks)

- **No Knowledge Object created for `RI-7`** (KOD's own Knowledge Object
  template). Its content is a bare list of section headers with no
  filled-in claim — there is no knowledge to curate, only a schema to
  observe. Creating a KO here would manufacture a finding from a
  document's *shape* rather than its *content*, exactly the kind of
  hallucination this stress test is designed to catch. Recorded instead
  as a disambiguation citation only (`ROLE.md`'s Terminology note already
  covers this).
- **No Knowledge Object created for `RI-2`** (`EX-0001`'s 0%-progress
  counters). This is operational metadata about a research process's
  own status, not a domain claim — curating it as a "Knowledge Object"
  would blur the line between AG-003's Knowledge Base and a project
  status tracker. Recorded as declined, with reasoning, not silently
  skipped.
- **No Core Principle Proposal filed for `KO-S3-01`**, despite
  `occurrences: 3` (the same count that made `CPP-0001` a strong case in
  the first walkthrough). At `maturity: Recurring` (per Finding F-2,
  above), `KO-S3-01` meets `PROMOTION-RULES.md`'s `Draft → Candidate
  Principle` threshold (`occurrences >= 2`, `maturity >= Recurring`) —
  **a Core Principle Proposal for this exact step would be justified**
  and is filed below as `CPP-S3-01`, but explicitly **not** for
  `Candidate → Validated`, for the same F-2 reason `KO-0001` was held
  back in the first walkthrough.

## Core Principle Proposal CPP-S3-01

**Subject**: `KO-S3-01`. **Current status**: `Draft`. **Proposed
status**: `Candidate Principle` — one step only.

**Evidence against the threshold**: `occurrences: 3` (≥ 2 required);
`maturity: Recurring` (≥ `Recurring` required); no open Contradiction
Report names `KO-S3-01`.

**What this proposal does NOT claim**: it does not claim `Validated
Principle` — that requires `Convergent` maturity (two independent
sources or runs), which Finding F-2 above explicitly withholds for this
object pending a resolved source-granularity rule.

**Recommendation**: accept `Draft → Candidate Principle`.

## Provenance

`../../ai-organization/employees/AG-002-discovery-archaeologist/runs/
STRESS-RUN-0004-recovery-report.md`, `RI-2`, `RI-3`, `RI-5`, `RI-7`,
`RT-1`, `RT-2`.
