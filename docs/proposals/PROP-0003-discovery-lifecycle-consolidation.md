# PROP-0003 — Discovery Lifecycle Consolidation

Status: **DRAFT / EXPERIMENTAL / NOT ADOPTED**
Date: 2026-07-24
Author: Implementer session (Claude Code)
Depends on: `PROP-0001-discovery-lab-boundaries.md`,
`PROP-0002-discovery-intake-system.md`, `../ai-organization/
FOUNDING-CHARTER.md`

## How to read this document

This document does not invent a fourth lifecycle. It compares the three
that already exist in this repository, shows their conflicts without
smoothing them over, and proposes one canonical model derived from them
— not created independently of them. No existing specification is
edited by this document except for the minimal registration this
repository's own conventions already require (Section "Minimal
repository updates" at the end). PROP-0001's and PROP-0002's status are
unchanged; nothing here treats `../ai-organization/FOUNDING-CHARTER.md`
as final authority without argument — see Section 5.

---

## 1. Repository Inspection

Checked directly, in this session, before writing anything below —
not reconstructed from the task text alone:

- `docs/proposals/PROP-0001-discovery-lab-boundaries.md` — full
  document; specifically re-verified via `grep` the information-flow
  map (lines ~407–470), ground rule 1 (lines ~38–47), and the
  "Investigation" disambiguation note (lines ~348–361).
- `docs/proposals/PROP-0002-discovery-intake-system.md` — full
  document; specifically re-verified via `grep` the Intake Workflow
  pipeline (§4) and the Critical Review section (§9).
- `docs/ai-organization/FOUNDING-CHARTER.md` — full document;
  specifically re-verified via `sed` the exact text of §4 (Evolution)
  and the Candidate Conflicts section.
- `docs/ai-organization/HIRING-LIFECYCLE-DRAFT.md` — full document.
  Contains its own lifecycle (`Candidate → Prototype → Probation →
  Trusted → Retired`) — confirmed this governs **Role status**, not
  Discovery content flow, and is therefore adjacent context, not one of
  the three lifecycles this task names for consolidation.
- `docs/ai-organization/README.md` — checked; already contains a
  terminology disambiguation note for "Observation" (distinguishing
  AG-001's plain-English usage from KOD's Observation Knowledge Object
  and trust-engine's Observation Memory) — this document builds on that
  note rather than duplicating it.
- `docs/ai-organization/ORGANIZATION-DRAFT.md` — checked; references
  "a candidate lifecycle," confirmed to mean `HIRING-LIFECYCLE-DRAFT.md`,
  not the Discovery content lifecycle.
- `docs/ai-organization/EMPLOYEE-REGISTRY.md` and `docs/ai-
  organization/ORB/ORB-REGISTRY.md` — checked as examples of this
  repository's actual registry convention (a Markdown table, append-only,
  no dedicated index-generation tooling).
- `docs/ai-organization/ORB/ORB-PROTOCOL.md`, `ORB-REVIEW-TEMPLATE.md`
  — checked; `ORB-PROTOCOL.md` quotes KOD's own Research Session
  lifecycle (`Draft → Active Investigation → Ready for Evaluation →
  Under Review → Accepted/Rejected/Archived`) in its own disambiguation
  note — external context, not a discovery-lab lifecycle.
- `docs/ai-organization/employees/AG-001-repository-observer/*` (all 11
  files) and `.../runs/RUN-0001-observation-report.md` — checked;
  `RUN-PROTOCOL.md` and `PROMPT.md`'s own procedure is a single-run
  execution sequence, not a Discovery Lifecycle.
- `docs/investigations/INV-0001-discovery-lab-mandate.md` — checked;
  quotes KOD's Research Session lifecycle and KOD's Knowledge Lifecycle
  (`Observation → Question → Hypothesis → ... → Decision → Outcome →
  new Observation`) as diagnostic material about KOD, not as
  discovery-lab's own model.
- `docs/investigations/INV-0002-independent-architecture-passes.md` —
  checked; contains the same KOD material plus generative-discovery-
  engine's and trust-engine's own lifecycles, all external context.
- `docs/investigations/DL-0001-ecosystem-purpose-shift.md` — checked;
  no separate lifecycle description.
- `README.md`, `CONTEXT.md`, `STATE.md`, `CHANGELOG.md` (repository
  root) — checked. No additional lifecycle description found. **No
  dedicated proposal registry or index file exists anywhere in this
  repository** — `docs/proposals/` contains only the proposal documents
  themselves; tracking happens exclusively through prose in `STATE.md`
  and dated sections in `CHANGELOG.md`. This is documented here because
  it directly answers the "minimal repository updates" question at the
  end of this document.
- `docs/notes/2026-07-24-recovery-investigation.md` — checked, not
  relevant to lifecycle.
- Full-repository search for the exact string `Spark` (case-insensitive):
  **zero matches, in any file.** This is recorded explicitly because
  Section 4 and Section 7 depend on it.
- Full-repository search for `Origin Artifact`: matches only in
  `PROP-0002-discovery-intake-system.md` and its own `CHANGELOG.md`
  registration entry.
- Full-repository search for `Retire`/`Retired`: 7 files, all referring
  to `HIRING-LIFECYCLE-DRAFT.md`'s Role-status lifecycle, none to a
  Discovery content lifecycle.

---

## 2. Lifecycle Inventory

Three lifecycle descriptions were found. None is smoothed over below —
differences are shown as found.

### Model 1 — PROP-0001's information-flow map

| Property | Value |
|---|---|
| Source | `PROP-0001-discovery-lab-boundaries.md`, "Proposed information-flow map" |
| Stages | Reality/external signal → Observation → Candidate investigation → **Experiment** [explicitly marked DORMANT under the recommended Variant B] → Evidence → Review/falsification → Decision → Graduation, rejection, or deletion → Destination repository |
| Entry point | "Reality / external signal" — outside the system, undefined here |
| Terminal states | Three-way: Graduation, rejection, or deletion (named together, not individually detailed) |
| Decision points | "Decision" stage; a branch immediately after it ("no further action needed" vs. "implies a change") |
| Actors/authorities | Discovery Lab self-classifies at Decision (report author is also classifier — an admitted open gap); the *destination* repository's own human-gated process governs Graduation |
| Explicit transitions? | Named and arrow-connected; **no formal entry/exit condition per stage** |
| Rollback/reopen? | Not addressed directly in this pipeline (though `docs/investigations/`'s own SUPERSEDED convention exists separately) |
| Conflicts with others? | Yes — see Section 3 |

### Model 2 — `FOUNDING-CHARTER.md` §4, Evolution

| Property | Value |
|---|---|
| Source | `../ai-organization/FOUNDING-CHARTER.md`, Section 4 |
| Stages | Observation → Investigation → Experiment → Review → Decision → Adoption |
| Entry point | "Observation" — no "Reality" precursor stage at all |
| Terminal states | **Adoption only.** No Rejected/Archived terminal named anywhere in this section — a real gap, not an oversight this document should paper over. |
| Decision points | "Decision" stage, named but with zero further detail |
| Actors/authorities | **None specified per stage.** Section 9 (Human Authority) names who may finally accept a change, but not who acts at each stage. |
| Explicit transitions? | Least detailed of the three — a bare arrow diagram plus one sentence ("never through direct edit") |
| Rollback/reopen? | Not mentioned |
| Conflicts with others? | Yes — "Review" here is already flagged, by this same document's own Candidate Conflict 2, as a fourth, unreconciled sense of that word; stage order differs from Model 1 (no "Evidence" stage; "Investigation" appears immediately after "Observation" rather than after several intermediate stages) |

### Model 3 — PROP-0002's Intake Workflow

| Property | Value |
|---|---|
| Source | `PROP-0002-discovery-intake-system.md`, Section 4 |
| Stages | Reality → Inbox → Intake → Ledger → Classification → Origin Artifact → Investigation → Proposal → Adoption |
| Entry point | "Reality" — explicitly stated as outside Discovery Lab's control |
| Terminal states | "Adoption" is the named pipeline terminus, but Weekly Curation (§5, not itself numbered in this pipeline) adds two more practical termini: Archived, Merged — entries frequently never proceed past Classification |
| Decision points | Ledger→Classification, Classification→Origin Artifact (escalation judgment), Investigation→Proposal, Proposal→Adoption |
| Actors/authorities | **Most detailed of the three** — Intake (a mechanism, explicitly not an employee), a Curator, a human (for Investigation-opening and Adoption) are each named per relevant stage |
| Explicit transitions? | Each of the 9 transitions gets its own paragraph — most operationally detailed, though still not formatted with explicit entry/exit-condition fields |
| Rollback/reopen? | **Yes, explicitly** — Governance (§6) names "reopen entries" as a governed action |
| Conflicts with others? | Yes — introduces four stage names (Inbox, Ledger, Classification, Origin Artifact) absent from both other models; "Investigation," "Proposal," "Adoption" reused but positioned differently relative to the rest of the pipeline than in Model 1 |

### Adjacent, out-of-scope model — `HIRING-LIFECYCLE-DRAFT.md`

Not a Discovery content lifecycle — governs an AI Organization Role's
*status*, not how a raw observation flows to adoption. Included here
only because it also uses the word "lifecycle" and shares vocabulary
(`Archived`... no — actually shares no direct stage-name overlap with
the three above, but does share the word "Retired," addressed in
Section 7). Not consolidated by this document; consolidating it would
itself be scope creep — this document only compares the three
explicitly named in the task.

---

## 3. Conflict Analysis

Each of the nine conflict types named in the task, evidenced, with
severity and whether it requires a decision now or may stay open.

**1. Different stage order.** Evidence: Model 1 places "Evidence" as a
distinct stage between Experiment and Review; Model 2 has no separate
Evidence stage at all; Model 3 has no Evidence stage either, and places
Investigation immediately before Proposal with no Review/Evidence stage
between them. Consequence: a reader moving between these three
documents cannot assume "Investigation" sits in the same relative
position in each. Severity: **HIGH**. Decision now or open: requires a
decision now — this is exactly what Section 4 resolves.

**2. Different names for the same concept.** Evidence: the judgment
step that decides whether something proceeds is called "Review /
falsification" in Model 1, "Review" in Model 2, and "Weekly Curation"
(not part of the named pipeline at all) in Model 3. Consequence: three
different words for what is, functionally, the same kind of gate.
Severity: **MEDIUM**. Decision: now — Section 4 picks one term and
retires the others from pipeline-stage use.

**3. One name for different concepts.** Evidence: "Observation" means
(a) a KOD Knowledge Domain object, (b) AG-001's plain-English report
content (already disambiguated in `docs/ai-organization/README.md`),
and (c) a candidate Entry Type name proposed in `PROP-0002` §3, with no
qualifying form used consistently across the three. "Archive"/"Reject"
mean (a) a terminal verdict on a KOD Research Session's Knowledge claim
(`Accepted/Rejected/Archived`, cited in `INV-0001`), and (b) a Ledger
Entry housekeeping disposition in `PROP-0002` §2/§5 that carries no
truth-verdict at all. Severity: **HIGH** for "Observation" (five known
senses now), **MEDIUM** for "Archive"/"Reject" (two senses, but already
in different repositories, lower collision risk). Decision: now for
both — Section 7 resolves.

**4. Missing states.** Evidence: Model 2 (`FOUNDING-CHARTER.md` §4)
names no Rejected or Archived terminal at all — only Adoption. Read
literally, its Evolution pipeline has no way to represent "this did not
get adopted," which is a routine, expected outcome elsewhere in this
repository (PROP-0001's own Recommendation Ledger interface already
defines `REJECTED` as a normal status, not a defect). Severity:
**MEDIUM**. Decision: now — the canonical model in Section 4 names
Rejected explicitly.

**5. Different rights to change status.** Evidence: Model 3 has an
explicit Governance table (who creates/classifies/archives/reopens/
approves); Models 1 and 2 specify no per-stage authority at all beyond
a general "only a human decides" rule. Severity: **MEDIUM**. Decision:
can stay partially open — Section 6's reference rule requires any
document governing a specific stage to specify its own authority, but
this document does not attempt to retroactively assign authority to
Models 1 and 2's stages (see Section 8, Migration, "Recommended," not
"Required").

**6. Mixing artifact type and lifecycle state.** Evidence: `PROP-0002`
§3 proposes four Entry Types (Observation/Question/Idea/Anomaly) that,
read carelessly next to §4's sequential pipeline diagram, could be
mistaken for sequential stages rather than classifications applied at
one stage. Separately, "Proposal" is simultaneously an artifact type
(`docs/proposals/`, the `PROP-` convention, e.g. this document) and a
pipeline-stage label in Model 3 — here the two senses happen to align,
but the alignment is not explicit anywhere. Severity: **HIGH** — this
is one of the two conflict types the task's own Section 4 instructions
single out by name. Decision: now — Section 4 separates these
explicitly.

**7. Mixing organizational process and agent/employee.** Evidence
checked: "Intake" (`PROP-0002`) is explicitly stated as not an employee;
"Curator" (`PROP-0002` §5) is a procedural function, not a Role, and
this document does not create one either. No instance of a lifecycle
stage being conflated with an AI Organization Employee ID was found.
Severity: **NONE FOUND** — recorded here to show the check was actually
performed, not skipped because it came back clean.

**8. Different terminal states.** Evidence: Model 1's terminus is a
three-way branch (Graduation/rejection/deletion); Model 2's is
Adoption only; Model 3's named pipeline ends at Adoption but its
Curation sub-process (§5) adds Archived/Merged as earlier, equally
real termini. Severity: **HIGH**. Decision: now — Section 4 unifies
these into one terminal-state set.

**9. Different meaning of archive/reject/retire/adopt.** Evidence: see
conflict 3 for archive/reject. "Retire" is used exclusively by
`HIRING-LIFECYCLE-DRAFT.md` for Role status and does not appear in any
of the three Discovery-content pipelines at all — so there is no
existing conflict for "retire" specifically, only a risk that a future
document could introduce one by reusing it for Discovery content.
"Adopt" is used consistently across all three models with the same
meaning (a human accepts a Proposal). Severity: **MEDIUM** (mostly
already resolved by non-overlap; risk is prospective). Decision: can
stay open, addressed preventively in Section 7's dictionary rather than
requiring an active fix.

---

## 4. Canonical Lifecycle Proposal

**Discovery Lifecycle v0.1 (proposed).** Built from the union of the
three existing models — no stage below is a concept absent from at
least one of them; see the per-stage "Derived from" line.

A hard distinction is enforced throughout: **Artifact Type** (what kind
of content something is — Discovery Observation, Question, Idea,
Anomaly, or a document type like Investigation/Proposal) is never the
same axis as **Lifecycle State** (where an entry currently sits in this
process). A stage below may *produce* an artifact of a given type; it
is never itself an artifact type.

**On Spark:** evaluated, not included. A full-repository search found
zero existing uses of this term anywhere. There is nothing to
consolidate, and adding it now would be inventing new vocabulary this
task explicitly says not to do. If a real need for it emerges later,
it should go through this same lifecycle as a proposed addition (see
Section 6), not be assumed into existence here.

**On Origin Artifact:** evaluated and retained. It already exists with
a clear rationale in `PROP-0002` §4 (gives an Investigation a clean,
self-contained starting point instead of forcing it to reach into raw
Ledger text) and is kept as its own stage below.

### Stage 1 — Captured

- **Derived from:** Model 3's Intake→Ledger transition.
- **Purpose:** an entry exists, immutably, with a permanent ID, exactly
  as submitted.
- **Entry condition:** a submission has been made through the Intake
  mechanism (not itself a stage; see `PROP-0002` §1).
- **Allowed outputs:** exactly one new Ledger Entry.
- **Exit condition:** `entry_id`, `timestamp`, `source`, `author`, and
  `original_text` are recorded.
- **Authorized transition:** automatic on successful capture — no
  judgment is exercised at this stage.
- **Terminal/non-terminal:** non-terminal.
- **Traceability requirement:** the `entry_id` is the anchor every
  later stage must cite back to.

### Stage 2 — Classified

- **Derived from:** Model 3's Classification stage; the Artifact-Type
  taxonomy from `PROP-0002` §3.
- **Purpose:** assign one of the fixed Artifact Types (Discovery
  Observation / Question / Idea / Anomaly — see Section 7) or record an
  explicit, reasoned decision to leave the entry unclassified.
- **Entry condition:** entry status is `UNCLASSIFIED`.
- **Allowed outputs:** a `classification` value, or a recorded deferral
  reason.
- **Exit condition:** `classification` populated, or deferral reason
  recorded.
- **Authorized transition:** an authorized Classifier — never the
  Intake mechanism itself.
- **Terminal/non-terminal:** non-terminal.
- **Traceability requirement:** classification decision is dated and
  attributed.

### Stage 3 — Curated

- **Derived from:** Model 3's Weekly Curation (§5).
- **Purpose:** decide disposition — keep active, archive, merge, or
  move toward escalation.
- **Entry condition:** entry is Classified (or explicitly deferred).
- **Allowed outputs:** status change to `ARCHIVED`, `MERGED`, or
  continuation toward Stage 4.
- **Exit condition:** a disposition is recorded with a reason.
- **Authorized transition:** the Curator (a function, not an employee —
  see conflict-type 7 check above).
- **Terminal/non-terminal:** **terminal** if Archived or Merged;
  non-terminal otherwise.
- **Traceability requirement:** disposition reason recorded; a merge
  never deletes or rewrites either entry's original text.

### Stage 4 — Escalated (Origin Artifact produced)

- **Derived from:** `PROP-0002` §4's Origin Artifact transition.
- **Purpose:** package a Curated entry (or a linked set of them) into a
  self-contained starting point for formal investigation.
- **Entry condition:** Curation decided to escalate.
- **Allowed outputs:** one Origin Artifact document, referencing its
  source `entry_id`(s) by reference, not by copy.
- **Exit condition:** the Origin Artifact exists and is linked.
- **Authorized transition:** Curator or human, per Section 6's
  governance rule.
- **Terminal/non-terminal:** non-terminal.
- **Traceability requirement:** the Origin Artifact cites its source
  `entry_id`(s); the Ledger's `promoted_to`-equivalent field is set once
  Stage 5 opens.

### Stage 5 — Investigated

- **Derived from:** Model 1's "Candidate investigation"/"Evidence"
  stages (folded together — see Section 3, conflict 1); Model 2's
  "Investigation"; Model 3's "Investigation."
- **Purpose:** gather and cite evidence, and reach an explicit verdict.
  "Evidence" is a **requirement attached to this stage's output**, not
  a separate stage of its own — this is the resolution to conflict-type
  6.
- **Entry condition:** an Origin Artifact exists.
- **Allowed outputs:** a formal Investigation document
  (`docs/investigations/`, the existing `INV-`/`DL-` convention), ending
  in an explicit verdict — confirmed / contradicted / insufficient
  evidence, matching the convention `PROP-0001`'s own Ecosystem Health
  Review v0.1 already uses — or a documented "no further finding"
  closure.
- **Exit condition:** the Investigation records its own stated verdict.
- **Authorized transition:** a human, or an authorized AI Organization
  Role — never Intake or Curation alone.
- **Terminal/non-terminal:** **terminal for that entry's journey if the
  verdict is "no further finding"** (a valid, non-failure outcome — see
  `PROP-0002` §7's "Investigation yield" metric, which expects most
  Investigations not to yield a Proposal); non-terminal if it proceeds
  to Stage 6.
- **Traceability requirement:** cites its Origin Artifact and
  originating `entry_id`(s).

### Stage 6 — Proposed

- **Derived from:** Model 1's "Decision" stage's positive branch; Model
  3's "Proposal" stage.
- **Purpose:** draft a change proposal from an Investigation's finding.
- **Entry condition:** the Investigation's verdict warrants a change.
- **Allowed outputs:** one Proposal document (`docs/proposals/`, the
  `PROP-` convention — this very document is an instance of this
  stage's output).
- **Exit condition:** the Proposal exists and cites its Investigation.
- **Authorized transition:** human or authorized Role, matching Stage
  5's authorization.
- **Optional sub-element — Experiment:** conditionally usable only if
  `PROP-0001`'s eventual accepted mandate authorizes it (Variant A or
  C); currently **not authorized**, matching `PROP-0001`'s own explicit
  "DORMANT under Variant B" marking. Not a required part of this stage.
- **Terminal/non-terminal:** non-terminal.
- **Traceability requirement:** cites its Investigation's ID.

### Stage 7 — Adopted / Rejected

- **Derived from:** all three models agree without exception that this
  final step requires a human.
- **Purpose:** a human decision on the Proposal.
- **Entry condition:** a Proposal exists.
- **Allowed outputs:** exactly one of `ADOPTED`, `REJECTED`, or
  `AMENDED` (amendment opens a new, linked Proposal at Stage 6 — it
  never silently edits the original, per the Memory principle).
- **Exit condition:** a human decision is recorded with a reason.
- **Authorized transition:** **only a human.** No exception anywhere in
  this document.
- **Terminal/non-terminal:** terminal (`ADOPTED`, `REJECTED`); `AMENDED`
  loops back to Stage 6, non-terminally.
- **Traceability requirement:** decision and reason permanently
  recorded; rejection does not delete anything.

---

## 5. Canonical Source of Truth

| Criterion | Option A — dedicated `docs/discovery/DISCOVERY-LIFECYCLE.md` | Option B — stays in Founding Charter | Option C — stays in one approved proposal |
|---|---|---|---|
| Authority | Clear — one purpose-built document | Ambiguous — a Charter is meant to be high-level and rarely amended (per its own §9, changing it requires a human, via the full Evolution process); forcing operational lifecycle detail into it conflates "foundational, stable" with "operational, frequently tuned" | Ambiguous — none of the existing proposals is *about* the lifecycle as its primary subject; borrowing one conflates topics |
| Discoverability | High — matches the existing precedent of `HIRING-LIFECYCLE-DRAFT.md`, a dedicated file for exactly one lifecycle | Buried inside a longer document covering nine other subjects | Buried inside a document whose title is about something else (Intake, boundaries) |
| Duplication risk | Low — one file, everything else references it | Medium — Charter sections tend to get restated elsewhere (already true of Sections 2, 5, 7, 8 of the Charter itself, each restating something from `ORGANIZATION-DRAFT.md` or `HIRING-LIFECYCLE-DRAFT.md`) | Medium-High — if the "canonical" proposal is later superseded for an unrelated reason, the lifecycle definition moves with it unnecessarily |
| Update governance | Matches Section 6's reference rule cleanly: one file, one Adoption gate | Amending the lifecycle would require a full Charter amendment (Section 9), a heavier bar than lifecycle tuning likely needs | Same problem as Option A but without the discoverability benefit |
| Compatibility with repository conventions | **Strong precedent already exists** — `HIRING-LIFECYCLE-DRAFT.md` is exactly this pattern, one dedicated file per lifecycle | Weaker — no existing Charter section is treated as a machine-checkable operational spec | Weak — proposals are not currently treated as living, canonical references once superseded |
| Danger of premature adoption | Low — a dedicated DRAFT file can stay DRAFT indefinitely without blocking anything | Higher — bundling it with Charter-level principles risks the lifecycle being treated as more settled than it is, by association | Low, but for the wrong reason (nobody would look there) |

**Recommendation: Option A**, not created by this document (per
instruction), with one open point: whether a single file needs its own
`docs/discovery/` directory or could instead sit directly at
`docs/DISCOVERY-LIFECYCLE.md`. This document does not resolve that
naming detail — it is recorded as an Open Question (Section 10).

This directly addresses the instruction not to accept `FOUNDING-
CHARTER.md` as final authority without analysis: Option B was evaluated
on the same six criteria as the other two and scored worse on four of
them, not assumed inferior.

---

## 6. Reference Rule

Proposed rule, extending the example given in the task:

> A document may describe only the lifecycle segment it governs, in
> full operational detail, and must reference the canonical Discovery
> Lifecycle document for the complete process. It must not redraw the
> full end-to-end pipeline.

**How referencing is done.** A document that touches the Discovery
Lifecycle opens the relevant section with a line naming which Stage(s)
(by number and name, from Section 4) it governs, and a link to the
canonical file — for example: "This section governs Stages 1–3 of the
canonical Discovery Lifecycle (`docs/discovery/DISCOVERY-LIFECYCLE.md`);
it does not itself define the lifecycle."

**What local description is allowed.** Full operational detail for the
stage(s) the document actually owns — for example, `PROP-0002` may (and
does) fully specify how Capture and Classification work, because it
owns those stages' operational mechanics. It may not redefine a stage it
does not own beyond a one-line pointer.

**What counts as prohibited duplication.** Drawing a complete,
end-to-end arrow diagram naming every stage, when the document governs
only some of them; introducing a new stage name not in the canonical
list; silently renaming a canonical stage locally (e.g. calling Stage 5
"Review" instead of "Investigated" inside a different document).

**How a lifecycle-change proposal is handled.** A proposed change to
the canonical lifecycle itself goes through the same lifecycle it
defines — recursively: the proposed change is itself a Discovery Entry
(Captured → Classified → Curated → Escalated → Investigated → Proposed
→ Adopted/Rejected). This matches `FOUNDING-CHARTER.md` §4's "never
through direct edit" principle, applied here explicitly to the
lifecycle file itself, closing a gap the Charter's own text leaves open
(it names the rule but not what it applies to).

**Who may approve.** Only a human, at Stage 7 — no exception, matching
every other adoption gate already established in this repository.

---

## 7. Terminology and Namespaces

| Term | Definition | Namespace | Allowed usage | Prohibited / ambiguous usage | Relation |
|---|---|---|---|---|---|
| Discovery Entry | Any submission accepted into the Discovery Lifecycle, at any stage. A superset term. | Discovery Lab | General references to "something in the system" | As a synonym for a specific stage's artifact | Umbrella; not itself a stage or type |
| Raw Entry | A not-yet-captured thought, before Intake. Never has an `entry_id`. | Discovery Lab (pre-system) | Describing the Inbox concept (`PROP-0002` §4) | As a record that exists anywhere durably | Pre-Stage-1; conceptual only |
| Ledger Entry | The specific, IDed record created at Stage 1 (Captured). | Discovery Lab's Discovery Ledger | The concrete Ledger row/file for one submission | — | = Stage 1's artifact |
| Observation (bare, unqualified) | — | — | **Prohibited unqualified**, per `PROP-0001` ground rule 1, extended here | Any unqualified use | Must take one of the three qualified forms below |
| Discovery Observation | An Artifact Type assigned at Stage 2 (Classified). | Discovery Lab's Classification taxonomy | Classifying a Ledger Entry as this type | Referring to KOD's or AG-001's usage | Artifact Type, not a stage |
| Repository Observation | A cited fact in an AG-001 (or future Role) Observation Report (`.../OUTPUTS.md`). | AI Organization, Role-conduct output | Describing what a Role's run produced | Treating it as automatically a Discovery Entry — it becomes one only if separately submitted (see `PROP-0002` §2's own `source` example, "AG-001 RUN-0001 finding #7") | Role output; may become a Discovery Entry's `source`, is not one by default |
| KOD Observation | KOD's own Knowledge Domain Observation object (`KOD/Foundations/OBSERVATION.md`). | KOD (external repository) | Citing KOD's own concept accurately | Discovery Lab claiming any authority over its meaning | External; out of this document's scope entirely |
| Finding | — | — | Ordinary English, left **deliberately undefined** — see note below | Treating it as a reserved, formally-typed term | Not formalized at v0.1 |
| Evidence | A citation requirement attached to Stage 5/6 outputs. | Cross-cutting requirement | "This claim is supported by evidence X" | As a stage name (already prohibited by `PROP-0001` ground rule 1) | Requirement/property, not a stage or type |
| Spark | **Not currently used anywhere in this repository** (verified, Section 1). | — | Not applicable | Any use, until introduced through Section 6's own process | Not part of this lifecycle |
| Origin Artifact | Stage 4's output document. | Discovery Lab | The packaged starting point handed to Stage 5 | As a synonym for the raw Ledger Entry it references | = Stage 4's artifact |
| Investigation | Stage 5's process, and its resulting document type (`docs/investigations/`, `INV-`/`DL-`). | Discovery Lab | Both senses, since they coincide | Conflating with KOD's Investigation Engine concept (already disambiguated in `PROP-0001`) | = Stage 5; restates, does not alter, `PROP-0001`'s existing note |
| Experiment | An optional sub-element of Stage 6, gated by `PROP-0001`'s mandate decision. | Discovery Lab, conditional | Only if a mandate variant authorizing it is adopted | Treating it as always available | Not a required stage; currently dormant |
| Proposal | Stage 6's output, and the `docs/proposals/` artifact type. | Discovery Lab | Both senses, since they coincide (unlike some other rows here) | — | = Stage 6's artifact |
| Adoption | Stage 7's terminal, positive outcome. | Discovery Lab | A human's acceptance of a Proposal | — | = Stage 7 (positive branch) |
| Archive | **Two senses, kept distinct.** (1) KOD's Research Session terminal Knowledge-claim verdict. (2) Discovery Lab's Stage 3 Ledger-entry housekeeping disposition — carries **no truth-verdict**. | (1) KOD; (2) Discovery Lab | Either, if the repository/lifecycle is named alongside it | Using either sense without naming which lifecycle it belongs to | (2) = Stage 3 terminal branch |
| Rejection | **Two senses, kept distinct.** (1) KOD's Research Session Knowledge-claim verdict. (2) Discovery Lab's Stage 7 human decision not to adopt a Proposal. | (1) KOD; (2) Discovery Lab | Either, if named | Same as Archive | (2) = Stage 7 (negative branch) |
| Retirement | AI Organization's Role-status lifecycle terminal state (`HIRING-LIFECYCLE-DRAFT.md`) only. | AI Organization | Role status only | **Reusing it for Discovery content** — this lifecycle does not have a "Retired" state at all | Belongs to a different lifecycle entirely; not part of Section 4's model |

**Note on "Finding."** Deliberately left generic. It already appears
informally across this repository (AG-001's report findings, ORB
review findings, this document's own Critical Review items in Section
10) with no single meaning that would survive formalization without
creating a sixth overloaded word. Not formalizing it is a decision, not
an oversight — it is not needed at v0.1, and adding it "because it was
in the task's own list" would repeat the exact mistake this document
otherwise tries to stop.

**Note on existing concepts.** No concept already defined in `PROP-0001`,
`PROP-0002`, or `../ai-organization/FOUNDING-CHARTER.md` is renamed here
without the justification given in Section 4's per-stage "Derived from"
line. Where this document introduces a stage label not verbatim in any
source document (Captured, Classified, Curated, Escalated, Investigated,
Proposed), that is flagged explicitly as a self-critique finding in
Section 10, not hidden.

---

## 8. Migration Impact

No migration is performed by this document. This is a plan only.

**Required (upon adoption of PROP-0003):**

- Create the canonical file recommended in Section 5 (Option A).
- Add a short "superseded for lifecycle purposes, retained for history"
  pointer to `PROP-0001`'s information-flow map section and to
  `../ai-organization/FOUNDING-CHARTER.md` §4 — neither section is
  deleted (Memory principle); both gain a note directing readers to the
  canonical file.

**Recommended:**

- Extend `docs/ai-organization/README.md`'s existing "Observation"
  disambiguation note with the three-way qualified-form split from
  Section 7 of this document.
- Update `PROP-0002` §3 to reference the canonical file for the
  Artifact-Type-vs-Lifecycle-State distinction instead of re-explaining
  it locally.
- Add a cross-reference from `../ai-organization/ORB/ORB-PROTOCOL.md`'s
  existing "Review" disambiguation note to this document's finding that
  the canonical lifecycle deliberately does not use "Review" as a stage
  name.

**Optional:**

- Consider whether `docs/investigations/` or `docs/proposals/` would
  benefit from a short README pointing to the canonical lifecycle for
  orientation.
- Consider whether `HIRING-LIFECYCLE-DRAFT.md` should be renamed (e.g.
  to a name that cannot be mistaken for "the" lifecycle) — its content
  is already unambiguous; only its filename is a mild risk.

**Deferred:**

- Splitting `PROP-0002`'s §1/§2/§5 content into dedicated `docs/intake/`
  files — already deferred by `PROP-0002` itself, unrelated to lifecycle
  consolidation specifically.
- Any formal ADR-style acceptance record — deferred until a human
  actually adopts this document.
- Retrofitting `INV-0001`, `INV-0002`, or `DL-0001` with canonical
  lifecycle-stage citations — they predate this consolidation and are
  historical record; retrofitting them is optional-if-ever, not
  required.

---

## 9. Scalability Finding

**The finding, restated precisely.** `PROP-0002`'s own Critical Review
(finding 14) already recorded that AG-001's single existing run,
`RUN-0001`, produced 17 distinct findings — 5 confirmed changes, 6
current-state observations, 3 structural signals, 1 insufficient-access
item, 2 unknowns — from one run of one Role, before Intake or the
Ledger exist at all.

**This document does not solve it by assumption.** With exactly one
data point, no sound decision between "this is fine" and "this breaks
the model" is possible yet.

**Disposition: operational metric, not an immediate architectural
change, and not yet an Investigation.** `PROP-0002` §7 already defines
`classification latency` and `conversion rate: Ledger → Investigation`
as metrics; this finding does not require inventing a new one — it
requires actually measuring the two that already exist, against real
data, once Intake is in use. Escalating straight to an architectural
change (e.g. redesigning Curation cadence) would itself violate
`../ai-organization/FOUNDING-CHARTER.md` §3 ("no organizational rule is
accepted without evidence") on the very first attempt to apply that
principle to a real question.

**Research question:** Does AI Organization Role output (for example,
AG-001 runs) generate Ledger Entries at a rate that exceeds what a
weekly, single-Curator process can classify and curate within its own
cycle, once Intake is actually in use?

**Minimal data required before deciding:**

- The actual count of Ledger Entries submitted per week, across at
  least 4–6 real Weekly Curation cycles, including entries sourced from
  AI Organization Role runs and not only human submissions.
- The actual time a single Curator spends per entry during a real
  session (a rough estimate is sufficient; no new instrumentation is
  proposed).
- The `classification latency` metric (`PROP-0002` §7), tracked across
  those same cycles, to see whether it trends flat or upward (a growing
  backlog).

Only if this data shows a sustained, real gap should this become a
formal Investigation. No Investigation file is created by this
document, per instruction.

---

## 10. Adversarial Review

Performed after writing the sections above, against this document
itself. Findings are not fixed here — each carries a Disposition, per
instruction.

**Finding 1 — Six of this document's seven canonical stage names
("Captured," "Classified," "Curated," "Escalated," "Investigated,"
"Proposed") do not appear verbatim as stage names in any of the three
source models.**
Severity: **HIGH**.
Evidence: Model 3 (`PROP-0002`) names its own stages "Intake," "Ledger,"
"Classification," "Origin Artifact," "Investigation," "Proposal" — not
"Captured," "Classified," "Escalated," "Investigated," "Proposed." More
specifically: `PROP-0002` §1 already defines a *separate*, narrower
micro-lifecycle for the Intake mechanism itself — "Submitted → Captured
(written to the Ledger) → Acknowledged" — and this document's Stage 1
reuses the word "Captured" for a different, broader lifecycle's own
stage name, creating a fresh, self-inflicted collision inside this very
document.
Consequence: a reader could reasonably conclude this document *is* a
fourth lifecycle — the one thing it was explicitly told not to be —
because it introduces new labels rather than adopting the source
documents' own vocabulary verbatim.
Disposition: **OPEN QUESTION** — not fixed here. A human should decide
whether the canonical model should instead use Model 3's own stage
names verbatim (Intake/Ledger/Classification/Origin Artifact/
Investigation/Proposal/Adoption, with Reality and Curation added where
Model 3 leaves them implicit) rather than the state-oriented renaming
attempted here.

**Finding 2 — The per-stage specification depth (seven fields × seven
stages) may itself be premature bureaucracy.**
Severity: **MEDIUM**.
Evidence: zero Ledger Entries exist anywhere; this level of detail
exceeds what `PROP-0002`'s own Critical Review (finding 5) already
flagged as premature for its Ledger schema, applied at an even larger
scale here.
Consequence: same class of risk `PROP-0002` already named, compounded.
Disposition: **ACCEPTED RISK** — this depth was explicitly required by
the task's own instructions for Section 4; avoiding it would mean not
completing the assigned deliverable.

**Finding 3 — Stage 7's "AMENDED → new Proposal version" mechanic is
invented, not derived.**
Severity: **MEDIUM**.
Evidence: none of the three source models specify how "amend" works
procedurally — all three only use the bare word.
Consequence: could preempt a better-reasoned amendment design.
Disposition: **OPEN QUESTION**.

**Finding 4 — "Experiment" is described as an optional lifecycle
sub-element, but could equally be read as an artifact type (an
"Experiment brief," analogous to how a Proposal is a document type).**
Severity: **LOW-MEDIUM**.
Evidence: Section 4 places it under Stage 6 as a "sub-element," not
clearly on either side of the Artifact-Type/Lifecycle-State line this
document otherwise insists on.
Consequence: a small instance of the same conflict-type-6 problem this
document was written to resolve, surviving inside the resolution
itself.
Disposition: **OPEN QUESTION**.

**Finding 5 — Authority ("human or authorized Role") is left unnamed,
for the fourth time in this repository.**
Severity: **MEDIUM** (recurring, not new).
Evidence: `HIRING-LIFECYCLE-DRAFT.md`, `../ai-organization/
FOUNDING-CHARTER.md`, `PROP-0002`, and now this document all leave "who
exactly" unresolved.
Consequence: every "authorized transition" field in Section 4 is
currently unenforceable in practice.
Disposition: **OPEN QUESTION** — explicitly not resolved here either;
resolving it is bigger than this document's scope.

**Finding 6 — This document does not itself edit `PROP-0001` or
`FOUNDING-CHARTER.md`, leaving a window where both still present their
own pipelines unmarked as non-canonical.**
Severity: **MEDIUM**.
Evidence: Section 8 lists the pointer-note edits as "Required," but this
commit does not make them, per explicit instruction not to correct
existing specifications beyond minimal registration.
Consequence: a reader who opens `PROP-0001` or the Charter directly,
without first finding this document, has no signal that their pipeline
section is now considered non-canonical.
Disposition: **ACCEPTED RISK** — direct, unavoidable consequence of the
task's own constraint against fixing multiple documents in one commit.

**Finding 7 — Backwards compatibility: `RUN-0001` and `DL-0001` predate
the Ledger and do not map onto Stage 1 (Captured) at all.**
Severity: **LOW**.
Evidence: neither has an `entry_id`; the Ledger did not exist when
either was created.
Consequence: none currently — the Memory principle protects historical
documents from needing retroactive rewriting.
Disposition: **DEFERRED** (matches Section 8).

**Finding 8 — Terminology self-check.** "Curator" was checked against
the rest of the repository for collision risk; none was found — no
other document uses this word for anything else. Recorded to show the
check was performed, not to manufacture a finding where none exists.
Disposition: **not applicable** (no defect found).

**Finding 9 — Stage 5's exit condition ("the Investigation reaches its
own stated verdict") does not define what happens if it never does.**
Severity: **LOW-MEDIUM**.
Evidence: `DL-0001` has remained open, without a verdict, since its
creation, with no forcing function — the same open-endedness `PROP-0002`
already flagged for its own `UNCLASSIFIED` status, now recurring one
stage later.
Disposition: **OPEN QUESTION**.

**Finding 10 — No rule in this document, including its own "authorized
transition" fields, is mechanically checkable.**
Severity: **MEDIUM**.
Evidence: unlike AG-001's evidence-citation requirement (checkable by
inspecting whether an `Evidence` entry exists) or ORB's review process
(a defined, if manual, check), nothing here proposes any way to verify
that a transition was actually performed by an authorized party.
Consequence: the canonical lifecycle's own authority rules are exactly
as unenforceable as the three documents it set out to reconcile.
Disposition: **OPEN QUESTION**.

**Ten findings.** Zero rated for immediate FIX BEFORE ADOPTION — every
substantive finding is left as OPEN QUESTION or ACCEPTED RISK, per
instruction not to silently correct this document's own conflicts in
the same pass that found them. A human reviewing this document should
treat Finding 1 as the one most worth resolving before any adoption
decision, since it bears most directly on whether this document
achieved its stated purpose.

---

## Minimal Repository Updates

Per the repository inspection in Section 1: **no dedicated proposal
registry or index file exists anywhere in this repository.** Tracking
of `PROP-` documents happens only through `STATE.md` prose and dated
`CHANGELOG.md` sections — the same minimal pattern already used to
register `PROP-0001` and `PROP-0002`. No registry file is created here,
because none is this repository's established convention.
`STATE.md` and `CHANGELOG.md` are updated accordingly, alongside this
document. No other file is touched.
