"""Mechanical, deterministic pre-filters. No model call anywhere in this
package (see CONTRACT.md and tests/test_safety.py) - retweet/marketing
detection is plain heuristics, not an LLM judgment, so it can never be
"the model liked this post" masquerading as evidence quality."""

from __future__ import annotations

import re

_MARKETING_PHRASES = (
    "check out", "sign up", "link in bio", "use code", "% off",
    "limited time", "join our", "download now", "book a demo",
    "dm us", "click here", "giveaway", "early access",
)

_URL_RE = re.compile(r"https?://\S+")
_RT_PREFIX_RE = re.compile(r"^\s*RT\s+@")


def is_retweet(text: str, referenced_tweet_types: tuple[str, ...] = ()) -> bool:
    if "retweeted" in referenced_tweet_types:
        return True
    return bool(_RT_PREFIX_RE.match(text or ""))


def is_marketing_like(text: str, *, max_urls: int = 2) -> bool:
    lowered = (text or "").lower()
    if any(phrase in lowered for phrase in _MARKETING_PHRASES):
        return True
    if len(_URL_RE.findall(text or "")) > max_urls:
        return True
    return False


def is_first_person_report(text: str) -> bool:
    """Loose signal-quality hint for the report's breakdown only - never
    a hard filter, since a real problem report phrased in the third
    person should not be discarded on that basis alone."""
    return bool(re.search(r"\b(we|our|i|my team|my company)\b", (text or "").lower()))
