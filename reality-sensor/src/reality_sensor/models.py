"""Data model for the Reality Sensor's Signal Registry.

Field names and vocabularies implement EXEC-008's own spec exactly —
this module does not invent a schema, it codifies the one already
named in the task (Signal Model, Source Trust Levels, Evidence
Discipline, Relevance Gate's 5 projects).
"""

from __future__ import annotations

from dataclasses import dataclass, field


class TrustLevel:
    """Closed vocabulary, per EXEC-008's Source Trust Levels section.
    Every source must be classified as exactly one of these — never
    inferred, never left blank."""

    PRIMARY = "PRIMARY"
    OFFICIAL = "OFFICIAL"
    RESEARCH = "RESEARCH"
    SECONDARY = "SECONDARY"
    COMMUNITY = "COMMUNITY"
    UNKNOWN = "UNKNOWN"

    ALL = (PRIMARY, OFFICIAL, RESEARCH, SECONDARY, COMMUNITY, UNKNOWN)


class Category:
    """The 4 Initial Observation Domains (A-D), closed by design —
    EXEC-008 names exactly these four and no others for this first
    sensor."""

    FOUNDATION_MODEL_RELEASES = "FOUNDATION_MODEL_RELEASES"
    AGENT_INFRASTRUCTURE = "AGENT_INFRASTRUCTURE"
    DEVELOPER_PLATFORMS = "DEVELOPER_PLATFORMS"
    RESEARCH = "RESEARCH"

    ALL = (
        FOUNDATION_MODEL_RELEASES,
        AGENT_INFRASTRUCTURE,
        DEVELOPER_PLATFORMS,
        RESEARCH,
    )


class Confidence:
    """Per EXEC-008's Confidence Rules: "Confidence depends on
    evidence. Not popularity. Not excitement. Not marketing." HIGH can
    never be assigned from COMMUNITY-trust evidence alone — enforced in
    trust.py, not just documented here. INSUFFICIENT_EVIDENCE mirrors
    the same honesty-over-certainty vocabulary Observation Agent and
    Headquarters already use throughout this ecosystem."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

    ALL = (HIGH, MEDIUM, LOW, INSUFFICIENT_EVIDENCE)


class Urgency:
    """How soon a human should look at this signal — not how exciting
    it is. See trust.py's assess_urgency for the transparent, documented
    heuristic (mirrors the Attention Engine's own "fully shown, documented
    rubric" discipline in headquarters/src/headquarters/prioritizer.py)."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

    ALL = (HIGH, MEDIUM, LOW)


class Project:
    """The 5 Discovery Lab projects EXEC-008's Relevance Gate names as
    allowed answers, plus the WATCH sentinel for "no project applies
    yet" — never force relevance where none exists."""

    KOD = "KOD"
    DISCOVERY_LAB = "Discovery Lab"
    TRUST_ENGINE = "Trust Engine"
    GENERATIVE_DISCOVERY_ENGINE = "Generative Discovery Engine"
    DINEV_ASSISTANT = "Dinev Assistant"
    WATCH = "WATCH"

    NAMED = (KOD, DISCOVERY_LAB, TRUST_ENGINE, GENERATIVE_DISCOVERY_ENGINE, DINEV_ASSISTANT)
    ALL = NAMED + (WATCH,)


@dataclass
class RawCapture:
    """One fetched source, before any interpretation. This is the FACT
    stage of the Evidence Discipline (FACT -> CLAIM -> EVIDENCE ->
    INTERPRETATION -> ACTION): exactly what a source said, with no
    scoring, no clustering, no summary yet. Produced by the capture
    step (see ARCHITECTURE.md), consumed only by dedup.py/cli.py — this
    dataclass never appears in the Signal Registry itself."""

    source_name: str
    source_url: str
    source_trust: str  # TrustLevel
    category: str  # Category
    captured_at: str  # ISO-8601 UTC
    title: str
    raw_text: str  # the source's own words — never edited or summarized here
    affected_capability: str  # short factual label, e.g. "200K context window"
    capability_keywords: list[str] = field(default_factory=list)  # clustering + relevance input
    practical_impact_note: str = ""  # the capture step's own factual note on why this might matter;
    # still written by a human/executor at capture time, kept in a
    # separate field from raw_text so it is never confused with a
    # verbatim quote from the source itself


@dataclass
class Evidence:
    """The EVIDENCE stage: a specific, citable pointer back to a
    RawCapture. Never contains interpretation — that lives on Signal
    (summary / practical_impact), kept structurally separate."""

    source_name: str
    source_url: str
    source_trust: str  # TrustLevel
    quoted_text: str

    def citation(self) -> str:
        return f"{self.source_name} ({self.source_trust}) — \"{self.quoted_text}\" [{self.source_url}]"


@dataclass
class Signal:
    """One entry in the Signal Registry. All 13 fields EXEC-008's own
    Signal Model section names are present and required; nothing here
    is optional. Corresponds to the CLAIM/INTERPRETATION/ACTION stages
    of the Evidence Discipline — summary and practical_impact are this
    tool's own structured interpretation, kept in separate fields from
    the raw `evidence` list so a reader can never confuse "what the
    source said" with "what this tool concluded from it."""

    signal_id: str  # RS-000N, persistent across runs — see registry.py
    timestamp: str  # ISO-8601 UTC, first-seen time
    source: str  # primary source name (may be a cluster of several — see evidence)
    source_trust: str  # TrustLevel of the primary/highest-trust source
    category: str  # Category
    affected_capability: str
    affected_projects: list[str]  # Project.ALL members, or [Project.WATCH]
    evidence: list[Evidence]
    summary: str  # this tool's own structured summary — INTERPRETATION, not FACT
    practical_impact: str  # INTERPRETATION: why this might matter
    confidence: str  # Confidence
    urgency: str  # Urgency
    recommended_action: str  # ACTION stage — always advisory, never performed
    key: str = ""  # dedup/reuse key — internal, not part of the public schema
    first_seen: str = ""
    last_seen: str = ""
    times_seen: int = 1

    def evidence_citations(self) -> list[str]:
        return [e.citation() for e in self.evidence]
