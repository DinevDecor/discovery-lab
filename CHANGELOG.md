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

## 2026-07-24 (Memory Source Registry + Connection Protocol)

- Added `docs/ai-organization/MEMORY-SOURCES/` — **infrastructure, not
  a new employee**: no Employee ID, no `EMPLOYEE-REGISTRY.md` entry, no
  `CONTRACT.md`, no assigned Executor, matching the same framing already
  used for `ORB/`. **AG-002 was left entirely unchanged**, per explicit
  instruction — confirmed via `git diff --stat` showing zero changes
  under its directory.
- `MEMORY-SOURCE-PROTOCOL.md` defines a registry schema
  (`source_id`, `name`, `type`, `locator`, `access_requirements`,
  `status`, `steward`, `added`, `last_verified`, `notes`) and a
  six-stage Connection Protocol: Lookup → Selection & Authorization →
  Resolution → Verification → Read-only Access → Disconnection.
  **Paths are never hardcoded**: a `locator` is a stable,
  environment-independent reference (a Git repository name + relative
  path + ref; a Drive folder's own identifier) — never a literal local
  filesystem path, which is specific to one session's mount layout and
  would silently break elsewhere. Resolution to an actual local path
  happens fresh per session (Stage 3) and is never written back into
  the registry.
- Explicitly **not** a trust/reliability score for sources (`status` is
  an availability flag only — trust-scoring is trust-engine's territory,
  per `PROP-0001` ground rule 3) and explicitly **not** a credential
  store (`access_requirements` is an abstract description, never an
  actual secret).
- Added disambiguation notes: "Memory" here means an external data
  repository, not trust-engine's "Trust Memory"/"Observation Memory"
  concepts; "Source" here is a registered, typed, verifiable system,
  distinct from `PROP-0002`'s Discovery Ledger `source` field (a
  possible future integration is noted as an open question, not acted
  on — `PROP-0002` itself was not modified).
- `SOURCE-REGISTRATION-TEMPLATE.md` added, mirroring
  `../ORB/ORB-REVIEW-TEMPLATE.md`'s placeholder-based style.
- `MEMORY-SOURCE-REGISTRY.md` seeded with exactly **one** real entry,
  `MEM-001` (`project-memory` archive, the source `PILOT-RUN-0001`
  actually scanned and verified) — no `google_drive` entry and no
  additional Git repositories (`KOD`, `generative-discovery-engine`,
  `trust-engine`, though technically accessible in this session from
  unrelated earlier work) were registered, since none has actually been
  used as a memory source by any Role yet; adding them now would be
  registering ahead of evidence.
- Wiring AG-002 (or any Role) to actually consult this registry by
  default is explicitly deferred to a future step, not performed here.
  All relative-path references mechanically verified before commit. No
  code, automation, or GitHub Action introduced. No other repository
  read, modified, or notified.

## 2026-07-24 (AG-002 PILOT-RUN-0002 — blocked at Stage 1)

- A second real recovery mission was requested for AG-002, naming one
  sole authorized source (no substitution permitted this time): a
  diary archive at Google Drive, "Project Memory → Archive → oneDay
  6.zip".
- Stage 1 (Historical Sources / Lookup) was attempted by three
  distinct methods in this session: `search_files` with
  `title contains 'oneDay 6'`, `search_files` with
  `title contains 'Project Memory'`, and `list_recent_files`. All
  three returned identically: `MCP error -32003: MCP tool call
  requires approval`. No file, folder, or file metadata was ever
  retrieved from Google Drive.
- Per the requesting task's stop rule and `RUN-PROTOCOL.md`'s own Stop
  rule, the run halted at Stage 1 rather than substituting another
  source or inventing content. **No Recovery Report was produced** —
  writing one would misrepresent zero actual scanning as a completed
  run. `PILOT-RUN-0002-Recovery-Report.md` does not exist.
- Reported to the requester as `BLOCKED — Diary archive exists but is
  not accessible from the current execution environment.`
- Recorded as a new entry in AG-002's own append-only
  `HISTORY.md` (the run was real and belongs to AG-002's record even
  though it produced no report). `EMPLOYEE-REGISTRY.md`,
  `STATUS.yaml`, and every other AG-002 file were left unchanged — no
  run was actually completed, so `runs_completed` was not incremented.
  No source document was read, modified, or fabricated. No other
  repository read, modified, or notified.

## 2026-07-24 (Infrastructure Sprint 01 — root-cause diagnosis of the Google Drive block)

- Treated the PILOT-RUN-0002 block as an infrastructure problem, not an
  AG-002 problem, per explicit instruction. Gathered direct evidence
  instead of guessing: `ListConnectors` output (Google Drive
  `connected: true`, `enabledInChat: true` — fully authenticated),
  Claude Code's own MCP debug logs (`mcp-logs-6c0f8fb6-.../*.jsonl`,
  `mcp-logs-Google-Drive/*.jsonl`), the CLI's local permission settings
  (`/root/.claude/launcher-settings.json`,
  `/home/claude/.claude/launcher-settings.json` — both
  `permissions.allow: ["Skill"]` only), and the agent proxy's own
  documented failure modes (`/root/.ccr/README.md`, ruled out — this is
  not a network/TLS issue).
- **Root cause identified, with quoted log evidence:** every Google
  Drive tool call fails with `MCP error -32003: MCP tool call requires
  approval`; the same log line reads `"...needs_approval
  (tool_name=mcp__Google_Drive__search_files) — surfacing retroactive
  approval card"`. This is a per-tool, per-session, human-interactive
  consent gate on org "Directory"-origin connectors, sitting in front
  of the Drive API itself, independent of the connector's own
  authenticated/connected state. No human was present in this
  unattended task session to click the approval card when it was
  surfaced, so it was never granted. Explicitly ruled out with
  evidence: network/proxy/TLS, missing OAuth, missing connector,
  repository/`.claude/settings.json` configuration, Drive API scope.
- Produced
  `docs/ai-organization/MEMORY-SOURCES/INFRA-SPRINT-01-report.md`:
  Infrastructure Report (what works / what's blocked / why / which
  component / exact missing capability), Permanent Architecture (Google
  Drive → Memory Source Registry → AI Organization → AG-001/AG-002/
  future employees, built entirely on the existing, unmodified
  Connection Protocol, plus one *finding* — an implicit "Stage 0
  Platform Tool Approval" precondition — recorded, not silently added
  to the Protocol), a 5-step Connection Plan (owner / prerequisite /
  expected result / verification method each), a PASS-test Verification
  Procedure (AG-002 must discover, resolve, verify, read, and produce a
  real cited Recovery Report, unattended, with zero manual copying), and
  an exact Human Action section naming the one action only Petko can
  take, including an explicit, flagged uncertainty about whether
  approval is session-scoped or persistent — not assumed either way.
- Added `MEM-002` (Project Memory diary archive, Google Drive) to
  `MEMORY-SOURCE-REGISTRY.md`: `type: google_drive`, `status:
  unverified`, `drive_or_shared_drive`/`folder_path_or_id` both
  honestly `UNKNOWN` (Lookup never succeeded — no ID was ever
  retrieved, so none was invented). This is the correct starting state
  per `SOURCE-REGISTRATION-TEMPLATE.md`, not a defect.
- **Definition of Done: NOT YET PASS.** Every remaining step is blocked
  on one human action (approving the pending Drive tool-call request);
  nothing in this sprint claims otherwise. AG-002 and Discovery Lab's
  governance documents (`FOUNDING-CHARTER.md`, `PROP-0001`–`PROP-0003`,
  `ORB/`, `MEMORY-SOURCE-PROTOCOL.md`) were not modified. No temporary
  workaround (caching, copying, bypassing the gate) was attempted.
- Recorded, per explicit new instruction: from this sprint forward, a
  `BLOCKED` result from any Discovery Lab agent is followed by
  "diagnose and eliminate the root cause," not "retry" — this sprint is
  the first applied instance, noted as a now-followed practice, not
  silently written into
  `docs/ai-organization/FOUNDING-CHARTER.md` or
  `docs/ai-organization/HIRING-LIFECYCLE-DRAFT.md`.
- Added a **Five Whys** root-cause classification to the same report
  (§8) before closing the sprint. Chain: symptom (`PILOT-RUN-0002`
  `BLOCKED`) → technical cause (`-32003` on every Google Drive call,
  regardless of tool/query) → infrastructure cause (the approval gate
  is interactive-only with no unattended path through it, *and* the
  Registry's Stage 4 Verification is not enforced before Stage 2
  Selection & Authorization) → **governance cause, and the first cause
  under human organizational control**: no human or Curator has ever
  been assigned standing ownership of external-connector approval or
  source verification — already on record, unresolved, as
  `permanent organizational owner` in AG-002's own
  `STATUS.yaml`. Smallest permanent fix recommended (not applied): (1)
  the one human approval click already requested in §5, plus (2) one
  governance rule — a Registry entry may not be cited as an authorized
  source while `status: unverified` — which converts the existing,
  already-built Stage 4 into an enforced gate instead of an
  aspirational one. No new employee, document set, or automation
  proposed.

## 2026-07-24 (ADR-0001 — Human Authority Gates)

- Added `docs/adr/` and its first document,
  `docs/adr/ADR-0001-human-authority-gates.md` — the first ADR in this
  repository, distinct from the existing `PROP-000N` proposal series.
  Status: **DRAFT**, unadopted, matching every other governing document
  in this repository.
- Defines **Human Authority Gate (HAG)**: any action requiring explicit
  human authorization before the organization may continue — never an
  error, always a normal state transition. Generalizes exactly what
  `INFRA-SPRINT-01-report.md` found concretely: a connected, authenticated
  Google Drive connector that still requires one-time human consent per
  tool call.
- Defines **Standard Agent Behavior** for a HAG (stop, preserve, record,
  specify the minimal human action, wait, resume automatically if
  possible — no retries, no workarounds, no duplicated data) and a
  **required HAG report format** (Resource / Requested action / Blocking
  authority / Evidence / Exact human action / Expected result / Resume
  point) — `INFRA-SPRINT-01-report.md` §5 already contains every one of
  these fields in substance, cited as the worked template.
- Proposes a **Registry extension**: every source gains two independent
  states — Connectivity (Connected/Disconnected) and Authority
  (Authorized/Pending Human Approval/Denied/Unknown) — never merged.
  Worked example, from real evidence: `MEM-002` is Connected (the MCP
  transport connects fine) **and** Pending Human Approval (every tool
  call returns `-32003`), a distinction the current single `status`
  field cannot represent. Flags one unresolved question of its own:
  where the existing `deprecated` value fits in a two-axis model — not
  decided here.
- **Reconciles a terminology collision** between this ADR's four
  organizational categories (technical failure / infrastructure
  limitation / governance boundary / Human Authority Gate) and Sprint
  01's Five Whys, which used "governance cause" in a different sense (an
  organizational ownership gap, not a by-design boundary). Under this
  ADR, the `-32003` signal itself reclassifies from Sprint 01's
  "technical cause" to a Human Authority Gate; Sprint 01's downstream
  findings (no automatic resume path, Stage 4 not enforced, no assigned
  owner) remain genuine Infrastructure limitations — nothing in Sprint
  01's conclusion is contradicted, only refined.
- **Adopts nothing else.** AG-002's `RUN-PROTOCOL.md`/`INPUTS.md`
  terminology, the Memory Source Registry's actual schema, and a HAG Log
  are all explicitly listed (ADR §8) as separate, human-gated migration
  steps this document does not perform — no registry created ahead of a
  first real entry, no existing file rewritten.

## 2026-07-24 (ADR-0001 accepted; migration planned, not started; Sprint 01 continued)

- **Petko accepted ADR-0001.** `ADR-0001-human-authority-gates.md`'s
  `Status:` changed `DRAFT → ACCEPTED`, with a new "Acceptance record"
  section quoting the exact terms ("architectural principles approved...
  do not begin the migration yet") and stating precisely what is now
  settled architecture (§1–§7) versus what remains deliberately
  unimplemented (§8). Fixed two stale internal section references found
  while editing (`§7` had incorrectly pointed at "Success Criteria" in
  two places where "§8, the punch list" was meant).
- Added `docs/adr/README.md` — the ADR index the acceptance decision
  asked for, distinct from the existing `PROP-000N` series, with a
  Status-value legend and an explicit rule that the ADR file itself is
  authoritative if this table ever drifts from it. Current total: 1 ADR,
  1 accepted.
- Added `docs/adr/ADR-0001-migration-plan.md` — Status: **PLANNED / NOT
  STARTED**, per explicit instruction not to begin migration yet. Expands
  ADR-0001 §8's four items into ordered, verifiable steps (owner /
  prerequisite / action / expected result / verification, matching
  `INFRA-SPRINT-01-report.md`'s Connection Plan format): AG-002
  terminology migration, Registry schema migration (including resolving
  §5.2's open `deprecated`-placement question first), a HAG Log
  explicitly gated on a first real HAG entry existing before the file is
  created, and an "automatic resume" item flagged as possibly bounded by
  the same platform layer Sprint 01 already found responsible for the
  approval gate itself — not assumed buildable within this repository.
- **Continued Infrastructure Sprint 01**, per instruction: re-attempted
  Google Drive access (`list_recent_files`, `search_files`, plus a fresh
  `ListConnectors` check). Result: **still blocked**. Every call again
  returned `MCP error -32003: MCP tool call requires approval`
  (fresh log timestamps 13:09–13:10Z); the connector's own state is
  unchanged from Sprint 01 (`connected: true`, `enabledInChat: true`) —
  nothing indicates the pending approval has been granted yet. No
  `PILOT-RUN-0002` report was produced; Sprint 01's actual completion
  criterion (a successful Recovery Run) remains unmet. This re-check is
  itself the first real, evidence-backed encounter that could be filed
  in ADR-0001's HAG report format — reported to the requester in that
  format directly, without creating `docs/adr/HAG-LOG.md`, since
  Migration Item 3 correctly gates that file's creation on migration
  actually starting, which it has not.

## 2026-07-24 (Infrastructure Sprint 01 closed — platform limitation; ADR-0002 drafted)

- **Live approval test, conducted with Petko actively present.** After
  Petko clicked "Allow once" on the surfaced Drive approval card, the
  very next call in the same session (`list_recent_files`, then
  `search_files`) still returned `MCP error -32003`, with the log
  repeating `"...surfacing retroactive approval card"` for each new call
  — each call generates its own fresh card rather than consuming a
  standing grant. A further, deliberately minimal single call
  (`list_recent_files`, pageSize 1) was then issued while Petko was
  actively watching and approving, to test whether a call could be
  caught mid-flight and resumed. It also failed in `0s` — proof the call
  never reaches a "pending" state at all; the card is generated
  retroactively, after rejection, not during a live request.
- **`INFRA-SPRINT-01-report.md` updated with a new §9, "Final
  Conclusion — Platform Limitation, Not a Project Failure,"** recording:
  Connector status **CONNECTED**; Organization authorization
  **COMPLETE**; Per-call approval flow **NON-RESUMABLE / RETROACTIVE**;
  Unattended Google Drive access **NOT SUPPORTED IN THIS CLIENT**;
  `MEM-002` operational status **BLOCKED BY PLATFORM APPROVAL MODEL**.
  Explicitly framed as a platform limitation — not a project failure,
  not a missing OAuth authorization; every layer this repository
  controls (connector auth, Registry entry, AG-002's Stop rule) worked
  correctly throughout. The report's header, §1.6, §3 (Connection Plan),
  §4 (Verification Procedure), and §5 (Human Action Required) were all
  annotated with this outcome — none of the original text was deleted,
  each superseded section is marked as such, preserving the historical
  record of what was actually tried. **No further Google Drive retries
  will be attempted**, per explicit instruction.
- `MEMORY-SOURCE-REGISTRY.md`'s `MEM-002` entry updated: `status` stays
  `unverified` (still accurate — Lookup never succeeded), `notes`
  rewritten to record the closure and point to the new ADR-0002 proposal
  instead of a still-pending action. Not marked `deprecated` — Google
  Drive remains the intended canonical source if a working access path
  is ever found.
- **Added `docs/adr/ADR-0002-ag002-alternative-memory-access.md`** —
  Status: **DRAFT, proposal only, not implemented**. Proposes a
  Human-Mediated Export Bridge: a human periodically exports the diary
  from Drive into a new Git-tracked source (a future `MEM-003`, not
  created here) that AG-002 reads through its existing, unmodified
  Recovery Protocol — the same mechanism already proven working for
  `MEM-001`. Frames this as relocating the Human Authority Gate ADR-0001
  defines to one human action per export, instead of one per call (which
  §9 shows this client cannot support). Records two alternatives
  considered and not recommended (a service-account Drive path; waiting
  for a platform fix) and one self-critical, explicitly unresolved
  tension: this proposal duplicates data, in tension with the Registry's
  own "no duplicated memory" principle — flagged for Petko to decide, not
  resolved unilaterally. Leaves open where the export lives and how
  often it recurs.
- `docs/adr/README.md` updated: ADR-0002 added as **DRAFT** (index now 2
  ADRs: 1 accepted, 1 draft).

## 2026-07-24 (AG-002 Memory Access Blocker resolved — ADR-0002 implemented, verified PASS)

- **ADR-0002 accepted and implemented**, in the same task sequence as its
  draft — `docs/adr/ADR-0002-ag002-alternative-memory-access.md`'s
  `Status:` changed `DRAFT → ACCEPTED — IMPLEMENTED`, with an Acceptance
  record resolving its own open questions (export location =
  `discovery-lab/memory/`; cadence = manual v1; the "no duplicated
  memory" tension resolved by instruction — bounded, purpose-scoped
  mirroring authorized, wholesale duplication still prohibited). The
  original draft text (§1–§6) is preserved unedited below the Acceptance
  block, per this repository's "don't rewrite history" discipline.
- **Documented the Google Drive role change** `INFRA-SPRINT-01-report.md`
  §6 required before making it: Drive stays the canonical,
  human-maintained archive, but is no longer treated as a source any Role
  reads directly. Recorded in a new **§10, "Decision & Implementation —
  Repository-Based Operational Memory Layer,"** which also updates §2's
  Permanent Architecture diagram (superseded-and-annotated, not deleted)
  and closes with a completion verdict.
- **Added `memory/`** at the `discovery-lab` repo root: `inbox/`,
  `journal/`, `decisions/`, `observations/`, `README.md`,
  `PROVENANCE-SYNC-SPEC.md`, `IMPORT-PROCEDURE.md`, `source-manifest.md`.
  Explicitly not a bulk Drive copy — seeded with exactly one file, added
  through the real import procedure it defines. `PROVENANCE-SYNC-SPEC.md`
  defines the 8-field metadata block (`source_system`, `source_path`,
  `source_file_id`, `source_modified_at`, `mirrored_at`, `mirror_method`,
  `content_hash`, `verification_status`) and the sync rules: Drive is
  canonical, the mirror is never a second source of truth, no silent
  overwrites, no claim of completeness, unresolved divergence reported
  not guessed. `IMPORT-PROCEDURE.md` is manual-only for v1 (no automatic
  Drive sync), and is explicit that the mechanical filing steps are
  performed by a human/steward, not by AG-002 — consistent with AG-002's
  own unmodified `INPUTS.md`.
- **`MEMORY-SOURCE-REGISTRY.md` updated**: `MEM-002` reclassified (not
  deprecated) — `connectivity: CONNECTED`,
  `agent_access: HUMAN-INTERACTIVE / NOT AGENT-OPERATIONAL`. `MEM-003`
  added (`type: git_repository`, same shape as `MEM-001`, zero new
  capability required of any Role), initially `unverified`, later
  promoted to `status: active`, `agent_access: AGENT-OPERATIONAL —
  PRIMARY FOR AG-002` once verification passed (below) — marked primary
  only after verification, per instruction, not on creation. The new
  `connectivity`/`agent_access` fields are noted explicitly as a small,
  ad hoc addition, **not** `ADR-0001-migration-plan.md` Item 2's full
  two-axis schema migration, which remains **NOT STARTED**.
- **One real end-to-end verification performed.** A synthetic test
  fixture (`memory/journal/SYNTHETIC-TEST-journal-0001.md`) was created
  and labeled as fabricated at every point of contact — in its own
  banner text, its provenance front matter, its manifest entry, and the
  run report — since no real, accessible Drive content exists yet to
  test against. It was imported through the real procedure: placed in
  `memory/inbox/`, hashed
  (`sha256:aa75e30c1edc6e4df6cbb793dcc0ad2f91ba7b2be84f2c9a3d89b6b1c0ee8407`),
  filed into `memory/journal/` with full provenance, logged as
  `memory/source-manifest.md` entry `MIRROR-001`.
- **AG-002 run `MIRROR-VERIFY-0001`**
  (`docs/ai-organization/employees/AG-002-discovery-archaeologist/runs/
  MIRROR-VERIFY-0001-recovery-report.md`), using AG-002's existing,
  unmodified Recovery Protocol, unedited by this task: discovered
  `MEM-003` via the Registry, read the filed file in full, preserved and
  cited its provenance, extracted one finding (a recurring, fabricated
  "standing observatory" idea, stated twice), wrote the result to
  `memory/observations/MIRROR-VERIFY-0001-observation-0001.md`, and did
  not modify the source — confirmed in the report's own Archaeologist
  Boundary Statement. The report itself carries a prominent warning
  banner distinguishing it from a real recovery mission and from the
  still-unattempted, still-blocked `PILOT-RUN-0002`.
- `AG-002`'s `HISTORY.md` gets a new, honestly-labeled entry
  (`MIRROR-VERIFY-0001`); `STATUS.yaml`'s `runs_completed` incremented
  `1 → 2` (a real run genuinely occurred, even though its source content
  was synthetic) — performance/quality fields left untouched, pending
  independent review, per `CHECKLIST.md`.
- Two broken relative-path references caught and fixed during mechanical
  verification before commit (`../../MEMORY-SOURCES/...` in the new run
  report needed one more `../` level — corrected to `../../../MEMORY-SOURCES/...`).
- **Completion verdict: PASS** — AG-002 successfully completed an
  end-to-end run using the repository memory source. Remaining
  limitation, stated plainly: no real Google Drive content has been
  mirrored yet; only the mechanism is proven. No further Google Drive
  MCP calls were attempted, no bulk copy was made, no background sync was
  built, and no secrets or sensitive data were introduced — all per
  explicit constraint.

## 2026-07-24 (Reality Inbox created — organization-wide intake layer, verified PASS)

- **Simplified before it was built.** The requesting task's own first
  draft specified a 7-folder intake design
  (`incoming/processing/accepted/rejected/manifests/fixtures/INDEX.md`);
  the same message then replaced it with a simpler instruction — one
  folder for humans, agent handles the rest — before implementation
  began. Only the simplified version was built.
- **Added `reality-inbox/`** at the `discovery-lab` repo root:
  **`📥 DROP HERE/`** (emoji-named exactly as specified — verified to
  work cleanly with `mkdir`/`git add` before relying on it) is the
  *only* folder a human ever interacts with; no routing decision is
  asked of them. `manifests/`, `processed/`, `fixtures/`, `INDEX.md`,
  `README.md`, and `PROCESSING-PROTOCOL.md` are agent/steward-managed
  bookkeeping — a file's status (`INCOMING` through `ARCHIVED`) lives in
  its manifest, not in which folder it sits in; a single `processed/`
  archive holds every handled file regardless of outcome, so nothing is
  ever silently deleted.
- **`PROCESSING-PROTOCOL.md`** defines the 12-step intake procedure, the
  manifest schema (the task's required fields plus three supplementary
  ones — `processing_agent`, `processed_at`, `outputs` — needed to
  actually satisfy the Provenance rule and step 11), and the
  file-handling rules: no secrets/credentials committed unnecessarily,
  no uncontrolled large binaries (manifest-only + external reference
  until a size policy exists — none does yet), no overwrites, no silent
  renames, no auto-deletion of rejected files, duplicates never treated
  as new evidence.
- **`MEMORY-SOURCE-REGISTRY.md` updated**: `MEM-004` added for
  `reality-inbox/`, `agent_access: AGENT-OPERATIONAL — DEFAULT SOURCE
  FOR AG-002`. `MEM-003` (`memory/`) explicitly **not** superseded —
  reclassified in its own notes as the downstream
  "Knowledge/Registry/Ledger" layer, with the Reality Inbox as the new
  front door in front of it. `memory/inbox/README.md` updated to note
  it is superseded as the human-facing drop point by
  `reality-inbox/📥 DROP HERE/`.
- **AG-002 integration — small, additive edits, not a redesign**:
  `INPUTS.md` gained a "Default operational source: the Reality Inbox"
  section; `LIMITATIONS.md` gained a prohibition on scanning unrelated
  repository content as memory and a **fourth mandatory escalation
  value, `BLOCKED`** (a source is reachable but its manifest/provenance
  failed validation — distinct from `INSUFFICIENT ACCESS`);
  `RUN-PROTOCOL.md` Stage 1 and `CHECKLIST.md` each gained a one-line
  Reality Inbox manifest check. `ROLE.md`, `OUTPUTS.md`, `CONTRACT.md`,
  `METRICS.md`, and `PROMPT.md` untouched.
- **AG-001 reviewed and found not to need a compatibility update** — it
  observes `discovery-lab`'s own repository structure, not external
  evidence; recorded as a real finding in `MEM-004`'s notes, not a
  silent skip, per the task's own instruction.
- **One real, independent end-to-end verification performed**, distinct
  from the prior `MIRROR-VERIFY-0001`: a synthetic fixture
  (`reality-inbox/fixtures/SYNTHETIC-TEST-note-0001.md`) placed in
  `📥 DROP HERE/`, manifested as `RI-0001` (hash
  `sha256:0f75163b0c3204d8de2893caafe088072b34570b75acca15e158b4beeaf4f6b1`,
  duplicate-checked, verified readable, sensitivity classified,
  destination identified), moved to `processed/`. AG-002 ran
  `REALITY-VERIFY-0001`
  (`docs/ai-organization/employees/AG-002-discovery-archaeologist/runs/
  REALITY-VERIFY-0001-recovery-report.md`), confirming the manifest's
  `status: ACCEPTED` and full provenance *before* reading (the new Stage
  1 check), then discovered, read, cited, extracted one finding, wrote
  it to `memory/observations/
  REALITY-VERIFY-0001-observation-0001.md`, and left the source
  unmodified — confirmed in the report's own Archaeologist Boundary
  Statement. `reality-inbox/INDEX.md` and AG-002's `HISTORY.md` /
  `STATUS.yaml` (`runs_completed` `2 → 3`) updated accordingly.
- One broken relative path (the same off-by-one pattern as the previous
  task's `runs/` report) caught and fixed during mechanical verification
  before commit.
- **Completion verdict: PASS** — the Reality Inbox works end to end and
  AG-002 completed the synthetic pilot. Stated limitation: no real
  evidence has entered the Reality Inbox yet; only the mechanism is
  proven, twice over now (`memory/` and `reality-inbox/`).

## 2026-07-24 (ADR-0003 — Reality Inbox Architecture, FROZEN)

- **Numbering conflict flagged, not silently resolved.** The requesting
  task asked to create "ADR-0002 — Reality Inbox Architecture," but
  `ADR-0002` was already registered
  (`ADR-0002-ag002-alternative-memory-access.md`, ACCEPTED — IMPLEMENTED).
  Per `docs/adr/README.md`'s own rule ("numbered sequentially, never
  renumbered or reused"), this document is registered as **`ADR-0003`**
  instead — recorded explicitly in the ADR's own header, not silently
  renumbered or overwritten.
- **Added `docs/adr/ADR-0003-reality-inbox-architecture.md`** — Status:
  **ACCEPTED — FROZEN**. Freezes two properties of the design built and
  verified in the immediately preceding task
  (`INFRA-SPRINT-01-report.md` §11) as fixed architecture: (1) the
  human-facing interface is exactly one folder,
  `reality-inbox/📥 DROP HERE/`; (2) processing state is tracked only
  through manifests (`reality-inbox/manifests/`), never through which
  folder a file sits in.
- **§3 draws an explicit, enforceable governance line** — requires a new
  ADR: a second human-facing folder or drop-time choice; moving state
  tracking out of manifests; changing the manifest schema; changing who
  may perform mechanical processing; weakening any file-handling rule.
  Does **not** require a new ADR: processing real files through the
  existing procedure; adding manifest/`INDEX.md` entries; writing the
  still-missing large-file size policy (a documented gap, not a frozen
  absence); extending the same design to another repository.
- **Made the freeze discoverable, not just recorded**: added a one-line
  "Core architecture FROZEN, see ADR-0003" status marker to
  `reality-inbox/README.md` and `reality-inbox/PROCESSING-PROTOCOL.md` —
  no other content in either file changed.
- **Caught and fixed a real staleness bug** while updating the ADR index:
  `docs/adr/README.md` still listed `ADR-0002` as `DRAFT`, even though
  the ADR file itself was updated to `ACCEPTED — IMPLEMENTED` in an
  earlier task and the index was never updated to match. Corrected, per
  the index's own stated rule that the ADR file is authoritative over
  its summary table. `docs/adr/README.md` now lists 3 ADRs (all
  accepted: 1 migration-deferred, 1 implemented, 1 frozen).

## 2026-07-24 (ADR-0004 — local Google-Drive-synced intake; ADR-0003 amended)

- **Requester's core complaint**: the Reality Inbox as built (previous
  entry) still optimized for the repository, not the user — every
  ordinary intake required a GitHub upload or branch interaction.
- **Rigorously confirmed, not assumed, that this session cannot reach
  the user's local machine.** Checked `git rev-parse --show-toplevel`
  (`/workspace/discovery-lab`), `df -h .` (`/dev/vda`, mounted at `/`),
  the full mount table (no CIFS/SMB/NFS/9p, no drive-letter concept —
  this is Linux), environment variables (nothing Drive/Windows-related),
  and `rclone listremotes` (binary present at `/opt/rclone` but not on
  `PATH`, no remotes configured). **Conclusion: structural, not a
  permissions gap** — this session runs in a remote, ephemeral container
  (`CLAUDE_CODE_REMOTE=true`) with no filesystem bridge to the user's
  computer at all, let alone to Google Drive specifically.
- **Explicitly disambiguated from the earlier Drive limitation**
  (`INFRA-SPRINT-01-report.md` §9): that was the Drive **MCP
  connector's** non-resumable per-call approval flow — an API problem.
  This is a **local-filesystem** problem — unrelated, does not depend on
  the MCP connector, and would not be solved even if that connector were
  fixed (`G:\...` is a Windows path, not a Drive API identifier).
- **Added `docs/adr/ADR-0004-local-drive-synced-reality-inbox.md`** —
  Status: **ACCEPTED — DESIGN COMPLETE, AWAITING LOCAL VERIFICATION**.
  Decision: for sessions with local filesystem access (Claude Desktop,
  local Claude Code), the one human-facing intake folder becomes
  `G:\My Drive\Projects\discovery-lab\DROP HERE` — an ordinary,
  already-Drive-synced folder requiring only a file copy and a spoken
  instruction to the agent; no Git, no GitHub, no branch. The local
  agent performs hashing, manifesting, and the `git commit`/`push` of
  the result itself, never handing a Git step back to the human. The
  original file is **copied**, not moved, into
  `reality-inbox/processed/` — it stays on the user's Drive-synced disk
  untouched. `reality-inbox/📥 DROP HERE/` (git-tracked) is kept,
  unedited, as the explicit fallback for sessions without local access —
  this repository's own remote sessions among them.
- **Amended `ADR-0003` in place** (frozen text preserved, not rewritten):
  added an "Amended, 2026-07-24" note pointing to `ADR-0004`, explaining
  that "exactly one human-facing folder" now means exactly one *per
  reachable filesystem*, not a rule broken by the new local path. This
  is `ADR-0003` §3's own required "new ADR" step, triggered correctly.
- **Repository-side logic kept as-is**, per instruction: the manifest
  schema, provenance rule, and 12-step processing protocol are
  unchanged in substance. One small additive field,
  `intake_mode: local-drive-sync | repo-tracked-fallback`, records which
  folder a file actually came through; steps 1 and 8 note the
  mode-specific copy-vs-move detail.
- Updated `reality-inbox/README.md` (two-mode workflow, updated
  architecture diagram, honest "not yet verified in local mode" note),
  `PROCESSING-PROTOCOL.md`, `MEMORY-SOURCE-REGISTRY.md`'s `MEM-004`
  notes, and `docs/adr/README.md` (4 ADRs now, `ADR-0003`'s row marked
  "amended by ADR-0004"). One inconsistent citation style caught and
  fixed in the Registry during verification (a bare `ADR-0004-...`
  filename that didn't match this file's own `../../adr/...` convention
  elsewhere).
- **No fabricated verification.** This session cannot create, populate,
  or test `G:\My Drive\Projects\discovery-lab\DROP HERE` — the design is
  recorded as accepted and ready, explicitly not as implemented or
  tested, pending a real run from a session with local access.

## 2026-07-24 (ADR-0004 local verification attempted — result: BLOCKED)

- **Requested: run the full local-verification cycle from this session.**
  Attempted in good faith, with exact evidence recorded, rather than
  declined outright.
- **Re-confirmed, fresh, this is the identical remote container**
  (`CLAUDE_CODE_CONTAINER_ID=container_01T4iigk7CVPKUrCE3TAbvc2--claude_code_remote--9e8649`,
  `CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE=cloud_default`), with no mount,
  network filesystem, or environment variable connecting it to the
  user's machine or Google Drive — same conclusion as `ADR-0004` §2, not
  assumed carried over.
- **One important negative result, recorded so it is never mistaken for
  progress:** `mkdir -p "/mnt/g/My Drive/Projects/discovery-lab/DROP
  HERE"` **succeeded** (exit 0). This is explicitly **not** evidence of
  Drive access — Linux creates arbitrary directory paths regardless of
  what they're named; the resulting folder was an ordinary, empty,
  fully disconnected directory on this container's own ephemeral disk,
  coincidentally sharing a name with the real target. **Deleted
  immediately** (`rm -rf /mnt/g`) once established, so no misleading
  artifact was left for a future reader to mistake for a working bridge.
- Since there was no real folder to read from, steps 3 onward of the
  requested cycle (confirm read/write, detect a real diary file, copy
  the original, manifest with `intake_mode: LOCAL_DRIVE`, process,
  commit/push) were **correctly not attempted** — not skipped by
  oversight, but because performing them against the fabricated
  look-alike directory would have meant processing nothing real while
  appearing to complete the cycle.
- **`ADR-0004`'s status was not changed to `VERIFIED`**, per the
  requester's own explicit instruction ("only if the full cycle
  succeeds") and this repository's standing discipline against claiming
  synchronization or access that has not happened. Added a new §6,
  "Verification attempt log," documenting the attempt and its evidence
  in full; updated the ADR's header status line and `docs/adr/README.md`'s
  summary row to reflect it, without erasing the original "awaiting
  verification" framing.
- **Verdict: BLOCKED** — an external dependency (a session actually
  running on the user's machine, with Google Drive for Desktop syncing
  the target folder) prevents completion; nothing in this repository can
  substitute for it.
