"""No secret ever reaches a written record.

Applied to every string field of an ExecutorSubmission before it is
converted to a C3 submission and written to incoming/. The check is
literal-substring, against the actual credential values read from the
environment at run time -- not a speculative pattern scan, because a
speculative scan either misses real secrets shaped differently than
expected or false-positives on ordinary hex-looking content (a hash, a
part number). Literal substring matching against the values actually in
use is the one check that can never be wrong about what a secret looks
like, because it's checking for the secret itself.
"""

from __future__ import annotations

import os
from typing import Iterable, List

#: Env var names that may hold a credential. Kept in one place so a new
#: provider only has to be added here, never re-implemented per module.
SECRET_ENV_VARS = (
    "DIGIKEY_CLIENT_ID",
    "DIGIKEY_CLIENT_SECRET",
    "MOUSER_API_KEY",
)


class SecretLeakError(ValueError):
    """Raised when a value about to be written into a record contains a
    live credential."""


def known_secret_values(env: os._Environ = None) -> List[str]:
    env = env if env is not None else os.environ
    values = []
    for name in SECRET_ENV_VARS:
        value = env.get(name)
        if value:
            values.append(value)
    return values


def assert_no_secret_leak(text: str, known_secrets: Iterable[str] = None) -> None:
    """Raises SecretLeakError if any known live credential value appears
    verbatim inside `text`. `known_secrets` defaults to whatever is
    currently in the environment; tests pass an explicit list so they never
    depend on real credentials being set."""
    if not text:
        return
    secrets_to_check = list(known_secrets) if known_secrets is not None else known_secret_values()
    for secret in secrets_to_check:
        if secret and secret in text:
            raise SecretLeakError("a credential value was found inside a record field")


def _walk_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for sub_value in value.values():
            yield from _walk_strings(sub_value)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _walk_strings(item)


def assert_submission_has_no_secret(submission: dict, known_secrets: Iterable[str] = None) -> None:
    """Checks every string field of a C3 submission dict (as produced by
    ExecutorSubmission.to_c3_submission()) for a leaked credential, at any
    nesting depth -- a secret hiding inside observation.identity_values is
    just as much a leak as one in raw_content."""
    secrets_to_check = list(known_secrets) if known_secrets is not None else known_secret_values()
    for text in _walk_strings(submission):
        assert_no_secret_leak(text, secrets_to_check)
