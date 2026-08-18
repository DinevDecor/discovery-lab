# Contract — Prospective Ground-Truth Stream v0.1 (`prospective-ground-truth/`)

Core Principle: **Freeze the claim and the evidence before reality answers it. Record
the answer, from reality, later - append-only, never touching the freeze.**

This is a **tool contract**, matching the precedent of `constraint-change-
observatory/CONTRACT.md` and `adversarial-review-kernel/CONTRACT.md` — not a
governance/Employee Role contract.

## Origin

Direct response to the Ground-Truth Ablation & Kill Test's own verdict
(`experiments/ground-truth-kill-test-001/`): 0 valid / 13 excluded, `INSUFFICIENT
DATA`. That experiment could not run because the repository contained no real,
externally-resolved, contamination-free T0→T1 cases. This package is the smallest
possible fix for the *cause*, not a rerun of the experiment: a protocol for
registering real prospective cases now, so a future kill test has genuine ground
truth to score against, months from now, once reality has actually answered them.

## Scope of authority

`src/prospective_ground_truth/{models,identity,packet,validator,ledger}.py` have
**zero import dependency on `ca_agents`, `case_claim_kernel`, `gpt_mechanism_judge`,
`blind_analysis_kernel`, `adversarial_review_kernel`, `business_candidate_analyst`,
`calendar_arbitrage_watch`, `constraint_change_observatory`, `x_signal_probe`, or
`capability_observatory`** — enforced by `tests/test_safety.py`. This package is a
wholly separate evidence stream, the same boundary
`constraint-change-observatory/CONTRACT.md` draws for itself. A case's
`source_case_id` may reference an existing CA anomaly, BCA candidate, or any other
identifier by string alone — this package never reads, imports, or depends on the
system that produced it.

`run_prospective_ground_truth.py`'s three subcommands (`register`, `resolve`,
`report`) are the only entry points. `register` and `resolve` write only to this
package's own `data/{cases.jsonl,resolutions.jsonl,cases.json}` (append-only via
`ledger.py`, never hand-edited, never read-modify-written for the two `.jsonl`
files). `report` is read-only.

## Hard boundary — this tool MUST NOT

- call a language model, or any network endpoint. No module imports a model client,
  `requests`, or `urllib.request` — enforced by `tests/test_safety.py`. Task §8:
  "Models are never resolution evidence." A human may use a model to help *find* a
  resolution source, but that fact about how the human worked is outside this tool's
  own boundary, exactly as `constraint-change-observatory/CONTRACT.md`'s `analyst`
  field precedent already establishes — this code itself never calls one.
- run unattended. No scheduler, cron entry, or GitHub Actions workflow calls this
  package — checked in `tests/test_safety.py` against the real repo-wide
  `.github/workflows/` directory. Task §9/§17: intake stays manual.
- mutate a case's frozen T0 content, ever, for any reason. `CaseLedger.append()` is
  the only path that can write a `ProspectiveCase`, it opens `data/cases.jsonl` only
  in append mode, and `ResolutionLedger` — the only thing that runs later — is a
  structurally separate file with no read or write path into `data/cases.jsonl` at
  all (`tests/test_ledger.py::T0NeverMutatedByResolutionTests`).
- let post-T0 evidence enter a frozen packet. `validator.py` rejects any
  `T0EvidenceItem` whose `captured_at` is after the case's own `t0_cutoff`, and
  independently recomputes `t0.packet_sha256` from `t0.t0_cutoff` + `t0.evidence` and
  rejects the case if the stored hash disagrees — internal consistency is checked,
  not assumed.
- let a case be registered without all three resolution criteria
  (`positive_condition`/`negative_condition`/`ambiguous_condition`) already stated.
  `validator.py` rejects a case with any of the three blank — criteria cannot be
  written after the outcome because there is no code path that lets a case exist
  without them in the first place.
- let `Resolution.outcome ∈ {POSITIVE, NEGATIVE, AMBIGUOUS}` be recorded without real
  T1 evidence and a named authoritative source type. `EXPIRED_UNRESOLVED` and
  `INVALIDATED` are exempt (they assert an absence or a defect, not a claim about
  reality) but still require a `resolution_rationale` — task §7: "Never force
  POSITIVE/NEGATIVE."
- let `resolver_type` be a bare model call. `RESOLVER_TYPES` contains only `human`
  and `model_assisted_human_confirmed` — there is no plain `"model"` value anywhere
  in the schema for a resolution to claim.
- collapse `AMBIGUOUS` or `EXPIRED_UNRESOLVED` toward `NEGATIVE`, or compute any
  aggregate accuracy/reliability/weight from `Resolution` data. Task §15: "no
  premature calibration" — there is no scoring or weighting logic anywhere in this
  package for such a coercion to even occur in (`tests/test_safety.py
  ::NoCalibrationOrScoringLogicTests`).
- resolve a case that was never registered. `run_prospective_ground_truth.py resolve`
  checks `CaseLedger.has(prospective_case_id)` before ever constructing a `Resolution`
  and refuses (`SystemExit`, nothing written) if the case is unknown.
- write to any CA/BCA/Calendar-Arbitrage/X-Signal-Probe/Capability-Observatory/
  Constraint-Change-Observatory/kernel data path, or reference one as a default
  ledger location — checked against the literal path markers in
  `tests/test_safety.py::NeverWritesToProductionDataTests`.

## Rights

- The right to a case that stays `OPEN`/`AWAITING_OUTCOME` indefinitely if reality
  simply hasn't answered yet. Not every registered case needs a same-day, or even
  same-quarter, `Resolution`.
- The right to record `EXPIRED_UNRESOLVED` — a window closing with no authoritative
  answer is itself informative, not a failure to paper over with a forced guess.
- The right to record `INVALIDATED` — a case later found to have been malformed at
  registration (contaminated T0 evidence, a proposition that was never actually
  falsifiable) is recorded as such, not silently deleted or quietly re-registered.

## Responsibilities

- Report the exact `t0_packet_sha256` a case was frozen against, independently
  recomputable from the case's own stored `t0.evidence`, so "this evidence is exactly
  what was frozen at T0" is verifiable from the record alone, not merely asserted.
- Keep every evidence item's own `captured_at` honest — the date discipline that
  makes "no post-T0 evidence" a checked property rather than a promise.
- Prefer real primary sources (regulator, tender authority, court, exchange, company
  filing) over secondary news for `authoritative_source_type` wherever one is
  reasonably available — task §8.

## Executor independence

This contract binds the tool, not whoever runs it — same precedent as
`observation-agent/CONTRACT.md`.

## Revocation and change

This tool may be modified, extended, or retired at any time by direct repository
change. A change that would let a model resolve a case on its own, schedule intake
automatically, compute model reliability/calibration from `Resolution` data, or wire
this package's cases into a Stage 5 router or Trust Engine is out of scope for this
contract entirely and needs a new, explicit human decision.
