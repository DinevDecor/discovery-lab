# Deliverable — Comparison Matrix

Current hypothesis (as stated in the request) vs. the alternative in
`1-ALTERNATIVE-ARCHITECTURE.md`.

| Dimension | Current hypothesis (build `DLOS`) | Alternative (reconcile + gate + one execution path) |
|---|---|---|
| Coordination layer | Treated as missing; proposes designing a fifth system | Treated as already built three times, unreconciled; proposes adopting one, informed by the other two |
| Relationship to `project-memory`'s Control Plane design | Not referenced; `DLOS` would be built independently of it, risking a fourth reinvention | Used as the base document — the only one already explicitly scoped for this purpose and already "Candidate for Adoption" |
| Freeze sequencing (`PROP-0001` vs. `AG-002`/`AG-003`) | Not addressed — inversion persists silently | Directly fixed via a named precondition rule on the `Freeze Recommendation` step |
| Execution/runtime gap | Not addressed by the hypothesis at all — `DLOS` is framed as a coordinator of roles, not an executor of actions | Directly targeted, narrowly, via one real approved-action path |
| Autonomy | Implied next step once `DLOS` "coordinates work" | Explicitly held constant; sequenced after foundation + execution evidence exist |
| Effort shape | New design + new build (a fifth system, from partial requirements) | Reconciliation + one governance rule + one narrow build (reuses ~80% already-designed content across three real documents) |
| Risk of repeating the ecosystem's own demonstrated failure mode | High — same failure mode that produced three independent coordination layers (build without cross-checking existing work) | Low by construction — the alternative's first step is explicitly a cross-check |
| Evidence backing | None cited in the hypothesis itself | `META-001` `P1` (Strong, 4/4), `P3` (Cross-domain Stable, 4/4); direct grep confirming `DLOS` has no existing design anywhere |
| Consistent with Discovery Lab's own Principle 0 ("never decide unilaterally; propose, don't impose") | Ambiguous — a `DLOS` build would itself need a human ratification step not currently specified | Consistent — item 2's ratification gate and item 1's "adopted by a real human decision" are load-bearing, not decorative |
| What it would require of Discovery Lab specifically | Presumably a new proposal (`PROP-000x`) authorizing `DLOS` design work | No new proposal type required; `PROP-0001` ratification (already pending) plus a `GOVERNANCE.md` amendment covers it |

## Where the two agree

Both keep the four-domain split. Both keep human final authority as
non-negotiable. Neither argues for merging `project-memory`, `kod`,
`discovery-lab`, or a confirmed operational-intelligence system into a
single codebase — the domains are genuinely different (commercial
field-service dispatch has nothing to do with knowledge curation).

## Where they cannot both be right

The hypothesis's claim that "DLOS coordinates work" describes a
missing system. The evidence (three independently built coordination
designs, one of them explicitly diagramming the others as inheritors)
shows this is false as stated — coordination is not missing, it is
unreconciled. This is not a matter of preference between two designs;
it is a factual disagreement about the current state of the
repositories, resolved by direct inspection in
`0-ARCHITECTURE-ASSESSMENT.md`'s Q1.
