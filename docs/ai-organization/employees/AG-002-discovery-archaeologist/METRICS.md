# Metrics — AG-002 Discovery Archaeologist

Employee ID: **AG-002** · Role Name: **Discovery Archaeologist** ·
Status: **FROZEN** · Version:
**1.0**

This document defines AG-002's quality-measurement **interface** only.
No aggregate score, no invented starting values — matching AG-001's
`../AG-001-repository-observer/METRICS.md` precedent.

## Metrics

- **`source_coverage`** — of the sources requested, what proportion
  were actually scanned in full.
- **`citation_completeness`** — of all findings reported, what
  proportion carry a valid, checkable Evidence citation.
- **`unsupported_claim_rate`** — of all findings, what proportion lack
  a citation that actually supports them on inspection.
- **`duplicate_preservation_compliance`** — whether any duplicate was
  ever removed rather than preserved and cited (should always read
  zero violations; any nonzero value is a boundary violation, not a
  quality nuance).
- **`recovery_yield`** — count of candidate findings per source scanned
  — a volume signal only, not a quality signal on its own.
- **`cross_source_convergence_rate`** — proportion of recovered ideas
  that appear in more than one independent source (a stronger form of
  evidence than a single-source finding).

## No aggregate score

These metrics are not combined into a single "recovery quality" score.
A general trust-scoring pipeline is trust-engine's territory (`../../../
proposals/PROP-0001-discovery-lab-boundaries.md`, ground rule 3), not
this Role's.

## Measured, not assumed

`runs/PILOT-RUN-0001-recovery-report.md` is this Role's first and only
run to date. Any metric value reported there is a description of that
one run, not a validated baseline — one data point is not a trend.
