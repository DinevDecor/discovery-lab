# Outcome Tracking v1 Slice 1 Review

## Summary

Outcome Tracking v1 Slice 1 creates manual outcome recording for Decision Memory.

Core principle:

```text
Decision -> Outcome -> Experience Memory
```

This slice creates Outcome Memory only. It does not learn, update trust, modify predictions, or generate outcomes automatically.

## Files Created

| File | Purpose |
| --- | --- |
| `outcome_tracking.py` | Manual outcome recording and read helpers. |
| `outcome_tracking_review.md` | Review of schema, functions, validations, and limitations. |

No selector files were modified.

No migration scripts were modified.

## Schema Created

`outcome_tracking.py` ensures the `decision_outcomes` table exists when outcome functions are called.

Target fields:

| Field | Type | Purpose |
| --- | --- | --- |
| `outcome_id` | integer primary key | Unique outcome ID. |
| `decision_id` | integer not null | Parent decision. |
| `outcome` | text not null | Outcome category. |
| `outcome_score` | real nullable | Manual score from 0 to 100. |
| `outcome_notes` | text nullable | Human review notes. |
| `reviewed_at` | text | Review timestamp. |

Compatibility behavior:

- If `decision_outcomes` does not exist, it is created.
- If a legacy `decision_outcomes` table already exists, missing Slice 1 columns are added.
- Existing legacy columns are preserved.

## Functions Created

### `record_outcome(decision_id, outcome, outcome_score=None, notes=None, db_path="trust_engine.db")`

Records one manual outcome for an existing decision.

Returns:

```text
outcome_id
```

Allowed outcome values:

- `SUCCESS`
- `PARTIAL`
- `FAILURE`
- `UNKNOWN`

The function validates:

- `decision_id` exists in `decisions`
- `outcome` is valid
- `outcome_score` is null or between 0 and 100

### `get_outcome(outcome_id, db_path="trust_engine.db")`

Returns one outcome row as a dictionary, or `None` if not found.

### `get_outcomes_for_decision(decision_id, db_path="trust_engine.db")`

Returns all outcomes for one decision, newest first.

The function validates:

- `decision_id` exists

### `list_recent_outcomes(limit=20, db_path="trust_engine.db")`

Returns recent outcomes, newest first.

The function validates:

- `limit >= 1`

## Validations

### Decision Validation

Before recording an outcome:

```sql
SELECT decision_id
FROM decisions
WHERE decision_id = ?
```

If no row exists, `record_outcome()` raises `ValueError`.

### Outcome Category Validation

Accepted values:

```text
SUCCESS
PARTIAL
FAILURE
UNKNOWN
```

Input is normalized to uppercase.

### Outcome Score Validation

Accepted:

```text
NULL
0 <= outcome_score <= 100
```

Scores are intentionally manual in Slice 1.

The module does not auto-map categories to scores.

## Explicit Non-Goals

This slice does not implement:

- trust score updates
- score snapshots
- selector modifications
- prediction changes
- prediction review changes
- error profile changes
- learning engine
- automatic outcome generation
- automatic outcome scoring

## Protected Tables

The module does not write to:

- `trust_scores`
- `score_snapshots`
- `predictions`
- `prediction_reviews`
- `error_profiles`

The only intended write path is:

```text
decision_outcomes
```

plus table/column creation for the `decision_outcomes` audit structure when needed.

## Limitations

1. Outcome recording is manual only.
2. Multiple outcomes per decision are allowed; no final-outcome constraint exists yet.
3. Outcome scores are 0 to 100 per Slice 1 requirements, not normalized 0 to 1.
4. No foreign key constraint is added if the table already exists.
5. No trust update pipeline consumes outcomes yet.
6. No CLI is provided yet.
7. No automatic status update is made on the parent decision.
8. No outcome category-to-score mapping is enforced.

## Example Usage

```python
from outcome_tracking import record_outcome, get_outcome, get_outcomes_for_decision

outcome_id = record_outcome(
    decision_id=1,
    outcome="SUCCESS",
    outcome_score=85,
    notes="The selected model was useful for the decision.",
)

outcome = get_outcome(outcome_id)
decision_outcomes = get_outcomes_for_decision(1)
```

## Review Conclusion

Outcome Tracking v1 Slice 1 implements the minimum manual outcome memory layer:

```text
Decision
-> Outcome
-> Experience Memory
```

It creates auditable outcome records without learning, trust updates, or automatic score changes.
