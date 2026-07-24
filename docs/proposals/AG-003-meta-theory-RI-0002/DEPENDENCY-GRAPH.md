# Dependency Graph — RI-0002

Per `META-THEORY-REPORT.md` Q5. **Dependency, not chronology, not
similarity.** An edge `A → B` means A generates, explains, or is a
precondition for B being intelligible — not merely that A came first or
resembles B. Where the honest relationship is thematic resonance without
a real dependency, it is marked as such and drawn separately, not folded
into the graph as if it were the same kind of connection.

## Edge types used

- **generates** — B is a direct application, revision, or output of A;
  removing A would make B's specific content unmotivated.
- **names / generalizes** — A is a later, explicit statement of the
  abstract pattern B (and others) already instantiate without naming it.
  Not chronological cause — A is usually dated *after* B.
- **justifies** — A supplies the reason B's mechanism is necessary, not
  B's content.
- **instantiates** — B is a concrete architectural application of A's
  general rule to one specific system.
- **weak echo** *(dashed, not a full edge)* — real thematic resonance,
  insufficient to claim dependency.
- **resonance only** *(dotted, not a graph edge at all)* — a structural
  parallel across a project boundary, deliberately not drawn as a
  dependency, per `COUNTER-THEORY.md`.

## The graph

```
RI-16 (second-order sensor) ───justifies──┬─→ RI-1/RI-2 (Kernel)
                                           ├─→ RI-9 (Investigation gate)
                                           ├─→ RI-10 (Research Protocol)
                                           └─→ RI-15 (Gen-Val Separation)

RI-3 (reality is final arbiter) ──justifies──┬─→ RI-1/RI-2
                                              └─→ RI-9
                        ╲
                         ╲weak echo
                          ╲
                          RT-1 (defend the method)

RI-15 (Gen-Val Separation) ──names/generalizes──┬─→ RI-1/RI-2
      [dated 20260715, AFTER the nodes it names]  ├─→ RI-9
                                                   └─→ RI-10

RI-1/RI-2 ──generates──→ RT-4 (Recursive Adaptive Response, v1→v4)
RI-10 (Breaker Mode) ──generates──→ RT-4 (v2 explicitly "post-Breaker")
RI-10 (Evidence Ladder / Breaker Mode) ──generates──→ RI-17 (negative-knowledge result)

RI-5 (nature as library) ──generates──→ RI-6 (organism challenges)
RI-5 ──generates──→ RI-7 (candidate: "whole doesn't control parts")
      [same edge already formally proposed as `derived_from` in
       DATASET-1-REAUDIT.md's finding F-4]

RI-9 (Investigation gate) ──instantiates──→ RI-12 ("Registry never
                                              changes automatically")
RI-8 (Architecture Baseline) ─ ─supports (unfiled)─ ─→ RI-12
      [KMP-0001 already declined to treat these as the SAME claim;
       a weaker supports/derived_from edge was recommended there but
       never formally proposed]
RI-11 (methodology GRIF cluster) ──weak echo──→ RI-12

RI-14 (anti-accumulation) ──weak echo──→ RI-9

RI-13 (Trust Engine) ┄┄resonance only┄┄ {RI-1/RI-2, RI-10}
      [structurally similar move — constraints over surface pattern —
       in a DIFFERENT named project; not drawn as a dependency edge]

RI-18 (Knowledge Crystallization / Reality Observatory)  — isolated,
      no edge in or out (confirms GAP-0001's original finding)
RT-2 (terminology overlap)  — isolated, AG-002 already declined it
```

## Edge table (every edge, with citation)

| From | To | Type | Citation |
|---|---|---|---|
| `RI-16` | `RI-1`/`RI-2`, `RI-9`, `RI-10`, `RI-15` | justifies | `RI-16`'s sensor-chain hypothesis is the stated reason no single perspective (human or AI) can self-certify — the structural reason external checks exist at all |
| `RI-3` | `RI-1`/`RI-2`, `RI-9` | justifies | `RI-3` Article 2, *"Reality is the final arbiter"* — the Kernel and the Investigation-gate are both this axiom made procedural |
| `RI-15` | `RI-1`/`RI-2`, `RI-9`, `RI-10` | names/generalizes | `RI-15` cites *"KOD Kernel architecture itself"* as one of five convergence domains — an explicit, source-stated link, not inferred |
| `RI-1`/`RI-2` | `RT-4` | generates | Recovery Report's own text: `RT-4` is *"direct evidence the Kernel protocol is not just aspirational"* |
| `RI-10` | `RT-4` | generates | `RT-4`'s v2 is explicitly labeled *"post-Breaker"* — `RI-10`'s own named mode |
| `RI-10` | `RI-17` | generates | `RI-17`'s meta-observation (formulate → attack → discard → keep smallest core) restates `RI-10`'s Evidence Ladder / Breaker Mode in applied form |
| `RI-5` | `RI-6` | generates | same entry (`20260625`), `RI-6` supplies the concrete organism cases `RI-5`'s method calls for |
| `RI-5` | `RI-7` | generates | already formally proposed as `derived_from` in `DATASET-1-REAUDIT.md` finding `F-4` |
| `RI-9` | `RI-12` | instantiates | `RI-12`'s *"the Registry never changes automatically... every update is a proposal"* is `RI-9`'s governance rule applied to one concrete system |
| `RI-8` | `RI-12` | weak, unfiled | `KMP-0001` examined this pair directly and declined to merge them; a `supports`/`derived_from` relationship was recommended there but never filed — this report does not file it either, consistent with not relitigating `KMP-0001`'s own decision |
| `RI-11` | `RI-12` | weak echo | chronologically adjacent (`20260702`→`20260703`), both about consolidating/storing validated methodology, no stated link |
| `RI-14` | `RI-9` | weak echo | anti-accumulation (*"does not grow by addition"*) resonates with gated, non-automatic growth, but governs a different question (stance toward existing material vs. process for adding new material) |
| `RI-13` | `RI-1`/`RI-2`, `RI-10` | resonance only | same underlying move (constraints over surface pattern) in a **different named project** — deliberately not drawn as a dependency; see `COUNTER-THEORY.md` |
| `RT-1` | `RI-3` | weak echo | *"never defend the conclusion, defend the method"* is a corollary of, not a new claim beyond, `RI-3`'s own honesty-to-reality article |

## What the graph shows

- **Two root justifications, no single root.** `RI-3` (an axiom) and
  `RI-16` (an epistemic-limits argument) both independently justify the
  same cluster of mechanisms (`RI-1`/`RI-2`, `RI-9`, `RI-10`) without
  either being downstream of the other. A graph with two independent
  roots converging on the same targets is stronger evidence of real
  structure than a single root would be — two different kinds of
  argument (an asserted axiom, and a limits-based argument) reaching the
  same place.
- **`RI-15` is not a root — it is dated after every node it names.**
  This is worth stating plainly: `RI-15`'s explanatory power comes from
  making an already-operating pattern explicit, not from having caused
  it. Treating a later, naming node as if it were foundational is
  exactly the kind of narrative-fallacy risk `COUNTER-THEORY.md`
  examines directly.
- **Two genuine `generates` edges are the strongest evidence in this
  entire report**: `RI-1`/`RI-2` → `RT-4` and `RI-10` → `RT-4`, both
  because the target (`RT-4`) is a real, dated, revised artifact whose
  own content names the mechanism that produced it (*"post-Breaker"*),
  not an inference this report supplies.
- **`RI-18` and `RT-2` are confirmed, not just asserted, as isolated** —
  this graph independently reproduces `GAP-0001`'s original finding
  about `RI-18` (a zero-degree node) using a different method (explicit
  edge search here, vs. `GAP-0001`'s structural gap-screening), which is
  itself a small piece of corroborating evidence, not a coincidence to
  ignore.
- **`RI-13` is deliberately drawn outside the dependency graph proper.**
  It is real evidence for a *broader* pattern than one project's
  philosophy, which is exactly why it cannot be drawn as a dependency
  *within* a graph whose nodes are otherwise all KOD-internal — see
  `META-THEORY-REPORT.md` Q1 and `COUNTER-THEORY.md`.
