# Deliverable 9 — Ratification Record

## Decision

**Subject**: `PROP-0001` — Discovery Lab Mandate.
**Decision**: `ACCEPT`.
**Variant adopted**: **B — Ecosystem Observatory, alone, for now** —
the document's own single recommendation, per
`2-EXACT-PROPOSAL-TEXT.md`.
**Decision Maker**: Petko Dinev.
**Date**: 2026-07-25.
**Message, verbatim**: "ACCEPT".

## How the variant was determined

The message itself did not name a variant. Per `8-OPEN-QUESTIONS.md`
item 6, this was flagged in advance as a real ambiguity. Resolved by
reading "ACCEPT" against the ratification package's own structure: the
package (`README.md`, `2-EXACT-PROPOSAL-TEXT.md`,
`6-CONSEQUENCES-ACCEPT.md`) presented Variant B throughout as *the*
operative recommendation being put up for ratification, `PROP-0001`
itself recommends only Variant B ("Recommended: Variant B — Ecosystem
Observatory, alone, for now"), and no part of the exchange referenced
Variant A or C. This reading was stated explicitly and prominently at
the moment of acting on it, specifically so it could be corrected
immediately if wrong — it was not.

## What was mechanically done in response

1. `docs/proposals/PROP-0001-discovery-lab-boundaries.md`'s own status
   header updated from `DRAFT PROPOSAL — not accepted, not an ADR` to
   `ACCEPTED — Variant B (Ecosystem Observatory) adopted, 2026-07-25`,
   citing this record. The document's own self-classification ("not an
   ADR") is preserved — it was not renamed or moved into `docs/adr/`.
2. The `## Recommendation (proposed, not accepted)` section heading
   updated to `(ACCEPTED 2026-07-25 — see header)`; "Recommended"
   changed to "Adopted" in the recommendation line itself; the closing
   "This recommendation is not an acceptance" sentence replaced with a
   statement that it was accepted, pointing to this record.
3. No other line of `PROP-0001-discovery-lab-boundaries.md` was
   touched — not the three variant definitions, not the evidence
   basis, not the self-critique, not the Adversarial Review record, not
   the Unresolved Questions. This is a status-field-level change, the
   same discipline `EXEC-001`'s `KO-S3-01.md` promotion used (exactly
   the fields the decision concerns, nothing else).

## What this closes

`ARCH-001`'s `R1` ("Frozen implementation on an unratified mandate") —
the ecosystem's own top-ranked architectural risk, reconfirmed
unresolved through `ARCH-002` (`G5`), `ARCH-003`, `EXEC-001`, and `G2`
without ever being re-litigated — is closed by this decision. `AG-002`
and `AG-003`'s `FROZEN v1.0` status is now grounded in an accepted
mandate rather than resting on a `DRAFT` one, per
`6-CONSEQUENCES-ACCEPT.md`'s own advance description of exactly this
outcome.

## What this does not do, and what remains for a separate decision

Per `6-CONSEQUENCES-ACCEPT.md`, accepting the mandate does not by
itself: run `Ecosystem Health Review v0.1` (specified, authorized as of
this decision, but not executed — running it is a separate action,
not undertaken here without being asked); add `discovery-lab` as a row
in `project-memory/PROJECT_REGISTRY.md` (now decidable, per
`PROP-0001`'s own deferral rule, but that edit belongs to
`project-memory`'s own process, not this record); create an
independent reviewer role for Discovery Lab's own investigation
reports (still an open, named gap — `8-OPEN-QUESTIONS.md` item 1);
or resolve `G2`'s Unified Control Plane Specification's own separate
adoption question. Each is named as unblocked, not as done.
