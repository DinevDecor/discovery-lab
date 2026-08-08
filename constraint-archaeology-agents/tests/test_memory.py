import os, sys, unittest
ROOT=os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0,os.path.join(ROOT,"src"))
from ca_agents.models import Observation
from ca_agents.memory import rebuild_anomalies, classify_function

class TestMemory(unittest.TestCase):
    def obs(self,i,source,process,pain):
        return Observation(f"OBS-{i}",source,"u","d",process,"","human",pain,"failure","quote",.8,str(i))

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

if __name__=="__main__":
    unittest.main()
