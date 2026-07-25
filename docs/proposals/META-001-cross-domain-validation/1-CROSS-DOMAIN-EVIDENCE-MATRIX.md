# Deliverable 1 — Cross-Domain Evidence Matrix

Per `META-001`. Six source groups (`PHASE1-BLIND-CLASSIFICATION.md`)
across four independent repositories, tested against `RI-0002`'s
candidate meta-theory (`../AG-003-meta-theory-RI-0002/
META-THEORY-REPORT.md` Q2). **Architectural similarity is evidence;
shared vocabulary is not** — every row below cites the specific
mechanism, not a matching word.

## Independence disclosure (read before the matrix)

- Groups A and B share one repository (`kod`) and one presumed author —
  counted as **one independent domain**, not two, in all aggregate
  counts below.
- Groups D and E share one repository (`project-memory`) and one
  presumed author — counted as **one independent domain**, not two.
- Group F (`discovery-lab`) includes one reused document (`ADR-0001`,
  already analyzed in the Reality Stress Test for a different question)
  — flagged, not hidden.
- **Effective independent domain count: four** (`kod`, `trust-engine`,
  `project-memory`, `discovery-lab`), not six groups. All ratios below
  are stated against this real count.

## Matrix: candidate principle × domain

| Candidate principle | `kod` (A+B) | `trust-engine` (C) | `project-memory` (D+E) | `discovery-lab` (F) | Domains showing it |
|---|---|---|---|---|---|
| **P1** — AI proposes, human commits | Yes (`ADR-0009` Kernel Review + Headquarters commit) | Yes (Proposal → Approval → Applied Update) | Yes (explicit principle 1 + `INV-4`) | Yes (`ADR-0001` HAG, `GOVERNANCE.md`) | 4 / 4 |
| **P2** — one authoritative representation, no auto-resolution | Yes (`ADR-0009` Authority Matrix) | Yes (Trust Memory vs. raw evidence) | Yes (two-plane split + Drift) | Yes (`ARCHITECTURE-MAP.md` Knowledge Base) | 4 / 4 |
| **P3** — named uncertainty states, never silent | Yes (`BLOCKED` + criterion; Guardian's 6 outputs) | Yes (`UNKNOWN`, `INSUFFICIENT_EVIDENCE`) | Yes (`unresolved` list; `Drift`) | Yes (4-category Organizational Principle) | **4 / 4** |
| **P4** — role separation (validator ≠ generator) | Yes (Writer Matrix; 3-engine split) | Yes (5-step review, each own responsibility) | Weaker in D; strong in E (`INV-5`) | Yes (4 senses of "review" kept distinct) | 4 / 4 |
| **P7** — process over conclusion, named | Strong in B; weaker in A | Strong (verbatim "reality is final arbiter") | Strong in E; evidentiary-not-epistemic framing in D | Implicit in lifecycle stages, not named | 3 strong / 4 |
| **Generative abstraction** (`RI-0002` Principle 2) | **No** | **No** | **No** | **No** | **0 / 4** |

## Reading the matrix

- **`P3` is the single strongest cross-domain finding in this entire
  validation**: present in all four independent domains, in four
  structurally different vocabularies (`BLOCKED`/Guardian states,
  `UNKNOWN`/`INSUFFICIENT_EVIDENCE`, `unresolved`/`Drift`, the
  4-category principle), none of which is a shared template — see
  `5-COUNTER-THEORY.md` for why templating was checked and ruled out
  as the explanation.
- **`P1`, `P2`, `P4` are close behind**, each present in all four
  domains with domain-specific mechanisms, not shared wording.
- **`P7` is real but not universal** — strongly named in `kod`'s
  Research Kernel documents and `trust-engine`, present but reframed as
  an evidentiary rule (not an epistemic one) in `project-memory`'s
  Handover system, and structurally enacted but not explicitly named in
  `discovery-lab`'s own governance documents.
- **`RI-0002`'s second principle, generative abstraction, has zero
  independent support in this sample.** No hedging: this is a clean,
  confirmed absence, not a weak or ambiguous showing. See
  `2-PRINCIPLE-SURVIVAL-TABLE.md`.

## Provenance

`PHASE1-BLIND-CLASSIFICATION.md`, `PHASE2-PATTERN-EXTRACTION.md`,
`PHASE3-5-WORKING-NOTES.md`. Candidate meta-theory:
`../AG-003-meta-theory-RI-0002/META-THEORY-REPORT.md`,
`FINAL-VERDICT.md`.
