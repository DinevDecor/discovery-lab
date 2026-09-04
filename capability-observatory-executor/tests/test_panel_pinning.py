import _pathsetup  # noqa: F401
import unittest

from capability_observatory_executor.panel_pinning import (
    PinApplicationError,
    apply_pin_proposal,
    propose_pin,
)

PANEL = {
    "panel_version": "2026-08-09-v1",
    "items": [
        {"panel_item_id": "C3-010", "provider": "provider_d_digikey", "source_url": "https://www.digikey.com/",
         "source_url_pinned": False},
    ],
}


class ProposePinTests(unittest.TestCase):
    def test_rejects_a_proposal_with_no_identity_values(self):
        with self.assertRaises(PinApplicationError):
            propose_pin("C3-010", "https://www.digikey.com/product/abc", {}, "automation:x", "found via API")

    def test_valid_proposal(self):
        proposal = propose_pin(
            "C3-010", "https://www.digikey.com/product/abc",
            {"manufacturer": "STMicroelectronics", "mpn": "STM32F103C8T6"},
            "automation:x", "found via DigiKey keyword search", evidence_capture_id="CAP-abc",
        )
        self.assertTrue(proposal.proposed_source_url_pinned)
        self.assertEqual(proposal.evidence_capture_id, "CAP-abc")


class ApplyPinProposalTests(unittest.TestCase):
    def setUp(self):
        self.proposal = propose_pin(
            "C3-010", "https://www.digikey.com/product/abc",
            {"manufacturer": "STMicroelectronics", "mpn": "STM32F103C8T6"},
            "automation:x", "found via DigiKey keyword search",
        )

    def test_refuses_without_a_version_bump(self):
        with self.assertRaises(PinApplicationError):
            apply_pin_proposal(PANEL, self.proposal, new_panel_version="2026-08-09-v1")

    def test_refuses_a_missing_new_version(self):
        with self.assertRaises(PinApplicationError):
            apply_pin_proposal(PANEL, self.proposal, new_panel_version="")

    def test_refuses_an_unknown_panel_item(self):
        unknown_proposal = propose_pin(
            "C3-999", "https://www.digikey.com/product/xyz", {"mpn": "XYZ"}, "automation:x", "n/a",
        )
        with self.assertRaises(PinApplicationError):
            apply_pin_proposal(PANEL, unknown_proposal, new_panel_version="2026-08-23-v2")

    def test_applies_cleanly_with_an_explicit_version_bump(self):
        new_panel = apply_pin_proposal(PANEL, self.proposal, new_panel_version="2026-08-23-v2")
        self.assertEqual(new_panel["panel_version"], "2026-08-23-v2")
        pinned_item = next(i for i in new_panel["items"] if i["panel_item_id"] == "C3-010")
        self.assertTrue(pinned_item["source_url_pinned"])
        self.assertEqual(pinned_item["source_url"], "https://www.digikey.com/product/abc")

    def test_never_mutates_the_input_panel(self):
        apply_pin_proposal(PANEL, self.proposal, new_panel_version="2026-08-23-v2")
        self.assertEqual(PANEL["panel_version"], "2026-08-09-v1")
        self.assertFalse(PANEL["items"][0]["source_url_pinned"])


if __name__ == "__main__":
    unittest.main()
