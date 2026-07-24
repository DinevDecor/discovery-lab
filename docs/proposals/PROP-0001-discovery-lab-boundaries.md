# PROP-0001 — Discovery Lab Mandate: Three Variants and a Recommendation

Status: DRAFT PROPOSAL — not accepted, not an ADR
Date: 2026-07-24
Author: Implementer session (Claude Code)
Depends on: `docs/investigations/INV-0001-discovery-lab-mandate.md`
  (diagnosis — read that first; this document proposes solutions only)

## How to read this document

Nothing here is accepted. No variant is adopted by writing it down. Per
the task constraints, a recommendation is given at the end, but it is
explicitly marked as unaccepted and requires a human decision
(consistent with `generative-discovery-engine/adr/ADR-0001`'s rule that AI
may draft/propose but not finalize architectural decisions — the same
discipline is applied here even though this is a different repository).

---

## Shared ground rules (apply to all three variants)

These follow directly from the overlaps and risks identified in INV-0001,
and apply regardless of which variant (if any) is eventually chosen:

1. Discovery Lab never uses the words **Observation, Hypothesis, Research
   Session, or Investigation Engine** as first-class artifact types of its
   own — those names are already owned by KOD's Foundations layer. If
   discovery-lab needs an analogous but lighter-weight concept, it must
   use a visibly different name (e.g. "note," "check," "spike") so the
   two are never confused.
2. Discovery Lab never re-implements a discovery-method validation
   pipeline (pre-registration, frozen protocol, PASS/FAIL verdict
   registry) — that is GDE's fully-specified territory.
3. Discovery Lab never writes to another repository's registry or state
   file. It may only *propose* a change (e.g., "PROJECT_REGISTRY.md
   should add a row for X") for a human or the owning repo's own process
   to apply.
4. Every artifact discovery-lab produces has an explicit fate: it either
   graduates to a named receiving repository, or it is marked
   SUPERSEDED/EXPIRED with a date. Nothing sits indefinitely in an
   ambiguous "still relevant?" state.
5. No ADR in discovery-lab is marked ACCEPTED unless an existing record
   shows a human accepted it.

---

## Variant A — Experiment Laboratory

**Purpose.** A technical sandbox for building and breaking agent
prototypes and running quick implementation spikes ("does this technical
approach even work?") — strictly implementation-level, not method
validation (GDE) and not knowledge/hypothesis research (KOD).

**Allowed artifacts.** Throwaway prototype code, spike scripts, scratch
technical notes, a dated result note per spike (worked / did not work /
inconclusive) with an explicit expiry date.

**Prohibited artifacts.** Production code or anything meant to run
unattended; accepted ADRs; discovery-method pre-registrations (GDE's
job); formal hypotheses, observations, or research sessions (KOD's job);
any persistent registry duplicating project-memory's or KOD's.

**Lifecycle of an experiment.** Draft spike → run → record result with a
verdict and an expiry date → either graduate (a real commit lands in the
owning repository — KOD, GDE, trust-engine, or a product repo) or the
spike is deleted/archived when its expiry date passes, whichever comes
first.

**Relationship to other repositories.** Strictly upstream and one-way:
discovery-lab produces candidate technical findings; nothing is
authoritative until it lands, as a real commit, in the repository that
actually owns that class of work.

**Advantages.** Cheap and fast; keeps KOD's and GDE's rigor from being
diluted by half-finished spikes; narrow enough to explain in one sentence.

**Failure modes.** Without enforced expiry, becomes a prototype graveyard;
risk of a spike quietly becoming a de facto dependency of something real
without ever formally graduating ("shadow production").

**Deletion/graduation rules.** Every spike carries an expiry date at
creation time. No graduation without a corresponding commit in the
receiving repository — a note in discovery-lab saying "this is done" is
not graduation.

---

## Variant B — Ecosystem Observatory

**Purpose.** A dedicated home for cross-repository ecosystem-health and
evidence investigations — access checks, drift detection, registry
cross-verification — of exactly the kind already performed twice, ad hoc,
inside `project-memory/notes/` (see INV-0001 §4). No code, no experiment
execution.

**Allowed artifacts.** Dated investigation reports, access/health-check
logs, cross-repo inventories, drift or contradiction findings.

**Prohibited artifacts.** Any code; any experiment; any hypothesis or
discovery-method claim; any write access to another repository — this
variant is read-only with respect to everything it inspects.

**Lifecycle of an investigation.** Triggered (manually, on request) →
report drafted with an explicit reconciliation/classification verdict →
findings routed as a proposal to the owning repository (e.g., a suggested
`PROJECT_REGISTRY.md` row change sent to project-memory as a proposal, not
applied directly) → report marked SUPERSEDED when a later investigation
of the same subject exists, otherwise kept as a permanent, append-only
evidence trail (mirroring the convention project-memory's own notes/
already uses).

**Relationship to other repositories.** Read-only inspector of KOD, GDE,
trust-engine, project-memory, and any product repository. Writes only
inside itself. Escalates findings as proposals, never edits other
repositories directly.

**Advantages.** Gives cross-repo evidence work a proper, low-risk,
correctly-scoped home instead of continuing to accumulate inside
project-memory's notes/ folder by convention; keeps project-memory
focused on being the control plane rather than the investigation archive;
directly evidenced need (two precedents already exist).

**Failure modes.** Could become a passive archive nobody acts on if
findings never get routed anywhere; risk of drifting into duplicating
project-memory's registry function if it starts trying to be authoritative
about other repositories' status itself rather than merely proposing.

**Deletion/graduation rules.** A finding that leads to action gets a
linked follow-up entry in the target repository; a stale or superseded
investigation report is marked SUPERSEDED with a date and kept, not
deleted (matches the append-only evidence convention already established
in project-memory).

---

## Variant C — Combined Lab + Observatory

**Purpose.** Both A and B under one roof, on the premise that ecosystem
findings (Observatory) and technical spikes (Lab) naturally feed each
other — an observatory finding ("repo X's state file is stale") can
motivate a lab spike ("prototype a fix"), and this is close to the literal
wording of the task's own core question.

**Allowed artifacts.** The union of A and B's allowed artifacts, kept in
clearly separated top-level directories (e.g. `experiments/` vs
`investigations/`) so they are never conflated.

**Prohibited artifacts.** The union of A and B's prohibitions, plus: an
investigation must never silently become the justification for an
experiment without the experiment being separately drafted and dated, and
vice versa.

**Lifecycle.** A's and B's lifecycles run independently, side by side, in
one repository, with a single shared `STATE.md` so both kinds of active
work are visible together.

**Relationship to other repositories.** The union of A's and B's
relationships. The added value over running A and B as two separate
repositories is the visible feedback loop between "what's wrong" and
"can we prototype a fix," at the cost of a repository trying to do two
structurally different jobs at once.

**Advantages.** One mandate, one repository to maintain; a natural
observatory→lab feedback loop; matches the task's own phrasing almost
exactly.

**Failure modes.** This is the variant with the **highest** risk of
becoming exactly the "miscellaneous dumping ground" the task explicitly
warns against. Combining two purposes under one roof, before either has
been tested alone, is a textbook premature abstraction: it assumes the
feedback loop between the two is valuable before either side has produced
a single real artifact to test that assumption against. It also makes the
"clear boundaries over ambitious scope" principle harder to hold in
practice — a repository that is both an inspector and a workshop is more
likely to blur provenance between "just checking" and "just building"
over time.

**Deletion/graduation rules.** Same as A and B, plus a mandatory
directory-level tag discipline (every top-level folder states which of
the two lifecycles it belongs to) so the two never merge into one
undifferentiated pile.

---

## Recommendation (proposed, not accepted)

**Recommended: Variant B — Ecosystem Observatory, alone, for now.**

Reasoning:

- It is the only variant with **direct, existing evidence of need** —
  this session's own recovery investigation, and the 2026-07-19 Dinev
  Decor evidence check, both already did Observatory-shaped work with
  nowhere proper to put it. Variant A's need (agent-prototype/technical
  spikes) is asserted by the task's core question but has no equivalent
  observed precedent yet in this ecosystem.
- It has the **narrowest, most defensible boundary** of the three: no
  code, no execution, read-only with respect to everything it inspects.
  This directly serves the task's own instruction to "prefer clear
  boundaries over ambitious scope."
- Variant C's core justification — a valuable feedback loop between
  observation and experimentation — is a hypothesis about value, not yet
  a demonstrated one. Adopting it now, before Variant B alone has even
  run once, is the kind of premature abstraction the task explicitly asks
  to guard against ("the right idea at the wrong time is still a
  methodological error"). If Variant B proves useful and a genuine,
  observed need for on-repository technical prototyping shows up
  afterward, Variant A or the merge into C can be reconsidered then, with
  evidence instead of anticipation.

This recommendation is not an acceptance. It requires a human decision
before any variant governs how discovery-lab is actually used.

---

## Proposed information-flow map (for Variant B, the recommended variant)

```
 ┌────────────────────────────────────────────────────────────────┐
 │                     Other DinevDecor repositories                │
 │   KOD   generative-discovery-engine   trust-engine   product repos│
 └───────────────────────────┬────────────────────────────────────┘
                              │ read-only inspection
                              ▼
                 ┌─────────────────────────────┐
                 │   discovery-lab (Observatory) │
                 │  docs/investigations/INV-NNNN  │  ← observations enter
                 │  (dated report, read-only)     │     and are reviewed
                 │  reconciliation/classification │     here — self-
                 │  verdict recorded in the report│     contained, no
                 └───────────────┬─────────────┘     external reviewer
                                  │ findings routed as a PROPOSAL           defined yet
                                  │ (never a direct write)
                 ┌────────────────┴─────────────────┐
                 ▼                                   ▼
   ┌───────────────────────────┐      ┌───────────────────────────────┐
   │  project-memory            │      │  the specific owning repo       │
   │  PROJECT_REGISTRY.md        │      │  (KOD Research Session, GDE      │
   │  PROJECT_STATE.md           │      │  pre-registration, a product    │
   │  — sole authoritative       │      │  repo commit, etc.)             │
   │  source for cross-project   │      │  — validated knowledge          │
   │  STATUS                     │      │  graduates here, formalized     │
   └───────────────────────────┘      │  in that repo's own process     │
                                        └───────────────────────────────┘
```

Where each thing happens:

- **Observations enter:** inside `discovery-lab/docs/investigations/`,
  produced by read-only inspection of the other repositories. Nothing
  external is written to during this step.
- **Experiments run:** nowhere, under the recommended Variant B. (If
  Variant A/C is chosen later, this would be `discovery-lab/experiments/`.)
- **Reviews happen:** inside the investigation report itself
  (self-contained reconciliation/classification verdict, as INV-0001 and
  the prior `docs/notes/2026-07-24-recovery-investigation.md` already do).
  No external/independent reviewer role is defined for discovery-lab —
  this is an explicit open question below.
- **Validated knowledge graduates:** to the specific repository that
  already owns that class of claim — project-memory's registry for
  project-status corrections, KOD's Research Session pipeline for
  knowledge/hypothesis claims, GDE's pre-registration pipeline for
  discovery-method claims, or a direct commit in the relevant product
  repository for code/architecture findings. Discovery-lab itself never
  becomes the authoritative source for any of these.
- **Project status is recorded:** only in `project-memory/
  PROJECT_REGISTRY.md` and `PROJECT_STATE.md`. Discovery-lab's own
  `STATE.md` records discovery-lab's own internal state only, and never
  asserts another repository's status.

---

## Smallest first experiment to test whether Variant B is useful

Run exactly **one** more Observatory-shaped investigation, entirely inside
discovery-lab this time instead of project-memory, and see whether the
pattern holds up outside its original ad hoc home:

> **INV-0002 (proposed, not yet run):** Produce a single dated snapshot
> file listing, for each repository currently known in this account (KOD,
> generative-discovery-engine, trust-engine, project-memory, discovery-lab
> itself, and any others discoverable via a repo listing) — its default
> branch, latest commit date, and whether it has a `STATE.md`/equivalent
> status file and what that file currently says. No automation, no
> scheduling, one person/session, one file, manual only.

This is deliberately the smallest possible test: it produces exactly one
artifact, requires no new infrastructure, and directly tests the one
open question that matters most — whether a dedicated `docs/
investigations/` home in discovery-lab is actually easier to use and more
discoverable than continuing to write these into `project-memory/notes/`
by habit. If it is not clearly better after one attempt, Variant B should
be reconsidered rather than assumed.

---

## Unresolved questions

- No independent review role is defined for discovery-lab's own
  investigation reports (GDE has a Critical Reviewer; KOD has a Research
  Guardian; discovery-lab currently has neither). Whether Variant B needs
  one, or whether self-contained reports are sufficient at this scale, is
  open.
- Whether `discovery-lab` should be added as a row in project-memory's
  `PROJECT_REGISTRY.md` is explicitly **not decided here** — per the rule
  already applied to the "Dinev Decor Systems" row in the 2026-07-19 note,
  the registry should not change while a repository's mandate is still
  DRAFT.
- Whether Variant A's asserted need (agent-prototype/technical spikes)
  is real cannot be resolved by this document — it can only be resolved
  by an actual observed need arising, which has not happened yet in this
  ecosystem as far as this investigation found.
- Whether KOD's internal use of the phrase "project memory" (ADR-0009)
  and the external `project-memory` repository could cause confusion
  in cross-repo documents remains unresolved and is flagged for whoever
  next writes KOD- or ecosystem-facing documentation, not resolved here.
