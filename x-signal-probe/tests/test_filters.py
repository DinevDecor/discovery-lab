import _pathsetup  # noqa: F401
import unittest

from x_signal_probe import filters


class RetweetTests(unittest.TestCase):
    def test_rt_prefix_detected(self):
        self.assertTrue(filters.is_retweet("RT @someone: our bill exploded"))

    def test_referenced_type_retweeted_detected(self):
        self.assertTrue(filters.is_retweet("our bill exploded", ("retweeted",)))

    def test_referenced_type_quoted_not_treated_as_retweet(self):
        self.assertFalse(filters.is_retweet("our bill exploded", ("quoted",)))

    def test_normal_post_not_retweet(self):
        self.assertFalse(filters.is_retweet("our bill exploded this month", ()))


class MarketingTests(unittest.TestCase):
    def test_marketing_phrase_detected(self):
        self.assertTrue(filters.is_marketing_like("Check out our new tool, sign up today!"))

    def test_link_heavy_post_detected(self):
        text = "see https://a.example https://b.example https://c.example"
        self.assertTrue(filters.is_marketing_like(text))

    def test_single_link_not_treated_as_marketing(self):
        text = "our bill tripled this month, wrote it up here https://a.example"
        self.assertFalse(filters.is_marketing_like(text))

    def test_plain_problem_report_not_marketing(self):
        self.assertFalse(filters.is_marketing_like("our AWS bill tripled and nobody knows why"))


class FirstPersonHintTests(unittest.TestCase):
    def test_first_person_detected(self):
        self.assertTrue(filters.is_first_person_report("our bill tripled and we had no warning"))

    def test_third_person_not_flagged(self):
        self.assertFalse(filters.is_first_person_report("that company had a rough month apparently"))


if __name__ == "__main__":
    unittest.main()
