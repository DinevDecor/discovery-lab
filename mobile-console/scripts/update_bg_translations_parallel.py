#!/usr/bin/env python3
"""Parallel wrapper for Bulgarian display-cache refresh.

Uses the existing translation contract and source collection, but executes
independent translation batches concurrently so the refresh finishes well
inside the GitHub Actions timeout. Writes only site/translations-bg.json.
"""

from __future__ import annotations

import argparse
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import update_bg_translations as base

CACHE_PATH = Path(__file__).resolve().parents[1] / "site" / "translations-bg.json"


def _chunks(items: List[str], size: int) -> List[List[str]]:
    return [items[i:i + size] for i in range(0, len(items), size)]


def refresh(api_key: str, model: str, batch_size: int, workers: int) -> Dict[str, int]:
    source_strings = base.collect_source_strings()
    cache = base.load_cache(CACHE_PATH)
    entries = dict(cache.get("entries", {}))

    current = {base.source_hash(text): text for text in source_strings}
    entries = {key: value for key, value in entries.items() if key in current}
    missing = [text for key, text in current.items() if key not in entries]

    batches = _chunks(missing, max(1, batch_size))
    if batches:
        with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
            future_to_batch = {
                pool.submit(base.translate_batch, batch, api_key, model): batch
                for batch in batches
            }
            for future in as_completed(future_to_batch):
                batch = future_to_batch[future]
                translated = future.result()
                for text in batch:
                    digest = base.source_hash(text)
                    entries[digest] = {
                        "source": text,
                        "bg": translated[digest],
                        "source_sha256": digest,
                    }

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

    return {
        "sources": len(source_strings),
        "translated_now": len(missing),
        "cache_entries": len(entries),
        "batches": len(batches),
        "workers": max(1, workers),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default=os.environ.get("TRANSLATION_MODEL", "gpt-4.1-mini"))
    parser.add_argument("--batch-size", type=int, default=20)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is required for translation-cache updates")

    print(json.dumps(refresh(api_key, args.model, args.batch_size, args.workers), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
