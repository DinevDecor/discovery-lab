# C3 External Capture Executor (Slice 03)

Implements `docs/architecture/reality-observatory-slice-03-executor-design.md`,
Section 13's "Minimum Slice 03": one external executor, one submission
envelope, one delivery mechanism, one executor health report.

**Job: FETCH only.** This package visits providers, preserves raw evidence,
and packages a valid submission for the existing C3 intake path. It never
analyzes prices, detects trends, creates Findings, decides identity
continuity, calls Constraint Archaeology, or infers business opportunities.
It never writes to `capability-observatory/data/*.jsonl` directly — every
capture flows through the existing, unmodified
`capability-observatory/run_capability_observatory.py process`.

## Why this is a separate package from `capability-observatory/`

`capability-observatory/tests/test_safety.py` forbids any network client
inside `capability-observatory/src/capability_observatory/`, by design, so
that package can stay easy to reason about as pure validate-and-record
logic (see its own README's "No unattended fetching"). This package is
where network calls are *supposed* to live instead — it imports
`capability_observatory` as a library (for the shared outcome vocabulary
and, in tests, for round-tripping through the real validator), but nothing
in `capability_observatory/` imports this package or knows it exists.

## Provider strategy

| Provider | Method | Why |
|---|---|---|
| DigiKey | Official API | Confirmed public self-serve developer portal, real-time pricing/availability |
| Mouser | Official API | Confirmed public, free, self-serve Search API; most complete single-call schema of the five |
| AutomationDirect | HTML, gated by a probe | No confirmed API; a real but unverified signal exists. `automationdirect.probe()` checks robots.txt + reachability before any capture is attempted; if the probe fails, it's treated as `HUMAN_FALLBACK` for that run |
| McMaster-Carr | Human fallback | API exists but is enterprise/EDI-only, not public self-serve |
| Grainger | Human fallback | No public self-serve API found; only enterprise punchout/EDI |

Full rationale: `config/provider_strategy.json` and the design doc's
Section 4. **Schema caveat:** the DigiKey/Mouser response field mappings in
`digikey.py` / `mouser.py` are a best-effort match to each vendor's
publicly documented field categories, not an independently fetched schema
document — this session's network egress was blocked from
`developer.digikey.com` and `mouser.com/api-hub` the same way it was
blocked from the five provider domains themselves. Verify against a live
sandbox app's actual response before trusting this for a real weekly run.

## Running

```
python3 run_executor.py run
```

Reads `capability-observatory/config/panel.json`, attempts every active
panel item via its assigned method, writes one submission file per
attempted item into `capability-observatory/incoming/` (named
`exec-<date>-<panel_item_id>.json`), then calls
`python3 run_capability_observatory.py process` from
`capability-observatory/` — unmodified, exactly as the existing
`capability-observatory.yml` workflow already does — to validate, record,
and render C3's own report. Finally writes
`reports/latest-executor-health.json` and
`reports/executor-health-<date>.md` here.

McMaster-Carr and Grainger items are never attempted by this command — no
submission file is written for them, since a Capture record for a fetch
that was never even tried would misrepresent what happened. They show up
in the health report as `human_fallback_required` with no C3 record until
a human actually performs the capture (see below).

## Human fallback

`human_fallback.HUMAN_SUBMISSION_TEMPLATE` is the fixed shape a person
fills in — exact URL, exact timestamp, a raw-evidence reference
(screenshot or view-source save kept alongside the submission), price/
stock/lead-time exactly as observed, and `executor: "human:<name>"`. See
the design doc's Section 10 for the full discipline (no retrospective
reconstruction, no rounding/reconciling against last week's number).
`human_fallback.parse_human_submission()` turns a filled-in template into
the identical `ExecutorSubmission` the automated paths produce; from there
it goes through the same `to_c3_submission()` → `incoming/` → `process`
path as everything else. There is no separate human-evidence ledger.

## Panel pinning

All 20 panel items currently have `source_url_pinned: false`
(`capability-observatory/config/panel.json`) — confirmed directly, not
assumed, during the Slice 03 design review. This executor never fabricates
a plausible-looking product URL to make automation look like it's working:

- **AutomationDirect items** that aren't yet pinned get a real reachability
  probe (proving the domain/robots.txt genuinely allow the fetch) but no
  price/stock extraction attempt — there is no product-specific page to
  parse yet, and the submission says so honestly
  (`error_category=panel_item_not_pinned_to_product_page`).
- **DigiKey/Mouser items** search by the panel item's own existing
  `label`/category text (never a fabricated part number); a real result
  becomes genuine capture evidence.
- **Pinning itself is never automatic.** `panel_pinning.propose_pin()` /
  `apply_pin_proposal()` is the one function allowed to write a pin, and it
  refuses to run unless given a `panel_version` that actually differs from
  the panel's current one — see that module's docstring. This executor's
  `cli.py` does not call it; a successful capture is a proposal for a human
  to review and apply as its own explicit, versioned panel commit, not
  something this package does silently on your behalf.

## Failure semantics

See `docs/decisions/003-c3-capture-outcome-vocabulary-extended.md` for the
full decision record. In short: `capability_observatory.models
.CAPTURE_OUTCOMES` grew five new values so that "the executor's own network
failed" (`executor_network_blocked`) is never conflated with "the provider
denied us" (`provider_access_blocked`) again, the way both were folded into
one ambiguous `access_blocked` value in the first 20 real captures (week of
2026-08-09). `outcomes.py` groups the vocabulary for this package's own
routing/reporting use; it never redefines it.

## Tests

`python3 -m unittest discover -s tests -v` from this directory. Fully
offline and deterministic — every network-touching function
(`digikey.run`, `mouser.run`, `automationdirect.probe`/`run`) takes a
`transport` parameter, and tests pass `transport.FakeTransport` (see
`tests/test_safety.py` for the check that enforces this).
