# Trust Policy

Two independent classifications exist in this sensor, deliberately not
merged into one — see `models.py`'s own docstring on `SourceTrust` vs
`EvidenceLevel`.

## Source Trust (where a capture came from)

`EXEC-010`'s own priority order, closed vocabulary:

| Level | Meaning | Example |
|---|---|---|
| `PRIMARY` | arXiv, OpenReview, Nature, Science, ACL, NeurIPS, ICML, ICLR | `arxiv.org/list/cs.AI/recent` |
| `SECONDARY` | Official research blogs, laboratory publications | `deepmind.google/...`, `anthropic.com/research` |
| `COMMUNITY` | Discovery hints only | Hacker News, r/MachineLearning |

A source's Trust is fixed in `config/source-registry.json`, not
inferred at process time. See "Source validation" below for what
happens when a capture disagrees with the Registry.

## Evidence Level (the paper's own evidentiary strength)

Closed vocabulary, independent of which source reported it — a
`PRIMARY`-source (arXiv) capture is very often still just a
`PREPRINT`:

| Level | Meaning |
|---|---|
| `PEER_REVIEWED_PUBLISHED` | Published in a peer-reviewed venue (Nature, Science, a journal) |
| `PEER_REVIEWED_ACCEPTED` | Accepted at a peer-reviewed venue (ACL/NeurIPS/ICML/ICLR) |
| `NOTABLE_LAB_PREPRINT` | A preprint or official publication from a recognized research lab |
| `PREPRINT` | A preprint not independently placed at a recognized lab |
| `COMMUNITY_HINT` | A mention only — never itself citable evidence for a signal |
| `UNKNOWN` | Classification not yet possible |

## Confidence Rules

`EXEC-010`, verbatim: "Confidence depends on: publication quality, peer
review status, independent replication, evidence strength. Never on
popularity." Implemented in `trust.py::assess_confidence`, a pure
function of a cluster's `EvidenceLevel`s and how many independently
notable-or-better sources corroborate:

1. **No evidence at all → `INSUFFICIENT_EVIDENCE`.**
2. **All evidence is `COMMUNITY_HINT`/`UNKNOWN` → `INSUFFICIENT_EVIDENCE`,
   and the signal is never accepted at all** — this is stricter than
   `reality-sensor`'s "never `HIGH` from `COMMUNITY` alone"; here
   `registry.py::build_signal` returns `None` for such a cluster and
   `cli.py` counts it as a `discovery_hints_skipped` hint, never a
   registered signal. See `can_accept_signal`.
3. **Any `PEER_REVIEWED_PUBLISHED`/`PEER_REVIEWED_ACCEPTED` evidence →
   `HIGH`**, regardless of count.
4. **`NOTABLE_LAB_PREPRINT` evidence, with ≥2 independently notable-
   or-better sources corroborating → `HIGH`.**
5. **A single `NOTABLE_LAB_PREPRINT` → `MEDIUM`**, never `HIGH` alone —
   one lab's own preprint is a real claim, not yet independently
   corroborated.
6. **`PREPRINT`-only evidence → `LOW`**, regardless of how many
   preprints (count alone never substitutes for evidence quality — see
   `test_trust.py::test_never_depends_on_count_alone_for_low_tier_evidence`).

On re-processing (idempotent upsert, `registry.py::upsert`), confidence
can only improve as new corroborating evidence arrives — it is never
silently downgraded once established.

## Source validation

Every raw capture is checked against `config/source-registry.json`
before it can contribute to a signal (`cli.py::run_once`):

- A capture citing a `source_name` **not** in the Registry is kept
  (real evidence is never silently discarded) but flagged in the run's
  `validation_warnings`.
- A capture whose claimed `source_trust` **disagrees** with the
  Registry's own classification for that source is corrected — the
  Registry's value wins, and the disagreement is flagged, never
  silently overridden without a trace.
