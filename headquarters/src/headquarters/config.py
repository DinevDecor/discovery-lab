"""Load and validate config.json. JSON, not YAML — same reasoning as
observation-agent/src/observation_agent/config.py: no third-party
dependency for the handful of fields this tool actually reads."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RepoConfig:
    name: str
    path: str
    state_file: str | None
    adr_dir: str | None
    readme: str | None
    changelog: str | None


@dataclass
class ArtifactRef:
    repo: str
    path: str


@dataclass
class HeadquartersConfig:
    repos: list[RepoConfig]
    project_registry: ArtifactRef
    recommendation_ledger: ArtifactRef
    observation_agent_reports_dir: ArtifactRef
    governance_doc: ArtifactRef
    proposals_dir: ArtifactRef
    decision_backlog_threshold_days: int
    stale_adr_threshold_days: int

    def repo_by_name(self, name: str) -> RepoConfig | None:
        for r in self.repos:
            if r.name == name:
                return r
        return None

    def repo_path(self, ref: ArtifactRef) -> Path:
        repo = self.repo_by_name(ref.repo)
        base = Path(repo.path) if repo else Path(".")
        return base / ref.path


def load_config(config_path: str | Path) -> HeadquartersConfig:
    config_path = Path(config_path)
    with open(config_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    repos = [
        RepoConfig(
            name=r["name"],
            path=r["path"],
            state_file=r.get("state_file"),
            adr_dir=r.get("adr_dir"),
            readme=r.get("readme"),
            changelog=r.get("changelog"),
        )
        for r in raw["repos"]
    ]

    def ref(key: str) -> ArtifactRef:
        d = raw[key]
        return ArtifactRef(repo=d["repo"], path=d["path"])

    return HeadquartersConfig(
        repos=repos,
        project_registry=ref("project_registry"),
        recommendation_ledger=ref("recommendation_ledger"),
        observation_agent_reports_dir=ref("observation_agent_reports_dir"),
        governance_doc=ref("governance_doc"),
        proposals_dir=ref("proposals_dir"),
        decision_backlog_threshold_days=raw.get("decision_backlog_threshold_days", 3),
        stale_adr_threshold_days=raw.get("stale_adr_threshold_days", 30),
    )
