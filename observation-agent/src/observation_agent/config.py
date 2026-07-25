"""Load and validate the agent's configuration.

Deliberately JSON, not YAML — avoids adding a third-party dependency
(PyYAML is not installed in this environment) for something the
stdlib already does. Per PROP-0001's own fixed-scope rule, the
repository list is read from this file, never discovered dynamically
and never expanded at run time.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RepoConfig:
    name: str
    path: str
    state_file_candidates: list[str]


@dataclass
class AgentConfig:
    repos: list[RepoConfig]
    stale_threshold_days: int
    excluded_dirs: list[str]
    markdown_extensions: list[str]
    reference_extensions: list[str]


def load_config(config_path: str | Path) -> AgentConfig:
    config_path = Path(config_path)
    with open(config_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    repos = [
        RepoConfig(
            name=r["name"],
            path=r["path"],
            state_file_candidates=r.get("state_file_candidates", []),
        )
        for r in raw["repos"]
    ]

    return AgentConfig(
        repos=repos,
        stale_threshold_days=raw.get("stale_threshold_days", 3),
        excluded_dirs=raw.get("excluded_dirs", [".git"]),
        markdown_extensions=raw.get("markdown_extensions", [".md"]),
        reference_extensions=raw.get(
            "reference_extensions", [".md", ".py", ".yaml", ".yml"]
        ),
    )
