#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "tool-radar" / "data" / "tool_signals.jsonl"
OUT = ROOT / "mobile-console" / "site" / "tool-radar.json"


def load_rows() -> list[dict]:
    if not LEDGER.exists():
        return []
    rows: list[dict] = []
    seen: set[str] = set()
    for raw in LEDGER.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        row = json.loads(raw)
        signal_id = row["signal_id"]
        if signal_id in seen:
            raise ValueError(f"duplicate signal_id: {signal_id}")
        seen.add(signal_id)
        rows.append(row)
    rows.sort(key=lambda r: (r.get("source_email_ts", ""), r.get("recorded_at", "")), reverse=True)
    return rows


def main() -> None:
    rows = load_rows()
    payload = {"count": len(rows), "signals": rows}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"tool radar: {len(rows)} signal(s) -> {OUT}")


if __name__ == "__main__":
    main()
