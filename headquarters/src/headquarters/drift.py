"""Strategic Drift Detector. Implements five of the ten drift
categories EXEC-004 names, chosen because each is mechanically
checkable from artifacts this tool already reads — the other five
(overlapping projects, execution-without-specification,
specification-without-execution, architectural contradictions,
duplicated infrastructure beyond the registry-gap case below) would
require semantic judgment across free-text documents that no check
here can honestly claim, so v1.0 does not attempt them. See README's
Limitations. `unparseable_state_files` is a sixth check, added by the
Additional Execution Directive's Data Quality Issue category — it
does not detect a new drift *category* EXEC-004 named, it gives real
coverage to a classification bucket the Inconsistency taxonomy
otherwise had no check for.

Every finding cites the exact file(s) it came from. `MISMATCH` means
mechanically confirmed; `INSUFFICIENT_EVIDENCE` means a real signal
that still needs human interpretation to call a defect. Every finding
here (never an Opportunity) also gets classified by
`inconsistency.py` into Implementation / Documentation / Governance /
Data Quality / Unknown, per the Additional Execution Directive — this
module never silently fixes anything, only records and classifies."""

from __future__ import annotations

import re
from datetime import date, datetime, timezone
from pathlib import Path

from .collector import Collected
from .config import HeadquartersConfig
from .models import Confidence, Evidence, Finding

_ADR_ID = re.compile(r"ADR-(\d+)", re.IGNORECASE)


def duplicate_adr_ids(collected: Collected) -> list[Finding]:
    findings: list[Finding] = []
    for repo_name, snap in collected.repos.items():
        by_id: dict[str, list[str]] = {}
        for filename, _mtime in snap.adr_files:
            m = _ADR_ID.search(filename)
            if m:
                by_id.setdefault(m.group(1), []).append(filename)
        for adr_id, files in by_id.items():
            if len(files) > 1:
                findings.append(
                    Finding(
                        finding_id=f"duplicate-adr-{repo_name}-{adr_id}",
                        category="duplicated_infrastructure",
                        title=f"{repo_name}: two files both claim ADR-{adr_id}",
                        description=(
                            f"{repo_name}'s ADR directory contains {len(files)} files "
                            f"that all parse as ADR-{adr_id}: {', '.join(files)}. "
                            "An ADR ID should identify exactly one decision."
                        ),
                        confidence=Confidence.MISMATCH,
                        evidence=[Evidence(repo_name, f) for f in files],
                        affected=[repo_name],
                    )
                )
    return findings


def stale_adrs(collected: Collected, threshold_days: int, now: date) -> list[Finding]:
    findings: list[Finding] = []
    now_ts = datetime(now.year, now.month, now.day, tzinfo=timezone.utc).timestamp()
    for repo_name, snap in collected.repos.items():
        for filename, mtime in snap.adr_files:
            age_days = (now_ts - mtime) / 86400
            if age_days > threshold_days:
                findings.append(
                    Finding(
                        finding_id=f"stale-adr-{repo_name}-{filename}",
                        category="stale_specification",
                        title=f"{repo_name}/{filename} has not changed in {round(age_days)} day(s)",
                        description=(
                            "File modification time is a known-unreliable signal in "
                            "shallow clones (the same caveat observation-agent's own "
                            "stale_state check documents) — this is a candidate for "
                            "review, not a confirmed defect."
                        ),
                        confidence=Confidence.INSUFFICIENT_EVIDENCE,
                        evidence=[Evidence(repo_name, f"{filename}: mtime age {round(age_days)}d")],
                        affected=[repo_name],
                    )
                )
    return findings


def registry_gaps(collected: Collected, config: HeadquartersConfig) -> list[Finding]:
    """Which configured repos are absent as a row in project-memory's
    own PROJECT_REGISTRY.md — the one cross-repo project list that
    exists in this ecosystem."""
    if not collected.project_registry_rows:
        return [
            Finding(
                finding_id="registry-unreadable",
                category="governance_inconsistency",
                title="project-memory/PROJECT_REGISTRY.md has no readable table",
                description="Expected a Markdown table listing ecosystem projects; none was found.",
                confidence=Confidence.INSUFFICIENT_EVIDENCE,
                evidence=[Evidence("project-memory", config.project_registry.path)],
                affected=["project-memory"],
            )
        ]

    registry_names = " ".join(row[0].lower() for row in collected.project_registry_rows if row)
    findings: list[Finding] = []
    for repo in config.repos:
        slug = repo.name.replace("-", " ")
        if slug.lower() not in registry_names and repo.name.lower() not in registry_names:
            findings.append(
                Finding(
                    finding_id=f"registry-gap-{repo.name}",
                    category="governance_inconsistency",
                    title=f"{repo.name} is not listed in project-memory/PROJECT_REGISTRY.md",
                    description=(
                        f"PROJECT_REGISTRY.md lists {len(collected.project_registry_rows)} "
                        f"project row(s), none matching '{repo.name}'. This repository is "
                        "part of the Observation Agent's fixed 5-repo scope but absent from "
                        "the ecosystem's own project registry."
                    ),
                    confidence=Confidence.MISMATCH,
                    evidence=[Evidence("project-memory", config.project_registry.path)],
                    affected=[repo.name],
                )
            )
    return findings


def decision_backlog_findings(collected: Collected, threshold_days: int, now: date) -> list[Finding]:
    findings: list[Finding] = []
    for e in collected.ledger_entries:
        if e.fields.get("status") != "PROPOSED":
            continue
        d = re.search(r"(\d{4})-(\d{2})-(\d{2})", e.fields.get("date_proposed", ""))
        if not d:
            continue
        proposed = date(int(d.group(1)), int(d.group(2)), int(d.group(3)))
        age = (now - proposed).days
        if age > threshold_days:
            rec_id = e.fields.get("recommendation_id", "?")
            dest = e.fields.get("destination_repository", "?")
            findings.append(
                Finding(
                    finding_id=f"decision-backlog-{rec_id}",
                    category="decision_backlog",
                    title=f"{rec_id} has awaited a decision for {age} day(s)",
                    description=(
                        f"Proposed to {dest} on {e.fields.get('date_proposed')}, status "
                        f"still PROPOSED. {e.fields.get('summary', '')[:160]}"
                    ),
                    confidence=Confidence.MISMATCH,
                    evidence=[Evidence("RECOMMENDATION-LEDGER.md", rec_id)],
                    affected=[dest],
                )
            )
    return findings


def proposals_without_state_reference(collected: Collected, config: HeadquartersConfig) -> list[Finding]:
    """proposals_dir-shaped subdirectories (wherever config points —
    not hardcoded to any one repository) never mentioned anywhere in
    that same repository's own state file — a proxy for "possibly
    abandoned," not proof of it: a finished initiative folded into
    later work without a name-check is indistinguishable from a
    forgotten one using only this signal, so this is always
    INSUFFICIENT_EVIDENCE."""
    owner_repo_name = config.proposals_dir.repo
    owner = collected.repos.get(owner_repo_name)
    state_text = " ".join(owner.state_fields.values()) if owner else ""
    findings: list[Finding] = []
    for dirname in collected.proposal_dirs:
        if dirname.lower() not in state_text.lower():
            findings.append(
                Finding(
                    finding_id=f"unreferenced-proposal-{dirname}",
                    category="possibly_abandoned_initiative",
                    title=f"{config.proposals_dir.path}/{dirname} is not mentioned in {owner_repo_name}'s own state file",
                    description=(
                        "The state file's own narrative fields do not name this "
                        "directory. May simply predate the current narrative window "
                        "rather than being abandoned."
                    ),
                    confidence=Confidence.INSUFFICIENT_EVIDENCE,
                    evidence=[Evidence(owner_repo_name, f"{config.proposals_dir.path}/{dirname}/")],
                    affected=[owner_repo_name],
                )
            )
    return findings


def unparseable_state_files(collected: Collected, config: HeadquartersConfig) -> list[Finding]:
    """A repo has a state file configured and the file exists on disk,
    but this tool's tolerant parsers extracted fewer than 2 fields
    from it — the artifact does not fit the shape any tooling in this
    ecosystem currently expects. A Data Quality signal, not a
    governance one: the file exists, it is just not shaped the way
    `parse_state_fields` can make sense of."""
    findings: list[Finding] = []
    for repo in config.repos:
        if not repo.state_file:
            continue
        path = Path(repo.path) / repo.state_file
        if not path.is_file():
            continue
        snap = collected.repos.get(repo.name)
        if snap and len(snap.state_fields) < 2:
            findings.append(
                Finding(
                    finding_id=f"unparseable-state-{repo.name}",
                    category="data_quality",
                    title=f"{repo.name}/{repo.state_file} exists but yielded fewer than 2 parseable fields",
                    description=(
                        "The file is present but neither the fenced-block nor the "
                        "loose key:value parser could extract a meaningful state "
                        "from it. This may be a genuinely different, valid format "
                        "this tool's parsers simply don't recognize yet — not "
                        "necessarily a defect in the file itself."
                    ),
                    confidence=Confidence.INSUFFICIENT_EVIDENCE,
                    evidence=[Evidence(repo.name, repo.state_file)],
                    affected=[repo.name],
                )
            )
    return findings


def detect_drift(
    collected: Collected, config: HeadquartersConfig, now: date | None = None
) -> list[Finding]:
    now = now or datetime.now(timezone.utc).date()
    findings: list[Finding] = []
    findings += duplicate_adr_ids(collected)
    findings += stale_adrs(collected, config.stale_adr_threshold_days, now)
    findings += registry_gaps(collected, config)
    findings += decision_backlog_findings(collected, config.decision_backlog_threshold_days, now)
    findings += proposals_without_state_reference(collected, config)
    findings += unparseable_state_files(collected, config)
    return findings
