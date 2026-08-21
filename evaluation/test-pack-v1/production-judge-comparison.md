# Test Pack v1 — Production Judge Validation

Follow-up to the isolated-subagent run (`ground-truth.json` / `results.json` / `report.md`).
Purpose: isolate whether the split bias observed there belongs to (A) the gate's decision
rule, or (B) the judge substitution used because the interactive session had no
`ANTHROPIC_API_KEY`. Runs the **exact same 10 frozen pairs** from `ground-truth.json`
through the real production judge. Gate code (`same_mechanism_gate.py`), taxonomy,
short-circuit logic, and thresholds are **unmodified** — same as the first run.

**This document's headline evidence is the six-run production distribution (PROD-R1..R6,
60 attempts total), not the original single PROD-R1 sample.** §2 presents that
distribution; the original PROD-R1 walk-through in §3–§10 remains as one specific,
labeled sample within it, kept because its per-case diagnostic reasoning (§8–§10) is
still the most detailed account of *why* individual verdicts land where they do.

## 1. Was the real production judge actually used, all six times?

**Yes.** `evaluation/test-pack-v1/run_test_pack_production.py` imports
`ca_agents.mechanism_judge.ClaudeMechanismJudge` unmodified and calls the real
`profile_anomaly()` / `same_mechanism()` from `same_mechanism_gate.py`. PROD-R1 ran inside
GitHub Actions run [31300689766](https://github.com/DinevDecor/discovery-lab/actions/runs/31300689766)
(workflow `test-pack-v1-production-judge.yml`, triggered by the deliberate commit `d4bd4a6`
on this branch). PROD-R2..PROD-R6 ran via five further dispatches of the same workflow on
this same branch, using the repository's existing `ANTHROPIC_API_KEY` secret — the same
secret the daily pipeline already uses. Their run IDs are visible in this branch's Actions
history for `test-pack-v1-production-judge.yml`. Each run wrote its own untouched
`results-production-judge*.json` file; no run's output was ever edited by hand or
overwritten by another run.

## 2. Six-run distribution — the headline evidence

`aggregate_production_runs.py` (new in this update, see §12) reads all six
`results-production-judge*.json` files and recomputes every number below directly from
them — nothing here is carried forward from a narrative claim.

### 2.1 Per-case table (60 attempts = 6 runs × 10 cases)

| Case | Expected edge | Correct | Wrong | Runtime error | Completed-run edges | Behavior |
|---|---|---|---|---|---|---|
| TP-01 | merged | 3/6 | 3/6 | 0 | related_distinct ×3, merged ×3 | **sampling-sensitive** |
| TP-02 | merged | 1/6 | 5/6 | 0 | related_distinct ×5, merged ×1 | **sampling-sensitive** |
| TP-03 | merged | 4/4 completed | 0 | 2/6 | merged ×4 | stable-correct-when-completed |
| TP-04 | related_distinct | 6/6 | 0 | 0 | related_distinct ×6 | stable-correct |
| TP-05 | related_distinct | 6/6 | 0 | 0 | related_distinct ×6 | stable-correct |
| TP-06 | related_distinct | 6/6 | 0 | 0 | related_distinct ×6 | stable-correct |
| TP-07 | related_distinct | 6/6 | 0 | 0 | related_distinct ×6 | stable-correct |
| TP-08 | unresolved | 0/6 | 6/6 | 0 | related_distinct ×6 | **stable-wrong** |
| TP-09 | unresolved | 0/5 completed | 5/5 completed | 1/6 | related_distinct ×2, merged ×3 | **sampling-sensitive**, stable-wrong on correctness |
| TP-10 | related_distinct | 6/6 | 0 | 0 | related_distinct ×6 | stable-correct |

**Totals: 38 correct, 19 wrong (semantic), 3 runtime errors, out of 60 attempts.**
Accuracy among completed attempts: 38/57 (66.7%). Accuracy including runtime errors as
failures: 38/60 (63.3%).

This directly confirms the five specific per-case counts stated before this aggregator
was built — recomputed here from the JSON files, not accepted on trust:

- TP-01 correctly merged in 3/6 ✓
- TP-02 correctly merged in 1/6 ✓
- TP-03 correct in all 4 completed runs, with 2 runtime errors ✓
- TP-08 0/6 correctly unresolved ✓
- TP-09 0/5 correctly unresolved among completed runs, with 1 runtime error ✓

### 2.2 Per-run table

| Run | Completed | Runtime errors | Correct (of completed) | Edge distribution |
|---|---|---|---|---|
| PROD-R1 | 10 | — | 6 | related_distinct ×9, merged ×1 |
| PROD-R2 | 10 | — | 6 | related_distinct ×9, merged ×1 |
| PROD-R3 | 9 | TP-09 | 7 | related_distinct ×7, merged ×2 |
| PROD-R4 | 10 | — | 7 | related_distinct ×7, merged ×3 |
| PROD-R5 | 9 | TP-03 | 7 | related_distinct ×6, merged ×3 |
| PROD-R6 | 9 | TP-03 | 5 | related_distinct ×8, merged ×1 |

**Stable vs. sampling-sensitive** (§2.1's "behavior" column) is derived only from whether
a case's own completed-run edges agree with each other — never from whether the case is
correct. Six of ten cases (TP-04–07, TP-10, and TP-08) are behaviorally stable: the gate
lands on the identical edge every time it completes, whether or not that edge is right.
Three cases (TP-01, TP-02, TP-09) are genuinely sampling-sensitive — the same frozen pair,
the same unmodified gate code, produces a different edge on different real-judge samples.
TP-03 is stable whenever it completes (always `merged`) but crashed twice.

## 3. PROD-R1 detail — one sample within the distribution above

*(Original single-run write-up, kept for its diagnostic detail. Read §2 first — this
section describes one of six samples, not the aggregate result.)*

### Model / provider (PROD-R1)

| Field | Value |
|---|---|
| Provider | Anthropic |
| API endpoint | `https://api.anthropic.com/v1/messages` |
| API version header | `2023-06-01` |
| Model | `claude-sonnet-4-5` (module default; no `ANTHROPIC_MODEL` override was set) |
| Judge class | `ca_agents.mechanism_judge.ClaudeMechanismJudge` (production, unmodified) |

All six runs used the same model and judge class; nothing here varies run-to-run except
the judge's own sampled responses.

### 10/10 result table — isolated vs. PROD-R1

| ID | expected edge | isolated actual | PROD-R1 actual | isolated result | PROD-R1 result |
|---|---|---|---|---|---|
| TP-01 | merged | related_distinct | related_distinct | FAIL | FAIL |
| TP-02 | merged | related_distinct | related_distinct | FAIL | FAIL |
| TP-03 | merged | related_distinct | **merged** | FAIL | **PASS** |
| TP-04 | related_distinct | related_distinct | related_distinct | PASS | PASS |
| TP-05 | related_distinct | related_distinct | related_distinct | PASS | PASS |
| TP-06 | related_distinct | related_distinct | related_distinct | PASS | PASS |
| TP-07 | related_distinct | related_distinct | related_distinct | PASS | PASS |
| TP-08 | unresolved | unresolved | **related_distinct** | PASS | **FAIL** |
| TP-09 | unresolved | unresolved | **related_distinct** | PASS | **FAIL** |
| TP-10 | related_distinct | related_distinct | related_distinct | PASS | PASS |

**PROD-R1: isolated 7/10, production 6/10.** One case flipped from wrong to right (TP-03);
two flipped from right to wrong (TP-08, TP-09) — a new failure mode not present in the
isolated run, and one that §2 shows recurs across further real-judge samples (TP-09 in
particular: never once correctly unresolved across 5 completed runs).

### Failure location — isolated vs. PROD-R1

| ID | isolated failure location | PROD-R1 failure location |
|---|---|---|
| TP-01 | `failure_classification` (short-circuited: corruption vs absence) | `counterfactual reasoning` (classes agreed on `absence`/`absence`, reached counterfactual, both directions rejected on literal repair wording) |
| TP-02 | `counterfactual reasoning` (classes agreed on `capacity`/`capacity`, counterfactual rejected on carrier-specific wording) | `failure_classification` (short-circuited: **capacity vs latency**) |
| TP-03 | `failure_classification` (short-circuited: unverified vs conflict) | *(none — correct)* classes agreed on `unverified`/`unverified`, counterfactual passed both directions |
| TP-08 | *(none — correct)* left profiled at confidence 0.1, correctly triggered evidence floor | `evidence_threshold` (left profiled at confidence **0.75** despite being the same maximally vague single-anecdote report; floor never triggered) |
| TP-09 | *(none — correct)* right profiled at confidence 0.35, correctly triggered evidence floor | `evidence_threshold` (both profiled at confidence **0.92–0.95**; floor never triggered) |

## 4. Metrics — six-run aggregate

| Metric | Isolated (1 run) | PROD-R1 (1 run) | **Production, 6-run aggregate** |
|---|---|---|---|
| Overall accuracy | 7/10 (70%) | 6/10 (60%) | **38/60 (63.3%)**, 38/57 (66.7%) of completed |
| SAME_MECHANISM (TP-01/02/03) correct | 0/3 | 1/3 | **8/18 attempts** (3+1+4), 0 fully-passing runs |
| RELATED_DISTINCT (TP-04/05/06/07/10) correct | 5/5 | 5/5 | **30/30 (100%)** — never wrong once, 60 total attempts across these 5 cases |
| UNRESOLVED (TP-08/09) correct | 2/2 | 0/2 | **0/11 completed attempts (0%)**, plus 1 runtime error |
| False merges of a RELATED_DISTINCT case | 0 | 0 | **0 / 30 attempts** |
| False merges of the UNRESOLVED TP-09 | n/a | n/a | **3 / 5 completed attempts** — see §5 |
| False splits (true=merged, actual=related_distinct) | 3 | 2 | **8 / 18 attempts** (TP-01 ×3, TP-02 ×5) |
| Runtime/parser errors | 0 | 0 | **3 / 60 attempts (5%)** — see §7a |

## 5. False merges — the unqualified "0" is wrong; here is the qualified version

**Zero false merges of any RELATED_DISTINCT ground-truth case, across all 30 attempts on
TP-04/05/06/07/10 and all 6 attempts on the RELATED_DISTINCT-only comparisons within
TP-01/TP-02.** That property held identically in the isolated run and holds identically
across every one of the six real-judge runs — it is the one genuinely robust, replicating
finding in this whole evaluation.

**But TP-09 — ground truth `unresolved` — was merged 3 times out of 5 completed production
attempts** (PROD-R4, PROD-R5, PROD-R6; see §7). That is a false merge in every meaningful
sense: the gate asserted `same_mechanism` / `merged` with reason "each repair removes the
other's failure" for a pair the frozen ground truth explicitly says the evidence does not
yet support a firm answer on. Stating "0 false merges" without this qualification, as the
original single-run write-up did, is misleading — it is true only for the RELATED_DISTINCT
class, and false, repeatedly, for the UNRESOLVED class. From here on this document always
distinguishes the two.

## 6. False splits

**Isolated: 3. PROD-R1: 2. Six-run aggregate: 8 attempts across TP-01 (3/6) and TP-02
(5/6).** TP-01 and TP-02 fail in every run of both the isolated and production sets, but
via different mechanisms each time (see §8/§9) — the specific reason changes, the outcome
mostly does not. TP-01's split rate (3/6) is close to a coin flip; TP-02's (5/6) is not —
TP-02 is the single most reliably-wrong SAME_MECHANISM case in the whole pack.

## 7. Unresolved mistakes

**Isolated: 0. PROD-R1: 2. Six-run aggregate: TP-08 wrong in 6/6, TP-09 wrong in 5/5
completed (plus 1 runtime error).** This is the most important new signal from the
production experiment. The evidence-floor safeguard
(`same_mechanism_gate.py::same_mechanism`, `confidence < 0.5 or evidence_count < 1`) only
works if the value it checks reflects real evidence sufficiency. Two independent problems
compound here, confirmed by reading the gate's own code (unmodified, read-only inspection
for this analysis):

1. **The floor checks the *judge's own self-reported profiling confidence*, not the
   original observation's declared `confidence`/`evidence_count`.** TP-09's two source
   reports both carry `evidence_count: 1, confidence: 0.6` in the frozen ground truth — by
   any reasonable reading, thin, single-source evidence. But `MechanismProfile.confidence`
   is `float(raw.get("confidence", 0.0))` from the judge's *profiling* response, a
   separate number the judge invents when asked to decompose the failure — not the
   original report's own confidence. Across every one of TP-09's 5 completed runs, the
   judge's self-reported profiling confidence came back ≥ 0.5, so the floor never fired
   once, regardless of how thin the underlying report actually was.
2. **The `evidence_count` axis of the same floor is close to a no-op for this data.**
   `min_evidence=1` and real single-observation anomalies almost always carry
   `evidence_count ≥ 1`, so `evidence_count < min_evidence` essentially never trips in
   practice — the floor's only live axis, for inputs like this test pack's, is the judge's
   own confidence self-report.

The isolated-subagent judge happened to rate itself low on these same two reports (0.1 and
0.35) and correctly triggered the floor both times. The real production judge did not
(0.75, and 0.92–0.95 in PROD-R1 alone) — it produced fluent, structured, plausible-sounding
mechanism profiles from thin single-anecdote reports and rated its own output confidently.
The gate's evidence threshold is only as good as the judge's self-calibration, and the real
judge is measurably less willing to say "I don't know" than the substitute was.

### 7a. Runtime/parser failures — kept separate from the semantic misses above

Three of the sixty attempts never reached a verdict at all: **PROD-R3/TP-09,
PROD-R5/TP-03, PROD-R6/TP-03**, each crashing with the identical error text
`could not convert string to float: 'high'`. None of these are counted as "wrong" anywhere
in §2–§6 — `aggregate_production_runs.py`'s `classify()` puts a crashed attempt in its own
`runtime_error` bucket, never merged into `correct`/`wrong`.

**Root cause, read directly from the unmodified gate source (no code was changed to make
this observation):** `profile_anomaly()` calls `float(raw.get("confidence", 0.0))` on the
judge's raw JSON response with no type check and no `try`/`except`. `PROFILE_PROMPT` asks
for `confidence` as a bare JSON key with no numeric-format instruction — unlike
`failure_class`, which is given an explicit closed enum in the same prompt. Nothing in the
prompt the gate sends ever tells the judge `confidence` must be a 0–1 float rather than a
category word. Three times out of sixty, the real judge reasonably answered with a
category word (`"high"`) instead, and the gate's own unvalidated `float()` call crashed.
This is a genuine boundary defect: the crash *site* is inside the gate, but the *trigger*
is an underspecified prompt contract the judge was never unambiguously told to honor. See
§11 for how this affects the overall classification.

## 8. TP-01 diagnostic — would it have reached the counterfactual test without the short-circuit?

**Directly answered by PROD-R1: yes, and it still fails there.** Both sides were
independently classified `absence` (0.95 / 0.92 confidence) — the short-circuit did *not*
fire (`short_circuited: false`), so the pair reached the real symmetric counterfactual test
exactly as the method intends. Both directions returned `removes_failure: false`. The
production judge's own stated reason: the engineer-side repair ("persistent shared
incident log... diagnostic actions and results") and the nurse-side repair ("explicit
agreement-state field... which care decisions have already been negotiated") are
"fundamentally different information types," rejecting the pair for tracking "diagnostic
actions" vs. "agreement states" as structurally distinct, even while conceding "both
involve handoff problems."

Across all six runs TP-01 never once short-circuits (`short_circuited: [False]×6`,
recomputed directly from the six JSON files) — it always reaches the counterfactual step,
and still only merges correctly 3 of 6 times. So for TP-01, removing the short-circuit
does not fix the false split — the counterfactual step itself, working as designed, is the
actual site of the instability, rejecting the merge on the specificity of how the repair
was worded in each case's own vocabulary about half the time.

## 9. TP-02 diagnostic — is the failed counterfactual caused primarily by carrier/domain-specific repair wording?

**Confirmed for the isolated run and for the runs where production reaches the
counterfactual step; but production reaches that step inconsistently, because its own
`failure_class` label for this pair is not stable across samples.** Recomputed directly
from all six files, TP-02's `short_circuited` flag is `[True, True, True, False, False,
True]` — 4 of 6 runs short-circuit on a `failure_class` disagreement, 2 reach the
counterfactual test. The specific disagreeing pair of classes is *not stable either*:
PROD-R1/R2 disagree as `capacity` vs `latency`; PROD-R3/R6 disagree as `absence` vs
`capacity`. In the isolated run, both sides agreed `capacity`/`capacity`, reached the
counterfactual step, and were rejected there on carrier-specific repair wording (rejecting
the aviation repair applied to the logistics failure because "the failure occurs upstream
of any shop-level inventory policy," and the reverse because these are "different
processes with different mechanisms").

TP-02 sits close enough to a genuine class boundary that its outcome depends on which
specific `failure_class` label a given judge sample happens to land on — sometimes that
disagreement alone decides the case before counterfactual reasoning is ever consulted,
sometimes the classes agree and the case is decided (also wrongly, in every observed
instance) by the same carrier-specific-wording pattern seen in the isolated run. This is
the clearest example of "taxonomy short-circuit instability" in the whole pack: not that
the short-circuit logic is wrong, but that the categorical judgment it depends on is not
reproducible run to run for a borderline pair.

## 10. TP-03 diagnostic

TP-03 is the cleanest natural experiment in this whole comparison. Isolated run:
independently classified `unverified` vs. `conflict` → short-circuited → false split.
PROD-R1: independently classified `unverified` vs. `unverified` (both sides) → *not*
short-circuited → reached the counterfactual test → both directions returned
`removes_failure: true` → correctly merged. Across all four *completed* production runs,
TP-03 merges correctly every time (`stable-correct-when-completed` in §2.1) — when the
gate reaches a verdict for this pair, that verdict is reliable. Its only real production
weakness is the two runtime crashes in §7a, both from the same underspecified-confidence
parser gap, unrelated to the merge decision itself.

This is direct, same-inputs evidence that when the taxonomy step agrees, the symmetric
counterfactual test the method actually relies on works as intended for TP-03 specifically
— the remaining instability for this case is a parsing/contract gap, not a decision-rule
gap.

## 11. Classification

### Verdict: **GATE_DEFECT** remains the primary finding, with an explicit, narrower **GATE/JUDGE CONTRACT DEFECT** carved out for the three runtime crashes only — the two are not the same claim and this document no longer collapses them.

**Why GATE_DEFECT for the semantic-accuracy findings (TP-01, TP-02, TP-08, and 2 of TP-09's
completed misses — 16 of the 19 wrong-but-completed attempts):**

- **Not JUDGE_ARTIFACT.** A judge-artifact theory predicts the defect disappears with a
  different judge. It doesn't: TP-01 and TP-02 fail in *both* the isolated substitute run
  and every one of the six real production runs. The specific proximate cause moves
  (short-circuit vs. counterfactual-literalism, and which class pair disagrees — see §8,
  §9), but the outcome, and the two underlying decision-rule mechanisms that produce it
  (taxonomy-boundary instability; counterfactual rejection triggered by carrier/domain-
  specific repair phrasing rather than the abstracted capability), reproduce under a real,
  well-resourced production judge across six independent samples, not just under one
  substitute.
- **Not MIXED.** MIXED would mean errors redistributing or disappearing with no new class
  of error introduced. TP-08/TP-09's evidence-floor bypass is a new failure mode absent
  from the isolated run, and it is not a one-off: TP-08 is wrong in 6/6 production
  attempts, and TP-09's false-merge specifically recurs in 3/5 completed attempts (60% of
  the times the gate reaches a verdict for that case at all) — the dominant behavior for
  that case under the real judge, not a fluke sample.
- **The floor-bypass traces to a real gate design choice, not only judge behavior.**
  §7 shows the evidence floor checks the judge's *self-reported profiling confidence*,
  never the original observation's own `confidence`/`evidence_count`, and that
  `evidence_count < min_evidence` is nearly unreachable for real single-observation
  anomalies. A better-calibrated judge happened to mask this gate-level design gap in the
  isolated run; the real judge did not. That the defect is judge-calibration-*sensitive*
  does not make it judge-*caused* — the gate chose to trust an unverified judge-supplied
  number instead of deriving the floor from the anomaly's own recorded evidence, and that
  choice is what actually failed.
- **The one clean positive — zero false merges of any RELATED_DISTINCT case — replicates
  identically across the isolated run and all six production runs (§5),** and should be
  read as a genuine, robust property of the decision rule's conservatism for that specific
  class. It does not extend to the UNRESOLVED class (§5's TP-09 qualification), and does
  not offset the recall and evidence-threshold findings above.

**Why GATE/JUDGE CONTRACT DEFECT, narrowly, for the 3 runtime crashes only:**

§7a's root cause — `PROFILE_PROMPT` never specifies that `confidence` must be numeric, and
`profile_anomaly()` never validates the type it receives before calling `float()` on it —
is a genuine boundary defect neither side owns outright: the crash *site* is gate code, the
crash *trigger* is a judge answer the gate's own prompt never ruled out. This is
structurally different from the TP-01/02/08/09 findings above, which involve zero parsing
ambiguity and zero crashes — they are pure decision-rule and floor-design behavior. Folding
the 3 runtime crashes into "GATE_DEFECT" without qualification would overstate how much of
the defect surface is decision-logic vs. an underspecified contract; folding the 16
semantic misses into "just a judge/contract problem" would understate a decision-rule
weakness that reproduces under two different judges with zero crashes involved. Both
descriptions are kept, scoped to what they actually explain.

## 12. Ground-truth risk

This entire evaluation rests on 10 synthetic, hand-labeled pairs, not on real, subsequently
resolved cases:

- **Only 10 pairs total** — every percentage in this document has a denominator small
  enough that one case flipping changes the headline number by 10 points (a single run) or
  can shift a per-case rate by 1/6 = 16.7 points.
- **Only 3 SAME_MECHANISM pairs** (TP-01/02/03) and **only 2 UNRESOLVED pairs**
  (TP-08/09) — the two classes this evaluation's most important findings (false-split rate,
  evidence-floor bypass) rest on are each represented by a two- or three-case sample. No
  claim in this document about "the" SAME_MECHANISM recall or "the" UNRESOLVED bypass rate
  should be read as a population estimate; they are exact counts over a very small labeled
  set.
- **No independent second annotator reviewed the ground truth.** All 10 expected
  verdicts/edges in `ground-truth.json` were authored and frozen by one process before any
  run. Nothing in this evaluation checks whether a second, independent reviewer would label
  every pair the same way.
- **TP-09 specifically deserves scrutiny on what its ground truth actually requires.**
  TP-09's `expected_edge: unresolved` implicitly encodes a stricter reading than "the two
  processes look similar" — its own failure-mode text for both sides states a proposed fix
  (walkthrough sign-off / signed checklist) "has not been tried yet and nobody has assessed
  whether" it would have prevented the incidents. Whether "the repair's effect must already
  be independently verified before a merge is permitted" is a requirement that belongs to
  the same-mechanism gate's own contract (`same_mechanism()`'s actual decision rule, which
  has no such check) or was added only through this evaluation's own label authoring is an
  open question this task does not resolve. **TP-09's ground truth is not changed by this
  update** — this section only marks the risk, as instructed, for a human reviewer to
  weigh when reading TP-09's 0/5 and 3/5-false-merge numbers above.

## 13. What this update closes, and what remains open

The original §12 of this document recommended running the production judge 4–5 more times
before drawing firmer conclusions. **That recommendation is now satisfied — PROD-R2..R6
are the requested runs, and §2 above is their distribution, not a proposal for one.** This
document no longer asks for more identical sampling runs.

What remains genuinely open, for a human reviewer, not for another same-shape run:

- The ground-truth risks in §12, particularly whether TP-09's implicit
  "repair-must-already-be-verified" bar belongs in the gate's own contract.
- Whether `PROFILE_PROMPT` should ever specify a numeric format for `confidence` — this
  document deliberately does not propose that change; `same_mechanism_gate.py` is
  unmodified, and any change to it is out of scope for an evaluation task.
- Whether the evidence floor should be derived from the anomaly's own recorded
  `confidence`/`evidence_count` rather than the judge's self-reported profiling
  confidence — again, an observation this document makes, not a change it makes.
