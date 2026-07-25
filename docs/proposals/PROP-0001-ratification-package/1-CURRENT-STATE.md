# Deliverable 1 — Current `PROP-0001` State

Source: `docs/proposals/PROP-0001-discovery-lab-boundaries.md`, read
in full, unmodified. Nothing in this package changes a word of it.

## Header, verbatim

> Status: DRAFT PROPOSAL — not accepted, not an ADR (revision 3,
> post-adversarial-review)
> Date: 2026-07-24
> Author: Implementer session (Claude Code)
> Depends on: `docs/investigations/INV-0001-discovery-lab-mandate.md`
> and `docs/investigations/INV-0002-independent-architecture-passes.md`

## What "revision 3, post-adversarial-review" means concretely

The document has already been through one full internal cycle: a
first draft, a rebuild from three independent architecture passes
(`INV-0002`), and a named "Adversarial Review — vFinal" (dated
2026-07-24) that returned **`APPROVE WITH MINOR CHANGES`**. All six
risks that review found were judged fixable without reopening the
core Variant A/B/C decision, and every fix was applied directly in the
document (Principle 0's wording, the Recommendation Ledger's status
discipline, the Evidence Coverage field, `C2`'s scope narrowing, the
KOD Research Guardian non-duplication note, the scope-stability rule,
the archive-trigger threshold). This is not a first draft awaiting
initial review — it is a document that already survived one.

## What is recommended, but not yet decided

**Variant B — Ecosystem Observatory, alone, for now** — read-only,
proposal-only, cross-repository status-checking. Not Variant A
(Experiment Laboratory) or Variant C (Combined). The recommendation
itself is explicitly marked, in the document's own words: *"This
recommendation is not an acceptance. It requires a human decision
before any variant governs how discovery-lab is actually used."*

## What has happened in this ecosystem since, without the mandate being ratified

`AG-002` (Discovery Archaeologist) and `AG-003` (Knowledge Curator)
were designed, adversarially reviewed, reality-stress-tested (4/4
datasets `PASS`), and marked **`FROZEN v1.0`** — per
`docs/ai-organization/EMPLOYEE-REGISTRY.md`, both remain
**`Prototype (not adopted)`** on the organizational-trust axis while
`FROZEN` on the architecture-stability axis; `discovery-lab`'s own
`STATE.md` records real work: 7 `AG-002` runs, 3 `AG-003` curation
passes, and — as of `EXEC-001` — one real, human-approved, filed
Knowledge Object (`memory/knowledge-objects/KO-S3-01.md`). All of this
happened while the mandate that authorizes `discovery-lab` to exist and
operate has remained `DRAFT` throughout. `ARCH-001` named this
sequencing the ecosystem's single highest architectural risk (`R1`);
`ARCH-002` (`G5`) and `G2`'s own verdict both reconfirmed it,
unresolved, without re-litigating it further. This package is the
first task in the session whose explicit purpose is to move that
sequencing toward resolution — by preparing the decision, not making
it.
