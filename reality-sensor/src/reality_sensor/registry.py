"""Signal Registry: builds Signals from RawCapture clusters and persists
them with stable RS-000N identifiers.

The persistence half mirrors headquarters/src/headquarters/
recommendation.py's HQ-000N pattern deliberately, not coincidentally:
same problem (a recurring real-world thing should keep one ID across
runs, not mint a new one every time it's seen again), same solution
(match on a content-derived `key`, reuse the ID, bump a counter).
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from .config import RelevanceGateConfig
from .models import Evidence, RawCapture, Signal
from .relevance import gate
from .trust import assess_confidence, assess_urgency

# Trust-level ranking used only to choose which cluster member is the
# "primary" source a Signal's headline fields are built from - lower
# index = stronger trust, matching TrustLevel.ALL's own declared order.
_TRUST_RANK = {t: i for i, t in enumerate(
    ("PRIMARY", "OFFICIAL", "RESEARCH", "SECONDARY", "COMMUNITY", "UNKNOWN")
)}


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "unspecified"


def _primary(captures: list[RawCapture]) -> RawCapture:
    return sorted(
        captures,
        key=lambda c: (_TRUST_RANK.get(c.source_trust, 99), c.source_name),
    )[0]


def build_signal(captures: list[RawCapture], relevance_config: RelevanceGateConfig) -> Signal:
    """Pure function: same cluster in -> same Signal fields out, every
    time. No randomness, no wall-clock dependency in any field except
    timestamp/first_seen/last_seen, which the caller supplies."""
    primary = _primary(captures)

    evidence = [
        Evidence(
            source_name=c.source_name,
            source_url=c.source_url,
            source_trust=c.source_trust,
            quoted_text=c.raw_text,
        )
        for c in sorted(captures, key=lambda c: (c.source_name, c.source_url))
    ]

    trust_levels = [c.source_trust for c in captures]
    confidence = assess_confidence(trust_levels)

    practical_impact = next(
        (c.practical_impact_note for c in captures if c.practical_impact_note), ""
    )
    summary = f"{primary.source_name}: {primary.title}"
    gate_text = " ".join(
        [primary.affected_capability, summary, practical_impact]
    )
    affected_projects = gate(gate_text, relevance_config)
    urgency = assess_urgency(primary.category, confidence, gate_text)

    if confidence == "INSUFFICIENT_EVIDENCE":
        recommended_action = "Monitor for corroborating evidence before any human action."
    else:
        recommended_action = (
            "Advisory only - a human should review this signal for relevance "
            f"to {', '.join(affected_projects)}; this sensor takes no action."
        )

    key = f"{primary.category}:{_slugify(primary.affected_capability)}"

    return Signal(
        signal_id="",  # assigned by upsert()
        timestamp=primary.captured_at,
        source=primary.source_name,
        source_trust=primary.source_trust,
        category=primary.category,
        affected_capability=primary.affected_capability,
        affected_projects=affected_projects,
        evidence=evidence,
        summary=summary,
        practical_impact=practical_impact,
        confidence=confidence,
        urgency=urgency,
        recommended_action=recommended_action,
        key=key,
    )


def _next_id(records: list[Signal]) -> str:
    max_n = 0
    for r in records:
        if r.signal_id.startswith("RS-"):
            try:
                max_n = max(max_n, int(r.signal_id.split("-")[1]))
            except (IndexError, ValueError):
                continue
    return f"RS-{max_n + 1:04d}"


def upsert(signal: Signal, records: list[Signal], run_timestamp: str) -> list[Signal]:
    """Reuses an existing RS-000N for the same `key`, bumping
    times_seen/last_seen; otherwise mints the next sequential ID.
    Returns the updated records list (records is mutated in place and
    also returned, matching recommendation.py's own return style)."""
    for r in records:
        if r.key == signal.key:
            r.last_seen = run_timestamp
            r.times_seen += 1
            # Evidence can grow across runs (new corroborating sources)
            # but never shrinks - existing citations are never dropped.
            existing_urls = {e.source_url for e in r.evidence}
            for e in signal.evidence:
                if e.source_url not in existing_urls:
                    r.evidence.append(e)
                    existing_urls.add(e.source_url)
            # Confidence can only improve (more evidence -> stronger
            # trust achievable), never silently downgrade what was
            # already established.
            new_conf = assess_confidence([e.source_trust for e in r.evidence])
            rank = {"INSUFFICIENT_EVIDENCE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}
            if rank.get(new_conf, 0) > rank.get(r.confidence, 0):
                r.confidence = new_conf
            return records

    signal.signal_id = _next_id(records)
    signal.first_seen = run_timestamp
    signal.last_seen = run_timestamp
    signal.times_seen = 1
    records.append(signal)
    return records


def load_registry(path: Path) -> list[Signal]:
    if not path.is_file():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    out = []
    for r in raw:
        evidence = [Evidence(**e) for e in r.pop("evidence", [])]
        out.append(Signal(evidence=evidence, **r))
    return out


def save_registry(path: Path, records: list[Signal]) -> None:
    path.write_text(
        json.dumps([asdict(r) for r in records], indent=2, sort_keys=False),
        encoding="utf-8",
    )
