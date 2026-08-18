"""X API v2 client for the X Signal Probe.

Read-only. `get_bearer_token` is the only place X_BEARER_TOKEN is read
from the environment - never logged, never printed, never persisted,
and never falls back to a hardcoded credential when absent. All network
I/O goes through the `transport` parameter (defaulting to `_http_get`)
so tests can substitute a fake transport, matching the mocking style
already used by ca_agents.collector's Product Hunt tests
(`patch.object(collector, "_post_graphql", ...)`)  - the real network
call is never exercised by this package's test suite.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

SEARCH_URL = "https://api.x.com/2/tweets/search/recent"
API_VERSION = "x_api_v2_recent_search"
UA = "discovery-lab-x-signal-probe/0.1 research probe (read-only)"

DEFAULT_MAX_RESULTS_PER_QUERY = 10
DEFAULT_MAX_PAGES_PER_QUERY = 1
DEFAULT_MAX_RETRIES = 2
DEFAULT_RETRY_BACKOFF_SECONDS = (2, 4)


class MissingSecretError(RuntimeError):
    """Raised when X_BEARER_TOKEN is absent or empty. Never caught to
    fall back to a hardcoded credential or to silently skip the probe -
    a missing secret must fail the run clearly."""


class XApiError(RuntimeError):
    """Raised for any X API failure: HTTP error, an error payload, or
    retries exhausted. Callers must record it truthfully in the run
    report/errors list and move on - never invent observations in its
    place, and never let it break anything outside this package."""


def get_bearer_token(env: dict | None = None) -> str:
    """Reads X_BEARER_TOKEN from `env` (defaults to os.environ). Raises
    MissingSecretError rather than returning "" or a placeholder."""
    source = env if env is not None else os.environ
    token = source.get("X_BEARER_TOKEN", "")
    if not token:
        raise MissingSecretError(
            "X_BEARER_TOKEN is not set. This probe only reads it from the "
            "environment / GitHub Actions secret - there is no fallback "
            "and no hardcoded credential."
        )
    return token


def _http_get(url: str, headers: dict) -> dict:
    """Real transport. The test suite never calls this - every test
    patches `transport` out with a fake."""
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def _is_retryable(exc: Exception) -> bool:
    if isinstance(exc, urllib.error.HTTPError):
        return exc.code == 429 or 500 <= exc.code < 600
    return False


def search_recent(
    query: str,
    bearer_token: str,
    *,
    max_results: int = DEFAULT_MAX_RESULTS_PER_QUERY,
    max_pages: int = DEFAULT_MAX_PAGES_PER_QUERY,
    max_retries: int = DEFAULT_MAX_RETRIES,
    retry_backoff_seconds=DEFAULT_RETRY_BACKOFF_SECONDS,
    transport=_http_get,
    sleep_fn=time.sleep,
) -> list[dict]:
    """Fetches up to `max_pages` pages (a hard bound - never follows
    `next_token` beyond it, so this can never turn into unbounded
    pagination) of up to `max_results` results each, for one
    pre-registered query. Returns the raw `data` list of tweet objects
    from the API response(s); parsing into probe models happens one
    layer up in probe.py, so this function's only job is a bounded,
    retried HTTP fetch.

    Retries only on 429/5xx, up to `max_retries` times per page, using a
    small fixed backoff schedule (`retry_backoff_seconds`) - never an
    unbounded or exponential retry storm. Any other failure (4xx auth or
    query errors, malformed payload) raises immediately without
    retrying, since retrying a bad token or a bad query can only burn
    budget for no benefit.
    """
    if max_pages < 1:
        raise ValueError("max_pages must be >= 1")

    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "User-Agent": UA,
        "Accept": "application/json",
    }
    results: list[dict] = []
    next_token = None

    for _ in range(max_pages):
        params = {
            "query": query,
            "max_results": max_results,
            "tweet.fields": "created_at,author_id,referenced_tweets",
        }
        if next_token:
            params["next_token"] = next_token
        url = f"{SEARCH_URL}?{urllib.parse.urlencode(params)}"

        attempt = 0
        while True:
            try:
                payload = transport(url, headers)
                break
            except Exception as exc:
                if attempt < max_retries and _is_retryable(exc):
                    delay = retry_backoff_seconds[min(attempt, len(retry_backoff_seconds) - 1)]
                    sleep_fn(delay)
                    attempt += 1
                    continue
                raise XApiError(f"X API request failed for query {query!r}: {exc}") from exc

        if "errors" in payload and "data" not in payload:
            raise XApiError(f"X API error for query {query!r}: {payload['errors']}")

        results.extend(payload.get("data", []))
        next_token = payload.get("meta", {}).get("next_token")
        if not next_token:
            break

    return results
