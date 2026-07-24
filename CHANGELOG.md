# Changelog

## 2026-07-24

- Verified remote access to `DinevDecor/discovery-lab` (previously untested;
  distinct from the earlier KOD/trust-engine/SketchUp-DDF access check).
- Confirmed the remote repository contained only an auto-generated
  `README.md` ("# discovery-lab") and a single "Initial commit" — no other
  branches, pull requests, issues, or tags.
- Searched the local workspace (the `project-memory` repository in full,
  `/home/user`, `/workspace`, `/root`, and recently modified files) for a
  previously exported "architectural draft" for discovery-lab. None was
  found.
- Established baseline repository structure (`README.md`, `CONTEXT.md`,
  `STATE.md`, `CHANGELOG.md`, `docs/notes/`) documenting confirmed facts
  only, without inventing architecture.
- Added a provenance/recovery note
  (`docs/notes/2026-07-24-recovery-investigation.md`) recording the search
  performed and its outcome.
- Opened draft PR #1 (`claude/recover-discovery-lab` → `main`) with this
  work. A companion investigation note recording the same findings from
  the `project-memory` side is at
  `project-memory/notes/2026-07-24-discovery-lab-recovery.md`.

## 2026-07-24 (mandate drafting)

- Inspected KOD (`Core/`, `Foundations/`, `Knowledge/`, `Core/Registry/`)
  and generative-discovery-engine (`README`, `CONTEXT`, `STATE`, `adr/`,
  `contracts/`, `registry/`, `docs/protocols/RVS-00-validation-kernel.md`)
  to identify what each already owns, to avoid duplicating either.
- Recorded the inspection and diagnosis (overlaps, gaps, ownership risks,
  dumping-ground risk) in
  `docs/investigations/INV-0001-discovery-lab-mandate.md`.
- Proposed three mandate variants — Experiment Laboratory, Ecosystem
  Observatory, Combined Lab + Observatory — with allowed/prohibited
  artifacts, lifecycle, relationships, advantages, and failure modes for
  each, in `docs/proposals/PROP-0001-discovery-lab-boundaries.md`.
- Recommended (not accepted) the Ecosystem Observatory variant, on the
  grounds that it is the only variant with directly observed precedent
  (this session's own recovery investigation and the 2026-07-19 Dinev
  Decor evidence check, both previously done ad hoc in
  `project-memory/notes/`).
- Proposed a smallest-possible first experiment ("Ecosystem Health Review
  v0.1", not yet run) to test the recommended mandate before committing
  further.
- Updated `STATE.md` to reflect `MANDATE_DRAFTING` phase. No ADR was
  created or accepted; no architecture was invented.

## 2026-07-24 (independent architecture passes)

- Ran three completely independent, isolated, read-only architecture
  reviews — one each over KOD, generative-discovery-engine, and
  trust-engine — each answering a fixed 8-question diagnostic with no
  visibility into the other two passes or into prior discovery-lab work.
  Recorded verbatim, plus a fourth cross-repository synthesis pass run
  only afterward, in
  `docs/investigations/INV-0002-independent-architecture-passes.md`.
- The trust-engine pass found a previously undocumented gap: roughly
  60+ architecture/spec documents but only 15 implemented Python
  modules, with entire subsystems (Mechanism Trust Layer, Meta Trust
  Layer) fully specified but never built.
- Rewrote `docs/proposals/PROP-0001-discovery-lab-boundaries.md` (revision
  2) with three variants that are genuinely distinct in entry criteria,
  exit criteria, deletion mechanics, and governance burden — not
  cosmetic renamings of the same design — each specifying its
  relationship to KOD, generative-discovery-engine, trust-engine, and
  project-memory individually.
- Recommendation unchanged in substance (Ecosystem Observatory, still
  not accepted) but now backed by the trust-engine gap as a live example
  of the role's value, with explicit reasons Variants A and C were not
  selected and a list of assumptions still requiring validation.
- Added a full information-flow map (Reality → Observation → Candidate
  investigation → Experiment → Evidence → Review/falsification →
  Decision → Graduation/rejection/deletion → Destination repository)
  with per-transfer source/destination/artifact/approval-gate/provenance
  specifications, and marked the Experiment stage explicitly dormant
  under the recommended variant.
- Defined "Ecosystem Health Review v0.1" as the proposed first
  experiment — fixed scope, frozen review criteria, a defined output
  schema and PASS/PARTIAL/FAIL/INSUFFICIENT rubric, a stop rule, and
  named conditions under which its result would invalidate the
  recommended mandate. Not implemented; no agent created; no recurring
  monitoring scheduled.
- Ran a self-critique pass (hidden duplication, vague ownership,
  irreversible scope growth, circular information flows, missing
  deletion rules, unsupported recommendations) and fixed two findings:
  added a terminology disambiguation note against KOD's "Investigation"
  concept, and added an `archive/` consolidation path to Variant B's
  deletion rules to bound long-term accumulation. Still no ADR created
  or accepted; still no architecture invented or implemented.

## 2026-07-24 (adversarial review, vFinal)

- Ran an independent, deliberately destructive architecture review of
  `docs/proposals/PROP-0001-discovery-lab-boundaries.md`, instructed to
  attack the design rather than defend it. Full record, including risks
  as originally found before any fix, in the new "Adversarial Review —
  vFinal" section of that document.
- Evaluated three candidate additions and integrated all three, minimally
  and not implemented:
  - **Principle 0** ("Discovery Lab never creates truth... only
    observes, compares, identifies inconsistencies, and proposes next
    steps") — added above the Shared ground rules as the frame the rest
    of the document derives from, reworded from the candidate text which
    overclaimed a dormant capability (Experiment).
  - **Recommendation quality** — defined a Recommendation Ledger
    interface (not implemented) so "do receiving repositories act on
    routed proposals?" can eventually be checked instead of staying
    permanently untestable. Named the metric `acceptance_rate`, not
    "precision" — Discovery Lab has no correctness oracle and Principle
    0 forbids claiming one. Added a `PENDING_NO_RESPONSE` status so
    silence is never conflated with rejection.
  - **Evidence Coverage** — added as a defined-but-unformulated field in
    the Ecosystem Health Review v0.1 output schema, with no formula
    invented.
- Attempted to break the recommended Variant B and found, described, then
  fixed 6 risks: (1) criterion C2 smuggled interpretation of another
  team's intent into a claimed read-only check — narrowed to require a
  citable planning artifact; (2) Variant B's C1–C3 checks were never
  checked against KOD's Research Guardian specifically (only against the
  Research Engine) — added an explicit non-duplication boundary; (3) the
  "no repository added mid-review" rule bounded a single review but not
  a series of them — added a scope-stability rule across future review
  generations; (4) the archive-consolidation rule used non-binding
  language — replaced with a concrete 12-month/20-report trigger; (5)
  adding two new self-tracking structures at once is a real, if mild,
  governance-creep risk — named explicitly, not hidden; (6) recommendation
  tracking could have inferred REJECTED from silence — fixed via the
  `PENDING_NO_RESPONSE` status.
- Merge gate verdict: **APPROVE WITH MINOR CHANGES**. All fixes applied
  in place, next to the rule each corrects. No new architectural
  dependency introduced; no responsibility added beyond what Variant B
  already claimed; still strictly read-only and proposal-only. No ADR
  created or accepted.

## 2026-07-24 (DL-0001)

- Recorded the first entry in a new "DL-" investigation series (distinct
  from the fact-checking "INV-" series): `docs/investigations/
  DL-0001-ecosystem-purpose-shift.md` — a candidate hypothesis, provided
  directly by the requester with its origin quoted verbatim, that KOD,
  Trust Engine, Discovery Lab, project-memory, and
  generative-discovery-engine may share a common terminal purpose
  (improving decisions) for which each repository's own primary output is
  instrumental rather than terminal.
- Recorded explicitly as CANDIDATE, not accepted, not a KOD Hypothesis
  object, not entered in any registry outside discovery-lab. Documented
  arguments for and against (grounded only in citations already gathered
  in `INV-0002`), potential impact if verified or falsified, and a
  proposed verification experiment (DL-0001-EXP-1) that is defined but
  not run.
- No other repository (KOD, generative-discovery-engine, trust-engine,
  project-memory) was read, modified, or notified. `PROP-0001`'s
  recommendation is explicitly unaffected by this document.

## 2026-07-24 (AI Organization prototype)

- Created `docs/ai-organization/`, a bounded DRAFT/EXPERIMENTAL/NOT
  ADOPTED prototype living inside `discovery-lab` — explicitly not a new
  GitHub repository. Four organization-level documents
  (`README.md`, `ORGANIZATION-DRAFT.md`, `EMPLOYEE-REGISTRY.md`,
  `HIRING-LIFECYCLE-DRAFT.md`) establish a candidate organizational
  model: a permanent, versioned **Role** (organizational position) is
  defined independently of whichever **Executor** currently performs it
  ("Role is stable. Executor is replaceable.").
- Fully populated the first Role, `AG-001 — Repository Observer` v0.1,
  across all 11 required documents (`CONTRACT.md`, `ROLE.md`,
  `INPUTS.md`, `OUTPUTS.md`, `LIMITATIONS.md`, `CHECKLIST.md`,
  `METRICS.md`, `RUN-PROTOCOL.md`, `PROMPT.md`, `STATUS.yaml`,
  `HISTORY.md`) at `docs/ai-organization/employees/
  AG-001-repository-observer/`. Mission: "Observe changes. Report
  evidence. Do not decide." — read-only, no recommendations, no
  architectural interpretation, escalates to `UNKNOWN` /
  `INSUFFICIENT ACCESS` rather than guessing.
- Added an explicit terminology disambiguation (in `README.md` and
  `ROLE.md`) clarifying that AG-001's "Observation Report" /
  "Observations" use the plain-English sense of the word, and are
  **not** KOD's Knowledge Domain "Observation" object or trust-engine's
  "Observation Memory" — found and fixed as part of the required
  pre-commit check against `PROP-0001`'s ground rule 1, following the
  same pattern already used for "Investigation" (`PROP-0001`) and
  "Hypothesis" (`DL-0001`).
- No aggregate trust score, no invented metric values, and no candidate
  promotion thresholds were defined in v0.1 — `METRICS.md` defines nine
  named metrics as an interface only, with zero run data to populate
  them (`runs_completed: 0`). No Senior/Architect lifecycle tier was
  added, for lack of demonstrated need.
- No code, no automation workflow, and no specific AI model is
  referenced anywhere in the architecture (model names appear only as
  illustrative examples of interchangeable executors, in explanatory
  prose, never inside the actual role definition or prompt template).
- No other repository (KOD, generative-discovery-engine, trust-engine,
  project-memory) was read, modified, or notified. No new GitHub
  repository was created; `add_repo` was not used.

## 2026-07-24 (AG-001 RUN-0001)

- Executed AG-001 Repository Observer's first real run, `RUN-0001`,
  following `PROMPT.md` / `RUN-PROTOCOL.md` / `CHECKLIST.md` /
  `OUTPUTS.md` exactly. Scope: `discovery-lab` only, read-only.
  Baseline: commit `dff7810`. Target state: branch
  `claude/ai-org-ag-001-prototype` at commit `bfaa17f`.
- Report at `docs/ai-organization/employees/AG-001-repository-observer/
  runs/RUN-0001-observation-report.md`: 5 confirmed changes, 6
  current-state observations, 3 structural signals (including two
  broken relative-path references discovered in AG-001's own
  `HISTORY.md`, and a field mismatch between `INPUTS.md`/`PROMPT.md`
  and `OUTPUTS.md`'s fixed Run Metadata template), 1 `INSUFFICIENT
  ACCESS` item, 2 `UNKNOWN` items. No recommendations or conclusions
  given.
- Per `RUN-PROTOCOL.md` step 8, exactly one line was appended to
  `HISTORY.md` recording the run — no other file in AG-001's folder was
  touched. `STATUS.yaml` was deliberately not updated; the role's status
  remains `prototype` pending independent review.

## 2026-07-24 (ORB — Organizational Review Board)

- Created `docs/ai-organization/ORB/` — an organizational **process**,
  not a new employee: no Employee ID, no entry in
  `EMPLOYEE-REGISTRY.md`, no `CONTRACT.md`, no assigned Executor.
- Added `ORB-PROTOCOL.md`, formalizing the "independent review of a
  sample of reports" step `HIRING-LIFECYCLE-DRAFT.md` already requires
  for every stage transition, without modifying that document. Defines
  who may act as Reviewer (must not be the Executor of the reviewed
  run), what ORB does and does not review (conduct against an existing
  contract, never the contract's own design), and hard boundaries: an
  ORB Review never edits a reviewed Role's files or `STATUS.yaml`, never
  changes governance, is not automated, and never itself decides a
  status change — only a human does, per `HIRING-LIFECYCLE-DRAFT.md`.
- Added `ORB-REVIEW-TEMPLATE.md`, requiring every review to answer six
  fixed questions (contract honored; authority exceeded; unsupported
  claims; real value delivered; new organizational lesson; whether a
  separate Investigation is needed instead of a direct change), each
  with a fixed verdict vocabulary and mandatory evidence, plus a Review
  Boundary Statement mirroring AG-001's own Observer Boundary Statement.
- Added `ORB-REGISTRY.md`, an empty append-only index (0 reviews
  conducted) — no review of AG-001 or `RUN-0001` was performed as part
  of this change, per instruction.
- Added a disambiguation note distinguishing "ORB Review" from KOD's
  "Under Review" Research Session stage and generative-discovery-
  engine's "Critical Review" — a third, distinct scope (AI employee
  conduct, not knowledge claims or discovery methods).
- No changes to AG-001, `EMPLOYEE-REGISTRY.md`, `HIRING-LIFECYCLE-
  DRAFT.md`, `ORGANIZATION-DRAFT.md`, or any other governance document.
  No automation introduced. No other repository read, modified, or
  notified.

## 2026-07-24 (FP-0001 — Founding Charter)

- Added `docs/ai-organization/FOUNDING-CHARTER.md` (FP-0001, v0.1),
  **Status: DRAFT**, deliberately not the word KOD's own foundational
  document uses for itself — the distinction is explained in the
  document's own opening section. Creates no new governance layer:
  every one of its 9 sections restates a principle already established
  in `ORGANIZATION-DRAFT.md`, `HIRING-LIFECYCLE-DRAFT.md`, or
  `PROP-0001`, labeled explicitly as a "Candidate principle," or states
  a design intent (Purpose) distinct from `DL-0001`'s still-unverified
  hypothesis.
- Sections: Purpose, Identity, Evidence, Evolution (a named six-stage
  change pipeline — Observation → Investigation → Experiment → Review →
  Decision → Adoption, never by direct edit), Boundaries, Independence,
  Memory, Promotion, Human Authority, and a mandatory Open Questions
  section (5 questions recorded, none resolved prematurely).
- Ran the required self-critical review after writing the document and
  recorded — without fixing any of them directly, per instruction — 6
  Candidate Conflicts: (1) four of Discovery Lab's five reserved terms
  (`Observation`, `Experiment`, `Review`, `Evidence`) used as section
  titles without the disambiguation notes given to every earlier
  instance of this exact collision; (2) Section 4's "Review" stage is a
  fourth, unreconciled sense of the word alongside KOD's, GDE's, and
  ORB's; (3) Section 3's evidence standard is not satisfied by how the
  lifecycle stages, ORB's six questions, or AG-001's metric names were
  actually produced (design reasoning, not gathered evidence); (4)
  Section 6's independence standard goes further than `RUN-0001`
  actually practiced; (5) Section 4's "Experiment" stage names a
  capability `PROP-0001` marks as currently dormant; (6) Section 8's use
  of "Trust" thematically echoes trust-engine's namesake concept.
- All relative-path references mechanically verified before commit;
  two ambiguous bare-filename references (to AG-001's `CONTRACT.md` and
  `METRICS.md`) were tightened to full relative paths as a mechanical
  fix, separate from the substantive Candidate Conflicts above.
- No new governance layer, no new employee, no automation introduced.
  No other repository read, modified, or notified.

## 2026-07-24 (PROP-0002 — Discovery Intake System)

- Added `docs/proposals/PROP-0002-discovery-intake-system.md` (v0.1,
  DRAFT, not implemented). Explicitly variant-agnostic with respect to
  `PROP-0001`'s still-unaccepted mandate — Intake defines how raw
  material enters, not what happens to it downstream.
- **Specification:** Intake as a defined capture point, explicitly not
  a new employee/Role — no Employee ID, no `CONTRACT.md`. Preserves
  input verbatim; never classifies, researches, or edits meaning.
- **Ledger:** immutable append-only record (`entry_id`, `timestamp`,
  `original_text`, `source`, `author`, `status`, `classification`,
  `related_entries`, `promoted_to`) — only `status` and derived
  metadata change, and only by append, never by overwrite. Rationale
  tied explicitly to `FOUNDING-CHARTER.md` Section 7 (Memory).
- **Entry Types:** decided entries stay `UNCLASSIFIED` at intake
  (Principles 2/3); a fixed four-type taxonomy (Observation/Question/
  Idea/Anomaly) applies only later, at Classification.
- **Workflow:** all nine transitions in `Reality → Inbox → Intake →
  Ledger → Classification → Origin Artifact → Investigation → Proposal
  → Adoption` defined individually, with Adoption requiring a human
  decision per `FOUNDING-CHARTER.md` Section 9 and Principle 0.
- **Weekly Curation, Governance, Metrics** (reusing `PROP-0001`'s
  `acceptance_rate` and ORB's Q4 "real value" question rather than
  inventing competing ones; no vanity metrics; no aggregate score,
  matching AG-001's `METRICS.md` precedent), and a **recommended (not
  created)** repository layout under `docs/intake/`.
- **Adversarial critical review**, run after the design and left
  unfixed per instruction: **14 findings** across all 7 requested
  categories — including three overlapping, unreconciled pipelines now
  present in this repository (`PROP-0001`, `FOUNDING-CHARTER.md`
  Section 4, and this document's own workflow); reuse of the reserved
  word "Observation" as an Entry Type without a disambiguation note;
  no enforcement mechanism for the Investigation-must-cite-its-Ledger-
  entry rule; and a concrete, evidence-grounded scalability concern —
  `RUN-0001` alone produced 17 distinct findings from a single run of a
  single Role, far more than a weekly, single-Curator process could
  obviously absorb.
- Two unrelated broken bare-filename references (mechanical fixes, not
  Candidate-Conflict-style findings) were corrected to full relative
  paths before commit; all references mechanically re-verified.
- No implementation, no automation, no GitHub Action, no agent, no
  prompt. Nothing under `docs/intake/` was created. No other
  repository read, modified, or notified.

## 2026-07-24 (PROP-0003 — Discovery Lifecycle Consolidation)

- Added `docs/proposals/PROP-0003-discovery-lifecycle-consolidation.md`
  (DRAFT / EXPERIMENTAL / NOT ADOPTED). Inspected and cited exact file
  locations for all three existing lifecycle descriptions (`PROP-0001`'s
  information-flow map, `FOUNDING-CHARTER.md` §4's Evolution pipeline,
  `PROP-0002`'s Intake Workflow), plus `HIRING-LIFECYCLE-DRAFT.md` as
  adjacent (Role-status, not content-flow) context, and KOD's own
  Research Session and Knowledge lifecycles as external reference
  material already quoted elsewhere in this repository.
- Built a comparative inventory of all three models (stages, entry
  point, terminal states, decision points, actors, transition
  explicitness, rollback support) without smoothing over differences,
  and a conflict analysis covering all nine conflict types named in the
  task, each with evidence, severity, and whether it needs a decision
  now or can stay open.
- Proposed one canonical 7-stage Discovery Lifecycle (Captured →
  Classified → Curated → Escalated → Investigated → Proposed →
  Adopted/Rejected), derived from the union of the three existing
  models — no wholly new concept introduced. Confirmed via full-
  repository search that "Spark" is used nowhere in this repository and
  is therefore not added to the canonical model. Kept Artifact Type
  (Discovery Observation/Question/Idea/Anomaly) and Lifecycle State
  explicitly separate throughout.
- Compared three canonical-source-of-truth options against six criteria
  and recommended a dedicated `docs/discovery/DISCOVERY-LIFECYCLE.md`
  (not created), explicitly declining to treat `FOUNDING-CHARTER.md` as
  default authority without argument. Proposed a reference rule
  preventing future documents from redrawing the full pipeline, plus a
  namespace dictionary covering all 18 terms named in the task,
  including a three-way qualified split for "Observation" and two kept-
  distinct senses each for "Archive" and "Rejection."
- Converted the "AG-001's one run produced 17 findings" scalability
  concern into a stated research question and a minimal-data
  requirement, explicitly avoiding both a premature architectural fix
  and premature escalation to a formal Investigation.
- Ran the required adversarial review of this document itself and
  recorded 10 findings, none disposed FIX BEFORE ADOPTION. Most
  notable: six of the seven canonical stage names do not appear
  verbatim in any of the three source documents, and "Captured" (this
  document's own Stage 1 name) collides with a stage name `PROP-0002`
  §1 already uses for the Intake mechanism's own separate micro-
  lifecycle — recorded as an OPEN QUESTION, not fixed silently.
- `PROP-0001` and `PROP-0002` were not modified in substance. No code,
  automation, GitHub Action, agent, or prompt introduced. No dedicated
  proposal registry exists in this repository (confirmed by inspection)
  — only `STATE.md`/`CHANGELOG.md` registration was added, matching the
  same minimal pattern already used for `PROP-0001` and `PROP-0002`.
  No other repository read, modified, or notified.

## 2026-07-24 (AG-002 — Discovery Archaeologist, v0.1 + PILOT-RUN-0001)

- **Blocker found before any design work began, and reported rather
  than worked around:** the task requested review of "the supplied
  diary archive together with the Project Memory archive." A full
  filesystem search (`/home/user`, `/workspace`, and a broad
  system-wide `find`) found no diary archive anywhere accessible to
  this session. Rather than inventing diary content or fabricating
  "recovered ideas" attributed to a nonexistent source — which would
  have directly violated the task's own "never invent information" and
  "evidence always wins over interpretation" constraints — this was
  reported, and the run proceeded on the one named source that does
  exist: `project-memory/archive/`.
- Created `docs/ai-organization/employees/AG-002-discovery-archaeologist/`
  — full document set (`CONTRACT.md`, `ROLE.md`, `INPUTS.md`,
  `OUTPUTS.md`, `LIMITATIONS.md`, `CHECKLIST.md`, `METRICS.md`, a
  Recovery Protocol `RUN-PROTOCOL.md` — Historical Sources → Scanning →
  Candidate Discovery → Evidence Linking → Clustering → Recovery Report
  → Recovery Queue — `PROMPT.md`, `STATUS.yaml`, `HISTORY.md`), mirroring
  AG-001's established convention. Status set to **`prototype`**, not
  the "production-ready" language the requesting task used — recorded
  explicitly as a deliberate deviation, since this is the Role's first
  run and `HIRING-LIFECYCLE-DRAFT.md` requires real runs, independent
  review, and a human decision before any advancement.
- Ran `PILOT-RUN-0001` for real: scanned
  `project-memory/archive/architecture-design-document.md`,
  `spike-protocol-potok-b.md`, `AI-Collaboration-Architecture-v1_0.md`,
  and `v1_1.md` in full, plus current-state `project-memory` files for
  comparison. Report:
  `employees/AG-002-discovery-archaeologist/runs/
  PILOT-RUN-0001-recovery-report.md`.
- **Findings, each fully cited:** 7 Recovered Ideas (including a
  complete, apparently-unbound installer "Handover" architecture, and a
  complete, apparently-unexecuted "Поток B" validation spike); 4
  Repeated Themes (most stable: the identical five-word `OPEN → BRIEF →
  WORK → EXTRACT → CLOSE` session lifecycle, unchanged across three
  points in time); 5 Idea Evolution timelines (e.g. a "Kernel"
  governance layer absent from the earliest version scanned, then
  explicitly reintroduced, then accepted but explicitly left
  unvalidated by Pilot 0's own stated boundary); 2 Forgotten Ideas; 2
  Contradictions (one self-documented revision between versions, one
  principle-vs-outcome gap, neither adjudicated); 6 Open Questions; a
  4-item Recovery Queue — **no Investigation created automatically**.
- No source document was edited. No duplicate was removed — repeated
  appearances across versions are cited together as the finding itself,
  not collapsed. No recovered idea is asserted as true or worth
  pursuing.
- Registered AG-002 in `EMPLOYEE-REGISTRY.md` (now 2 Roles, 0 Trusted).
  All relative-path references mechanically verified before commit. No
  other repository read, modified, or notified.
