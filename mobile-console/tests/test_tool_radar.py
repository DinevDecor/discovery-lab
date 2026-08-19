import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = REPO_ROOT / "tool-radar" / "data" / "tool_signals.jsonl"
BUILDER = REPO_ROOT / "mobile-console" / "scripts" / "build_tool_radar.py"


class ToolRadarStreamTests(unittest.TestCase):
    def setUp(self):
        self.rows = [json.loads(line) for line in LEDGER.read_text(encoding="utf-8").splitlines() if line.strip()]

    def test_seed_stream_is_nonempty_and_unique(self):
        self.assertGreater(len(self.rows), 0)
        ids = [r["signal_id"] for r in self.rows]
        self.assertEqual(len(ids), len(set(ids)))
        pairs = [(r["source_email_id"], r["product"]) for r in self.rows]
        self.assertEqual(len(pairs), len(set(pairs)))

    def test_required_fields_and_use_types(self):
        required = {
            "signal_id", "source_email_id", "source_email_ts", "source_subject", "product",
            "source_description", "project_fit_en", "project_fit_bg", "use_type",
            "build_vs_buy_en", "build_vs_buy_bg", "why_it_matters_en", "why_it_matters_bg",
            "cheapest_test_en", "cheapest_test_bg", "risk_overlap_en", "risk_overlap_bg",
            "verdict_en", "verdict_bg", "recorded_at",
        }
        allowed = {"USE_NOW", "CHEAP_TEST", "COMPETITIVE_ARCHAEOLOGY", "WATCH", "IGNORE"}
        for row in self.rows:
            self.assertTrue(required.issubset(row), row.get("signal_id"))
            self.assertIn(row["use_type"], allowed)

    def test_builder_is_local_and_read_only_against_source_stream(self):
        text = BUILDER.read_text(encoding="utf-8")
        self.assertIn('"tool-radar" / "data" / "tool_signals.jsonl"', text)
        self.assertIn('"mobile-console" / "site" / "tool-radar.json"', text)
        self.assertNotIn("urllib", text)
        self.assertNotIn("requests", text)
        self.assertNotIn("business-candidate-analyst", text)
        self.assertNotIn("constraint-archaeology-agents", text)


if __name__ == "__main__":
    unittest.main()
