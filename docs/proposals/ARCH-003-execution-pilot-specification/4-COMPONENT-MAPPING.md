# Deliverable 4 — Component Mapping

Per `ARCH-003` Phase 4. Every step of `3-EXECUTION-SPECIFICATION.md`
mapped to `Unified Coordination Model v1.0`
(`ARCH-002/4-UNIFIED-COORDINATION-MODEL.md`). Only the three required
principles are used — no other component from that model, and nothing
outside it.

| Pilot step | Unified Coordination Model component | Ratifying source |
|---|---|---|
| `AG-003` produced `KO-S3-01` and `CPP-S3-01` (already done, prior to this pilot) | **Contract-Defined Roles** — `AG-003` acts under a versioned contract, not as a fixed model | `docs/ai-organization/employees/AG-003-knowledge-curator/CONTRACT.md`, `Status: FROZEN` |
| Reviewer independence requirement | **Formal Gate** — the gate's own definition requires the checking actor to be distinct from the proposal's author | `REVIEW-PROTOCOL.md` §"Who may conduct a review," `FROZEN` |
| Six mandatory questions, each verdicted `SOUND`/`UNSOUND`/`INSUFFICIENT EVIDENCE` | **Formal Gate** — a check against fixed criteria producing a small enumerated verdict, never itself the final authority | `REVIEW-PROTOCOL.md` §"The six mandatory questions," `FROZEN` |
| Review filed as a recommendation, not a decision | **Formal Gate** boundary — "nothing is final until a human acts on it" | `REVIEW-PROTOCOL.md` §7 |
| Human Decision record (`Accept`/`Reject`/`Defer`) | **Human Final Authority** | `REVIEW-PROTOCOL.md` §7; `PROMOTION-RULES.md` §"What 'promotion is never automatic' means concretely" |
| Only one field (`status`) changes; no other artifact touched | **Formal Gate** boundary, carried into execution | `REVIEW-PROTOCOL.md` §"Boundaries this procedure must never cross" |
| The write itself (creating `KO-S3-01.md`) | **Not mapped to any component** — deliberately | See note below |

## The deliberate gap in the last row

Every other step in this pilot maps cleanly onto one of the three
required principles. The physical write does not, and this is not an
oversight — it is the pilot's actual finding, made visible by the
mapping exercise itself rather than argued separately. `Unified
Coordination Model v1.0` ratifies who may propose (Contract-Defined
Roles), who may check (Formal Gate), and who may decide (Human Final
Authority) — it does not ratify who, or what, carries out a decision
once made. `ARCH-002`'s `G1` named this gap in the abstract; this
mapping shows exactly where it sits inside one concrete pilot: between
"Human Decision: `Accept`" and a file existing on disk.

## Why this is not a violation of "no new components"

The specification in `3-EXECUTION-SPECIFICATION.md` does not invent a
component to fill this gap — it explicitly declines to. No Runtime, no
Dispatcher, no execution Role is named for the write step; it is
specified only as "the Executor who performs this write," undefined
beyond that, precisely because inventing a name for it would be
inventing a fourth component this task's Critical Rules forbid. The
pilot is designed to surface `G1` at its smallest possible scale, not
to quietly solve it.
