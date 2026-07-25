# AG-003 Curation Pass — Dataset 4 (Operational Material, trust-engine)

Source: `../../ai-organization/employees/AG-002-discovery-archaeologist/
runs/STRESS-RUN-0005-recovery-report.md`. Per `CURATION-PROTOCOL.md`
Stages 1–9.

## Knowledge Objects created

### KO-S4-01 — trust_engine `M1`/`М1` model-identity collision (real system bug)

```yaml
id: KO-S4-01
title: "trust_engine: Latin/Cyrillic model-ID collision (M1 vs М1)"
status: Draft
first_seen: "2026-06-17"
last_seen: "2026-06-17"
occurrences: 1
confidence: 0.4
maturity: Emerging
derived_from: []
supported_by: []
contradicted_by: []
related_objects:
  - {ko_id: KO-S4-02, type: depends_on}   # RI-2's migration exclusion depends on this bug's existence
candidate_investigations: [CI-9]
provenance:
  - report: "../../ai-organization/employees/AG-002-discovery-archaeologist/runs/STRESS-RUN-0005-recovery-report.md"
    finding_id: RI-1
    date: "2026-06-17"
    citation: "trust_engine_audit_report.md: normalized_key M1, original_values \"M1, М1\", unicode_codepoints U+004D U+0031 vs U+041C U+0031, severity High."
```

**Deliberate restraint check — the trap this dataset was built to
test**: this curation pass did **not** create two separate Knowledge
Objects ("M1" and "М1") and did **not** propose a Knowledge Merge
Proposal to combine them. `RI-1`'s own text is a single finding — *the
audited system contains two distinct strings for one intended
identity* — not two independently-recovered ideas that happen to look
alike. Treating "M1" and "М1" as two candidate duplicates would
misread a bug report as if it were two overlapping pieces of curated
knowledge, exactly the false-merge-proposal failure mode this stress
test's task description asks to hunt for. `KO-S4-01` is one object; its
own content documents the two-string collision as evidence, not as two
separate objects' identity.

### KO-S4-02 — Phase 1 migration: excludes flagged rows, does not fix them

```yaml
id: KO-S4-02
title: "trust_engine Phase 1 migration excludes (not fixes) audit-flagged rows"
status: Draft
first_seen: "2026-06-18"
last_seen: "2026-06-18"
occurrences: 1
confidence: 0.4
maturity: Emerging
derived_from: []
supported_by: [KO-S4-01]
contradicted_by: []
related_objects: []
candidate_investigations: []
provenance:
  - report: "../../ai-organization/employees/AG-002-discovery-archaeologist/runs/STRESS-RUN-0005-recovery-report.md"
    finding_id: RI-2
    date: "2026-06-18"
    citation: "phase1_prediction_reviews_report.md: eligible_count=3 (of 5), memory_id 3 and 5 excluded from eligible set; PASS/84 checks describes correct exclusion, not resolution of RI-1's data-quality issues."
```

## Relationship Proposal REL-S4-01

**Source**: `KO-S4-03` (Outcome Tracking, not filed in full here for
space — `RI-3`). **Target**: `KO-S4-02` (Phase 1 migration).

**Evidence**: `RI-3`'s "Protected Tables" list names `predictions` and
`prediction_reviews` — the exact tables `RI-2`'s migration created.

**Proposed type**: `depends_on` — Outcome Tracking's own design
(explicitly not writing to those tables) presupposes they already exist
with the schema the migration created; if the migration's schema
changed incompatibly, Outcome Tracking's own protected-tables list would
need reconsideration.

**Why not `supports` or `derived_from`**: `supports` would understate
the relationship — Outcome Tracking isn't offering corroborating
evidence *for* the migration, it structurally relies on the migration's
schema already being in place. `derived_from` would overstate it —
Outcome Tracking's own content (manual outcome recording) is not
extracted or recombined from the migration's content; it merely respects
a boundary the migration established.

**Confidence caveat, stated plainly**: this relationship is inferred
from **shared table names alone** — `RI-3` carries no date and no
explicit citation of `RI-2` or the migration by name. This is weaker
evidence than `STRESS-RUN-0003`'s header-declared relationships and
roughly comparable in strength to `STRESS-RUN-0004`'s content-order
inference. Filed as `depends_on`, flagged `INSUFFICIENT EVIDENCE` on
strength (not on type-fit, unlike `REL-S2-01`'s finding) — a different
kind of uncertainty than dataset 2 produced, worth distinguishing in the
cross-dataset analysis.

## Contradiction screening — explicitly declined

Checked whether `KO-S4-01` (the `M1`/`М1` bug) and `KO-S4-02` (migration
`PASS`) should generate a Contradiction Report — a naive reading could
see "Blocked" (audit) and "PASS" (migration) as two claims that cannot
both be true. **Declined**: they are not claims about the same subject.
`RI-1`'s "Blocked" describes migration-*readiness* before cleanup;
`RI-2`'s "PASS" describes the migration *script's own execution
correctness* after deliberately excluding the blocking rows — different
subjects, not a contradiction. This mirrors `CONTRADICTION-CHECK-0001.md`'s
discipline from the first walkthrough: checking a plausible-looking
candidate against the actual text before filing anything.

## Provenance

`../../ai-organization/employees/AG-002-discovery-archaeologist/runs/
STRESS-RUN-0005-recovery-report.md`, `RI-1`, `RI-2`, `RI-3`.
