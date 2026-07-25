# Deliverable 6 — Consequences of ACCEPT

Assumes the recommended reading: accepting `PROP-0001` means adopting
**Variant B — Ecosystem Observatory, alone**, since that is the only
variant the document itself recommends. If a human instead accepts a
different variant (A or C), most of the consequences below would
differ — flagged where that matters.

## Immediate, mechanical consequences

- `discovery-lab`'s mandate moves from `DRAFT PROPOSAL` to an accepted
  governing document — the exact pattern already used for `ADR-0001`–
  `ADR-0004` and `GOVERNANCE.md`, per this package's Deliverable 1.
- `Ecosystem Health Review v0.1` becomes authorized to run, exactly as
  specified (5 fixed repositories, `C1`–`C3` criteria, frozen verdict
  rubric) — no further design work needed first.
- The deferred `project-memory/PROJECT_REGISTRY.md` question
  (Deliverable 5) becomes decidable rather than blocked — `PROP-0001`'s
  own text ties that specifically to the mandate no longer being
  `DRAFT`.
- `discovery-lab` becomes formally bound to Variant B's prohibitions:
  no code, no prototypes, no Hypothesis/discovery-method/trust-score
  artifacts, every finding proposal-only. This is a real narrowing, not
  a formality — it forecloses Variant A/C's capabilities unless a
  future, separate decision revisits the variant choice.

## Consequences for existing work

- `AG-002` and `AG-003`'s `FROZEN v1.0` status becomes retroactively
  grounded in an accepted mandate rather than resting on a `DRAFT` one
  — directly closing `ARCH-001`'s `R1`, the ecosystem's own top-ranked
  risk, without further architectural work.
- `EXEC-001`'s executed pilot (`memory/knowledge-objects/KO-S3-01.md`)
  and its underlying `CPP-S3-01`/`KR-0001` chain move from
  "provisional, standing on a `DRAFT` mandate" (as `6-FINAL-VERDICT.md`
  and `STATE.md` currently record it) to settled.
- `G2`'s Unified Control Plane Specification's own open item — that
  `discovery-lab`'s canonical instances are downstream of `PROP-0001` —
  is resolved for the `discovery-lab` side specifically (the
  `kod`/`project-memory` side of that reconciliation is unaffected
  either way).

## What remains open even after ACCEPT

Accepting does not resolve `PROP-0001`'s own named unresolved
questions (Deliverable 4) — no independent reviewer role is created by
ratification alone; whether receiving repositories will act on routed
proposals stays untested until `Ecosystem Health Review v0.1`
actually runs and produces a routed finding; the self-review weakness
that applies to this very ratification process is not addressed by
the ratification itself. Accepting starts the clock on testing these,
it does not answer them in advance.

## If a variant other than B is accepted instead

Accepting **Variant A** would authorize bounded technical prototyping
against already-specified-but-unbuilt architecture (the document's own
example: trust-engine's Mechanism/Meta Trust Layer) — but the document
itself argues against this now, since "no repository has requested
prototyping help" and the one candidate need is inferred, not
evidenced. Accepting **Variant C** would authorize both A and B
together at HIGH governance burden, which the document argues is
premature until B alone has run and shown the feedback loop is
valuable. Neither A nor C changes the `AG-002`/`AG-003` consequence
above, since that consequence follows from ratifying *any* mandate,
not specifically from Variant B's content.
