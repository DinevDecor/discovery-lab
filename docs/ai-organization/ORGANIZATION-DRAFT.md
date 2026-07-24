# AI Organization — Organizational Model (DRAFT)

**Status: DRAFT — candidate organizational design, not accepted, not an
ADR.** This document does not establish AI Organization as accepted
architecture, does not create a permanent new component of the
DinevDecor ecosystem, and does not bind any repository other than this
prototype's own files inside `discovery-lab`.

## Core principle

> **Role is stable. Executor is replaceable.**

A **Role** is a permanent, versioned organizational position: a job
description with a mission, enumerated responsibilities, hard
limitations, defined inputs and outputs, a metrics interface, and a
place in a candidate lifecycle. A Role does not change because the
entity performing it changes.

An **Executor** is whoever currently performs a Role at a given time —
Claude, another AI model, a local automated process, or a human. A Role
may go through several Executors over its lifetime without itself
changing. `STATUS.yaml`'s `executor` field records the current one, or
`unassigned` if none is currently performing the role.

This separation is the entire reason a Role's definition lives in
several independent documents (contract, responsibilities, limitations,
inputs, outputs, metrics, run protocol, prompt) rather than in a single
prompt: replacing the Executor should never require rewriting the Role.

## Numbering and directory convention

Each Role receives a unique, permanent **Employee ID** in the form
`AG-NNN` (e.g. `AG-001`), assigned in order of creation and never
reused, even if the Role is later retired. Each Role's files live at:

```
docs/ai-organization/employees/<employee-id>-<role-slug>/
```

for example `employees/AG-001-repository-observer/`.

## What belongs in a Role's folder

Each Role's folder contains exactly these documents, each independently
readable without requiring the others:

- `CONTRACT.md` — the role's terms: parties, scope of authority,
  rights, responsibilities, term, and revocation conditions.
- `ROLE.md` — the full role definition: mission, core principle,
  responsibilities, explicit prohibitions, and escalation values.
- `INPUTS.md` — exactly what the role may receive before it may act.
- `OUTPUTS.md` — the exact required output format the role must
  produce.
- `LIMITATIONS.md` — the canonical, standalone list of hard boundaries;
  takes precedence if any other document appears to conflict with it.
- `CHECKLIST.md` — a practical pre-run / during-run / pre-submission
  checklist derived from the role's own rules.
- `METRICS.md` — the role's quality-measurement interface: metric
  names and their purpose, with no invented starting values.
- `RUN-PROTOCOL.md` — the step-by-step procedure the role follows,
  described in prose, not as executable code or an automation workflow.
- `PROMPT.md` — an executable prompt template for whichever Executor
  performs the role, with no specific AI model referenced.
- `STATUS.yaml` — the role's current machine-readable status.
- `HISTORY.md` — an append-only log of what has actually happened to
  this role (runs, reviews, status changes) — never edited
  retroactively, only appended to.

No file is added to a Role's folder beyond this set without first being
proposed, in writing, as a candidate addition — never created directly
alongside an unrelated task.

## Registry and lifecycle

`EMPLOYEE-REGISTRY.md` is the single index of every Role that has ever
been created, at any status, including retired ones — entries are never
removed, only updated. `HIRING-LIFECYCLE-DRAFT.md` defines the candidate
status stages every Role moves through and what is required to move
between them.

## Relationship to Discovery Lab's existing mandate

This model is a use of Discovery Lab's own custodianship function
(`PROP-0001`, Variant B — Ecosystem Observatory): a candidate
organizational design, held in DRAFT form, until someone verifies it is
worth adopting. It does not revise `PROP-0001`, and `PROP-0001`'s
recommendation is unaffected by this document. AG-001's core principle —
"Observe changes. Report evidence. Do not decide." — is a direct
instance of `PROP-0001`'s Principle 0 applied to a single organizational
role, not a new or competing principle.

## Explicit non-claims

- This document does not claim AI Organization is a good idea, only
  that it is a coherent one worth testing.
- This document does not claim any Role is ready to operate
  unsupervised.
- This document does not claim discovery-lab is the permanent home for
  AI Organization — see `STATUS.yaml`'s open governance questions.
- This document does not create, imply, or schedule any second Role.
  Additional Roles require their own demonstrated need, established
  separately, before being created — not scaffolded in advance.
