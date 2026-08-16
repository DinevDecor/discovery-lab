# Claim Ledger — 7-Day Manual Validation (CLV-001)

**Status:** IN PROGRESS
**Started (setup):** 2026-08-16 13:54 UTC
**Day 1 begins:** with the first Business Candidate Analyst output produced *after* this setup — the 22:00 UTC 2026-08-16 run of `constraint-archaeology-daily.yml` (Constraint Archaeology → Business Candidate Analyst), or its report file, whichever lands first.
**Ends:** the experiment runs for **at least** 7 consecutive calendar days from Day 1's first logged claim, **and** requires **at least** 20 decision-relevant claims — both conditions must hold, not either. Concretely: if 20 claims accumulate before day 7, logging/reconciliation continues anyway through the end of day 7, and the experiment concludes then. If day 7 arrives with fewer than 20 claims logged, the experiment continues past day 7, logging only, until 20 decision-relevant claims are reached. The moment both the 7-day minimum and the 20-claim minimum are satisfied, the experiment stops immediately and the final report is issued. (Corrected 2026-08-16, before Day 1 began — the original scaffold below used an "OR, whichever first" rule; nothing else about the schema, save criteria, or daily process changed.)
**This is not a software task.** No product, service, database, or BCA logic change is created by this file or this process. This is a manual, append-only research log.

---

## 0. What this validates

One question only:

> Does an explicit claim ledger prevent materially wrong analytical memory, claim merging, promotion, or reuse often enough to justify becoming a standalone tool?

This document is the append-only ledger itself. Nothing above this line, and nothing in an already-appended entry below, is edited once written. A correction is a new entry that references the claim ID it corrects.

Adversarial framing actively pursued during logging, per instruction: **prefer evidence that "Claim Ledger is merely good research hygiene, not a standalone product"** over evidence that manufactures a save.

---

## 1. What counts as a logged claim

Only a claim expressible as one falsifiable sentence that could materially affect: ADVANCE/REJECT/WATCH/CHEAP_TEST state, prioritization, capital allocation, research direction, interpretation of market structure, assessment of competition, or belief that a constraint/opportunity actually exists. Not logged: scene-setting, restated context, prose quality, or anything not decision-relevant. Real BCA candidates/results only — no claim here is backfilled from data older than this experiment's start.

## 2. Claim record schema

Each entry uses this exact field set:

```
### CLV-NNN
- Timestamp / as-of:
- Candidate / workflow:
- Exact claim:
- Claim type: OBSERVATION | EVIDENCED_FACT | INFERENCE | ASSUMPTION | INSUFFICIENT_DATA
- Evidence tier: T0 (no external evidence) | T1 (single secondary/repeated source) | T2 (multiple independent secondary sources) | T3 (primary source) | T4 (independently measured / directly observed)
- Sources:
- What would falsify it:
- Decision dependency:
- Reused from earlier claim?: NO | CLV-xxx
- Same claim or changed claim?: SAME | NARROWER | BROADER | CONTRADICTS | IDENTITY_BREAK | N/A (first mention)
- Current status: OPEN | SUPPORTED | WEAKENED | FALSIFIED | SUPERSEDED | UNRESOLVED
```

## 3. Critical event log (CLAIM_LEDGER_SAVE)

A `CLAIM_LEDGER_SAVE` is counted **only** when the ledger exposes something that likely would have been missed without it (a claim reused with quietly-weaker evidence than remembered, an inference later misremembered as observed fact, two distinct claims silently merged, a falsified claim still influencing a later decision, a "second source" that's actually the same upstream source, stale evidence on a still-cited claim, `INSUFFICIENT_DATA` misremembered as a negative conclusion, or a decision reversed once the original claim/evidence was reconstructed). Formatting, easier note-taking, generic traceability, or "nice to have the history" do **not** count. Logged below as they're found, not retroactively inflated at report time.

*(none logged yet — populated during reconciliation passes)*

## 4. Daily run log

| Day | Date (UTC) | BCA report checked | New claims logged | Reconciliation done | Notes |
|---|---|---|---|---|---|
| 0 (setup) | 2026-08-16 | `business-candidates-2026-08-15.md` (baseline only, not logged from) | 0 | — | Ledger created; waiting for first new run |

## 5. Claims

*(none yet — first entries land after the 2026-08-16 22:00 UTC pipeline run)*

---

## 6. Final report

*(written at experiment end — see §0 for the stop condition)*
