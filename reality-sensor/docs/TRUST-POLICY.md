# Trust Policy

## Source Trust Levels

`EXEC-008`'s closed vocabulary — every source must be classified as
exactly one of these, never left blank, never inferred at process
time (the Trust Level is fixed per source in
`config/source-registry.json`, or, for a source not yet in that
registry, whatever the capture step recorded, flagged as unconfirmed —
see "Source validation" below):

| Level | Meaning | Example (from `config/source-registry.json`) |
|---|---|---|
| `PRIMARY` | The vendor's own definitive technical artifact — a changelog, spec, or release notes page | `code.claude.com/docs/en/changelog`, `modelcontextprotocol.io/specification/` |
| `OFFICIAL` | An official company blog/news post | `openai.com/news/`, `github.blog/` |
| `RESEARCH` | A peer-reviewed or preprint research artifact | `arxiv.org`, `openreview.net` |
| `SECONDARY` | Independent, professional tech journalism reporting on a primary event | TechCrunch, Axios, The Register |
| `COMMUNITY` | Forums, social media, unmoderated discussion | (none in the fixed initial list — see `docs/SOURCE-REGISTRY.md`) |
| `UNKNOWN` | Classification not yet possible | assigned only when a capture cites a source absent from the Registry and the capturer did not classify it |

## Confidence Rules

`EXEC-008`, verbatim: "Confidence depends on evidence. Not popularity.
Not excitement. Not marketing." Implemented in `trust.py`'s
`assess_confidence`, a pure function of the Trust Levels of a Signal's
attached Evidence — nothing else (not the number of sources, not the
category, not urgency):

1. **Zero evidence -> `INSUFFICIENT_EVIDENCE`.** A Signal cannot be
   built without at least one Evidence entry in the first place, but
   the rule is stated explicitly and tested (`tests/test_registry.py::
   TestEvidenceEnforcement`).
2. **Any `PRIMARY` or `OFFICIAL` evidence present -> `HIGH`.**
3. **Otherwise, any `RESEARCH` or `SECONDARY` evidence present ->
   `MEDIUM`.** A single preprint or news report is a real claim, not
   yet independently corroborated by the vendor itself.
4. **`COMMUNITY`-only or `UNKNOWN`-only evidence -> `LOW`, never
   `HIGH`.** This is the one rule `EXEC-008` states explicitly: "Never
   assign HIGH confidence from COMMUNITY alone." Note the word
   "alone" — `COMMUNITY` evidence alongside a `PRIMARY` source for the
   same event still supports `HIGH` (rule 2 already covers this; rule
   4 only fires when `COMMUNITY`/`UNKNOWN` is *all* there is).

On re-processing (idempotent upsert, `registry.py`), confidence can
only improve as new corroborating evidence arrives - it is never
silently downgraded once established.

## Urgency

How soon a human should look at a signal, not how exciting it is —
`trust.py`'s `assess_urgency`, a small, transparent, fully documented
heuristic (mirroring the Attention Engine's own "fully shown rubric"
discipline in `headquarters/src/headquarters/prioritizer.py`):

- Any of a short list of high-urgency keywords (`deprecat`, `sunset`,
  `breaking change`, `end of life`, `security`, `vulnerability`,
  `shutdown`) appearing anywhere in the Signal's own capability/
  summary/impact text -> `HIGH`, regardless of confidence.
- `INSUFFICIENT_EVIDENCE` confidence -> always `LOW` (nothing
  unconfirmed is ever flagged urgent).
- A preprint/workshop/position-paper hint in the text -> `LOW`.
- `HIGH` confidence with none of the above -> `MEDIUM`.
- Everything else -> `LOW`.

## Source validation

Every raw capture is checked against `config/source-registry.json`
before it can contribute to a Signal (`cli.py::run_once`):

- A capture citing a `source_name`/`source_url` **not** in the
  Registry is kept (this sensor does not silently discard real
  evidence) but flagged in the run's validation warnings — its trust
  level is whatever the capturer recorded, not independently
  confirmed.
- A capture whose claimed `source_trust` **disagrees** with the
  Registry's own classification for that source is corrected — the
  Registry's value wins, and the disagreement is flagged in the run's
  validation warnings, never silently overridden without a trace.
