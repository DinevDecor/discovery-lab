import os, sys, unittest
from types import SimpleNamespace
ROOT=os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0,os.path.join(ROOT,"src"))
from ca_agents.sensor import cap_confidence_for_source, _SOLUTION_SIGNAL_CONFIDENCE_CAP, _source_event_id


class TestConfidenceCap(unittest.TestCase):
    def test_product_hunt_high_confidence_is_capped(self):
        self.assertEqual(cap_confidence_for_source("product_hunt", 0.95), _SOLUTION_SIGNAL_CONFIDENCE_CAP)

    def test_product_hunt_low_confidence_not_raised(self):
        self.assertEqual(cap_confidence_for_source("product_hunt", 0.2), 0.2)

    def test_other_sources_unaffected(self):
        self.assertEqual(cap_confidence_for_source("hacker_news", 0.95), 0.95)
        self.assertEqual(cap_confidence_for_source("discourse:python", 0.95), 0.95)


class TestSourceEventIdentity(unittest.TestCase):
    def _capture(self, **changes):
        data=dict(source="hacker_news",url="https://example.com/item/42/",title="Title",text="original text",published_at="2026-08-25T06:00:00Z",captured_at="2026-08-25T07:00:00Z")
        data.update(changes)
        return SimpleNamespace(**data)

    def test_identity_ignores_capture_time_and_derived_text(self):
        a=self._capture()
        b=self._capture(captured_at="2026-08-25T09:00:00Z",title="Retitled",text="different extraction input")
        self.assertEqual(_source_event_id(a),_source_event_id(b))

    def test_trailing_slash_does_not_change_identity(self):
        self.assertEqual(_source_event_id(self._capture(url="https://example.com/item/42/")),_source_event_id(self._capture(url="https://example.com/item/42")))

    def test_different_source_event_changes_identity(self):
        self.assertNotEqual(_source_event_id(self._capture()),_source_event_id(self._capture(url="https://example.com/item/43")))


if __name__ == "__main__":
    unittest.main()
