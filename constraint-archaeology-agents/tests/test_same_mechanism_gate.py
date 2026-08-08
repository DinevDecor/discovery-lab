import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__),"..","src"))
from ca_agents.same_mechanism_gate import GateAnomaly, Verdict, EdgeType, gate_pair

class ScriptedJudge:
    def __init__(self,profiles,counterfactuals):
        self._profiles=profiles; self._counterfactuals=counterfactuals
        self.profile_calls=[]; self.counterfactual_calls=[]
    def _lookup(self,table,prompt):
        for key,value in table.items():
            if key in prompt: return value
        raise KeyError(prompt)
    def profile(self,prompt): self.profile_calls.append(prompt); return self._lookup(self._profiles,prompt)
    def counterfactual(self,prompt): self.counterfactual_calls.append(prompt); return self._lookup(self._counterfactuals,prompt)

def mk(id_,process,pain,carrier,failure_mode,conf=.8,n=2):
    return GateAnomaly(id_,"test",process,pain,carrier,failure_mode,n,conf)

class GateTests(unittest.TestCase):
    def test_conflict_and_absence_short_circuit(self):
        a=mk("A","coordinating concurrent sessions","state carried by hand","human","two sessions make incompatible choices")
        b=mk("B","generating code in an existing project","context re-supplied","human memory","output ignores conventions")
        judge=ScriptedJudge({
          "coordinating concurrent sessions":{"hidden_function":"reconcile","inputs":"decisions","outputs":"compatible decision","carrier":"human","failure_class":"conflict","failure_mechanism":"valid choices conflict","repair":"authority serialises writes","confidence":.8},
          "generating code in an existing project":{"hidden_function":"supply conventions","inputs":"rules","outputs":"conforming work","carrier":"human","failure_class":"absence","failure_mechanism":"actor never receives conventions","repair":"durable artifact read before acting","confidence":.8}}, {})
        d=gate_pair(a,b,judge)
        self.assertIs(d.verdict,Verdict.DIFFERENT_MECHANISMS); self.assertIs(d.edge,EdgeType.RELATED_DISTINCT)
        self.assertTrue(d.short_circuited); self.assertEqual(judge.counterfactual_calls,[])

    def test_same_class_cross_repairs_merge(self):
        a=mk("H1","shift handover on a ward","recite from memory","human memory","pending decisions not passed")
        b=mk("H2","transfer of a patient between wards","reconstruct by asking","human memory","prior decisions unknown")
        prof={
          "shift handover on a ward":{"hidden_function":"carry decisions","inputs":"open decisions","outputs":"same decisions","carrier":"human","failure_class":"absence","failure_mechanism":"next actor never receives decisions","repair":"structured record handed over","confidence":.8},
          "transfer of a patient between wards":{"hidden_function":"carry decisions","inputs":"open decisions","outputs":"same decisions","carrier":"human","failure_class":"absence","failure_mechanism":"receiver never receives decisions","repair":"structured record attached to case","confidence":.8}}
        cf={"transfer of a patient between wards":{"removes_failure":True,"reason":"record travels"},"shift handover on a ward":{"removes_failure":True,"reason":"record travels"}}
        d=gate_pair(a,b,ScriptedJudge(prof,cf)); self.assertIs(d.verdict,Verdict.SAME_MECHANISM); self.assertIs(d.edge,EdgeType.MERGED)

    def test_same_class_repair_does_not_transfer(self):
        a=mk("F1","quoting a repair before opening the machine","scope unknown","estimator","estimate misses hidden work")
        b=mk("F2","onboarding a temporary operator to a line","operator lacks quirks","leader","operator misses quirks")
        prof={
          "quoting a repair before opening the machine":{"hidden_function":"price unknown scope","inputs":"symptoms","outputs":"price","carrier":"estimator","failure_class":"absence","failure_mechanism":"fact does not exist yet","repair":"observe hidden scope before price","confidence":.8},
          "onboarding a temporary operator to a line":{"hidden_function":"transfer practice","inputs":"quirks","outputs":"competence","carrier":"leader","failure_class":"absence","failure_mechanism":"fact exists but not written","repair":"written record of quirks","confidence":.8}}
        cf={"onboarding a temporary operator to a line":{"removes_failure":False,"reason":"scope observation does not teach quirks"},"quoting a repair before opening the machine":{"removes_failure":False,"reason":"writing practice cannot reveal unknown scope"}}
        d=gate_pair(a,b,ScriptedJudge(prof,cf)); self.assertIs(d.verdict,Verdict.DIFFERENT_MECHANISMS); self.assertFalse(d.short_circuited)

    def test_thin_evidence_unresolved(self):
        a=mk("T1","p","x","human","y",.2); b=mk("T2","q","x","human","y",.9)
        prof={"p":{"failure_class":"absence","confidence":.2},"q":{"failure_class":"absence","confidence":.9}}
        d=gate_pair(a,b,ScriptedJudge(prof,{})); self.assertIs(d.verdict,Verdict.INSUFFICIENT_DATA); self.assertIs(d.edge,EdgeType.UNRESOLVED)

    def test_undecidable_counterfactual_unresolved(self):
        a=mk("U1","alpha","x","human","y"); b=mk("U2","beta","x","human","y")
        prof={"alpha":{"failure_class":"absence","failure_mechanism":"m","repair":"r1","confidence":.9},"beta":{"failure_class":"absence","failure_mechanism":"m","repair":"r2","confidence":.9}}
        cf={"beta":{"removes_failure":True,"reason":"ok"},"alpha":{"removes_failure":None,"reason":"unknown"}}
        self.assertIs(gate_pair(a,b,ScriptedJudge(prof,cf)).verdict,Verdict.INSUFFICIENT_DATA)

    def test_order_independence(self):
        a=mk("O1","alpha","x","human","y"); b=mk("O2","beta","x","human","y")
        prof={"alpha":{"failure_class":"conflict","failure_mechanism":"m","repair":"r1","confidence":.9},"beta":{"failure_class":"conflict","failure_mechanism":"m","repair":"r2","confidence":.9}}
        cf={"beta":{"removes_failure":True,"reason":""},"alpha":{"removes_failure":False,"reason":"fails"}}
        self.assertIs(gate_pair(a,b,ScriptedJudge(prof,cf)).verdict,gate_pair(b,a,ScriptedJudge(prof,cf)).verdict)

    def test_profiling_is_independent(self):
        a=mk("I1","alpha process","pain-a","human","fm-a"); b=mk("I2","beta process","pain-b","human","fm-b")
        prof={"alpha process":{"failure_class":"absence","failure_mechanism":"m","repair":"r","confidence":.9},"beta process":{"failure_class":"absence","failure_mechanism":"m","repair":"r","confidence":.9}}
        judge=ScriptedJudge(prof,{"beta process":{"removes_failure":True,"reason":""},"alpha process":{"removes_failure":True,"reason":""}}); gate_pair(a,b,judge)
        for prompt in judge.profile_calls:
            self.assertFalse("alpha process" in prompt and "beta process" in prompt)
            self.assertFalse("pain-a" in prompt and "pain-b" in prompt)

if __name__=="__main__": unittest.main()
