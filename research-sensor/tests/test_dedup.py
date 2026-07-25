import _pathsetup  # noqa: F401
import unittest

from research_sensor.dedup import cluster
from research_sensor.models import Domain, RawPaperCapture, SourceTrust, EvidenceLevel


def _capture(title, domain, keywords, **overrides):
    base = dict(
        title=title,
        authors=["A. Author"],
        publication="arXiv",
        date="2026-07-10",
        source_name="arXiv cs.AI Recent",
        source_url=f"https://arxiv.org/abs/{title}",
        source_trust=SourceTrust.PRIMARY,
        evidence_level=EvidenceLevel.PREPRINT,
        domain=domain,
        raw_abstract=f"{title} abstract",
        problem_addressed=f"{title} problem",
        main_contribution=f"{title} contribution",
        idea_keywords=keywords,
    )
    base.update(overrides)
    return RawPaperCapture(**base)


class TestDuplicateDetection(unittest.TestCase):
    def test_multiple_papers_supporting_one_idea_become_one_signal(self):
        # EXEC-010: "One research idea -> One research signal."
        a = _capture("PaperA", Domain.AI_FOR_SCIENTIFIC_DISCOVERY, ["hypothesis-generation", "llm"])
        b = _capture("PaperB", Domain.AI_FOR_SCIENTIFIC_DISCOVERY, ["hypothesis-generation", "search"])
        clusters = cluster([a, b])
        self.assertEqual(len(clusters), 1)
        self.assertEqual(len(clusters[0]), 2)

    def test_unrelated_papers_stay_separate(self):
        a = _capture("PaperA", Domain.AI_FOR_SCIENTIFIC_DISCOVERY, ["hypothesis-generation"])
        b = _capture("PaperB", Domain.KNOWLEDGE_SYSTEMS, ["provenance"])
        clusters = cluster([a, b])
        self.assertEqual(len(clusters), 2)

    def test_same_domain_no_shared_idea_stays_separate(self):
        a = _capture("PaperA", Domain.VALIDATION_METHODOLOGY, ["falsification"])
        b = _capture("PaperB", Domain.VALIDATION_METHODOLOGY, ["benchmarking"])
        clusters = cluster([a, b])
        self.assertEqual(len(clusters), 2)

    def test_transitive_clustering(self):
        a = _capture("A", Domain.COGNITIVE_ARCHITECTURES, ["reflection", "meta-reasoning"])
        b = _capture("B", Domain.COGNITIVE_ARCHITECTURES, ["meta-reasoning", "planning"])
        c = _capture("C", Domain.COGNITIVE_ARCHITECTURES, ["planning", "self-improvement"])
        clusters = cluster([a, b, c])
        self.assertEqual(len(clusters), 1)
        self.assertEqual(len(clusters[0]), 3)

    def test_empty_input_gives_empty_clusters(self):
        self.assertEqual(cluster([]), [])


if __name__ == "__main__":
    unittest.main()
