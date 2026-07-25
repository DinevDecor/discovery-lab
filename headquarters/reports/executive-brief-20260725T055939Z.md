# Ecosystem Headquarters — Executive Brief

## Overall Health
**71%**
_Formula: mean of State Visibility, Observation Cleanliness, Decision Currency, Governance Integrity (each in 0..1; unavailable sub-scores excluded, not zeroed)_

## Projects
### project-memory
- Trend: ■ Stable
- Current State: ACTIVE — Phase 1 closed — exit criteria verified
- Purpose: Project Memory is the collaboration control plane for work across Petko Dinev's projects and AI tools.
- Health Score: 100%
- Risk Level: LOW
- Confidence: HIGH
- Dependencies: INSUFFICIENT_EVIDENCE (v1.0 does not parse a dependency graph — see README Limitations)
- Last Meaningful Progress: 2026-07-16

### kod
- Trend: ■ Stable
- Current State: ACTIVE
- Purpose: INSUFFICIENT_EVIDENCE (no README purpose paragraph found)
- Health Score: 100%
- Risk Level: LOW
- Confidence: HIGH
- Dependencies: INSUFFICIENT_EVIDENCE (v1.0 does not parse a dependency graph — see README Limitations)
- Last Meaningful Progress: INSUFFICIENT_EVIDENCE (no updated_at-equivalent field found)

### discovery-lab
- Trend: ■ Stable
- Current State: ACTIVE / BOOTSTRAP — EXEC-004 executed - Ecosystem Headquarters v1.0 built and run for real (headquarters/): consumes Observation...
- Purpose: This repository was recovered/established on 2026-07-24 after a search for a previously exported "architectural draft" found no such material anywhere in the accessible local workspace. See `STATE.md` for current status, `CONTEXT.md` for what is actually known, and `docs/notes/2026-07-24-recovery-investigation.md` for the full search record.
- Health Score: 67%
- Risk Level: HIGH
- Confidence: HIGH
- Dependencies: INSUFFICIENT_EVIDENCE (v1.0 does not parse a dependency graph — see README Limitations)
- Last Meaningful Progress: 2026-07-25

### generative-discovery-engine
- Trend: ■ Stable
- Current State: BLOCKED — Resolve unresolved thresholds in RVS-00 v0.4 and obtain its independent critical review
- Purpose: INSUFFICIENT_EVIDENCE (no README purpose paragraph found)
- Health Score: 83%
- Risk Level: HIGH
- Confidence: HIGH
- Dependencies: INSUFFICIENT_EVIDENCE (v1.0 does not parse a dependency graph — see README Limitations)
- Last Meaningful Progress: INSUFFICIENT_EVIDENCE (no updated_at-equivalent field found)

### trust-engine
- Trend: ■ Stable
- Current State: UNKNOWN — no parseable state file found
- Purpose: INSUFFICIENT_EVIDENCE (no README purpose paragraph found)
- Health Score: 67%
- Risk Level: MEDIUM
- Confidence: MEDIUM
- Dependencies: INSUFFICIENT_EVIDENCE (v1.0 does not parse a dependency graph — see README Limitations)
- Last Meaningful Progress: INSUFFICIENT_EVIDENCE (no updated_at-equivalent field found)

## Most Important Recommendation
**HQ-0001**: discovery-lab: two files both claim ADR-0001

### Reason
discovery-lab's ADR directory contains 2 files that all parse as ADR-0001: ADR-0001-human-authority-gates.md, ADR-0001-migration-plan.md. An ADR ID should identify exactly one decision.

### Evidence
- discovery-lab — ADR-0001-human-authority-gates.md
- discovery-lab — ADR-0001-migration-plan.md

### Reasoning (score breakdown)
- +3 confirmed (MISMATCH-confidence evidence)
- +2 small/mechanical to finish (aligns with the guiding principle)
- +1 breadth (1 repo(s) affected, capped at 2)
- **Total score: 6**

### Expected Impact
Removes a genuine ID collision so the ADR sequence in this repository is unambiguous again.

### Dependencies
None outside the affected repository's own maintainers choosing which file to keep.

### Estimated Confidence
MISMATCH

### Estimated Risk
LOW — a rename/removal of one duplicate file, not a design change.

## Other Candidates Considered (not selected this run — shown for transparency, not as a second priority list)
- `finding-opportunity-changelog-size-discovery-lab` — discovery-lab/CHANGELOG.md is 2427 lines (INSUFFICIENT_EVIDENCE, DRAFT opportunity)
- `finding-opportunity-registry-index-discovery-lab` — discovery-lab maintains 3 separate registries with no cross-index (INSUFFICIENT_EVIDENCE, DRAFT opportunity)
- `finding-opportunity-registry-index-kod` — kod maintains 4 separate registries with no cross-index (INSUFFICIENT_EVIDENCE, DRAFT opportunity)
- `finding-opportunity-shared-safety-scanner` — 2 tools each maintain their own copy of a safety scanner (INSUFFICIENT_EVIDENCE, DRAFT opportunity)
- `finding-registry-gap-discovery-lab` — discovery-lab is not listed in project-memory/PROJECT_REGISTRY.md (MISMATCH)
- `finding-registry-gap-generative-discovery-engine` — generative-discovery-engine is not listed in project-memory/PROJECT_REGISTRY.md (MISMATCH)
- `finding-unreferenced-proposal-AG-003-knowledge-curator-walkthrough` — docs/proposals/AG-003-knowledge-curator-walkthrough is not mentioned in discovery-lab's own state file (INSUFFICIENT_EVIDENCE)
- `finding-unreferenced-proposal-AG-003-meta-theory-RI-0002` — docs/proposals/AG-003-meta-theory-RI-0002 is not mentioned in discovery-lab's own state file (INSUFFICIENT_EVIDENCE)
- `finding-unreferenced-proposal-AG-003-reality-stress-test` — docs/proposals/AG-003-reality-stress-test is not mentioned in discovery-lab's own state file (INSUFFICIENT_EVIDENCE)
- `finding-unreferenced-proposal-AGENT-001-observation-agent` — docs/proposals/AGENT-001-observation-agent is not mentioned in discovery-lab's own state file (INSUFFICIENT_EVIDENCE)
- ... and 14 more

## Critical Risks
- **discovery-lab: two files both claim ADR-0001** (discovery-lab) — discovery-lab's ADR directory contains 2 files that all parse as ADR-0001: ADR-0001-human-authority-gates.md, ADR-0001-migration-plan.md. An ADR ID should identify exactly one decision.
- **discovery-lab is not listed in project-memory/PROJECT_REGISTRY.md** (discovery-lab) — PROJECT_REGISTRY.md lists 5 project row(s), none matching 'discovery-lab'. This repository is part of the Observation Agent's fixed 5-repo scope but absent from the ecosystem's own project registry.
- **generative-discovery-engine is not listed in project-memory/PROJECT_REGISTRY.md** (generative-discovery-engine) — PROJECT_REGISTRY.md lists 5 project row(s), none matching 'generative-discovery-engine'. This repository is part of the Observation Agent's fixed 5-repo scope but absent from the ecosystem's own project registry.

## Opportunities (DRAFT — none self-approved)
- **2 tools each maintain their own copy of a safety scanner** (discovery-lab) — Each `<tool>/tests/test_safety.py` found implements the same static forbidden-pattern / write-mode detector independently (same forbidden-pattern list, same self-check discipline). DRAFT candidate: factor the detector into a small shared module every tool's test suite imports, rather than independently-maintained copies drifting apart over time.
- **kod maintains 4 separate registries with no cross-index** (kod) — kod has 4 files matching '*registry*.md' (Core/Registry/REGISTRY_README.md, Knowledge/HYPOTHESIS_REGISTRY.md, Knowledge/IDEA_REGISTRY.md, Knowledge/PRINCIPLE_REGISTRY.md) with no single index pointing between them. DRAFT candidate: a lightweight index page, at the repository's own maintainers' discretion.
- **discovery-lab maintains 3 separate registries with no cross-index** (discovery-lab) — discovery-lab has 3 files matching '*registry*.md' (docs/ai-organization/EMPLOYEE-REGISTRY.md, docs/ai-organization/MEMORY-SOURCES/MEMORY-SOURCE-REGISTRY.md, docs/ai-organization/ORB/ORB-REGISTRY.md) with no single index pointing between them. DRAFT candidate: a lightweight index page, at the repository's own maintainers' discretion.
- **discovery-lab/CHANGELOG.md is 2427 lines** (discovery-lab) — Exceeds this check's arbitrary 1000-line readability threshold. DRAFT candidate: consider splitting by year or quarter, at the repository's own maintainers' discretion — this is a readability suggestion, not a claim anything is wrong.

## Inconsistencies (recorded and classified, not fixed — the ecosystem is not reshaped to satisfy Headquarters)
### [Governance Issue] discovery-lab: two files both claim ADR-0001
- Affected artifact: discovery-lab
- Observed evidence: discovery-lab — ADR-0001-human-authority-gates.md; discovery-lab — ADR-0001-migration-plan.md
- Operational impact: Any reference to this ADR ID is ambiguous — a reader or tool cannot tell which decision is meant.
- Recommended future action: A human familiar with this repository should rename or renumber one of the colliding files.
- Category rationale: An ADR records a governance decision; two files claiming the same ID is a decision-record integrity problem, not a code defect.

### [Governance Issue] discovery-lab is not listed in project-memory/PROJECT_REGISTRY.md
- Affected artifact: discovery-lab
- Observed evidence: project-memory — PROJECT_REGISTRY.md
- Operational impact: This repository's real status is invisible to anyone consulting the ecosystem's own registry of record.
- Recommended future action: A human with authority over the registry should add or correct the missing entry.
- Category rationale: The ecosystem's own governance registry does not reflect reality.

### [Governance Issue] generative-discovery-engine is not listed in project-memory/PROJECT_REGISTRY.md
- Affected artifact: generative-discovery-engine
- Observed evidence: project-memory — PROJECT_REGISTRY.md
- Operational impact: This repository's real status is invisible to anyone consulting the ecosystem's own registry of record.
- Recommended future action: A human with authority over the registry should add or correct the missing entry.
- Category rationale: The ecosystem's own governance registry does not reflect reality.

### [Unknown] docs/proposals/AG-003-knowledge-curator-walkthrough is not mentioned in discovery-lab's own state file
- Affected artifact: discovery-lab
- Observed evidence: discovery-lab — docs/proposals/AG-003-knowledge-curator-walkthrough/
- Operational impact: Ambiguous: no operational impact if the initiative genuinely finished; a real information gap if it did not.
- Recommended future action: A human familiar with this initiative's history should confirm its real status and update STATE.md if it is in fact finished.
- Category rationale: A missing name-check in STATE.md cannot distinguish 'abandoned' from 'finished and folded into later work without a mention' — genuinely unknown from this evidence alone.

### [Unknown] docs/proposals/AG-003-meta-theory-RI-0002 is not mentioned in discovery-lab's own state file
- Affected artifact: discovery-lab
- Observed evidence: discovery-lab — docs/proposals/AG-003-meta-theory-RI-0002/
- Operational impact: Ambiguous: no operational impact if the initiative genuinely finished; a real information gap if it did not.
- Recommended future action: A human familiar with this initiative's history should confirm its real status and update STATE.md if it is in fact finished.
- Category rationale: A missing name-check in STATE.md cannot distinguish 'abandoned' from 'finished and folded into later work without a mention' — genuinely unknown from this evidence alone.

### [Unknown] docs/proposals/AG-003-reality-stress-test is not mentioned in discovery-lab's own state file
- Affected artifact: discovery-lab
- Observed evidence: discovery-lab — docs/proposals/AG-003-reality-stress-test/
- Operational impact: Ambiguous: no operational impact if the initiative genuinely finished; a real information gap if it did not.
- Recommended future action: A human familiar with this initiative's history should confirm its real status and update STATE.md if it is in fact finished.
- Category rationale: A missing name-check in STATE.md cannot distinguish 'abandoned' from 'finished and folded into later work without a mention' — genuinely unknown from this evidence alone.

### [Unknown] docs/proposals/AGENT-001-observation-agent is not mentioned in discovery-lab's own state file
- Affected artifact: discovery-lab
- Observed evidence: discovery-lab — docs/proposals/AGENT-001-observation-agent/
- Operational impact: Ambiguous: no operational impact if the initiative genuinely finished; a real information gap if it did not.
- Recommended future action: A human familiar with this initiative's history should confirm its real status and update STATE.md if it is in fact finished.
- Category rationale: A missing name-check in STATE.md cannot distinguish 'abandoned' from 'finished and folded into later work without a mention' — genuinely unknown from this evidence alone.

### [Unknown] docs/proposals/ARCH-001-independent-architecture-review is not mentioned in discovery-lab's own state file
- Affected artifact: discovery-lab
- Observed evidence: discovery-lab — docs/proposals/ARCH-001-independent-architecture-review/
- Operational impact: Ambiguous: no operational impact if the initiative genuinely finished; a real information gap if it did not.
- Recommended future action: A human familiar with this initiative's history should confirm its real status and update STATE.md if it is in fact finished.
- Category rationale: A missing name-check in STATE.md cannot distinguish 'abandoned' from 'finished and folded into later work without a mention' — genuinely unknown from this evidence alone.

### [Unknown] docs/proposals/ARCH-002-unified-coordination-model is not mentioned in discovery-lab's own state file
- Affected artifact: discovery-lab
- Observed evidence: discovery-lab — docs/proposals/ARCH-002-unified-coordination-model/
- Operational impact: Ambiguous: no operational impact if the initiative genuinely finished; a real information gap if it did not.
- Recommended future action: A human familiar with this initiative's history should confirm its real status and update STATE.md if it is in fact finished.
- Category rationale: A missing name-check in STATE.md cannot distinguish 'abandoned' from 'finished and folded into later work without a mention' — genuinely unknown from this evidence alone.

### [Unknown] docs/proposals/ARCH-003-execution-pilot-specification is not mentioned in discovery-lab's own state file
- Affected artifact: discovery-lab
- Observed evidence: discovery-lab — docs/proposals/ARCH-003-execution-pilot-specification/
- Operational impact: Ambiguous: no operational impact if the initiative genuinely finished; a real information gap if it did not.
- Recommended future action: A human familiar with this initiative's history should confirm its real status and update STATE.md if it is in fact finished.
- Category rationale: A missing name-check in STATE.md cannot distinguish 'abandoned' from 'finished and folded into later work without a mention' — genuinely unknown from this evidence alone.

### [Unknown] docs/proposals/EXEC-001-arch-003-pilot-execution is not mentioned in discovery-lab's own state file
- Affected artifact: discovery-lab
- Observed evidence: discovery-lab — docs/proposals/EXEC-001-arch-003-pilot-execution/
- Operational impact: Ambiguous: no operational impact if the initiative genuinely finished; a real information gap if it did not.
- Recommended future action: A human familiar with this initiative's history should confirm its real status and update STATE.md if it is in fact finished.
- Category rationale: A missing name-check in STATE.md cannot distinguish 'abandoned' from 'finished and folded into later work without a mention' — genuinely unknown from this evidence alone.

### [Unknown] docs/proposals/G2-control-plane-reconciliation is not mentioned in discovery-lab's own state file
- Affected artifact: discovery-lab
- Observed evidence: discovery-lab — docs/proposals/G2-control-plane-reconciliation/
- Operational impact: Ambiguous: no operational impact if the initiative genuinely finished; a real information gap if it did not.
- Recommended future action: A human familiar with this initiative's history should confirm its real status and update STATE.md if it is in fact finished.
- Category rationale: A missing name-check in STATE.md cannot distinguish 'abandoned' from 'finished and folded into later work without a mention' — genuinely unknown from this evidence alone.

### [Unknown] docs/proposals/META-001-cross-domain-validation is not mentioned in discovery-lab's own state file
- Affected artifact: discovery-lab
- Observed evidence: discovery-lab — docs/proposals/META-001-cross-domain-validation/
- Operational impact: Ambiguous: no operational impact if the initiative genuinely finished; a real information gap if it did not.
- Recommended future action: A human familiar with this initiative's history should confirm its real status and update STATE.md if it is in fact finished.
- Category rationale: A missing name-check in STATE.md cannot distinguish 'abandoned' from 'finished and folded into later work without a mention' — genuinely unknown from this evidence alone.

### [Unknown] docs/proposals/PROP-0001-ratification-package is not mentioned in discovery-lab's own state file
- Affected artifact: discovery-lab
- Observed evidence: discovery-lab — docs/proposals/PROP-0001-ratification-package/
- Operational impact: Ambiguous: no operational impact if the initiative genuinely finished; a real information gap if it did not.
- Recommended future action: A human familiar with this initiative's history should confirm its real status and update STATE.md if it is in fact finished.
- Category rationale: A missing name-check in STATE.md cannot distinguish 'abandoned' from 'finished and folded into later work without a mention' — genuinely unknown from this evidence alone.

### [Unknown] docs/proposals/STRATEGIC-001-close-evidence-loop is not mentioned in discovery-lab's own state file
- Affected artifact: discovery-lab
- Observed evidence: discovery-lab — docs/proposals/STRATEGIC-001-close-evidence-loop/
- Operational impact: Ambiguous: no operational impact if the initiative genuinely finished; a real information gap if it did not.
- Recommended future action: A human familiar with this initiative's history should confirm its real status and update STATE.md if it is in fact finished.
- Category rationale: A missing name-check in STATE.md cannot distinguish 'abandoned' from 'finished and folded into later work without a mention' — genuinely unknown from this evidence alone.

## Human Decisions Required
- templates/TASK_TEMPLATE.md is a 0-byte file
- docs/specs/WORKFLOW.md is a 0-byte file
- PROJECT_REGISTRY.md: row for 'Project Memory' claims an ACTIVE-shaped status with no in-row citation
- PROJECT_REGISTRY.md: row for 'KOD' claims an ACTIVE-shaped status with no in-row citation
- PROJECT_REGISTRY.md: row for 'Trust Engine' claims an ACTIVE-shaped status with no in-row citation
- PROJECT_REGISTRY.md: row for 'Regime AI' claims an ACTIVE-shaped status with no in-row citation
- PROJECT_REGISTRY.md: row for 'Dinev Decor Systems' claims an ACTIVE-shaped status with no in-row citation
- PROJECT_STATE.md declares date 2026-07-16, but other files in project-memory were modified as recently as 2026-07-24
- ROS_ARCHITECTURE.md is a 0-byte file
- Knowledge/EXCAVATION_PROTOCOL.md is a 0-byte file
- Knowledge/.gitkeep is a 0-byte file
- Products/.gitkeep is a 0-byte file
- Core/IDENTITY.md is a 0-byte file
- Core/WORKFLOW.md is a 0-byte file
- Core/.gitkeep is a 0-byte file
- Core/Registry/TRACEABILITY.md is a 0-byte file
- Infrastructure/.gitkeep is a 0-byte file
- Infrastructure/python/kod/__init__.py is a 0-byte file
- Infrastructure/python/kod/validator.py is a 0-byte file
- Infrastructure/python/kod/services/__init__.py is a 0-byte file
- Infrastructure/python/kod/parsers/__init__.py is a 0-byte file
- Infrastructure/python/kod/models/__init__.py is a 0-byte file
- Infrastructure/python/kod/models/project_state.py is a 0-byte file
- Infrastructure/python/tests/__init__.py is a 0-byte file
- reality-inbox/processed/oneDay-6/20251117/diary.txt is a 0-byte file
- reality-inbox/processed/oneDay-6/20251101/diary.txt is a 0-byte file
- reality-inbox/processed/oneDay-6/20251118/diary.txt is a 0-byte file
- reality-inbox/processed/oneDay-6/20251212/diary.txt is a 0-byte file
- reality-inbox/processed/oneDay-6/20260111/diary.txt is a 0-byte file
- reality-inbox/processed/oneDay-6/20260212/diary.txt is a 0-byte file
- docs/ai-organization/employees/AG-002-discovery-archaeologist/STATUS.yaml declares runs_completed=7, but docs/ai-organization/employees/AG-002-discovery-archaeologist/HISTORY.md records 5 run entr(y/ies)
- docs/ai-organization/employees/AG-003-knowledge-curator/STATUS.yaml declares runs_completed=3, but docs/ai-organization/employees/AG-003-knowledge-curator/HISTORY.md records 0 run entr(y/ies)
- HQ-0001: discovery-lab: two files both claim ADR-0001

## Trend (vs previous execution)
- Overall Health: stable (+0.0 pts vs previous execution)

## Recommendation Evaluation
- INSUFFICIENT_EVIDENCE (no recommendation-decisions.json entries recorded yet)
- Total tracked recommendations: 1

## Observation Agent Coverage
- Scanned: project-memory, kod, discovery-lab, generative-discovery-engine, trust-engine
- Skipped: (none)

## Metrics
- **State Visibility**: 4/5 repos (80%) — _(# configured repos with >=2 parsed state fields) / (# configured repos)_
- **Observation Cleanliness**: 25% (24 MISMATCH of 32) — _1 - (MISMATCH / total observations) from the latest Observation Agent report_
- **Decision Currency**: 100% (0/6 entries overdue for a decision) — _1 - (# PROPOSED entries older than 3d / total entries)_
- **Governance Integrity**: 80% (3 confirmed governance findings) — _1 - (# MISMATCH-confidence drift findings / # drift findings surfaced this run)_
- **Observation Coverage**: 5/5 repos (100%) — _(# repos SCANned in the latest execution log) / (# configured repos)_
- **Recommendation Backlog**: 6 — _count of RECOMMENDATION-LEDGER.md entries with status: PROPOSED_
- **Decision Backlog**: 0 — _count of PROPOSED entries with date_proposed more than 3 day(s) before this run_

_Guiding principle: "The ecosystem grows by finishing high-value work, not by maximizing the number of active ideas." Headquarters is advisory only — see CONTRACT.md. It has not modified any repository._
