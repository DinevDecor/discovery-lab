"""X API v2 client for audit rehydration - ID lookup ONLY.

Deliberately a separate module from client.py, and deliberately does
not import, wrap, or expose client.search_recent. This module's only
capability is looking up a fixed, pre-registered, already-frozen list
of post IDs by ID - there is no code path from here into a new
discovery search, a query string, or config/queries.json.
tests/test_audit_safety.py enforces this statically, not just this
docstring.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request

LOOKUP_URL = "https://api.x.com/2/tweets"
API_VERSION = "x_api_v2_tweets_lookup"
UA = "discovery-lab-x-signal-probe-audit/0.1 research probe (read-only, id-lookup-only)"

# X API v2 tweets-lookup accepts at most 100 ids per call. The audit
# never needs more than 20, and never splits a request across calls -
# more ids than this is a caller error, not something to page through.
MAX_IDS_PER_REQUEST = 100
DEFAULT_MAX_RETRIES = 2
DEFAULT_RETRY_BACKOFF_SECONDS = (2, 4)


class TooManyIdsError(ValueError):
    """Raised if more ids are requested than one batched call allows.
    The audit never paginates or splits a lookup into multiple calls -
    an oversized request is a bug to fix, not a retry target."""


class AuditApiError(RuntimeError):
    """Raised for any X API failure during rehydration. Callers must
    record it truthfully and must never fabricate post content in its
    place."""


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


def get_posts_by_ids(
    ids: list[str],
    bearer_token: str,
    *,
    max_retries: int = DEFAULT_MAX_RETRIES,
    retry_backoff_seconds=DEFAULT_RETRY_BACKOFF_SECONDS,
    transport=_http_get,
    sleep_fn=time.sleep,
):
    """Looks up `ids` (<=100) in exactly one request - never a second
    request, never a smaller retry batch, never a fallback to search.

    Returns (found, unavailable):
      found: dict[post_id, {"text": ..., "created_at": ...}]
      unavailable: list[post_id] - every requested id that did not come
        back in `data`, whether the API explicitly listed it in
        `errors` (deleted, suspended, protected, not authorized, etc.)
        or simply omitted it. An id here is unavailable, full stop -
        there is no second lookup attempt and no substitution.
    """
    ids = list(dict.fromkeys(ids))  # de-dupe, preserve order - never changes which ids are requested
    if len(ids) > MAX_IDS_PER_REQUEST:
        raise TooManyIdsError(
            f"{len(ids)} ids requested, exceeds the {MAX_IDS_PER_REQUEST}-id single-request "
            "limit - the audit never splits a lookup into multiple calls"
        )

    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "User-Agent": UA,
        "Accept": "application/json",
    }
    params = {"ids": ",".join(ids), "tweet.fields": "created_at"}
    url = f"{LOOKUP_URL}?{urllib.parse.urlencode(params)}"

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
            raise AuditApiError(f"X API ID lookup failed: {exc}") from exc

    found: dict[str, dict] = {}
    for item in payload.get("data", []) or []:
        pid = str(item.get("id", ""))
        if pid:
            found[pid] = {"text": item.get("text", ""), "created_at": item.get("created_at", "")}

    unavailable = [pid for pid in ids if pid not in found]
    return found, unavailable
