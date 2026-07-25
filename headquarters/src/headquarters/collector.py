"""Reads existing artifacts. Reads only — no repository is scanned
file-by-file here; every path this module opens is a specific,
pre-configured artifact location (a state file, a registry, an ADR
directory's own file listing, the Observation Agent's own latest
report). That is the boundary between this tool and observation-agent:
observation-agent is the sensor that walks repositories; Headquarters
only ever reads what already exists."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .config import HeadquartersConfig, RepoConfig
from .parsing import (
    extract_fenced_blocks,
    first_paragraph_after_title,
    parse_fenced_key_values,
    parse_markdown_table,
    parse_state_fields,
)


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


@dataclass
class RepoSnapshot:
    name: str
    path: str
    state_fields: dict[str, str]
    state_file_path: str | None
    purpose: str | None
    adr_files: list[tuple[str, float]]  # (filename, mtime)
    changelog_lines: int | None


@dataclass
class ObservationAgentSnapshot:
    report_path: str | None
    log_path: str | None
    confidence_counts: dict[str, int]
    scanned_repos: list[str]
    skipped_repos: list[str]
    human_decisions: list[str]


@dataclass
class LedgerEntry:
    fields: dict[str, str]


@dataclass
class Collected:
    repos: dict[str, RepoSnapshot]
    project_registry_headers: list[str]
    project_registry_rows: list[list[str]]
    ledger_entries: list[LedgerEntry]
    ledger_metrics: dict[str, str]
    observation: ObservationAgentSnapshot
    governance_doc_present: bool
    proposal_dirs: list[str]


def collect_repo(repo: RepoConfig) -> RepoSnapshot:
    root = Path(repo.path)
    state_fields: dict[str, str] = {}
    state_file_path = None
    if repo.state_file:
        p = root / repo.state_file
        text = _read(p)
        if text is not None:
            state_fields = parse_state_fields(text)
            state_file_path = repo.state_file

    purpose = None
    if repo.readme:
        text = _read(root / repo.readme)
        if text is not None:
            purpose = first_paragraph_after_title(text)

    adr_files: list[tuple[str, float]] = []
    if repo.adr_dir:
        adr_path = root / repo.adr_dir
        if adr_path.is_dir():
            for p in sorted(adr_path.iterdir()):
                if p.is_file() and p.suffix == ".md":
                    try:
                        adr_files.append((p.name, p.stat().st_mtime))
                    except OSError:
                        continue

    changelog_lines = None
    if repo.changelog:
        text = _read(root / repo.changelog)
        if text is not None:
            changelog_lines = len(text.splitlines())

    return RepoSnapshot(
        name=repo.name,
        path=repo.path,
        state_fields=state_fields,
        state_file_path=state_file_path,
        purpose=purpose,
        adr_files=adr_files,
        changelog_lines=changelog_lines,
    )


def collect_project_registry(config: HeadquartersConfig) -> tuple[list[str], list[list[str]]]:
    path = config.repo_path(config.project_registry)
    text = _read(path)
    if text is None:
        return [], []
    return parse_markdown_table(text)


def collect_ledger(config: HeadquartersConfig) -> tuple[list[LedgerEntry], dict[str, str]]:
    path = config.repo_path(config.recommendation_ledger)
    text = _read(path)
    if text is None:
        return [], {}

    entries: list[LedgerEntry] = []
    metrics: dict[str, str] = {}
    for block in extract_fenced_blocks(text):
        fields = parse_fenced_key_values(block)
        if "recommendation_id" in fields:
            entries.append(LedgerEntry(fields=fields))
        elif "total" in fields:
            metrics = fields
    return entries, metrics


def collect_observation_agent(config: HeadquartersConfig) -> ObservationAgentSnapshot:
    reports_dir = config.repo_path(config.observation_agent_reports_dir)
    if not reports_dir.is_dir():
        return ObservationAgentSnapshot(None, None, {}, [], [], [])

    reports = sorted(reports_dir.glob("observation-report-*.md"))
    logs = sorted(reports_dir.glob("execution-log-*.md"))
    report_path = reports[-1] if reports else None
    log_path = logs[-1] if logs else None

    confidence_counts: dict[str, int] = {}
    human_decisions: list[str] = []
    if report_path is not None:
        text = _read(report_path) or ""
        m = re.search(
            r"MATCH:\s*(\d+)\s*\S\s*MISMATCH:\s*(\d+)\s*\S\s*INSUFFICIENT_EVIDENCE:\s*(\d+)",
            text,
        )
        if m:
            confidence_counts = {
                "MATCH": int(m.group(1)),
                "MISMATCH": int(m.group(2)),
                "INSUFFICIENT_EVIDENCE": int(m.group(3)),
            }
        section = re.search(
            r"## Human Decisions Required\n(.*?)(?:\n## |\Z)", text, re.DOTALL
        )
        if section:
            human_decisions = [
                line.strip("- ").strip()
                for line in section.group(1).splitlines()
                if line.strip().startswith("-")
            ]

    scanned: list[str] = []
    skipped: list[str] = []
    if log_path is not None:
        log_text = _read(log_path) or ""
        for line in log_text.splitlines():
            m = re.match(r"^- SCAN ([^:]+):", line)
            if m:
                scanned.append(m.group(1).strip())
            m = re.match(r"^- SKIP ([^:]+):", line)
            if m:
                skipped.append(m.group(1).strip())

    return ObservationAgentSnapshot(
        report_path=str(report_path) if report_path else None,
        log_path=str(log_path) if log_path else None,
        confidence_counts=confidence_counts,
        scanned_repos=scanned,
        skipped_repos=skipped,
        human_decisions=human_decisions,
    )


def collect(config: HeadquartersConfig) -> Collected:
    repos = {r.name: collect_repo(r) for r in config.repos}
    registry_headers, registry_rows = collect_project_registry(config)
    ledger_entries, ledger_metrics = collect_ledger(config)
    observation = collect_observation_agent(config)

    governance_path = config.repo_path(config.governance_doc)
    governance_present = governance_path.is_file()

    proposals_path = config.repo_path(config.proposals_dir)
    proposal_dirs: list[str] = []
    if proposals_path.is_dir():
        proposal_dirs = sorted(
            p.name for p in proposals_path.iterdir() if p.is_dir()
        )

    return Collected(
        repos=repos,
        project_registry_headers=registry_headers,
        project_registry_rows=registry_rows,
        ledger_entries=ledger_entries,
        ledger_metrics=ledger_metrics,
        observation=observation,
        governance_doc_present=governance_present,
        proposal_dirs=proposal_dirs,
    )
