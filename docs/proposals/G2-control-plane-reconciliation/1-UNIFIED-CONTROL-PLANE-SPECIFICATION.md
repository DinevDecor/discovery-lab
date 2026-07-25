# Deliverable 1 — Unified Control Plane Specification

Reconciled from `project-memory/adr/ADR-0001-ai-collaboration-
architecture.md` + the Stable Core of `archive/AI-Collaboration-
Architecture-v1_1.md` it ratifies ("PM"), `kod/Core/ADR/ADR-0009.md`
("KOD"), and `discovery-lab/docs/ai-organization/GOVERNANCE.md`
("DL"). Every section states the canonical formulation once, with
each source's own terminology and citation — reconciliation, not
invention, per this task's own rule.

## 1. Source of Truth

**Canonical statement**: Versioned repository artifacts (commits,
accepted decisions, contracts) are authoritative. Conversation,
chat memory, and prompts are never authoritative — at most, raw
material.

- **PM** (`INV-2`, "Чатът не е истина"): "Никое решение не съществува
  само в conversation memory. Чат transcript има авторитет нула, но
  стойност като суров източник." Reinforced in the Authority/Truth
  Model: "notes, drafts, chat transcripts... не са в нито един слой на
  властта: те са суровина."
- **KOD** (Repository Governance): "The repository is the Single
  Source of Truth for the KOD ecosystem. No conversation, prompt, or
  AI memory is authoritative."
- **DL** (implicit throughout the Freeze Lifecycle): every stage
  produces a versioned artifact (`STATUS.yaml`, `HISTORY.md`, the
  Freeze Recommendation record); "The Git commit is the authoritative
  record" pattern is inherited from the same `ADR-0001`–`ADR-0004`
  acceptance precedent `GOVERNANCE.md`'s own header cites, though
  `GOVERNANCE.md` itself does not restate the SSOT principle as its own
  invariant — it assumes it.

**Convergence**: identical principle, stated explicitly by PM and KOD,
assumed without restatement by DL.

## 2. Contract-Defined Roles

**Canonical statement**: Roles are versioned, repository-stored
contracts, not prompts and not fixed models. An executor (human or AI)
binds to a contract; the contract, not the executor's identity, defines
what the role may and may not do.

- **PM** (`INV-3`, "Договори, не модели"): "Всяка роля е
  version-controlled контракт. Кой модел го изпълнява е подменяем
  детайл." Contract format specified (§7): Mission, Inputs, Outputs,
  Authority, Prohibitions, Definition of Done, Duty to Object.
- **KOD**: "Roles are defined by versioned Agent Contracts stored in
  the repository... Prompts do not define roles. Prompts load
  contracts." Contract fields: Purpose, Authority, Inputs, Outputs,
  Forbidden Actions, Writer Permissions. Contract changes require an
  ADR. A session binds to a specific contract version by commit
  reference (`Load contract: <path> @ <commit>`) and is never rebound
  mid-task.
- **DL**: not restated in `GOVERNANCE.md` itself as a named principle —
  `GOVERNANCE.md` governs the *lifecycle* a Role's document set (which
  includes `CONTRACT.md`) goes through, presupposing the
  contract-not-model principle rather than asserting it. Each `AG-00X`
  Role's `CONTRACT.md` (outside this document's own scope) is the
  concrete instance.

**Convergence**: identical mechanism (PM, KOD); DL's `GOVERNANCE.md`
operates one layer up (governing how a Role's contract set matures)
and presupposes rather than restates the principle. See
`4-CONFLICT-RESOLUTION-LOG.md` item C2 for the role-taxonomy layer
distinction this implies.

## 3. Formal Gate

**Canonical statement**: A mechanical, criterion-bound check —
distinct from open-ended critique — that verifies an artifact against
a fixed, applicable standard and returns a small enumerated verdict.
It never edits the artifact, never invents criteria beyond the
standard, never assigns work, never merges, and never renders the
final human decision.

- **PM** (§8, Kernel Governance Layer): Kernel is "формален
  пропускателен пункт" ("formal gate"), answering exactly one
  question: does the artifact satisfy the applicable Review Contract?
  Protocol: identify the applicable contract → fix its version →
  check criterion by criterion → return `PASS` or `BLOCKED` (+ which
  criterion, where, quoted). Explicit prohibitions: no inventing
  criteria, no editing, no assigning tasks, no merging, no final human
  decision, no softening `BLOCKED` into "PASS with notes." "Kernel като
  концепция за формален gate е Stable Core" — the concept itself,
  distinct from its specific daily-session implementation (marked
  Experimental).
- **KOD**: "Kernel Review" is both a Role and the act it performs: "An
  ADR moves from Draft to Accepted only after Kernel Review returns
  PASS. If Kernel Review returns BLOCKED, the ADR remains in Draft
  until revised and re-reviewed."
- **DL**: the closest equivalent within `GOVERNANCE.md`'s own scope is
  the **Adversarial Review** stage of the 7-stage Freeze Lifecycle: "an
  active attempt to find defects the Draft introduces on its own
  terms... Must produce a written record of every defect found... and
  a stated verdict." Distinct in scope from PM/KOD's Kernel: PM's
  Kernel checks conformance to a fixed *Review Contract*; DL's
  Adversarial Review is a broader, less formally bounded defect-hunt
  against the Draft's *own internal consistency*, not a fixed external
  contract. Both feed into a subsequent, separate acceptance step (DL:
  Freeze Recommendation → human `FROZEN` decision) rather than deciding
  anything themselves.

**Convergence**: same underlying shape (bounded check, enumerated
verdict, feeds a separate human decision, no editing/deciding power of
its own) across all three; **not identical in formal strictness** — PM
and KOD's Kernel is the more mechanical, contract-bound instance; DL's
Adversarial Review is broader and less formally bounded. See
`4-CONFLICT-RESOLUTION-LOG.md` item C1.

## 4. Human Final Authority

**Canonical statement**: A category of decisions — accepting a
proposal, merging, resolving a normative/operational mismatch,
changing the governing rules themselves — belongs only to a human, not
to any AI role, however senior.

- **PM** (`INV-4`, explicit): "Само човекът: приема ADR, разрешава
  merge, разрешава drift, променя протокола." Restated in the Authority
  Matrix (Матрица на правомощията): only "Човек" may accept an ADR,
  merge to main, or change the protocol; an AI role may only signal
  drift, never resolve it.
- **KOD**: "Headquarters commits the status change. The Git commit is
  the authoritative record of acceptance." **`ADR-0009`'s own text does
  not state that Headquarters must be human** — see
  `4-CONFLICT-RESOLUTION-LOG.md` item C3; this is a real textual gap,
  not resolved here by assumption.
- **DL**: "an explicit human decision (a direct instruction, or a
  recorded acceptance in the same pattern as `ADR-0001`–`ADR-0004`)
  accepts the Freeze Recommendation. Only this step changes a Role's
  `status` field to `frozen`." Also: "Discovery Lab does not freeze
  itself" — the same "who may run the process, and who may not decide
  it" split `HIRING-LIFECYCLE-DRAFT.md` states for its own `Trusted`
  tier.

**Convergence**: explicit and identical in PM and DL. **Not explicitly
stated in KOD's `ADR-0009`** — a genuine gap, recorded, not filled.

## 5. Drift — normative/operational mismatch

**Canonical statement**: When what a system is authorized to do
(normative layer) and what it actually does (operational layer)
diverge, this is a named, first-class state — not an error to hide and
not automatically resolved in either direction. It blocks the affected
work until a human decides.

- **PM** (`INV-6` + §6 "Architecture–Implementation Drift"): two-layer
  truth model (Normative Authority: Constitution → Accepted ADR →
  Specification → Issue; Operational Reality: code in main → tests →
  runtime behavior); "Между слоевете няма автоматичен победител."
  Procedure: detection → `STATUS: DRIFT` (blocks affected work) → short
  drift analysis → human decision (code is wrong / ADR is stale / both
  partially true) → drift closed, recorded. "Кодът не става
  архитектурна истина само защото е merge-нат. ADR не остава истина
  само защото е приет."
- **KOD**: no directly equivalent named state in `ADR-0009` itself.
  The Authority Matrix's precedence order (Git commits/tests as ground
  truth, above ADRs) addresses a related but narrower question —
  *which artifact wins when two disagree* — not the broader "this
  needs a human decision, not an automatic resolution" principle PM
  states. See `4-CONFLICT-RESOLUTION-LOG.md` item C4.
- **DL**: no equivalent named state in `GOVERNANCE.md` — the closest
  parallel is a `NOT READY` Freeze Recommendation verdict returning a
  Role to `Draft`, which is a lifecycle-stage rollback, not a named
  standing "drift" state between two independent layers of authority.

**Convergence**: PM states this as a Stable Core invariant with a full
named procedure. Neither KOD nor DL's cited document restates it. Not
a contradiction — DL and KOD are simply silent here, within the scope
of these three specific documents.

## 6. Communication and Handoff

**Canonical statement**: Agents do not communicate directly or
autonomously. Work in progress crosses a session/agent boundary
through a structured, written Handoff artifact that summarizes
completed work and points to authoritative repository state. A Handoff
is never itself evidence and never replaces the repository artifacts
it references.

- **PM** (§14, Handoff Protocol): fixed template (Goal, Done,
  Micro-decisions, Not done, Next concrete step, Traps, Open
  questions); "Handoff се пише от изпълняващата роля преди CLOSE, не
  от човека по памет" (written by the executing role before session
  close, not reconstructed from the human's memory).
- **KOD** (Communication Protocol + Human Message Bus): "Agents do not
  communicate directly. Communication occurs through repository
  artifacts and structured Handoffs... A Handoff is never evidence and
  never replaces repository state." Explicitly names the *current*
  mechanism as human-mediated: "The human operator performs message
  passing by transferring Handoffs, repository references, and
  contract pointers between sessions... Future automation may replace
  the human message bus without changing the collaboration model."
- **DL**: no equivalent named artifact in `GOVERNANCE.md` itself — this
  document governs Role-freeze lifecycle, not session-to-session
  handoff mechanics; out of this specific document's scope, not a
  disagreement.

**Convergence**: PM and KOD converge closely, including on the same
honest acknowledgment that the mechanism is currently human-mediated
and may be automated later "without changing the collaboration model."
DL's cited document is silent, out of scope rather than in conflict.

## 7. Staged, Human-Gated, Revisable Lifecycle

**Canonical statement**: An artifact or Role moves through named
stages, from proposed to authoritative, via a formal gate and a
terminal human decision; the process can be re-entered for
substantive revision, and versioning reflects the scale of change.

- **PM**: ADR-implicit (Authority Matrix's "Приема ADR (→ ACCEPTED)"
  row; §16 "Artifact Lifecycles" governs document artifacts) — present
  as a assumed shape, not elaborated to DL's level of granularity
  within the Stable Core sections reconciled here.
- **KOD**: "An ADR is created in Draft status by Headquarters. An ADR
  moves from Draft to Accepted only after Kernel Review returns PASS.
  If Kernel Review returns BLOCKED, the ADR remains in Draft until
  revised and re-reviewed. Headquarters commits the status change."
  Two states (`Draft`, `Accepted`), one gate.
- **DL**: by far the most granular of the three, within scope: seven
  named stages (`Idea → Draft → Internal Review → Adversarial Review →
  Reality Stress Test → Freeze Recommendation → FROZEN`), plus a
  five-way versioning taxonomy (bug fix / clarification / minor
  revision / major revision / deprecation), each with precise
  triggering criteria and required evidence.

**Convergence**: same underlying shape (proposed → gated → human
decision → authoritative, with a re-entry path for revision) at three
different levels of elaboration. DL's `GOVERNANCE.md` is the most
detailed articulation of a shape KOD states in its minimal two-state
form and PM assumes without full elaboration in the sections
reconciled here. Not a contradiction — a difference in the granularity
each document commits to text.

## What this specification deliberately does not state

No new Runtime, no new Role, no new Gate type, and no resolution to
the four real gaps recorded in `4-CONFLICT-RESOLUTION-LOG.md` (Kernel
vs. Adversarial Review's differing formality; whether Human Final
Authority binds `kod`'s Headquarters role; PM's Anti-theater clause
having no stated KOD/DL counterpart; Drift having no stated KOD/DL
counterpart). Each is reported, not invented past.
