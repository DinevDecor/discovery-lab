# Outputs — AG-003 Knowledge Curator

Employee ID: **AG-003** · Role Name: **Knowledge Curator** ·
Status: **FROZEN** · Version:
**1.0**
Core Principle: **Curate what was recovered. Propose, never impose.
Every claim traces back to a Recovery Report.**

AG-003 produces exactly six kinds of artifact, and nothing else. Every
one is a proposal or a report — none is an automatic action, and none
modifies a Recovery Report or any other Role's files.

## 1. Knowledge Objects (`KO-NNNN`)

Not a proposal by itself — the curated unit AG-003 maintains. Full field
spec and lifecycle rules: `KNOWLEDGE-OBJECT-SPEC.md`, `LIFECYCLE.md`.
Stored under `../../../../memory/knowledge-objects/KO-NNNN.md` once a real
Knowledge Base exists (not created by this design task — see
`STATUS.yaml`). A Knowledge Object's `status` field only ever advances
via an accepted Core Principle Proposal (below), never directly.

## 2. Knowledge Merge Proposals (`KMP-NNNN`)

```
# Knowledge Merge Proposal KMP-NNNN

## Candidate Knowledge Objects
## Evidence of overlap
## Evidence of distinction (if any)
## Proposed unified object (if accepted)
## Reversibility statement
## Recommendation
## Provenance
```

Produced by duplicate detection (`ROLE.md` responsibility 1). **Never
executes a merge.** `Reversibility statement` is mandatory, and reversal
depends on a concrete bookkeeping rule, not just a promise: **every
`provenance` entry carried into the unified object is tagged with the
`KO-NNNN` it originally belonged to** (a `merged_from_ko` field on that
entry). Without this tag, a later split could not tell which citations
came from which original object once they are pooled together in one
list — the tag is what actually makes "reversible by construction" true,
for a two-way merge or an N-way one. See `LIFECYCLE.md`, "What a merge
does to IDs."

## 3. Relationship Proposals (`REL-NNNN`)

```
# Relationship Proposal REL-NNNN

## Source Knowledge Object
## Target Knowledge Object
## Proposed relationship type(s)
## Evidence
## Why this type, and not a confusable alternative
## Recommendation
## Provenance
```

Produced by relationship-graph construction (`ROLE.md` responsibility
3). Must select from the fixed ontology in `RELATIONSHIP-ONTOLOGY.md`
and must explicitly address why a confusable alternative type was not
chosen — an unexplained relationship is not a valid proposal.

## 4. Core Principle Proposals (`CPP-NNNN`)

```
# Core Principle Proposal CPP-NNNN

## Subject Knowledge Object
## Current status
## Proposed status
## Evidence against PROMOTION-RULES.md's threshold for this step
## What this proposal does NOT claim
## Recommendation
## Provenance
```

Produced by Core Principle detection (`ROLE.md` responsibility 4).
Proposes exactly **one** step of `Draft → Candidate Principle →
Validated Principle → Core Principle` at a time — never a skip. See
`PROMOTION-RULES.md`.

## 5. Contradiction Reports (`KCR-NNNN`)

```
# Contradiction Report KCR-NNNN

## Knowledge Objects in tension
## What cannot both be true
## Evidence (cited from both objects' provenance)
## Prior AG-002 markings on this tension, if any
## What this report does NOT do
## Provenance
```

Produced by contradiction detection (`ROLE.md` responsibility 5).
**Never proposes a resolution.** If AG-002 already marked the underlying
tension `INSUFFICIENT EVIDENCE`, this report says so explicitly under
"Prior AG-002 markings" and does not escalate past that marking on its
own authority.

## 6. Knowledge Evolution Reports (`KEV-NNNN`)

```
# Knowledge Evolution Report KEV-NNNN

## Subject Knowledge Object(s)
## Lifecycle timeline (first_seen -> last_seen, each occurrence cited)
## Confidence evolution
## Maturity trajectory
## Provenance
```

Produced by knowledge-evolution tracking (`ROLE.md` responsibility 2).
Descriptive only — states what the lifecycle record shows, proposes
nothing by itself (a Core Principle Proposal may cite one as evidence).

## 7. Gap Reports (`GAP-NNNN`)

```
# Gap Report GAP-NNNN

## Missing evidence / isolated objects / weak connections observed
## Candidate Investigations generated (CI-NNNN, continuing AG-002's sequence)
## Relationship to any existing Candidate Investigation
## Provenance
```

Produced by gap discovery (`ROLE.md` responsibility 6). **Candidate
Investigations continue AG-002's existing `CI-NNNN` sequence** — AG-003
never starts a second, competing numbering scheme for the same concept.
A Gap Report that only restates an existing `CI-NNNN` does not mint a
new one; it cites the existing one.

## Hard rules about every output above

- **Every artifact carries a `Provenance` section** citing the exact
  Recovery Report(s) and Recovered Idea / Repeated Theme identifiers it
  derives from — an artifact without one is not valid under this format.
- **Nothing here is an accepted fact until a human (or the Knowledge
  Review process, `REVIEW-PROTOCOL.md`) acts on it.** A proposal or
  report is a recommendation, exactly as AG-002's Recovery Queue and
  ORB's own reviews are.
- **No artifact merges, promotes, resolves, or invents.** Six output
  kinds exist because six actions are permitted; nothing else is
  produced under any other name.
- **A Knowledge Merge Proposal and a Relationship Proposal are not
  interchangeable.** If two Knowledge Objects are genuinely the same
  concept, propose a merge. If they are related but distinct, propose a
  relationship. Proposing a relationship as a workaround for an
  unresolved merge question is not valid — use `INSUFFICIENT EVIDENCE`
  instead and leave both open.

## Relationship to other documents

The procedure that produces these outputs is the Curation Protocol
(`CURATION-PROTOCOL.md`). What AG-003 may curate is in `ROLE.md`'s
Responsibilities. A practical pre/during/post-pass checklist is in
`CHECKLIST.md`.
