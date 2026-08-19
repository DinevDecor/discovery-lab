#!/usr/bin/env python3
"""Update the Mobile Console's derived Bulgarian display cache.

This script is intentionally outside src/mobile_console: the console itself
remains a deterministic, read-only viewer with no model/network client.
The script is run by GitHub Actions when canonical records change. It writes
only site/translations-bg.json.

Only strings that the current mobile UI can actually render are collected.
Translation requests run in a small bounded pool so a full refresh completes
inside the Actions budget without changing canonical data or browser safety.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple

CONSOLE_ROOT = Path(__file__).resolve().parents[1]
SRC = CONSOLE_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mobile_console.aggregate import load_all  # noqa: E402
from mobile_console.translations import load_cache, source_hash  # noqa: E402

CACHE_PATH = CONSOLE_ROOT / "site" / "translations-bg.json"
APP_JS_PATH = CONSOLE_ROOT / "site" / "app.js"
DEFAULT_MODEL = os.environ.get("TRANSLATION_MODEL", "gpt-4.1-mini")

_ID_LIKE = re.compile(
    r"^(?:OBS-|ANOM-|BC-|PGT-|pgt-case:|case:|analysis:|falsification:|judgment:|run\s+\d|[0-9a-f]{24,}$)",
    re.I,
)
_URL = re.compile(r"^https?://", re.I)
_DATEISH = re.compile(r"^\d{4}-\d{2}-\d{2}(?:[T ][0-9:.+Z-]+)?$")


def _add(bucket: Set[str], value: Any) -> None:
    if isinstance(value, list):
        for item in value:
            _add(bucket, item)
        return
    if not isinstance(value, str):
        return
    text = value.strip()
    if len(text) < 3 or len(text) > 6000:
        return
    if _URL.match(text) or _ID_LIKE.match(text) or _DATEISH.match(text):
        return
    if text.upper() == text and len(text) < 50 and re.fullmatch(r"[A-Z0-9_ .·/-]+", text):
        return
    if text in {"anthropic", "openai", "Claude", "GPT", "Hacker News", "Fly.io"}:
        return
    bucket.add(text)


def _collect_case_static_strings(bucket: Set[str]) -> None:
    """Collect human-facing text nodes from the special CASE DETAIL docket."""
    if not APP_JS_PATH.exists():
        return
    text = APP_JS_PATH.read_text(encoding="utf-8")
    marker = "// ---------- CASE DETAIL ----------"
    if marker not in text:
        return
    section = text.split(marker, 1)[1].split("// ---------- ROUTER ----------", 1)[0]
    for raw in re.findall(r">([^<>\n]+)<", section):
        candidate = html.unescape(raw).strip()
        if not candidate or "${" in candidate or "}" in candidate:
            continue
        candidate = re.sub(r"\s+", " ", candidate)
        _add(bucket, candidate)


def collect_source_strings() -> List[str]:
    """Collect only narrative strings that the current console renders."""
    raw = load_all()
    bucket: Set[str] = set()

    obs_by_id = {o.get("observation_id"): o for o in raw["observations"]}
    anomaly_by_id = {a.get("anomaly_id"): a for a in raw["anomalies"]}

    for candidate in raw["candidates"]:
        for anomaly_id in candidate.get("anomaly_ids", []):
            _add(bucket, anomaly_by_id.get(anomaly_id, {}).get("canonical_pattern"))

        observation_ids = candidate.get("observation_ids", [])
        if observation_ids:
            obs = obs_by_id.get(observation_ids[0], {})
            for field in ("process", "pain", "evidence_quote"):
                _add(bucket, obs.get(field))

        product = candidate.get("dimensions", {}).get("potential_product_function", {})
        if isinstance(product, dict):
            _add(bucket, product.get("value"))
            _add(bucket, product.get("note"))

    for artifact in raw["blind_analyses"]:
        analysis = artifact.get("analysis", {})
        if isinstance(analysis, dict):
            _add(bucket, analysis.get("hidden_function"))

    for case in raw["pgt_cases"]:
        _add(bucket, case.get("domain"))
        _add(bucket, case.get("proposition"))

    _collect_case_static_strings(bucket)
    return sorted(bucket, key=lambda s: (len(s), s))


def _response_json(payload: Dict[str, Any], api_key: str, retries: int = 4) -> Dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    for attempt in range(retries):
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=body,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=75) as res:
                return json.loads(res.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == retries - 1:
                detail = exc.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"OpenAI translation request failed HTTP {exc.code}: {detail[:1000]}") from exc
            time.sleep(2 ** attempt)
        except (urllib.error.URLError, TimeoutError) as exc:
            if attempt == retries - 1:
                raise RuntimeError(f"OpenAI translation request failed after retries: {exc}") from exc
            time.sleep(2 ** attempt)
    raise RuntimeError("translation request exhausted retries")


def translate_batch(texts: List[str], api_key: str, model: str) -> Dict[str, str]:
    items = [{"id": source_hash(text), "text": text} for text in texts]
    payload = {
        "model": model,
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": (
                    "Translate the supplied user-facing Discovery Machine text into natural Bulgarian. "
                    "Preserve technical product names, IDs, code identifiers, model names, acronyms, URLs, "
                    "and canonical verdict tokens such as WATCH/ADVANCE/REJECT exactly when they occur. "
                    "Do not add facts, explanations, confidence, or interpretation. Preserve quoted meaning. "
                    "Return ONLY a JSON object of the exact form {\"translations\": {\"<id>\": \"<Bulgarian>\"}} "
                    "with one value for every supplied id and no extra keys."
                ),
            },
            {"role": "user", "content": json.dumps(items, ensure_ascii=False)},
        ],
    }
    response = _response_json(payload, api_key)
    try:
        content = response["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        translated = parsed["translations"]
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError("OpenAI returned an invalid translation payload") from exc

    expected = {item["id"] for item in items}
    if set(translated) != expected:
        missing = sorted(expected - set(translated))
        extra = sorted(set(translated) - expected)
        raise RuntimeError(f"translation id mismatch; missing={missing[:5]} extra={extra[:5]}")

    out: Dict[str, str] = {}
    for item in items:
        value = translated[item["id"]]
        if not isinstance(value, str) or not value.strip():
            raise RuntimeError(f"empty translation for {item['id']}")
        out[item["id"]] = value.strip()
    return out


def chunks(items: List[str], size: int) -> Iterable[List[str]]:
    for i in range(0, len(items), size):
        yield items[i:i + size]


def _translate_indexed_batch(args: Tuple[int, List[str], str, str]) -> Tuple[int, List[str], Dict[str, str]]:
    index, batch, api_key, model = args
    return index, batch, translate_batch(batch, api_key, model)


def update_cache(api_key: str, model: str, batch_size: int, concurrency: int) -> Dict[str, int]:
    source_strings = collect_source_strings()
    cache = load_cache(CACHE_PATH)
    entries = dict(cache.get("entries", {}))

    current_hashes = {source_hash(text): text for text in source_strings}
    entries = {key: value for key, value in entries.items() if key in current_hashes}
    missing = [text for key, text in current_hashes.items() if key not in entries]
    batches = list(chunks(missing, batch_size))

    print(
        json.dumps(
            {
                "sources": len(source_strings),
                "already_cached": len(entries),
                "missing": len(missing),
                "batches": len(batches),
                "batch_size": batch_size,
                "concurrency": concurrency,
            },
            sort_keys=True,
        ),
        flush=True,
    )

    if batches:
        workers = max(1, min(concurrency, len(batches)))
        work = [(i, batch, api_key, model) for i, batch in enumerate(batches, 1)]
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(_translate_indexed_batch, item): item[0] for item in work}
            completed = 0
            for future in as_completed(futures):
                index, batch, translated = future.result()
                for text in batch:
                    digest = source_hash(text)
                    entries[digest] = {
                        "source": text,
                        "bg": translated[digest],
                        "source_sha256": digest,
                    }
                completed += 1
                print(f"translated batch {index}/{len(batches)}; completed={completed}", flush=True)

    payload = {
        "version": 1,
        "language": "bg",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "model": model,
        "entries": {key: entries[key] for key in sorted(entries)},
    }
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = CACHE_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(CACHE_PATH)
    return {"sources": len(source_strings), "translated_now": len(missing), "cache_entries": len(entries)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--batch-size", type=int, default=60)
    parser.add_argument("--concurrency", type=int, default=6)
    parser.add_argument("--collect-only", action="store_true", help="print source count without calling a model or writing")
    args = parser.parse_args()

    sources = collect_source_strings()
    if args.collect_only:
        print(json.dumps({"sources": len(sources)}, indent=2))
        return

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is required for translation-cache updates")
    result = update_cache(
        api_key,
        args.model,
        max(1, args.batch_size),
        max(1, args.concurrency),
    )
    print(json.dumps(result, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
