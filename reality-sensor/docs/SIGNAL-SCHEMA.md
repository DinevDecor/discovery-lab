# Signal Schema

Implements `EXEC-008`'s own Signal Model and Evidence Discipline
sections exactly — this document does not invent fields, it specifies
the 13 the task names plus the internal bookkeeping fields the
idempotent registry needs.

## The Signal (13 required fields + bookkeeping)

| Field | Type | Meaning |
|---|---|---|
| `signal_id` | `str` | `RS-000N`, persistent across runs (see "Stable IDs" in `docs/VALIDATION-REPORT.md`) |
| `timestamp` | `str` (ISO-8601 UTC) | first-seen time |
| `source` | `str` | primary source name (the highest-trust member of the cluster this Signal was built from) |
| `source_trust` | `str` | `TrustLevel` of the primary source |
| `category` | `str` | one of the 4 Initial Observation Domains |
| `affected_capability` | `str` | short, factual label for what changed |
| `affected_projects` | `list[str]` | 1+ of the 5 named projects, or exactly `["WATCH"]` |
| `evidence` | `list[Evidence]` | 1+ citable entries — see below; 0 forces `confidence = INSUFFICIENT_EVIDENCE` |
| `summary` | `str` | this tool's own structured one-line summary — INTERPRETATION, never FACT |
| `practical_impact` | `str` | this tool's own assessment of why it might matter — INTERPRETATION |
| `confidence` | `str` | `HIGH` / `MEDIUM` / `LOW` / `INSUFFICIENT_EVIDENCE` — see `docs/TRUST-POLICY.md` |
| `urgency` | `str` | `HIGH` / `MEDIUM` / `LOW` |
| `recommended_action` | `str` | ACTION stage — always advisory prose, never an instruction this tool or anything downstream executes |

Bookkeeping fields (not part of `EXEC-008`'s own 13, needed for the
idempotent registry): `key` (internal dedup key), `first_seen`,
`last_seen`, `times_seen`.

## Evidence

| Field | Type | Meaning |
|---|---|---|
| `source_name` | `str` | |
| `source_url` | `str` | |
| `source_trust` | `str` | `TrustLevel` |
| `quoted_text` | `str` | the source's own words — never edited, never merged with interpretation |

## Raw Capture (capture-time input, never appears in the Signal Registry)

The shape the capture step (see `ARCHITECTURE.md`) must produce, one
entry per fetched source, before any clustering or scoring:

| Field | Required | Meaning |
|---|---|---|
| `source_name` | yes | |
| `source_url` | yes | |
| `source_trust` | yes | the capturer's own classification — the Source Registry has final say (see `docs/TRUST-POLICY.md`'s "Source validation") |
| `category` | yes | one of the 4 domains |
| `captured_at` | yes | ISO-8601 UTC, when the capture step actually fetched this |
| `title` | yes | |
| `raw_text` | yes | a real quote from the source — FACT/EVIDENCE stage, never invented |
| `affected_capability` | yes | short factual label |
| `capability_keywords` | no (default `[]`) | used for clustering — see "Duplicate Detection" below |
| `practical_impact_note` | no (default `""`) | the capture step's own factual note on why this might matter, kept in a separate field from `raw_text` so a verbatim quote is never confused with judgment |

## Evidence Discipline: FACT -> CLAIM -> EVIDENCE -> INTERPRETATION -> ACTION

`EXEC-008`: "Strict separation... Never merge these." This schema
enforces the separation structurally, not just by convention:

- **FACT / CLAIM / EVIDENCE** live in `RawCapture.raw_text` and,
  downstream, `Evidence.quoted_text` — always the source's own words.
- **INTERPRETATION** lives in `Signal.summary` and
  `Signal.practical_impact` — this tool's own structured judgment,
  never copied into an `Evidence.quoted_text` field.
  `tests/test_registry.py::TestFactVsInterpretationSeparation` asserts
  this directly: no `Evidence.quoted_text` ever contains a Signal's
  own `summary` or `recommended_action` text.
- **ACTION** lives in `Signal.recommended_action` — always advisory
  prose ("a human should review..."), never an instruction this tool
  or anything downstream executes. Enforced by `CONTRACT.md`'s Read-
  only Rules and `tests/test_safety.py`'s static scan for any action-
  taking call.

## Duplicate Detection

Two Raw Captures cluster into one Signal if they share `category` and
have at least one case-insensitive `capability_keywords` overlap;
clustering is transitive (see `dedup.py`). All Evidence from every
member of a cluster is attached to the resulting single Signal - never
one Signal per article about the same event.
