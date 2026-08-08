from __future__ import annotations
import json
from .llm import call_claude, parse_json_object
from .models import Evaluation

SYSTEM='''You are the Constraint Archaeologist Agent. You receive an evidence dossier only. You are forbidden to invent evidence or browse. Your job is to try to kill the anomaly using frozen Constraint Archaeology v0.5. Separate Mechanism from Capture. Return JSON only. K1 surviving value; K2 load structure; K3 minimum viable configuration; K4 true compounding; K5 customer substitute level+direction; K6 supply overshoot. Allowed action values: KILL, WATCH, INVESTIGATE. INVESTIGATE requires adequate evidence and no hard mechanism fail.'''

def evaluate(anomaly, evidence):
    dossier={"anomaly":anomaly,"evidence":evidence}
    user='''Evaluate this dossier. Return JSON fields: mechanism_verdict (PASS/PASS WITH NARROW WEDGE/FAIL/INSUFFICIENT DATA), capture_verdict (PASS/WEAK PASS/FAIL/INSUFFICIENT DATA), k1,k2,k3,k4,k5,k6 (short findings), rationale, evidence_used (observation ids only), action (KILL/WATCH/INVESTIGATE). If evidence is thin, choose WATCH or INSUFFICIENT DATA.\n\n'''+json.dumps(dossier,ensure_ascii=False)
    o=parse_json_object(call_claude(SYSTEM,user,2000))
    return Evaluation(anomaly["anomaly_id"],o["mechanism_verdict"],o["capture_verdict"],o["k1"],o["k2"],o["k3"],o["k4"],o["k5"],o["k6"],o["rationale"],o.get("evidence_used",[]),o["action"])
