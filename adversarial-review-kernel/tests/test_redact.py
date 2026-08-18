import _pathsetup  # noqa: F401
import unittest

from adversarial_review_kernel.models import Disagreement
from adversarial_review_kernel.redact import redact_for_critic


def _disagreements():
    return [
        Disagreement(field="carrier", claude_value="CLAUDE_CARRIER", gpt_value="GPT_CARRIER",
                     claude_artifact_id="analysis:c", gpt_artifact_id="analysis:g"),
        Disagreement(field="confidence", claude_value=0.92, gpt_value=0.0,
                     claude_artifact_id="analysis:c", gpt_artifact_id="analysis:g"),
    ]


class RedactForCriticTests(unittest.TestCase):
    def test_claude_critic_sees_only_gpt_values(self):
        redacted = redact_for_critic(_disagreements(), critic_is_claude=True)
        values = [r["target_value"] for r in redacted]
        self.assertIn("GPT_CARRIER", values)
        self.assertIn(0.0, values)
        self.assertNotIn("CLAUDE_CARRIER", values)
        self.assertNotIn(0.92, values)

    def test_gpt_critic_sees_only_claude_values(self):
        redacted = redact_for_critic(_disagreements(), critic_is_claude=False)
        values = [r["target_value"] for r in redacted]
        self.assertIn("CLAUDE_CARRIER", values)
        self.assertIn(0.92, values)
        self.assertNotIn("GPT_CARRIER", values)
        self.assertNotIn(0.0, values)

    def test_redacted_entries_have_exactly_two_keys(self):
        for r in redact_for_critic(_disagreements(), critic_is_claude=True):
            self.assertEqual(set(r.keys()), {"field", "target_value"})

    def test_field_order_and_names_preserved(self):
        redacted = redact_for_critic(_disagreements(), critic_is_claude=True)
        self.assertEqual([r["field"] for r in redacted], ["carrier", "confidence"])

    def test_no_artifact_id_leaks_into_the_redacted_view(self):
        """Extra defense: the redacted view a Falsifier sees should not
        even carry artifact ids that could hint which provider is which
        beyond what the prompt template itself explicitly states."""
        for r in redact_for_critic(_disagreements(), critic_is_claude=True):
            self.assertNotIn("claude_artifact_id", r)
            self.assertNotIn("gpt_artifact_id", r)

    def test_empty_disagreement_list_returns_empty(self):
        self.assertEqual(redact_for_critic([], critic_is_claude=True), [])


if __name__ == "__main__":
    unittest.main()
