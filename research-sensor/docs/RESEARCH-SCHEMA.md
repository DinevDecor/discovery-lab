# Research Signal Schema

The authoritative implementation is `src/research_sensor/models.py` —
this document exists so a human can read the shape without reading
Python. Field names and vocabularies implement `EXEC-010`'s own
14-field Research Signal Model exactly.

## `ResearchSignal` (the 14 named fields)

| Field | Type | Meaning |
|---|---|---|
| `research_id` | str | Persistent `RES-000N` identifier, assigned once, reused on re-processing |
| `title` | str | The strongest supporting paper's title (see "which capture is `primary`" below) |
| `authors` | list[str] | The strongest supporting paper's authors |
| `publication` | str | Venue name, e.g. `arXiv`, `Google DeepMind (public policy)` |
| `date` | str | The strongest supporting paper's own date, as captured |
| `domain` | str | One of the 5 `Domain` values (A–E) |
| `problem_addressed` | str | FACT: what problem the paper targets |
| `main_contribution` | str | FACT: what the paper actually did |
| `evidence_level` | str | `EvidenceLevel` of the strongest supporting citation |
| `affected_projects` | list[str] | `Project.NAMED` members this signal was gated to, or `[Project.WATCH]` |
| `possible_experiments` | list[`PossibleExperiment`] | Only populated for high-value, non-`WATCH` signals — see `EXPERIMENT-EXTRACTION-POLICY.md` |
| `architectural_relevance` | str | INTERPRETATION: why this might matter to Discovery Lab |
| `confidence` | str | One of `HIGH`/`MEDIUM`/`LOW`/`INSUFFICIENT_EVIDENCE` |
| `recommended_action` | str | Always advisory prose; never an instruction to build, merge, or deploy |

Two bookkeeping additions beyond the 14 named fields, both required to
satisfy EXEC-010's own PASS criterion "research provenance is
preserved":

- `evidence: list[Citation]` — every capture that supports this signal,
  each carrying its own `title`/`authors`/`publication`/`date`/
  `source_url`/`source_trust`/`evidence_level`/`quoted_abstract`. This
  is the FACT/EVIDENCE layer; `architectural_relevance` and
  `recommended_action` are the only INTERPRETATION fields on the
  record, and they are structurally distinct dataclass fields, never
  merged into `evidence`.
- `key`, `first_seen`, `last_seen`, `times_seen` — internal, not part
  of the public schema `EXEC-010` names, used only by `registry.py`'s
  idempotent upsert.

## `RawPaperCapture` (input, before interpretation)

The FACT/CLAIM stage a capture step produces — see `ARCHITECTURE.md`.
Never appears in the Research Signal Registry itself; `registry.py`
consumes a cluster of these and emits one `ResearchSignal`. Required
fields: `title`, `authors`, `publication`, `date`, `source_name`,
`source_url`, `source_trust`, `evidence_level`, `domain`,
`raw_abstract`, `problem_addressed`, `main_contribution`. Optional:
`idea_keywords` (clustering + relevance input),
`architectural_relevance_note` (capture-time judgment), and
`possible_experiment_notes` (see `EXPERIMENT-EXTRACTION-POLICY.md`).

## Which capture becomes `primary`

When a cluster has more than one capture (multiple papers supporting
the same research idea), `registry.py::_strongest` picks the capture
with the highest-ranked `evidence_level`
(`PEER_REVIEWED_PUBLISHED` > `PEER_REVIEWED_ACCEPTED` >
`NOTABLE_LAB_PREPRINT` > `PREPRINT` > `COMMUNITY_HINT` > `UNKNOWN`, tie
broken by title) to supply the signal's own `title`/`authors`/
`publication`/`date`/`problem_addressed`/`main_contribution`/
`architectural_relevance_note`. Every capture in the cluster still
contributes a `Citation` to `evidence`, regardless of which one was
`primary`.

## The 5 Primary Observation Domains

`AI_FOR_SCIENTIFIC_DISCOVERY`, `MULTI_AGENT_RESEARCH`,
`KNOWLEDGE_SYSTEMS`, `VALIDATION_METHODOLOGY`,
`COGNITIVE_ARCHITECTURES` — closed by design, matching `EXEC-010`'s
Domains A–E exactly. See `SOURCE-REGISTRY.md` for each source's
`domain_hint`.
