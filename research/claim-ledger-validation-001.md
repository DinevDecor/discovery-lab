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

**SAVE-001** (2026-08-18, Day 3, from CLV-002 reconciliation): The anomaly ID `ANOM-0362` was confirmed, on two independent checks two days apart, to have pointed at three different underlying observation sets (Day 0/probe: fly.io idle-machines, 1 obs; Day 1: orphaned-subagents, unrelated content; Day 3: fly.io idle-machines again, 2 obs) — and the same pattern independently reproduced on `BC-0130`'s own `anomaly_ids` field (`[ANOM-0321, ANOM-0392]` → `[ANOM-0324, ANOM-0396, ANOM-0432]` across the same window, same candidate, same core evidence). This is a "stale evidence citation on a still-cited claim" pattern — a reference that reads as durable but silently isn't — and it would very likely have been missed without a persistent record spanning the two check dates: reading either day's `anomalies.json` alone, in isolation, gives no indication the ID is unstable; only comparing today's content against a fixed record of what the ID held two days ago exposes it. **Caveat kept attached, per the adversarial framing this experiment asked for:** this does not appear to affect BCA's own promotion arithmetic, which keys off `OBS-####` IDs and source names (both stable across the same runs), not `ANOM-####`. The practical risk is narrower than "this breaks the pipeline" — it is "any *report* (including this repository's own research artifacts) that cites an `ANOM-####` as if it were a durable reference is citing something less stable than it appears."

**SAVE-002** (2026-08-18, Day 3, from CLV-001 reconciliation): `BC-0130`'s VALIDATING promotion rests on grouping what read, on manual reciprocal-repair analysis against this repository's own stated same-mechanism standard, as three distinct failure mechanisms (pre-execution spend-ceiling gap; idle-machine monitoring gap; pricing-model confusion) under one candidate, inflating its apparent "2 distinct sources" into what may functionally be three separate single-source opportunities miscounted as one multi-source one. A reader trusting the report's `VALIDATING` label at face value — the only signal a non-ledger read would surface — would not see this; it only surfaces by explicitly restating the claim as falsifiable ("these anomalies are the same underlying opportunity") and checking it against a named standard, which is exactly the discipline the ledger schema forces and a quick read does not.

## 4. Daily run log

| Day | Date (UTC) | BCA report checked | New claims logged | Reconciliation done | Notes |
|---|---|---|---|---|---|
| 0 (setup) | 2026-08-16 | `business-candidates-2026-08-15.md` (baseline only, not logged from) | 0 | — | Ledger created; waiting for first new run |
| 1 | 2026-08-16 | `business-candidates-2026-08-16.md` (real scheduled run 31... completed 22:57:58Z, merged into this branch) | 2 (CLV-001, CLV-002) | N/A — no prior OPEN claims to reconcile yet | One real lifecycle escalation (WATCH→VALIDATING) landed on Day 1; both logged claims are about that escalation's evidentiary basis, not manufactured for volume |
| 2 | 2026-08-17 | none — no new report produced | 0 | None possible — no new data; CLV-001/CLV-002 remain OPEN unchanged | Real pipeline failure, not a delay: run `32075974441` (schedule, main), unit-test steps 4–6 all passed, step 7 "Run daily pipeline" itself failed after 26 min (22:26:04Z→22:52:52Z), commit step correctly skipped. `main` still at yesterday's head (`f2ff868`). Per protocol: 0 claims logged, no diagnosis/fix attempted (out of scope for this experiment) |
| 3 | 2026-08-18 | `business-candidates-2026-08-18.md` (pipeline recovered; `material-events-2026-08-18.json` empty — no lifecycle transitions today) | 0 new; 2 reconciled (CLV-001, CLV-002) | Both CLV-001 and CLV-002 reconciled against fresh data; **2 CLAIM_LEDGER_SAVE events logged (SAVE-001, SAVE-002)** | No new claims manufactured for volume — today's work was entirely reconciliation of Day 1's open claims, which is where the material findings actually landed |

## 5. Claims

### CLV-001
- Timestamp / as-of: 2026-08-16T22:59:16Z (BCA report timestamp)
- Candidate / workflow: BC-0130 (Business Candidate Analyst, Mode A) — lifecycle escalation WATCH → VALIDATING, recorded in `business-candidate-analyst/reports/material-events-2026-08-16.json` as `state_changed:BC-0130`, reason "reached VALIDATING: distinct_sources>=2 (have 2); economic_consequence EVIDENCED"
- Exact claim: BC-0130's two grouped anomalies — ANOM-0321 ("Enforcing spend ceiling per user session or agent run when LLM calls paid external functions") and ANOM-0392 ("Tracking cloud infrastructure cost and machine provisioning state — idle resources ran unnoticed... accumulating $600 charge") — describe the same underlying business opportunity.
- Claim type: INFERENCE
- Evidence tier: T1 (single source: BCA's own grouping output; not independently corroborated that these are one mechanism)
- Sources: `business-candidate-analyst/data/candidates.json` (BC-0130 record, `anomaly_ids: [ANOM-0321, ANOM-0392]`); `constraint-archaeology-agents/data/anomalies.json` (ANOM-0321, ANOM-0392 canonical_pattern text); `business-candidate-analyst/README.md` §"Deduplication: same underlying opportunity, not same wording" (merge rule: `buyer_bucket` + `function_class` match + ≥2 shared taxonomy keywords vs. a single anchor observation — explicitly a keyword/bucket heuristic, not `ca_agents.same_mechanism_gate`'s reciprocal-repair test; the same README states plainly that "false merges within a bucket are structurally possible even after these fixes")
- What would falsify it: Running (or manually reasoning through) a reciprocal-repair test on ANOM-0321 vs. ANOM-0392 — does fixing "add a pre-execution spend ceiling to metered LLM function calls" also fix "no alerting when a manually-scaled-up machine is never scaled back down," and vice versa? If the fixes are independent (plausible: one is a pre-execution budget/approval gate, the other is a post-hoc resource-lifecycle/idle-detection monitor — the exact same two-layer distinction drawn in `docs/research/ai-agent-cost-governance-opportunity-probe.md` §2's Layer C vs. Layer D split), the claim is falsified.
- Decision dependency: If falsified, BC-0130's VALIDATING state is a false positive from this run's own stated promotion rule ("distinct_sources>=2") — the "2 sources" are actually 2 different opportunities each still resting on 1 source, and correct treatment is two separate WATCH candidates (frequency still INSUFFICIENT_DATA each), not one VALIDATING candidate. Matters directly to research prioritization: VALIDATING is meant to signal stronger multi-source corroboration than either sub-claim independently has.
- Reused from earlier claim?: NO (first mention in this ledger; thematically adjacent to, but not reused from, the "E. Agent Cost Governance" finalist scored `recurrence: 3/10` in the prior Claim Ledger opportunity-archaeology artifact — noted as a cross-reference only, not counted as reuse)
- Same claim or changed claim?: N/A — first mention
- Current status: OPEN

**Reconciliation note, 2026-08-18 (Day 3):** BC-0130 gained a third observation today (`OBS-20260818-0022-9ac98d`), still within the same 2 distinct sources (fly-io, openai-devs) — `independent_observation_count` went 2→3, `evidence_diversity` unchanged. The new observation's text is explicitly about **pricing-model confusion** ("customer (non-technical) trying to understand pay-as-you-go vs fixed pricing... confusion about pricing structure; user expects fixed monthly plans but provider uses metered billing") — a *third*, textually distinct thread now folded into the same candidate alongside the original two (pre-execution spend-ceiling gap; idle-machine monitoring gap).
Applying this repository's own same-mechanism standard (`CLAUDE.md`: "Two anomalies merge only if each one's own repair removes the other's failure, in both directions") as a manual reciprocal-repair check across all three threads: a pre-execution budget gate on metered calls does not fix idle unmonitored machines; idle-machine alerting does not fix a model over-calling a metered function mid-run; and clearer pricing documentation fixes neither. None of the three repairs the other two. By this repository's own documented standard, **these read as three different mechanisms, not one** — this is my own reasoned inference applying that standard, not a pipeline-verified fact (BCA does not run the reciprocal-repair test itself; its own README states its merge rule is a coarser keyword/bucket heuristic).
Classification: **CONTRADICTS** (the claim that these are "the same underlying opportunity" is contradicted by this repository's own same-mechanism standard, applied manually). Current status updated: **WEAKENED** (not FALSIFIED outright — I have not run the actual `ca_agents.same_mechanism_gate` code against this text, only reasoned by hand from its stated principle; a stronger falsification would run the real gate).

### CLV-002
- Timestamp / as-of: 2026-08-16T22:59:16Z (anomalies.json as merged into this branch) vs. 2026-08-16T07:38Z (probe's own stated timestamp, same calendar day, ~15h earlier)
- Candidate / workflow: `constraint-archaeology-agents` anomaly registry, cross-referenced against `docs/research/ai-agent-cost-governance-opportunity-probe.md` §1's evidence table (a same-repository artifact produced earlier the same day, before this experiment began)
- Exact claim: The anomaly ID `ANOM-0362`, as it currently reads in `constraint-archaeology-agents/data/anomalies.json` after today's run, has a different canonical_pattern (orphaned subagents, `OBS-20260815-0031-8266d1`) than the pattern the same-day-earlier opportunity probe attributed to `ANOM-0362` (fly.io idle machines / ~$600, `OBS-20260815-0022-5480ed`) — that observation now appears un-anomaly-numbered the same way in this run's file (it is `BC-0139`'s cited evidence, but its current `ANOM-####` grouping was not independently re-confirmed this pass).
- Claim type: OBSERVATION
- Evidence tier: T4 (directly diffed two committed artifacts — the probe's own table text vs. today's `anomalies.json` content for the same ID)
- Sources: `docs/research/ai-agent-cost-governance-opportunity-probe.md` §1 table (branch `claude/ai-agent-cost-governance-probe-9axch5`, commit `8a2f922`); `constraint-archaeology-agents/data/anomalies.json` as of commit `f2ff868` (merged into this branch today)
- What would falsify it: Re-reading the probe's table and finding a transcription error on my part (i.e. it never actually said `ANOM-0362` = fly.io); or discovering `anomalies.json`'s ID space is sharded/scoped in a way that makes two same-numbered entries not actually comparable (e.g. per-run files rather than one running file) rather than one flat, reused ID space.
- Decision dependency: Any report — including this repository's own prior research artifacts — that cites a constraint-archaeology `ANOM-####` as if it were a stable, durable reference risks silently pointing at different content a day later. This repo's own `CLAUDE.md` already documents `anomalies.json` as a **snapshot file, not an append-only ledger** ("Snapshot files remain runtime truth... Do not migrate readers") — so the *underlying* non-durability is expected/known infrastructure behavior, not a hidden defect. The open question for reconciliation is narrower: whether a persistent claim ledger is what actually catches the risk of a *report* citing a snapshot ID as if it were durable — or whether that risk is equally visible without one, in which case this is closer to a false positive than a save. Marked OPEN, not pre-judged.
- Reused from earlier claim?: NO
- Same claim or changed claim?: N/A — first mention
- Current status: OPEN

**Reconciliation note, 2026-08-18 (Day 3):** checked `ANOM-0362` a third time. Today it reads: canonical_pattern "Managing cloud compute machine lifecycle after parallel batch jobs complete — 40 idle machines ran unnoticed for two weeks... $600", `observation_ids: [OBS-20260815-0022-5480ed, OBS-20260818-0077-df0218]`, `first_seen: 2026-08-18`. This is the fly.io story again — matching the *original probe's* content (Day 0) better than Day 1's content did — but it is not identical to either prior state: Day 0 (probe) cited exactly one observation (`...5480ed`); Day 1 cited zero fly.io observations (orphaned-subagents instead); Day 3 cites two (`...5480ed` plus a new `...df0218`). `first_seen` also reset to `2026-08-18`, even though `...5480ed` was first captured 2026-08-15 — confirming this field tracks the anomaly *record's* lifetime, not the underlying observation's age.
Independently, `BC-0130`'s own `anomaly_ids` field (checked directly in `candidates.json`) also changed this run: `[ANOM-0321, ANOM-0392]` (Day 1) → `[ANOM-0324, ANOM-0396, ANOM-0432]` (Day 3) — three different numbers, for the same stable `candidate_id` and (mostly) the same underlying `OBS-####` evidence. Across both checks, the pattern is now consistent and reproducible: **`ANOM-####` numbering is rebuilt/reassigned on every pipeline run; it is not a persistent identifier**, while `BC-####` (candidate) and `OBS-####` (observation) evidence IDs are stable across the same runs.
Classification: **IDENTITY_BREAK**, now confirmed on two independent checks (Day 1 and Day 3), not merely flagged. Current status updated: **SUPPORTED** (the claim as stated — that the ID drifted and doesn't durably identify content — holds up; the caveat noted on Day 1, that this doesn't touch BCA's own promotion math since that keys off `OBS-####`/source names rather than `ANOM-####`, also still holds and is worth keeping attached to this finding so it isn't overstated).

*(written at experiment end — see §0 for the stop condition)*
