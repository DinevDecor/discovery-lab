from __future__ import annotations
import argparse, datetime as dt, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__),"src"))
from ca_agents.collector import collect_from_config
from ca_agents.sensor import extract_observation
from ca_agents.memory import append_jsonl, load_jsonl, rebuild_anomalies, persist_anomalies, persist_gate_decisions
from ca_agents.mechanism_judge import ClaudeMechanismJudge
from ca_agents.archaeologist import evaluate
from ca_agents.models import to_dict
from ca_agents.report import render

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--config",default="config/sources.json")
    p.add_argument("--max-captures",type=int,default=80)
    p.add_argument("--min-independent-sources",type=int,default=3)
    a=p.parse_args()
    root=os.path.dirname(__file__)
    data=os.path.join(root,"data")
    reports=os.path.join(root,"reports")
    captures,errors,telemetry=collect_from_config(os.path.join(root,a.config),budget=a.max_captures)
    obs=[]
    for i,c in enumerate(captures,1):
        try:
            o=extract_observation(c,i)
            if o:
                obs.append(o)
                telemetry[c.source].observations+=1
        except Exception as e:
            errors.append({"source":c.source,"error":f"sensor: {e}"})
            telemetry[c.source].errors+=1
    append_jsonl(os.path.join(data,"observations.jsonl"),[to_dict(o) for o in obs])
    allobs=load_jsonl(os.path.join(data,"observations.jsonl"))
    judge=ClaudeMechanismJudge()
    anomalies,gate_decisions=rebuild_anomalies(allobs,judge=judge,return_decisions=True)
    persist_anomalies(os.path.join(data,"anomalies.json"),anomalies)
    persist_gate_decisions(os.path.join(data,"latest-gate-decisions.json"),gate_decisions)
    byid={o["observation_id"]:o for o in allobs}
    evals=[]
    for an in anomalies:
        if len(an.independent_sources) < a.min_independent_sources:
            continue
        evidence=[byid[x] for x in an.observation_ids if x in byid]
        try:
            evals.append(evaluate(to_dict(an),evidence))
        except Exception as e:
            errors.append({"source":an.anomaly_id,"error":f"archaeologist: {e}"})
    stamp=dt.date.today().isoformat()
    render(os.path.join(reports,f"daily-{stamp}.md"),{"captures":len(captures),"observations":len(obs),"anomalies":len(anomalies),"evaluated":len(evals),"gate_decisions":len(gate_decisions)},evals,errors,telemetry)
    with open(os.path.join(data,"latest-evaluations.json"),"w",encoding="utf-8") as f:
        json.dump([to_dict(e) for e in evals],f,ensure_ascii=False,indent=2)
    print(json.dumps({"captures":len(captures),"observations":len(obs),"anomalies":len(anomalies),"evaluated":len(evals),"gate_decisions":len(gate_decisions),"errors":len(errors)}))

if __name__=="__main__":
    main()
