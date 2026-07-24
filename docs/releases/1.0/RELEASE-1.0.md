# Discovery Lab — Release 1.0

Freeze date: **2026-07-24**
Frozen components: **AG-002 Discovery Archaeologist v1.0 (FROZEN)**,
**AG-003 Knowledge Curator v1.0 (FROZEN)**
Accepted: 2026-07-24, via direct task instruction ("Discovery Lab —
Freeze Release 1.0"), the same acceptance pattern already used for
`ADR-0001`–`ADR-0004` in this repository — a governance decision, not an
architecture decision. This document formalizes it; it does not decide
it independently.

**This is a governance release, not a development release.** No
architecture was redesigned to produce it. No feature was added. Every
change bundled into this freeze (three small corrections from the
Reality Stress Test — see `VALIDATION-HISTORY.md`) was already applied
and committed before this freeze was requested; this release formalizes
their finality, it does not introduce them.

## What has been proven

Both Roles' governing documents (`docs/ai-organization/employees/
AG-002-discovery-archaeologist/`, `docs/ai-organization/employees/
AG-003-knowledge-curator/`) have survived, in order:

1. **Internal design review** — each Role's document set was written
   against, and cross-checked with, the established repository
   discipline (evidence rules, escalation values, boundary/limitation
   lists) already proven by AG-001.
2. **Adversarial self-review** — `docs/proposals/
   AG-003-knowledge-curator-walkthrough/ADVERSARIAL-REVIEW-0001.md`
   found and fixed three real design defects in AG-003 before any real
   data touched it (an unreproducible `confidence` formula, an
   unmechanized merge-reversibility claim, an unsynced `derived_from`
   field).
3. **A real Reality Stress Test** — `docs/proposals/
   AG-003-reality-stress-test/REALITY-STRESS-TEST-REPORT.md` ran both
   Roles, in sequence (AG-002 recovery → AG-003 curation), against four
   structurally different **real** datasets: a personal diary, this
   repository's own governance documents, a separate research
   repository (`kod`), and a separate operational-reports repository
   (`trust-engine`). It found and fixed three further real,
   evidence-linked architecture gaps (`F-1`, `F-2`, `F-3`) and recorded
   one coverage note (`F-4`).

**What specifically held, across all of the above, without exception**:

- AG-002 never edited, reordered, or invented content in any source it
  read (diary, this repository's own ADRs, `kod`, `trust-engine`).
- AG-003 never merged, promoted, or resolved a contradiction
  automatically — every one of its outputs (Knowledge Merge Proposals,
  Relationship Proposals, Core Principle Proposals, Contradiction
  Reports, Knowledge Evolution Reports, Gap Reports) was a proposal, not
  an action.
- AG-003 never overrode an `INSUFFICIENT EVIDENCE` marking AG-002 had
  already recorded.
- Every Knowledge Object and proposal AG-003 produced carried a citation
  back to a specific AG-002 finding — no invented fact was found in any
  of the four datasets.
- Two deliberate hallucination traps (a near-empty KOD excavation
  progress file, a blank KOD Knowledge Object template) and one
  deliberate false-merge trap (a Latin/Cyrillic model-ID collision
  inside a real trust-engine audit) were all handled correctly.
- Terminology disambiguation (KOD's `Registry`/`Knowledge Graph`/
  `confidence` vs. AG-003's own Knowledge Object) held up against real,
  previously-unseen KOD content, not just the material it was originally
  written against.
- A genuine, positive Knowledge Merge Proposal (`KMP-S3-01`, "reality is
  the final arbiter") was filed and recommended, alongside genuine
  declined merges (`KMP-0001`, the "requested ADR-0002" collision) —
  confirming the merge logic is not systematically biased in either
  direction.

## What remains intentionally out of scope

Freezing the architecture is not a claim that everything it could
eventually do has been built or exercised. Explicitly out of scope for
this release, by design, not by oversight:

- **No real Knowledge Base store exists yet.** `memory/knowledge-
  objects/` was never created; every Knowledge Object produced so far
  (in the first walkthrough and the Reality Stress Test) is written
  inline in `docs/proposals/`, deliberately so it cannot be mistaken for
  a filed, accepted Knowledge Base entry. Building that store is future
  work, not part of this freeze.
- **No independent review has occurred.** Every review of AG-003's
  architecture and output to date — the adversarial review, the Reality
  Stress Test — was conducted by the same session that built the
  architecture. `AG-003-knowledge-curator/STATUS.yaml`'s
  `open_governance_questions` still lists "who conducts the first real,
  genuinely independent Knowledge Review or ORB Review" as unresolved.
  This freeze does not resolve it, and does not claim independent
  validation it did not receive.
- **`Validated Principle` and `Core Principle` promotion thresholds have
  never been exercised for real.** Every Core Principle Proposal filed
  to date (`CPP-0001`, `CPP-S3-01`) proposed `Draft → Candidate
  Principle` only — the higher thresholds in `PROMOTION-RULES.md`
  (requiring cross-source convergence, or a 90-day/three-run span) were
  never met by any real Knowledge Object, so they remain unexercised
  specification, not validated behavior.
- **`CI-NNNN` numbering has no collision-prevention mechanism.** The
  Reality Stress Test minted `CI-6` through `CI-10` without incident,
  but nothing stops two concurrent sessions from independently reusing a
  number. Recorded as an open governance question, not fixed in this
  freeze (fixing it would be a real architecture change, out of scope
  for a freeze task that explicitly forbids redesign).
- **No aggregate quality or trust score exists**, by design — this was
  true at v0.1 and remains true at this freeze; a general trust-scoring
  pipeline remains trust-engine's territory (`PROP-0001`, ground rule
  3), not this Role's, at any version.
- **Neither Role has been organizationally adopted.** `adoption_status:
  not_adopted` is unchanged by this freeze — see `GOVERNANCE.md`,
  "Freeze vs. adoption," and `HIRING-LIFECYCLE-DRAFT.md`'s own
  `Candidate → Prototype → Probation → Trusted → Retired` axis, which
  this freeze does not advance.

## Validation history

Full chronological record: `VALIDATION-HISTORY.md`. Summary: 1 internal
design review, 1 adversarial self-review (3 defects found and fixed),
1 Reality Stress Test across 4 real datasets (3 architecture defects
found and fixed, 1 coverage note recorded), 0 independent reviews.

## Known limitations

- Both Roles' only reviewers, to date, have been the same session that
  designed them — see "What remains intentionally out of scope," above.
- AG-002 has processed a small number of real sources (1 diary archive,
  4 governance documents, 7 research documents, 3 operational reports) —
  not a large-scale corpus. Its `METRICS.md` values (`source_coverage`,
  `citation_completeness`, etc.) have real data points but are not
  statistically robust claims.
- AG-003's `maturity: Convergent` and above has never actually been
  reached by any real Knowledge Object — every one built so far tops
  out at `Recurring` (single-source/single-run), per `KNOWLEDGE-OBJECT-
  SPEC.md`'s source-granularity rule (added by this freeze's own
  validation history, `F-2`).
- The `F-4` coverage note (two concrete relationships the first
  walkthrough's limited one-Knowledge-Object scope missed) means a real
  production Knowledge Base build should expect further, currently-
  unknown gaps once it covers a dataset's full finding set — freezing
  the architecture is not the same claim as declaring any given
  Knowledge Base complete.
- **A real, unresolved inconsistency between two validation passes**,
  caught while writing `VALIDATION-HISTORY.md` (its item 16), not before:
  the adversarial review's finding 4 flagged that `maturity: Convergent`
  is exploitable by re-scanning the same source in a second run; the
  Reality Stress Test's `F-2` fix to `KNOWLEDGE-OBJECT-SPEC.md`, written
  to close a *different* ambiguity (file-vs-repository granularity),
  incidentally states that `Convergent` is satisfied by *"two separate
  AG-002 runs over the same"* repository — which does not close finding
  4's loophole, and arguably restates it in the fix's own wording. Left
  unfixed in this freeze, deliberately: this release's task forbids
  redesign, and a proper fix (most likely requiring materially new
  source content, not just a new run ID) deserves its own evidence-linked
  pass. See `LESSONS-FROM-V1.md`.

## Acceptance criteria (met, before this freeze was recorded)

1. A complete, internally consistent document set exists for both Roles
   (Contract, Role, Inputs, Outputs, Limitations, Checklist, Metrics,
   Prompt, Status, History, plus AG-003's Knowledge Object spec,
   lifecycle, relationship ontology, promotion rules, review protocol,
   and curation protocol). **Met.**
2. An adversarial review was conducted against the architecture, found
   real defects, and those defects were fixed before being called
   resolved. **Met** — `ADVERSARIAL-REVIEW-0001.md`.
3. A real, falsification-oriented stress test was conducted against real
   data from more than one structurally different source, actively
   hunting for the specific failure modes governance/curation
   architectures are prone to (false merges, missed contradictions,
   hallucinated findings, confidence inflation, circular relationships).
   **Met** — `REALITY-STRESS-TEST-REPORT.md`.
4. Every defect found in (2) and (3) was either fixed with a minimal,
   evidence-linked correction, or explicitly recorded as an accepted,
   named limitation — never silently dropped. **Met** — see "Known
   limitations," above, and `VALIDATION-HISTORY.md`'s full defect
   ledger.
5. A freeze recommendation was actually returned, not assumed. **Met**
   — `REALITY-STRESS-TEST-REPORT.md`'s own verdict: `READY WITH MINOR
   CHANGES`, with the "minor changes" already applied prior to this
   freeze being requested.

## Freeze date

**2026-07-24.**

## Repository commit references

- `01656e5` — AG-002 Discovery Archaeologist v0.1 created (with
  `PILOT-RUN-0001`).
- `a8031c6` — `PILOT-RUN-0002` first attempted, correctly `BLOCKED` at
  Stage 1 (Google Drive access).
- `0e12c85` — AG-002 memory access blocker resolved (`memory/`
  established).
- `44def99` — `PILOT-RUN-0002` processed the real diary (partial, by
  design — paused on a genuine human-decision point).
- `8240cf4` — `PILOT-RUN-0002` completed: all 77 real diary entries
  read.
- `e0bd346` — AG-003 Knowledge Curator v0.1 architecture designed
  (DRAFT, no implementation), including the first adversarial review and
  worked-example walkthrough.
- `652db3d` — AG-003 Reality Stress Test: four real datasets, three
  architecture corrections applied, freeze recommendation issued.
- The commit introducing this file (`RELEASE-1.0.md`,
  `VALIDATION-HISTORY.md`, `GOVERNANCE.md`, `ARCHITECTURE-MAP.md`,
  `LESSONS-FROM-V1.md`, and the `FROZEN`/`1.0` header updates across
  both Roles' document sets) is the freeze commit itself — see this
  repository's own `git log` on branch
  `claude/prop-0002-discovery-intake` for its exact SHA, immediately
  following `652db3d`.
