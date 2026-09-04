# 003 — C3 capture-outcome vocabulary extended to separate executor failure from provider denial

**Status:** adopted, implemented in `capability-observatory/` (Slice 03,
external capture executor).

## Decision

`capability_observatory.models.CAPTURE_OUTCOMES` is extended, additively,
from five values to ten:

```
ok, unavailable, access_blocked, parse_error, source_missing,   # unchanged
provider_access_blocked, executor_network_blocked, timeout,      # new
credentials_error, api_quota_error                                # new
```

`access_blocked` is kept, unchanged in meaning, permanently — it is not
deprecated in the sense of being removed or rejected by `validate_submission`;
it remains a fully valid `capture_outcome` forever, because
`capability-observatory/data/captures.jsonl` and
`capability-observatory/incoming/processed/*.json` are append-only and are
never rewritten (see `CLAUDE.md`: "A newer result is a NEW record, never an
edit"). The first 20 real captures — `week-2026-08-09-C3-001.json` through
`-020.json` — are recorded under `access_blocked` and stay that way
permanently. New submissions should prefer the five specific new values
instead of `access_blocked` going forward; `access_blocked` is not removed
from `CAPTURE_OUTCOMES` because doing so would make those 20 historical
records fail re-validation against the current schema, which is exactly the
kind of retroactive rewrite this project's append-only discipline forbids.

`OBSERVATION_PRODUCING_OUTCOMES` is unchanged: `("ok", "unavailable")`. None
of the five new values, nor `access_blocked`, may ever produce an
Observation. `metrics.py`'s stop-rule thresholds
(`MIN_OBSERVABILITY_COUNT`, `MIN_CAPTURE_SUCCESS_RATE`, `MAX_IDENTITY_BACKLOG`)
are untouched; `capture_success()` and `observability()` are shape-based
(they check `capture_outcome == "ok"` / whether any Observation exists),
not exhaustive-enumeration-based, so they compute correctly against the
wider vocabulary with no code change.

## Reason

The 20 real captures from the week of 2026-08-09 are all recorded with
`capture_outcome: "access_blocked"`. Reading `capture_intake.py:14-32` and
the actual `week-2026-08-09-C3-001.json` submission, what happened was: the
capturing session's own network egress policy refused the connection to
`www.automationdirect.com` *before the request reached the provider at
all* — confirmed independently during the Slice 03 design review, which
reproduced the identical block from a separate execution session against
all five provider domains. That is an **executor-side** infrastructure
failure. `access_blocked`, as originally defined, does not distinguish that
from a **provider-side** denial (a CAPTCHA page, a WAF challenge, an
explicit 403). The only thing keeping the two apart in the real incident
was a hand-written sentence in the submission's `notes` field: *"This is
NOT a vendor bot-detection event."* That is a convention, not a structural
guarantee — the schema itself could not tell the difference, and
`metrics.py::evaluate_stop_rules`'s `Rule A` (capture mechanism failing)
fired on numbers that read identically whether the cause was "the network
path is broken" (cheap to fix, orthogonal to the domain) or "these five
providers cannot be captured" (expensive, a real domain-feasibility
question). Conflating those under one value makes the stop-rule signal
strictly less informative than it should be.

## Alternative rejected

**Rewriting the 20 existing `access_blocked` records to the new, more
specific values** was considered and rejected outright. Even though the
correct reclassification is knowable today (all 20 were
`executor_network_blocked`, not `provider_access_blocked` — the `notes`
field already says as much), rewriting them would mean a Capture record's
`capture_outcome` is no longer a fixed statement of what was recorded at
the time, but a value that can be "corrected" after the fact — exactly the
property `CLAUDE.md`'s append-only rule exists to prevent ("A retroactively
generated Finding is not equivalent to one recorded at the time. That
distinction is the whole point," applied here to Captures). A human or
future analyst reading `captures.jsonl` must always be able to trust that a
record reflects what the system actually believed at `recorded_at`, not
what it was later realized to mean.

## Consequence

Reading any `access_blocked` record older than this decision requires an
extra step: check its `notes` field for which situation actually applied,
rather than trusting the outcome value alone to carry that distinction —
this is documented in `capability-observatory/README.md`'s outcome-
vocabulary section. Going forward, new submissions carry the distinction
structurally, and `Rule A` firing on post-Slice-03 evidence is a stronger
signal than it was before: it is far less likely to be a same-domain
"the network path we used doesn't work" problem hiding as a "the providers
can't be captured" problem, provided submitters use the specific new values
instead of falling back to `access_blocked` out of habit.
