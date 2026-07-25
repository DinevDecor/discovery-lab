# Known Limitations — Research Reality Sensor 001

Documented scope boundaries and honestly-observed weaknesses, not bugs
to be silently tightened away — same discipline `reality-sensor/docs/
KNOWN-LIMITATIONS.md` established for its own tool.

## Architectural

- **This sensor cannot fetch the internet itself.** Its checked-in
  source is, by design and by test (`tests/test_safety.py`), 100%
  network-free. It depends entirely on a human or AI executor
  performing the capture step and supplying a well-formed raw-captures
  file. Same dependency `reality-sensor` documents for itself.
- **`architectural_relevance` and `possible_experiments` quality
  depends on the capture step's own judgment**, not on the raw paper
  text directly — the same deliberate design choice `reality-sensor`
  makes for its `practical_impact_note`, for the same reason (keeps
  the checked-in pipeline deterministic and testable).

## Operational

- **Direct `WebFetch` was blocked (HTTP 403) on every domain attempted
  in this task's real capture pass** — `arxiv.org` (both `/abs/` and
  `/pdf/` paths), `deepmind.google`, and `alignment.anthropic.com` all
  returned 403 to this session's fetch tool. This is a stricter block
  than `reality-sensor`'s own validation pass encountered (which
  reached 2 genuinely `PRIMARY` sources directly). As a result, **every
  quoted abstract in `validation-dataset/raw-captures-2026-06-25-to-2026-07-25.json`
  is sourced from `WebSearch`'s indexed snippet text, not a direct
  fetch of the paper's own page** — real, attributed, and traceable to
  a real `source_url`, but not independently re-verified against the
  primary page by this session. A future capture pass with working
  `WebFetch` access to these domains should re-verify.
- **Three captures carry an explicit date-precision caveat** rather
  than a fabricated exact date: "Rethinking Scientific Discovery in the
  Agentic Era" and "What LLM Agents Say When No One Is Watching" are
  known to be July 2026 (from their arXiv ID prefix) but their exact
  day was not resolved from available sources; the DeepMind "Conjecture
  Machines" piece's date is recorded as "approximate, circa mid-July
  2026" per an indexed secondary source's own wording. Each caveat is
  machine-visible in the capture's own `date` field, not hidden — the
  same honesty precedent `reality-sensor`'s `RS-0008` set for its own
  date-uncertain research signal.
- **One author list is incomplete.** "REAL: A Reasoning-Enhanced Graph
  Framework for Long-Term Memory Management of LLMs" lists only its
  first author ("Keer Lu, et al.") — the full author list was not
  resolved from available search results within this pass's budget.

## Data Quality

- **No real duplicate cluster occurred in this capture window.** All 7
  real captures produced 7 distinct clusters — an honest property of
  this particular 30-day window's real papers, not evidence that
  duplicate detection doesn't work; `test_dedup.py` proves the merge
  behavior directly against synthetic data designed to exercise it.
- **No cross-run corroboration was possible in this validation pass.**
  Because the 3x-repeated-execution proof intentionally re-processes
  the *same* fixed raw-captures file, no signal had the chance to
  accumulate a second, independent piece of evidence across real runs
  on different days. `registry.py::upsert`'s evidence-growth logic is
  unit-tested directly (`test_registry.py`) but not yet observed
  accumulating real evidence over real elapsed time.
- **`RES-0006`'s source URL is a `/public-policy/` path, not the
  registered `Google DeepMind Research Blog` root path.** Kept under
  the existing `Google DeepMind Research Blog` source name rather than
  added as a new entry, since it is the same publisher — see
  `docs/SOURCE-REGISTRY.md`. A human may prefer a more specific source
  entry for DeepMind's public-policy content in a future config edit.

## Governance

- **`config/relevance-gate.json`'s keyword mapping is a first-draft
  heuristic**, built the same way `reality-sensor`'s own relevance gate
  was — grounded in each project's available README/state content, not
  a deep review of real current priorities. A human familiar with each
  project should review it before treating `affected_projects` as
  authoritative. In this real run, all 6 registered signals' project
  matches read as substantively correct on inspection, but this is not
  a substitute for that review.

## Unknown

- Whether `arxiv.org`, `deepmind.google`, and `alignment.anthropic.com`
  remain blocked to `WebFetch` on a future capture pass is, honestly,
  unverified — bot-protection policies on these domains can change
  without notice, the same caveat `reality-sensor` names for its own
  blocked domains.
