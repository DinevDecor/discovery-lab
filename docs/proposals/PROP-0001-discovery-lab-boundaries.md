# PROP-0001 — Discovery Lab Mandate: Three Variants and a Recommendation

Status: DRAFT PROPOSAL — not accepted, not an ADR (revision 3, post-adversarial-review)
Date: 2026-07-24
Author: Implementer session (Claude Code)
Depends on: `docs/investigations/INV-0001-discovery-lab-mandate.md` and
  `docs/investigations/INV-0002-independent-architecture-passes.md`
  (diagnosis — read those first; this document proposes solutions only)

## Revision note

This revision replaces the first draft of PROP-0001. The three variants
below are rebuilt from three independent, isolated architecture passes
over KOD, generative-discovery-engine, and trust-engine (`INV-0002`),
rather than from the lighter single-agent survey used in the first
draft. The variants are also deliberately re-checked for being
*genuinely* distinct — each has different entry criteria, exit criteria,
and governance burden, not just different prose describing the same
mechanics. Nothing from the first draft is treated as accepted; this is
still entirely DRAFT.

## How to read this document

Nothing here is accepted. No variant is adopted by writing it down. A
recommendation is given at the end, but it is explicitly marked as
unaccepted and requires a human decision — the same discipline
`generative-discovery-engine/adr/ADR-0001` applies to itself: AI may
draft, propose, and recommend; it may not finalize.

---

## Principle 0

> **Discovery Lab never creates truth. It only observes, compares, and
> identifies inconsistencies, and proposes next steps — an experiment, a
> correction, or a question — for the owning repository to accept or
> reject through its own governance. Discovery Lab itself never accepts,
> finalizes, or applies any of these proposals.**

This is the frame every other rule in this document derives from. It was
added and reworded during the adversarial review recorded at the end of
this document (see "Adversarial Review — vFinal"): the original candidate
wording said Discovery Lab "proposes experiments," which overclaims —
under the recommended Variant B, the Experiment stage is dormant, so the
principle is worded to cover whichever next step is actually authorized
(currently: a proposal, nothing more) without hard-coding a capability
Discovery Lab does not yet have.

---

## Shared ground rules (apply to all three variants)

These follow directly from the overlaps and risks identified in
`INV-0001` and `INV-0002`, and apply regardless of which variant (if
any) is eventually chosen:

1. Discovery Lab never uses **Observation, Hypothesis, Evidence,
   Experiment, or Review** as its own first-class artifact type names
   without qualification. These words are simultaneously load-bearing,
   specifically-defined terms in KOD (Knowledge Domain), Trust Engine
   (Observation/Evidence Memory, Structured Experience, Review
   Protocol), and GDE (pre-registered Experiment, Critical Review) —
   reusing any of them unqualified collides with all three at once, not
   just one. Where a genuinely analogous but lighter-weight concept is
   needed, it is named differently and scoped explicitly (see the
   disambiguation note in the recommendation section below).
2. Discovery Lab never re-implements a discovery-method validation
   pipeline (pre-registration, frozen protocol, PASS/FAIL verdict
   registry) — that is GDE's fully-specified territory.
3. Discovery Lab never re-implements a context-scoped trust-scoring or
   trust-mutation pipeline (proposal → approval → applied update,
   ledgered) — that is trust-engine's fully-specified territory.
4. Discovery Lab never writes to another repository's registry or
   state file. It may only *propose* a change for a human, or that
   repository's own process, to apply — this is Principle 0 applied
   mechanically to registries and state files specifically.
5. Every artifact Discovery Lab produces has an explicit fate: it
   either graduates to a named receiving repository, or it is marked
   SUPERSEDED/EXPIRED with a date. Nothing sits indefinitely in an
   ambiguous "still relevant?" state.
6. No ADR in Discovery Lab is marked ACCEPTED unless an existing record
   shows a human accepted it.

---

## Variant A — Experiment Laboratory

**Primary purpose.** A bounded technical sandbox for prototyping
implementation-level questions about pieces of architecture that another
repository has already specified but not yet built — e.g. trust-engine's
Mechanism Trust Layer and Meta Trust Layer, which `INV-0002` found to be
fully documented (`mechanism_trust_architecture_v1.md`,
`meta_trust_layer_architecture.md`, etc.) with zero corresponding code.
Never for knowledge claims, discovery-method claims, or trust claims —
only for "does this specific, already-specified technical approach
work."

**Owned artifacts.** Throwaway prototype code; a dated spike brief
(question + reference to the specification it tests + expiry date); a
dated result note (worked / did not work / inconclusive).

**Prohibited artifacts.** Anything claiming to be a Research Session,
Hypothesis, discovery method, or trust score; production code meant to
run unattended; speculative prototyping with no existing specification
to test against (Discovery Lab must not invent architecture, only test
already-written architecture); any registry entry outside discovery-lab
itself.

**Entry criteria.** The technical question must cite an existing,
already-written specification in the owning repository. No speculative
or unspecified prototyping is permitted — this is the mechanism that
prevents Discovery Lab from inventing architecture under this variant.

**Exit / graduation criteria.** The spike produces a verdict within its
stated expiry window. Graduation means a real commit lands in the owning
repository (e.g. trust-engine), reviewed by that repository's own
process — a note in discovery-lab claiming "this is done" is never
graduation by itself.

**Deletion rules.** Every spike carries a hard expiry date set at
creation. If ungraduated by expiry, it is deleted or archived; no silent
extensions — a new expiry requires a new dated spike entry.

**Relationship to KOD.** May prototype pieces of KOD's own
`Infrastructure/python` layer only if KOD's own Foundations/Core
documents already describe that piece unbuilt. Never invents
Foundations-layer concepts (Observation, Hypothesis, Research Session
remain KOD's exclusively).

**Relationship to generative-discovery-engine.** None. GDE has no
unimplemented code surface of this kind — it is a validation-methodology
repository, not primarily a code repository. Discovery Lab must not
build discovery-method tooling under this variant.

**Relationship to trust-engine.** The primary candidate consumer.
`INV-0002` found a concrete, existing, spec'd-but-unbuilt surface
(Mechanism Trust Layer, Meta Trust Layer) that this variant could
prototype pieces of before a real trust-engine commit — strictly bounded
by trust-engine's own existing specification, never extending it.

**Relationship to project-memory.** None directly. A graduated spike is
never registered in project-memory unless the receiving repository's own
status changes as a result, and that change is recorded by the
receiving repository, not by Discovery Lab.

**Principal failure mode.** Prototype code becomes a de facto production
dependency without ever passing through the owning repository's real
review/commit process — "shadow production."

**Governance burden.** LOW. Single author, no independent reviewer
required, because nothing produced here is ever treated as true or valid
until it separately passes the owning repository's own gate.

---

## Variant B — Ecosystem Observatory

**Primary purpose.** Read-only, cross-repository evidence and health
investigation — checking whether a repository's self-reported status
(state file, registry) still matches what is actually verifiable in its
own committed content, and routing findings to whichever repository
actually owns that class of claim.

**Owned artifacts.** Dated investigation reports, each ending in an
explicit verdict (confirmed / contradicted / insufficient evidence) and
tagged with an intended destination repository if the finding implies a
change.

**Prohibited artifacts.** Any code; any prototype; any artifact that is
itself a Hypothesis, discovery method, or trust score — those must be
handed to the owning repository's own process, never decided here.

**Entry criteria.** A specific, falsifiable question about the
ecosystem's actual current state (e.g. "does trust-engine's documented
Mechanism Trust Layer have any corresponding implementation?"). No
open-ended, unscoped "look around and see" investigations. The set of
repositories Discovery Lab is allowed to inspect is fixed by the mandate
that authorized the current review cycle (see "Ecosystem Health Review
v0.1" below); expanding that list is a mandate change, not a decision a
future review may make on its own — this prevents scope drift from
happening gradually, one review generation at a time, instead of all at
once and visibly (see Adversarial Review — vFinal, Risk 3).

**Exit / graduation criteria.** The investigation ends in confirmed /
contradicted / insufficient evidence. If the finding implies a change,
it is filed as a proposal in the destination repository's own terms
(e.g. a suggested diff to `PROJECT_REGISTRY.md`) — never applied
directly by Discovery Lab.

**Deletion rules.** Reports are never deleted. A report superseded by a
later investigation of the same question is marked SUPERSEDED with a
date and kept — an append-only evidence trail, matching the convention
already used in `project-memory/notes/`. To prevent unbounded
accumulation over long timescales, SUPERSEDED reports are moved into an
`archive/` directory (mirroring project-memory's own `archive/`
convention) once **either** 12 months have passed since they were
superseded **or** more than 20 non-archived reports exist, whichever
comes first — a concrete, checkable trigger, not an optional "later"
(the first draft of this rule used vague language that would not have
reliably fired; see Adversarial Review — vFinal, Risk 4). Archiving never
destroys content.

**Relationship to KOD.** Read-only inspector of KOD's Registry,
`PROJECT_STATE.md`, and ADRs. May propose but never apply a correction.
**Explicit non-duplication note:** KOD's own Research Guardian already
performs process-compliance checking — verifying observations are
separated from interpretation, falsification attempts preserved,
reasoning traceable — but strictly *inside* a single Research Session.
Discovery Lab's C1–C3 checks (see "Ecosystem Health Review v0.1") are a
structurally similar act (checking whether a stated claim satisfies its
own evidentiary standard) applied *across* repository boundaries instead
of within one Research Session. This is close enough to warrant an
explicit boundary: Discovery Lab must never run this kind of check
*inside* a KOD Research Session — that is the Research Guardian's
exclusive territory — only across or outside them (see Adversarial
Review — vFinal, Risk 2).

**Relationship to generative-discovery-engine.** Read-only inspector of
GDE's `registry/` and `STATE.md`. May flag if GDE's claimed phase does
not match its registry's actual contents.

**Relationship to trust-engine.** Read-only inspector of trust-engine's
architecture-vs-implementation gap and its many `*_validation_report.md`
self-audits. The 60-document/15-module gap `INV-0002` found is itself an
example of exactly this variant's output.

**Relationship to project-memory.** The primary downstream recipient for
project-status-shaped findings. Project-memory remains the sole
authority to actually edit `PROJECT_REGISTRY.md` / `PROJECT_STATE.md`.

**Principal failure mode.** Becomes a passive audit archive nobody acts
on, because it has authority to observe but not to change anything, and
no receiving repository has an obligation to respond.

**Governance burden.** LOW-MEDIUM. No independent reviewer role is
defined yet — the report author is currently also the classifier. This
is a real, open gap, carried forward as an unresolved question below,
not silently resolved.

---

## Variant C — Combined Lab + Observatory

**Primary purpose.** Both A and B under one roof, on the premise that an
Observatory finding (e.g. "trust-engine's Mechanism Trust Layer is
spec'd but unbuilt") can directly motivate a Lab spike (prototype a
piece of it) — the two feed each other.

**Owned artifacts.** The union of A's and B's artifacts, but every
artifact must be filed under one of two top-level namespaces
(`experiments/` vs `investigations/`) at creation time — no artifact may
exist without that classification.

**Prohibited artifacts.** The union of A's and B's prohibitions, plus: an
investigation finding may not be used to justify a spike without the
spike being separately opened as its own dated artifact — no silent
conversion from one track to the other.

**Entry criteria.** The union of A's and B's entry criteria, plus a
mandatory triage step: every new item must be classified
investigation-track or experiment-track *before* work starts. This is a
genuinely additional decision point neither A nor B needs alone.

**Exit / graduation criteria.** The union of A's and B's, run
independently; the only addition is an optional cross-link field ("this
experiment was motivated by investigation INV-00xx") used only when the
feedback loop is actually exercised.

**Deletion rules.** The union of A's and B's, but requires the
directory-level separation (`experiments/` vs `investigations/`) to be
actively maintained — a housekeeping burden neither A nor B carries
alone.

**Relationship to KOD / generative-discovery-engine / trust-engine /
project-memory.** The union of A's and B's relationships to each,
unchanged.

**Principal failure mode.** The two purposes blur: a technical spike
gets justified retroactively by a vague "ecosystem finding" that was
never itself written down and reviewed, or an investigation report
quietly turns into prototype code without ever being logged as a
distinct experiment. This is the literal miscellaneous-dumping-ground
failure mode the task explicitly warns against, and it is structurally
*more* likely here than in A or B alone, because there is no natural
boundary forcing separation — it depends entirely on continued triage
discipline holding.

**Governance burden.** HIGH. Requires both A's and B's review/expiry
mechanics running simultaneously, the added mandatory triage step,
active directory discipline, and (whenever the feedback loop is used)
tracking cross-links between the two tracks. This is a materially
higher governance burden than A or B individually, which is the
confirmation that C is a genuinely distinct variant and not a cosmetic
combination of the other two.

---

## Are the three variants genuinely distinct?

Checked explicitly, since cosmetic renaming was a named risk:

- **Entry criteria differ in kind, not just wording.** A requires an
  existing unimplemented specification to test; B requires a
  falsifiable cross-repo question; C requires both of those *plus* a
  triage classification step that neither A nor B has.
- **Deletion mechanics differ.** A hard-deletes/archives on expiry; B
  never deletes, only supersedes; C must run both mechanics correctly at
  once without letting them merge.
- **Governance burden is ordered, not equal**: LOW (A) < LOW-MEDIUM (B)
  < HIGH (C), and the reasons are structural (single review path vs. no
  review path vs. two review paths plus triage plus directory
  discipline), not merely descriptive.
- **Principal failure modes are different in mechanism**: A fails by
  quietly becoming production; B fails by being ignored; C fails by the
  two tracks blurring into each other — three distinct ways to fail, not
  one failure mode described three ways.

---

## Recommendation (proposed, not accepted)

**Recommended: Variant B — Ecosystem Observatory, alone, for now.**

**1. Evidence basis.** Three independent lines of evidence support this,
all drawn from `INV-0001` and `INV-0002`:

- Two concrete precedents of Observatory-shaped work already happening
  in practice, ad hoc, with nowhere proper to live
  (`project-memory/notes/2026-07-19-dinev-decor-systems-location-
  check.md` and `project-memory/notes/2026-07-24-discovery-lab-
  recovery.md`).
- All three independently-reviewed repositories (KOD, GDE, trust-engine)
  are strictly inward-facing — none has any documented awareness of the
  other two, of discovery-lab, or of project-memory (`INV-0002`
  synthesis, "Gaps").
- The independent trust-engine pass itself produced a live example of
  Observatory-shaped value during this very investigation: a genuine,
  previously-undocumented 60-document/15-module specification-vs-
  implementation gap, found by simply reading the repository's own
  files against each other — proving the role's usefulness empirically,
  not just by argument.

**2. Why Variant A was not selected.** No repository has *requested*
prototyping help. The one concrete candidate need identified
(trust-engine's spec'd-but-unbuilt Mechanism/Meta Trust Layer) was
inferred by this analysis, not evidenced by an actual ask from
trust-engine's own docs. Adopting Variant A now would be building
capacity for a need that is speculative rather than observed — exactly
the premature-abstraction risk the task warns against ("the right idea
at the wrong time is still a methodological error").

**3. Why Variant C was not selected.** C's added governance burden
(mandatory triage, directory discipline, cross-link tracking) is only
justified if the observatory→lab feedback loop is actually valuable,
which cannot be established until Variant B alone has run at least once
and shown its outputs are worth acting on. Adopting C now assumes the
answer to a question Variant B alone hasn't been given the chance to
test yet.

**4. Assumptions that still require validation** (none of these are
resolved by this document):

- That findings routed to KOD, GDE, trust-engine, or project-memory as
  proposals will actually be looked at and acted on by those
  repositories' own maintainers — untested; no receiving process has
  agreed to this.
- That a report author acting as their own classifier (no independent
  reviewer defined for Discovery Lab yet) does not introduce meaningful
  bias at this early scale.
- That trust-engine's specification-vs-implementation gap is intentional
  paced roadmap sequencing rather than a symptom of exactly the drift
  problem Discovery Lab would want to catch — this cannot be resolved
  without asking trust-engine's own maintainers, which is out of scope
  for this document.

**5. No ownership claimed elsewhere.** Variant B explicitly does not
claim: KOD's Constitution, knowledge-lifecycle, or falsification-
enforcement authority (Observatory does not evaluate whether a
Hypothesis is true — only whether a stated status matches observable
fact, a narrower and different act); GDE's validation-kernel or
role-separated governance for discovery methods (Observatory never
evaluates whether a *method* works); trust-engine's context-scoped
trust-scoring or mutation-ledger pipeline (Observatory never assigns a
trust score to a model or mechanism).

This recommendation is not an acceptance. It requires a human decision
before any variant governs how discovery-lab is actually used.

---

## Disambiguation note (terminology collision, per ground rule 1)

Discovery Lab's own artifact type, under the recommended Variant B, is
called an **investigation report** (already the convention used in
`docs/investigations/`). This deliberately shares a root word with KOD's
"Investigation," governed by KOD's Investigation Engine inside a single
Research Session. The two are **not the same thing**: KOD's Investigation
organizes Knowledge Objects toward a truth-claim inside one Research
Session; Discovery Lab's investigation report checks whether a stated
fact about a repository's status matches observable reality, across
repository boundaries, and never produces a truth-claim about anything
other than "does the claim match the evidence." Anyone extending this
mandate later should keep this distinction explicit rather than let the
shared word blur the two.

---

## Proposed information-flow map

The task's general information-flow pipeline is: **Reality / external
signal → Observation → Candidate investigation → Experiment → Evidence →
Review / falsification → Decision → Graduation, rejection, or deletion →
Destination repository.**

Under the **recommended Variant B alone**, the *Experiment* stage has no
home in Discovery Lab and stays dormant — it would only activate if
Variant A or C were adopted later. The map below marks this explicitly.

```
 Reality / external signal
   (an actual repository's committed content, at a point in time)
              │
              ▼
        Observation
   (a person notices a specific, checkable question worth asking —
    not logged anywhere yet)
              │
              ▼
     Candidate investigation                    [ACTIVE under Variant B]
   (the question qualifies under entry criteria: specific,
    falsifiable, about ecosystem state — opened as a dated
    docs/investigations/INV-NNNN file in discovery-lab)
              │
              ▼
          Experiment                          [DORMANT under Variant B —
   (a bounded technical test with code)         only active if A/C adopted]
              │
              ▼
           Evidence
   (file citations, quotes, git history — gathered inside the same
    INV report; nothing is asserted without a citation)
              │
              ▼
     Review / falsification
   (currently self-contained: the report's own author classifies the
    evidence — NO independent reviewer role exists yet; this is an
    open gap, not a resolved design)
              │
              ▼
           Decision
   (the report's own explicit verdict: confirmed / contradicted /
    insufficient evidence, recorded in the INV report itself)
              │
       ┌──────┴──────┐
       ▼             ▼
  no further      implies a change
  action needed         │
       │                ▼
       │      Graduation, rejection, or deletion
       │      (a PROPOSAL is drafted and sent to the specific
       │       destination repository; that repository's own
       │       human-gated process decides graduate/reject —
       │       Discovery Lab has no authority to apply it directly)
       │                │
       ▼                ▼
  report stays in   Destination repository
  discovery-lab,     (KOD / generative-discovery-engine / trust-engine /
  marked as-is       project-memory — whichever one's registry or
                      state file the finding actually concerns)
```

### Per-transfer specification

**Transfer 1 — Investigation report → destination repository (proposal
only)**

- Source: `discovery-lab/docs/investigations/INV-NNNN.md`
- Destination: the specific owning repository's own registry/state file
  (e.g. `project-memory/PROJECT_REGISTRY.md`,
  `KOD/Core/Registry/PROJECT_STATE.md`, `generative-discovery-engine/
  registry/*`, or a trust-engine architecture/state document)
- Artifact transferred: a proposed diff or statement, never an applied
  change
- Approval gate: the destination repository's own human-only
  finalization rule — already independently required by all three
  reviewed repositories (KOD's Research Guardian/Engine non-authority,
  GDE's `ADR-0001`, trust-engine's Approval → Applied Update). Discovery
  Lab has no authority to bypass this in any repository.
- What remains behind as provenance: the original INV report stays in
  discovery-lab, unmodified, as the evidence trail. If the destination
  repository accepts the proposal, its own commit references the INV
  report by path — the reference never runs the other direction.

**Transfer 2 — Lab spike → owning repository commit** *(dormant unless
Variant A or C is later adopted)*

- Source: `discovery-lab/experiments/EXP-NNNN` (not authorized under the
  recommended Variant B)
- Destination: the owning repository's actual codebase (e.g.
  trust-engine's `Infrastructure`/module tree)
- Artifact transferred: real code, reviewed and re-committed through the
  owning repository's own normal review process — never copy-pasted in
  directly
- Approval gate: the owning repository's own code review process
- What remains behind as provenance: the spike brief and result note
  stay in discovery-lab, marked GRADUATED with a link to the receiving
  commit.

### Where each pipeline question is answered

- **Where observations enter:** informally, in a person's head, until
  they qualify as a Candidate investigation under Variant B's entry
  criteria.
- **Where experiments run:** nowhere, under the recommended Variant B.
- **Where reviews happen:** inside the investigation report itself —
  currently self-classified, no independent reviewer (open question).
- **Where validated knowledge graduates:** to whichever specific
  repository already owns that class of claim — never to Discovery Lab
  itself, which is never authoritative for anything outside its own
  internal state.
- **Where project status is recorded:** only in `project-memory/
  PROJECT_REGISTRY.md` and `PROJECT_STATE.md`. Discovery Lab's own
  `STATE.md` records only Discovery Lab's own internal state.

---

## Recommendation quality: interface definition only (not implemented)

Variant B's own principal failure mode is "becomes a passive audit
archive nobody acts on." There is currently no way to tell, even in
principle, whether that is happening — Discovery Lab has no record of
what happened to the proposals it routes out (Transfer 1 in the
information-flow map above). This section defines the interface for
tracking that. **Nothing in this section is implemented.** No file, no
automation, no schedule is created by this document.

**Why this is architecturally necessary, not optional polish:** without
it, "Assumption requiring validation #1" in the Recommendation section
above (do receiving repositories act on routed proposals?) can never be
checked — it would stay permanently untestable, which defeats the point
of naming it as an assumption at all.

**Proposed artifact: a Recommendation Ledger**, one entry per proposal
routed out via Transfer 1, with fields:

```
recommendation_id: <id>
source_investigation: <path to the INV-NNNN report that produced it>
destination_repository: <KOD | generative-discovery-engine | trust-engine
                          | project-memory>
date_proposed: <date>
status: PROPOSED | ACCEPTED | REJECTED | PENDING_NO_RESPONSE | INSUFFICIENT
date_status_recorded: <date, when status last changed>
```

**Status discipline (this is the part that must not be gotten wrong):**
`status` is set only from the destination repository's own recorded
decision — never inferred by Discovery Lab itself. In particular,
**silence is never treated as REJECTED.** If a destination repository has
not responded after a stated waiting period, the status is
`PENDING_NO_RESPONSE`, a distinct value — collapsing "no answer" into
"answer was no" would let Discovery Lab quietly assign an outcome that
belongs exclusively to the destination repository's own governance,
violating Principle 0 (see Adversarial Review — vFinal, Risk 6).

**Metrics (interface only, not computed by this document):**

- `total`, `accepted`, `rejected`, `pending_no_response`, `insufficient`
- `acceptance_rate = accepted / (accepted + rejected)`, explicitly
  excluding `pending_no_response` and `insufficient` from the
  denominator, since neither represents a governance decision yet.

**Naming caveat — read before using this number anywhere:**
`acceptance_rate` measures whether a destination repository's own
governance *agreed* with a Discovery Lab proposal. It is **not** a
measure of objective correctness, and must never be called "precision"
without this caveat attached. Discovery Lab has no oracle for whether an
accepted proposal was actually right, or a rejected one actually wrong —
claiming otherwise would directly violate Principle 0. This naming
problem was caught during the adversarial review recorded at the end of
this document (see "Adversarial Review — vFinal," Part 1B) and is the
reason "precision" is avoided as the metric's name here.

This ledger has no home yet (no file has been created for it) and is not
populated until at least one recommendation exists to track — it should
not block the first run of Ecosystem Health Review v0.1 below.

---

## First experiment: Ecosystem Health Review v0.1

The smallest experiment that could test whether the recommended mandate
(Variant B) is actually useful, small enough to finish manually before
any automation is considered.

**Research question.** For each in-scope repository, does its own
self-reported status (a state file, plus registry entries) accurately
reflect what is actually verifiable in that repository's own committed
content, as of a fixed observation date?

**Repositories in scope (fixed list, no dynamic discovery).** KOD,
generative-discovery-engine, trust-engine, project-memory, and
discovery-lab itself (self-check). No repository may be added to scope
mid-review — this bounds the experiment and prevents Discovery Lab from
turning into an open-ended command center.

**Fixed review criteria (frozen before running, in the spirit of GDE's
own Threshold Freeze Rule — not changed after evidence is seen).** For
each repository, check exactly three things, no more:

- **C1 — Status vs. reality.** Does the repository's status/state field
  match what is observable (e.g. "ACTIVE" claimed but no recent
  commits, or no registry activity matching the claim)?
- **C2 — Lifecycle vs. artifacts.** Does the repository's own claimed
  lifecycle stage (a sprint, a phase, an MVP slice) match what is
  actually implemented or committed? A gap counts as "planned, not a
  finding" **only if a specific file in the repository itself can be
  cited stating the gap is intentional and sequenced** (a roadmap entry,
  a phase document, an explicit "not yet implemented" note). Absent such
  a citable artifact, the gap is recorded as MISMATCH (or INSUFFICIENT
  if it cannot be checked at all) — never silently assumed intentional.
  This keeps C2 an observation ("is there a citable planning document?
  yes/no") rather than an inference about another team's intent, which
  would smuggle interpretation into a check that must stay observational
  (see Adversarial Review — vFinal, Risk 1).
- **C3 — Internal consistency.** Does the repository's own doc set
  cross-reference consistently — no document claims something is DONE
  that another document in the same repository contradicts?

**Evidence requirements.** Every claim must cite a specific file path
and a short quote or line reference. No verdict may rest on "seems
like" or on memory from a prior, differently-scoped pass — each
criterion must be freshly verified against the repository's current
content at review time.

**Output schema (per repository):**

```
repo: <name>
observation_date: <date>
C1_status_vs_reality: MATCH | MISMATCH | INSUFFICIENT_EVIDENCE   (+ citation)
C2_lifecycle_vs_artifacts: MATCH | MISMATCH | INSUFFICIENT_EVIDENCE (+ citation)
C3_internal_consistency: MATCH | MISMATCH | INSUFFICIENT_EVIDENCE (+ citation)
evidence_coverage: <per-criterion note on which relevant documents were
  checked vs. not checked, and why — no formula defined yet; see
  "Evidence Coverage" below>
repo_verdict: PASS | PARTIAL | FAIL | INSUFFICIENT
notes: <optional>
```

**Evidence Coverage.** A defined field, not a computed metric — there is
not yet enough information to fix a formula (what counts as "all
relevant evidence" is not comparable between a 5-file repository and a
60-plus-document one). Its role is to record, per criterion, what was
actually checked versus what exists but was not checked, and why —
distinguishing "I reviewed everything relevant and still can't tell"
(genuine INSUFFICIENT_EVIDENCE) from "I checked one document out of many
and called it MATCH" (a shallow verdict that looks confident but isn't).
A concrete formula should only be proposed after Ecosystem Health Review
v0.1 has actually run once and shown what "relevant evidence" looks like
in practice for repositories of very different sizes.

**Verdict rubric (fixed, frozen before running).**

- **PASS** — all three criteria MATCH.
- **PARTIAL** — exactly one criterion MISMATCH, none INSUFFICIENT.
- **FAIL** — two or more criteria MISMATCH.
- **INSUFFICIENT** — any criterion cannot be evaluated for lack of
  accessible evidence; this overrides PARTIAL/FAIL if the evidence gap
  is the actual limiting factor, not a MISMATCH.

No single aggregate score is produced across repositories — the
repositories are structurally different, and forcing one number would
misrepresent them. The experiment reports per-repository verdicts only.

**Experiment-level success is procedural, separate from what is
found**, following GDE's own necessity/sufficiency labeling discipline:
the experiment succeeds as a *process* if every in-scope repository
receives a cited verdict, regardless of what that verdict is.

**Stop rule.** Exactly one review pass per repository. No re-checking a
repository after seeing another repository's result, to avoid criteria
drift or cross-repository observer bias. The whole review must complete
within one sitting — no multi-day investigation. It must not trigger any
write to another repository; a MISMATCH is recorded as a finding and
optional proposal only, never auto-corrected.

**Success conditions (does this validate the Observatory mandate?)**

- At least one genuine MISMATCH or INSUFFICIENT is found, with a
  citation-backed reason — proving the review can detect real drift, not
  just rubber-stamp everything PASS.
- The process completes manually, within scope, without needing write
  access to any other repository.
- The resulting report is specific enough that a human could act on it —
  not just a vague "looks fine."

**Risks of false positives.**

- A MISMATCH could be wrongly flagged when a repository's status is
  intentionally ahead of or behind its documentation by design (e.g.
  trust-engine's Mechanism Trust Layer being spec'd-but-unbuilt could be
  normal, sequenced roadmap staging rather than drift). The reviewer
  must check for an explicit roadmap/phase statement before flagging C2
  as MISMATCH, not just the raw presence of a gap.
- Reviewer bias from having recently read a repository for an unrelated
  purpose (as happened in this very session) could inflate confidence
  in a finding without fresh verification — mitigated by the evidence
  requirement above: every criterion needs a fresh citation, not a
  reused prior conclusion.

**What result would invalidate the recommended mandate.**

- If every repository scores PASS with no findings worth routing
  anywhere, that would suggest the Observatory role adds no value beyond
  what each repository's own state file already shows — undermining the
  evidence basis for recommending Variant B.
- If, when a finding is drafted as a hypothetical proposal, there is no
  realistic mechanism or willingness for the destination repository to
  ever act on it, that would suggest Variant B's core value proposition
  (findings get routed and acted on) does not hold, and the mandate
  needs rethinking.
- If the experiment cannot be completed manually within a single sitting
  for just five repositories, that would suggest the Observatory
  approach does not scale even at the smallest possible test size,
  invalidating the "smallest first experiment" premise itself.

This experiment is **proposed only**. It is not implemented, no agent is
created to run it, and no recurring monitoring is scheduled by this
document.

---

## Self-critique

Run against the specific failure modes named in the task:

- **Hidden duplication.** Found and fixed: the generic pipeline stage
  "Candidate investigation" and Discovery Lab's own "investigation
  report" artifact share a root word with KOD's "Investigation"
  concept. Addressed explicitly in the Disambiguation note above rather
  than left implicit or renamed away from the task's own requested
  pipeline wording.
- **Vague ownership.** Found, not fully fixed — flagged as an open
  assumption instead of pretending to resolve it: Variant B's Review /
  falsification stage has no independent reviewer defined. The report
  author is currently also the classifier. This is carried forward as
  an unresolved question, not silently decided.
- **Irreversible scope growth.** Checked: the recommended mandate
  (Variant B) is read-only and proposal-only everywhere it touches
  another repository — fully reversible, since nothing is deleted or
  mutated outside discovery-lab itself. The one action with any
  lasting-commitment shape — scheduling recurring monitoring — is
  explicitly not proposed here, per the task's own constraint; the first
  experiment is manual and one-shot only.
- **Circular information flows.** Checked: the flow map's "Decision"
  stage (Discovery Lab's own self-classified verdict) and "Graduation"
  stage (the destination repository's separate, human-gated decision)
  are kept as two distinct steps, not merged. A destination
  repository's updated state does eventually become "Reality" for a
  future investigation — but only after passing through that
  repository's own approval gate each time, never as a direct shortcut
  from Discovery Lab's own verdict back to a new Observation.
- **Missing deletion rules.** Found and fixed: Variant B's original
  "never delete" rule, taken alone, risks unbounded file accumulation
  over long timescales even though nothing individual item is ever
  "orphaned." Addressed by adding an `archive/` consolidation path
  (mirroring project-memory's own `archive/` convention) for very old
  SUPERSEDED reports, without ever destroying content outright.
- **Recommendations unsupported by repository evidence.** Checked: the
  recommendation for Variant B cites three specific, sourced pieces of
  evidence (two project-memory precedents, all-three-repos'
  inward-facing posture, and the trust-engine gap found live during
  `INV-0002`). The one place this document reasons beyond direct
  evidence — Variant A's "candidate future need" from trust-engine's
  unbuilt Mechanism Trust Layer — is explicitly labeled *inferred, not
  requested* and used as a reason to *not* select Variant A yet, which
  is the evidence-humble direction, not an overreach.

---

## Adversarial Review — vFinal

Date: 2026-07-24. An independent, deliberately destructive review pass
over this document as it stood at the end of the "independent
architecture passes" revision — instructed to attack the design, not
defend it. Recorded here in full, including the risks as originally
found, before any fix, per the review's own instructions.

### Part 1 — Evaluation of three candidate additions

**A. Principle 0 — accepted, reworded.** The candidate wording said
Discovery Lab "proposes experiments," which overclaims a capability not
authorized under the recommended Variant B (Experiment stays dormant).
Reworded to "proposes next steps — an experiment, a correction, or a
question" and integrated above, before the Shared ground rules, as the
frame the rest of the document derives from.

**B. Recommendation Precision — accepted, renamed.** Well-motivated: it
is the only way to ever check "Assumption #1" (do proposals get acted
on?) instead of leaving it permanently untestable. But "precision"
implies a correctness oracle Discovery Lab does not have and Principle 0
forbids claiming. Integrated as an `acceptance_rate` metric with an
explicit naming caveat, plus a `PENDING_NO_RESPONSE` status so silence is
never conflated with rejection (see Risk 6 below). Interface only — not
implemented.

**C. Evidence Coverage — accepted, scoped down.** The existing "Fixed
review criteria" require a citation per claim but not comprehensiveness,
so a shallow, cherry-picked citation could currently pass as MATCH.
Integrated as a defined-but-unformulated field in the Ecosystem Health
Review v0.1 output schema. No formula invented, as instructed — there is
not yet enough evidence across repositories of very different sizes to
fix one responsibly.

### Part 2 — Attempting to break Variant B

Risks as originally found, described before any fix was applied:

1. **Hidden interpretation inside a claimed read-only check.** The
   original C2 criterion ("distinguishing a documented, sequenced,
   planned gap from an undocumented one") required the reviewer to infer
   another team's *intent*, not just observe a fact — exactly the
   Observation/interpretation mixing that Trust Engine's own rules
   forbid ("observation must never contain interpretation"). Variant B
   claims to be purely observational; this criterion, as first written,
   was not.
2. **Possible duplication of KOD's Research Guardian.** The Guardian
   already performs process-compliance checking — verifying a claim
   satisfies its own evidentiary standard — inside a Research Session.
   Variant B's C1–C3 checks are a structurally similar act, just applied
   across repository boundaries. The earlier duplication analysis
   checked against KOD's Research Engine (truth-evaluation) and found no
   overlap, but never checked against the Guardian's narrower
   process-compliance function specifically — a real gap in the earlier
   analysis.
3. **Scope is bounded per review, not across review generations.**
   "No repository added mid-review" protects any single Ecosystem Health
   Review, but nothing prevented v0.2, v0.3, etc. from each quietly
   adding repositories on their own — scope inflation spread across
   versions instead of happening visibly, all at once.
4. **The archive trigger was optional language, not a rule.** "Very old
   reports may later be moved" does not reliably fire; a rule that can
   always be deferred is not a rule.
5. **Governance creep from adding two new self-tracking structures at
   once.** A Recommendation Ledger plus an Evidence Coverage field both
   at once nudge Discovery Lab toward tracking its own performance —
   individually justified (Part 1), but worth naming as a real, if mild,
   increase in governance surface. Notably, trust-engine's own Meta Trust
   Layer (a mechanism for validating its own mechanisms) is fully
   specified but still unbuilt in that repository — self-referential
   tracking is evidently hard to get right even for a repository built
   for exactly this purpose.
6. **Recommendation Precision could infer REJECTED from silence.** If a
   destination repository simply never responds, Discovery Lab must not
   decide on its own that this means "rejected" — that would be Discovery
   Lab assigning an outcome that belongs exclusively to the destination
   repository's own governance, in direct violation of Principle 0.

All six risks were judged fixable with precise, minimal, non-scope-
expanding edits — none required reopening the Variant A/B/C decision or
redesigning Variant B. Each fix is applied at its specific location
above (C2's wording, the KOD non-duplication note, the scope-stability
sentence, the archive trigger threshold, the ledger's status discipline)
rather than gathered into a single patch, so each stays next to the rule
it corrects.

### Part 3 — Merge Gate

**Verdict: APPROVE WITH MINOR CHANGES.**

Changes made in response to this review (all applied above, no other
scope added):
- Added Principle 0, reworded from the candidate text.
- Added the Recommendation Ledger interface, with an explicit naming
  caveat and a `PENDING_NO_RESPONSE` status.
- Added the Evidence Coverage field to the Ecosystem Health Review v0.1
  output schema, without inventing a formula.
- Narrowed C2 to require a citable planning artifact instead of inferred
  intent.
- Added an explicit non-duplication boundary against KOD's Research
  Guardian.
- Added a scope-stability rule preventing silent expansion across future
  review generations.
- Replaced the vague archive-consolidation language with a concrete,
  checkable trigger.

No new architectural dependency was introduced. No responsibility was
added to Discovery Lab beyond what Variant B already claimed — every
change either sharpens an existing boundary or defines an interface that
remains explicitly unimplemented. The mandate remains strictly read-only
and proposal-only.

---

## Unresolved questions

- No independent review role is defined for Discovery Lab's own
  investigation reports (GDE has a Critical Reviewer; KOD has a
  Research Guardian; Discovery Lab currently has neither).
- Whether `discovery-lab` should be added as a row in project-memory's
  `PROJECT_REGISTRY.md` is explicitly **not decided here** — per the
  rule already applied to the "Dinev Decor Systems" row in the
  2026-07-19 note, the registry should not change while a repository's
  mandate is still DRAFT.
- Whether Variant A's asserted prototyping need is real cannot be
  resolved by this document — only by an actual observed need arising,
  which has not happened yet in this ecosystem as far as this
  investigation found.
- Whether trust-engine's documentation-vs-implementation gap is healthy
  staged sequencing or a real drift problem is unresolved and would need
  trust-engine's own maintainers to answer — Discovery Lab, under the
  recommended Variant B, can only observe and propose, not decide this.
- Whether a receiving repository (KOD, GDE, trust-engine, project-memory)
  would actually act on a routed proposal is untested — the Ecosystem
  Health Review v0.1 experiment above is designed to start probing this,
  but cannot answer it definitively on its own.
