# Deliverable 7 — Risk Assessment

Per `ARCH-003`. Ranked by likelihood × consequence, given this
specific pilot, not the ecosystem in general.

## Risk 1 — Reviewer independence cannot be genuinely satisfied (highest)

`REVIEW-PROTOCOL.md` requires the Knowledge Reviewer to be someone
other than `CPP-S3-01`'s producer. `CPP-S3-01` was produced by `AG-003`
acting inside this same session's earlier work (the Reality Stress
Test). If this pilot is ever run by continuing the same session or
persona, no genuinely independent Reviewer is available without
deliberately involving a different session, model instance, or a
human. This is not hypothetical caution — it is the same self-review
limitation `ARCH-001` (`R4`) and `ARCH-002` already named in the
abstract, now concretely blocking one specific, named step of one
specific pilot. **Likelihood: high if run carelessly. Consequence:
high** — a review conducted without real independence would produce a
Knowledge Review that looks complete (all six questions answered) while
failing the one condition that makes it a check at all.

**Mitigation, stated in the specification, not invented here**: the
pilot must not be executed by the same session/persona that produced
`CPP-S3-01`, and the Knowledge Review must record, per its own
Procedure step 2, an honest statement of who performed the review and
why they are independent.

## Risk 2 — The Human Decision step gets simulated rather than real

Because this task and its predecessors have operated with a human
present only at the level of issuing task instructions, not at the
level of individual approvals, there is a real risk that a future
execution of this pilot treats "the user gave the original ARCH-003
instruction" as equivalent to "a human approved this specific
promotion" — it is not. `REVIEW-PROTOCOL.md` and `PROMOTION-RULES.md`
both require a decision on the *specific proposal*, not a standing
delegation. **Likelihood: moderate. Consequence: high** — this is the
single mechanism (Human Final Authority) every ratified document in
`ARCH-002`'s model treats as non-negotiable; simulating it would
invalidate the pilot's entire evidentiary value.

## Risk 3 — `PROP-0001` dependency (carried forward, not re-litigated)

`ARCH-001` (`R1`) and `ARCH-002` (`G5`) both already flag that
`discovery-lab`'s ratified mechanisms sit on top of `PROP-0001`, still
`DRAFT`. This pilot inherits that same provisional standing — a
promotion executed under this specification would itself be
provisional until `PROP-0001` is resolved. **Likelihood: certain
(already true). Consequence: low for this pilot specifically** — the
pilot's own value (evidence about whether the coordination model can
govern execution) does not depend on `PROP-0001`'s resolution, only the
long-term standing of `KO-S3-01`'s resulting status does.

## Risk 4 — Creating `memory/knowledge-objects/` sets an unreviewed precedent for its internal layout

This will be the first real file in a location `KNOWLEDGE-OBJECT-SPEC.md`
names but has never been instantiated. A single file, created under
pressure to "just get the pilot done," could silently set conventions
(naming, directory depth, file granularity) that later real objects
would then have to match without those conventions ever having been
separately reviewed. **Likelihood: moderate. Consequence: moderate** —
contained by the fact that `KNOWLEDGE-OBJECT-SPEC.md` already specifies
the exact path and one-file-per-object convention, leaving little room
for the pilot to improvise beyond what is already written.

## Risk 5 — N = 1 generalization risk

A single successful pilot on a single, unusually clean promotion
proposal is weak evidence that the model handles harder cases (merges,
contested relationship types, higher promotion thresholds, or actions
in `kod`/`trust-engine`/`project-memory`). **Likelihood: certain
(inherent to any N=1 pilot). Consequence: low, if the result is
reported honestly as narrow** — this is exactly why
`2-SELECTED-EXECUTION-PILOT.md` scoped the pilot this narrowly and why
`8-GO-NO-GO-RECOMMENDATION.md` frames its conclusion accordingly.

## Risk not present, checked directly

**Risk of the pilot corrupting or overwriting existing data**: not
present. Per `3-EXECUTION-SPECIFICATION.md`, every artifact the pilot
can produce is a new file; no existing ratified document is ever
opened for editing. This was verified against `REVIEW-PROTOCOL.md`'s
own explicit boundary clause, not assumed.
