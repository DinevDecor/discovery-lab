import _pathsetup  # noqa: F401
import tempfile
import unittest
from pathlib import Path

from observation_agent.models import Confidence, Evidence, Observation
from observation_agent.report import (
    diff_against_previous,
    load_previous_snapshot,
    render_report,
    save_snapshot,
)


def _make_observation(event: str, check_name: str = "orphan_files") -> Observation:
    return Observation(
        event=event,
        evidence=[Evidence(repo="fixture", file_path="x.md", line_number=None, quoted_text="x")],
        verification_method="test",
        confidence=Confidence.MISMATCH,
        possible_interpretation="test",
        recommended_action="fix it",
        human_needed=True,
        check_name=check_name,
    )


class TestReportDiff(unittest.TestCase):
    def test_first_run_everything_is_new(self):
        obs = [_make_observation("finding A")]
        new_obs, repeated_obs, resolved = diff_against_previous(obs, previous={})
        self.assertEqual(len(new_obs), 1)
        self.assertEqual(repeated_obs, [])
        self.assertEqual(resolved, [])

    def test_snapshot_roundtrip_and_repeat_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            snapshot_path = Path(tmp) / "snap.json"
            obs = [_make_observation("finding A")]
            save_snapshot(snapshot_path, obs)

            previous = load_previous_snapshot(snapshot_path)
            new_obs, repeated_obs, resolved = diff_against_previous(obs, previous)
            self.assertEqual(new_obs, [])
            self.assertEqual(len(repeated_obs), 1)
            self.assertEqual(resolved, [])

    def test_resolved_finding_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            snapshot_path = Path(tmp) / "snap.json"
            save_snapshot(snapshot_path, [_make_observation("finding A")])
            previous = load_previous_snapshot(snapshot_path)

            new_obs, repeated_obs, resolved = diff_against_previous([], previous)
            self.assertEqual(new_obs, [])
            self.assertEqual(repeated_obs, [])
            self.assertEqual(len(resolved), 1)

    def test_render_report_produces_all_required_sections(self):
        obs = [_make_observation("finding A")]
        text = render_report(obs, obs, [], [], scanned_repos=["fixture"], skipped_repos=[])
        for heading in [
            "## Summary",
            "## New Observations",
            "## Repeated Findings",
            "## Resolved Findings",
            "## Risk Changes",
            "## Confidence",
            "## Evidence Links",
            "## Recommended Actions",
            "## Human Decisions Required",
        ]:
            self.assertIn(heading, text)

    def test_render_report_never_prints_a_single_aggregate_score(self):
        obs = [_make_observation("finding A")]
        text = render_report(obs, obs, [], [], scanned_repos=["fixture"], skipped_repos=[])
        self.assertIn("No single aggregate score", text)


if __name__ == "__main__":
    unittest.main()
