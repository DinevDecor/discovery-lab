# PROP-0002 — Discovery Intake System v0.1

Status: DRAFT PROPOSAL — not accepted, not an ADR, not implemented.
Date: 2026-07-24
Author: Implementer session (Claude Code)
Depends on: `PROP-0001-discovery-lab-boundaries.md`, `../ai-organization/
FOUNDING-CHARTER.md`

## How to read this document

This is an organizational design only. No code, no automation, no
GitHub Action, no agent, and no prompt is created by this document.
Nothing under a `docs/intake/` directory is created — Section 8
recommends a repository layout; it does not build one. Discovery Lab
itself remains DRAFT throughout.

**Relationship to Discovery Lab's still-unaccepted mandate.** `PROP-0001`
recommends, but has not had accepted, one of three mandate variants for
Discovery Lab. This document does not presuppose which one (if any) is
chosen. Intake is upstream infrastructure — how raw material enters —
and is equally usable whether Discovery Lab ends up an Experiment
Laboratory, an Ecosystem Observatory, or a Combined variant. What
happens to an entry *after* Classification depends on that unresolved
decision; this document does not resolve it and does not need to.

---

## 1. Discovery Intake Specification

**Purpose.** Provide the single, low-friction entry point through which
any raw observation, question, idea, or anomaly enters Discovery Lab —
preserving it exactly as given, before any classification, research, or
interpretation happens.

**Scope.** Intake covers exactly the moment of capture: from the
instant something is submitted to the instant it is durably recorded in
the Discovery Ledger with a unique ID and timestamp. Nothing before that
(noticing something) and nothing after it (classifying, curating,
investigating) belongs to Intake.

**Responsibilities.**

- Accept a submission from any authorized source (see Governance,
  Section 6 — in this design, unrestricted).
- Preserve the submission's original content exactly — no correction,
  no paraphrase, no reformatting beyond what plain storage requires.
- Assign a unique, permanent Ledger ID.
- Record a timestamp, a source, and an author — or explicitly `unknown`
  if genuinely not available. Never fabricated.
- Append the entry to the Discovery Ledger.
- Confirm receipt to whoever submitted it — a minimal acknowledgment,
  not a judgment of the entry's worth.

**Non-responsibilities.** These follow directly from the seven
fundamental principles given for this design:

- Intake never performs research (no fact-checking, no verification, no
  investigation of whether the observation is correct).
- Intake never edits meaning (no summarizing, no "cleaning up," no
  correcting the submitter's own words — any note Intake staff might
  want to add is separate metadata, never merged into the original
  text).
- Intake never proposes solutions (no recommendations, no suggested next
  steps, no priority assignment).
- Intake never classifies. Classification is a distinct, later stage
  (Section 3, Section 4) — this is stated as a hard non-responsibility
  precisely because Principles 2 and 3 name it as fundamental, not
  incidental.
- Intake never rejects a submission for seeming low-quality, silly,
  duplicate, or out of scope. Filtering happens later, in Weekly
  Curation (Section 5) — not at the door.

**Lifecycle (of an Intake action, not of the resulting entry).**
`Submitted → Captured (written to the Ledger) → Acknowledged.` This is
short and complete on purpose: Intake's job ends the moment an entry
exists in the Ledger with an ID. Everything after that — classification,
curation, investigation — belongs to a different stage with a different
actor.

**Actors.**

- **Submitter** — anyone permitted to create an entry: any human, or any
  AI Executor acting in any capacity, including one performing an AI
  Organization Role (e.g. AG-001) or working in a different repository
  entirely. See Governance, Section 6.
- **Intake mechanism** — explicitly **not a new employee and not an AI
  Organization Role.** It has no Employee ID, no `CONTRACT.md`, no
  assigned Executor of its own, matching the same framing already used
  for `ORB` ("not a new employee"). Intake is a defined **capture point**
  — in this design, a place a submission is written to (see Section 8)
  — not an actor with judgment or discretion. Nothing about accepting a
  submission requires interpretation, so nothing about it requires an
  employee.

**Interfaces with the rest of Discovery Lab.**

- **Downstream:** a classified Ledger entry may become the origin
  material for a formal Investigation (`docs/investigations/`, the
  existing `INV-`/`DL-` numbering convention), by way of an Origin
  Artifact (Section 4). Intake feeds this; it does not create
  Investigations itself.
- **AI Organization:** if an AI Organization Role (present or future)
  notices something worth recording, it submits through Intake exactly
  like any other Submitter — it does not have, and should not be given,
  a side channel around this system.
- **Discovery Lab's mandate (`PROP-0001`):** as stated above, this
  design is deliberately variant-agnostic. It defines entry, not
  disposition.

---

## 2. Discovery Ledger Specification

**Purpose.** An append-only, immutable record of every entry ever
submitted through Intake, in the exact order received.

**Fields per entry.**

| Field | Description |
|---|---|
| `entry_id` | Unique, permanent, sequential ID assigned at capture (e.g. `DIS-000001`), matching the zero-padded, sequential ID convention already used for `INV-`, `PROP-`, `DL-`, `ORB-`, and `RUN-` identifiers elsewhere in this repository. Never reused, even if the entry is later archived. |
| `timestamp` | Capture time, ISO 8601. Immutable. |
| `original_text` | The submitter's exact input, verbatim — including typos, incomplete thoughts, or informal phrasing. Immutable. |
| `source` | Free text describing where the entry came from (e.g. "manual entry," "AG-001 RUN-0001 finding #7," "external conversation"). Not a fixed enum — sources are not fully predictable in advance. |
| `author` | Who submitted it — a name, an AI Role's Employee ID, or `unknown`. Never fabricated if not provided. |
| `status` | The one field expected to change over time: `UNCLASSIFIED → CLASSIFIED → (ARCHIVED \| MERGED \| PROMOTED_TO_INVESTIGATION)`. |
| `classification` | Populated only after Classification (Section 3/4); absent until then. |
| `related_entries` | A list of other `entry_id`s this one is linked to, for duplicate/merge handling (Section 5). Append-only. |
| `promoted_to` | If this entry becomes the origin material for a formal Investigation, the Investigation's own ID (e.g. `INV-0003`), recorded here to make the link traceable in both directions. |

**Why ledger entries are immutable.** `entry_id`, `timestamp`,
`original_text`, `source`, and `author` are fixed permanently at
capture and never edited afterward, for the same reason `../ai-
organization/FOUNDING-CHARTER.md` Section 7 ("the organization preserves
its history — it does not rewrite it") already states for the rest of
this repository's own history (`HISTORY.md` files,
`EMPLOYEE-REGISTRY.md`, `docs/investigations/`'s SUPERSEDED-not-deleted
convention). If the original text could be edited after the fact, the
Ledger would stop being a trustworthy record of what was actually
observed and when — anyone could quietly "clean up" an entry once they
saw where it led, and no later reader could ever be certain a record
they're looking at is what was actually first said. The Ledger's entire
value is being tamper-evident; a mutable ledger is not a ledger, it is
a notes file.

The remaining fields (`status`, `classification`, `related_entries`,
`promoted_to`) are metadata *about* an entry's journey, not edits to the
entry's own content, and even these are recorded as **appended, dated
changes** — never as silent in-place overwrites — mirroring the
append-only style already used in every `HISTORY.md` file in this
repository.

**Traceability requirements.**

- Every entry is traceable forward: Ledger → Classification → (if
  applicable) Origin Artifact → Investigation → Proposal → Adoption.
- Every Investigation that originates from a Ledger entry is expected
  to cite that entry's `entry_id`, and the entry's own `promoted_to`
  field records the Investigation's ID in return — a two-way link.
- No entry is ever deleted. An entry found to be a duplicate, a
  mistake, or no longer relevant is marked with a `status`, never
  removed.

---

## 3. Discovery Entry Types

**Decision: entries remain unclassified at intake.** A small, fixed
candidate taxonomy is defined, but it is applied only later, at
Classification (Section 4) — never at the point of submission.

The four candidate types, evaluated as requested:

- **Observation** — a report that something was noticed to be true or
  present. Used here in the plain sense; see Critical Review (Section
  9) for the terminology overlap this creates.
- **Question** — something unresolved, seeking an answer.
- **Idea** — a candidate proposal, direction, or design worth exploring.
- **Anomaly** — something that appears inconsistent, unexpected, or
  contradictory, without yet knowing why.

**Justification.** Forcing classification at the moment of capture adds
exactly the kind of friction Principle 7 (minimize friction, under 30
seconds) works against, at precisely the moment friction is most
costly. Many entries are also genuinely ambiguous when first written —
something that looks like an "anomaly" may turn out, on reflection, to
be a "question," and an "idea" may really be an "observation" wearing a
different hat. Because the Ledger is immutable in its original content
but *not* in its classification field, there is no cost to waiting:
recording `UNCLASSIFIED` now and classifying correctly once, later, with
more context, is strictly better than guessing immediately and having
to carry a wrong label. This is also a direct, literal application of
Principles 2 and 3, which name this as a *fundamental* design
requirement, not an optimization.

The four candidate types themselves are kept as a **fixed, closed set**
rather than an open, ad hoc vocabulary, so that Classification (a
later, separate judgment) has a small, learnable standard to apply
consistently — the alternative, letting classifiers invent categories
as they go, would recreate the same "increase in documents" problem
`../ai-organization/FOUNDING-CHARTER.md` Section 1 explicitly says AI
Organization does not exist to produce.

---

## 4. Intake Workflow

```
Reality
   ↓
Inbox
   ↓
Intake
   ↓
Ledger
   ↓
Classification
   ↓
Origin Artifact
   ↓
Investigation
   ↓
Proposal
   ↓
Adoption
```

**Reality → Inbox.** A person, or an AI Executor performing some Role,
notices something in the ordinary course of their work. This step is
entirely outside Discovery Lab's control — the "Inbox" is simply
wherever a not-yet-submitted thought sits before someone decides to
write it down. Nothing about this transition is designed here; it
cannot be.

**Inbox → Intake.** The submitter writes the raw thought down, in
whatever words come naturally, and submits it through the single
official Intake mechanism (Section 8). This is the transition Principle
7's 30-second target applies to most directly — the design goal is that
nothing between deciding to submit and having submitted should require
more than the text itself.

**Intake → Ledger.** Intake captures the submission, assigns
`entry_id` and `timestamp`, and appends it to the Ledger exactly as
received. This is the only transition Intake itself performs (Section
1). Once complete, Intake's role in this specific entry's life is over.

**Ledger → Classification.** During Weekly Curation (Section 5), or ad
hoc by an authorized Classifier, an `UNCLASSIFIED` entry is reviewed and
assigned one of the four Entry Types (Section 3) — or left explicitly
unclassified, with a recorded reason, if genuinely unclear. This
transition changes the `status` and `classification` fields only;
`original_text` is never touched.

**Classification → Origin Artifact.** For an entry judged worth
pursuing further, a short, dedicated Origin Artifact is produced — a
small document that packages the Ledger entry (by reference to its
`entry_id`, not by copying its text) together with whatever additional
context is needed to hand it to a formal Investigation. This mirrors a
pattern already used, without this name, in `docs/investigations/
DL-0001-ecosystem-purpose-shift.md`'s own "Origin" section, which
already records exactly where an idea came from, verbatim. This step
exists so that an Investigation does not have to reach back into the
raw Ledger itself for its starting point — it receives a clean,
self-contained one.

**Origin Artifact → Investigation.** A human, or an authorized AI
Organization Role, opens a formal Investigation (the existing `INV-`/
`DL-` convention under `docs/investigations/`) using the Origin Artifact
as its starting evidence. This is a deliberate escalation, not an
automatic one — see Section 7 (Metrics): most Ledger entries are
expected to never reach this stage, and that is the healthy outcome,
not a shortfall.

**Investigation → Proposal.** If an Investigation's findings suggest a
change, a Proposal is drafted under `docs/proposals/`, the same
convention this very document follows (`PROP-0001`, `PROP-0002`).

**Proposal → Adoption.** A human decision accepts, rejects, or amends
the Proposal — matching `../ai-organization/FOUNDING-CHARTER.md` Section
9 (Human Authority) and Discovery Lab's own Principle 0 exactly.
Neither Discovery Lab nor any AI Executor adopts its own proposal, here
or anywhere else in this repository.

---

## 5. Weekly Curation Protocol

**Who performs it.** A designated Curator — a human, or an AI Executor
acting in a defined procedural function, the same way `ORB`'s Reviewer
is a function rather than a new employee (Section 1). Where practical,
the Curator for a given entry should not be the same party who
submitted it, to avoid a submitter classifying or dismissing their own
very-recent entry alone — a lighter version of the independence norm
`../ai-organization/ORB/ORB-PROTOCOL.md` already requires strictly for
its own reviews.

**Decision criteria.** For each entry still `UNCLASSIFIED`: (a) assign
one of the four Entry Types, or explicitly record that it remains
unclassified and why; (b) decide a disposition — keep active, archive,
merge, or escalate toward an Origin Artifact.

**Archive rules.** An entry is archived — `status: ARCHIVED`, never
deleted — when it is clearly resolved elsewhere, superseded by a later
entry, or judged, with a one-line recorded reason, not worth pursuing
further. This mirrors the SUPERSEDED convention already used in
`docs/investigations/`.

**Duplicate handling.** Entries describing the same underlying thing are
linked through `related_entries`, never merged destructively. One may
be marked primary and the others `MERGED` into it, but every original
text stays in the Ledger unchanged — only `status` and `related_entries`
change.

**Merge policy.** A merge is a metadata operation only. It never
rewrites, deletes, or combines original text. Every merge carries a
one-line recorded reason.

**Escalation to Investigation.** Reserved for entries that are specific
and evidenced, or clearly evidence-seeking, and not already covered by
an existing Investigation. This is a deliberate judgment call, not a
volume-based trigger — a low escalation rate is the expected, healthy
outcome (Section 7).

---

## 6. Governance

| Action | Who may do it |
|---|---|
| Create entries | Anyone — any human, any AI Executor in any capacity, from inside or outside AI Organization. Unrestricted, per the friction principle: restricting submission would itself be friction, and would risk losing observations from exactly the people or systems closest to noticing something. |
| Classify entries | The designated Curator, or any explicitly authorized Classifier — not restricted to one person, but should avoid a submitter classifying their own very-recent entry alone (Section 5). |
| Archive entries | Same authority as classification. Archiving is organizational housekeeping, not a judgment of the submitter. |
| Reopen entries | Any authorized Classifier or Curator, with a recorded reason. Reopening is always available — nothing is permanently closed without a trace, matching the Memory principle (`../ai-organization/FOUNDING-CHARTER.md` Section 7). |
| Approve Investigations (open one; and separately, adopt a resulting Proposal) | Only a human. An AI Executor or Curator may *propose* that an entry be escalated, but opening a formal Investigation — and certainly adopting any resulting Proposal — requires a human decision, matching `../ai-organization/FOUNDING-CHARTER.md` Section 9 and Discovery Lab's Principle 0 exactly. |

This document does not name a specific person with final authority over
any of the above — see Section 9 (Critical Review) and the
already-existing open governance questions in `../ai-organization/
HIRING-LIFECYCLE-DRAFT.md` and `../ai-organization/FOUNDING-CHARTER.md`,
neither of which this document resolves either.

---

## 7. Metrics

Explicitly avoiding vanity metrics (raw entry counts):

- **Intake friction time** — measured or estimated time from Inbox to
  Ledger, target under 30 seconds. A process-health metric, not a
  volume metric.
- **Classification latency** — time an entry spends `UNCLASSIFIED`
  before Weekly Curation resolves it.
- **Conversion rate: Ledger → Investigation** — the fraction of entries
  ever escalated to a formal Investigation. Expected to be small; this
  metric tracks selectivity, not productivity.
- **Investigation yield** — the fraction of Investigations that
  actually produce a Proposal, versus dead-ending in no finding or
  insufficient evidence. This measures whether escalation judgment is
  good, not how many Investigations happen.
- **Proposal adoption rate** — the fraction of Proposals a human
  actually adopts. This is the same concept as the `acceptance_rate`
  metric already defined, but not implemented, in `PROP-0001`'s
  Recommendation Ledger section — this document reuses that name and
  definition rather than inventing a second one.
- **Organizational impact** — for adopted Proposals, whether they led to
  an actual change in a real destination repository. This is the same
  question `../ai-organization/ORB/ORB-REVIEW-TEMPLATE.md`'s Q4 ("did it
  deliver real value?") already asks of a single employee's run; this
  document does not
  propose a separate scoring mechanism for it and instead points back
  to ORB's own existing one.
- **Duplicate/merge rate** — the fraction of entries that turn out to be
  duplicates. A signal about submission clarity, not itself good or
  bad.

No single aggregate score combines these, matching AG-001's own
`../ai-organization/employees/AG-001-repository-observer/METRICS.md`
precedent ("no aggregate trust score in v0.1"). None of
these metrics has been measured yet — the Ledger does not exist, and no
entry has been submitted.

---

## 8. Repository Structure (recommended, not created)

```
docs/
  intake/
    INTAKE-SPEC.md          — this document's Section 1, split out on adoption
    LEDGER-SPEC.md          — this document's Section 2, split out on adoption
    LEDGER.md               — one table row per entry (short entries inlined;
                               long ones referenced into entries/)
    entries/
      DIS-NNNNNN.md         — full original text for entries too long to
                               inline in LEDGER.md
    CURATION-PROTOCOL.md    — this document's Section 5, split out on adoption
  proposals/
    PROP-0002-discovery-intake-system.md   — this document, staying here
                                              until/unless adopted
  investigations/           — unchanged; Origin Artifacts and Investigations
                               continue to live here under the existing
                               INV-/DL- convention
```

**Why `docs/intake/` and not `docs/ai-organization/`.** Intake is core
Discovery Lab infrastructure for *any* entry, not something specific to
AI Organization's employees — it deserves its own top-level namespace,
parallel to `investigations/` and `proposals/`, rather than living
inside a directory scoped to AI Organization Roles and processes.

**Why a hybrid `LEDGER.md` + `entries/` rather than one file per
entry, or one giant file.** A single growing file, in table form, keeps
short entries (the common case, if Principle 7's 30-second goal is
being met) cheap to browse and diff. A dedicated file per long entry
avoids forcing a large block of text into a single wide table cell.
This tradeoff is not free — see Critical Review, Section 9.

**No part of this structure is created by this document.** Per "no
implementation," it is a recommendation only, to be built if and when
this proposal, or some version of it, is adopted.

---

## 9. Critical Review

Written after the design above, as a separate, deliberately adversarial
pass, per instruction. Nothing below is fixed in the sections above —
findings are recorded here only.

**Hidden complexity**

1. The `LEDGER.md` + `entries/` hybrid (Section 8) introduces an
   undefined branch point — "is this entry short enough to inline?" —
   with no threshold specified. Left undefined, this could itself
   become a source of hesitation at exactly the point (submission) that
   is supposed to take under 30 seconds.
2. Three overlapping, non-identical pipelines now exist in this
   repository with no document reconciling them: `PROP-0001`'s
   information-flow map (`Reality → Observation → Candidate
   investigation → Experiment → Evidence → Review/falsification →
   Decision → Graduation, rejection, or deletion → Destination
   repository`), `../ai-organization/FOUNDING-CHARTER.md` Section 4's
   Evolution pipeline (`Observation → Investigation → Experiment →
   Review → Decision → Adoption`), and this document's own Intake
   Workflow (`Reality → Inbox → Intake → Ledger → Classification →
   Origin Artifact → Investigation → Proposal → Adoption`). A newcomer
   would need to reconcile three similar-looking models of "how change
   happens here" without being told how they relate.

**Premature bureaucracy**

3. A fixed, closed four-type taxonomy (Observation/Question/Idea/
   Anomaly) is defined at v0.1, before a single real entry has ever
   been classified under it. If it turns out to be missing a needed
   category, fixing that is a governance change (per `../ai-
   organization/FOUNDING-CHARTER.md` Section 4's "never by direct
   edit"), not a data correction — a heavier fix than the situation may
   warrant this early.
4. A fixed weekly cadence for Curation is asserted without evidence that
   weekly is the right frequency. For a Ledger that may hold very few
   entries early on, weekly curation could itself be process overhead
   applied to an almost-empty queue.

**Unnecessary classifications**

5. The Ledger schema (Section 2) specifies `related_entries` and
   `promoted_to` as distinct fields, plus a five-value `status` enum,
   before any real entry has tested whether this level of structure is
   needed. By this document's own Section 3 reasoning (why entries stay
   unclassified until evidence justifies a label), this schema is
   itself an unclassified idea being treated as settled.

**User friction**

6. Section 2 requires `source` and `author` on every entry. Section 4
   describes these as "often auto-derivable from context" without
   specifying how, given the explicit constraint that no automation may
   be introduced. As written, satisfying these two fields may require
   the submitter to stop and think about phrasing — in direct tension
   with the 30-second target this document otherwise holds as
   fundamental.

**Traceability gaps**

7. The requirement that an Investigation "cite" its originating Ledger
   entry (Section 2) has no enforcement mechanism. Elsewhere in this
   repository, evidence rules are paired with a check — AG-001's own
   evidence-citation requirement, or an ORB Review's compliance
   verdicts. Here, the citation requirement exists only as prose.
8. Section 4 does not specify what happens to an entry that is never
   classified — no timeout, no default disposition, no forcing
   function. Per the Memory principle this is not itself a problem
   (nothing needs to be deleted), but it does mean indefinite
   `UNCLASSIFIED` status is indistinguishable, from outside, between "we
   deliberately chose to leave this open" and "no one ever got to it."

**Governance ambiguity**

9. "Any authorized Classifier" (Section 6) does not name who is
   actually authorized. This is now the third document in this
   repository — after `../ai-organization/HIRING-LIFECYCLE-DRAFT.md` and
   `../ai-organization/FOUNDING-CHARTER.md` — to carry forward the same
   unresolved "who is the human/authority here" question without
   resolving it.
10. Section 3 reuses "Observation" as a first-class Entry Type name.
    `PROP-0001`'s ground rule 1 names this exact word as reserved,
    already load-bearing in KOD's Knowledge Domain and trust-engine's
    Observation Memory, and requires a disambiguation note wherever
    reused — no such note is added here.
11. This document's own workflow (Section 4) reuses "Investigation"
    (already the subject of a disambiguation note in `PROP-0001`) and
    assumes the reader already knows that distinction, without
    restating or extending it here.

**Scalability problems**

12. A single, flat, growing `LEDGER.md` table has no partitioning
    scheme (for example, by month or quarter), unlike
    `docs/investigations/`'s natural partitioning into one file per
    numbered entry. At large entry counts this file will become
    unwieldy to read or diff.
13. Weekly Curation by a single Curator does not scale with entry
    volume, and this document defines no process for multiple curators,
    conflicting classifications, or load-balancing.
14. The relationship between Intake volume and AI Organization Role
    output is not addressed, and the evidence already available in this
    repository suggests it should be: AG-001's single existing run,
    `RUN-0001`, alone produced 5 confirmed changes, 6 current-state
    observations, 3 structural signals, 1 insufficient-access item, and
    2 unknowns — 17 distinct findings from one run of one Role. If each
    such finding became a separate Ledger entry, Intake volume could
    scale far faster than a weekly, single-Curator review process can
    absorb, well before AI Organization has more than one active Role.

Fourteen findings, spanning all seven requested categories. None are
fixed above; all remain open for a human, or a future Investigation, to
weigh.
