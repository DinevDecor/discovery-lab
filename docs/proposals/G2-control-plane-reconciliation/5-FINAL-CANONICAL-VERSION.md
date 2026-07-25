# Unified Control Plane Specification — v0.1 (Reconciliation Draft)

**Status: DRAFT — Candidate for Adoption.** Not self-ratified — see
`README.md`. Reconciles `project-memory/adr/ADR-0001` (+ the Stable
Core of `AI-Collaboration-Architecture-v1_1.md` it accepts),
`kod/Core/ADR/ADR-0009`, and `discovery-lab/GOVERNANCE.md`. Full
reasoning, citations, and open gaps: `1-UNIFIED-CONTROL-PLANE-
SPECIFICATION.md` through `4-CONFLICT-RESOLUTION-LOG.md` in this same
directory. This document is the clean text; those are its working
record.

## 1. Source of Truth

Versioned repository artifacts — commits, accepted decisions,
contracts — are authoritative. Conversation, chat memory, and prompts
are never authoritative; at most, raw material for a future artifact.

## 2. Contract-Defined Roles

A role is a versioned, repository-stored contract, not a prompt and
not a fixed model. A contract defines mission, inputs, outputs,
authority, prohibitions, and definition of done. An executor — human
or AI — binds to a specific contract version; the contract, not the
executor's identity, governs what may be done. Changing a contract's
scope of authority is itself a governed change, not a casual edit.

## 3. Formal Gate

Before an artifact becomes authoritative, it passes a bounded,
criterion-based check, distinct from open-ended critique. This check:
verifies the artifact against a fixed, applicable standard; returns a
small enumerated verdict (e.g. `PASS`/`BLOCKED`, or a stated verdict
per stage); never invents criteria beyond the applicable standard;
never edits the artifact; never assigns work; never merges; never
renders the final human decision. Independence between the gate and
the artifact's author is preferred; where not practiced, that fact
must be disclosed, not omitted. [Note: the exact formality and
contract-binding of this gate varies by context — see
`4-CONFLICT-RESOLUTION-LOG.md` C1; this specification states the
shared shape, not a single uniform implementation.]

## 4. Human Final Authority

Accepting a proposal, merging to a shared branch, resolving a
normative/operational mismatch, and changing the governing rules
themselves belong only to a human — never to an AI role, regardless of
seniority. No process may certify its own final outcome; the same act
that produces an artifact under review may not also be the act that
finally accepts it.

## 5. Drift

When what a system is authorized to do and what it actually does
diverge, this is a named, first-class state, not an error to conceal
and not a condition either layer resolves automatically. Detection
blocks the affected work; a short analysis records what diverged,
since when, and why; a human then decides exactly one of: the
operational reality is wrong (fix it to match authority), the
normative authority is stale (supersede it), or both are partially
right (a new decision plus a fix). The state is closed only once
recorded.

## 6. Communication and Handoff

Agents do not communicate directly or autonomously. Work crossing a
session or agent boundary does so through a structured, written
Handoff: goal, what was done, small undocumented decisions worth
keeping, what remains undone, the next concrete step, known traps, and
open questions. A Handoff is never itself evidence and never replaces
the repository artifacts it references. The mechanism is currently
human-mediated; this is acknowledged as the current implementation,
not a permanent architectural commitment — future automation may
replace it without changing the underlying model.

## 7. Staged, Human-Gated, Revisable Lifecycle

An artifact or role moves from proposed to authoritative through named
stages, at least one formal gate, and a terminal human decision. The
process may be re-entered for substantive revision; the scale of a
change determines whether re-entry, a lighter versioned update, or an
in-place correction is required. No stage certifies itself.

## What this version does not claim

This specification does not resolve: whether Human Final Authority
binds every role-acceptance act in every one of the three source
ecosystems equally (open per `4-CONFLICT-RESOLUTION-LOG.md` C3);
whether Drift or an anti-complacency check apply outside the source
that names them (C4, C5); or how a generic cross-project role taxonomy
(PM, KOD) relates to a domain-specific Role's own lifecycle governance
(DL) (C2). These remain open, by design, pending a human decision — not
closed by this reconciliation.
