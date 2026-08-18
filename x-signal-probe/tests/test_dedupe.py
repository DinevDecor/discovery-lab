import _pathsetup  # noqa: F401
import unittest

from x_signal_probe.dedupe import mark_retrieval_duplicates
from x_signal_probe.models import RawPost


def _post(pid, family="f1"):
    return RawPost(post_id=pid, text="t", created_at="", retrieved_at="", query_id="q1", query_family=family)


class DedupeTests(unittest.TestCase):
    def test_no_duplicates_when_all_ids_unique(self):
        posts = [_post("1"), _post("2"), _post("3")]
        self.assertEqual(mark_retrieval_duplicates(posts), {})

    def test_second_occurrence_marked_first_is_not(self):
        posts = [_post("1"), _post("1")]
        dup = mark_retrieval_duplicates(posts)
        self.assertEqual(dup, {1: True})
        self.assertNotIn(0, dup)

    def test_marks_across_different_query_families(self):
        posts = [_post("1", "f1"), _post("2", "f2"), _post("1", "f2")]
        self.assertEqual(mark_retrieval_duplicates(posts), {2: True})

    def test_three_repeats_marks_only_the_repeats(self):
        posts = [_post("1"), _post("1"), _post("1")]
        self.assertEqual(mark_retrieval_duplicates(posts), {1: True, 2: True})


if __name__ == "__main__":
    unittest.main()
