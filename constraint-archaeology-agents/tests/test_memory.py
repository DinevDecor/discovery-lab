import json, os, sys, tempfile, unittest
ROOT=os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0,os.path.join(ROOT,"src"))
from ca_agents.models import Observation
from ca_agents.memory import rebuild_anomalies, classify_function, append_jsonl, load_jsonl

class TestMemory(unittest.TestCase):
    def obs(self,i,source,process,pain,crosspost_group=""):
        return Observation(f"OBS-{i}",source,"u","d",process,"","human",pain,"failure","quote",.8,str(i),crosspost_group)

    def test_same_pattern_clusters(self):
        rows=[
            self.obs(1,"a","manual invoice reconciliation","same invoice entered manually into systems"),
            self.obs(2,"b","manual invoice reconciliation","invoice manually entered into multiple systems")
        ]
        ans=rebuild_anomalies(rows,threshold=.15)
        self.assertEqual(len(ans),1)
        self.assertEqual(set(ans[0].independent_sources),{"a","b"})

    def test_function_class(self):
        o=self.obs(1,"a","working capital financing","payment delay creates cash flow gap")
        self.assertEqual(classify_function(o),"capital_time_risk")

    def test_crosspost_does_not_inflate_independent_sources(self):
        rows=[
            self.obs(1,"hacker_news","manual invoice reconciliation","same invoice entered manually into systems","STORY-abc"),
            self.obs(2,"lobsters","manual invoice reconciliation","invoice manually entered into multiple systems","STORY-abc"),
        ]
        ans=rebuild_anomalies(rows,threshold=.15)
        self.assertEqual(len(ans),1)
        self.assertEqual(ans[0].independent_sources,["hacker_news"])
        self.assertEqual(len(ans[0].observation_ids),2)

    def test_distinct_stories_still_count_independently(self):
        rows=[
            self.obs(1,"hacker_news","manual invoice reconciliation","same invoice entered manually into systems"),
            self.obs(2,"lobsters","manual invoice reconciliation","invoice manually entered into multiple systems"),
        ]
        ans=rebuild_anomalies(rows,threshold=.15)
        self.assertEqual(set(ans[0].independent_sources),{"hacker_news","lobsters"})

    def test_third_crosspost_of_same_story_still_does_not_inflate(self):
        rows=[
            self.obs(1,"hacker_news","manual invoice reconciliation","same invoice entered manually into systems","STORY-abc"),
            self.obs(2,"lobsters","manual invoice reconciliation","invoice manually entered into multiple systems","STORY-abc"),
            self.obs(3,"dev:discuss","manual invoice reconciliation","invoice typed by hand into three separate systems","STORY-abc"),
        ]
        ans=rebuild_anomalies(rows,threshold=.15)
        self.assertEqual(len(ans),1)
        self.assertEqual(ans[0].independent_sources,["hacker_news"])
        self.assertEqual(len(ans[0].observation_ids),3)

    def test_append_jsonl_skips_existing_observation_id(self):
        with tempfile.TemporaryDirectory() as d:
            path=os.path.join(d,"observations.jsonl")
            first={"observation_id":"OBS-SRC-abc","process":"first phrasing"}
            retry={"observation_id":"OBS-SRC-abc","process":"different LLM phrasing"}
            self.assertEqual(append_jsonl(path,[first]),1)
            self.assertEqual(append_jsonl(path,[retry]),0)
            rows=load_jsonl(path)
            self.assertEqual(rows,[first])

    def test_append_jsonl_dedups_same_id_within_batch(self):
        with tempfile.TemporaryDirectory() as d:
            path=os.path.join(d,"observations.jsonl")
            rows=[{"observation_id":"OBS-SRC-abc","x":1},{"observation_id":"OBS-SRC-abc","x":2}]
            self.assertEqual(append_jsonl(path,rows),1)
            self.assertEqual(len(load_jsonl(path)),1)

if __name__=="__main__":
    unittest.main()
