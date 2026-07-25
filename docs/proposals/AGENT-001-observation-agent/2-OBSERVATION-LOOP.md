# Deliverable 2 — Observation Loop

Per the task's own required cycle: `Reality → Observation → Evidence →
Verification → Finding → Report → Recommendation → Human`. **No step
after Human** — the loop is a straight line, not a cycle in the
automation sense; nothing wraps back into a new action automatically.

## The eight steps, each grounded in an already-ratified or already-exercised mechanism

1. **Reality** — the actual, current, committed content of an
   authorized repository. Not a claim about reality; reality itself,
   read directly (matches `AG-001/ROLE.md`'s own framing and
   `PROP-0001`'s evidence requirement: "each criterion must be freshly
   verified against the repository's current content at review time").
2. **Observation** — a specific, checkable question is asked about
   that content (per `PROP-0001`'s entry criteria: "a specific,
   falsifiable question... No open-ended, unscoped 'look around and
   see' investigations").
3. **Evidence** — file path, line/section reference, and (where
   applicable) commit reference, gathered per `AG-001/RUN-PROTOCOL.md`
   step 5: "No claim is recorded without a matching `Evidence` entry."
4. **Verification** — the evidence is checked against the applicable
   standard: another file's claim, a citable planning document (for
   `C2`-style checks), or the repository's own prior statement about
   itself. Mirrors `AG-003/REVIEW-PROTOCOL.md`'s own Knowledge Review
   discipline (cross-checking a claim against its cited source, not
   trusting the claim at face value) and `KR-0001`'s own demonstrated
   practice.
5. **Finding** — classified using `PROP-0001`'s own fixed vocabulary
   (`MATCH`/`MISMATCH`/`INSUFFICIENT_EVIDENCE`), never an invented
   category.
6. **Report** — assembled per `5-REPORTING-SPECIFICATION.md`. This is
   where multiple Findings from one run are compiled; the Report itself
   makes no decision.
7. **Recommendation** — present only when a Finding is a `MISMATCH`
   with enough evidence to state what appears wrong; phrased as a
   proposal, never an instruction, matching `PROP-0001`'s own
   Principle 0 ("proposes next steps... for the owning repository to
   accept or reject"). **Before a Recommendation reaches a human, it
   must pass a Formal Gate** — the same independent-check pattern
   `AG-003`'s Knowledge Review already exercises for real (`KR-0001`).
   This is not optional: a Recommendation with no Gate step would be a
   proposal reaching Human Final Authority without the check every
   other ratified pattern in this ecosystem requires first.
8. **Human** — Human Final Authority decides: accept, reject, defer,
   or request more evidence. **The loop terminates here.** No branch
   from this step re-enters the loop automatically; a new run, if one
   happens, is a new invocation of step 1, not a continuation.

## Why "no step after Human" is architecturally load-bearing, not just a rule

If anything followed Human automatically, the agent would cease to be
an Observation Agent and would become an execution mechanism —
precisely the boundary `ARCH-002`'s `G1` finding (no execution
mechanism exists anywhere) and this task's own Mission ("This is not an
execution agent") both require staying closed. The loop's shape is the
safety property, not an add-on to it — see `4-SAFETY-ANALYSIS.md`.

## Observation Model — schema

For every individual observation, seven fields, always in this order:

```
Event:                  <what was checked, in one sentence>
Evidence:               <file path, line/section, commit ref if applicable>
Verification Method:    <how the evidence was checked — cross-reference,
                          citation match, date comparison, etc.>
Confidence:             <MATCH | MISMATCH | INSUFFICIENT_EVIDENCE,
                          per PROP-0001's own fixed vocabulary>
Possible Interpretation: <the most likely honest reading — including
                          "may be intentional, not drift" where relevant>
Recommended Action:      <a proposal, or "none — informational only">
Human Needed?:          <YES, always, if a Recommended Action is
                          present; NO for a pure MATCH observation with
                          nothing to act on>
```

## Three worked examples, using real, already-verified findings

**Example 1 — the finding this very proposal surfaced**

```
Event:                  AG-001's own STATUS.yaml run-count vs. its own
                          HISTORY.md and runs/ directory
Evidence:                docs/ai-organization/employees/
                          AG-001-repository-observer/STATUS.yaml
                          ("runs_completed: 0", "last_run: null");
                          .../HISTORY.md ("2026-07-24 — RUN-0001... First
                          real run executed"); .../runs/
                          RUN-0001-observation-report.md (exists)
Verification Method:     Direct cross-reference between two files
                          governed by the same Role
Confidence:               MISMATCH
Possible Interpretation: STATUS.yaml was not updated when RUN-0001 was
                          recorded in HISTORY.md — a bookkeeping gap,
                          not a disputed fact (HISTORY.md and the report
                          file agree with each other)
Recommended Action:      Update AG-001/STATUS.yaml's runs_completed and
                          last_run fields to match HISTORY.md — a
                          bug-fix-tier correction per GOVERNANCE.md
                          (no version bump, no lifecycle re-entry)
Human Needed?:           YES
```

**Example 2 — carried from `DL-001`, re-expressed in this schema**

```
Event:                  project-memory/PROJECT_REGISTRY.md's "Dinev
                          Decor Systems" status vs. the repository's own
                          investigation
Evidence:                PROJECT_REGISTRY.md ("ACTIVE / DISCOVERY");
                          notes/2026-07-19-dinev-decor-systems-location-
                          check.md (concluded INSUFFICIENT ACCESS)
Verification Method:     Cross-reference between a registry claim and a
                          citable investigation in the same repository
Confidence:               MISMATCH
Possible Interpretation: The registry entry predates the investigation
                          and was never revisited after it concluded
Recommended Action:      Flag for project-memory's own maintainers —
                          Discovery Lab has no authority to edit another
                          repository's registry (Principle 0)
Human Needed?:           YES
```

**Example 3 — a clean `MATCH`, included so the schema isn't only shown producing findings**

```
Event:                  generative-discovery-engine's README.md status
                          block vs. STATE.md
Evidence:                README.md ("Project status: DRAFT... Method
                          status: BLOCKED"); STATE.md ("Current verdict:
                          BLOCKED")
Verification Method:     Direct text comparison
Confidence:               MATCH
Possible Interpretation: n/a — no discrepancy found
Recommended Action:      none — informational only
Human Needed?:           NO
```
