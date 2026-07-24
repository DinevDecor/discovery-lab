# AI Organization — README

**Status: DRAFT / EXPERIMENTAL / NOT ADOPTED.** This is not a new
repository, not an accepted architecture, and not a permanent new
component of the DinevDecor ecosystem. It is a bounded prototype living
inside `discovery-lab`, at `docs/ai-organization/`.

## What this is

An organizational model for AI-performed work, structured the way a real
company structures jobs: a **Role** — a permanent, versioned job
description (mission, responsibilities, limitations, inputs, outputs,
metrics, lifecycle) — is defined independently of any **Executor** — the
specific model, process, or person who currently performs it.

The candidate principle behind this, exactly as given at its origin:

> **Role is stable. Executor is replaceable.**

The first proposed role is `AG-001 — Repository Observer`, defined in
full in `employees/AG-001-repository-observer/`. Its origin: during an
architectural discussion about future AI agents, the observation emerged
that instead of creating free-floating "agents," each AI executor should
occupy a clearly defined organizational position — one that is permanent
and independent of the specific model performing it, because the
executor could be Claude, ChatGPT, another model, a local process, or a
future system. The reason given for AG-001 specifically: the ecosystem
currently lacks systematic, traceable observation of changes across its
repositories.

## Why this differs from a traditional multi-agent system

A traditional multi-agent setup typically defines an **agent**: a prompt,
a toolset, and a session, usually bound implicitly to whichever model
runs it. Replacing the model means rewriting the agent. Responsibilities,
limits, and success criteria often live only inside the prompt text
itself, and are easy to drift silently as the prompt is edited.

This prototype instead defines an **organizational position**: a role
with its own contract, explicit rights and responsibilities, a versioned
metrics interface, a candidate lifecycle with promotion/retirement
criteria, and hard, enumerated limitations — all as separate,
independently readable documents, of which the prompt (`PROMPT.md`) is
only the operational trigger for whichever executor currently holds the
role. Swapping the executor does not require rewriting the role. The
role's contract and limitations stay in force regardless of who or what
performs it. This is the entire reason `employees/` documents are split
across eleven separate files instead of one prompt file.

## Why AG-001 is not yet "hired"

Per `HIRING-LIFECYCLE-DRAFT.md`, AG-001 currently sits at
**Prototype**, the second of five candidate stages (`Candidate → Prototype
→ Probation → Trusted → Retired`). It has zero completed runs
(`STATUS.yaml: runs_completed: 0`), zero reviewed reports, and no
executor assigned (`executor: unassigned`). Advancing even one stage
requires a defined number of real runs, independent review of a sample
of its reports, documented gaps and false positives, and — critically —
a human decision with a recorded reason. None of that has happened yet.

## Why these files existing does not prove the architecture is correct

Writing a contract, a role definition, and a metrics interface makes a
design **legible and falsifiable** — it does not make it **true**. This
is the same discipline `PROP-0001`'s **Principle 0** already states for
the rest of Discovery Lab:

> Discovery Lab never creates truth. It only observes, compares, and
> identifies inconsistencies, and proposes next steps... Discovery Lab
> itself never accepts, finalizes, or applies any of these proposals.

AG-001's own core principle — "Observe changes. Report evidence. Do not
decide." — is a direct operationalization of that same rule at the level
of an individual role, not a new or competing principle.

## What would be needed before adoption

At minimum, per `HIRING-LIFECYCLE-DRAFT.md`: a stated number of real
runs against real, authorized repositories; an independent review of a
sample of the resulting Observation Reports for accuracy and boundary
compliance; a documented account of any false positives or missed
changes found during that review; and an explicit human decision,
recorded with its reason, to advance the role's status. Nothing in this
prototype claims any of that has happened.

## Why future roles should not be pre-created

Creating an organizational position before a specific, demonstrated need
exists is the same premature-abstraction risk `PROP-0001` already
identified and avoided when choosing between its three mandate variants.
This prototype deliberately defines exactly one role. No second role is
proposed or scaffolded here.

## Terminology note (disambiguation)

AG-001 produces documents literally titled "Observation Report" with a
section called "Current-State Observations." This uses the word
*observation* in the plain sense — a directly recorded fact about
repository state — and is **not** KOD's Knowledge Domain "Observation"
Knowledge Object (`KOD/Foundations/OBSERVATION.md`), and **not**
trust-engine's "Observation Memory" (`observation_architecture_v1.md`).
Nothing produced by AG-001 is entered into KOD's Knowledge Graph or
Trust Engine's memory layers by this prototype. If an AG-001 finding is
ever formalized inside either of those systems, that is a decision for
that system's own governance to make, not something AG-001 does on its
behalf. This follows the same disambiguation discipline `PROP-0001`
(ground rule 1, and its "Investigation" note) and `DL-0001` (its
"Hypothesis" note) already established for this repository.

## Open questions

- No permanent organizational owner is designated for this structure
  (see `STATUS.yaml: open_governance_questions`).
- No authority is designated to promote AG-001 to `trusted` — this
  document does not resolve who has that authority.
- The long-term location of AI Organization — staying inside
  `discovery-lab`, moving to its own repository, or being absorbed
  elsewhere — is undecided.
- A possible future question, explicitly not acted on here: **should
  Repository Observer remain limited to repository facts, or should a
  separate Organization Observer role be investigated?** This is
  recorded only as a question. AG-001's scope is not changed by it, and
  no new role or investigation is created in response to it in this
  prototype.
