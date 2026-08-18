import _pathsetup  # noqa: F401
import unittest
from pathlib import Path

from x_signal_probe import existing_sources

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "existing_observations_sample.jsonl"


class LoadTests(unittest.TestCase):
    def test_loads_pain_text_pairs(self):
        pairs = existing_sources.load_existing_pain_texts([str(FIXTURE)])
        self.assertEqual(len(pairs), 2)
        self.assertEqual(pairs[0][0], "OBS-20260810-0001-abcdef")

    def test_missing_path_skipped_not_errored(self):
        pairs = existing_sources.load_existing_pain_texts(["/nonexistent/path.jsonl"])
        self.assertEqual(pairs, [])

    def test_mix_of_missing_and_present_paths(self):
        pairs = existing_sources.load_existing_pain_texts(["/nonexistent/path.jsonl", str(FIXTURE)])
        self.assertEqual(len(pairs), 2)


class MatchTests(unittest.TestCase):
    def setUp(self):
        self.existing = existing_sources.load_existing_pain_texts([str(FIXTURE)])

    def test_finds_match_above_threshold(self):
        match = existing_sources.find_existing_match(
            "our cloud spend keeps spiking and we cannot predict monthly usage costs",
            self.existing,
            threshold=0.15,
        )
        self.assertEqual(match, "OBS-20260810-0001-abcdef")

    def test_no_match_below_threshold_returns_empty_string(self):
        match = existing_sources.find_existing_match(
            "completely unrelated post about gardening tips", self.existing
        )
        self.assertEqual(match, "")

    def test_empty_candidate_text_returns_empty_string(self):
        self.assertEqual(existing_sources.find_existing_match("", self.existing), "")

    def test_empty_existing_corpus_returns_empty_string(self):
        match = existing_sources.find_existing_match("anything at all here", [])
        self.assertEqual(match, "")


if __name__ == "__main__":
    unittest.main()
