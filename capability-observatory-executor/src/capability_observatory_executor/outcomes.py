"""Executor-side view of C3's capture-outcome vocabulary.

The vocabulary itself lives in one place only:
capability_observatory.models.CAPTURE_OUTCOMES (extended in Slice 03 --
see docs/decisions/003-c3-capture-outcome-vocabulary-extended.md). This
module never redefines that list; it only groups it for the executor's own
routing decisions (does this outcome mean "try automation", "this needs a
human", or "this is infrastructure noise, not evidence of anything about
the provider")without ever inventing a second vocabulary.
"""

from __future__ import annotations

from capability_observatory.models import (
    CAPTURE_OUTCOMES,
    OBSERVATION_PRODUCING_OUTCOMES,
)

#: Outcomes that mean "the executor's own path failed before we learned
#: anything about the provider." These must never be read as evidence the
#: provider is unreachable or hostile -- see Section 9 of the Slice 03
#: design doc. A run dominated by these outcomes is an executor bug or an
#: environment problem, not a capture-mechanism-vs-domain finding.
EXECUTOR_SIDE_OUTCOMES = (
    "executor_network_blocked",
    "timeout",
    "credentials_error",
    "api_quota_error",
)

#: Outcomes that mean the provider was reached and it, specifically, denied
#: or could not serve the request.
PROVIDER_SIDE_OUTCOMES = (
    "provider_access_blocked",
    "parse_error",
    "source_missing",
)

#: access_blocked is legacy and deliberately excluded from both buckets
#: above -- it predates the split and cannot be reclassified without
#: rewriting historical records (forbidden). Callers that need to bucket a
#: legacy record should read its `notes` field, not guess from the outcome
#: alone.
LEGACY_AMBIGUOUS_OUTCOMES = ("access_blocked",)


def is_executor_side_failure(capture_outcome: str) -> bool:
    return capture_outcome in EXECUTOR_SIDE_OUTCOMES


def is_provider_side_failure(capture_outcome: str) -> bool:
    return capture_outcome in PROVIDER_SIDE_OUTCOMES


def is_legacy_ambiguous(capture_outcome: str) -> bool:
    return capture_outcome in LEGACY_AMBIGUOUS_OUTCOMES


def is_success(capture_outcome: str) -> bool:
    return capture_outcome in OBSERVATION_PRODUCING_OUTCOMES


assert set(EXECUTOR_SIDE_OUTCOMES) | set(PROVIDER_SIDE_OUTCOMES) | set(LEGACY_AMBIGUOUS_OUTCOMES) | set(
    OBSERVATION_PRODUCING_OUTCOMES
) == set(CAPTURE_OUTCOMES), "every C3 capture outcome must be classified exactly once here"
