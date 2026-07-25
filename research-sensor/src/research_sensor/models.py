"""Data model for the Research Reality Sensor's Research Signal
Registry.

Field names and vocabularies implement EXEC-010's own spec exactly:
the 14-field Research Signal Model, the 5 Primary Observation Domains,
the publication-quality-based Trust Policy, and the Experiment
Extraction structure. This module does not invent a schema.
"""

from __future__ import annotations

from dataclasses import dataclass, field


class SourceTrust:
    """EXEC-010's own 3-tier Source priority order. Distinct from
    EvidenceLevel below: this classifies the *source* (where a capture
    came from); EvidenceLevel classifies the *paper's own* evidentiary
    strength, which a PRIMARY-source capture can still report as merely
    a preprint."""

    PRIMARY = "PRIMARY"      # arXiv, OpenReview, Nature, Science, ACL, NeurIPS, ICML, ICLR
    SECONDARY = "SECONDARY"  # official research blogs, laboratory publications
    COMMUNITY = "COMMUNITY"  # discovery hints only - never citable evidence alone

    ALL = (PRIMARY, SECONDARY, COMMUNITY)


class EvidenceLevel:
    """Closed vocabulary driving Confidence, per EXEC-010's Trust
    Policy: "Confidence depends on: publication quality, peer review
    status, independent replication, evidence strength. Never on
    popularity." """

    PEER_REVIEWED_PUBLISHED = "PEER_REVIEWED_PUBLISHED"    # Nature, Science, a journal
    PEER_REVIEWED_ACCEPTED = "PEER_REVIEWED_ACCEPTED"        # ACL/NeurIPS/ICML/ICLR accepted paper
    NOTABLE_LAB_PREPRINT = "NOTABLE_LAB_PREPRINT"            # arXiv/OpenReview, recognized lab
    PREPRINT = "PREPRINT"                                     # arXiv/OpenReview, not independently placed
    COMMUNITY_HINT = "COMMUNITY_HINT"                         # mention only, not itself citable
    UNKNOWN = "UNKNOWN"

    ALL = (
        PEER_REVIEWED_PUBLISHED,
        PEER_REVIEWED_ACCEPTED,
        NOTABLE_LAB_PREPRINT,
        PREPRINT,
        COMMUNITY_HINT,
        UNKNOWN,
    )


class Domain:
    """The 5 Primary Observation Domains (A-E), closed by design -
    EXEC-010 names exactly these five for this sensor."""

    AI_FOR_SCIENTIFIC_DISCOVERY = "AI_FOR_SCIENTIFIC_DISCOVERY"
    MULTI_AGENT_RESEARCH = "MULTI_AGENT_RESEARCH"
    KNOWLEDGE_SYSTEMS = "KNOWLEDGE_SYSTEMS"
    VALIDATION_METHODOLOGY = "VALIDATION_METHODOLOGY"
    COGNITIVE_ARCHITECTURES = "COGNITIVE_ARCHITECTURES"

    ALL = (
        AI_FOR_SCIENTIFIC_DISCOVERY,
        MULTI_AGENT_RESEARCH,
        KNOWLEDGE_SYSTEMS,
        VALIDATION_METHODOLOGY,
        COGNITIVE_ARCHITECTURES,
    )


class Confidence:
    """Independently chosen for this sensor's own domain - EXEC-009's
    Human Acceptance explicitly ruled out a *unified* confidence
    vocabulary across sensors, not similarity between them. HIGH can
    never be reached from COMMUNITY_HINT evidence alone - see
    trust.py."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

    ALL = (HIGH, MEDIUM, LOW, INSUFFICIENT_EVIDENCE)


class Project:
    """The 5 Discovery Lab projects EXEC-010's own Relation to
    Existing Projects section names, plus WATCH for "no project
    applies yet" - never force relevance where none exists."""

    KOD = "KOD"
    DISCOVERY_LAB = "Discovery Lab"
    TRUST_ENGINE = "Trust Engine"
    GENERATIVE_DISCOVERY_ENGINE = "Generative Discovery Engine"
    DINEV_ASSISTANT = "Dinev Assistant"
    WATCH = "WATCH"

    NAMED = (KOD, DISCOVERY_LAB, TRUST_ENGINE, GENERATIVE_DISCOVERY_ENGINE, DINEV_ASSISTANT)
    ALL = NAMED + (WATCH,)


@dataclass
class RawPaperCapture:
    """One fetched paper, before any interpretation - the FACT/CLAIM
    stage. Produced by the capture step (see ARCHITECTURE.md),
    consumed only by dedup.py/cli.py - never appears in the Research
    Signal Registry itself."""

    title: str
    authors: list[str]
    publication: str          # venue name, e.g. "arXiv", "NeurIPS 2026", "Nature"
    date: str                 # ISO-8601 date the paper/version was published
    source_name: str
    source_url: str
    source_trust: str         # SourceTrust
    evidence_level: str       # EvidenceLevel - the capturer's own classification;
                               # trust.py may not upgrade it, only cap confidence
    domain: str                # Domain
    raw_abstract: str          # the paper's own words - never edited or summarized here
    problem_addressed: str     # factual, capture-time note: what problem this paper targets
    main_contribution: str     # factual, capture-time note: what the paper actually did
    idea_keywords: list[str] = field(default_factory=list)  # clustering + relevance input
    architectural_relevance_note: str = ""  # capture-time judgment: why this might matter
    possible_experiment_notes: list[dict] = field(default_factory=list)
    # each dict: {"description", "expected_benefit", "uncertainty",
    #             "prerequisites", "validation_idea"} - see experiments.py


@dataclass
class Citation:
    """Provenance for a ResearchSignal - preserves "research provenance
    is preserved" (EXEC-010's own PASS criterion) the same structural
    way Evidence does in observation-agent/reality-sensor: a citable,
    provenance-tagged record, never merged with interpretation."""

    title: str
    authors: list[str]
    publication: str
    date: str
    source_url: str
    source_trust: str
    evidence_level: str
    quoted_abstract: str

    def citation(self) -> str:
        author_str = ", ".join(self.authors) if self.authors else "unknown authors"
        return (
            f"{self.title} — {author_str} ({self.publication}, {self.date}) "
            f"[{self.evidence_level}] — \"{self.quoted_abstract}\" [{self.source_url}]"
        )


@dataclass
class PossibleExperiment:
    """EXEC-010's own Experiment Extraction structure, verbatim:
    "at least one possible experiment; expected benefit; uncertainty;
    prerequisites; validation idea." Never an implementation plan -
    experiments.py structurally cannot add a task list, code, or file
    path to this dataclass."""

    description: str
    expected_benefit: str
    uncertainty: str
    prerequisites: str
    validation_idea: str


@dataclass
class ResearchSignal:
    """One entry in the Research Signal Registry. The 14 fields
    EXEC-010's own Research Signal Model names are all present.
    Bookkeeping fields (key/first_seen/last_seen/times_seen) support
    the idempotent registry, mirroring RS-000N/HQ-000N - see
    registry.py."""

    research_id: str               # RES-000N, persistent across runs
    title: str
    authors: list[str]
    publication: str
    date: str
    domain: str                     # Domain
    problem_addressed: str
    main_contribution: str
    evidence_level: str             # EvidenceLevel of the strongest supporting citation
    affected_projects: list[str]    # Project.ALL members, or [Project.WATCH]
    possible_experiments: list[PossibleExperiment]
    architectural_relevance: str    # why this might matter to Discovery Lab - INTERPRETATION
    confidence: str                 # Confidence
    recommended_action: str         # always advisory, never performed
    evidence: list[Citation] = field(default_factory=list)  # provenance, not part of the
    # 14 named fields but required to satisfy "research provenance is preserved"
    key: str = ""                   # dedup/reuse key - internal, not part of the public schema
    first_seen: str = ""
    last_seen: str = ""
    times_seen: int = 1

    def evidence_citations(self) -> list[str]:
        return [e.citation() for e in self.evidence]
