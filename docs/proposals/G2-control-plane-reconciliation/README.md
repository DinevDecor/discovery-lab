# G2 — Control Plane Reconciliation

Status: **Reconciliation Draft — Candidate for Adoption.** Not
self-ratified. This task's own Mission asks for "one officially
accepted specification," but no document in this session ratifies
itself — every prior FROZEN/ACCEPTED artifact in this ecosystem
(`ADR-0001`, `ADR-0009`, `GOVERNANCE.md` themselves) required an
explicit human decision to reach that status. Producing that decision
is not this task's role, per Discovery Lab's own Principle 0 (propose,
don't impose) and per the Critical Rule against introducing a new
Governance mechanism — self-ratification would be exactly that. The
deliverable set below is the reconciliation; adoption remains a human
decision.

## Scope note — read before the deliverables

`G2`'s own "Sources" list names three items: `project-memory —
ADR-0001`, `KOD — ADR-0009`, `discovery-lab — GOVERNANCE.md`.
`project-memory/adr/ADR-0001-ai-collaboration-architecture.md` is
short — it is the ratifying instrument, not the substantive
architecture. Its own text states: *"The Stable Core of AI
Collaboration Architecture v1.1 is ACCEPTED"* and *"Project Memory is
established as the collaboration control plane."* This reconciliation
therefore treats "`project-memory — ADR-0001`" as the ADR **plus the
specific Stable-Core sections of `archive/AI-Collaboration-Architecture-v1_1.md`
it names as accepted** (§2 Fundamental Invariants, §3's tiering table,
§4 Control Plane, §6 Authority and Truth Model, §7's role-as-contract
principle, §8 Kernel Governance Layer) — not the Operational Defaults
or Experimental layers of the same document, which `ADR-0001` itself
marks `UNDER_TEST`, not accepted. This reading is stated explicitly, not
assumed silently, so it can be corrected if a stricter scope was
intended. No chat transcript, note, or investigation document was used
as a source anywhere in this task.

## Deliverables

1. `1-UNIFIED-CONTROL-PLANE-SPECIFICATION.md` — the reconciled
   specification itself, organized by shared concept, each with its
   canonical statement and source citations.
2. `2-CROSS-REFERENCE-MATRIX.md` — concept × source-document
   terminology table.
3. `3-DOCUMENT-MAPPING.md` — section-by-section correspondence between
   the three source documents.
4. `4-CONFLICT-RESOLUTION-LOG.md` — every real divergence found,
   resolved conservatively or left explicitly open — none invented,
   none silently smoothed over.
5. `5-FINAL-CANONICAL-VERSION.md` — the clean, adoptable text, without
   the reconciliation working-notes visible in Deliverable 1.
6. `6-VERDICT.md` — **PASS**.

## What this task did not do

No new Runtime, Governance model, Role, process, or principle was
introduced anywhere in this deliverable set. Every statement in
`1-UNIFIED-CONTROL-PLANE-SPECIFICATION.md` and
`5-FINAL-CANONICAL-VERSION.md` traces to specific text in one or more
of the three sources, cited inline. Where the sources genuinely
disagree or one is silent where another speaks, that gap is recorded
in `4-CONFLICT-RESOLUTION-LOG.md`, not resolved by invention.
