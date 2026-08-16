"""End-to-end regression test for the 2026-08-15-5 correction
(REAL-CASE-001 finding #1): a submission carrying only RAW,
evidence-backed inputs must produce real DERIVED specialist outputs
(g_r_days, g_d_novo_days, g_d_active_days, s_ready, rivalry_index) in the
ledger and snapshot after `cli.cmd_add` runs - without the submitter
computing any of those numbers by hand.

Before the fix, `cmd_add` never called `specialist.derive_assessment`
(which didn't exist) or any of the individual `compute_*` functions -
every derived field stayed at its empty INSUFFICIENT_DATA default no
matter what raw evidence a submission carried. This test would have
FAILED against the pre-fix code (every assertion below on a `.value`
would have seen `None` and every `evidence_status` would have read
INSUFFICIENT_DATA instead of OBSERVED).

Dates are computed relative to the real wall-clock "today" (matching
`cli._today_iso()`, which this test does not mock) so the test stays
valid regardless of which day it runs on.
"""

import _pathsetup  # noqa: F401
import datetime as dt
import json
import os
import shutil
import tempfile
import unittest

from calendar_arbitrage_watch import cli, ledger
from calendar_arbitrage_watch.models import OBSERVED, INSUFFICIENT_DATA


def _iso(days_from_today: int) -> str:
    return (dt.date.today() + dt.timedelta(days=days_from_today)).isoformat()


def _raw_submission() -> dict:
    """A submission with ONLY raw inputs asserted - no g_r_days,
    g_d_novo_days, g_d_active_days, s_ready, or rivalry_index anywhere.
    Chosen so every derived quantity works out to a clean, hand-checkable
    number: shock 100 days out, our own l_remaining=50 (G_r=+50),
    l_irr_denovo=80 (G_d^novo=80-100=-20), one competitor already 30 days
    from finishing with 30 MW capacity (ready, since 30<=100) against
    d_shock=100 MW / s_existing=20 MW (S_ready=30, RI=100/(20+30)=2.0)."""
    return {
        "candidate_id": "derivation-regression-0001",
        "mode": "DISCOVERY",
        "category": "regulatory_clock",
        "title": "Derivation regression fixture - raw inputs only",
        "evidence_ids": ["synthetic-derivation-regression"],
        "shock_forecast": {
            "shock_type": "DATED",
            "date_bound": {"earliest": _iso(100), "latest": _iso(100), "evidence_status": OBSERVED},
        },
        "readiness": {
            "l_remaining_days": {"value": 50, "unit": "days", "evidence_status": OBSERVED},
        },
        "defensive": {
            "l_irr_denovo": {"value": 80, "unit": "days", "evidence_status": OBSERVED},
            "tracked_competitor": {
                "competitor_id": "rival-1",
                "l_min_remaining_as_of": {"value": 30, "unit": "days", "evidence_status": OBSERVED},
            },
        },
        "rivalry": {
            "unit": "MW",
            "d_shock": {"value": 100, "unit": "MW", "evidence_status": OBSERVED},
            "s_existing": {"value": 20, "unit": "MW", "evidence_status": OBSERVED},
            "competitors": [
                {
                    "competitor_id": "rival-1",
                    "l_min_remaining_as_of": {"value": 30, "unit": "days", "evidence_status": OBSERVED},
                    "q": {"value": 30, "unit": "MW", "evidence_status": OBSERVED},
                },
            ],
        },
    }


class DerivationWiredIntoCliTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.tmpdir, "data"))
        os.makedirs(os.path.join(self.tmpdir, "reports"))
        self.submission_path = os.path.join(self.tmpdir, "submission.json")
        with open(self.submission_path, "w", encoding="utf-8") as f:
            json.dump(_raw_submission(), f)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _current_record(self) -> dict:
        led = ledger.CalendarLedger(os.path.join(self.tmpdir, "data", "calendar_events.jsonl"))
        snapshot = ledger.rebuild_snapshot(led.all_entries())
        self.assertEqual(len(snapshot["current"]), 1)
        return snapshot["current"][0]

    def test_g_r_days_is_derived_not_insufficient_data(self):
        cli.cmd_add(self.tmpdir, [self.submission_path])
        record = self._current_record()
        g_r = record["readiness"]["g_r_days"]
        self.assertEqual(g_r["evidence_status"], OBSERVED)
        self.assertEqual(g_r["value"], 50.0)

    def test_g_d_novo_days_is_derived_not_insufficient_data(self):
        cli.cmd_add(self.tmpdir, [self.submission_path])
        record = self._current_record()
        g_d_novo = record["defensive"]["g_d_novo_days"]
        self.assertEqual(g_d_novo["evidence_status"], OBSERVED)
        self.assertEqual(g_d_novo["value"], -20.0)

    def test_g_d_active_days_is_derived_not_insufficient_data(self):
        cli.cmd_add(self.tmpdir, [self.submission_path])
        record = self._current_record()
        g_d_active = record["defensive"]["g_d_active_days"]
        self.assertEqual(g_d_active["evidence_status"], OBSERVED)
        self.assertEqual(g_d_active["value"], -20.0)

    def test_s_ready_is_derived_not_insufficient_data(self):
        cli.cmd_add(self.tmpdir, [self.submission_path])
        record = self._current_record()
        s_ready = record["rivalry"]["s_ready"]
        self.assertEqual(s_ready["evidence_status"], OBSERVED)
        self.assertEqual(s_ready["value"], 30.0)

    def test_rivalry_index_is_derived_not_insufficient_data(self):
        cli.cmd_add(self.tmpdir, [self.submission_path])
        record = self._current_record()
        ri = record["rivalry"]["rivalry_index"]
        self.assertEqual(ri["evidence_status"], OBSERVED)
        self.assertEqual(ri["value"], 2.0)

    def test_submitter_never_asserted_any_derived_field_themselves(self):
        """Sanity check on the fixture itself: proves the derived values
        above could only have come from the CLI's own derivation step,
        not from the submission JSON, which contains no g_r_days,
        g_d_novo_days, g_d_active_days, s_ready, or rivalry_index key
        anywhere."""
        with open(self.submission_path, encoding="utf-8") as f:
            raw_text = f.read()
        for forbidden in ("g_r_days", "g_d_novo_days", "g_d_active_days", "s_ready", "rivalry_index"):
            self.assertNotIn(forbidden, raw_text)

    def test_gate_reads_the_derived_competitive_picture_not_empty_defaults(self):
        """Before the fix, the gate's Rule 4 always saw both defensive
        gaps as INSUFFICIENT_DATA (nothing derived them), regardless of
        competitor evidence in the submission - exactly the REAL-CASE-001
        symptom. With derivation wired in, a submission that DOES supply
        competitor evidence must not be killed by Rule 4 for that reason."""
        cli.cmd_add(self.tmpdir, [self.submission_path])
        record = self._current_record()
        self.assertNotIn("no competitive picture asserted", record["lifecycle_reason"])

    def test_missing_raw_input_still_yields_insufficient_data_not_fabrication(self):
        """The other half of the contract: an input genuinely not
        supplied must still come out INSUFFICIENT_DATA, never a
        fabricated number, even after wiring in derivation."""
        data = _raw_submission()
        del data["defensive"]["l_irr_denovo"]
        path = os.path.join(self.tmpdir, "no_l_irr.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        cli.cmd_add(self.tmpdir, [path])
        led = ledger.CalendarLedger(os.path.join(self.tmpdir, "data", "calendar_events.jsonl"))
        snapshot = ledger.rebuild_snapshot(led.all_entries())
        record = snapshot["current"][0]
        g_d_novo = record["defensive"]["g_d_novo_days"]
        self.assertEqual(g_d_novo["evidence_status"], INSUFFICIENT_DATA)
        self.assertIsNone(g_d_novo["value"])


if __name__ == "__main__":
    unittest.main()
