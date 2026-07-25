# Deliverable 4 — Conflict Resolution Log

Every real divergence found while reconciling the three sources. None
resolved by inventing a new rule — per this task's Constraints, only
reconciliation, normalization, cross-reference, and consolidation are
in scope. Where a genuine gap exists between the sources, it is
recorded as open, not closed.

## C1 — Kernel (PM/KOD) vs. Adversarial Review (DL): different formal strictness

**What differs**: PM's Kernel and KOD's Kernel Review are bound to a
specific, versioned **Review Contract** — a fixed external standard,
checked criterion by criterion, with an explicit prohibition on
inventing criteria. DL's Adversarial Review is a broader "active
attempt to find defects the Draft introduces on its own terms" —
bounded by the Draft's own internal consistency, not by a separate,
versioned contract document.

**Is this a contradiction?** No. Both are formal-gate-shaped checks
that feed a separate acceptance decision and never decide anything
themselves. The difference is scope and strictness, not opposed
claims.

**Resolution**: recorded as a real difference in
`1-UNIFIED-CONTROL-PLANE-SPECIFICATION.md` §3 and
`2-CROSS-REFERENCE-MATRIX.md`. Not resolved by forcing DL's
Adversarial Review into PM/KOD's contract-bound Kernel shape, or vice
versa — that would be introducing a new rule neither source states.
Left as: two real, different gate implementations, both consistent
with the same underlying "formal check before a separate acceptance
decision" shape.

## C2 — Generic role taxonomy (PM/KOD) vs. domain-specific Role lifecycle (DL): different layers

**What differs**: PM defines four generic, cross-project roles
(Architect/Researcher, Reviewer/Breaker, Implementer, Kernel). KOD
defines five (Headquarters, Research Lab, Software Lab, Kernel Review,
Applications). `GOVERNANCE.md` does not define any generic role
taxonomy at all — it governs the *lifecycle* that DL's own
domain-specific Roles (`AG-001`, `AG-002`, `AG-003`, each with a
distinct mission) pass through on their way to `FROZEN`.

**Is this a contradiction?** No. PM and KOD operate at the layer of
"what generic coordination roles exist"; DL's cited document operates
at the layer of "how does any Role's own governing documents mature
and stabilize" — a different question, answerable independently of
which specific roles exist.

**Resolution**: recorded as a layer distinction, not a naming
conflict. This reconciliation does not attempt to fit DL's `AG-00X`
Roles into PM's or KOD's generic taxonomy, or vice versa — doing so
would require inventing a mapping neither source states, which the
Constraints forbid.

## C3 — Human Final Authority: stated in PM and DL, silent in KOD

**What differs**: PM's `INV-4` and DL's stage-7 text both explicitly
restrict certain decisions (accept, merge, protocol-change / `FROZEN`)
to a human. KOD's `ADR-0009` states "Headquarters commits the status
change" and "The Git commit is the authoritative record of acceptance"
— without stating that Headquarters must be occupied by a human. Roles
in `ADR-0009` are described generically as executable "by different
chat sessions over time," which does not itself exclude an AI
executor occupying Headquarters.

**Is this a contradiction?** Not necessarily — KOD's silence is
consistent with either reading (Headquarters is implicitly human, or
KOD genuinely leaves this open). It cannot be resolved from `ADR-0009`'s
own text alone.

**Resolution**: **left explicitly open, not resolved by assumption.**
This is the single most significant gap this reconciliation found. It
is not closed here, because closing it either way (assuming KOD agrees
with PM/DL, or assuming KOD deliberately diverges) would require either
inventing a rule KOD's text does not state, or overriding what KOD's
text does state — both outside this task's scope. Flagged for a human
decision if the three governance instruments are ever formally merged;
not decided by this reconciliation.

## C4 — Drift: stated fully in PM, absent from KOD/DL

**What differs**: PM names "Architecture–Implementation Drift" as a
first-class state with its own detection→analysis→human-decision
procedure. Neither KOD's `ADR-0009` nor DL's `GOVERNANCE.md` names an
equivalent state. KOD's Authority Matrix precedence order (which
artifact wins when two disagree) addresses a related but narrower
question. DL's `NOT READY` verdict is a lifecycle-stage rollback for
one Role's own Freeze process, not a cross-layer state.

**Is this a contradiction?** No — silence, not disagreement. Nothing
in KOD or DL contradicts PM's Drift concept; it simply is not
independently stated in either of the other two cited documents.

**Resolution**: recorded as present in one source, absent in the other
two. Not imported into KOD or DL's own text by this reconciliation —
doing so would be introducing a new concept into documents that do not
state it, which the Constraints forbid, even though the concept itself
already exists (in PM) and is not "new" in the ecosystem sense the
Critical Rules are protecting against.

## C5 — Anti-theater clause: stated only in PM

**What differs**: PM's §8 explicitly names an anti-complacency check
("20 consecutive Kernel `PASS` results is a red flag, not success").
No equivalent named clause appears in KOD's `ADR-0009` or DL's
`GOVERNANCE.md`, though `GOVERNANCE.md` has a structurally adjacent
rule ("no stage may be self-certified by the same act that produced
the artifact under review") addressing a related but distinct concern
(self-certification, not run-count complacency).

**Resolution**: recorded as PM-only within the three cited documents.
Not extended to KOD or DL here.

## Summary

Five items logged: two (`C1`, `C2`) are differences in scope/layer,
not contradictions, and are resolved by recording both as valid,
non-competing statements. Three (`C3`, `C4`, `C5`) are real
one-sided-or-partial gaps, left open rather than closed by invention.
Zero outright contradictions found — no two sources make mutually
exclusive claims about the same question.
