# ARCH-003 — Execution Pilot Specification

Status: **Architecture Implementation Preparation**, completed. Builds
exclusively on `ARCH-001` and `ARCH-002` — no new architecture, no new
concepts, `Unified Coordination Model v1.0`
(`../ARCH-002-unified-coordination-model/4-UNIFIED-COORDINATION-MODEL.md`)
accepted as the current working foundation, exactly as instructed.

## What this task is

A **specification**, not an execution. Per the request's own
Definition of Done, this task produces a specification for one real
pilot that *can* be executed without introducing new architectural
concepts — it does not run that pilot. No file outside this proposal
directory and (for reference-checking purposes only) the sources it
cites has been modified.

## Constraint compliance, stated explicitly

- Sourced only from `ARCH-001`, `ARCH-002`, `Unified Coordination
  Model v1.0`, documents with `ACCEPTED`/`FROZEN` status, or concepts
  independently repeated across repositories — no `DRAFT` document is
  used as an architectural foundation anywhere in this task. Where a
  `DRAFT` fact is mentioned (`PROP-0001`), it is cited only as a
  carried-over risk, never as a basis for the pilot's design.
- Uses exactly the three required principles — Contract-Defined Roles,
  Formal Gate, Human Final Authority — and no other governance
  mechanism.
- Introduces no new component. The one genuine gap found (who/what
  physically performs the write) is reported as a finding
  (`4-COMPONENT-MAPPING.md`), not filled with an invented Runtime,
  Dispatcher, or Role.

## Deliverables

1. `1-CANDIDATE-PILOT-ANALYSIS.md` — five real candidates, all
   already-existing artifacts from `AG-003`'s real (non-demonstration)
   Reality Stress Test output.
2. `2-SELECTED-EXECUTION-PILOT.md` — **C1: promote `KO-S3-01` via the
   already-filed, real `CPP-S3-01`**, `Draft → Candidate Principle`.
3. `3-EXECUTION-SPECIFICATION.md` — Trigger, Inputs, Roles, Gates,
   Human approval, Execution, Outputs, Evidence, Success/Failure
   criteria, Rollback.
4. `4-COMPONENT-MAPPING.md` — every step mapped to the Unified Model;
   one deliberate, reported gap (the physical write, `ARCH-002` `G1`,
   at its smallest possible scale).
5. `5-EVIDENCE-COLLECTION-PLAN.md`.
6. `6-SUCCESS-METRICS.md` — nine binary/countable metrics.
7. `7-RISK-ASSESSMENT.md` — highest risk: Reviewer independence cannot
   be genuinely satisfied if run by the same session that produced the
   proposal under review.
8. `8-GO-NO-GO-RECOMMENDATION.md` — **GO**, conditional on genuine
   Reviewer independence and a real, dated Human Decision — not an
   unconditional yes.

## Headline finding

A real, narrow execution pilot can be fully specified today using only
already-ratified mechanisms, with zero new architecture. The one place
the specification cannot name a responsible component — who actually
performs the approved write — is not a defect in this task; it is
`ARCH-002`'s `G1` finding, made concrete at the smallest possible
scale rather than left abstract.
