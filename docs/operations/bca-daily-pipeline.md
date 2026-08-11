# Business Candidate Analyst — daily pipeline operating contract

Status: production-enabled. Read this before changing anything about how
or when Business Candidate Analyst runs.

## What the system is

**The system is not a business idea generator. It is an evidence
accumulation and candidate escalation system.**

It does not invent opportunities. It reads what Constraint Archaeology has
already observed, groups observations that are evidenced to be the same
missing product function, tracks that grouping's identity across days,
and escalates a human's attention only when the accumulated evidence
crosses a meaningful lifecycle boundary. Everything else — every WATCH
candidate created, every observation absorbed into an existing candidate,
every day nothing material happens — is silent by design and stays that
way in the append-only record for anyone who wants to look.

## Daily order

```
Constraint Archaeology daily scan
  -> persist CA observations / anomalies / report
  -> (only if CA succeeded) Business Candidate Analyst
  -> persist candidate registry / events / report
  -> material-event extraction (read-only over this run's own new events)
```

Enforced by `run_daily_pipeline.py` at the repo root: it runs the CA scan
as a subprocess and inspects its exit code before deciding whether to run
BCA at all. A failed CA scan means BCA does not run that day — there is
no partial-evidence mode. `run_pipeline()` (the same function, importable)
is the tested seam; the tests substitute deterministic stand-ins for the
real CA subprocess so they stay offline and fast, without weakening what
the real orchestration does.

## Silence is the default

WATCH candidate creation and same-state evidence accumulation
(`evidence_reassessed` events where the state doesn't change) are the
normal, expected shape of most days and produce **zero** material events.
A day with zero material events is not a day where nothing happened — CA
still scanned, BCA still processed every anomaly, candidates still
accumulated evidence — it is a day where nothing yet warrants a human
decision.

## What is material (and gets surfaced)

Exactly six categories, implemented in
`business_candidate_analyst/material_events.py::detect_material_events`
(categories 1-5) and `run_daily_pipeline.py` (category 6):

1. WATCH -> VALIDATING
2. VALIDATING -> INVESTIGATE
3. INVESTIGATE -> PROMISING
4. any transition to REJECTED **from VALIDATING or higher** (REJECTED
   directly from WATCH never earned attention in the first place, and
   stays silent)
5. a candidate merge whose target candidate's lifecycle state also
   changed in the same run (a merge that leaves state unchanged — the
   common case — is not material)
6. a pipeline failure at either stage (CA or BCA)

Nothing else is material. In particular: ordinary `candidate_created`
events, `evidence_reassessed` events with no state change, and merges
that don't move lifecycle state are never surfaced.

## Where the record lives

This repository has no notification-delivery integration today (no
Slack/email/pager hook), so this pipeline does not invent one. It
persists two machine-readable artifacts every run, for whatever system
eventually reads them:

- `reports/pipeline-status-<date>.json` — this run's CA/BCA outcome
  (`OK` / `CA_FAILED` / `BCA_FAILED`), including exit codes and
  stdout/stderr tails from each stage. A non-zero process exit code
  (from `run_daily_pipeline.py` itself) is the failure signal any
  wrapping scheduler already understands — this is category 6.
- `business-candidate-analyst/reports/material-events-<date>.json` —
  written by BCA itself at the end of its own run, listing only
  categories 1-5 from *this run's* freshly-appended events. An empty
  list is the expected, common case.

Both are overwritten (not appended) per calendar date, so re-running the
same day's corpus never accumulates duplicate artifacts — matching the
append-only *event log*'s own idempotency (a rerun over unchanged
evidence appends zero new events; see `test_daily_pipeline.py` and each
package's own idempotency tests).

## What must never change without deliberate review

- CA thresholds, BCA lifecycle thresholds, taxonomy, and `signature.py`'s
  semantics are independent of this pipeline wiring and must stay that
  way — the orchestrator only sequences and gates two existing tools; it
  does not adjust what either one decides.
- Constraint Change Observatory is a separate evidence stream, untouched
  by this pipeline.
- `candidate_events.jsonl` remains the only authoritative record. Both
  artifacts above are downstream, disposable summaries — safe to delete
  and regenerate from the event log at any time; never a second source
  of truth.
