from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, Protocol, Any, Dict

class FailureClass(str, Enum):
    ABSENCE = "absence"
    CONFLICT = "conflict"
    CORRUPTION = "corruption"
    LATENCY = "latency"
    UNVERIFIED = "unverified"
    CAPACITY = "capacity"
    OTHER = "other"

class Verdict(str, Enum):
    SAME_MECHANISM = "same_mechanism"
    DIFFERENT_MECHANISMS = "different_mechanisms"
    INSUFFICIENT_DATA = "insufficient_data"

class EdgeType(str, Enum):
    MERGED = "merged"
    RELATED_DISTINCT = "related_distinct"
    UNRESOLVED = "unresolved"

@dataclass(frozen=True)
class GateAnomaly:
    id: str
    source: str
    process: str
    pain: str
    current_carrier: str
    failure_mode: str
    evidence_count: int = 1
    confidence: float = 0.0
    raw: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class MechanismProfile:
    anomaly_id: str
    hidden_function: str
    inputs: str
    outputs: str
    carrier: str
    failure_class: FailureClass
    failure_mechanism: str
    repair: str
    confidence: float
    evidence_count: int

@dataclass(frozen=True)
class CounterfactualResult:
    repair_from: str
    applied_to: str
    removes_failure: Optional[bool]
    reason: str

@dataclass(frozen=True)
class GateDecision:
    verdict: Verdict
    edge: EdgeType
    left_id: str
    right_id: str
    reasons: list
    counterfactuals: list
    short_circuited: bool = False
    def to_dict(self):
        d=asdict(self); d["verdict"]=self.verdict.value; d["edge"]=self.edge.value
        return d

PROFILE_PROMPT = """You are decomposing a single reported failure. You will not be shown any other case.\n\nReport:\n  process:         {process}\n  reported pain:   {pain}\n  current carrier: {current_carrier}\n  failure mode:    {failure_mode}\n\nAnswer strictly as JSON with keys: hidden_function, inputs, outputs, carrier, failure_class (absence|conflict|corruption|latency|unverified|capacity|other), failure_mechanism, repair, confidence. The repair must be the MINIMAL capability change that makes this specific failure stop. Do not speculate beyond the report."""

COUNTERFACTUAL_PROMPT = """A proposed change is described below. Separately, an unrelated failure is described.\n\nProposed change:\n  {repair}\n\nFailure:\n  process:           {process}\n  reported pain:     {pain}\n  failure mechanism: {failure_mechanism}\n\nIf the proposed change were fully and perfectly in place, would THIS failure stop occurring? Answer strictly as JSON: removes_failure (true|false|null), reason. Partial mitigation is false."""

class JudgeProtocol(Protocol):
    def profile(self, prompt: str) -> Dict[str, Any]: ...
    def counterfactual(self, prompt: str) -> Dict[str, Any]: ...

def _coerce_confidence(value) -> float:
    """A real run crashed on judge.profile() returning confidence as "85%"
    instead of 0.85 - float() has no idea what to do with a percent sign.
    Same defensive shape as the failure_class fallback just above: try the
    natural conversion, and only fall back to the existing 0.0 default if it
    genuinely can't be read as a number. Doesn't change what confidence
    MEANS or how the evidence-floor check uses it - only what input shapes
    survive to reach that check instead of crashing before it runs."""
    if isinstance(value, (int, float)):
        return float(value)
    try:
        text = str(value).strip()
        if text.endswith("%"):
            return float(text[:-1]) / 100.0
        return float(text)
    except (TypeError, ValueError):
        return 0.0

def profile_anomaly(anomaly: GateAnomaly, judge: JudgeProtocol) -> MechanismProfile:
    raw=judge.profile(PROFILE_PROMPT.format(process=anomaly.process,pain=anomaly.pain,current_carrier=anomaly.current_carrier,failure_mode=anomaly.failure_mode))
    try: fclass=FailureClass(str(raw.get("failure_class","other")).lower())
    except ValueError: fclass=FailureClass.OTHER
    return MechanismProfile(anomaly.id,raw.get("hidden_function",""),raw.get("inputs",""),raw.get("outputs",""),raw.get("carrier",anomaly.current_carrier),fclass,raw.get("failure_mechanism",""),raw.get("repair",""),_coerce_confidence(raw.get("confidence",0.0)),anomaly.evidence_count)

def _cross_test(repair_profile,target,target_profile,judge):
    raw=judge.counterfactual(COUNTERFACTUAL_PROMPT.format(repair=repair_profile.repair,process=target.process,pain=target.pain,failure_mechanism=target_profile.failure_mechanism))
    val=raw.get("removes_failure",None)
    if val is not None: val=bool(val)
    return CounterfactualResult(repair_profile.anomaly_id,target.id,val,raw.get("reason",""))

def same_mechanism(left,right,left_profile,right_profile,judge,min_confidence=.5,min_evidence=1):
    reasons=[]
    thin=[p.anomaly_id for p in (left_profile,right_profile) if p.confidence<min_confidence or p.evidence_count<min_evidence]
    if thin:
        reasons.append(f"evidence below floor for {sorted(thin)}")
        return GateDecision(Verdict.INSUFFICIENT_DATA,EdgeType.UNRESOLVED,left.id,right.id,reasons,[])
    lc,rc=left_profile.failure_class,right_profile.failure_class
    if lc!=rc and FailureClass.OTHER not in (lc,rc):
        reasons.append(f"failure_class differs: {lc.value} vs {rc.value}")
        return GateDecision(Verdict.DIFFERENT_MECHANISMS,EdgeType.RELATED_DISTINCT,left.id,right.id,reasons,[],True)
    cf=[_cross_test(left_profile,right,right_profile,judge),_cross_test(right_profile,left,left_profile,judge)]
    if any(c.removes_failure is None for c in cf):
        return GateDecision(Verdict.INSUFFICIENT_DATA,EdgeType.UNRESOLVED,left.id,right.id,["counterfactual undecidable"],cf)
    if all(c.removes_failure for c in cf):
        return GateDecision(Verdict.SAME_MECHANISM,EdgeType.MERGED,left.id,right.id,["each repair removes the other's failure"],cf)
    failed=[f"{c.repair_from}->{c.applied_to}: {c.reason}" for c in cf if not c.removes_failure]
    return GateDecision(Verdict.DIFFERENT_MECHANISMS,EdgeType.RELATED_DISTINCT,left.id,right.id,["counterfactual fails: "+"; ".join(failed)],cf)

def gate_pair(left,right,judge,**kwargs):
    lp=profile_anomaly(left,judge); rp=profile_anomaly(right,judge)
    return same_mechanism(left,right,lp,rp,judge,**kwargs)
