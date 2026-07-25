# Deliverable 1 — Observation Agent Architecture

## Identity

**Proposed name**: Ecosystem Observation Agent.
**Proposed Employee ID**: `AG-004` (next available, per
`docs/ai-organization/EMPLOYEE-REGISTRY.md` — 3 Roles currently
recorded). Proposed, not claimed — assigning the ID is itself a Draft-stage
act this proposal does not perform.
**Core Principle** (proposed, directly extending AG-001's own): *"Observe
changes. Report evidence. Recommend, never decide."* — one clause added
to AG-001's exact wording, marking the one new capability.

## What this Role is built from — cited, not duplicated

| Component | Source | Status |
|---|---|---|
| Observation discipline (evidence citation, escalation to `UNKNOWN`/`INSUFFICIENT ACCESS`, never resolving ambiguity by inference) | `AG-001-repository-observer/RUN-PROTOCOL.md`, `LIMITATIONS.md` | `Prototype`, real-run-tested (`RUN-0001`) |
| Cross-repository, multi-criterion investigation shape (`C1`/`C2`/`C3`, fixed-before-running criteria, per-repository verdicts, no aggregate) | `PROP-0001` Variant B, `Ecosystem Health Review v0.1` | `ACCEPTED` |
| The `Recommended Action` step | `PROP-0001`'s own information-flow map: `Decision → Graduation, rejection, or deletion (a PROPOSAL is drafted...)` | `ACCEPTED`, specified, never yet built as a working mechanism |
| Contract-Defined Role structure | `G2/1-UNIFIED-CONTROL-PLANE-SPECIFICATION.md` §2 | `DRAFT — Candidate for Adoption` (`G2`'s own status) |
| Formal Gate before any recommendation reaches a human as a proposal | `G2` §3; concretely, `AG-003/REVIEW-PROTOCOL.md`'s Knowledge Review as the nearest working instance | `FROZEN` (`AG-003`), exercised for real (`KR-0001`) |
| Human Final Authority as the loop's terminus | `G2` §4; `PROP-0001` Principle 0 | Ratified across three repositories independently |

Nothing in this table is new. The architecture is an assembly of
already-existing, already-ratified or already-exercised pieces.

## Position in `Unified Coordination Model v1.0`

The agent is a **Contract-Defined Role**, exactly like `AG-001`,
`AG-002`, `AG-003`. Its output (a Report, optionally containing
Recommended Actions) is not self-executing and not self-authorizing —
per the Observation Loop (`2-OBSERVATION-LOOP.md`), a Recommended
Action must pass a **Formal Gate** before it is even eligible for
**Human Final Authority** to act on. No fourth mechanism is introduced;
the agent occupies the same three-mechanism structure every other real
governance pattern in this ecosystem already uses.

## What the agent is not

Not a Runtime (`ARCH-002`'s `G1` gap is untouched by this design — the
agent never carries out anything, including its own recommendations).
Not a Dispatcher (it does not route work to other Roles or decide what
happens next — it only reports and, at most, proposes). Not a
Coordination Agent (`DL-002`'s Part D explicitly excluded this class as
unjustified by any real candidate; this design does not revisit that).
Not an extension of `AG-002` or `AG-003` (`AG-002` recovers ideas from
historical sources; `AG-003` curates recovered findings into Knowledge
Objects; this agent observes the ecosystem's *current, live* state —
distinct subject matter, no overlap in scope).

## Boundary against `AG-001` specifically

`AG-001`'s own `RUN-PROTOCOL.md` format has no `Recommendations` or
`Conclusions` section by design ("because neither exists in this
format"). This proposal does not ask `AG-001` to grow one — it proposes
a separate, smaller Role that reuses `AG-001`'s evidence discipline as
an input method, while adding the one new step `AG-001`'s own design
deliberately excludes. If this proposal is ever accepted, `AG-001`
itself is unmodified; the new Role would sit alongside it, not replace
or absorb it.
