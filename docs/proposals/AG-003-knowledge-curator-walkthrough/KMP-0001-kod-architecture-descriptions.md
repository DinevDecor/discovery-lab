# Knowledge Merge Proposal KMP-0001

Demonstration proposal — not filed to a real Knowledge Base (see
`README.md`). Format per `../../ai-organization/employees/
AG-003-knowledge-curator/OUTPUTS.md`.

## Candidate Knowledge Objects

Neither is filed as a real `KO-NNNN` in this walkthrough (only `KO-0001`
is, for focus) — described here as they would appear if curated:

- **Candidate A** — "KOD Architecture Baseline v1.0": four layers
  (Identity, Registry, Runtime, Kernel), Registry described as *"the
  official Single Source of Truth"* — `RI-8`, dated `2026-06-28`.
- **Candidate B** — "Three-layer knowledge architecture": Knowledge
  Layer (Obsidian), Control Layer (KOD Registry — *"Single Source of
  Truth... never all knowledge"*), Reasoning Layer (AI) — `RI-12`, dated
  `2026-07-03`–`2026-07-04`.

## Evidence of overlap

- Both name "Registry" as KOD's Single Source of Truth, in near-identical
  language, six days apart.
- Both are structural, layered descriptions of how KOD organizes itself.
- Both come from the same source (the diary) and the same AG-002 run.

## Evidence of distinction

- Candidate A describes a **four**-layer runtime/system architecture,
  with concrete Python classes (`Registry`, `KODKernel`, `ProjectState`,
  `MasterIndex`, `Investigation`, `Session`, `Paths`) — an
  implementation-level description.
- Candidate B describes a **three**-layer knowledge-storage/tooling
  architecture (Obsidian / Registry / AI), explicitly scoped to how
  external tools like Obsidian and Neo4j relate to the Registry — a
  different question (how humans and AI *interact with* stored
  knowledge) than Candidate A's (what the system's own runtime is made
  of).
- Candidate B's own text is consistent with, not contradicting, Candidate
  A: it states Obsidian/Neo4j are *"interfaces only, never the Source of
  Truth,"* which presupposes rather than replaces something like
  Candidate A's Registry layer.

## Proposed unified object (if accepted)

**Not proposed.** The evidence of distinction outweighs the evidence of
overlap: these describe two different architectural questions (internal
runtime structure vs. external knowledge-tooling interface), both
converging on the same Registry concept rather than being restatements
of the same claim. Merging them would lose the distinction between "what
KOD's runtime is built from" and "how external tools relate to it."

## Reversibility statement

N/A — no merge is recommended. Had one been accepted, both candidates'
`derived_from` and `provenance` would be preserved on the resulting
object, and either could be reconstructed as a standalone Knowledge
Object by a later human decision.

## Recommendation

**Do not merge.** This looks like a case for a Relationship Proposal
instead — Candidate B plausibly `derived_from` or `supports` Candidate A
(both readings are defensible; a full Relationship Proposal is not filed
in this walkthrough, to keep this demonstration focused on the
merge-vs-distinct judgment itself, per `../../ai-organization/employees/
AG-003-knowledge-curator/OUTPUTS.md`'s rule that a relationship must not
be used as a workaround for an unresolved merge question — here the
merge question *is* resolved, just resolved as "no").

## Provenance

`../../ai-organization/employees/AG-002-discovery-archaeologist/runs/
PILOT-RUN-0002-recovery-report.md`, `RI-8` and `RI-12`.
