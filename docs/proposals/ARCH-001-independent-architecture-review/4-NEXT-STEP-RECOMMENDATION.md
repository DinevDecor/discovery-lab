# Deliverable — Next-Step Recommendation

Six-month roadmap. Architecture, not features, per the task's explicit
instruction. Ordered — each step is a precondition for the next, not a
menu.

## Month 0–1: Ratify or reject `PROP-0001`

A human decision, not a build task. This is R1 from
`3-RISK-ASSESSMENT.md`, and it is first because every other
recommendation below either depends on `discovery-lab`'s authority
being settled or is a governance change that should happen under a
ratified mandate rather than a draft one. Output: `PROP-0001` moves to
`Accepted` (with `AG-002`/`AG-003`'s existing freezes now validly
grounded) or to `Rejected`/`Revised` (with the freezes explicitly
relabeled provisional pending re-validation). Either outcome is
progress; leaving it `DRAFT` indefinitely is the one outcome this
roadmap argues against.

## Month 1–3: Reconcile the three coordination designs into one adopted Control Plane spec

Per `1-ALTERNATIVE-ARCHITECTURE.md` item 1. Concretely: take
`project-memory/archive/AI-Collaboration-Architecture-v1_1.md` from
`Candidate for Adoption` to `Adopted`, amended to explicitly fold in
`kod/ADR-0009`'s Authority/Writer Matrices and
`discovery-lab/GOVERNANCE.md`'s lifecycle and ORB as named domain
instantiations of its invariants. This is editorial/architectural
reconciliation work, doable without new infrastructure. Add the
Foundation Ledger gate (`1-ALTERNATIVE-ARCHITECTURE.md` item 2) as part
of this same amendment, since it is a rule change to the same document.
Output: one Control Plane document, one owner, referenced (not
reinvented) by `kod` and `discovery-lab`.

## Month 3–5: Build exactly one real, narrow execution path

Per `1-ALTERNATIVE-ARCHITECTURE.md` item 3. Select one already-real,
already-human-approvable action category — an `AG-003` Knowledge Merge
Proposal is the best-understood candidate, since three real curation
passes already exist as source material — and build the smallest
mechanism that executes an approved instance of it without manual
file editing. Explicitly not a general runtime, not an event bus, not
infrastructure for other action types yet. The purpose of this step is
evidence generation: it will surface what "execution" actually
requires in this ecosystem, which nothing built so far can answer
because nothing built so far executes anything.

## Month 5–6: Evidence-based revisit of the autonomy question

Only after Month 3–5 produces real execution data. Re-ask this
review's own Q3 with that data in hand, rather than governance
documents alone. Do not pre-commit to an outcome — this step could
legitimately still conclude autonomy should not increase yet; the
point is that the decision would then be grounded in how the one real
execution path actually behaved, not in projection.

## Explicitly deferred, not recommended for this six-month window

- **Designing `DLOS`, or any new coordination system**, per Q1/Q2 — the
  need is reconciliation, not invention.
- **A knowledge graph, distributed cognition, or planning layer** —
  presuppose the execution substrate Month 3–5 has not yet built.
- **Resolving `Dinev Assistant`'s existence** — remains
  `INSUFFICIENT ACCESS`; not blocking on any step above, but not worth
  spending this window's effort chasing given the higher-priority items
  already identified.
- **The still-open maturity re-scan loophole**
  (`releases/1.0/VALIDATION-HISTORY.md` item 16) and **first genuinely
  independent Knowledge/ORB Review** (R4) — real, but narrower in blast
  radius than R1/R2; worth scheduling, not worth displacing the four
  steps above.
