# Trust Engine Phase 1 Prediction Reviews Migration Report

## Summary

| Field | Value |
| --- | --- |
| Database | trust_engine.db |
| Timestamp | 2026-06-18T09:24:17 |
| Mode | apply |
| Overall status | PASS |
| Committed | True |
| Backup | backups\trust_engine_phase1_schema_backup_20260618_092417.db |
| Checks | 84 |
| Failed checks | 0 |

## Slice A Validation Checks

| Result | Check | Details |
| --- | --- | --- |
| PASS | Database exists | path=trust_engine.db |
| PASS | Backup reminder | Before schema creation, verify a timestamped backup exists. --apply also creates a new backup. |
| PASS | models table exists | existing=['context_tags', 'contexts', 'decision_outcomes', 'decisions', 'domains', 'error_profiles', 'models', 'prediction_context_tags', 'prediction_reviews', 'predictions', 'score_snapshots', 'sqlite_sequence', 'trust_memory', 'trust_scores'] |
| PASS | trust_memory table exists | existing=['context_tags', 'contexts', 'decision_outcomes', 'decisions', 'domains', 'error_profiles', 'models', 'prediction_context_tags', 'prediction_reviews', 'predictions', 'score_snapshots', 'sqlite_sequence', 'trust_memory', 'trust_scores'] |
| PASS | decisions table exists | existing=['context_tags', 'contexts', 'decision_outcomes', 'decisions', 'domains', 'error_profiles', 'models', 'prediction_context_tags', 'prediction_reviews', 'predictions', 'score_snapshots', 'sqlite_sequence', 'trust_memory', 'trust_scores'] |
| PASS | models contains M1 | model_ids=['M1', 'M2', 'M3', 'M4'] |
| PASS | models contains M2 | model_ids=['M1', 'M2', 'M3', 'M4'] |
| PASS | models contains M3 | model_ids=['M1', 'M2', 'M3', 'M4'] |
| PASS | models contains M4 | model_ids=['M1', 'M2', 'M3', 'M4'] |
| PASS | Domains in models are populated | blank_domain_rows=[] |
| PASS | memory_id 3 and 5 exist | found=[3, 5] |
| PASS | Eligible migration rows count | eligible_count=3 |
| PASS | Eligible rows have valid model references | rows=[] |
| PASS | Eligible rows have non-blank predictions | rows=[] |
| PASS | Eligible rows have non-blank contexts | rows=[] |
| PASS | decisions count = 0 | decisions_count=0 |

## Schema Operations

| Executed | Operation | Details |
| --- | --- | --- |
| True | create table domains | CREATE TABLE IF NOT EXISTS |
| True | create table contexts | CREATE TABLE IF NOT EXISTS |
| True | create table context_tags | CREATE TABLE IF NOT EXISTS |
| True | create table predictions | CREATE TABLE IF NOT EXISTS |
| True | create table prediction_context_tags | CREATE TABLE IF NOT EXISTS |
| True | create table prediction_reviews | CREATE TABLE IF NOT EXISTS |
| True | create table error_profiles | CREATE TABLE IF NOT EXISTS |
| True | create table decision_outcomes | CREATE TABLE IF NOT EXISTS |
| True | create table trust_scores | CREATE TABLE IF NOT EXISTS |
| True | create table score_snapshots | CREATE TABLE IF NOT EXISTS |

## Schema Validation Checks

| Result | Check | Details |
| --- | --- | --- |
| PASS | context_tags table exists | existing=True |
| PASS | contexts table exists | existing=True |
| PASS | decision_outcomes table exists | existing=True |
| PASS | domains table exists | existing=True |
| PASS | error_profiles table exists | existing=True |
| PASS | prediction_context_tags table exists | existing=True |
| PASS | prediction_reviews table exists | existing=True |
| PASS | predictions table exists | existing=True |
| PASS | score_snapshots table exists | existing=True |
| PASS | trust_scores table exists | existing=True |
| PASS | models.provider column exists | columns=['active', 'created_at', 'description', 'domain', 'model_id', 'name', 'provider', 'version'] |
| PASS | models.version column exists | columns=['active', 'created_at', 'description', 'domain', 'model_id', 'name', 'provider', 'version'] |
| PASS | models.active column exists | columns=['active', 'created_at', 'description', 'domain', 'model_id', 'name', 'provider', 'version'] |
| PASS | decisions.context_id column exists | columns=['candidate_models', 'context', 'context_id', 'decision_date', 'decision_id', 'notes', 'objective', 'outcome', 'reason', 'selected_model', 'selected_model_id', 'selected_trust_score', 'selection_reason', 'status'] |
| PASS | decisions.selected_model_id column exists | columns=['candidate_models', 'context', 'context_id', 'decision_date', 'decision_id', 'notes', 'objective', 'outcome', 'reason', 'selected_model', 'selected_model_id', 'selected_trust_score', 'selection_reason', 'status'] |
| PASS | decisions.selection_reason column exists | columns=['candidate_models', 'context', 'context_id', 'decision_date', 'decision_id', 'notes', 'objective', 'outcome', 'reason', 'selected_model', 'selected_model_id', 'selected_trust_score', 'selection_reason', 'status'] |
| PASS | decisions.selected_trust_score column exists | columns=['candidate_models', 'context', 'context_id', 'decision_date', 'decision_id', 'notes', 'objective', 'outcome', 'reason', 'selected_model', 'selected_model_id', 'selected_trust_score', 'selection_reason', 'status'] |
| PASS | decisions.status column exists | columns=['candidate_models', 'context', 'context_id', 'decision_date', 'decision_id', 'notes', 'objective', 'outcome', 'reason', 'selected_model', 'selected_model_id', 'selected_trust_score', 'selection_reason', 'status'] |
| PASS | domains expected columns exist | missing=none |
| PASS | contexts expected columns exist | missing=none |
| PASS | context_tags expected columns exist | missing=none |
| PASS | predictions expected columns exist | missing=none |
| PASS | prediction_context_tags expected columns exist | missing=none |
| PASS | prediction_reviews expected columns exist | missing=none |
| PASS | error_profiles expected columns exist | missing=none |
| PASS | decision_outcomes expected columns exist | missing=none |
| PASS | trust_scores expected columns exist | missing=none |
| PASS | score_snapshots expected columns exist | missing=none |
| PASS | context_tags has no migrated data yet | count=0 |
| PASS | prediction_context_tags has no migrated data yet | count=0 |
| PASS | error_profiles has no migrated data yet | count=0 |
| PASS | decision_outcomes has no migrated data yet | count=0 |
| PASS | trust_scores has no migrated data yet | count=0 |
| PASS | score_snapshots has no migrated data yet | count=0 |

## Domain Operations

| Executed | Operation | Details |
| --- | --- | --- |
| True | insert domain AI Infrastructure | already existed |
| True | insert domain Constraints | already existed |
| True | insert domain General | already existed |
| True | insert domain Liquidity | already existed |
| True | insert domain Markets | already existed |

## Domain Validation Checks

| Result | Check | Details |
| --- | --- | --- |
| PASS | expected domains exist | missing=none, actual=['AI Infrastructure', 'Constraints', 'General', 'Liquidity', 'Markets'] |
| PASS | domains have no duplicate names | duplicates=none |
| PASS | all distinct models.domain values exist in domains | missing=none, model_domains=['AI Infrastructure', 'Constraints', 'Liquidity', 'Markets'] |
| PASS | context_tags still has no migrated data | count=0 |
| PASS | prediction_context_tags still has no migrated data | count=0 |
| PASS | error_profiles still has no migrated data | count=0 |
| PASS | decision_outcomes still has no migrated data | count=0 |
| PASS | trust_scores still has no migrated data | count=0 |
| PASS | score_snapshots still has no migrated data | count=0 |

## Context Operations

| Executed | Operation | Details |
| --- | --- | --- |
| True | insert context for trust_memory 1 | already existed |
| True | insert context for trust_memory 2 | already existed |
| True | insert context for trust_memory 4 | already existed |

## Context Validation Checks

| Result | Check | Details |
| --- | --- | --- |
| PASS | contexts count = 3 | count=3 |
| PASS | no contexts for memory_id 3 or 5 | rows=[] |
| PASS | no duplicate contexts by source_table/source_id | rows=[] |
| PASS | all eligible trust_memory rows have contexts | rows=[] |
| PASS | context field mappings are correct | rows=[] |
| PASS | error_profiles still has no migrated data | count=0 |
| PASS | trust_scores still has no migrated data | count=0 |
| PASS | score_snapshots still has no migrated data | count=0 |

## Prediction Operations

| Executed | Operation | Details |
| --- | --- | --- |
| True | insert prediction for trust_memory 1 | already existed |
| True | insert prediction for trust_memory 2 | already existed |
| True | insert prediction for trust_memory 4 | already existed |

## Prediction Validation Checks

| Result | Check | Details |
| --- | --- | --- |
| PASS | predictions count = 3 | count=3 |
| PASS | no predictions for memory_id 3 or 5 | rows=[] |
| PASS | no duplicate predictions by legacy_memory_id | rows=[] |
| PASS | all eligible trust_memory rows have predictions | rows=[] |
| PASS | prediction field mappings are correct | rows=[] |
| PASS | error_profiles still has no migrated data | count=0 |
| PASS | trust_scores still has no migrated data | count=0 |
| PASS | score_snapshots still has no migrated data | count=0 |

## Prediction Review Operations

| Executed | Operation | Details |
| --- | --- | --- |
| True | insert prediction review for trust_memory 1 | inserted |

## Prediction Review Validation Checks

| Result | Check | Details |
| --- | --- | --- |
| PASS | prediction_reviews count matches closed eligible rows | count=1, expected=1 |
| PASS | no prediction reviews for memory_id 3 or 5 | rows=[] |
| PASS | no duplicate prediction reviews by legacy_memory_id | rows=[] |
| PASS | all closed eligible trust_memory rows have prediction reviews | rows=[] |
| PASS | only closed predictions receive reviews | rows=[] |
| PASS | prediction review field mappings are correct | rows=[] |
| PASS | error_profiles still has no migrated data | count=0 |
| PASS | trust_scores still has no migrated data | count=0 |
| PASS | score_snapshots still has no migrated data | count=0 |

## Notes

- Slice F creates schema if missing, migrates domains, contexts, predictions, and prediction reviews only.
- Domains are inserted idempotently with duplicate protection.
- Contexts are inserted idempotently with UNIQUE(source_table, source_id).
- Predictions are inserted idempotently with UNIQUE(legacy_memory_id).
- Prediction reviews are inserted idempotently with UNIQUE(legacy_memory_id).
- Open predictions do not receive reviews.
- No error profiles were inserted.
- No trust scores or score snapshots were inserted.
