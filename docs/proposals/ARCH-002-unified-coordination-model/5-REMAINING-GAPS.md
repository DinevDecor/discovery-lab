# Deliverable 5 — Remaining Gaps

Per `ARCH-002` Phase 6: what is actually necessary for
`4-UNIFIED-COORDINATION-MODEL.md` to become executable — not what
would be a nice addition. Each gap below is justified by a specific
document already cited in this review, not by preference.

## G1 — No mechanism anywhere carries out an approved action

Every ratified component in the Unified Model (Formal Gate, Human
Final Authority) ends at "a human approves." Nothing after that point
is architecture — it is a person manually doing the work. This is not
inferred; it is stated by the ecosystem's own documents: `kod`'s
`PROJECT_STATE.md` lists an `Execution Layer` separately from Control/
Knowledge layers and marks its own `Kernel Status: DESIGN` (not
built); `project-memory`'s Dispatcher contract states outright that it
"does not perform the specialized work itself"; `trust-engine`'s gate
architecture states "even `CRITICAL` does not mean automatic trust
mutation." **Necessary because**: without this, "canonical
architecture" and "who does the actual work" remain two unconnected
facts — the model can be as correct as it likes and nothing downstream
of an approval will happen without a human doing it by hand, forever.

## G2 — The ratified Control Plane concept has no enactment mechanism

`project-memory/ADR-0001` and `kod/ADR-0009` each independently and
formally ratify the same three mechanisms (Contract-Defined Roles,
Formal Gate, Human Final Authority) — but neither references the
other, and nothing in either repository checks that its own instance
still matches the other's. The Unified Model in this review is itself
now a fourth artifact making the same claim, with the same
enforcement problem: nothing requires `kod`, `discovery-lab`, or
`trust-engine` to notice if this document changes. **Necessary
because**: a "canonical architecture" that no repository is mechanically
required to consult is canonical only by this review's assertion, not
by any property of the ecosystem — exactly the failure mode `ARCH-001`
found (three independent, unreconciled coordination designs) would
simply recur a fourth time around this document unless something
changes.

## G3 — `trust-engine` has no ratification vocabulary at all

Confirmed directly in `1-ARCHITECTURE-INVENTORY.md`: every other
repository has an explicit status vocabulary
(`ACCEPTED`/`DRAFT`/`PILOT`/`FROZEN` in `kod` and `project-memory`;
`ACCEPTED`/`DRAFT` in `discovery-lab`). `trust-engine` has none — not
one architecture document carries a document-level status field. Its
Formal Gate and Human Final Authority instances entered this review's
canonical model only through the "independently repeated concept"
path, never through ratification, because there is currently no
ratification path available in that repository to use. **Necessary
because**: as long as this gap exists, nothing in `trust-engine` can
ever become a first-class (ratified) source for future architecture
work — every future review of this kind will have to keep re-deriving
`trust-engine`'s standing from repetition alone, which is a weaker and
slower form of evidence than a status field would provide.

## G4 — No mechanism checks the three ratified instances for drift

`project-memory`'s own Stable Core already names the concept this gap
needs — "Architecture–Implementation Drift," a named state that blocks
and requires a human decision when normative authority and operational
reality diverge. That concept has never been applied across
repository boundaries. Nothing currently checks whether `kod`'s Kernel
Review, `discovery-lab`'s Adversarial Review, and `project-memory`'s
Kernel-as-gate-concept remain the same mechanism over time as each
repository evolves independently. **Necessary because**: three
already-ratified, currently-aligned instances of the same concept is
exactly the situation that silently becomes three diverged instances
if nothing watches for it — and the ecosystem already has a name and a
precedent for the watching mechanism, it has just never been pointed
across repositories.

## G5 — Named, not re-litigated: `PROP-0001` still `DRAFT`

`ARCH-001` already found and ranked this as the ecosystem's top risk
(discovery-lab's Roles `FROZEN v1.0` on an unratified mandate). It
resurfaces here only because `discovery-lab`'s Formal Gate and Human
Final Authority instances — both cited as canonical in
`4-UNIFIED-COORDINATION-MODEL.md` — are ratified *via `GOVERNANCE.md`*,
which itself operates under that same unratified mandate. This review
does not re-run that analysis; it notes that G1–G4 do not make it less
urgent, and one of the four canonical instances this document just
certified is downstream of it.

## What is explicitly not a gap

Scheduler, Event, and Planning components (`2-COMPONENT-MATRIX.md`)
are absent everywhere, but their absence is not listed as a gap here —
nothing in the ecosystem's own roadmaps or state files claims a
present need for them, and inventing a need for a component the
evidence does not call for would violate this task's own "do not be
creative" rule. If G1 (execution) is closed first, whether a
Scheduler/Event/Planning layer is then actually necessary becomes an
empirical question the execution layer's own operation would answer —
not one this archaeological review can answer today.
