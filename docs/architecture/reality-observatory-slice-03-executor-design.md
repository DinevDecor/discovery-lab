# Reality Observatory — Slice 03: External Capture Executor for C3

**Type:** design document. No implementation, no code, no workflow changes.
**Status:** proposal, pending review. Nothing in this document has been built.
**Do not touch:** Constraint Archaeology v0.5, the same-mechanism gate, the Test Pack,
`capability-observatory/src/capability_observatory/`, `capability-observatory/data/*.jsonl`,
the 20-item panel's identity, the stop-rule thresholds, `.github/workflows/*.yml`.

---

## 0. What actually happened, precisely

Read from the repo, not summarized secondhand:

- `capability-observatory/incoming/processed/week-2026-08-09-C3-001.json` (and the other 19
  files in that directory) each record `capture_outcome: "access_blocked"`, with
  `executor: "ai:claude-code-web-session-01Rj4BPwXrprhL4qiWbAZKMG"` and a `raw_content` field
  that is not page content at all — it's a synthesized error narrative:
  > *"HTTPS fetch to www.automationdirect.com refused by the executing session's own network
  > egress policy (WebFetch tool error_type=EGRESS_BLOCKED...). No content was returned by
  > www.automationdirect.com itself — the block occurred before the request reached the
  > provider."*
- The submission's own `notes` field says as much explicitly: *"This is NOT a vendor
  bot-detection event."*
- `reports/latest-summary.json` and `metrics.py::evaluate_stop_rules` correctly computed
  `rule_a_capture_mechanism_failing: true` → `kill_or_redesign: true`. The stop rule fired
  correctly on the numbers it was given. It has no way to know *why* capture failed — that
  distinction lived only in a human-readable `notes` string, not in the schema.
- **I independently reproduced the identical failure in this session.** Attempting
  `WebFetch` against `www.automationdirect.com`, `www.grainger.com`, `www.mcmaster.com`,
  `www.digikey.com`, and `www.mouser.com` from *this* design-only session returned
  `EGRESS_BLOCKED` for all five, with the same error shape. This session runs in a
  different execution context (Claude Code Remote, not the original web session), which
  means the block is not an artifact of one session's config — it is a property of running
  fetches from *any* Claude-hosted execution surface against these five domains. That is
  the load-bearing fact behind this whole design: **no architecture that executes inside an
  Anthropic-hosted AI session can be the primary Slice 03 executor**, independent of how
  good the fetch code is.

This reframes the problem correctly, matching the task's own framing: this is a capture
*executor* failure — a network-path problem — not evidence that these five domains are
unreachable to ordinary internet clients, and not evidence about the domain (industrial
component pricing) being unobservable.

---

## 1. Current C3 ingestion contract (from code, not assumption)

### Submission envelope (what an executor must produce)

One JSON file per panel item per attempt, dropped into `capability-observatory/incoming/`.
Shape defined by `capture_intake.py`'s module docstring and enforced by
`validate_submission()` (`capture_intake.py:75-106`):

```
REQUIRED (capture_intake.py:53-56):
  panel_item_id   str  — must match a config/panel.json entry exactly
  source          str  — provider name as the executor saw it
  source_url      str  — exact URL fetched
  fetched_at      str  — ISO-8601 UTC
  capture_outcome str  — one of: ok | unavailable | access_blocked | parse_error | source_missing
  executor        str  — free-text "<kind>:<identifier>", e.g. "human:jane-doe",
                          "ai:claude-code-web-session-...". No enum — convention only.
  raw_content     str  — the actual bytes fetched, OR (for a failure outcome) whatever
                          evidence exists: an error page body, or — as used in the real
                          incident — a synthesized description of what happened.

OPTIONAL:
  notes           str
  observation     dict — ONLY legal when capture_outcome ∈ {ok, unavailable}
                          (models.py:31, enforced at capture_intake.py:89-93):
      price, currency, unit, quantity_basis, lead_time_days,
      availability (must be in AVAILABILITY_VALUES), quote_type (must be "list_price" —
      the only QUOTE_TYPES member today), identity_values (dict keyed by the panel
      item's declared identity_fields)
```

Nothing is inferred or defaulted except `availability→"unknown"` and
`quote_type→"list_price"` (capture_intake.py:184-185) — every other field is exactly what
the executor supplied, or `None`.

### What C3 computes on intake (`capture_intake.py:109-218`)

- `raw_content_hash = sha256(raw_content)` — **the hash is what's stored in the Capture
  record; the raw bytes themselves are not.** The only durable copy of the actual raw
  content is the submission file itself, once moved to `incoming/processed/` (or
  `incoming/rejected/`) and committed to git. This is a real constraint for Section 5.
- `capture_id = "CAP-" + sha256(panel_item_id|fetched_at|raw_content_hash)[:24]` —
  deterministic, not random. Section 6 depends on this.
- `Capture` is always written (success or failure — `models.py:50-65`).
- `Observation` is written only if `capture_outcome ∈ OBSERVATION_PRODUCING_OUTCOMES =
  (ok, unavailable)` (`models.py:31`).
- `IdentityBreak` is written only if a new `spec_fingerprint` differs from the last known
  one for that panel item, and is always `status="UNRESOLVED"` — never auto-merged.

### Storage layout (`storage.py`, `README.md:92-104`)

```
config/panel.json                  20-item panel, versioned, human-edited
data/captures.jsonl                every attempt, ok or not — append-only
data/observations.jsonl            only from ok/unavailable captures — append-only
data/identity_breaks.jsonl         fingerprint discontinuities — append-only
incoming/                          drop zone for submission files
incoming/processed/                moved here after successful recording (kept forever)
incoming/rejected/                 moved here if validation fails (kept forever, not discarded)
reports/latest-summary.json        materialized view, always regenerable
reports/weekly-<date>.md           human-readable run summary
```

`AppendOnlyStore.append()` (`storage.py:54-68`) is a no-op — returns `False`, writes
nothing — if the record's id is already known. This is the entire idempotency mechanism
and it already works; see Section 6.

### GitHub Actions workflow (`.github/workflows/capability-observatory.yml`)

- Trigger: **`workflow_dispatch` only. No cron.** Explicitly by design (the file's own
  header comment).
- Steps: checkout → setup Python 3.11 → run C3's unit tests → run
  `run_capability_observatory.py process` → `git add data reports incoming` → commit
  directly → `git pull --rebase` → `git push` **directly to whatever ref triggered the
  workflow.** `permissions: contents: write`. No PR is opened anywhere in this workflow.
- The workflow **never fetches anything**. It only validates and records whatever is
  already sitting in `incoming/` when it runs. This is the exact boundary Slice 03 must
  respect: an executor's job ends the moment a submission file exists in `incoming/`
  before this workflow runs; everything after that point is C3's, unmodified.

### The hard safety boundary (`tests/test_safety.py`)

`test_no_network_client_anywhere_in_checked_in_source` fails the build if any file under
`src/capability_observatory/` contains `requests.`, `urllib.request`, `httpx.`,
`socket.`, `WebFetch`, `WebSearch`, etc. This is a **structural** guarantee, not a
convention: the executor's code must never live inside
`capability-observatory/src/capability_observatory/`, or CI breaks by design. There is
also a destructive-action scan (`os.remove`, `shutil.rmtree`, `.push(`, `.commit(`,
`.merge(` — `test_safety.py:33-44`) with the same enforcement.

### Panel prerequisite the executor inherits, unrelated to its own architecture

`config/panel.json` — **all 20 items still carry `source_url_pinned: false`**, and 13 of
them (all `provider_a_automationdirect` items) share the literal same bare homepage URL
(`https://www.automationdirect.com/`). Confirmed directly:

```
13 https://www.automationdirect.com/
 4 https://www.digikey.com/
 1 https://www.grainger.com/
 1 https://www.mcmaster.com/
 1 https://www.mouser.com/
```

This was true before the access_blocked incident and is independent of it — the panel
was never reachable far enough to hit this problem yet. Per the panel file's own notes
and `README.md:51-59`, pinning a real, live, publicly-priced product page per item is
**the first executor's job**, done as an explicit, versioned panel change
(`panel_version` bump, `added_in_panel_version` on each pinned item) — not a silent
overwrite, and not this design task's job to perform. Flagged here because it blocks
Slice 03's first real run regardless of which executor architecture is chosen, and
because fetching the bare AutomationDirect homepage 13 times would produce 13 identical
`raw_content_hash` values — not usable evidence.

### What an external executor must never do

- Never write to `data/*.jsonl` directly.
- Never move files into `incoming/processed/` or `incoming/rejected/` itself — that's
  `cmd_process`'s job, and doing it externally would desync the append-only stores from
  the moved-file record.
- Never invent a value for a field it didn't observe.
- Never live inside `capability-observatory/src/capability_observatory/`.
- Never attempt to make `capture_outcome` anything other than a truthful description of
  what happened.

---

## 2. Executor options comparison

Six architectures, evaluated against the task's 18 criteria. Full detail in prose below
the table; the table is a compressed summary, not a score.

| | A. GH-hosted runner | B. Self-hosted runner | C. Small cloud VM/container | D. Browser-automation-as-a-service | E. Human browser | F. Hybrid (A + E) |
|---|---|---|---|---|---|---|
| **1. Network reachability** | GH Azure datacenter IPs — **not** the blocked path | Whatever host you register — could be residential/business | Cloud-provider datacenter IPs | Vendor-managed IP pool | Ordinary residential — best | Best of A and E, item-by-item |
| **2. Reliability** | High (GH owns uptime) | Medium (you own uptime) | High if managed scheduler | High (vendor SLA) but 3rd-party dependency | Low for *cadence*, high for *quality* | Bounded by the weaker of the two paths per item |
| **3. Weekly automation** | Native `schedule:` cron | Native `schedule:` cron | Native platform scheduler | Triggered from a GH job | None — manual | Automated core + small manual queue |
| **4. Legal/ToS risk** | Low, for plain public GETs | Low, same | Low, same | **Risk rises sharply if "stealth"/proxy-rotation/CAPTCHA-solving tiers are used** | Lowest of all six | Lowest of the automated options |
| **5. Bot-protection risk** | Medium–High (GH IP ranges are well-cataloged as CI traffic) | Medium (depends on host reputation) | Medium (smaller/less-cataloged range than GH, not zero) | Low technically, but crosses into evasion if misused | Near zero | Bounded — only pays this cost on providers it works for |
| **6. Raw HTML preservation** | Trivial | Trivial | Trivial | Native | Manual discipline (view-source save) | Same as A for automated half |
| **7. Rendered-page preservation** | Needs Playwright add-on, doable in-runner | Same | Same, more headroom | Native, that's the product | Native (human sees the rendered page) | Same as A/E per item |
| **8. Dynamic JS sites** | Supported via headless Chromium at cost of job minutes | Same | Same, more comfortably | Purpose-built for this | Supported, free | Routed per-provider |
| **9. Price capture** | Depends on page, not host | Same | Same | Same | Best ground-truth fidelity | Same as constituent |
| **10. Stock capture** | Same | Same | Same | Same | Same | Same |
| **11. Lead-time capture** | Same | Same | Same | Same | Same | Same |
| **12. Operational cost** | ~Free (GH free-tier minutes) | Host cost + maintenance time | Real recurring $ + a second vendor | Metered, per-request $ | Person-time only (real but not $) | Automation cost + shrinking human-time budget |
| **13. Engineering complexity** | Low — one job, one script | Medium — provisioning + hardening + keep-alive | Medium–High — new infra + delivery-back-to-GH problem | Low integration, vendor-specific contract | None | Medium — two paths, one shared envelope |
| **14. Credential burden** | None for public GETs | Runner registration token | Cloud creds **+ a GitHub PAT stored outside GH's own secret store** | One more API key | None — no secrets touch the repo | Same as A, plus nothing new for E |
| **15. Failure observability** | Native GH Actions logs/summary (existing precedent in `observation-agent.yml`'s `ci_summary.py`) | Same, plus the runner's own liveness must be watched separately | Must build your own alerting, or round-trip through a GH workflow anyway | Vendor dashboard + caller logs | Self-reported at submission time | Native GH logs + a documented human checklist |
| **16. Vendor lock-in** | Some (GH Actions-specific YAML), portable script | Low, tied to a host | Cloud-provider-specific tooling | High — vendor API shape | None | Same as A |
| **17. Compatibility with C3 input contract** | Perfect — same repo checkout, writes JSON straight into `incoming/` | Same | Requires a delivery *mechanism* back to the repo (Section 8) | Same delivery-mechanism problem as C | Perfect — a human writes the same JSON shape | Perfect |
| **18. Independence from Claude/AI execution env** | **Yes — and this fixes the actual observed failure** | Yes | Yes, but now depends on a second vendor | Yes from AI vendors, but adds a third vendor and the highest ToS-risk surface of the six | Total | Total |

### Why this ranks the way it does

**A (GitHub-hosted runner)** is the strongest single option purely because it directly
answers the observed failure: the 20/20 `access_blocked` result was caused by an
AI-session network policy, and a GH-hosted runner is not that network. It costs
approximately nothing, needs no new credentials for public pages, fits the existing
`incoming/`-drop-zone contract with zero translation, and follows the exact pattern this
repo already uses successfully in `observation-agent.yml` (scheduled, read-mostly,
artifact/summary-driven). Its real risk is orthogonal to the failure we actually saw: GH
Actions egress IP ranges are well-known to commercial WAFs (Cloudflare, Akamai,
PerimeterX) as CI/bot infrastructure, so some fraction of these five providers may soft-
block or CAPTCHA-challenge it — a *different*, not-yet-observed risk, addressed in
Section 12.

**B (self-hosted runner)** trades GH's IP reputation for a host you control, which can
help if you have a business/residential IP, but GitHub explicitly warns against
self-hosted runners on repos where untrusted workflow triggers exist, and it adds a
standing maintenance burden (patching, uptime, and a silent-failure mode: an offline
runner just doesn't pick up dispatched jobs, and there is no automatic alert for that from
GitHub itself). Only worth it if A's bot-protection risk turns out to be real *and*
you already have a low-reputation IP host to register.

**C (small cloud VM/container)** buys nothing A doesn't already have, and adds a second
vendor plus the delivery-back-to-GitHub problem (a PAT stored outside GitHub's own secret
store — a new credential-security surface). Only justified if you specifically need more
compute/disk than GH's free runner gives you (e.g., heavy screenshot storage before
upload), which 20 items/week does not.

**D (browser-automation-as-a-service)** is real infrastructure for genuinely JS-heavy
pages, but its highest-value features (residential proxy rotation, CAPTCHA solving) are
explicitly the evasion techniques this task instructs against. Restricted to its
plain-rendering tier only, it's a viable *fallback for specific dynamic-JS providers*, not
a primary architecture — and even then it's a third vendor with vendor-specific API shape
and metered cost for no reachability benefit over A on providers that aren't actually
bot-gated.

**E (human browser)** is what already produced the one fully valid pair of fixtures in
this repo (`submission_ok_example.json`, `submission_access_blocked_example.json`, both
`executor: "human:jane-doe"`) and is the highest-fidelity, lowest-risk path per attempt.
It does not scale to a repeatable weekly cadence on its own — Section 12's "weekly human
fallback becomes operational debt" attack is real and is exactly why E is not the primary.

**F (hybrid)** is not a compromise between A and E — it is what the actual, unverifiable-
in-advance heterogeneity of these five providers forces. AutomationDirect and DigiKey/
Mouser (via official API) are plausible automation candidates; McMaster-Carr and Grainger
are enterprise-only for programmatic access and unverified for plain HTML risk. A single
uniform architecture applied to all five either over-invests in evasion-adjacent tooling
for the hard providers or under-uses the easy ones. F bounds the automation risk to where
it's earned and the human cost to where it's actually needed. This is the recommendation
(Section 15).

*Note on a 7th option:* the task allows adding one. "Official distributor API
integration" is not a *hosting* choice — it's a *data-source* choice orthogonal to A–F
(an official API call can run from a GH Actions job exactly like an HTML fetch can). It is
evaluated per-provider in Section 4 rather than listed here as a seventh architecture.

---

## 3. Public access vs. access control — the line the executor must not cross

| Category | Executor behavior |
|---|---|
| Normal public page retrieval (unauthenticated GET, no challenge) | **Allowed** — this is the target case |
| `robots.txt` restrictions | **Respected.** A disallowed path is not fetched; the panel item is marked `DROP_PROVIDER` or `HUMAN_FALLBACK`, never routed around |
| Rate limits (stated or observed via 429/Retry-After) | **Respected.** Back off per the stated policy; a rate-limited item this run becomes next week's evidence, not a reason to hammer harder |
| Login-required content | **Never attempted.** Out of scope — C3 measures public list prices only (`quote_type=list_price` is the only supported value) |
| Geo-restricted pages | Recorded as `access_blocked` if hit; not worked around with proxies/VPNs |
| Bot challenges (JS challenge pages, Cloudflare/Akamai interstitials) | Recorded as `access_blocked`. No headless-browser fingerprint spoofing, no challenge-solving |
| CAPTCHA | **Never solved, automatically or via a paid solving service.** Immediate `access_blocked` → route to `HUMAN_FALLBACK` or `DROP_PROVIDER` |
| Explicit denial (403, ToS statement against automated access) | **Terminal for that provider.** Never retried with different headers/UA to "get past it" |
| API-only access (official, documented, self-serve) | **Preferred over HTML scraping wherever it exists** — see Section 4 |

The distinguishing test the executor applies before automating any provider: *is this a
technical control the provider put there on purpose to stop exactly this kind of
automated access?* If yes, automation stops there — full stop, not "automation with a
workaround." That decision is made once per provider, in Section 4, and re-checked
periodically (Section 11), not decided ad hoc inside a scraping loop.

---

## 4. Provider-by-provider strategy

Verified against public documentation where reachable; where this session's own
`EGRESS_BLOCKED` against these five domains made direct verification (robots.txt,
provider ToS text) impossible, that is stated explicitly rather than assumed.

| Provider | Official API? | Method recommendation | Confidence |
|---|---|---|---|
| **DigiKey** | **Yes, confirmed.** Public self-serve developer portal (`developer.digikey.com`), Product Information V4: `ProductSearch`, `ProductDetails`, `ProductPricing` — explicitly "real-time pricing and availability." OAuth2, sandbox app to start. | **API.** Highest-confidence path of all five. | High — verified via developer portal search results |
| **Mouser** | **Yes, confirmed.** Public Search API (`mouser.com/api-hub`), **free**, key via a request form (1–2 business day approval), rate-limited 30 calls/min, 1000/day. Returns MPN, availability, **lead time explicitly listed**, up to 4 price breaks, packaging, category. | **API.** Second-highest confidence; explicitly returns all three fields C3 needs (price, stock, lead time) in one documented schema. | High |
| **AutomationDirect** | **Unclear, not ruled out.** Their own site references a "Product API," and a live community-forum thread is literally titled *"API for price and stock status on AutomationDirect"* — but this session cannot reach `community.automationdirect.com` (same egress block) to read what it says. | **Verify API first** (this is a human-doable, 10-minute check from an unblocked network — read that forum thread and `support.automationdirect.com`). If no accessible API: **HTML capture candidate** — smaller catalog site, historically simpler markup than the big distributors, not confirmed to run aggressive bot-management. Must check `robots.txt` from the actual executor host (not from here) before the first automated fetch. | Medium — real signal found, not independently confirmed |
| **McMaster-Carr** | **Enterprise-only, confirmed.** They publish a "Product Information API" (`mcmaster.com/help/api/`) explicitly for *approved* procurement customers doing OCI/punchout integration — not public self-serve signup. No path to this within a 30-day trial without an existing commercial account. | **HUMAN_FALLBACK**, at least initially. McMaster-Carr is also widely known in the scraping community for aggressive anti-automation measures (obfuscated markup, session-gated pricing) — consistent with an enterprise-only API stance. Do not attempt HTML capture without first re-verifying `robots.txt`/ToS from an unblocked host; if it disallows automated access, this becomes `DROP_PROVIDER` or stays `HUMAN_FALLBACK` permanently. | Medium-high on "no self-serve API"; low on markup difficulty (industry reputation, not independently re-verified here) |
| **Grainger** | **No public self-serve API found.** Only punchout/EDI integration for enterprise procurement accounts, reported 4–6 week setup — not viable for this trial. | **HTML capture candidate, with caution** — verify `robots.txt` from the actual executor host first. If Grainger runs enterprise-grade bot management (plausible for a Fortune 500 distributor, not independently confirmed), fall back to `HUMAN_FALLBACK`. | Medium — API absence confirmed by search; bot-protection posture not verified |

None of the above is final. This table is the starting hypothesis for Slice 03's first
run: try the API where one plausibly exists, check `robots.txt` from the real executor
host (not from this design session) for HTML-candidate providers before ever fetching a
product page, and downgrade to `HUMAN_FALLBACK` the moment either check fails. No provider
is assumed automatable before that check actually happens.

---

## 5. Raw evidence envelope

The C3 `Capture` record already defines the authoritative fields
(`panel_item_id, source, source_url, fetched_at, capture_outcome, executor, raw_content
→ raw_content_hash, notes`). The executor's envelope is **exactly the existing submission
shape from Section 1 — no second ontology.** The only genuinely new concept is what the
executor keeps *before* it writes that JSON file, since — as noted in Section 1 — C3
itself only persists a hash of `raw_content`, not the bytes; the only durable copy of the
actual raw content is the submission file once committed.

Per attempt, the executor should locally produce, then fold into the one submission file:

| Field | Where it goes | Notes |
|---|---|---|
| `requested_url` | `source_url` | Already in the contract |
| `final_url` (post-redirect) | New field inside `notes`, or appended to `raw_content` as a preface line | Not in today's schema — worth having when a provider redirects a stale product URL to a category page, which is itself evidence of "product disappeared" |
| `fetched_at` | `fetched_at` | Already in the contract; must be the actual fetch instant, not a batch/run timestamp |
| HTTP status | `notes` (free text) today; candidate schema field if this becomes systematic — see Section 9 | Distinguishes 403 (blocked) from 404 (gone) from 200-with-CAPTCHA-body |
| Response headers subset (`Content-Type`, `Server`, rate-limit headers if present) | `notes` | Only what's useful for later diagnosis — not the full header dump |
| `raw_content` / body | `raw_content` | Already in the contract. For HTML: the actual response body. For a rendered/JS page where a screenshot is the only evidence: the extracted text/DOM snapshot, with the screenshot referenced separately (below) |
| `raw_content_hash` | Computed by C3, not the executor | Already automatic (`capture_intake.py:124`) |
| Rendered screenshot (only when JS rendering was needed) | **Not embedded in the JSON.** See below | Screenshots are binary and can be large; embedding base64 in a JSON submission file that lives forever in git is exactly the "screenshots become huge" risk flagged in Section 12 |
| `executor` version/identity | `executor` | Extend the existing free-text convention to `<kind>:<identifier>:<version>`, e.g. `automation:gh-actions-executor:v1` — still just a string, no schema change |
| Capture method (`api` / `html` / `rendered` / `human`) | `notes`, structured as a short prefix, e.g. `"method=api;..."` | Candidate for a real field later (Section 9) but not required to start |
| `provider`, `panel_item_id` | Already required fields | — |
| Access outcome | `capture_outcome` | Already the contract's core field |
| Error category | `notes` | See Section 9 for why today's 5-value vocabulary is coarser than what's needed here |

**Screenshot handling:** if a provider genuinely requires JS rendering to reach the
price/stock text (Section 4 will show this is not yet confirmed necessary for any of the
five), store the screenshot as a GitHub Actions **artifact**, not inside the committed
JSON — reference it by artifact name/run ID in `notes` if wanted for a human to
double-check later. Do not commit binary screenshots into `incoming/processed/` — that
directory is kept forever, and unlike `raw_content_hash`, a screenshot has no compact
canonical form to fall back to. This is a design constraint, not a decision to build a
screenshot pipeline now — none of the five providers is yet known to need one.

---

## 6. Idempotency

**The recording layer is already idempotent — read from code, not assumed:**
`capture_id = "CAP-" + sha256(panel_item_id|fetched_at|raw_content_hash)[:24]`
(`capture_intake.py:63-64`), and `AppendOnlyStore.append()` is a no-op — returns `False`,
writes nothing — when that id is already known (`storage.py:54-62`). Re-running
`run_capability_observatory.py process` against the same already-committed
`incoming/processed/*.json` file (e.g., after a crashed workflow run gets re-dispatched)
reproduces the identical `capture_id` and correctly no-ops. This needs no new design.

What the *executor* needs to guarantee, upstream of that:

- **Deterministic attempt identity:** one submission file per `panel_item_id` per weekly
  run, named by convention (e.g. `week-<iso-week>-<panel_item_id>.json`, matching the
  existing `incoming/processed/` naming already visible in the repo). This is a
  file-naming discipline for the executor's own working directory, not something C3
  enforces — `_process_incoming` (`cli.py:89-92`) picks up every `*.json` file in
  `incoming/` regardless of name.
- **Retry behavior:** keep transient retries (timeout, 5xx, connection reset) **internal**
  to the executor's fetch step, with backoff. Submit exactly one file per item per run,
  reflecting the *final* outcome of that run's attempt — not one file per retry. This
  keeps `captures.jsonl` at one record per item per week under normal operation, matching
  the panel's own weekly cadence, while still recording a genuine failure honestly if all
  retries exhaust.
- **Same URL fetched twice in one run:** does not currently occur across *different*
  panel items with genuinely different products — but will occur today if the panel's
  unpinned placeholder URLs (Section 1) are fetched as-is, since 13 items share one bare
  homepage URL. This is a reason pinning must happen before automation starts, not
  something the executor should paper over by de-duplicating fetches — each panel item is
  a distinct piece of evidence even if (before pinning) the URL happens to collide.
- **Partial failure handling:** if a run completes 12/20 items before crashing, submit
  files for the 12 completed items; do not synthesize placeholders for the other 8.
  Per the "no historical backfill" project rule, the missing 8 are not retroactively
  filled in — next week's scheduled run attempts all 20 again, honestly.
- **Interrupted run:** the GH Actions commit step is last. If the job is killed before
  it, nothing is committed — no partial or corrupted state reaches `data/*.jsonl`. A
  re-dispatch performs a fresh full attempt; any differing `fetched_at` values just
  produce distinct, honest Capture records, never a silent overwrite.
- **Rerun after GitHub failure:** covered by the two points above — deterministic
  `capture_id` at the recording layer, and "submit only completed items" at the executor
  layer, together make a full rerun safe by default.

No database is needed. The append-only JSONL files plus deterministic ids are sufficient;
this matches the project's own "prefer removing a component over generalising it" rule.

---

## 7. Security model

**Rules applied directly:**

- **No secrets in the repo.** Any provider API key (DigiKey OAuth client secret, Mouser
  key) is a GitHub Actions **encrypted secret**, referenced as `${{ secrets.* }}` — the
  same pattern already in use for `ANTHROPIC_API_KEY` in
  `constraint-archaeology-daily.yml:31`.
- **No secrets in Capture records.** `executor`, `notes`, and `raw_content` must never
  contain an API key, token, or session cookie — this needs to be an explicit executor
  invariant (a redaction check before writing the submission file), since a copy-pasted
  raw response body from an authenticated API call could otherwise leak a key into a
  file kept forever in `incoming/processed/`.
- **Least privilege.** The workflow's `GITHUB_TOKEN` (or a scoped PAT if going the PR
  route — Section 8) needs write access to `capability-observatory/{data,reports,
  incoming}` only. GitHub Actions permissions are repo-wide, not path-scoped, so this is
  enforced by **branch protection + CODEOWNERS on the frozen paths**, not by the token
  itself — see Section 14 for exactly which paths need that.
- **The executor cannot modify Constraint Archaeology.** It has no code path that
  touches `constraint-archaeology-agents/` at all — same structural independence C3
  itself already claims in its own README (`capability-observatory/README.md:9-10`).
- **Provider API keys** (DigiKey, Mouser): least-privilege means read-only product-search
  scopes only, never an order-placing or account-management scope, even if the vendor
  offers one.

**Direct commits to `main` vs. a PR/artifact boundary:**

The existing `capability-observatory.yml` workflow already commits directly to whatever
ref triggered it, with `contents: write`. That precedent exists and works for
*human/AI-in-the-loop* submissions dropped into `incoming/` by hand before the workflow
runs. An *unattended, scheduled* executor is a materially different trust boundary: it
runs with no human reviewing its output before it lands. Recommendation: **the executor
itself should never hold repo-write credentials at all.** It should only ever be able to
place files into `incoming/` — via a GitHub Actions artifact upload (Section 8, option C)
or a PR (option B) — and the *existing, already-reviewed* `capability-observatory.yml`
`process` step remains the only thing with `contents: write`. This means a compromised or
malfunctioning executor can, at absolute worst, submit garbage that C3's own validation
(`validate_submission`) rejects into `incoming/rejected/` — it can never itself push a
commit, and it never needs a GitHub PAT with repo-write scope at all.

---

## 8. Data delivery options

| Option | Mechanism | Fit for a 30-day trial |
|---|---|---|
| A. Commit directly to `incoming/` | Executor holds a repo-write credential, pushes JSON files itself | **No** — gives the executor exactly the credential Section 7 argues against holding |
| B. Open a PR containing incoming files | Executor pushes to a branch, opens a PR; a human or the existing workflow merges | Safer than A, but adds review latency to a process that's supposed to run unattended weekly, and a PR-per-week for machine-generated JSON is process overhead disproportionate to the content |
| **C. GH Actions artifact → existing `process` workflow ingests it** | Fetch job runs as its own workflow (or an early job in the same workflow), uploads submission JSON as a build artifact; a subsequent step/job downloads the artifact into `incoming/` before calling the *existing, unmodified* `run_capability_observatory.py process` | **Recommended.** No new credential at all — same `GITHUB_TOKEN`, scoped to the one workflow run. Zero new infrastructure: it's one more job in the same GH Actions pipeline that already exists |
| D. Object storage + manifest committed to repo | S3/GCS bucket holds raw payloads, repo holds a manifest pointing at them | Overbuilt for 20 items/week of mostly-text HTML; adds a cloud-storage credential and a second source of truth the task explicitly warns against ("avoid building infrastructure for hypothetical scale") |
| E. API/webhook endpoint | A hosted endpoint receives captures, writes to the repo itself | Requires standing infrastructure (something has to host the endpoint) for no benefit over C at this scale |

**Minimum for the first 30 days: C.** Concretely: the *fetch* step (new) runs as a job in
GitHub Actions (triggered on the same `workflow_dispatch`, or a new `schedule:` cron —
that trigger-type decision is itself an implementation detail, not part of this design),
writes submission JSON files, uploads them as a build artifact. A following job downloads
that artifact into `capability-observatory/incoming/` and then invokes the **existing,
untouched** `run_capability_observatory.py process` — i.e. Slice 03 adds a *producer* job
in front of the *consumer* workflow that Slice 02 already built and tested; it does not
modify the consumer at all.

---

## 9. Failure semantics

**The real incident is the clearest evidence for what's missing.** Today's
`CAPTURE_OUTCOMES = (ok, unavailable, access_blocked, parse_error, source_missing)`
(`models.py:25`) has exactly one bucket, `access_blocked`, for "we got no trustworthy
content, and it wasn't a parse problem." The actual incident put a genuine **executor
network/infra failure** (the AI session's own egress proxy refusing the connection before
it ever reached the provider) into that same bucket as a genuine **vendor-side denial**
(a CAPTCHA/WAF challenge, as in `tests/fixtures/submission_access_blocked_example.json`).
The only thing that kept these distinguishable at all was a hand-written sentence in
`notes`: *"This is NOT a vendor bot-detection event."* That's a convention holding up a
distinction the schema doesn't make. If it happens again with a less careful `notes`
entry, `rule_a_capture_mechanism_failing` fires and reads as "the domain/providers can't
be captured," when what actually happened is "the network path we used doesn't work,"
which is a far cheaper problem to fix.

Mapping the task's failure list onto today's vocabulary, and marking the gaps:

| Failure | Today's outcome | Clean fit? |
|---|---|---|
| Provider truly unavailable (site down) | `access_blocked` (stretch) or `source_missing` | Ambiguous |
| Product disappeared (page 404s / redirects to category) | `source_missing` | Clean |
| Access blocked *by the provider* (CAPTCHA, WAF, login wall) | `access_blocked` | Clean, if this is the only thing living there |
| **Executor network failure** (DNS, TLS, egress policy, connection refused before reaching the provider) | `access_blocked` (what actually happened) | **Not clean — this is the exact gap the incident exposed** |
| Parser failure (page fetched fine, extraction logic broke) | `parse_error` | Clean |
| Timeout | No clean home — currently would be shoehorned into `access_blocked` | **Gap** |
| Credentials failure (API key rejected/expired) | No clean home — only matters once Section 4's API path is used | **Gap, but only relevant once an API executor exists** |
| API quota failure (e.g. Mouser's 1000/day cap exceeded) | No clean home | **Gap, same condition** |
| Invalid product page (loaded, but doesn't match expected identity_fields) | `parse_error` | Clean |

**The smallest compatible extension — not implemented here, per instructions —** would
split today's overloaded `access_blocked` into vendor-side denial vs. executor-side
infrastructure failure, and add a distinct `timeout` value:

```
CAPTURE_OUTCOMES (proposed, additive only — existing five values keep their meaning):
  ok, unavailable, source_missing, parse_error,   # unchanged
  access_blocked,          # narrowed: confirmed vendor-side denial only
                            # (CAPTCHA, WAF challenge body, explicit 403-with-denial-page,
                            #  robots.txt disallow)
  executor_network_failure,  # NEW — DNS/TLS/connection/egress-policy failure before
                              # any provider response was received
  executor_auth_failure,     # NEW — only reachable via an API executor; credentials
                              # rejected/expired
  executor_quota_exceeded,   # NEW — only reachable via an API executor; provider-side
                              # rate/quota limit hit
  timeout,                   # NEW — request sent, no response within budget
```

None of these new values would join `OBSERVATION_PRODUCING_OUTCOMES` — they're all still
"no trustworthy content," same as today's `access_blocked`. This changes
`metrics.py::observability` and `capture_success` not at all in shape, only in which
bucket a given failed attempt lands in — meaning `Rule A`'s *meaning* sharpens (it becomes
"the mechanism that talks to providers doesn't work" only when the failures are actually
`access_blocked`/`parse_error`/`source_missing`, rather than firing identically on a
transient infra outage). Until this extension actually happens, the fallback discipline is
the one already used in the real incident: **be explicit in `notes` about whether a given
`access_blocked` was vendor-side or executor-side**, and treat that distinction as load-
bearing when reading `Rule A`, not just decorative.

---

## 10. Human fallback protocol

For any panel item marked `HUMAN_FALLBACK` in Section 4 (or that repeatedly fails
automation — see Section 11's per-provider failure-rate metric), the fallback is not a
separate truth model — it is **the exact same submission envelope from Section 1**,
`executor` field set to `human:<name>`, exactly as already demonstrated by
`tests/fixtures/submission_ok_example.json`. Discipline required of the human step:

1. **Timestamp:** record `fetched_at` at the moment the page is actually viewed, not
   batched to a round hour or backfilled after the fact.
2. **URL:** the exact product-page URL landed on, including any redirect — not a search
   query, not a category page (unless the item is genuinely confirmed gone, in which
   case that IS the evidence, recorded as `source_missing`).
3. **Raw/screenshot evidence:** view-source or a full-page screenshot, kept alongside the
   submission (Section 5's artifact-not-commit guidance applies here too).
4. **Price/stock/lead-time exactly as observed** — copied from what the page actually
   shows, not corrected, rounded, or reconciled against last week's number.
5. **Executor identity:** `human:<real name or handle>`, consistently, so
   `provider_parse_failure_rate`-style per-executor breakdowns are possible later if
   needed.
6. **No retrospective reconstruction.** If the human forgot to capture in the correct
   week, that week is `INSUFFICIENT DATA` for that item — never filled in after the fact
   from memory or a cached browser tab from days later. This is the same "no historical
   backfill" rule already governing `findings.jsonl`, applied here to the human path
   specifically because it's the path most tempted to "just fix it retroactively."

The human path feeds the identical `incoming/` → `process` pipeline as the automated
path. There is no separate ledger, no separate schema, no separate report.

---

## 11. First 30-day executor experiment

C3's own 30-day trial and stop rules (`metrics.py`) are unmodified and remain the primary
gate. Slice 03 adds executor-specific metrics *on top*, computed from the same
`data/captures.jsonl` plus a small amount of executor-side run metadata (timing, cost) not
currently in scope for C3's own schema:

| Metric | Definition | Derived from the 20-item panel |
|---|---|---|
| Provider reachability rate | Fraction of attempts that got *any* provider response (not `executor_network_failure`/`timeout`) | Per provider, out of its item count (13/1/1/4/1) |
| Successful raw capture rate | Fraction of attempts with `capture_outcome` ∈ {ok, unavailable} — i.e., not blocked/failed | Same denominator as C3's own `capture_success` |
| Successful Observation yield | Same as C3's `observability` (already computed) | Reused, not duplicated |
| Automation coverage | Panel items successfully captured by an automated path (API or HTML), vs. items requiring `human:` | Out of 20 |
| Human-fallback rate | Fraction of weekly attempts routed to `HUMAN_FALLBACK` | Target: shrinking over the 30 days, not flat |
| Median execution time | Wall-clock per successful automated capture | Executor-run metadata, not a C3 field |
| Cost per successful observation | (GH Actions minutes cost + any API metering) ÷ successful Observations that week | Should be near-zero given free-tier GH minutes and free DigiKey/Mouser API tiers |
| Provider-specific failure rate | `parse_error`/`access_blocked` rate per provider — **this already exists**: `metrics.py::provider_parse_failure_rate` computes exactly this, with a 20% alert threshold, per provider | Reused as-is |
| Dynamic-page failure rate | Fraction of failures specifically attributable to needing JS rendering that wasn't attempted | New — only meaningful once Section 4's per-provider method is actually tried |

### Executor-specific stop/redesign thresholds

Derived from the actual 5-provider, 20-item panel composition (13/1/1/4/1 items across
AutomationDirect/Grainger/McMaster/DigiKey/Mouser):

- **If DigiKey and Mouser (5/20 items, both API-confirmed) cannot reach the 60% capture-
  success target via their official APIs**, that is a signal the executor implementation
  is broken, not that the domain is unreachable — these are the highest-confidence paths
  in Section 4, and failure there should trigger an executor-code review before anything
  else.
- **If AutomationDirect (13/20 items — the majority of the panel) ends up
  `HUMAN_FALLBACK` or `DROP_PROVIDER`**, automation coverage caps out at 5/20 (25%) even
  with both APIs working perfectly. At that point, ask explicitly (matching the task's own
  example rule): *is a hybrid architecture that only reliably automates 1/5 providers
  still worth running,* given the human-fallback labor for the other 13-item majority is
  the real weekly cost driver? This is a redesign trigger, not an automatic kill — C3's
  own `Rule A` (< 60% success AND < 15/20 observed) would very likely already be firing in
  this scenario anyway, since 25% automation coverage plus a stretched human-fallback
  queue is exactly the shape Rule A is built to catch.
- **If human-fallback rate is not shrinking over successive weeks** (i.e., no
  automation coverage gained as the executor is iterated on), that's the "operational debt"
  failure mode named in Section 12 — treat as a redesign trigger independent of whether
  C3's own stop rules have fired yet, since C3's rules are about *whether capture works at
  all*, not about *whether the labor cost is sustainable*.

---

## 12. Adversarial attack

| Attack | Verdict | Reasoning |
|---|---|---|
| GitHub-hosted IPs get blocked | **PLAUSIBLE, unconfirmed** | Not yet observed — the actual incident was an AI-session egress policy, not a WAF decision against a datacenter IP. GH Actions IP ranges are publicly documented and are a known signature to commercial bot-management, so this is a real, live risk for the automated half, distinct from the failure already seen. First real automated run is the actual test |
| Cloud VM IP gets blocked | **PLAUSIBLE, unconfirmed** | Same category of risk as above, for Option C — not chosen as primary, so this attack mainly argues against *escalating* to C if A gets blocked, rather than against A itself |
| Provider changes HTML | **SUPPORTED — will happen eventually** | `provider_parse_failure_rate` already exists in `metrics.py` with a 20% per-provider alert threshold specifically for this. Design already survives this by detecting it, not preventing it |
| JS rendering breaks | **INSUFFICIENT_DATA** | No provider in Section 4 is yet confirmed to *require* JS rendering for price/stock text — this may never materialize as a real cost. If it does, Option D's plain-rendering tier is the documented fallback (Section 2), not a reason to abandon the design |
| Official API omits lead time | **PLAUSIBLE for DigiKey, REFUTED for Mouser** | Mouser's documented schema explicitly lists lead time as a returned field (verified via search). DigiKey's confirmed fields are pricing/availability; lead time (commonly `ManufacturerLeadWeeks` in DigiKey's actual schema from general familiarity with the API, not independently re-verified here) needs confirming against live docs before build — flagged, not assumed |
| Public price differs from transaction price | **SUPPORTED, and already designed for** | C3's `quote_type` field exists precisely for this, hard-restricted to `"list_price"` only (`QUOTE_TYPES = ("list_price",)`, `models.py:41`) — the schema already refuses to conflate the two. Slice 03 changes nothing here; the executor simply never has access to a transaction price to begin with (no login, no account) |
| Weekly human fallback becomes operational debt | **SUPPORTED — the real risk of this whole design** | This is why Section 11 adds a shrinking-human-fallback-rate threshold as an explicit redesign trigger independent of C3's own stop rules, and why F is scoped as "automation for what's provably automatable, human for the bounded rest," not "human as a permanent crutch for 13/20 items" |
| Screenshots become huge | **REFUTED, by design choice** | Section 5 explicitly keeps screenshots out of committed JSON, in GH Actions artifacts (which expire) instead. No screenshot pipeline is being built until a provider is actually shown to need one |
| Raw HTML storage grows | **SUPPORTED, bounded** | `incoming/processed/*.json` already grows forever by design (append-only, never pruned) — this is the *same* growth pattern the project already accepts for `data/*.jsonl` (CLAUDE.md: "append-only... never rewritten"). 20 items/week of mostly-text HTML is on the order of tens of KB/week; not a near-term concern, but worth noting as a long-horizon cost the project has already chosen to accept elsewhere |
| Provider ToS changes | **SUPPORTED** | Section 4's per-provider classification is not permanent — Section 11's periodic re-check (implicitly, each weekly run's failure pattern) is the detection mechanism; a provider moving from HTML-viable to blocked shows up as a `provider_parse_failure_rate`/`access_blocked` rate spike, same signal as an HTML change |
| Executor silently loses coverage | **REFUTED by C3's own design, if Section 9's extension lands** | `observability` and `capture_success` are recomputed fresh from the append-only logs every run (`metrics.py`'s own docstring: "none of them write anything... always recomputed fresh") — a coverage drop is visible in the very next weekly report, not hidden. The remaining risk is exactly Section 9's gap: a coverage drop caused by *infra* failure currently looks identical to one caused by *provider* failure unless `notes` is read carefully |
| Access works now but fails unpredictably later | **SUPPORTED — accepted, not solved** | No design eliminates this; the honest position is that Section 11's metrics catch it *after* it happens, same as any real-world capture system. This is why the executor's failure semantics (Section 9) matter more than perfect uptime: when it fails, the failure needs to be legible, not why it never fails |

**Does the design survive?** Yes, with two explicit, named residual risks the design
does not eliminate and should not pretend to: (1) GH-hosted IP bot-protection risk is
real and untested until the first automated run actually happens, and (2) human-fallback
labor cost is the design's actual long-term liability if AutomationDirect's 13/20-item
majority ends up not automatable. Both are addressed by making them *visible, measured
things* (Section 11's metrics and stop thresholds) rather than by claiming to prevent
them in advance.

---

## 13. Minimum Slice 03

One external executor. One submission envelope (Section 1's existing shape, unchanged).
One delivery mechanism (Section 8, option C — artifact → existing `process` workflow).
One executor health report (a short per-run summary — reachability rate, automation
coverage, human-fallback count — alongside the existing `reports/weekly-<date>.md`, not
replacing it).

Nothing here requires a second executor backend, a database, object storage, or a new
top-level primitive beyond what C3 (Section 1) and the Reality Observatory's own six
primitives (`docs/architecture/reality-observatory-v0.1.md`, §1: Capture, Observation,
Entity, Expectation, Finding, Link) already define. A second executor later (e.g., adding
Option D for one specific confirmed-JS-only provider) plugs into the same `incoming/`
contract without changing the C3 evidence model at all — that's the property the "thin
submission envelope, not a second ontology" instruction (Section 5 of the task) is
actually protecting.

---

## 14. Repository plan

```
CREATE (net new, none of it built yet — this design task creates none of this either)
  .github/workflows/capability-observatory-fetch.yml
      New workflow. Producer job: runs the fetch executor (API calls for DigiKey/Mouser,
      HTML fetch for AutomationDirect/Grainger pending robots.txt check, human-submitted
      files for McMaster-Carr/HUMAN_FALLBACK items), writes submission JSON, uploads as a
      build artifact. Consumer job: downloads the artifact into
      capability-observatory/incoming/, then calls the EXISTING
      run_capability_observatory.py process unmodified (or triggers
      capability-observatory.yml as a follow-up dispatch — an implementation choice, not
      a design one).

  capability-observatory-executor/                (name illustrative, not final)
      A new, separate package — sibling to capability-observatory/, not inside it.
      Contains the actual fetch code (API clients, HTML fetch, robots.txt check). Must
      live OUTSIDE capability-observatory/src/capability_observatory/ specifically
      because of test_safety.py's network-call ban (Section 1) — this is a hard
      structural requirement, not a style preference.

  capability-observatory-executor/config/provider_strategy.json  (or similar)
      Machine-readable version of Section 4's table: per-provider method
      (api/html/human/drop), so the workflow can route without re-deciding by hand
      each week.

  docs/decisions/003-*.md  (candidate, once actually implemented)
      "External capture executor decoupled from AI-hosted execution environments" — the
      root-cause finding in Section 0 is exactly ADR-shaped: a decision, a rejected
      alternative (running fetches from inside the same session that failed), and a
      consequence (a second CI workflow, no new credentials for the public-page path).
      Per docs/decisions/README.md convention: written when the decision is actually
      implemented, not before.

MODIFY (existing files, touched only for genuinely necessary reasons, all narrow)
  capability-observatory/config/panel.json
      Pin real source_url values (Section 1's prerequisite) — an explicit, versioned
      panel change (bump panel_version, set added_in_panel_version), done once, by
      whoever runs the first real automated/human capture per item. Not a Slice 03
      architecture change; a pre-existing panel-maintenance debt this design surfaces.

  capability-observatory/README.md
      Add a short "How the weekly capture is now performed" addendum once Slice 03
      actually exists, without rewriting the existing "How a weekly capture is
      performed" section's substance — fetching is still external to the package,
      still never touches the network from inside src/.

  capability-observatory/src/capability_observatory/models.py
      ONLY if Section 9's CAPTURE_OUTCOMES extension is separately approved — additive
      only (new tuple members), no existing value's meaning changes, no dataclass field
      removed or renamed. Not part of this design task's own deliverable; flagged as the
      smallest compatible extension, left unimplemented per instructions.

DO NOT TOUCH
  docs/method/constraint-archaeology-v0.4-spec.md
  docs/method/constraint-archaeology-v0.5-patch.md
  docs/method/blind-discovery-protocol-2026.md
  docs/method/blind-discovery-2026-move1.md
  docs/method/controls/**
  tests/test_same_mechanism_gate.py
  constraint-archaeology-agents/**                          (all of it)
  .github/workflows/constraint-archaeology-daily.yml
  capability-observatory/src/capability_observatory/**      (existing files — the
      executor is additive alongside this, never edits inside it, except the one
      narrowly-scoped models.py change above, if and when separately approved)
  capability-observatory/data/*.jsonl                       (append-only; Slice 03 adds
      records through the existing intake path only, never edits these files directly)
  capability-observatory/tests/**                           (existing tests; new
      executor code gets its own test suite in its own package, doesn't touch these)
  .github/workflows/capability-observatory.yml               (the existing consumer
      workflow — Slice 03's new workflow feeds it via artifact, per Section 8; this
      file's own `process` step logic does not change)
  20-item panel identity (panel_item_id, category, provider, identity_fields) — only
      source_url and source_url_pinned are touched, per the panel's own versioning rule
  Stop-rule thresholds in metrics.py (MIN_OBSERVABILITY_COUNT, MIN_CAPTURE_SUCCESS_RATE,
      MAX_IDENTITY_BACKLOG, PARSE_FAILURE_ALERT_RATE)
```

---

## 15. Decision

**GO**, scoped exactly to Section 13's minimum: one executor, one envelope, one delivery
mechanism, one health report — with the two residual risks from Section 12 named and
measured (Section 11), not assumed away.

**Primary executor: A — GitHub-hosted Actions runner**, calling official APIs where
Section 4 found one (DigiKey, Mouser — highest confidence, 5/20 panel items) and plain
HTTP/HTML fetch for AutomationDirect pending the two open verification steps a human can
close in minutes (read the community API thread this session couldn't reach; check
`robots.txt` from an unblocked network). This directly fixes the actual, reproduced
failure (Section 0) at effectively zero marginal cost and zero new credentials for the
public-page path, and needs no new infrastructure beyond one more job in a workflow
pattern this repo already runs successfully (`observation-agent.yml`).

**Fallback: E — human browser-assisted capture**, for McMaster-Carr and Grainger (no
viable public API found, unverified HTML risk against likely enterprise-grade bot
management) and for any item that fails automation repeatedly regardless of provider
(Section 11's per-provider failure-rate metric already exists to detect this). Feeds the
identical `incoming/` intake path — no separate model, per Section 10.

This is architecture F (hybrid) in Section 2's terms, with F's two constituent options
named explicitly as primary and fallback rather than left as an abstract "hybrid."

Not recommended, and not part of the primary/fallback pair: B and C (no reachability
benefit over A for this scale, add a maintenance or credential burden A doesn't have), and
D beyond its plain-rendering tier as a possible narrow addition later, only if a specific
provider is later confirmed to require JS rendering — which none currently is.
