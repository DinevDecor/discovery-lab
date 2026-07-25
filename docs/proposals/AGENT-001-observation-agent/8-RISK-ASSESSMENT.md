# Deliverable 8 — Risk Assessment

## R1 — Self-review recurring again, in a new place

The pilot's own Formal Gate step (`6-PILOT-SPECIFICATION.md` step 4)
reuses `EXEC-001`'s memoryless-but-orchestrated Agent instance pattern
— real independence at the letter of `REVIEW-PROTOCOL.md`'s rule, not
at the level of a genuinely separate actor. This is the same
limitation named in `EXEC-001`, `ARCH-001`'s `R4`, and `DL-002` —
recurring here because this design reuses the same mechanism, not
because it introduces a new instance of the problem.

## R2 — Duplication risk against `AG-001` and `AG-003`

`AG-001` already does evidence-cited observation; `AG-003` already
produces proposals from recovered evidence. This new Role sits between
them — real duplication risk if its boundary is not held precisely.
Mitigated in `1-OBSERVATION-AGENT-ARCHITECTURE.md`'s explicit boundary
statements, but boundaries stated in a proposal are not the same as
boundaries proven under real, repeated use — `PROP-0001`'s own
Adversarial Review found exactly this kind of risk for Variant B
against KOD's Research Guardian, and it is named here for the same
reason: to be checked, not assumed safe.

## R3 — Recommendation noise growing unmanaged over time

`5-REPORTING-SPECIFICATION.md`'s "Repeated Findings" field is explicit
about not auto-closing anything, which is correct for honesty but
creates a real risk: a report that only ever grows, never shrinks,
becomes exactly the kind of artifact `PROP-0001`'s own Variant B
"principal failure mode" describes — *"becomes a passive audit archive
nobody acts on."* Not solved by this design; named as a live,
inherited risk.

## R4 — The Employee ID and Role-creation question is not this proposal's to answer

Assigning `AG-004`, or any ID, and actually writing `CONTRACT.md`/
`ROLE.md`/etc., are Draft-stage acts under `GOVERNANCE.md`'s own
lifecycle — this proposal is the "Idea" stage only. If accepted, the
next step is a separate, human-authorized Draft task, not an automatic
continuation of this one.

## R5 — The `AG-001` `STATUS.yaml` finding, itself

Cited throughout this proposal as evidence, this is also a small, real,
live governance gap: a Role's own bookkeeping is inconsistent with its
own history, undetected until this proposal's own preparatory checking
found it. Low severity (a bug-fix-tier correction, per
`GOVERNANCE.md`'s own taxonomy — no version bump, no lifecycle
re-entry needed), but it is exactly the class of finding this whole
proposal exists to catch systematically rather than by incidental
discovery during unrelated work.

## Risk not present, checked directly

**Risk of this proposal itself creating scope creep by touching
repositories outside `discovery-lab`.** Not present — every file
created by this task is under `docs/proposals/AGENT-001-observation-
agent/`; `git status` on `project-memory`, `kod`, `trust-engine`, and
`generative-discovery-engine` shows zero changes from this task.
