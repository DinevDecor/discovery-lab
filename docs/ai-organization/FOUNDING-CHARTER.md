# AI Organization — Founding Charter (FP-0001, v0.1)

**Status: DRAFT.** Nothing in this document is final, accepted, or
binding. This charter does not create a new governance layer — every
principle below either restates something already established in
`ORGANIZATION-DRAFT.md`, `HIRING-LIFECYCLE-DRAFT.md`, or
`../proposals/PROP-0001-discovery-lab-boundaries.md`, or names a
candidate principle that has not yet been tested against real
organizational behavior.

## Why "Charter," not the word this document deliberately avoids

This document does not use the word KOD's own foundational document
uses for itself (`KOD/Core/CONSTITUTION.md`), and it is not named that
way here on purpose. That word implies something accepted and binding
— the highest authority its own system answers to. Nothing here has
earned that status. If real operation over time shows that a principle
below is wrong, it must be revisable through the same disciplined
process this document itself describes in Section 4 — not exempted from
it because it happens to be foundational. Calling this a "Charter"
rather than that other word is itself a small, deliberate statement:
foundational does not mean proven, and being written down first does
not mean being right.

---

## 1. Purpose

**Candidate principle:** The organization exists to improve the quality
of decisions through verifiable processes — not to increase the
quantity of AI agents or documents.

This is stated here as a design intent for AI Organization specifically
— what it is built to do — not as a claim that this intent has been
proven, and not as a restatement of `docs/investigations/
DL-0001-ecosystem-purpose-shift.md`'s broader, still-unverified
hypothesis about the wider DinevDecor ecosystem. The two are related in
spirit but distinct in status: DL-0001 is a candidate observation about
systems that already exist; this is a stated intent for a system still
being designed. Neither one's fate settles the other's.

## 2. Identity

**Candidate principle:** The organization is independent of any
specific AI model. Roles are permanent. Executors are replaceable.

This restates, without changing it, the core principle already stated
in `ORGANIZATION-DRAFT.md`: "Role is stable. Executor is replaceable."
Nothing new is introduced here.

## 3. Evidence

**Candidate principle:** No organizational rule is accepted without
evidence.

This is stated as a candidate standard the organization aspires to, not
as a description of how its rules have been produced so far — see
Candidate Conflict 3 below.

## 4. Evolution

**Candidate principle:** The organization changes through a fixed
sequence, never through direct edit:

```
Observation
   ↓
Investigation
   ↓
Experiment
   ↓
Review
   ↓
Decision
   ↓
Adoption
```

No principle in this charter, and no rule in any governance document
under `docs/ai-organization/`, is meant to be changed by editing it
directly. A change is expected to start as an Observation, become a
named Investigation (in the sense already used under
`docs/investigations/`), proceed through Experiment and Review, reach a
Decision, and only then be Adopted — mirroring the discipline
`../proposals/PROP-0001-discovery-lab-boundaries.md` already applies to
its own recommendation. This document does not further define any of
these six stages beyond naming them; several already have partial
definitions elsewhere in this repository, and several do not.

## 5. Boundaries

**Candidate principle:** Every employee has a bounded scope. Every
employee has the right to say `UNKNOWN` or `INSUFFICIENT ACCESS`.

This restates, without changing it, the pattern already established in
AG-001's own `LIMITATIONS.md` and `CONTRACT.md` (both under
`employees/AG-001-repository-observer/`) — this charter proposes it as
a general expectation for any future Role, not only AG-001.

## 6. Independence

**Candidate principle:** Where an independent verification method
exists, a single source is not enough.

This principle is grounded in something that already happened: during
AG-001's `RUN-0001`, a first check (`git branch -a`) produced an
incomplete result, and the finding was only trusted after being
cross-verified through two independent methods (`git ls-remote` and the
GitHub API). See Candidate Conflict 4 below for where this principle,
read strictly, goes further than `RUN-0001` itself actually did.

## 7. Memory

**Candidate principle:** The organization preserves its history. It
does not rewrite it.

This restates, without changing it, the append-only convention already
used throughout this repository — `EMPLOYEE-REGISTRY.md`,
`ORB/ORB-REGISTRY.md`, every Role's `HISTORY.md`, and
`docs/investigations/`'s own SUPERSEDED-not-deleted convention.

## 8. Promotion

**Candidate principle:** Trust is not declared. It is earned through
repeatedly verifiable behavior.

This restates, without changing it, `HIRING-LIFECYCLE-DRAFT.md`'s
existing lifecycle (`Candidate → Prototype → Probation → Trusted →
Retired`), which already requires real runs, independent review, and a
recorded human decision before any Role reaches `Trusted`. See
Candidate Conflict 6 below on this section's use of the word "Trust."

## 9. Human Authority

**Candidate principle:** Only a human can:

- accept organizational changes;
- expand a Role's authority or scope;
- appoint a `Trusted` Role;
- change this Founding Charter.

This restates, without changing it, `HIRING-LIFECYCLE-DRAFT.md`'s
existing rule that Discovery Lab may design and run a review but "must
not, on its own, declare any Role `Trusted`," and Discovery Lab's own
Principle 0 ("Discovery Lab itself never accepts, finalizes, or applies
any of these proposals"). It also matches a pattern already independent
of Discovery Lab: both `generative-discovery-engine`'s `ADR-0001`
("AI models cannot independently accept scientific or architectural
decisions") and trust-engine's own rule ("human approval remains
required for trust mutations... even CRITICAL does not mean automatic
trust mutation") converge on the same human-only-finalization
principle, independently of this charter and independently of each
other.

## 10. Open Questions

This charter does not resolve, and does not attempt to resolve, the
following:

- **Who is "a human" for the purposes of Section 9?** No document under
  `docs/ai-organization/` names a specific person or role with this
  authority. `HIRING-LIFECYCLE-DRAFT.md` already carries this as an open
  governance question ("who holds the final authority to appoint a
  Role... is not decided by this document"); this charter does not
  close it either.
- **How is a change to this Founding Charter itself reviewed**, before
  the human decision required by Section 9? Section 4's Evolution
  pipeline names a `Review` stage, but this document does not say which
  of the (at least three, now arguably four — see Candidate Conflict 2)
  existing senses of "review" in this ecosystem would apply to a
  proposed charter amendment, or whether a new one would need to be
  defined.
- **What happens if DL-0001's broader hypothesis is later found
  false**, for some or all of the other four repositories it covers?
  Section 1 states this charter's Purpose does not depend on DL-0001's
  outcome — but whether that separation actually holds in practice, once
  DL-0001-EXP-1 (or an equivalent check) is actually run, is untested.
- **Does Section 3's evidence standard apply retroactively** to rules
  already adopted before this charter existed (the lifecycle stages,
  ORB's six questions, AG-001's metric names) — or only to rules
  proposed from this point forward? This document does not decide.
- **The long-term location of AI Organization** — inside `discovery-lab`,
  as its own repository, or elsewhere — remains undecided, as already
  recorded in `README.md` and every Role's `STATUS.yaml`.

These are recorded here deliberately, not hidden, and not resolved
before their time.

---

## Candidate Conflicts (Self-Critical Review)

Written after the charter above, as a separate pass, per the
instruction that any conflict found must be recorded here rather than
fixed directly in the sections above.

**1. Section titles collide with Discovery Lab's own reserved
terminology.** `../proposals/PROP-0001-discovery-lab-boundaries.md`'s
ground rule 1 states that Discovery Lab "never uses Observation,
Hypothesis, Evidence, Experiment, or Review as its own first-class
artifact type names without qualification," precisely because each of
those words is already a specifically-defined, load-bearing concept in
KOD, trust-engine, or generative-discovery-engine. This charter uses
four of those five words directly as section or pipeline-stage titles —
"Evidence" (Section 3), and "Observation," "Experiment," "Review" (all
three inside Section 4) — without the disambiguation notes that were
added for every earlier instance of this exact collision (AG-001's
"Observation Report," Discovery Lab's own "investigation," DL-0001's
"hypothesis"). Per instruction, this is recorded here, not fixed above.

**2. Section 4's "Review" is a fourth, unreconciled sense of the
word.** This ecosystem already has three distinct "review" concepts:
KOD's `Under Review` Research Session stage, generative-discovery-
engine's Critical Review of a discovery method, and `docs/ai-
organization/ORB/`'s Review of a specific employee's conduct against
its contract. Section 4's Evolution pipeline introduces a fourth —
review of a proposed *organizational change* — without stating how, or
whether, it relates to any of the other three. This is a direct
instance of Conflict 1, called out separately because it is a source of
real, practical ambiguity (see Open Question 2) rather than only a
naming collision.

**3. Section 3's evidence standard is not satisfied by how most
existing rules were actually produced.** "No organizational rule is
accepted without evidence" is stated as a candidate principle, but
`HIRING-LIFECYCLE-DRAFT.md`'s stage requirements, `ORB/ORB-PROTOCOL.md`'s
six questions and verdict vocabulary, and AG-001's nine metric names in
`employees/AG-001-repository-observer/METRICS.md` were all produced by
design reasoning and analogy to
sibling-repository conventions — not by evidence gathered from AI
Organization's own operation, which to date consists of exactly one
real run (`RUN-0001`) and zero ORB reviews. Read literally, Section 3
is not yet satisfied by the body of rules it claims to govern.

**4. Section 6's independence standard goes further than `RUN-0001`
actually practiced.** `RUN-0001` cross-verified one specific finding
(the branch list) through two independent methods only after the first
method produced a result that looked incomplete — it did not apply
dual-sourcing to its other claims (for example, the tag list or the
file-diff counts), even though an independent verification method
existed for at least some of them (the GitHub API's own diff/compare
endpoints). `RUN-0001` was accepted as compliant under the rules that
existed at the time, which did not require this. Adopting Section 6 as
written raises an open question this charter does not answer: whether
it applies only prospectively, or would call `RUN-0001`'s single-sourced
claims into question retroactively.

**5. Section 4's "Experiment" stage names a capability that is
currently dormant.** `PROP-0001` (revision 3) explicitly marks its own
information-flow map's Experiment stage as "DORMANT under Variant B —
only active if Variant A or C were adopted later," since Discovery
Lab's recommended mandate does not currently authorize running
experiments. This charter's Evolution pipeline lists "Experiment" as a
standard stage without noting that, as of this document, that specific
stage has no authorized way to actually run.

**6. Section 8's use of "Trust" is thematically adjacent to
trust-engine's namesake concept.** `PROP-0001`'s ground rule 3 states
Discovery Lab "never re-implements a context-scoped trust-scoring or
trust-mutation pipeline... that is trust-engine's fully-specified
territory." Section 8 proposes no scoring formula or mutation pipeline
— its content is a restatement of `HIRING-LIFECYCLE-DRAFT.md`'s
already-existing `Trusted` lifecycle stage, which predates this charter
— but the word "Trust," paired with "earned through... verifiable
behavior," echoes trust-engine's own framing ("Trust is compressed
memory of how a model performed... against reality") closely enough
that this document records the resemblance rather than assuming it is
harmless.
