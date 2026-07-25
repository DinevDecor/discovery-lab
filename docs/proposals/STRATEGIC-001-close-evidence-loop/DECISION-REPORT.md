# STRATEGIC-001 — Decision Report

Discovery Lab, acting on its own ratified mandate (`PROP-0001`, Variant
B), deciding its own next step. Not requested by a numbered task —
self-directed, per this request's own Mission.

## The decision

**Close the evidence-and-accountability loop `PROP-0001` already
specified but never built**: file `DL-001`'s real findings as a proper,
durable investigation report (`docs/investigations/`, the "owned
artifact" type Variant B's own text names), and build and populate the
**Recommendation Ledger** — an interface `PROP-0001` fully specified in
its own text and explicitly deferred, on the condition that a real
recommendation would exist to seed it before it was needed. One now
does.

Executed in full below, within Discovery Lab's own authority. The
recommendations themselves remain `PROPOSED` — routing them to
`project-memory`'s and `kod`'s own maintainers for an actual accept/
reject decision is outside Discovery Lab's authority (Principle 0) and
is the one part of this initiative that requires a human to carry
forward.

## The bottleneck

Not a missing capability — a missing *memory*. `DL-001` ran, found five
real, citable discrepancies, and delivered them as a chat report only
(per that task's own "do not modify repositories" constraint). Nothing
about that constraint made the findings less real; it made them
**undurable**. If this conversation is lost or compacted without this
step, `kod`'s real-but-unreflected implementation code, `project-memory`'s
two stale artifacts, and every other `DL-001` finding disappear —
discoverable again only by re-running the entire review from scratch.
`AGENT-001`'s own design depends on exactly the durability this
bottleneck denies: its "Repeated Findings" mechanism (`5-REPORTING-
SPECIFICATION.md`) requires a prior run's report to exist and be
checkable — today, none does, anywhere, for any Discovery Lab review
ever performed.

## The largest remaining architectural risk

Not `G1` (no execution layer — well documented, not urgent given
nothing autonomous exists to need it yet). Not the independent-reviewer
gap (real, but already honestly disclosed everywhere it applies, a
managed risk, not a silent one). The largest *unmanaged* risk is this:
**`PROP-0001`'s own stated invalidation conditions for its Variant B
mandate cannot currently be checked, at all.** Its own text: *"If,
when a finding is drafted as a hypothetical proposal, there is no
realistic mechanism or willingness for the destination repository to
ever act on it, that would suggest Variant B's core value proposition...
does not hold, and the mandate needs rethinking."* Without a
Recommendation Ledger recording what was proposed and what happened to
it, this is not a hard question — it is an **unanswerable** one. The
mandate that was just ratified (`PROP-0001`, this session's own
highest-priority closed item) has no mechanism to ever demonstrate it
was the right call, or to catch it if it wasn't.

## The smallest action with the largest capability increase

Two files. `PROP-0001` already fully specifies both — an investigation
report format (used seven times before, by `AG-002`; new here only in
that Variant B's own report format, per `Ecosystem Health Review v0.1`'s
own output schema, has never been filed) and the Recommendation
Ledger's exact five-field schema, quoted verbatim in `PROP-0001` itself.
No new format is designed here. No new governance concept is
introduced. The capability increase is disproportionate to the size of
the change: Discovery Lab moves from "produces reports that vanish" to
"has a persistent, queryable, append-only record of what it has found
and what became of it" — the precondition for `AGENT-001`'s own
Repeated-Findings mechanism, for ever computing `PROP-0001`'s own
`acceptance_rate` metric, and for the mandate's own stated success
conditions to ever be checkable.

## Why this before every alternative

- **Before the `AGENT-001` Observation Pilot**: running the pilot before
  a Ledger exists means its own findings would repeat `DL-001`'s
  mistake — real, then lost. Building the Ledger first means the pilot,
  when it runs, has somewhere real to land.
- **Before a trigger/scheduling mechanism** (`DL-002`'s named gap): a
  trigger is valuable only for something worth running repeatedly with
  cumulative value. A Ledger is what makes repetition valuable
  (comparing today's findings to a real record of yesterday's) rather
  than noise. It is also a materially bigger undertaking — new
  infrastructure, likely its own dedicated design proposal like
  `AGENT-001` — and does not fit "smallest action."
- **Before an Independent Reviewer role**: that gap is a human/
  organizational decision (who counts as independent), not something
  buildable by this session alone, and it is already honestly disclosed
  everywhere it applies — a known, managed risk, not a silent one like
  the Ledger's absence.
- **Before other registry improvements**: smaller in scope and
  consequence than closing the accountability loop; the one concrete,
  already-recommended registry-adjacent fix found in this session
  (`AG-001/STATUS.yaml`'s stale run-count) is executed alongside this
  initiative, not instead of it — see `EXECUTION-LOG.md`.

## Constraints honored

No new governance model — the Ledger's schema, statuses, and
`acceptance_rate` naming caveat are `PROP-0001`'s own words, reused
verbatim. Human Final Authority not bypassed — every Ledger entry is
filed `PROPOSED`, none `ACCEPTED`; nothing is written to
`project-memory` or `kod` themselves, per Principle 0. No architecture
changed beyond what the already-accepted process explicitly allows
(`GOVERNANCE.md`'s own bug-fix-tier rule, applied once, in
`EXECUTION-LOG.md`). No new abstraction — both files use exactly the
structures `PROP-0001` already specifies.

See `EXECUTION-LOG.md` for what was actually done, and
`FINAL-VERDICT.md` for the closing verdict.
