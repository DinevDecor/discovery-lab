# Discovery Lab — Architecture Map

**Status: current as of Release 1.0** (`../releases/1.0/RELEASE-1.0.md`,
2026-07-24). Updated whenever a Role's frozen/adopted status changes;
not itself a governance document — see `GOVERNANCE.md` and
`HIRING-LIFECYCLE-DRAFT.md` for the processes that change what this map
records.

## The knowledge pipeline

```
Reality
   │
   ▼
AG-002 Discovery Archaeologist   ◄── FROZEN 1.0, validated production component
   │
   ▼
Recovered Knowledge
   │
   ▼
AG-003 Knowledge Curator          ◄── FROZEN 1.0, validated production component
   │
   ▼
Knowledge Base
```

### `Reality`

Historical source material, of any kind — the pipeline's only real
input. Reached exclusively through **manifested, provenance-complete
intake**, never read directly by either Role:

- `reality-inbox/` (`📥 DROP HERE/` for remote sessions, a local
  Drive-synced folder for local sessions per `ADR-0004`) — the
  organization-wide, human-facing intake layer, frozen architecture per
  `ADR-0003`.
- `memory/` — the downstream, human-curated operational mirror
  (`ADR-0002`).
- **External ecosystem repositories** (`kod`, `generative-discovery-
  engine`, `trust-engine`) — read as observed sources only, per
  `../proposals/PROP-0001-discovery-lab-boundaries.md` Principle 0;
  discovery-lab writes nothing back to any of them, ever. First
  exercised for real in the Reality Stress Test
  (`../proposals/AG-003-reality-stress-test/`).
- **This repository's own governance documents** (ADRs, proposals) —
  also valid `Reality` input, exercised in the same stress test.

### `AG-002 Discovery Archaeologist` — **FROZEN 1.0**

Reads exactly one manifested source at a time; recovers ideas, repeated
themes, idea evolution, forgotten ideas, candidate investigations,
contradictions, and open questions; cites everything; never edits a
source; never invents; never removes a duplicate. Full spec:
`employees/AG-002-discovery-archaeologist/`. Real runs to date: 7
(`PILOT-RUN-0001`, `PILOT-RUN-0002`, `MIRROR-VERIFY-0001`,
`REALITY-VERIFY-0001`, `STRESS-RUN-0003`, `-0004`, `-0005`).

### `Recovered Knowledge`

Not a stored artifact of its own — the name for what a Recovery Report
contains: Recovered Ideas, Repeated Themes, Idea Evolution, Forgotten
Ideas, Candidate Investigations, Contradictions, Open Questions, each
citation-backed. Currently exists only inside AG-002's own Recovery
Reports (`employees/AG-002-discovery-archaeologist/runs/`) — there is no
separate "Recovered Knowledge" store distinct from those report files.

### `AG-003 Knowledge Curator` — **FROZEN 1.0**

Reads only Recovery Reports, existing Knowledge Objects, and Registries
— never a raw source. Detects duplicates (Knowledge Merge Proposals),
tracks lifecycle (`status` formal/human-gated, `maturity` informal/
automatic), proposes typed relationships (seven-type ontology), proposes
Core Principle promotions (one step at a time), reports contradictions
(never resolves them), and surfaces gaps. Never merges, promotes, or
resolves anything automatically — every output is a proposal. Full
spec: `employees/AG-003-knowledge-curator/`. Real curation passes to
date: 3 (the Reality Stress Test's three new datasets;
the first walkthrough against `PILOT-RUN-0002` was an architecture
demonstration, not counted as a run — see `STATUS.yaml`).

### `Knowledge Base`

**The target end-state, not yet a populated store.** `memory/
knowledge-objects/` does not exist yet — every Knowledge Object produced
so far (the first walkthrough, the Reality Stress Test) is written
inline under `docs/proposals/`, deliberately so it cannot be mistaken
for a filed, accepted Knowledge Base entry. This is stated explicitly,
not smoothed over: the pipeline's first two stages (`AG-002`, `AG-003`)
are frozen and validated; the destination they feed is architecturally
specified (`KNOWLEDGE-OBJECT-SPEC.md`, `LIFECYCLE.md`,
`RELATIONSHIP-ONTOLOGY.md`) but not yet built as a real, running store.
Building it is future work — `RELEASE-1.0.md`'s "What remains
intentionally out of scope."

## What "validated production component" means here, precisely

Both `AG-002` and `AG-003` have: a complete, internally consistent
document set; a passed internal review; a passed adversarial review
(with real defects found and fixed); and a passed Reality Stress Test
against real, structurally diverse data (with further real defects found
and fixed). This is what "validated" and "production component" mean on
this map. It does **not** mean: independently reviewed (no reviewer
other than the design session has examined either Role yet — see
`RELEASE-1.0.md`'s "Known limitations"), organizationally adopted
(`adoption_status: not_adopted` on both, unchanged by this freeze — see
`EMPLOYEE-REGISTRY.md`), or exercised at production scale (a handful of
real sources each, not a large corpus). "Production component" describes
where each Role sits in this pipeline and how thoroughly its own
architecture has been tested — not a claim about deployment scale or
organizational trust, which remain separate, unresolved axes.

## Where AG-001 sits

`AG-001 Repository Observer` is **not part of this pipeline** — it
observes `discovery-lab`'s own repository structure (commits, file
layout, documentation drift), not external `Reality` sources, and
produces observations for ORB review, not Recovered Knowledge or
Knowledge Objects. It remains `Prototype`, unfrozen, un-stress-tested —
this map does not claim otherwise, and this release does not change its
status.

## Relationship to other maps and processes

`GOVERNANCE.md` defines how a Role reaches the `FROZEN` state shown
here. `HIRING-LIFECYCLE-DRAFT.md` defines the separate adoption axis,
unaffected by this map. `ORB/ORB-PROTOCOL.md` reviews conduct on a
specific run; AG-003's own `REVIEW-PROTOCOL.md` reviews a specific
proposal's content — neither is a review of this map itself, which has
had none.
