# Recovery Report — STRESS-RUN-0004

**STATUS: COMPLETE.** Real run, dataset 3 of the "AG-003 Reality Stress
Test" task: "Research notes / investigations (GRIF, Discovery
documents)." Source: `reality-inbox/` intake `RI-0004`
(`../../../../../reality-inbox/manifests/RI-0004.md`) — seven real files
from the `kod` repository, read as an external, observed source only
(`PROP-0001` Principle 0; nothing written back to `kod`).

## Run Metadata

- Run ID: `STRESS-RUN-0004`
- Timestamp: 2026-07-24
- Sources requested: `RI-0004` (7 files, all authorized)
- Sources scanned: 7 of 7 — `EX-0001_CASE.md`, `EX-0001_PROGRESS.md`,
  `ART-0001.md`, KOD's own `ADR-0001.md`/`ADR-0002.md`/`ADR-0003.md`,
  `KNOWLEDGE_OBJECT_TEMPLATE.md`
- Sources inaccessible: none
- Manifest check: `RI-0004` confirmed present with complete provenance
  before any file was read

## Executive Summary

Seven real KOD documents, two of them genuinely near-empty (an
excavation progress tracker at 0% and a blank Knowledge Object
template), five substantive. Recovered: an excavation charter defining
what "origin of KOD" research should preserve, four short axiomatic
claims from a Research Journal artifact, and three real Architecture
Decision Records forming a coherent, undated-but-ordered progression
(methodology-before-software → research-not-ideas → specification-
before-implementation). One strong repeated theme (research process
over conclusions, three independent statements) and one probable
near-duplicate (two separate "reality is the final arbiter" statements)
were found. **Two deliberate near-empty sources correctly yielded
almost no extractable knowledge** — recorded honestly as such, not
padded with inferred content. **KOD's own Knowledge Object template**
was recovered as a structural fact (its field list) only, not as
substantive knowledge, and not treated as this repository's own
Knowledge Object format.

## Recovered Ideas

### RI-1 — Excavation EX-0001: "Origins of KOD" charter

- `EX-0001_CASE.md`: Mission — reconstruct KOD's origin and early
  evolution; *"The objective is not to preserve conclusions. The
  objective is to preserve intellectual evolution."* Primary Question:
  *"When did KOD become a distinct research methodology rather than a
  collection of ideas?"* Status: `Active`. Success criteria list six
  categories to identify (first recurring questions, first core ideas,
  first hypotheses, first candidate principles, first architectural
  concepts, first methodological changes); deliverables list five items
  (Excavation Report, Timeline, Knowledge Objects, Research Sessions,
  Integration into Corpus).

### RI-2 — Excavation EX-0001's own progress: zero, as of an unknown date

- `EX-0001_PROGRESS.md`: Current Conversation: `None`. Conversations
  Processed: `0`. Knowledge Objects Extracted: `0`. Research Sessions
  Created: `0`. Candidate Principles: `0`. Accepted Principles: `0`.
  Architecture Decisions: `0`. Confidence: `0%`. **This file carries no
  date anywhere** — unlike every other source processed in this
  engagement to date, its currency cannot be established; recorded as
  `UNKNOWN` (`LIMITATIONS.md`), not assumed to be either stale or
  current.

### RI-3 — Four axiomatic claims (ART-0001)

- `ART-0001.md`, Source: "Research Journal," Status: `ACTIVE`: *"AI
  memory is insufficient."* *"Registry should become the Single Source
  of Truth."* *"The research process is more important than
  conclusions."* *"Reality is the final arbiter of trust."* Four short,
  separate declarative claims, no elaboration given in this artifact.

### RI-4 — KOD ADR-0001: methodology before software

- KOD's own `ADR-0001.md` (**note: this is a different document from
  this repository's `docs/adr/ADR-0001-human-authority-gates.md`,
  disambiguated by filename prefix in `RI-0004`'s manifest — see
  "Open Questions" below for the collision check**), Status `Accepted`:
  *"KOD is the methodology. Software systems are applications built on
  top of KOD. No product defines KOD. KOD defines the products."*
  Context names three concrete products: Trust Engine, Regime AI, Dinev
  Decor AI.

### RI-5 — KOD ADR-0002: protects research, not ideas

- KOD's own `ADR-0002.md`, Status `Accepted`: *"KOD does not protect
  ideas. KOD protects honest research... Reality remains the final
  arbiter."* Consequences name five required supporting mechanisms: an
  executable research constitution, a Research Guardian, a Research
  Journal, traceability from conclusion back to evidence, and
  preservation of rejected hypotheses.

### RI-6 — KOD ADR-0003: specification before implementation

- KOD's own `ADR-0003.md`, Status `Accepted`: every KOD component must
  exist as a Specification (`Foundations/`) before a Runtime
  (`Infrastructure/python/`); *"No runtime implementation may exist
  without an approved specification."* States a Development Lifecycle
  (`Idea → Research Session → Specification → Architecture Review →
  Implementation → Tests → Deployment`) and a nested Architectural
  Principle: *"Implementation follows architecture. Architecture follows
  methodology. Methodology follows the Constitution. The Constitution
  follows the Mission."*

### RI-7 — KOD's own Knowledge Object template (structural fact only)

- `KNOWLEDGE_OBJECT_TEMPLATE.md`: ten section headers, no content —
  `Title`, `Status`, `Purpose`, `Definition`, `Properties`,
  `Relationships`, `Examples`, `Counterexamples`, `Open Questions`,
  `Revision History`. **Recovered as a structural fact about KOD's own
  schema** (it exists, it has these ten fields), **not as substantive
  knowledge** — the template itself contains no filled-in claim to
  extract. This is deliberately not conflated with this repository's own
  `AG-003` Knowledge Object schema (`../../../AG-003-knowledge-curator/
  KNOWLEDGE-OBJECT-SPEC.md`) — the two share only the words "Title,"
  "Status," and "Relationships" in their field lists; the rest differ
  entirely, and AG-002 makes no claim about which is "better," only that
  they are different and both real.

## Repeated Themes

### RT-1 — "The research process matters more than its conclusions" (three independent statements)

- `EX-0001_CASE.md` (*"the objective is not to preserve conclusions...
  is to preserve intellectual evolution"*), `ART-0001.md` (*"the
  research process is more important than conclusions"*), and KOD's own
  `ADR-0002.md` (*"KOD does not protect ideas. KOD protects honest
  research"*) — three separately-authored documents (an excavation
  charter, a Research Journal artifact, and an accepted ADR) converging
  on the same underlying claim, in different words. Comparable in kind
  to `PILOT-RUN-0002`'s `RT-3` (five restatements of one idea within a
  single diary), but here the three restatements are **at least
  plausibly cross-document within KOD's own corpus**, not all three
  necessarily from the same author or session — this run cannot confirm
  authorship/session identity for any of the three, so this is recorded
  as a real repeated theme, not upgraded to a stronger "independent
  convergence" claim without that missing evidence.

### RT-2 — "Reality is the final arbiter" (probable near-duplicate, not a confirmed one)

- `ART-0001.md` (*"Reality is the final arbiter of trust"*) and KOD's
  `ADR-0002.md` (*"Reality remains the final arbiter"*) — near-identical
  wording, in two different documents. Recorded as a Repeated Theme
  here, **not silently merged** — whether these are the same claim
  (a general "reality is the final arbiter [of everything]" principle)
  or `ART-0001`'s version is narrower (specifically "of trust") is a
  real, undecided question this run does not resolve; see the Curation
  pass (`../../../../proposals/AG-003-reality-stress-test/
  CURATION-0004.md`) for how AG-003 handles this as a duplicate-detection
  case.

## Idea Evolution (Discovery Timeline)

**None of KOD's three ADRs in this dataset carry an explicit
`Depends on`/`Amends` header field**, unlike this run's sibling dataset
(`STRESS-RUN-0003`, this repository's own ADRs, which state their
dependencies directly). Any ordering among `RI-4`/`RI-5`/`RI-6` here is
**inferred from content only** — `ADR-0001`'s "methodology before
software" framing is presupposed by `ADR-0002`'s "protects research"
framing (which only makes sense if KOD is already established as more
than a product), which is in turn presupposed by `ADR-0003`'s
"specification before implementation" (which requires "methodology" and
"the Constitution" to already be meaningful terms, per its own closing
principle) — a plausible reading order (`ADR-0001 → ADR-0002 → ADR-0003`)
matching their numeric sequence, but **inferred, not source-declared**,
and explicitly flagged as such rather than reported with the same
confidence as `STRESS-RUN-0003`'s header-stated dependencies.

## Forgotten Ideas

**None confirmed.** `RI-2` (`EX-0001`'s 0% progress) could look like
abandonment, but `EX-0001_CASE.md`'s own `Status` field states `Active`,
not abandoned — this run does not override the source's own stated
status with an inference from a low progress number. Recorded as
`INSUFFICIENT EVIDENCE` for "forgotten," not as a confirmed forgotten
idea.

## Candidate Investigations

*(Continuing AG-002's global sequence; `STRESS-RUN-0003` used `CI-6`.)*

- **CI-7** — whether `EX-0001`'s excavation has progressed since
  `EX-0001_PROGRESS.md`'s undated 0%-complete snapshot. Cannot be
  resolved from this dataset (no date, no later file exists in the
  copied set).
- **CI-8** — whether `RT-2`'s two "reality is the final arbiter"
  statements are the same claim or two distinct, differently-scoped
  claims. Addressed as a duplicate-detection case in the Curation pass,
  not resolved here (Recovery is not Curation, per `RUN-PROTOCOL.md`).

## Contradictions

**None confirmed.** One candidate was checked and declined: `RI-2`'s
"0 Knowledge Objects Extracted" (specific to excavation `EX-0001`) does
**not** contradict `RI-3`'s existence (`ART-0001`, a Corpus Artifact) —
`EX-0001_PROGRESS.md`'s counters are scoped to that one excavation's own
output, not a system-wide count; `ART-0001` carries no reference tying it
to `EX-0001` at all. Treating these as contradictory would have been a
false-positive contradiction manufactured from an unstated scope
assumption, not from the text.

## Open Questions

- `CI-7`, `CI-8` above.
- **Naming-collision check, run deliberately**: does KOD's own
  `ADR-0001.md` (`RI-4`, "methodology before software") describe the
  same decision as this repository's `docs/adr/ADR-0001-human-authority-
  gates.md` (`STRESS-RUN-0003`'s `RI-1`, Human Authority Gates)? **No —
  confirmed distinct.** The two share only the bare numeric label
  "ADR-0001" and belong to different repositories with entirely
  unrelated subject matter (KOD's product-vs-methodology boundary versus
  this repository's human-authorization-gate concept). Checked directly
  against both texts, not assumed distinct from title alone.

## Recovery Queue

1. `CI-7`, `CI-8`.
2. Consider whether a future recovery run should read `kod/Foundations/`
   in full (this run read only `KNOWLEDGE_OBJECT_TEMPLATE.md` from that
   directory) — `RESEARCH_ENGINE.md`, `RESEARCH_GUARDIAN.md`, and others
   exist there and were not in `RI-0004`'s authorized scope.

## Evidence

All seven sources, in `reality-inbox/processed/stress-test-kod-research/`
(each prefixed `KOD-` to avoid filename collision with this repository's
own `docs/adr/`): `KOD-EX-0001_CASE.md`, `KOD-EX-0001_PROGRESS.md`,
`KOD-ART-0001.md`, `KOD-ADR-0001.md`, `KOD-ADR-0002.md`, `KOD-ADR-0003.md`,
`KOD-KNOWLEDGE_OBJECT_TEMPLATE.md` — quoted or cited above under the
matching Recovered Idea. `reality-inbox/manifests/RI-0004.md` — full
provenance and `sha256` hashes for all seven.

## Archaeologist Boundary Statement

No source document was modified — all seven files were read only, from
read-only copies hash-verified against the live `kod` repository at copy
time. No content was invented — `RI-2` and `RI-7` in particular are
reported as near-empty precisely because they *are* near-empty in the
source; no plausible-sounding content was supplied to fill the gap. No
duplicate was removed — `RT-2`'s two "final arbiter" statements are
preserved and cited together, flagged as a probable-not-confirmed
duplicate, left for Curation to formally propose or decline. No idea is
asserted as true, good, or worth pursuing — every finding is reported as
"KOD's own material states X," never independently endorsed.
`RI-0004.status` is `COMPLETED` — all 7 files read in full; two were
substantively empty by design of the source itself, not by an
incomplete read.
