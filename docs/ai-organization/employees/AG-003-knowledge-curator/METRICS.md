# Metrics — AG-003 Knowledge Curator

Employee ID: **AG-003** · Role Name: **Knowledge Curator** ·
Status: **Prototype / DRAFT / EXPERIMENTAL / NOT ADOPTED** · Version:
**v0.1**

This document defines AG-003's quality-measurement **interface** only.
No aggregate score, no invented starting values — matching AG-001's and
AG-002's own `METRICS.md` precedent.

## Metrics

- **`citation_completeness`** — of all Knowledge Objects and proposals
  produced, what proportion carry a valid, checkable `Provenance`
  citation back to a specific Recovery Report identifier.
- **`merge_proposal_precision`** — of Knowledge Merge Proposals filed,
  what proportion are accepted (versus rejected as false positives) once
  reviewed — measured only after a Knowledge Review has actually
  occurred (`REVIEW-PROTOCOL.md`); undefined until then.
- **`relationship_explainability`** — of Relationship Proposals filed,
  what proportion include a stated reason for rejecting each confusable
  alternative type (`RELATIONSHIP-ONTOLOGY.md`) — should always read
  100%; a proposal without this reasoning is invalid under `OUTPUTS.md`,
  not merely low-quality.
- **`promotion_proposal_discipline`** — count of any `status` field
  changed without a corresponding accepted Core Principle Proposal
  (should always read zero; any nonzero value is a boundary violation,
  not a quality nuance).
- **`contradiction_report_restraint`** — count of any Contradiction
  Report that proposed a resolution, or that escalated past an existing
  AG-002 `INSUFFICIENT EVIDENCE` marking without new cited evidence
  (should always read zero).
- **`gap_report_deduplication`** — count of any Gap Report that minted a
  new `CI-NNNN` for a gap AG-002 had already assigned one to (should
  always read zero).
- **`knowledge_base_coverage`** — of all Recovered Ideas and Repeated
  Themes across authorized Recovery Reports, what proportion have a
  corresponding Knowledge Object — a volume signal only, not a quality
  signal on its own.

## No aggregate score

These metrics are not combined into a single "curation quality" score. A
general trust-scoring pipeline is trust-engine's territory (per
`../../../proposals/PROP-0001-discovery-lab-boundaries.md`, ground rule
3), not this Role's.

## Measured, not assumed

AG-003 has had no real run as of v0.1 — see `STATUS.yaml`. The worked
example in `../../../proposals/AG-003-knowledge-curator-walkthrough/` is
an architecture demonstration, not a scored run; none of the metrics
above have a real value yet.
