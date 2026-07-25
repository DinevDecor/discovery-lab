# Deliverable 3 — Merge Analysis

Per `ARCH-002` Phase 4. For every candidate pair/cluster found in
`2-COMPONENT-MATRIX.md`: same, differently named, overlapping,
contradictory, or mergeable. No new concepts introduced.

## Same concept, different names — mergeable directly

**The formal gate before acceptance** (`Supervisor`/`Approval` rows).
`kod`'s Kernel Review (`PASS`/`BLOCKED`), `project-memory`'s
Kernel-as-formal-gate-concept (named explicitly as Stable Core),
`discovery-lab`'s Adversarial Review stage of the Freeze Lifecycle, and
`trust-engine`'s Proposal Quality Gate are the same mechanism: a
check, run against a fixed rule set, that produces a small enumerated
verdict and is never itself the final authority. Four different
vocabularies (`PASS`/`BLOCKED`; "Kernel"; "Adversarial Review";
`IGNORE`/`LOG_ONLY`/`PROPOSE`/`ESCALATE`) describing one mechanism.
**Mergeable as one canonical concept: the Formal Gate.**

**Human final authority over the gate's output.** Stated as its own
invariant in `project-memory` (Stable Core), enacted structurally in
`kod` (human merges after `PASS`), `discovery-lab`
(`ADR-0001-human-authority-gates.md`), and `trust-engine` ("even
`CRITICAL` does not mean automatic trust mutation"). Not four separate
rules — one rule, independently enforced four times.
**Mergeable as one canonical concept: Human Final Authority.**

## Differently named, and genuinely different underneath — do not merge

**`project-memory`'s Dispatcher vs. `discovery-lab`'s Reality Inbox.**
Both "receive something, classify it, route it, don't perform the
work yourself." But one dispatches *human work requests* to a
*role/workflow*; the other intakes *external material* into a
*recovery pipeline*. Merging them into a single "Dispatch" component
would erase a real distinction the evidence supports keeping: work
dispatch and material intake are not proven to be the same problem
just because they share a shape. **Keep separate. Note the shared
shape as a pattern, not a component** (see
`4-UNIFIED-COORDINATION-MODEL.md`).

**`kod`'s `RUNTIME_ARCHITECTURE.md` vs. what "runtime" means in the
other three repos.** `kod` uses "runtime" for a reasoning/data pipeline
(`KnowledgeObject → KnowledgeGraph → ReasoningEngine → ...`). No other
repository has anything called "runtime," and none of them mean
"pipeline that processes knowledge objects" when discussing
coordination — they mean (when they mean anything close to it) "the
thing that would carry out an approved action," which `kod` itself
admits does not exist yet (`Execution Layer: NOT_STARTED`,
`PROJECT_STATE.md`). **These are not the same concept under one name —
they are two different concepts that happen to share the English word
"runtime."** Treating `kod`'s Runtime Architecture as if it answered
the ecosystem's execution-layer gap would be a real error; flagged
here so it is not made in Phase 5 or Phase 6.

## Overlapping — partial merge only

**Lifecycle-with-named-stages, human-gated at the top.**
`trust-engine`'s Mechanism Lifecycle (`Candidate → Validation →
Trusted → Preferred → Deprecated`), `discovery-lab`'s Role Freeze
Lifecycle (`Idea → Draft → Internal Review → Adversarial Review →
Reality Stress Test → Freeze Recommendation → FROZEN`, Ratified via
`GOVERNANCE.md`) and its `AG-003` Knowledge Object two-track lifecycle
(`status`: Draft→Candidate Principle→Validated Principle→Core
Principle), and `kod`'s `AP6`/`AP7` (architecture itself evolves,
"even the architecture of KOD itself remains open to revision"). These
overlap in shape (staged promotion, human-gated, revision permitted)
but differ in what they gate — a *mechanism's* trust, a *Role's*
production status, a *piece of knowledge's* maturity, and *the
architecture itself*. **Merge the shape (staged, human-gated,
revisable promotion) as a canonical pattern; do not merge the specific
stage names — they are legitimately domain-specific.**

## No contradictions found

Checked directly, not assumed: does any repository's Formal Gate ever
grant itself the power to also be the final authority? No — `kod`'s
`ADR-0009` explicitly separates Kernel from Reviewer from human merge;
`trust-engine`'s quality gate explicitly denies itself automatic
mutation power even at its highest severity tier; `discovery-lab`'s
ORB is explicitly barred from certain actions
(`ORB-PROTOCOL.md` §"Boundaries this procedure must never cross");
`project-memory`'s Stable Core states human final authority as an
invariant, not a default that could be locally overridden. **Zero
contradictions found between the four repositories' Approval/Human
Final Authority concepts.**

## Cannot be merged — insufficient shared evidence

`discovery-lab`'s Queue (Reality Inbox, real and operating) has no
counterpart anywhere else in the ecosystem to merge with. `kod`'s
`PROJECT_STATE.md` and `project-memory`'s `PROJECT_STATE.md`/
`PROJECT_REGISTRY.md` are state files with a similar *purpose*
(tell a reader or a dispatcher what's current) but neither documents
the other's schema or existence — parallel invention, not
convergence; too little evidence to claim either "same" or
"contradicts." Left unmerged, named as parallel invention only.

## What Phase 4 leaves for Phase 5

Two components merge cleanly (Formal Gate, Human Final Authority) and
qualify as canonical under the task's ratified-or-repeated-concept
rule — both are ratified in at least two of the four repositories
*and* independently repeated in all four. One pattern (staged,
human-gated, revisable lifecycle) merges at the shape level only. One
apparent match (Dispatch vs. Reality Inbox) is kept deliberately
unmerged. One apparent match ("Runtime") is flagged as a false
cognate, not a shared concept.
