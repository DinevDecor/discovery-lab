from __future__ import annotations
import datetime as dt, html, json, os, re, urllib.parse, urllib.request
from .budget import allocate_by_source
from .dedup import assign_story_groups
from .models import Capture, SourceTelemetry

UA = "constraint-archaeology-agents/0.2 research bot"


class CollectorError(RuntimeError):
    """Raised for a source-level failure that must reach the daily report's
    error list rather than silently producing no captures - e.g. a missing
    credential for a source whose official access method requires one.
    Never caught internally to fabricate empty-but-successful output."""


def _get_json(url: str, headers: dict | None = None):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "application/json",
            **(headers or {}),
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def _post_graphql(url: str, token: str, query: str, variables: dict | None = None):
    payload = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "User-Agent": UA,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(text: str) -> str:
    """Discourse's `cooked` field is rendered HTML. This is a plain-text
    approximation for the sensor, not a sanitizer - good enough because the
    result is only ever read by the LLM extraction step, never rendered."""
    if not text:
        return ""
    return html.unescape(_TAG_RE.sub(" ", text)).strip()


def collect_hacker_news(limit: int = 40):
    params = urllib.parse.urlencode({"tags": "story", "hitsPerPage": limit})
    data = _get_json("https://hn.algolia.com/api/v1/search_by_date?" + params)
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    out = []
    for h in data.get("hits", []):
        text = (h.get("story_text") or h.get("comment_text") or h.get("title") or "").strip()
        if not text:
            continue
        out.append(
            Capture(
                "hacker_news",
                h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}",
                h.get("title") or "",
                text,
                h.get("created_at") or "",
                now,
            )
        )
    return out


def collect_lobsters(limit: int = 30):
    """Collect newest public Lobsters stories via its JSON feed."""
    data = _get_json("https://lobste.rs/newest.json")
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    out = []
    for item in data[:limit]:
        title = (item.get("title") or "").strip()
        description = (item.get("description") or "").strip()
        text = (title + "\n" + description).strip()
        if not text:
            continue
        out.append(
            Capture(
                "lobsters",
                item.get("comments_url") or item.get("url") or "",
                title,
                text,
                item.get("created_at") or "",
                now,
            )
        )
    return out


def collect_dev(tag: str, limit: int = 30):
    """Collect public DEV/Forem posts for a tag without authentication."""
    params = urllib.parse.urlencode({"tag": tag, "per_page": min(limit, 100)})
    data = _get_json("https://dev.to/api/articles?" + params)
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    out = []
    for item in data[:limit]:
        title = (item.get("title") or "").strip()
        description = (item.get("description") or "").strip()
        tags = item.get("tag_list") or []
        if isinstance(tags, list):
            tag_text = ", ".join(str(x) for x in tags)
        else:
            tag_text = str(tags)
        text = (title + "\n" + description + (f"\nTags: {tag_text}" if tag_text else "")).strip()
        if not text:
            continue
        out.append(
            Capture(
                f"dev:{tag}",
                item.get("url") or item.get("canonical_url") or "",
                title,
                text,
                item.get("published_at") or item.get("published_timestamp") or "",
                now,
            )
        )
    return out


def collect_reddit(subreddit: str, limit: int = 25):
    data = _get_json(
        f"https://www.reddit.com/r/{urllib.parse.quote(subreddit)}/new.json?limit={limit}"
    )
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    out = []
    for child in data.get("data", {}).get("children", []):
        d = child.get("data", {})
        text = ((d.get("title") or "") + "\n" + (d.get("selftext") or "")).strip()
        if not text:
            continue
        out.append(
            Capture(
                f"reddit:{subreddit}",
                "https://www.reddit.com" + (d.get("permalink") or ""),
                d.get("title") or "",
                text,
                str(d.get("created_utc") or ""),
                now,
            )
        )
    return out


_PH_GRAPHQL_URL = "https://api.producthunt.com/v2/api/graphql"

_PH_QUERY = """
query NewestPosts($first: Int!) {
  posts(first: $first, order: NEWEST) {
    edges {
      node {
        id
        name
        tagline
        slug
        website
        createdAt
        comments(first: 3) {
          edges { node { body } }
        }
      }
    }
  }
}
"""


def collect_product_hunt(limit: int = 20):
    """Collect newly launched products via Product Hunt's official GraphQL v2
    API (https://api.producthunt.com/v2/api/graphql). This is a solution /
    emerging-market sensor, not a firsthand problem-report source - see
    ca_agents.sensor.cap_confidence_for_source, which structurally caps the
    confidence this source can ever reach, and README.md's adapter notes.

    Requires a Product Hunt developer token (env PRODUCT_HUNT_TOKEN) minted
    from a registered OAuth application at
    https://www.producthunt.com/v2/oauth/applications - there is no
    unauthenticated public endpoint for post listings. Raises CollectorError
    rather than returning an empty list when the token is absent, so a
    missing credential shows up as a source error in the daily report
    instead of silently looking like "no new products today".

    Upvote/comment counts are intentionally never read into a Capture -
    popularity must not be able to inflate evidence strength. The first few
    comments are folded into the capture's text as context (the task's
    "available public discussion"), not emitted as separate per-comment
    captures, so one launch thread cannot masquerade as several independent
    sources.
    """
    token = os.environ.get("PRODUCT_HUNT_TOKEN")
    if not token:
        raise CollectorError(
            "PRODUCT_HUNT_TOKEN is not set; Product Hunt's official API "
            "(GraphQL v2) requires an OAuth developer token, there is no "
            "public unauthenticated endpoint for post listings"
        )
    data = _post_graphql(_PH_GRAPHQL_URL, token, _PH_QUERY, {"first": limit})
    if "errors" in data:
        raise CollectorError(f"Product Hunt API error: {data['errors']}")
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    out = []
    edges = data.get("data", {}).get("posts", {}).get("edges", [])
    for edge in edges[:limit]:
        node = edge.get("node", {})
        name = (node.get("name") or "").strip()
        tagline = (node.get("tagline") or "").strip()
        if not name:
            continue
        comment_bodies = [
            (c.get("node", {}).get("body") or "").strip()
            for c in node.get("comments", {}).get("edges", [])
        ]
        comment_bodies = [c for c in comment_bodies if c]
        text = f"{name}: {tagline}".strip(": ")
        if comment_bodies:
            text += "\n\nDiscussion:\n" + "\n".join(f"- {c}" for c in comment_bodies)
        slug = node.get("slug") or ""
        url = f"https://www.producthunt.com/posts/{slug}" if slug else (node.get("website") or "")
        out.append(
            Capture(
                "product_hunt",
                url,
                name,
                text,
                node.get("createdAt") or "",
                now,
            )
        )
    return out


def collect_discourse(base_url: str, community: str, limit: int = 20):
    """Collect newest topics from a public Discourse forum's JSON API.

    Sampling is newest-first by creation time (`/latest.json?order=created`),
    never by popularity and never filtered by a pre-set problem-keyword list
    - matching the task's requirement that Discourse sampling stay
    keyword-and-popularity-agnostic. For each topic, fetches the topic detail
    endpoint to get the opening post's actual text (not just the title) plus
    the first reply as light context, when present, so the sensor has enough
    to judge whether a real problem is being described.

    No authentication is required for a public Discourse category's JSON
    API. `community` becomes part of the source label
    (`discourse:<community>`) so each forum stays a distinct, identifiable
    origin - never merged with another forum or with any other source type.
    """
    base = base_url.rstrip("/")
    listing = _get_json(f"{base}/latest.json?order=created")
    topics = listing.get("topic_list", {}).get("topics", [])[:limit]
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    out = []
    for t in topics:
        topic_id = t.get("id")
        slug = t.get("slug", "")
        title = (t.get("title") or "").strip()
        if topic_id is None or not title:
            continue
        detail = _get_json(f"{base}/t/{topic_id}.json")
        posts = detail.get("post_stream", {}).get("posts", [])
        if not posts:
            continue  # no opening post fetched - a title alone isn't evidence
        op_text = _strip_html(posts[0].get("cooked", ""))
        parts = [title, op_text]
        if len(posts) > 1:
            reply_text = _strip_html(posts[1].get("cooked", ""))
            if reply_text:
                parts.append(f"First reply: {reply_text[:600]}")
        text = "\n\n".join(p for p in parts if p).strip()
        if not text:
            continue
        out.append(
            Capture(
                f"discourse:{community}",
                f"{base}/t/{slug}/{topic_id}" if slug else f"{base}/t/{topic_id}",
                title,
                text,
                t.get("created_at") or "",
                now,
            )
        )
    return out


DEFAULT_CAPTURE_BUDGET = 80


def _source_label(src: dict) -> str:
    """The label a config entry's captures will carry as Capture.source,
    computed the same way regardless of whether collection succeeds - so a
    source that errors before returning anything still gets a telemetry row
    instead of silently vanishing from the report."""
    t = src.get("type")
    if t == "dev":
        return f"dev:{src.get('tag', '?')}"
    if t == "reddit":
        return f"reddit:{src.get('subreddit', '?')}"
    if t == "discourse":
        return f"discourse:{src.get('community', '?')}"
    if t in ("hacker_news", "lobsters", "product_hunt"):
        return t
    return src.get("name", t or "unknown")


def collect_from_config(path: str, budget: int = DEFAULT_CAPTURE_BUDGET):
    """Fetches every configured source, then admits captures into the daily
    sensor budget with source-balanced round-robin allocation (see
    budget.py) instead of a first-come-first-served slice - so a
    high-volume early source (Hacker News, Lobsters) cannot exhaust the
    budget before a later one (Product Hunt, each Discourse forum) is ever
    considered. Each source's own `limit` in config is still respected as
    its individual fetch cap; `budget` is the separate, global cap on how
    many of those fetched captures collectively reach the sensor.

    Returns (admitted_captures, errors, telemetry) where telemetry is
    {source_label: SourceTelemetry} with `fetched`/`admitted`/`duplicates`
    filled in - `observations`/`errors` (sensor-stage) are the caller's to
    fill in as extraction proceeds.
    """
    cfg = json.load(open(path, "r", encoding="utf-8"))
    errors = []
    telemetry: dict[str, SourceTelemetry] = {}
    fetched_by_source: dict[str, list[Capture]] = {}

    for src in cfg.get("sources", []):
        label = _source_label(src)
        telemetry.setdefault(label, SourceTelemetry())
        try:
            if src["type"] == "hacker_news":
                fetched = collect_hacker_news(src.get("limit", 40))
            elif src["type"] == "lobsters":
                fetched = collect_lobsters(src.get("limit", 30))
            elif src["type"] == "dev":
                fetched = collect_dev(src["tag"], src.get("limit", 30))
            elif src["type"] == "reddit":
                fetched = collect_reddit(src["subreddit"], src.get("limit", 25))
            elif src["type"] == "product_hunt":
                fetched = collect_product_hunt(src.get("limit", 20))
            elif src["type"] == "discourse":
                fetched = collect_discourse(src["base_url"], src["community"], src.get("limit", 20))
            else:
                errors.append({"source": src.get("name", src.get("type")), "error": "unsupported source type"})
                continue
        except Exception as e:
            errors.append({"source": src.get("name", src.get("type")), "error": str(e)})
            continue

        telemetry[label].fetched += len(fetched)
        fetched_by_source.setdefault(label, []).extend(fetched)

    admitted = allocate_by_source(fetched_by_source, budget)
    for c in admitted:
        telemetry[c.source].admitted += 1

    groups = assign_story_groups(admitted)
    for i, group_id in groups.items():
        admitted[i].story_group = group_id
        telemetry[admitted[i].source].duplicates += 1

    return admitted, errors, telemetry
