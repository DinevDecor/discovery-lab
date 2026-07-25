# Known Limitations — Reality Intelligence Sensor 001

Documented scope boundaries and honestly-observed weaknesses, not bugs
to be silently tightened away — consistent with how `observation-agent/
README.md` and `headquarters/README.md` already treat this section for
their own tools.

## Architectural

- **This sensor cannot fetch the internet itself.** Its checked-in
  source is, by design and by test (`tests/test_safety.py`), 100%
  network-free. It depends entirely on a human or AI executor
  performing the capture step and supplying a well-formed raw-captures
  file. If no one performs that step, the sensor produces nothing —
  it does not "continuously observe" on its own in any automated
  sense. Turning this into a truly unattended, scheduled sensor (the
  way Observation Agent is scheduled via GitHub Actions) would require
  a separate, later, human-authorized decision about *how* the capture
  step itself gets automated (e.g., a scheduled job with its own
  narrowly-scoped, read-only fetch capability and its own safety
  review) — explicitly not attempted here.
- **Confidence/urgency/relevance scoring is a function of the capture
  step's own annotations** (`affected_capability`,
  `capability_keywords`, `practical_impact_note`), not of the raw
  article text directly. This is a deliberate design choice (see
  `ARCHITECTURE.md`) that keeps the checked-in pipeline deterministic
  and testable, but it means the *quality* of every Signal depends on
  the judgment of whoever performed capture — the same dependency
  Observation Agent has on its own check functions' regex precision,
  made explicit rather than hidden.

## Operational

- **Real capture in this task's own validation pass hit 3 blocked
  fetches**: `anthropic.com/news`, `openai.com` (both the news page and
  the Agents SDK announcement), and `arxiv.org/list/cs.AI/recent` all
  returned `HTTP 403` to direct `WebFetch` calls — common bot
  protection on those domains. Evidence for Anthropic's and OpenAI's
  releases was still gathered (via `WebSearch`'s own synthesis, citing
  real tech-journalism URLs, correctly classified `SECONDARY` rather
  than `OFFICIAL`/`PRIMARY` as a result) and one genuinely `PRIMARY`
  source was reached directly (`code.claude.com/docs/en/changelog`),
  but a future capture pass should expect the same blocks and budget
  for them.
- **The Domain D (Research) capture's freshness is unverified.**
  `arxiv.org` blocked direct fetch, and arXiv's own `YYMM`-prefixed ID
  convention could not be cross-checked against this environment's
  simulated current date with confidence. The one research signal in
  the validation dataset (`RS-0008`) carries an explicit,
  machine-visible caveat in its `practical_impact_note` rather than a
  false precision claim — and its `RESEARCH` trust level already caps
  its confidence at `MEDIUM`, which honestly reflects this
  uncertainty rather than compounding it.

## Governance

- **`config/relevance-gate.json`'s keyword mapping is a first-draft
  heuristic**, grounded in what little of each project's own charter
  was actually available (`generative-discovery-engine/README.md`'s
  stated Mission; `kod/Core/Registry/PROJECT_STATE.md`'s field
  labels; `trust-engine/`'s file listing, which suggests investment/
  decision-trust scoring rather than LLM-safety trust) — not a deep
  review of any project's real priorities. A human familiar with each
  project should review and correct `config/relevance-gate.json`
  before treating its `affected_projects` output as authoritative.
- **Naive substring keyword matching can self-trigger.** During real
  validation, a signal's own `practical_impact_note` mentioning
  "Trust Engine's... interests" caused the `relevance` gate to match
  Trust Engine via the literal substring `"trust"` — a legitimate
  match by the letter of the rule, but a reminder that the current
  heuristic matches *words*, not *meaning*. It never fabricates a
  match where the keyword doesn't literally appear, but it can also
  match on incidental phrasing. Documented here rather than quietly
  tuned away, matching Observation Agent's own precedent for naming
  a real false-positive risk rather than hiding it.
- **`code.claude.com/docs/en/changelog` is not yet in
  `config/source-registry.json`**, despite being the single most
  useful `PRIMARY` source found during validation — see `docs/
  SOURCE-REGISTRY.md`'s own note. Adding it is a routine config edit,
  left to a human rather than done unilaterally mid-task.

## Data Quality

- **No cross-run corroboration was possible in this validation pass.**
  Because the 3x-repeated-execution proof intentionally re-processes
  the *same* fixed raw-captures file (to prove determinism), no signal
  in the validation dataset had the chance to accumulate a second,
  independent piece of evidence across real runs on different days.
  The idempotent-upsert and evidence-growth logic (`registry.py::
  upsert`) is unit-tested directly (`tests/test_registry.py::
  TestStableIds`), but has not yet been observed accumulating real
  evidence over real elapsed time.

## Unknown

- Whether the 7 sources actually reachable in this validation pass
  (`code.claude.com`, `blog.modelcontextprotocol.io`,
  `github.blog`, plus the tech-journalism secondary sources) remain
  reachable on a future capture pass is, honestly, unverified —
  bot-protection policies on these domains can change without notice.
