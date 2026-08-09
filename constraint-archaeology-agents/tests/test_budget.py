import os, sys, unittest
ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(ROOT, "src"))
from ca_agents.budget import allocate_by_source


class TestAllocateBySource(unittest.TestCase):
    def test_low_volume_sources_are_not_starved_by_a_high_volume_one(self):
        # allocate_by_source returns admitted items without their source
        # label attached, so tag each item with its source to attribute
        # admissions back to a source after the fact.
        tagged = {
            "hacker_news": [("hacker_news", i) for i in range(100)],
            "product_hunt": [("product_hunt", i) for i in range(3)],
            "discourse:a": [("discourse:a", i) for i in range(3)],
        }
        admitted = allocate_by_source(tagged, budget=10)
        counts = {"hacker_news": 0, "product_hunt": 0, "discourse:a": 0}
        for name, _ in admitted:
            counts[name] += 1
        # The two low-volume sources have only 3 items each - round robin
        # must admit all of both before giving hacker_news more than its
        # fair share.
        self.assertEqual(counts["product_hunt"], 3)
        self.assertEqual(counts["discourse:a"], 3)
        self.assertEqual(counts["hacker_news"], 4)
        self.assertEqual(len(admitted), 10)

    def test_equal_supply_sources_split_evenly(self):
        tagged = {name: [(name, i) for i in range(20)] for name in ("a", "b", "c", "d")}
        admitted = allocate_by_source(tagged, budget=8)
        counts = {"a": 0, "b": 0, "c": 0, "d": 0}
        for name, _ in admitted:
            counts[name] += 1
        self.assertEqual(counts, {"a": 2, "b": 2, "c": 2, "d": 2})

    def test_within_source_order_is_preserved(self):
        by_source = {"a": ["a0", "a1", "a2"], "b": ["b0", "b1"]}
        admitted = allocate_by_source(by_source, budget=5)
        a_items = [x for x in admitted if x.startswith("a")]
        b_items = [x for x in admitted if x.startswith("b")]
        self.assertEqual(a_items, ["a0", "a1", "a2"])
        self.assertEqual(b_items, ["b0", "b1"])

    def test_budget_smaller_than_source_count_still_bounded_and_deterministic(self):
        by_source = {"a": [1], "b": [1], "c": [1], "d": [1], "e": [1]}
        admitted = allocate_by_source(by_source, budget=2)
        self.assertEqual(len(admitted), 2)

    def test_empty_sources_are_ignored_not_errors(self):
        by_source = {"a": [], "b": [1, 2], "c": []}
        admitted = allocate_by_source(by_source, budget=10)
        self.assertEqual(admitted, [1, 2])

    def test_budget_zero_admits_nothing(self):
        by_source = {"a": [1, 2, 3]}
        self.assertEqual(allocate_by_source(by_source, budget=0), [])

    def test_reproduces_real_sources_json_shape(self):
        """Same source set/volumes as the real config.json that produced the
        production starvation bug: HN(40)+Lobsters(30)+3xDEV(25 each) already
        sums to 145, more than the default budget of 80, before Reddit,
        Product Hunt or Discourse are even considered."""
        by_source = {
            "hacker_news": [("hacker_news", i) for i in range(40)],
            "lobsters": [("lobsters", i) for i in range(30)],
            "dev:discuss": [("dev:discuss", i) for i in range(25)],
            "dev:startup": [("dev:startup", i) for i in range(25)],
            "dev:entrepreneurship": [("dev:entrepreneurship", i) for i in range(25)],
            "product_hunt": [("product_hunt", i) for i in range(20)],
            "discourse:python": [("discourse:python", i) for i in range(20)],
            "discourse:home-assistant": [("discourse:home-assistant", i) for i in range(20)],
            "discourse:openai-devs": [("discourse:openai-devs", i) for i in range(20)],
            "discourse:level1techs": [("discourse:level1techs", i) for i in range(20)],
            "discourse:fly-io": [("discourse:fly-io", i) for i in range(20)],
        }
        admitted = allocate_by_source(by_source, budget=80)
        counts = {}
        for name, _ in admitted:
            counts[name] = counts.get(name, 0) + 1
        for name in by_source:
            self.assertGreater(counts.get(name, 0), 0, f"{name} was starved")
        self.assertEqual(sum(counts.values()), 80)


if __name__ == "__main__":
    unittest.main()
