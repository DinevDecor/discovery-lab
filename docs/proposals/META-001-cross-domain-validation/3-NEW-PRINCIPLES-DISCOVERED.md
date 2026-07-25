# Deliverable 3 — New Principles Discovered

Per `META-001` Phase 3. Principles that appear independently, with real
architectural weight, in the cross-domain sample, but that `RI-0002`
never suggested in any form. Their existence is itself evidence about
the diary's own limits as a source — some real, load-bearing
architectural ideas in this ecosystem simply never came up in one
person's diary entries about one project.

## 1. Named artifact/task ownership

*"Every artifact has exactly one writer or owner at any given moment,
never 'the organization.'"*

- `kod`'s `ADR-0009` Writer Matrix: "Every artifact has exactly one
  writing authority. Changing a writer requires an ADR."
- `project-memory`'s Handover architecture, principle 5: "Every object
  has a named owner at every moment... never 'the organization,' always
  a person."
- `project-memory`'s AI Collaboration Architecture: Issue ownership as
  one of three "cheap mechanisms" for parallel-work conflict control.

`RI-0002` contains nothing resembling this — no recovered idea in the
diary addresses who is accountable for a specific artifact at a specific
moment. This is a governance concern that only becomes visible once
multiple actors (human or AI) are actually working on shared artifacts
concurrently — a situation the diary's own research-journal format
never had to face.

## 2. A numeric score gates an escalation *tier*, never the final action

*"A computed score determines how urgently something is reviewed; it
never determines, by itself, whether the reviewed action is taken."*

- `trust-engine`'s `proposal_quality_gate_architecture.md`: `EQS`
  (`0–100`) maps to `IGNORE`/`LOG_ONLY`/`PROPOSE`/`ESCALATE` — "Even
  `CRITICAL` does not mean automatic trust mutation."
- `project-memory`'s Handover architecture: a configurable `confidence`
  threshold on AI-extracted fields gates whether a field can be
  bulk-confirmed or needs an individual click — the score changes review
  friction, never acceptance.

`RI-0002` has numeric `confidence` values on individual GRIFs
(`0.82`–`1.00`), but never this specific mechanism: a score used
specifically to *route* attention while a separate, unconditional gate
still stands between any score and any actual mutation of state. This
is a more mature, more specific pattern than anything the diary
recovered.

## 3. A two-layer authority model with a named mismatch state

*"Normative authority (what the system has the right to do) and
operational reality (what it actually does) are separate layers with no
automatic winner; their mismatch is a named, first-class state, not a
silent bug."*

- `project-memory`'s AI Collaboration Architecture: `Architecture–
  Implementation Drift`, with an explicit "the shame is unnoticed drift,
  not drift itself" framing, and a required three-way resolution (code
  is wrong / ADR is stale / both partially right).
- A partial, weaker echo in `kod`'s `ADR-0009` precedence order for
  disagreeing artifacts, which addresses a similar problem without
  naming it as its own state.

This is real and specific enough that it is not merely a restatement of
`P2` (one authoritative representation) — `P2` is about *which* record
is authoritative; this principle is about *what happens procedurally*
when reality and the authoritative record diverge, which `RI-0002`
never addresses at all (the diary has no equivalent of "code" vs.
"architecture" to diverge from each other).

## 4. An explicit "anti-theater" self-check

*"A validation process that always returns the same easy answer is
itself a failure signal, not a success signal."*

- `project-memory`'s AI Collaboration Architecture, `§8`: "if 20
  consecutive Kernel checks return PASS, this is not success — it is a
  signal that the review contracts are too weak or Kernel is not being
  applied where it hurts."

This is the single most conceptually sophisticated new principle found
in this validation. It has no equivalent anywhere in `RI-0002`, and it
is also the closest thing in the entire cross-domain sample to
addressing `RI-0002`'s own hidden assumption `H1` (the validating
mechanism is never itself checked) — not a full solution to that regress
problem, but a real, independently-built, partial countermeasure to
exactly the risk `H1` named as unexamined. Worth flagging explicitly:
this principle was discovered *because* the cross-domain search was
run, and it retroactively strengthens one part of the original
`RI-0002` analysis (`H1`) that the diary alone could never have
supported.

## Provenance

`PHASE1-BLIND-CLASSIFICATION.md`, `PHASE2-PATTERN-EXTRACTION.md`,
`PHASE3-5-WORKING-NOTES.md`. `H1` reference:
`../AG-003-meta-theory-RI-0002/META-THEORY-REPORT.md` Q6.
