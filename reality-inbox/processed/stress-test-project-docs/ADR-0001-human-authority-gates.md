# ADR-0001 — Human Authority Gates (HAG)

Status: **ACCEPTED**
Date: 2026-07-24
Accepted: 2026-07-24, by Petko (repository owner) — architectural
principles (§1–§7) approved and adopted as part of the AI Organization's
architecture. Migration explicitly deferred — see "Acceptance record",
below, and `ADR-0001-migration-plan.md`.
Author: Implementer session (Claude Code), from a design dictated directly
by the requester
Depends on / builds on: `../ai-organization/MEMORY-SOURCES/
INFRA-SPRINT-01-report.md` (the concrete incident this ADR generalizes
from), `../ai-organization/MEMORY-SOURCES/MEMORY-SOURCE-PROTOCOL.md`
(the Registry this ADR proposes extending), `../ai-organization/
employees/AG-002-discovery-archaeologist/RUN-PROTOCOL.md` (the Stop rule
this ADR reclassifies, without editing it)

## Acceptance record

Accepted by Petko on 2026-07-24, in response to the draft submitted the
same day. Explicit terms of acceptance, quoted from the decision: "The
architectural principles are approved and become part of the
organization's architecture. Do not begin the migration yet." Concretely:

- **Accepted and now in force as architecture**: the Human Authority Gate
  concept (§2), Standard Agent Behavior (§3), the required HAG report
  format (§4), the Registry Connectivity/Authority extension as designed
  (§5), and the four-category Organizational Principle with its
  reconciliation against Sprint 01 (§6). Future architectural reasoning in
  this repository may now cite this ADR as settled, the way `PROP-0001`'s
  Principle 0 is already cited elsewhere.
- **Explicitly not started**: implementation/migration. §8's four items
  (AG-002 terminology migration, Registry schema migration, HAG Log
  creation, automatic resume) remain unimplemented by decision, not by
  oversight. `ADR-0001-migration-plan.md` records the plan for that future
  work without performing any of it.
- Acceptance does not itself change any file this ADR previously left
  unmodified — `RUN-PROTOCOL.md`, `INPUTS.md`, `MEMORY-SOURCE-PROTOCOL.md`,
  and `MEMORY-SOURCE-REGISTRY.md` are all still exactly as they were when
  this ADR was drafted.

## How to read this document

This is the first ADR in `discovery-lab` — a new document type alongside
this repository's existing `PROP-000N` proposals. Where a `PROP` argues for
a policy or process, this ADR names and defines an architectural concept
(**Human Authority Gate**) and records the decision to adopt it. As of the
Acceptance record above, its architectural content (§1–§7) is **ACCEPTED**
— the first document in this repository to reach that status, ahead of
`FOUNDING-CHARTER.md` and `PROP-0001`–`PROP-0003`, which remain DRAFT.
Acceptance is deliberately narrow: nothing existing is rewritten by this
ADR or its acceptance — not AG-002's `RUN-PROTOCOL.md` or `INPUTS.md`, not
the Memory Source Registry's schema, not `INFRA-SPRINT-01-report.md`'s own
text. Section 8 states exactly what remains to be done to actually apply
this architecture, and `ADR-0001-migration-plan.md` is the plan for doing
it — deliberately not executed yet, per the acceptance terms above.

---

## 1. Problem

The AI Organization increasingly interacts with external resources that
cannot and should not be fully automated — Google Drive, GitHub protected
operations, Gmail send, Google Calendar modifications, banking APIs,
government portals, electronic signatures, physical-world approvals. These
systems intentionally require human authority.

Current behavior treats these situations as technical failures
(`BLOCKED`), but they are not failures — they are designed governance
boundaries.

This is not a hypothetical problem. `INFRA-SPRINT-01-report.md` is a
concrete, evidence-backed instance of exactly this: AG-002's
`PILOT-RUN-0002` returned `BLOCKED` against the Google Drive connector,
and the diagnosis (that report's §1, §8) found the connector fully
authenticated and connected — the actual condition was a one-time,
human-interactive approval requirement, not a defect anywhere in
discovery-lab's own code or configuration.

## 2. Decision

Introduce a new architectural concept: **Human Authority Gate (HAG)**.

> A Human Authority Gate is any action that requires explicit human
> authorization before the organization may continue.

**Crossing a HAG is never considered an error. It is a normal state
transition.**

## 3. Standard Agent Behavior

When a HAG is encountered, every AI employee must:

1. Stop immediately.
2. Preserve all accumulated work.
3. Record the exact reason.
4. Specify the minimal human action required.
5. Wait.
6. Resume automatically after authorization if possible.

No retries. No workarounds. No duplicated data.

This is not a new invention for this repository: it is the same discipline
`RUN-PROTOCOL.md`'s Stop rule and `INPUTS.md`'s `INSUFFICIENT ACCESS`
convention already practiced during `PILOT-RUN-0002` — stop, record, don't
substitute, don't fabricate. What this ADR changes is the **label** and
the **meaning attached to it**: the same behavior that produced `BLOCKED`
(read as failure) should, once this ADR is adopted, produce a HAG report
(read as an expected, resumable state). See §6 for why this distinction is
not merely cosmetic.

## 4. Required Output

Every HAG report must contain:

- Resource
- Requested action
- Blocking authority
- Evidence
- Exact human action
- Expected result
- Resume point

`INFRA-SPRINT-01-report.md` §5 ("Human Action Required") already contains
every one of these fields for the Google Drive incident, in substance if
not under these exact headings — it can serve as the worked template for
this format once adopted (§8, item 3).

## 5. Registry Extension

Every external resource gains two independent states, which must never be
merged into one:

**Connectivity**
- Connected
- Disconnected

**Authority**
- Authorized
- Pending Human Approval
- Denied
- Unknown

### 5.1 Worked example, from real evidence

Applying this two-axis model retroactively (for illustration only — not
applied to the actual Registry file by this ADR) to the two entries that
exist in `MEMORY-SOURCE-REGISTRY.md` today:

| Entry | Connectivity | Authority | Basis |
|---|---|---|---|
| `MEM-001` (project-memory, Git) | Connected | Authorized | Git fetch succeeded and was read in full during `PILOT-RUN-0001`; no interactive gate exists for this source type |
| `MEM-002` (Google Drive diary) | **Connected** | **Pending Human Approval** | `INFRA-SPRINT-01-report.md` §1.1: the MCP transport itself connects successfully (`"Successfully connected (transport: http) in 323ms"`); §1.3: every tool call returns `-32003 needs_approval` |

`MEM-002` is the clearest possible argument for this ADR: under the
current single-field `status` enum (`active | inactive | deprecated |
unverified`), a connected-but-gated source and a genuinely unreachable one
collapse into the same signal. The two-axis model is the only one of the
two schemas that can actually represent what `INFRA-SPRINT-01-report.md`
found.

### 5.2 Open question this ADR does not resolve

The current schema's `deprecated` value is a lifecycle/retirement flag,
not a live-state observation — it does not map cleanly onto either
Connectivity or Authority. This ADR does not resolve where `deprecated`
belongs in the two-axis model (a third, orthogonal `lifecycle` field is
one option; folding it into Authority as a fifth value is another).
Recorded as an open question, not decided here, in the same
"record, don't silently fix" discipline as `FOUNDING-CHARTER.md`'s
Candidate Conflicts.

## 6. Organizational Principle

The organization distinguishes four categories:

- Technical failure
- Infrastructure limitation
- Governance boundary
- Human Authority Gate

Only the first two are engineering problems. The latter two are expected
operational states.

### 6.1 Reconciliation with Infrastructure Sprint 01's Five Whys

`INFRA-SPRINT-01-report.md` §8 used a different four-layer vocabulary
(symptom / technical cause / infrastructure cause / governance cause) to
classify the same incident. The word **"governance"** is used differently
in each document, and that collision is disambiguated here rather than
left implicit:

- Sprint 01's **"governance cause"** meant: *an organizational ownership
  gap under human control* — nobody was assigned to grant connector
  approvals or enforce source verification. That is a fixable gap, not a
  permanent boundary.
- This ADR's **"Governance boundary"** category means something narrower
  and by-design: a boundary the organization *intends* to keep, e.g.
  `PROP-0001`'s Principle 0 ("Discovery Lab never creates truth"). It is
  not something to be engineered away.

Reconciled: under this ADR's four categories, the `-32003` signal itself
reclassifies from Sprint 01's "technical cause" to a **Human Authority
Gate** — not a failure, not an engineering problem. But Sprint 01's
downstream findings — no automatic resume path (behavior 6 above,
currently unimplemented anywhere), Registry Stage 4 not enforced before
Stage 2, no assigned owner — remain genuine **Infrastructure
limitations**: real, fixable gaps, exactly what Sprint 01's "smallest
permanent fix" and this ADR's §8 both target. Nothing in Sprint 01's
conclusion is contradicted by this ADR; the HAG concept refines which part
of that finding was ever an "error" (none of it, once correctly
classified) versus which part is still a real, actionable gap (the
missing ownership and enforcement, unchanged).

## 7. Success Criteria

Future agents encountering Gmail, Calendar, GitHub, Google Drive, ERP
systems, banking APIs, or other protected resources should all behave
identically: stop, preserve, report using the fixed field list in §4, wait,
resume if possible — never retry, never work around, never duplicate data.

## 8. What implementing this ADR still requires (accepted, not started)

This ADR's architecture is **ACCEPTED** (see Acceptance record, above),
but acceptance did not, by itself, change any other file, and the
requester explicitly instructed that migration not begin yet. These
remain separate, deferred steps — planned in full in
`ADR-0001-migration-plan.md`, not performed here or there:

1. **`RUN-PROTOCOL.md` / `INPUTS.md` (AG-002) migration** — deciding
   whether `INSUFFICIENT ACCESS` and `BLOCKED` should be replaced by, or
   mapped onto, the HAG report format in §4. Not done here — "do not
   redesign AG-002" held for this task as it has for prior ones.
2. **`MEMORY-SOURCE-PROTOCOL.md` schema migration** — replacing the
   single `status` field with the two independent axes in §5, updating
   `SOURCE-REGISTRATION-TEMPLATE.md`, and re-expressing `MEM-001`/`MEM-002`
   under the new schema. Not done here.
3. **A HAG Log** — an append-only record of HAG encounters, mirroring the
   existing convention already used by `EMPLOYEE-REGISTRY.md`,
   `ORB-REGISTRY.md`, and `MEMORY-SOURCE-REGISTRY.md`, would be the
   natural place to file reports in the §4 format. Not created here — no
   HAG has yet been reported *under this ADR's format*, and creating a
   registry ahead of its first real entry would repeat the exact mistake
   `MEMORY-SOURCE-PROTOCOL.md` explicitly argued against ("no invented
   starting values").
4. **Item 6 of §3 ("Resume automatically after authorization if
   possible")** — no mechanism for automatic resume currently exists
   anywhere in this repository or session tooling. This ADR states it as
   a target behavior; building it is out of scope here and is itself an
   Infrastructure limitation per §6.

## Definition of Done

**ACCEPTED, migration not started.** Petko accepted this ADR's
architectural content (§1–§7) on 2026-07-24, with migration explicitly
deferred (see Acceptance record, above). §8 remains the punch list of
what implementation requires; `ADR-0001-migration-plan.md` is the plan
for executing it, on its own future authorization.
