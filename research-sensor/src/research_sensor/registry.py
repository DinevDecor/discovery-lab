"""Research Signal Registry: builds ResearchSignals from paper-capture
clusters and persists them with stable RES-000N identifiers.

Independently reimplemented pattern - same idempotent-ID-by-key idea
as headquarters/src/headquarters/recommendation.py's HQ-000N and
reality-sensor/src/reality_sensor/registry.py's RS-000N, not shared
code, per EXEC-009's own ruling.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict
from pathlib import Path

from .config import RelevanceGateConfig
from .experiments import build_experiments, is_high_value
from .models import Citation, Project, RawPaperCapture, ResearchSignal
from .relevance import gate
from .trust import assess_confidence, can_accept_signal

_EVIDENCE_RANK = {t: i for i, t in enumerate((
    "PEER_REVIEWED_PUBLISHED", "PEER_REVIEWED_ACCEPTED", "NOTABLE_LAB_PREPRINT",
    "PREPRINT", "COMMUNITY_HINT", "UNKNOWN",
))}


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "unspecified"


def _strongest(captures: list[RawPaperCapture]) -> RawPaperCapture:
    return sorted(
        captures,
        key=lambda c: (_EVIDENCE_RANK.get(c.evidence_level, 99), c.title),
    )[0]


def build_signal(captures: list[RawPaperCapture], relevance_config: RelevanceGateConfig) -> ResearchSignal | None:
    """Returns None if the cluster's evidence is COMMUNITY_HINT-only -
    EXEC-010's Trust Policy: "COMMUNITY only as discovery hints," never
    itself sufficient to accept a signal. Callers must treat None as
    "log as a discovery hint, do not register" - see cli.py."""
    evidence_levels = [c.evidence_level for c in captures]
    if not can_accept_signal(evidence_levels):
        return None

    primary = _strongest(captures)

    citations = [
        Citation(
            title=c.title,
            authors=c.authors,
            publication=c.publication,
            date=c.date,
            source_url=c.source_url,
            source_trust=c.source_trust,
            evidence_level=c.evidence_level,
            quoted_abstract=c.raw_abstract,
        )
        for c in sorted(captures, key=lambda c: (c.title, c.source_url))
    ]

    corroborating = len({
        c.evidence_level for c in captures
        if _EVIDENCE_RANK.get(c.evidence_level, 99) <= _EVIDENCE_RANK["NOTABLE_LAB_PREPRINT"]
    })
    confidence = assess_confidence(evidence_levels, corroborating)

    gate_text = " ".join([
        primary.problem_addressed, primary.main_contribution,
        primary.architectural_relevance_note,
    ])
    affected_projects = gate(gate_text, relevance_config)

    experiments = build_experiments(captures) if is_high_value(affected_projects, confidence) else []

    if affected_projects == [Project.WATCH]:
        recommended_action = "WATCH - no named Discovery Lab project identified; monitor for future relevance."
    elif not experiments:
        recommended_action = (
            "Advisory only - relevant to "
            f"{', '.join(affected_projects)}, but no structured research opportunity "
            "was captured; a human should assess directly before further action."
        )
    else:
        recommended_action = (
            "Advisory only - a human should review the possible experiment(s) below for "
            f"relevance to {', '.join(affected_projects)}; this sensor takes no action."
        )

    key = f"{primary.domain}:{_slugify(primary.problem_addressed)}"

    return ResearchSignal(
        research_id="",  # assigned by upsert()
        title=primary.title,
        authors=primary.authors,
        publication=primary.publication,
        date=primary.date,
        domain=primary.domain,
        problem_addressed=primary.problem_addressed,
        main_contribution=primary.main_contribution,
        evidence_level=primary.evidence_level,
        affected_projects=affected_projects,
        possible_experiments=experiments,
        architectural_relevance=primary.architectural_relevance_note or "INSUFFICIENT_EVIDENCE",
        confidence=confidence,
        recommended_action=recommended_action,
        evidence=citations,
        key=key,
    )


def _next_id(records: list[ResearchSignal]) -> str:
    max_n = 0
    for r in records:
        if r.research_id.startswith("RES-"):
            try:
                max_n = max(max_n, int(r.research_id.split("-")[1]))
            except (IndexError, ValueError):
                continue
    return f"RES-{max_n + 1:04d}"


def upsert(signal: ResearchSignal, records: list[ResearchSignal], run_timestamp: str) -> list[ResearchSignal]:
    """Reuses an existing RES-000N for the same `key`; otherwise mints
    the next sequential ID. Evidence only grows across runs; confidence
    never silently downgrades once established - same discipline as
    reality-sensor's own upsert()."""
    for r in records:
        if r.key == signal.key:
            r.last_seen = run_timestamp
            r.times_seen += 1
            existing_urls = {e.source_url for e in r.evidence}
            for e in signal.evidence:
                if e.source_url not in existing_urls:
                    r.evidence.append(e)
                    existing_urls.add(e.source_url)
            new_conf = assess_confidence(
                [e.evidence_level for e in r.evidence],
                len({e.evidence_level for e in r.evidence
                     if _EVIDENCE_RANK.get(e.evidence_level, 99) <= _EVIDENCE_RANK["NOTABLE_LAB_PREPRINT"]}),
            )
            rank = {"INSUFFICIENT_EVIDENCE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}
            if rank.get(new_conf, 0) > rank.get(r.confidence, 0):
                r.confidence = new_conf
            return records

    signal.research_id = _next_id(records)
    signal.first_seen = run_timestamp
    signal.last_seen = run_timestamp
    signal.times_seen = 1
    records.append(signal)
    return records


def load_registry(path: Path) -> list[ResearchSignal]:
    if not path.is_file():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    out = []
    for r in raw:
        evidence = [Citation(**e) for e in r.pop("evidence", [])]
        experiments_raw = r.pop("possible_experiments", [])
        from .models import PossibleExperiment
        experiments = [PossibleExperiment(**e) for e in experiments_raw]
        out.append(ResearchSignal(evidence=evidence, possible_experiments=experiments, **r))
    return out


def save_registry(path: Path, records: list[ResearchSignal]) -> None:
    path.write_text(
        json.dumps([asdict(r) for r in records], indent=2, sort_keys=False),
        encoding="utf-8",
    )
