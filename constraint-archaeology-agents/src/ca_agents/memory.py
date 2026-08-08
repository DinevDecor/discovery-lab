from __future__ import annotations
import datetime as dt, json, os, re
from .models import Anomaly, Observation, to_dict
from .same_mechanism_gate import GateAnomaly, EdgeType, gate_pair

FUNCTIONS = {
 "state_verification": ["state","condition","handoff","verify","inspection","proof"],
 "unknown_scope_pricing": ["quote","estimate","scope","budget","price"],
 "rare_decision_trust": ["trust","reputation","rare","provider","vendor"],
 "lost_information_reconstruction": ["reconstruct","missing","lost","re-enter","manual entry","document"],
 "variability_buffering": ["buffer","variance","spike","forecast","capacity","queue"],
 "exception_handling": ["exception","mismatch","edge case","manual review","escalation"],
 "liability_transfer": ["liability","responsibility","acceptance","sign-off","warranty"],
 "capital_time_risk": ["working capital","payment delay","inventory","financing","cash flow","credit"],
}

def _tokens(s): return set(re.findall(r"[a-zA-Z0-9_]{4,}",s.lower()))
def _sim(a,b):
    A,B=_tokens(a),_tokens(b)
    return len(A&B)/max(1,len(A|B))

def classify_function(obs):
    text=" ".join([obs.process,obs.hidden_function_hint,obs.pain,obs.failure_mode]).lower()
    scores={k:sum(1 for w in ws if w in text) for k,ws in FUNCTIONS.items()}
    return max(scores,key=scores.get) if max(scores.values(),default=0)>0 else "unclassified"

def load_jsonl(path):
    if not os.path.exists(path): return []
    with open(path,encoding="utf-8") as f: return [json.loads(x) for x in f if x.strip()]

def append_jsonl(path, rows):
    os.makedirs(os.path.dirname(path),exist_ok=True)
    with open(path,"a",encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r,ensure_ascii=False)+"\n")

def _gate_obs(obs, evidence_count=1):
    return GateAnomaly(
        id=obs.observation_id, source=obs.source, process=obs.process,
        pain=obs.pain, current_carrier=obs.current_carrier,
        failure_mode=obs.failure_mode, evidence_count=evidence_count,
        confidence=obs.confidence,
    )

def rebuild_anomalies(observations, threshold=.22, judge=None, return_decisions=False):
    """Rebuild clusters from observations.

    Lexical/function similarity only proposes candidate pairs. When a judge is
    supplied, a pair may merge only after the symmetric same-mechanism gate.
    RELATED_DISTINCT and UNRESOLVED decisions are retained for audit.
    """
    anomalies=[]; decisions=[]; byid={}
    for o in observations:
        obs=Observation(**o) if isinstance(o,dict) else o
        byid[obs.observation_id]=obs
        best=None; bests=0
        for a in anomalies:
            if a.hidden_function_class != classify_function(obs): continue
            s=_sim(a.canonical_pattern,obs.process+" "+obs.pain)
            if s>bests: best,bests=a,s
        may_merge=best is not None and bests>=threshold
        if may_merge and judge is not None:
            rep=byid.get(best.observation_ids[0])
            if rep is None:
                may_merge=False
            else:
                decision=gate_pair(
                    _gate_obs(rep,len(best.observation_ids)),
                    _gate_obs(obs,1), judge
                )
                decisions.append(decision.to_dict())
                may_merge=decision.edge is EdgeType.MERGED
        if may_merge:
            best.observation_ids.append(obs.observation_id)
            if obs.source not in best.independent_sources: best.independent_sources.append(obs.source)
            best.last_seen=dt.date.today().isoformat()
        else:
            aid=f"ANOM-{len(anomalies)+1:04d}"
            anomalies.append(Anomaly(aid,obs.process+" — "+obs.pain,classify_function(obs),[obs.observation_id],[obs.source],dt.date.today().isoformat(),dt.date.today().isoformat(),"WATCH"))
    return (anomalies,decisions) if return_decisions else anomalies

def persist_anomalies(path, anomalies):
    os.makedirs(os.path.dirname(path),exist_ok=True)
    with open(path,"w",encoding="utf-8") as f: json.dump([to_dict(a) for a in anomalies],f,ensure_ascii=False,indent=2)

def persist_gate_decisions(path, decisions):
    os.makedirs(os.path.dirname(path),exist_ok=True)
    with open(path,"w",encoding="utf-8") as f: json.dump(decisions,f,ensure_ascii=False,indent=2)
