# Source Registry (human-readable)

The authoritative, machine-readable copy is `config/source-registry.json`
— this document exists only so a human can read the same list without
parsing JSON. Add or remove a source by editing the config file;
nothing in the code needs to change.

`processing_budget: 30`, `window_days: 30` — the fixed cap on
fetch/search operations a single capture pass may use, and the fixed
lookback window `EXEC-010`'s own Validation Dataset section names
("last 30 days"). This task's own real validation capture used 14 real
operations (12 `WebSearch` + 2 attempted `WebFetch`, both of which were
blocked with HTTP 403 — see `docs/KNOWN-LIMITATIONS.md`), well inside
budget.

## PRIMARY

| Source | Domain hint |
|---|---|
| arXiv cs.AI Recent | A |
| arXiv cs.CL Recent | C |
| arXiv cs.MA Recent | B |
| arXiv cs.LG Recent | E |
| OpenReview | D |
| Nature | A |
| Science | A |
| ACL Anthology | C |
| NeurIPS Proceedings | E |
| ICML Proceedings | D |
| ICLR Proceedings (OpenReview) | E |

## SECONDARY

| Source | Domain hint |
|---|---|
| Google DeepMind Research Blog | A |
| OpenAI Research | E |
| Anthropic Research | D |
| Microsoft Research Blog | C |

## COMMUNITY (discovery hint only)

| Source |
|---|
| Hacker News |
| r/MachineLearning |

## Sources actually used in this task's real validation pass

All 7 real captures in
`validation-dataset/raw-captures-2026-06-25-to-2026-07-25.json` came
from sources already in the fixed list above — `arXiv cs.AI/cs.CL/cs.MA/cs.LG
Recent`, `Google DeepMind Research Blog` (the specific URL fetched was
under `deepmind.google/public-policy/`, a sibling path to the
registered blog root — kept as `Google DeepMind Research Blog` rather
than added as a new source name, since it is the same publisher), and
`Hacker News`. No unlisted source was encountered, so
`validation_warnings` for the live run is empty — see
`docs/VALIDATION-REPORT.md`. `test_source_validation.py` exercises the
"unlisted source" and "trust mismatch" paths independently with
synthetic data, since the real capture pass did not happen to trigger
either.
