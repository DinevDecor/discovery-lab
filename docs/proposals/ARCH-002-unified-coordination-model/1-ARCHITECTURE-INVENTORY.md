# Deliverable 1 — Architecture Inventory

Per `ARCH-002` Phase 1. Every document found by content search (not
filename-pattern search) for: coordination, runtime, supervisor,
scheduler, dispatcher, execution, workflow, governance, orchestration,
control plane, event flow, organization, AI organization, operating
model — across all five available repositories. Status quoted exactly
as found in the source document, not inferred. This inventory is the
gate for every later deliverable: **Phase 5's canonical model may only
draw on the `Ratified` and `Repeated-concept` rows below**, per the
task's own explicit sourcing rule.

Status legend used in the rightmost column:
- **Ratified** — document (or a specifically named subsection of it)
  carries an explicit `ACCEPTED`/`FROZEN` status.
- **Unratified** — explicitly `DRAFT`/`PILOT`/`UNDER_TEST`/`Planned`/
  `BLOCKED`, or carries no status field at all.
- **Split** — the document itself is unratified, but a separate,
  ratified instrument (an ADR) formally accepts a named subset of its
  content. Both facts are recorded.

## `project-memory`

| Document | Status (as found) | What it is | Eligibility |
|---|---|---|---|
| `adr/ADR-0001-ai-collaboration-architecture.md` | **ACCEPTED** (2026-07-16) | Ratifies the Stable Core of `AI-Collaboration-Architecture-v1_1.md`; establishes `project-memory` as "collaboration control plane" | **Ratified** |
| `archive/AI-Collaboration-Architecture-v1_1.md` | Document header: "Candidate for Adoption." §3 splits itself into three tiers: **Stable Core** (7 invariants, two-layer truth model, contract model, human final authority, Control Plane as a concept, "Kernel as a formal-gate concept") — ratified by `ADR-0001`; **Operational Defaults** (§11–13 flows, file structure, artifact lifecycle, templates) — `UNDER_TEST`; **Experimental Practices** — `UNDER_TEST` | The Control Plane design | **Split** — only the named Stable Core items are usable as canonical source |
| `protocols/AI_COLLABORATION_PROTOCOL.md` | **Status: PILOT. Stable Core: ACCEPTED. Operational Defaults: UNDER_TEST. Experimental Practices: UNDER_TEST.** | Operational/pilot instantiation of the same architecture | **Split**, same boundary as above |
| `contracts/dispatcher.md` | **Status: PILOT** | A named "Dispatcher": accepts a task, classifies it into exactly one type, selects workflow/role/repo context, emits one next step — explicitly does not execute the specialized work itself | Unratified |
| `PROJECT_STATE.md`, `PROJECT_REGISTRY.md` | No document-level status field found | State/registry artifacts the Dispatcher reads as input | Unratified as architecture (they are live data, not a design) |
| `archive/architecture-design-document.md` | Not an ecosystem coordination document | The "Handover" field-service SaaS domain model — has its own domain-specific "Dispatcher" (a human installer-scheduling role), a different business meaning of the word, unrelated to AI-ecosystem coordination | **Excluded** — false positive, flagged not hidden |

## `kod`

| Document | Status (as found) | What it is | Eligibility |
|---|---|---|---|
| `Core/ADR/ADR-0009.md` | **Accepted** | Multi-Agent Collaboration Architecture: repository as Single Source of Truth, Agent Contracts, Authority Matrix, Writer Matrix, Kernel Review `PASS`/`BLOCKED` gate before Draft→Accepted, human-mediated message passing "explicitly recognized as part of the architecture" | **Ratified** |
| `Core/ADR/ADR-0003.md`, `ADR-0005.md`, `ADR-0006.md`, `ADR-0007.md` | **Accepted** (all four) | Specification-before-implementation; package architecture; runtime root; "Domain First Architecture" ("Architecture precedes implementation... Research precedes AI") | **Ratified**, supporting evidence |
| `Core/RUNTIME_ARCHITECTURE.md` | No status field in the document itself. Corroborated as delivered by `Core/ROADMAP.md`'s v0.1 "Foundation" milestone, which lists "Runtime Architecture" under `Completed` | Linear pipeline: `KnowledgeObject → KnowledgeGraph → ReasoningEngine → ReasoningValidator → Trust Engine`; one-responsibility-per-component rule | **Split** — treated as delivered (roadmap-corroborated), but it is a *reasoning/data* pipeline, not a *task/work* coordination runtime — see Phase 2 |
| `Core/Registry/PROJECT_STATE.md` | Live state file, not a design doc | States plainly: `Architecture Status: FROZEN`, `Kernel Status: DESIGN` (not built), and lists an `Execution Layer` (Python/SQLite/API) separately from `Control Layer`/`Knowledge Layer` — KOD's own admission that its execution layer does not exist yet | Not architecture itself; **direct primary evidence** for Phase 6 |
| `Core/ROADMAP.md` | Per-version `Status:` fields: v0.1 `Completed`; v0.2 "Research Operating System" (Research Guardian, Traceability Engine) `Planned`; v0.3 Trust Integration `Planned`; v0.4 Regime Integration `Planned` | KOD's own forward plan for a coordination/OS layer | **Unratified** (`Planned`) — cannot be canonical, but is direct evidence that KOD itself has not yet built the coordination layer ARCH-001/`DLOS` imagined |
| `Core/ARCHITECTURAL_PRINCIPLES.md` | No status field | General evolution principles (`AP1`–`AP7`, incl. `AP7` "No Architectural Ego" — even KOD's own architecture stays open to revision) | Unratified as a single document, but individual principles corroborate patterns found elsewhere — used only that way |
| `Core/DOMAIN_MODEL.md` | No status field; the file itself contains an unlabeled first draft, an explicit unresolved **"Open Question"** ("Is Research Session the fundamental entity of KOD, or is there a deeper object still missing?"), and *two different, inconsistent* sections both titled "Domain Model v2" | Concept modeling for `Research`/`Knowledge`/`Reasoning` | **Excluded from canonical use** — the document is internally unresolved by its own admission |
| `Foundations/RESEARCH_ENGINE.md`, `RESEARCH_GUARDIAN.md`, `RESEARCH_ENGINE_CONTRACT.md`, `INVESTIGATION_ENGINE.md` | Read in full during `META-001`; specification-status documents, not flagged `DRAFT` in that pass | Research Kernel specs: "never protects conclusions, protects the research process" | Treated as previously-verified stable specification; re-verify status only if this review's conclusions depend on a fine distinction (they do not, here) |

## `trust-engine`

| Document | Status (as found) | What it is | Eligibility |
|---|---|---|---|
| `trust_engine_architecture.md` | No document-level status field | Foundational spec: "Trust is compressed memory... Reality is the final arbiter" | **Unratified by label** — admissible only via the *independently-repeated-concept* path (see Phase 4/5) |
| `review_protocol_v1.md` | No status field | 5-step review (Outcome Review→Error Classification→Experience Assessment→Proposal Assessment→Trust Update Proposal); "Reviews never modify Trust Scores... only create structured evidence" | Same as above |
| `proposal_quality_gate_architecture.md` | No status field | EQS 0–100 → `IGNORE`/`LOG_ONLY`/`PROPOSE`/`ESCALATE`; "Even `CRITICAL` does not mean automatic trust mutation" | Same as above |
| `meta_trust_layer_architecture.md`, `meta_trust_layer_operating_model.md`, `meta_trust_layer_operating_loop_v1.md` | Self-versioned (`v0.1`, `v1`) but no `ACCEPTED`/`DRAFT` marker | Defines a **Mechanism Lifecycle**: `Candidate → Validation → Trusted → Preferred → Deprecated`; "No privileged models" / "Selection is a mechanism and receives no privileged status" | Same as above |
| `mechanism_validation_engine_architecture.md` | No status field | A validator explicitly declared not to be privileged over what it validates ("The Mechanism Validation Engine is itself a mechanism and receives no privileged status") | Same as above |
| *(archival note)* | — | **Finding in its own right**: unlike `kod` (clean `Status: Accepted` on every ADR) and `project-memory` (clean `Status:`/tiered-status headers throughout), no `trust-engine` architecture document carries a formal status marker at all. This is a real, observed difference in documentation discipline between the three repositories, not an oversight of this review. | — |

## `discovery-lab`

| Document | Status (as found) | What it is | Eligibility |
|---|---|---|---|
| `docs/ai-organization/GOVERNANCE.md` | **Status: ACCEPTED**, 2026-07-24 | The mandatory Freeze Lifecycle (`Idea→Draft→Internal Review→Adversarial Review→Reality Stress Test→Freeze Recommendation→FROZEN`) and versioning rules | **Ratified** |
| `docs/ai-organization/ARCHITECTURE-MAP.md` | "current as of Release 1.0" (tied to the accepted `RELEASE-1.0.md`) | Knowledge pipeline: `Reality → AG-002 (FROZEN 1.0) → Recovered Knowledge → AG-003 (FROZEN 1.0) → Knowledge Base` | **Ratified-adjacent**, treated as Ratified given its explicit tie to a dated, accepted release |
| `docs/adr/ADR-0001-human-authority-gates.md` | **Status: ACCEPTED** — first document in the repository to reach that status | Human Authority Gates concept | **Ratified** |
| `docs/adr/ADR-0003-reality-inbox-architecture.md` | **Status: ACCEPTED — FROZEN** | Reality Inbox: an intake pipeline (`manifests/` → `processed/`) for external material entering the lab | **Ratified** |
| `docs/adr/ADR-0004-local-drive-synced-reality-inbox.md` | **Status: ACCEPTED — DESIGN COMPLETE, AWAITING LOCAL VERIFICATION** | A sync mechanism for the intake pipeline above | **Ratified in design, not yet operational** — noted, not treated as equal to a running system |
| `docs/ai-organization/ORB/ORB-PROTOCOL.md` | **Status: DRAFT / Experimental Process** | Organizational Review Board: six mandatory questions, defined Reviewer role, procedure | Unratified |
| `docs/ai-organization/ORGANIZATION-DRAFT.md` | **Status: DRAFT — candidate organizational design, not accepted** | Draft org-design document | Unratified |
| `docs/ai-organization/HIRING-LIFECYCLE-DRAFT.md` | **Status: DRAFT — candidate lifecycle only, not adopted** | Candidate→Prototype→Probation→Trusted→Retired Role lifecycle | Unratified |
| `docs/ai-organization/FOUNDING-CHARTER.md` | **Status: DRAFT.** "Nothing in this document is final, accepted, or earned that status." | Founding charter | Unratified |
| `docs/ai-organization/MEMORY-SOURCES/MEMORY-SOURCE-PROTOCOL.md` | **Status: DRAFT / Experimental Process** | 6-stage Connection Protocol (`Lookup → Selection & Authorization → Resolution → Verification → Read-only Access → Disconnection`) for reaching external memory sources | Unratified |
| `memory/IMPORT-PROCEDURE.md` | **Status: DRAFT / EXPERIMENTAL v1** | Manual (non-automatic) import procedure | Unratified |

## `generative-discovery-engine`

| Document | Status (as found) | What it is | Eligibility |
|---|---|---|---|
| `README.md` / `STATE.md` | **Project status: DRAFT.** Active method `BLOCKED` | Whole-project status | Unratified |
| `docs/protocols/RVS-00-validation-kernel.md` (not re-read this pass; STATE.md corroborates) | `DRAFT`, currently at v0.4, `BLOCKED` pending independent review | A validation-kernel-shaped gate: "No discovery method is accepted or used operationally before surviving independent critical review and pre-registered validation" | Unratified — used only as a fifth data point for the independently-repeated "gate before acceptance" pattern (Phase 4) |

## What Phase 1 already shows, before any extraction

Of roughly 30 documents found by content search, only **eight** carry
an explicit, document-level `ACCEPTED`/`FROZEN` status:
`project-memory/adr/ADR-0001`, `kod/ADR-0003/0005/0006/0007/0009`,
`discovery-lab/GOVERNANCE.md`, `discovery-lab/ADR-0001`,
`discovery-lab/ADR-0003`. `trust-engine` contributes zero
document-level-ratified sources by label — every trust-engine document
that survives into the canonical model in Phase 5 does so only because
its concept independently repeats elsewhere, never because of its own
status marker. This asymmetry is reported as found, not smoothed over.
