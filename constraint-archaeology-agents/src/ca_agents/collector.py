from __future__ import annotations
import datetime as dt, json, urllib.parse, urllib.request
from .models import Capture

UA = "constraint-archaeology-agents/0.2 research bot"


def _get_json(url: str):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


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


def collect_from_config(path: str):
    cfg = json.load(open(path, "r", encoding="utf-8"))
    captures = []
    errors = []
    for src in cfg.get("sources", []):
        try:
            if src["type"] == "hacker_news":
                captures += collect_hacker_news(src.get("limit", 40))
            elif src["type"] == "lobsters":
                captures += collect_lobsters(src.get("limit", 30))
            elif src["type"] == "dev":
                captures += collect_dev(src["tag"], src.get("limit", 30))
            elif src["type"] == "reddit":
                captures += collect_reddit(src["subreddit"], src.get("limit", 25))
            else:
                errors.append({"source": src.get("name", src.get("type")), "error": "unsupported source type"})
        except Exception as e:
            errors.append({"source": src.get("name", src.get("type")), "error": str(e)})
    return captures, errors
