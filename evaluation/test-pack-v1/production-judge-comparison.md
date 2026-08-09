# Test Pack v1 — Production Judge Validation

Follow-up to the isolated-subagent run (`ground-truth.json` / `results.json` / `report.md`).
Purpose: isolate whether the split bias observed there belongs to (A) the gate's decision
rule, or (B) the judge substitution used because the interactive session had no
`ANTHROPIC_API_KEY`. Runs the **exact same 10 frozen pairs** from `ground-truth.json`
through the real production judge. Gate code (`same_mechanism_gate.py`), taxonomy,
short-circuit logic, and thresholds are **unmodified** — same as the first run.

## 1. Was the real production judge actually used?

**Yes.** `evaluation/test-pack-v1/run_test_pack_production.py` imports
`ca_agents.mechanism_judge.ClaudeMechanismJudge` unmodified and calls the real
`profile_anomaly()` / `same_mechanism()` from `same_mechanism_gate.py`, executed inside
GitHub Actions run [31300689766](https://github.com/DinevDecor/discovery-lab/actions/runs/31300689766)
(workflow `test-pack-v1-production-judge.yml`, triggered by the deliberate commit `d4bd4a6`
on this branch), using the repository's existing `ANTHROPIC_API_KEY` secret — the same
secret the daily pipeline already uses successfully. All 10 cases completed with no
errors (`run_metadata.errors: []` in `results-production-judge.json`).

## 2. Model / provider

From `results-production-judge.json.run_metadata`:

| Field | Value |
|---|---|
| Provider | Anthropic |
| API endpoint | `https://api.anthropic.com/v1/messages` |
| API version header | `2023-06-01` |
| Model | `claude-sonnet-4-5` (module default; no `ANTHROPIC_MODEL` override was set) |
| Judge class | `ca_agents.mechanism_judge.ClaudeMechanismJudge` (production, unmodified) |

## 3. 10/10 result table — isolated vs. production

| ID | expected edge | isolated actual | production actual | isolated result | production result |
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

**Overall: isolated 7/10, production 6/10.** One case flipped from wrong to right (TP-03);
two flipped from right to wrong (TP-08, TP-09) — a new failure mode, not present in the
isolated run.

### Failure location — isolated vs. production

| ID | isolated failure location | production failure location |
|---|---|---|
| TP-01 | `failure_classification` (short-circuited: corruption vs absence) | `counterfactual reasoning` (classes agreed on `absence`/`absence`, reached counterfactual, both directions rejected on literal repair wording) |
| TP-02 | `counterfactual reasoning` (classes agreed on `capacity`/`capacity`, counterfactual rejected on carrier-specific wording) | `failure_classification` (short-circuited: **capacity vs latency** — a *different* class disagreement than the isolated run) |
| TP-03 | `failure_classification` (short-circuited: unverified vs conflict) | *(none — correct)* classes agreed on `unverified`/`unverified`, counterfactual passed both directions |
| TP-08 | *(none — correct)* left profiled at confidence 0.1, correctly triggered evidence floor | `evidence_threshold` (left profiled at confidence **0.75** despite being the same maximally vague single-anecdote report; floor never triggered) |
| TP-09 | *(none — correct)* right profiled at confidence 0.35, correctly triggered evidence floor | `evidence_threshold` (both profiled at confidence **0.92–0.95**; floor never triggered, and the counterfactual explicitly reasoned through the "belief may have been wrong" ambiguity anyway and still returned a confident false) |

## 4. Metrics

| Metric | Isolated | Production |
|---|---|---|
| Overall accuracy | 7/10 (70%) | 6/10 (60%) |
| SAME_MECHANISM recall | 0/3 (0%) | 1/3 (33.3%) |
| SAME_MECHANISM precision | N/A (0 predicted) | 1/1 (100%) |
| RELATED_DISTINCT recall | 5/5 (100%) | 5/5 (100%) |
| RELATED_DISTINCT precision | 5/8 (62.5%) | 5/9 (55.6%) |
| UNRESOLVED recall | 2/2 (100%) | 0/2 (0%) |
| UNRESOLVED precision | 2/2 (100%) | N/A (0 predicted) |
| False merges | **0** | **0** |
| False splits (true=merged, actual≠merged) | 3 (TP-01,02,03) | 2 (TP-01,02) |
| Incorrectly resolved uncertainty (true=unresolved, actual=confident) | 0 | **2 (TP-08,09)** |
| Cross-domain accuracy | 6/9 (66.7%) | 5/9 (55.6%) |
| Cross-domain SAME_MECHANISM recall | 0/3 (0%) | 1/3 (33.3%) |

## 5. False merges

**0 in both runs.** The dangerous error did not occur with either judge implementation.
This is the one property that replicates cleanly and should be trusted more than any
single-run number here, precisely because it held under two different judges.

## 6. False splits

**Isolated: 3. Production: 2** (TP-03 now correctly merges). TP-01 and TP-02 fail in
**both** runs, but via different mechanisms each time (see §3 and §8/§9/§10 below) — the
specific reason changes, the outcome does not.

## 7. Unresolved mistakes

**Isolated: 0. Production: 2 (TP-08, TP-09).** This is the most important new signal from
this experiment. The evidence-floor safeguard (`confidence < 0.5` in
`same_mechanism_gate.py::same_mechanism`) only works if the judge honestly rates its own
confidence low on thin input. The isolated-subagent judge did so (0.1 and 0.35 on the
exact same two reports). The real production judge did not (0.75 and 0.92–0.95 on the
*same* reports) — it produced fluent, structured, plausible-sounding mechanism profiles
from a single vague anecdote (TP-08-L: "things reportedly get lost sometimes", no channel,
no artifact, no timing) and from single-incident reports whose own text states the
proposed fix's effect was never checked (TP-09). The gate's evidence threshold is only as
good as the judge's calibration, and the real judge is measurably less willing to say "I
don't know" than the substitute was.

## 8. TP-01 diagnostic — would it have reached the counterfactual test without the short-circuit?

**Directly answered by this run: yes, and it still fails there.** In production, both
sides were independently classified `absence` (0.95 / 0.92 confidence) — the short-circuit
did *not* fire (`short_circuited: false`), so the pair reached the real symmetric
counterfactual test exactly as the method intends. Both directions returned
`removes_failure: false`. The production judge's own stated reason: the engineer-side
repair ("persistent shared incident log... diagnostic actions and results") and the
nurse-side repair ("explicit agreement-state field... which care decisions have already
been negotiated") are "fundamentally different information types," and the check
explicitly rejects the pair for tracking "diagnostic actions" vs. "agreement states" as
structurally distinct, even while conceding "both involve handoff problems."

So for TP-01, removing the short-circuit does not fix the false split — the counterfactual
step itself, working as designed, rejects the merge on the specificity of how the repair
was worded in each case's own vocabulary. The short-circuit was the isolated run's proximate
cause; it is not TP-01's root cause.

## 9. TP-02 diagnostic — is the failed counterfactual caused primarily by carrier/domain-specific repair wording?

**Confirmed for the isolated run; not directly testable from production, because
production never reached the counterfactual step for this pair.** In the isolated run the
two counterfactual reasons say so explicitly: rejecting the aviation repair applied to the
logistics failure because "the failure occurs upstream of any shop-level inventory
policy... a different process," and rejecting the reverse because "these are different
processes with different mechanisms (retail store replenishment vs. carrier-held MRO spare
stocking)." Both rejections turn on the repair sentence naming the originating carrier
("the shop's own held stock," "replenishment order quantity calculation") rather than the
abstracted capability (size stock to demand variance, not the mean) both sides' own
`hidden_function` fields already agreed described the same thing.

In production, TP-02 was independently classified `capacity` (left) vs. `latency`
(right) — a *different* class disagreement than the isolated run's `capacity`/`capacity`
agreement — so it short-circuited before any counterfactual test ran, and this specific
hypothesis could not be exercised again. That two different judge instances found two
different, independent reasons to reject the same merge (one at classification, one at
counterfactual) is itself informative: TP-02 sits close enough to a genuine class boundary
that its outcome is sensitive to which specific labels a given judge run happens to land
on, not just to one deterministic defect.

## 10. TP-03 diagnostic

Not explicitly requested as a numbered diagnostic but directly relevant to the A/B
question: TP-03 is the cleanest natural experiment in this whole comparison. Isolated run:
independently classified `unverified` vs. `conflict` → short-circuited → false split.
Production run: independently classified `unverified` vs. `unverified` (both sides) → *not*
short-circuited → reached the counterfactual test → both directions returned
`removes_failure: true` ("directly addresses the failure mechanism... would be blocked by
an independent verification checkpoint") → correctly merged.

This is direct, same-inputs evidence that when the taxonomy step agrees, the symmetric
counterfactual test the method actually relies on works as intended — it isn't the
counterfactual logic itself that's broken for TP-03, it's classification-boundary
instability (two reasonable judges, two different fine-grained labels for what is
otherwise the same profiled failure) that decides the outcome before the more diagnostic
step is ever consulted.

## 11. Classification

### **GATE_DEFECT**

Reasoning, weighed against the four options as specified:

- **Not JUDGE_ARTIFACT.** The production judge did not "materially fix" SAME_MECHANISM
  recall — it went from 0/3 to 1/3, still a majority-wrong result on the one class the
  gate exists to detect. Overall accuracy did not improve (6/10 vs. 7/10); it declined.
  And the production judge introduced a new, real failure mode (2 incorrectly-resolved
  UNRESOLVED cases) that the isolated substitute did not have.
- **The core structural weaknesses reproduce, redistributed.** Two of three same-mechanism
  false splits (TP-01, TP-02) fail in *both* runs. The specific proximate cause moves
  between runs (short-circuit vs. counterfactual-literalism, and which class pair
  disagrees), but the outcome — and the two underlying mechanisms that can produce it
  (taxonomy-boundary instability; counterfactual rejection triggered by carrier-specific
  repair phrasing rather than abstracted capability) — are present with the real judge,
  not artifacts of the substitute.
- **Evidence-threshold reliance on judge self-calibration is exposed as fragile,
  specifically by the production run.** This is a gate-level design property (the floor
  check trusts the judge's own `confidence` field with no independent check) that a
  better-calibrated substitute judge happened to mask and the real judge did not.
- **The one clean positive — zero false merges — replicates identically in both runs**,
  and should be read as a genuine, robust property of the decision rule's conservatism
  (an AND across two symmetric conditions structurally cannot produce a false merge from
  either failure mode alone). That is evidence *for* one part of the gate working as
  designed, but it does not offset the recall and evidence-threshold findings above.

This is not a clean MIXED verdict either, because MIXED as specified implies some errors
disappearing while structural ones remain with no new errors introduced; here a new,
distinct error class appeared. The overall picture is a gate whose short-circuit and
counterfactual steps are both sensitive to phrasing/classification variance in ways that
persist under the real model, plus an evidence-threshold safeguard that depends on judge
honesty it did not get in this run.

## 12. Recommendation for the next experiment

Not a request to change the gate.

The two runs used **independent sets of profile/counterfactual calls** (20 fresh isolated
subagent calls, 20+ fresh production API calls) — none of the observed differences can yet
be separated from ordinary sampling variance in a single non-deterministic LLM call. Before
drawing firmer conclusions about TP-01/TP-02 specifically, or about how often TP-08/TP-09
land on the safe UNRESOLVED side versus not:

**Run the production `ClaudeMechanismJudge` on the same 10 frozen pairs 4–5 more times
(fresh `profile()`/`counterfactual()` calls each time, same unmodified gate code, same
ground truth) and look at the *distribution* of verdicts per case, not a single point
estimate.** This would answer three things this single run cannot: (1) whether TP-03's
merge is stable or was itself a lucky classification roll like TP-01/TP-02's instability
suggests; (2) whether TP-08/TP-09's overconfidence is systematic or one unlucky sample;
(3) an empirical rate for how often the taxonomy short-circuit changes which specific class
pair a given borderline case lands on. That distribution, not one more single run, is the
smallest experiment that would let a MIXED/GATE_DEFECT call be made with real confidence
rather than off two single-sample runs.
