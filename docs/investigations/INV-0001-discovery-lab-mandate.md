# INV-0001 — Discovery Lab Mandate: Baseline and Ecosystem Inspection

Status: DRAFT (investigation record — diagnosis only, no proposed solution)
Date: 2026-07-24
Author: Implementer session (Claude Code)

## Purpose

Before proposing what Discovery Lab should be, this investigation records
what currently exists: the repository's own baseline, and what the three
named sibling repositories (KOD, generative-discovery-engine,
project-memory) already claim as their responsibility. Per the task
constraints, this document diagnoses the situation only. Proposed mandate
variants, a recommendation, and a first experiment are in
`docs/proposals/PROP-0001-discovery-lab-boundaries.md`.

---

## 1. Discovery Lab's own baseline (as of this investigation)

From `README.md`, `CONTEXT.md`, `STATE.md`, `CHANGELOG.md`, and
`docs/notes/2026-07-24-recovery-investigation.md` (all committed on branch
`claude/recover-discovery-lab`, PR #1, still unmerged/draft):

- No architecture has been accepted. No ADRs exist.
- No previously exported "architectural draft" was ever recovered — the
  claim that one existed could not be corroborated.
- Current `STATE.md` status: `ACTIVE / BOOTSTRAP`, phase `RECOVERY`,
  blocked on purpose/scope being unconfirmed.
- `CONTEXT.md` explicitly records open questions about purpose and
  relationship to other repositories, and a non-claims section stating no
  operational or architectural fact should be assumed.

Discovery Lab therefore currently has zero committed obligations that a
mandate proposal could conflict with — the diagnosis below is entirely
about **sibling repositories' existing claims**, not about anything
Discovery Lab itself has already promised.

---

## 2. KOD — inspected via `Core/`, `Foundations/`, `Knowledge/`, `Core/Registry/`

KOD describes itself as "a research framework for building reliable
knowledge systems" and "a self-correcting research operating system," not
an AI model, programming language, or software framework
(`Core/README.md`, `CONSTITUTION.md`). Founding principle: "Reality is the
final arbiter of knowledge."

KOD already owns a complete, named knowledge lifecycle with dedicated spec
files under `Foundations/`:

- **Observation** — "a direct description of something perceived,
  measured or recorded... does not explain, does not conclude."
- **Question**, **Hypothesis** — "a proposed explanation, relationship or
  prediction that can be tested against reality."
- **Research Session** — "the primary unit of investigation inside KOD,"
  lifecycle Draft → Active Investigation → Ready for Evaluation → Under
  Review → Accepted/Rejected/Archived.
- **Investigation**, governed by the **Investigation Engine**, which
  "never evaluates conclusions," only organizes a Research Session.
- **Research Engine** — executes the KOD methodology, "require[s] attempts
  at falsification," classifies outcomes (Needs More Research / Candidate
  Principle / Verified Principle / Rejected / Archived). Its contract
  explicitly states it does NOT determine objective truth and does not
  protect any idea.
- **Research Guardian** — a compliance checker verifying the process
  (observations separated from interpretation, falsification attempts
  preserved), not a truth-decider.
- **Research Journal** — "the permanent memory of KOD," append-only,
  "nothing is deleted."
- **Excavation Protocol** — registered as a concept (`Knowledge/
  EXCAVATION_PROTOCOL.md`) but the protocol content itself is currently
  unwritten.

Overarching lifecycle (repeated in `KNOWLEDGE_LIFECYCLE.md`): Observation →
Question → Hypothesis → Prediction → Reality → Evidence → Confidence
Update → Principle → Decision → Outcome → New Observation.

`Core/ADR/ADR-0009.md` ("Multi-Agent Collaboration Architecture") defines
a **"KOD ecosystem"** of specialized agent roles (Headquarters, Research
Lab, Software Lab, Kernel Review, Applications) and states "the repository
is the Single Source of Truth for the KOD ecosystem." It also uses the
phrase "project memory" internally to describe repository-artifact
authority — a distinct usage from the external `project-memory` repository
and a candidate source of terminology confusion that any mandate document
must not deepen.

`Core/Registry/PROJECT_STATE.md`: Project status ACTIVE, Architecture
status FROZEN, Kernel status DESIGN, current sprint "Registry
Implementation," no active Research Session, 0 open hypotheses.

**Relevant finding:** KOD's Foundations layer is the formal, tracked home
for Observation, Hypothesis, Investigation, and falsification — but only
*inside* a Registry-tracked Research Session. KOD's own documents state no
allowance for pre-formal, disposable prototyping or observation-gathering
that has not yet been organized into a Research Session.

---

## 3. generative-discovery-engine (GDE) — inspected via `README.md`,
`CONTEXT.md`, `STATE.md`, `adr/`, `contracts/`, `registry/`,
`docs/protocols/RVS-00-validation-kernel.md`

GDE's stated purpose (README): "Develop and experimentally validate
methods that can systematically discover new business models, scientific
hypotheses, engineering solutions, and system architectures." Core rule:
"No discovery method is accepted or used operationally before surviving
independent critical review and pre-registered validation." `CONTEXT.md`
states GDE is explicitly "not an idea generator" — it validates *methods
of generation*, not the ideas themselves, across a four-tier ladder
(hypothesis generator → discovery method → validated method → real
business/scientific solution). GDE currently has items only in the first
two tiers.

Current `STATE.md`: project status **DRAFT**, Phase 1 (RVS validation
protocol design), RVS-00 at v0.4 DRAFT after three critical reviews, still
unfrozen, with unresolved numeric thresholds. Experiments started: 0.
Validated methods: 0. Discovery Agent role: DISABLED.

GDE already owns a complete, rigorous, but currently-unused experiment
lifecycle: Experiment Designer converts a *frozen* protocol into a
pre-registration filed in `docs/experiments/` and `registry/
EXPERIMENTS.md` before execution; results go through `docs/results/`;
verdicts feed `registry/DECISIONS.md` (human-approved) and `registry/
METHODS.md`. `RVS-00-validation-kernel.md` is a 21-section validation
protocol (operational definitions, locked data splits, sealed holdout
execution, PASS/PARTIAL/FAIL/INSUFFICIENT-DATA decision procedure,
multiplicity control, analyst independence) that gates every future
experiment.

Six agent-role contracts already exist in `contracts/`: Discovery Agent
(applies a validated method, currently disabled), Experiment Designer
(turns a frozen protocol into a pre-registered experiment), Critical
Reviewer (independently stress-tests a candidate method/protocol),
Protocol Keeper (guards against criteria drift), Reality Checker (audits
repository claims against evidence), Librarian (keeps registries coherent).

`ADR-0001` establishes the GitHub repository — not any AI chat session —
as the sole permanent source of truth, and that AI models cannot
independently accept scientific/architectural decisions; only a human can
move a decision from PROPOSED/RECORDED to ACCEPTED.

**Relevant finding:** GDE has no awareness of any sibling repository
(KOD, discovery-lab, trust-engine, project-memory are not mentioned
anywhere in it) and does not use or claim "ecosystem health," "agent
prototypes," or general "falsification testing" as concepts. It owns, in
full, the validation lifecycle for *discovery methods* specifically.

---

## 4. project-memory — already fully accessible in this session

`PROJECT_REGISTRY.md` lists five ACTIVE/DISCOVERY-status projects
governed or coordinated through Project Memory: Project Memory itself,
KOD, Trust Engine, Regime AI, and "Dinev Decor Systems" (still an unbound
placeholder). `discovery-lab` does not appear in this registry.

`CLAUDE.md` scopes the acting role in project-memory strictly as
"Implementer for Project Memory" whose mission is "implement small,
verifiable changes" to the control plane — not to conduct open-ended
cross-repo investigations.

In practice, however, `project-memory/notes/` already contains two
precedents of exactly that kind of work being done inside project-memory
by convention rather than by mandate: `2026-07-19-dinev-decor-systems-
location-check.md` (a multi-pass access/evidence investigation across
KOD, trust-engine, SketchUp-DDF, and dinevdecor.github.io) and
`2026-07-24-discovery-lab-recovery.md` (this session's own earlier
investigation into discovery-lab itself). Both are dated, append-only,
non-authoritative note files — not part of project-memory's registry or
state machinery.

**Relevant finding:** project-memory is the authoritative source for
cross-project *status* (`PROJECT_REGISTRY.md`, `PROJECT_STATE.md`), but
has no dedicated, mandated home for the *investigation work* that
produces the evidence behind status changes — that work currently lives
in `notes/` only because there was nowhere else to put it, not because
project-memory's own charter claims it.

---

## 5. Cross-cutting diagnosis

**Overlaps identified:**
- Any discovery-lab activity that validates a *method* of generating
  ideas/solutions would overlap GDE's fully-specified pre-registration →
  critical-review → decision pipeline.
- Any discovery-lab activity that formalizes an *Observation* or
  *Hypothesis* about reality, or runs a tracked multi-step *Investigation*
  toward a truth-claim, would overlap KOD's Foundations layer and its
  Research Session / Investigation Engine / Research Journal.
- The word "project memory" is already used internally by KOD (ADR-0009)
  in a sense distinct from the `project-memory` repository — a
  terminology collision risk independent of discovery-lab, but one a
  discovery-lab mandate should not add a third meaning to.

**Missing responsibility (gap) identified:**
- No repository currently claims, by mandate, a home for (a) pre-formal,
  disposable technical prototyping that hasn't yet earned a KOD Research
  Session or a GDE pre-registration, or (b) cross-repository
  ecosystem-health/evidence investigations of the kind already performed
  twice, ad hoc, inside `project-memory/notes/`.

**Conflicting ownership:** none currently exists as a formal conflict,
since discovery-lab has no accepted architecture. The risk is prospective:
if discovery-lab's future mandate reuses KOD's or GDE's terminology
(Hypothesis, Observation, Research Session, Experiment pre-registration)
for a lighter-weight process, or if it ever asserts authority over another
repository's status field, that would create a real conflict with an
existing, documented owner.

**Risk of becoming a miscellaneous dumping ground:** highest if a mandate
is adopted without an explicit expiry/graduation rule for every artifact
type it allows — the two existing investigation notes in project-memory
already show how easily "put it somewhere for now" precedents accumulate
without a lifecycle attached.

**Risk of duplicating KOD or GDE:** highest if discovery-lab's mandate
tries to be a second, lighter validation pipeline for either discovery
methods (GDE's territory) or knowledge/hypothesis claims (KOD's
territory), rather than a strictly pre-formal feeder that hands off into
those existing pipelines once something is worth formalizing.

This diagnosis is the basis for the three mandate variants proposed in
`docs/proposals/PROP-0001-discovery-lab-boundaries.md`.
