# Trust Engine Database Audit Report

## Summary

| Metric | Value |
| --- | --- |
| Database path | trust_engine.db |
| Audit timestamp | 2026-06-17T14:21:49 |
| Migration readiness | Blocked |
| Total issues | 4 |
| High severity issues | 3 |
| Medium severity issues | 1 |
| Low severity issues | 0 |

## Database Metadata

| Field | Value |
| --- | --- |
| database_path | trust_engine.db |
| file_exists | True |
| file_size_bytes | 24576 |
| last_modified_timestamp | 2026-06-17T14:20:28 |
| can_open_read_only | True |
| sqlite_integrity_check | ok |

## Table Status

| Table | Status |
| --- | --- |
| models | Exists |
| trust_memory | Exists |
| decisions | Exists |

### Extra Tables

| Table |
| --- |
| sqlite_sequence |

## Schema Status

### models

| Field | Value |
| --- | --- |
| expected_columns | model_id, name, description, domain, created_at |
| actual_columns | model_id, name, description, domain, created_at |
| missing_columns | None |
| extra_columns | None |

### trust_memory

| Field | Value |
| --- | --- |
| expected_columns | memory_id, model_id, context, prediction, confidence, date_created, review_date, result, error_type, notes |
| actual_columns | memory_id, model_id, context, prediction, confidence, date_created, review_date, result, error_type, notes |
| missing_columns | None |
| extra_columns | None |

### decisions

| Field | Value |
| --- | --- |
| expected_columns | decision_id, context, objective, candidate_models, selected_model, reason, decision_date, outcome, notes |
| actual_columns | decision_id, context, objective, candidate_models, selected_model, reason, decision_date, outcome, notes |
| missing_columns | None |
| extra_columns | None |

## Row Counts

| Metric | Count |
| --- | --- |
| models count | 4 |
| trust_memory count | 5 |
| open trust_memory count | 4 |
| closed trust_memory count | 1 |
| decisions count | 0 |
| unknown result count | 0 |

## Distinct Result Values

| Result value | Count |
| --- | --- |
| Open | 4 |
| True | 1 |

## Distinct Error Types

| Error type | Count |
| --- | --- |
| NULL | 4 |
| None | 1 |

## Data Quality Issues

### Invalid Confidence Values

No issues found.

### Missing Model References

#### trust_memory rows with missing model references

| Field | Value |
| --- | --- |
| Severity | High |
| Count | 2 |
| Why it matters | Migration to predictions requires valid model references; SQLite foreign keys may not currently be enforced. |
| Recommended action | Create missing model records or correct affected trust_memory.model_id values before migration. |

Rows affected: showing 2 of 2.

| memory_id | model_id | prediction excerpt | result |
| --- | --- | --- | --- |
| 3 | М1 | EMPTY_STRING | Open |
| 5 | М1 | EMPTY_STRING | Open |

### Blank Predictions

#### Blank prediction rows

| Field | Value |
| --- | --- |
| Severity | High |
| Count | 2 |
| Why it matters | Trust Engine v1 predictions.prediction_text should be required; blank predictions cannot be meaningfully reviewed or scored. |
| Recommended action | Fill or remove blank prediction rows before migration. |

Rows affected: showing 2 of 2.

| memory_id | model_id | context excerpt | confidence | result |
| --- | --- | --- | --- | --- |
| 3 | М1 | EMPTY_STRING | 0.7 | Open |
| 5 | М1 | EMPTY_STRING | 0.7 | Open |

### Blank Contexts

#### Blank context rows

| Field | Value |
| --- | --- |
| Severity | Medium |
| Count | 2 |
| Why it matters | Trust Engine v1 is context-aware; blank contexts reduce matching and domain inference quality. |
| Recommended action | Add context text where possible before context-aware scoring. |

Rows affected: showing 2 of 2.

| memory_id | model_id | prediction excerpt | confidence | result |
| --- | --- | --- | --- | --- |
| 3 | М1 | EMPTY_STRING | 0.7 | Open |
| 5 | М1 | EMPTY_STRING | 0.7 | Open |

### Unknown Result Values

No issues found.

### Unknown Error Types

No issues found.

### Latin/Cyrillic Model ID Ambiguity

#### Latin/Cyrillic model ID ambiguity collisions

| Field | Value |
| --- | --- |
| Severity | High |
| Count | 1 |
| Why it matters | Model detection and migration can silently break if visually identical IDs are different strings. |
| Recommended action | Create an explicit canonical model ID mapping before migration. Do not auto-normalize. |

Rows affected: showing 1 of 1.

| normalized_key | original_values | source_tables | row_counts | unicode_codepoints |
| --- | --- | --- | --- | --- |
| M1 | M1, М1 | models, trust_memory | models:M1=1, trust_memory:M1=1, trust_memory:М1=2 | M1: U+004D U+0031 \| М1: U+041C U+0031 |

### Date Quality Issues

No issues found.

### Other Issues

No issues found.

## Migration Readiness

**Status:** Blocked

Readiness rules:

- Ready: no high, medium, or low severity issues were found.
- Ready with warnings: no high severity issues were found, but medium or low issues exist.
- Blocked: one or more high severity issues exist.

## Recommended Next Actions

- Resolve high severity issues before migration.
- Do not switch the app to v1 tables yet.
- Back up `trust_engine.db` before any cleanup.
- Re-run this audit after cleanup and compare reports.
