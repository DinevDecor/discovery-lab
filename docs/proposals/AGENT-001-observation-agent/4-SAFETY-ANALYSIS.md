# Deliverable 4 — Safety Analysis

## Why it is read-only

The agent's Contract (once written, per `GOVERNANCE.md`'s Draft stage —
not written by this proposal) would grant no write, edit, commit, or
push authority of any kind, mirroring `AG-001/CONTRACT.md`'s own Scope
of authority clause verbatim in spirit: *"Read-only observation of
explicitly authorized repositories only... No authority beyond
observation is granted by this contract, regardless of what an
Executor might otherwise be capable of."* This is not a promise the
agent keeps voluntarily — it is a boundary defined by what the contract
authorizes at all, the same mechanism that has held for `AG-001`,
`AG-002`, and `AG-003` across every real run performed in this session,
with `AG-003`'s own `STATUS.yaml` recording `boundary_violations: 0`.

## Why it cannot drift governance

Its only output is a Report, optionally containing Recommended
Actions. Per the Observation Loop, a Recommended Action must pass a
Formal Gate before it is even eligible for Human Final Authority — and
even then, per `PROP-0001`'s Principle 0, *"Discovery Lab itself never
accepts, finalizes, or applies any of these proposals."* The agent has
no path from "I observed X" to "governance now reflects X" that does
not pass through both an independent check and a human decision. This
is the same two-gate structure `G2` found independently ratified three
times across three repositories — the agent adds no shortcut around it.

## Why it cannot self-improve

Its own Contract, `PROMPT.md`, and observation criteria are themselves
governed artifacts under `GOVERNANCE.md` — changing what the agent is
authorized to check, or how, is a Contract change, which (per
`GOVERNANCE.md`'s Major Revision rule) requires the full lifecycle
again, starting at Draft, decided by a human. The agent cannot revise
its own scope any more than `AG-001` or `AG-003` can revise theirs —
`PROP-0001`'s own discipline for `Ecosystem Health Review v0.1`
("Fixed review criteria... frozen before running... not changed after
evidence is seen") is the same principle applied to a single review;
here it applies to the agent's Contract itself.

## Why it cannot become an execution agent

There is no execution capability to "become" — none is granted, and
none exists anywhere in this ecosystem's ratified architecture to grant
(`ARCH-002`'s `G1`, unchanged). Even in the one real case where this
session executed something (`EXEC-001`), execution required a human
decision at the point of writing a file, performed by a session
distinct from this proposed agent's own scope. Nothing in this design
adds, or could add by its own action, a write permission it does not
already have.

## Why Human Final Authority remains intact

The Observation Loop's own last step is `Human`, with no step after it
— stated as an explicit architectural property in
`2-OBSERVATION-LOOP.md`, not merely a rule to be followed. Every real
precedent in this ecosystem (`EXEC-001`'s `KO-S3-01` promotion,
`PROP-0001`'s own ratification) shows this boundary holding under
actual use, not only in specification.

## What this analysis does not claim

It does not claim the agent is risk-free — `8-RISK-ASSESSMENT.md`
names real, non-safety risks (noise, duplication with `AG-001`/`AG-003`,
the self-review problem applying to its own Formal Gate step). "Cannot
damage the ecosystem" is a narrower, specifically safety-scoped claim:
no write path exists, no autonomous-decision path exists, and no
self-modification path exists — three separate, checkable properties,
not one vague assurance.
