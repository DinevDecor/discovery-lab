# Deliverable 2 — Component Matrix

Per `ARCH-002` Phase 2 (extraction) and Phase 3 (matrix). Only the
eight named components from the task are used —
no new component names are introduced. For each cell, facts only:
Responsibilities / Inputs / Outputs / Lifecycle / Ownership /
Dependencies / Human interaction / AI interaction, drawn only from
documents listed in `1-ARCHITECTURE-INVENTORY.md`.

## Summary matrix

| Component | `project-memory` | `kod` | `discovery-lab` | `trust-engine` | Verdict |
|---|---|---|---|---|---|
| **Scheduler** | Absent | Absent | Absent | Absent | **Absent everywhere** — no repository names or designs a time/priority-based task scheduler |
| **Supervisor** | `Kernel`-as-formal-gate named explicitly as **Stable Core** (Ratified) | Kernel Review `PASS`/`BLOCKED` gate, `ADR-0009` (Ratified) | ORB (`DRAFT`) + Adversarial Review stage of `GOVERNANCE.md` (Ratified) | Proposal Quality Gate (unratified by label) | **Present in all four**, ratified in three of four, under different names |
| **Runtime** | Absent as a named component | `RUNTIME_ARCHITECTURE.md` — but a *reasoning/data* pipeline (`KnowledgeObject→...→Trust Engine`), not a *task-execution* runtime; `Execution Layer` explicitly `NOT_STARTED` per `PROJECT_STATE.md` | Absent as a named component | Absent as a named component | **Named in only one repo, and even there it does not mean task execution** — see Phase 6 |
| **Dispatch** | `contracts/dispatcher.md` (`PILOT`) — literal Dispatcher | Absent as a named component | Reality Inbox intake (`ADR-0003`, Ratified) and Memory-Source Connection Protocol (`DRAFT`) — intake/routing, not task dispatch | Absent as a named component | **Two different meanings of "dispatch" in two repos** (work-item routing vs. material intake), neither in `kod` or `trust-engine` |
| **Queue** | Absent as an implemented structure (`PROJECT_STATE`/`PROJECT_REGISTRY` are state, not a queue) | Absent | Reality Inbox (`manifests/` → `processed/`), Ratified, file-based, actually operating | Proposal Quality Gate's four tiers (`IGNORE`/`LOG_ONLY`/`PROPOSE`/`ESCALATE`) are queue-shaped but exist only as a design, not a working structure | **Only `discovery-lab` has a real, ratified, operating queue** |
| **Event** | Absent | Absent (pipeline is synchronous, not event-driven) | Absent | Absent | **Absent everywhere** — no event bus, event log, or pub-sub concept anywhere in the ecosystem |
| **Approval** | Human final authority (Stable Core, Ratified); Dispatcher explicitly does not decide, only routes | `PASS`/`BLOCKED` Kernel gate before human merge (Ratified) | `ADR-0001` Human Authority Gates (Ratified); Freeze Recommendation requires explicit human step (`GOVERNANCE.md`, Ratified) | "Even `CRITICAL` does not mean automatic trust mutation" — repeated in every trust-engine document read, though none individually ratified | **Present, and the single strongest convergence in the whole ecosystem** — ratified in three of four repos, uniformly stated in the fourth |
| **Planning** | Ad hoc only: `PROJECT_STATE.md`'s own `next_action` field | Ad hoc only: `ROADMAP.md` (versions marked `Planned`, not a mechanism) | Ad hoc only: `STATE.md`'s `next_action` field | Ad hoc only: no equivalent found | **No architectural Planning component anywhere** — every repo does forward planning as informal prose in a state file or roadmap, never as a designed mechanism |

## Per-component extraction detail

### Supervisor / Approval (treated together — every source ties them to the same gate)

- **Responsibilities**: check a proposed change/decision against fixed
  criteria; return a binary or small enumerated verdict; never itself
  produce or approve the underlying work.
- **Inputs**: a proposed artifact/decision (`kod`: a Draft ADR or
  code change; `discovery-lab`: a Freeze Recommendation; `trust-engine`:
  a candidate trust-update proposal; `project-memory`: any artifact
  awaiting merge).
- **Outputs**: `kod` — `PASS`/`BLOCKED` plus criterion; `discovery-lab`
  — the ORB's four escalation categories (per `docs/ai-organization/
  ORB/ORB-PROTOCOL.md`) or a Freeze Recommendation verdict;
  `trust-engine` — `IGNORE`/`LOG_ONLY`/`PROPOSE`/`ESCALATE`;
  `project-memory` — the gate does not itself decide, it hands off to
  the next human step.
- **Lifecycle**: none of the four treat this as a stateful, evolving
  object — it is a check performed once per proposal, not a tracked
  entity with its own status field.
- **Ownership**: `kod` — "may be run by any model, ideally not the
  artifact's author" (`ADR-0009`); `discovery-lab` — a named,
  restricted Reviewer role (`ORB-PROTOCOL.md` §"Who may conduct a
  review"); `trust-engine` — unspecified actor; `project-memory` —
  unspecified actor, but explicitly "not the human" for the mechanical
  gate step.
- **Dependencies**: a proposal must already exist; none of the four
  gates can originate work.
- **Human interaction**: in every repo, the gate's output is
  *input to* a human decision, never a substitute for one — this is
  stated explicitly, not implied, in `trust-engine`
  (`proposal_quality_gate_architecture.md`: "Even `CRITICAL` does not
  mean automatic trust mutation") and in `project-memory`'s Stable
  Core ("само човекът приема и merge-ва" — only the human accepts and
  merges).
- **AI interaction**: an AI role may run the gate itself (`kod`
  explicitly allows this); no repository allows an AI role to be the
  final authority the gate's output feeds into.

### Dispatch (`project-memory`'s literal Dispatcher vs. `discovery-lab`'s Reality Inbox — extracted separately, not merged, per Phase 2's "facts only" rule)

**`project-memory/contracts/dispatcher.md`** (`PILOT`):
- Responsibilities: accept one human request; classify it as exactly
  one type (`ARCHITECTURE`, and others in the same enumeration);
  select the workflow, role, and repository context it requires; state
  the single next step. Does not perform the specialized work.
- Inputs: free-form human request, `PROJECT_STATE`, `PROJECT_REGISTRY`,
  project-specific state/context, or an existing artifact; explicitly
  handles "Продължи работата" ("continue the work") by reading
  `next_action` from the applicable `PROJECT_STATE`.
- Outputs: a Task Brief.
- Lifecycle: none — stateless per invocation.
- Ownership: Petko Dinev (contract owner); executor is model-agnostic.
- Dependencies: `PROJECT_STATE`/`PROJECT_REGISTRY` must exist and be
  current.
- Human interaction: triggered by a human request; returns to a human
  (or hands off per the Task Brief) — it does not act autonomously.
- AI interaction: is itself executable by any AI model, by design
  (role, not a fixed model).

**`discovery-lab/docs/adr/ADR-0003-reality-inbox-architecture.md`**
(`ACCEPTED — FROZEN`):
- Responsibilities: accept external material into `reality-inbox/`,
  produce a manifest, move processed items to `processed/`.
- Inputs: files dropped into the inbox (per
  `📥 DROP HERE/README.md`).
- Outputs: `manifests/RI-000N.md`, then a moved/archived artifact.
- Lifecycle: a manifest has its own state (see `INDEX.md`).
- Ownership: not individually named; governed by the ADR.
- Dependencies: none upstream — this is the ecosystem's actual
  external-material entry point.
- Human/AI interaction: both may drop material in; downstream
  processing (`AG-002`) is AI-run, gated by the same Human Authority
  Gates as everything else (`ADR-0001`).

**Reading the two side by side**: they are not the same component
under different names. One dispatches *work* (a human's request,
routed to a role); the other dispatches *material* (external content,
routed into a recovery pipeline). Both share the same underlying
shape — receive, classify, route, do not perform the specialized task
yourself — but conflating them into one "Dispatch" component would
overstate what the evidence shows. See `3-MERGE-ANALYSIS.md`.
