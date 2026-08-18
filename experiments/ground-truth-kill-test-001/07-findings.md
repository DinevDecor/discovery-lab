# Ground-Truth Ablation & Kill Test 001 — Findings

**Status: dataset archaeology only. No model was called. No experimental arm was run.**

This document records why. Per the task's own Section 2 stop rule, an insufficient
dataset is a valid, reportable result in itself — it is recorded here rather than
patched over with weak pseudo-outcomes.

## What was searched

Every directory in the repository with a plausible claim to holding a real,
externally-resolved case was inspected read-only: `constraint-archaeology-agents/`
(anomalies, observations, gate decisions), `business-candidate-analyst/` (candidates,
candidate_events, material-events reports), `calendar-arbitrage-watch/`,
`x-signal-probe/`, `capability-observatory/`, `case-claim-kernel/`,
`blind-analysis-kernel/`, `adversarial-review-kernel/`, `docs/reviews/`,
`docs/decisions/`, `docs/method/controls/`, `constraint-change-observatory/`,
`reality-sensor/`, `headquarters/`, and the full `git log` (98 commits, all real
timestamps). Thirteen candidate sources were identified and individually assessed
against criteria A–G; all thirteen are recorded in `01-preregistration.jsonl` with
`eligible: false` and a specific `exclusion_reason`. Two structural problems account
for essentially all of them.

## Problem 1 — the live pipeline has no real T0→T1 separation yet

The repository's actual git history spans exactly **2026-08-08 to 2026-08-18 (11
calendar days)** — confirmed both from commit timestamps and from every in-file
`first_seen`/`created_at` date found. Within that window:

- `constraint-archaeology-agents/data/anomalies.json` (419 records) is a **rebuilt
  daily snapshot, not an accumulating history** — every single record shows
  `status=WATCH`, `first_seen=last_seen=2026-08-16`. Zero anomalies have ever left
  WATCH.
- `business-candidate-analyst/data/candidates.json` (161 records): 159 are still
  `WATCH`, 2 are `VALIDATING`. Across the entire corpus there is exactly **one** real
  state transition ever recorded — `BC-0130`, `WATCH → VALIDATING`, 2026-08-14 to
  2026-08-16 (2 days). That transition is a procedural gate reassessment
  (`distinct_sources>=2`) performed by the same pipeline re-scanning the same class of
  forum evidence — it is not an external reality check, and 2 days is nowhere near
  enough time for a real business proposition to resolve either way. It is recorded
  individually (`GTK001-03`) as the closest near-miss found anywhere in the live
  system, and it still fails criteria D and G.
- `calendar-arbitrage-watch/data/` and `x-signal-probe/data/` contain **no records at
  all** — only `.gitkeep` placeholders, despite both modules' pipeline code being
  merged.
- `capability-observatory/` holds access-attempt telemetry (mostly `access_blocked`),
  not decision-relevant propositions.

None of this is a criticism of the pipeline — 11 days is simply too short a window for
any of these systems' real propositions (is this anomaly a real mechanism, is this
market opportunity real) to have resolved in reality yet. This is expected, not a
defect, and it is exactly the kind of ground truth this repository will eventually
accumulate. It does not exist yet.

## Problem 2 — the only real historical T0→T1 cases in the repo are famous enough that training-data contamination cannot be ruled out

`docs/method/controls/` contains four genuinely rich historical cases, each already
structured almost exactly like a "blind, freeze-then-reveal" experiment:

| case | domain | T0 freeze | T1 outcome | polarity |
|---|---|---|---|---|
| `02-negative-control-modular-housing.md` | factory/modular housing construction | ~2017-2018 | Katerra bankruptcy (2021), Ilke Homes collapse (2023), L&G modular wind-down (2023) | NEGATIVE |
| `03-positive-control-containerization.md` | intermodal shipping containers | 1955 | Malcolm McLean's first voyage (1956) through Sea-Land's 1969 sale; ~36x cost reduction, industry-wide adoption | POSITIVE |
| `04-false-negative-control-foundry.md` | pure-play semiconductor foundry | ~1985-1987 | TSMC founded Feb 1987, became the dominant pure-play foundry | POSITIVE |
| `05a`+`05b-false-positive-control-fiber.md` | wholesale long-haul fiber buildout | 31 Dec 1997 | Global Crossing and cohort (360networks, Williams Communications, KPNQwest) bankrupt 2001-2002 | NEGATIVE |

`constraint-change-observatory/data/constraints.json` adds 14 more (DNA sequencing
cost, containerization again, long-distance telephony, interstate branch banking,
solar PV, GPS/taxi dispatch, cloud vs. on-prem, digital photography, online banking,
3D printing, LED lighting, music streaming, distributed solar/grid, e-commerce).

This is a genuinely well-balanced set on paper (2 clean positives, 2 clean negatives
in the controls; a mostly-SHIFTED spread in the CCO records) — and if it could be used
safely, it would comfortably clear the 8-10 case target. It cannot be used safely, for
two independent reasons:

1. **Every one of these cases is a famous, extensively documented business-history
   narrative** — Malcolm McLean and the shipping container, TSMC's founding, the
   Global Crossing/dot-com-era fiber bust, and Katerra's collapse are all
   textbook-level, Wikipedia-depth stories, and the `constraint-change-observatory`
   cases were **explicitly, admittedly selected** for being "canonical 'technology
   disrupted X' narratives" (per the corpus's own 10-case falsification review). The
   task's rule is not "assume contamination is fine unless proven" — it is the
   opposite: "do NOT claim a case is absent from model training data unless this is
   actually knowable." Here the honest, knowable answer is that high contamination
   risk is not just unruled-out but actively likely. Feeding a frontier model a
   redacted T0 packet about Malcolm McLean or TSMC does not hide the ending from the
   model — it only hides it from the model's input context, while the model's
   parametric memory almost certainly already has the ending. A model could produce a
   confident, apparently insightful ADVANCE/REJECT purely by recalling public history,
   which would make every arm (A1/A2/B/C) score identically well for reasons that have
   nothing to do with the multi-model architecture — precisely the false signal this
   experiment exists to avoid manufacturing.

2. **The source material for both groups is not raw T0 evidence — it is a completed
   prior analysis.** The four `docs/method/controls/` documents each already contain a
   full 13-15-field structured write-up and a recorded verdict, produced specifically
   to validate the Constraint Archaeology *method*. Using any extract of them as a
   "T0 packet" would hand the experimental models a prior analyst's finished reasoning
   to repeat or grade, not raw facts to independently interpret. The
   `constraint-change-observatory` records compound this: every record's `analyst`
   field reads `"Claude (directed research pass)"`, with a single `first_seen` of
   2026-08-10 — meaning one model session researched and wrote *both* the
   `historical_evidence` (T0) and `current_evidence` (T1) fields together, already
   knowing the full arc. Any "T0-only" extract built from these records is therefore a
   hindsight-informed selection, not an independently blind time capsule, even before
   the separate training-data question is considered.

Two smaller sources were also checked and ruled out on simpler grounds:
`reality-sensor/validation-dataset/` (10 AI-ecosystem signal captures, 2026-07-11 to
2026-07-25) reports events that had *already happened* at capture time — there is no
forward-looking proposition with a pending resolution, the capture IS the resolution.
`docs/reviews/2026-08-08-cross-source-candidate.md` is a same-day adversarial review
whose REJECT verdict is the reviewer's own contemporaneous opinion, with zero time
separation from the evidence it reviews.

## Why this experiment did not proceed to build even a partial dataset

The task's stop rule is explicit and was followed exactly: **"Do not fabricate cases.
Do not use weak pseudo-outcomes. Do not substitute simulated ground truth."** Every
avenue that would have reached the 5-case minimum required either (a) accepting an
internal system state as external ground truth (`BC-0130`), which the task separately
and explicitly forbids for `WATCH`-shaped states, or (b) accepting a case whose
"hidden" T1 outcome is not actually hidden from a frontier model's training
knowledge, which would not test what the experiment is designed to test. Neither is a
legitimate substitute for a real, low-contamination, externally-resolved case.

## What would resolve this

- **Time.** The live pipeline (CA/BCA/calendar-arbitrage) needs weeks-to-months of
  real operation before any anomaly or candidate has a genuine chance to resolve one
  way or the other in the real world. A rerun of this kill test in, say, 60-90 days
  would very plausibly find several real WATCH→(something durable) cases with
  externally-checkable resolutions, assuming the pipeline keeps running.
- **Deliberately recent, obscure cases**, chosen specifically because they are *too
  small or too recent* to be well-covered — e.g. a specific, named individual
  developer/project situation with a checkable later update (did they ship it or
  abandon it) — would sidestep the "famous case" contamination problem the
  `docs/method/controls`/CCO material has. None currently exist in this repository
  with a real, verifiable later resolution; building them would require either (a)
  waiting for the live pipeline's own anomalies/candidates to age, or (b) a
  deliberately-scoped follow-up research pass to find small, checkable, recent (2025-
  2026), non-famous cases from public sources — explicitly out of scope for this task,
  which was read-only archaeology of the existing repository.

## Scope discipline

No prompts, materiality rules, Judge policy, evidence-packet schema, or falsification
taxonomy were touched. No provider, agent platform, scheduler, or Stage 5 router was
added. No case was fabricated. No synthetic disagreement was introduced. No model was
called — `MODEL_CALLS_EXECUTED: 0` is exact, not rounded.
