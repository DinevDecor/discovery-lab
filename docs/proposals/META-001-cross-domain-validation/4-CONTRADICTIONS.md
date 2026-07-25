# Deliverable 4 — Contradictions

Per `META-001`. Checked directly for two kinds of contradiction: (a)
between two of the cross-domain source documents themselves, and (b)
between the cross-domain evidence and `RI-0002`'s candidate meta-theory.
**None confirmed of either kind.** Every candidate below was actively
checked against the source text, not assumed absent.

## Candidate 1 — checked and declined: human-in-the-loop as permanent vs. temporary

`kod`'s `ADR-0009` states: *"Human-mediated message passing is the
current implementation and is explicitly recognized as part of the
architecture... Future automation may replace the human message bus
without changing the collaboration model."* This frames human mediation
as a *removable implementation detail*.

`project-memory`'s AI Collaboration Architecture states `INV-4` ("only
the human...") as part of its **Stable Core** — explicitly listed among
"what does not change" even after years of evolution (`§22`).

**Resolved as not a contradiction**: `kod`'s statement is scoped to
*message passing between agents* (a mechanical relay function);
`project-memory`'s `INV-4` is scoped to *final decision authority*
(accepting an ADR, authorizing merge). Automating the relay mechanism
does not touch who holds final authority — the two claims are about
different things wearing similar words. A careless read could have
flagged this as a contradiction; checked against the actual text, it is
not one.

## Candidate 2 — checked and declined: automatic scoring vs. "never automatic"

`trust-engine`'s `Experience Quality Score` and `project-memory`'s
`confidence` threshold are both computed **automatically** (by formula),
which could look like it contradicts the broader cross-domain pattern
`P1`/`P2` (nothing changes authoritative state automatically).

**Resolved as not a contradiction**: in both sources, what is automatic
is *classification/routing* (which tier, how much review friction);
what remains gated is the actual state mutation (`trust_scores` update,
a confirmed `Snapshot`). The sources themselves are explicit about this
distinction — `proposal_quality_gate_architecture.md`: "Even `CRITICAL`
does not mean automatic trust mutation." No contradiction survives
contact with the actual text.

## Candidate 3 — checked and declined: `RI-0002`'s generative abstraction vs. the cross-domain sample's silence on it

`RI-0002` proposes generative abstraction (strip domain-specific detail
to find an invariant process) as a real, well-evidenced method within
the diary. The cross-domain sample never mentions it. **This is an
absence, not a contradiction** — no cross-domain document states or
implies that generative abstraction is *wrong*, incompatible with, or
in tension with anything else found. It is simply not addressed. Recorded
under `2-PRINCIPLE-SURVIVAL-TABLE.md` as `Unsupported`, not here as a
contradiction — conflating "not found" with "found to be false" would
misrepresent what the search actually showed.

## What was not found

No genuine logical incompatibility — two claims that cannot both be
true — was found anywhere in this validation, either within the
cross-domain sample or between it and `RI-0002`. This mirrors the same
result the original `RI-0002` analysis and the Reality Stress Test both
reported: the DinevDecor ecosystem's governance material, across every
repository tested so far, has been unusually internally consistent. This
is reported as a real, checked result, not an assumption that
contradictions are unlikely to exist.
