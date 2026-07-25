"""EXEC-006 regression test — proves that a full CLI run, executed
twice in a row against a fixture repository with unchanged real
content, stays stable when the tool's own `reports/` output directory
is excluded via `excluded_paths`: the second run must not discover any
"new" observation attributable to the first run's own report. This is
the exact scenario INV-0004 found broken in EXEC-005's Operational
Validation, reproduced end-to-end through the same `cli.main()` entry
point a human actually invokes, not just at the unit level."""

import _pathsetup  # noqa: F401
import json
import tempfile
import unittest
from pathlib import Path

from observation_agent.cli import main


def _build_fixture_config(base: Path) -> tuple[Path, Path]:
    """Builds a fixture repo whose own `observation-agent/reports/`
    directory — where the CLI is told to write its output — lives
    *inside* the scanned repo, exactly like the real discovery-lab
    layout that produced the original bug. Returns (config_path,
    reports_dir)."""
    repo = base / "some-tool-repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "docs" / "index.md").write_text(
        "# Docs\n\nSee [missing](does-not-exist.md) for details.\n"
    )
    reports_dir = repo / "observation-agent" / "reports"
    reports_dir.mkdir(parents=True)

    config = {
        "repos": [
            {"name": "some-tool-repo", "path": str(repo), "state_file_candidates": []}
        ],
        "stale_threshold_days": 3,
        "excluded_dirs": [".git", "__pycache__"],
        "excluded_paths": ["observation-agent/reports"],
        "markdown_extensions": [".md"],
        "reference_extensions": [".md"],
    }
    config_path = base / "config.json"
    config_path.write_text(json.dumps(config))
    return config_path, reports_dir


class TestRepeatedRunsStayStable(unittest.TestCase):
    def test_second_run_finds_nothing_new_from_the_first_runs_own_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            config_path, reports_dir = _build_fixture_config(base)

            exit_code_1 = main(["--config", str(config_path), "--reports-dir", str(reports_dir)])
            self.assertEqual(exit_code_1, 0)

            snapshot_after_run1 = json.loads((reports_dir / "last_run_observations.json").read_text())

            exit_code_2 = main(["--config", str(config_path), "--reports-dir", str(reports_dir)])
            self.assertEqual(exit_code_2, 0)

            snapshot_after_run2 = json.loads((reports_dir / "last_run_observations.json").read_text())

            # Stability: rerunning against genuinely unchanged repository
            # content (the fixture repo itself was never touched between
            # runs) must not grow the observation count, even though the
            # first run's own report/log/snapshot files now sit inside
            # the scanned repo's own observation-agent/reports/, exactly
            # like the real discovery-lab layout.
            self.assertEqual(len(snapshot_after_run1), len(snapshot_after_run2))

    def test_three_repeated_runs_never_grow_observation_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            config_path, reports_dir = _build_fixture_config(base)

            counts = []
            for _ in range(3):
                main(["--config", str(config_path), "--reports-dir", str(reports_dir)])
                snapshot = json.loads((reports_dir / "last_run_observations.json").read_text())
                counts.append(len(snapshot))

            self.assertEqual(counts[0], counts[1])
            self.assertEqual(counts[1], counts[2])

    def test_without_the_exclusion_the_bug_reproduces(self):
        """Negative control: proves the above tests are exercising a
        real fix, not a scenario that was already impossible. With
        `excluded_paths` removed, the second run must find new content
        from the first run's own report."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            config_path, reports_dir = _build_fixture_config(base)
            unfixed_config = json.loads(config_path.read_text())
            unfixed_config["excluded_paths"] = []
            config_path.write_text(json.dumps(unfixed_config))

            main(["--config", str(config_path), "--reports-dir", str(reports_dir)])
            snapshot_after_run1 = json.loads((reports_dir / "last_run_observations.json").read_text())

            main(["--config", str(config_path), "--reports-dir", str(reports_dir)])
            snapshot_after_run2 = json.loads((reports_dir / "last_run_observations.json").read_text())

            self.assertGreater(
                len(snapshot_after_run2),
                len(snapshot_after_run1),
                "expected the feedback loop to reproduce without excluded_paths",
            )


if __name__ == "__main__":
    unittest.main()
