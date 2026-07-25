# Deliverable — Alternative Architecture

Not a rewrite of the domain boundaries — Q1 found those defensible.
This replaces the fifth line of the hypothesis ("DLOS coordinates
work") and fixes the freeze-sequencing defect found in Q4.

## What stays

- Four domain systems, unchanged in boundary: `project-memory`
  (organizational memory + the unrelated "Handover" commercial
  system), `kod` (trust/evidence/validation methodology and its
  generated products), `discovery-lab` (knowledge production from
  historical/operational sources), and whatever "operational
  intelligence" system eventually gets built and confirmed to exist
  (currently unconfirmed — see `DLOS`/`Dinev Assistant` finding in
  `0-ARCHITECTURE-ASSESSMENT.md`).
- Human final authority over commits, freezes, and trust mutations —
  every domain's own real mechanism already enforces this
  independently (`META-001` `P1`, `P3`); no redesign needed here, only
  explicit cross-domain adoption of the same rule instead of three
  separate re-derivations of it.

## What changes

### 1. One Control Plane specification, not three

Retire the premise that a `DLOS` needs to be designed. Instead:

- Take `project-memory/archive/AI-Collaboration-Architecture-v1_1.md`
  as the base document — it is the most complete of the three existing
  designs, already explicitly scoped as a cross-project Control Plane,
  and already names the other systems as intended inheritors.
- Reconcile `kod/Core/ADR/ADR-0009.md`'s Authority Matrix, Writer
  Matrix, and Kernel Review gate, and `discovery-lab`'s `GOVERNANCE.md`
  lifecycle and ORB, into that base document as domain-specific
  instantiations of the same invariants (`INV-1`–`INV-7`), not as
  competing designs. Where a domain's mechanism is stronger or more
  specific (e.g. `kod`'s Writer Matrix, `discovery-lab`'s explicit
  Recommendation Ledger / Evidence Coverage interfaces), fold it
  upward into the shared spec rather than discarding it.
- The output is one document, one owner, adopted (not just
  "Candidate") by a real human decision, that every domain repository
  references instead of redefining.

This is reconciliation of what already exists, not invention of a
fifth system — closer to a merge than a build.

### 2. A named "Foundation Ledger" gate before any Role/Component freeze

Directly fixes Q4's top weakness. Add one governance rule to whichever
document becomes the adopted Control Plane spec: **no Role, component,
or subsystem may reach `FROZEN` status while the mandate that
authorizes it is still `DRAFT`.** Concretely for `discovery-lab`: either
`PROP-0001` gets ratified (making `AG-002`/`AG-003`'s existing freezes
retroactively valid) or it gets rejected/revised (making the freezes
provisional and clearly labeled as such until re-validated). This is a
governance-rule addition, not a new system — it slots directly into
`GOVERNANCE.md`'s existing lifecycle as a precondition on the
`Freeze Recommendation` step.

### 3. One narrow, real execution path — not a general execution engine

Do not design a general-purpose runtime. Pick exactly one already-human-approved
action category (e.g., an `AG-003` Knowledge Merge Proposal that a
human has approved) and build the smallest possible mechanism that
carries out that specific approved action without a human manually
performing the file edit. This is deliberately narrow: it exists to
generate real evidence about what execution actually requires before
any broader "runtime" or "event architecture" gets designed — matching
this ecosystem's own repeated, evidence-first pattern (`ADR-0002`
"KOD protects honest research, not ideas"; the Reality Stress Test's
explicit rule to only change architecture on demonstrated, reproducible
weakness).

### 4. Autonomy stays exactly where it is until (1)–(3) exist

No component of this alternative architecture increases any Role's
current autonomy. This is a deliberate omission, not an oversight —
seeQ3.

## What this alternative does not include, and why

- **No `DLOS`.** Its function (coordination) is already covered three
  times over; what's missing is reconciliation, covered by item 1.
- **No knowledge graph, distributed cognition, or planning layer.**
  These presuppose a working execution substrate (item 3) that does
  not exist yet; designing them now would repeat the exact mistake
  this review is correcting — building ahead of ratification and
  ahead of evidence.
- **No new "operational intelligence" system design.** `Dinev
  Assistant` remains `INSUFFICIENT ACCESS`/unconfirmed; this review
  does not invent an architecture for a system whose existence cannot
  be verified. If it is real, it should inherit from item 1's Control
  Plane like every other domain project — that is the entire
  architectural statement needed about it until it is confirmed to
  exist.
