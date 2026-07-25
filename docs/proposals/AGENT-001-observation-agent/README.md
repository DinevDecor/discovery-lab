# AGENT-001 — Observation Agent

Status: **PROPOSAL.** No implementation — no `CONTRACT.md`, `ROLE.md`,
or any other document from `GOVERNANCE.md`'s Draft-stage set is created
by this task. This is the "Idea" stage of Discovery Lab's own mandatory
lifecycle (`Idea → Draft → Internal Review → Adversarial Review →
Reality Stress Test → Freeze Recommendation → FROZEN`) — a proposal
that a Role should exist, with an architecture sketch, not the Role
itself.

## What this proposal is, precisely

**Not a new concept.** `docs/ai-organization/employees/
AG-001-repository-observer/` already exists — same Core Principle
("Observe changes. Report evidence. Do not decide."), same read-only
discipline, same evidence-citation and escalation rules. Its own
`RUN-PROTOCOL.md` states plainly: *"nothing here is meant to run
unattended or be triggered on a schedule."* This proposal does not
invent a competing Observation Agent — it proposes extending AG-001's
already-proven observation discipline with the one capability it
explicitly lacks (a `Recommended Action` step, already specified but
never built in `PROP-0001`'s own Variant B information-flow map), as a
**new candidate Role** rather than a revision to AG-001 itself, because
adding "Generate Recommendations" to AG-001's `Responsibilities` would
be a Major Revision under `GOVERNANCE.md`'s own rule, and a new,
smaller Role is the more conservative change.

**A real, live finding surfaced while checking this.** `AG-001`'s own
`STATUS.yaml` states `runs_completed: 0`, `last_run: null` — but
`HISTORY.md` and `runs/RUN-0001-observation-report.md` show a real run
was executed on 2026-07-24. This is a genuine `C1`-style mismatch
inside `discovery-lab` itself, missed by `DL-001`'s own self-check
(which checked `STATE.md`, `CHANGELOG.md`, and `EMPLOYEE-REGISTRY.md`,
not AG-001's own sub-registry). Reported here rather than silently
corrected — this task's own Forbidden Actions include "change status,"
and fixing it is exactly the kind of write action this proposal is
designed to prove an Observation Agent should never perform itself.

## Deliverables

1. `1-OBSERVATION-AGENT-ARCHITECTURE.md`
2. `2-OBSERVATION-LOOP.md`
3. `3-EVENT-CLASSIFICATION.md`
4. `4-SAFETY-ANALYSIS.md`
5. `5-REPORTING-SPECIFICATION.md`
6. `6-PILOT-SPECIFICATION.md`
7. `7-SUCCESS-METRICS.md`
8. `8-RISK-ASSESSMENT.md`
9. `9-FINAL-VERDICT.md` — **READY FOR OBSERVATION PILOT**, scoped
   explicitly to human-invoked runs — `DL-002` already found no
   ratified trigger/scheduling mechanism exists anywhere in this
   ecosystem; this proposal does not solve that gap, and the
   recommended pilot does not require it to be solved first.

## Compatibility, stated explicitly

Built entirely from already-ratified or already-specified material:
`AG-001`'s observation discipline (Prototype, real-run-tested once);
`PROP-0001` Variant B's own information-flow map (`ACCEPTED`); `G2`'s
Unified Control Plane Specification's three mechanisms (Contract-Defined
Roles, Formal Gate, Human Final Authority). No new governance model, no
new Gate type, no new Runtime, no execution capability anywhere in this
design.
