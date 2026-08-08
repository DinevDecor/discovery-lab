from __future__ import annotations
import datetime as dt, os

def render(path, stats, evaluations, errors):
    os.makedirs(os.path.dirname(path),exist_ok=True)
    lines=[f"# Constraint Archaeology Daily — {dt.date.today().isoformat()}","",f"Scanned: **{stats['captures']}** · Observations: **{stats['observations']}** · Anomalies: **{stats['anomalies']}** · Mature evaluated: **{stats['evaluated']}**",""]
    if errors:
        lines += ["## Source errors"]+[f"- {e['source']}: {e['error']}" for e in errors]+[""]
    for action in ("INVESTIGATE","WATCH","KILL"):
        group=[e for e in evaluations if e.action==action]
        lines += [f"## {action} ({len(group)})"]
        for e in group:
            lines += [f"### {e.anomaly_id}",f"Mechanism: **{e.mechanism_verdict}** · Capture: **{e.capture_verdict}**",e.rationale,"",f"K1 {e.k1} | K2 {e.k2} | K3 {e.k3} | K4 {e.k4} | K5 {e.k5} | K6 {e.k6}",""]
    with open(path,"w",encoding="utf-8") as f:
        f.write("\n".join(lines)+"\n")
