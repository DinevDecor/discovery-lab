"""
same_mechanism_gate
===================

A pre-clustering gate for the Constraint Archaeology pipeline.

PURPOSE
    Two anomalies may be merged into one candidate constraint only if they share
    a failure *mechanism*, not merely a similar-sounding symptom. The join key is
    "what must change for the failure to disappear", never the wording of the pain.

    This module sits BEFORE Constraint Archaeology v0.5 and does not touch it.
    It decides which anomalies are allowed to be evaluated as one candidate.

CONTRACT
    profile_anomaly(a, judge)      -> MechanismProfile      (one anomaly at a time)
    same_mechanism(pa, pb, judge)  -> GateDecision

    `judge` is any callable implementing JudgeProtocol. It is injected, so the
    gate is testable without a model call and portable across providers.

TWO DESIGN RULES THAT MATTER
    1. INDEPENDENT PROFILING. profile_anomaly() accepts exactly one anomaly and
       never sees its sibling. Asking a model "are these the same?" primes a yes;
       asking it "what would fix this one?" does not.
    2. SYMMETRIC COUNTERFACTUAL. We do not test a guessed shared cause. We take
       each anomaly's own repair and apply it to the other. Merge requires BOTH
       directions to remove the failure. This needs no prior hypothesis about
       what the common constraint is.

NO DOMAIN KNOWLEDGE IS ENCODED HERE.
    There are no keyword lists, no topic terms, and no special cases. The failure
    taxonomy describes shapes of failure, not subject matter, and is meant to
    apply to a hospital handover as readily as to a build pipeline.
"""

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
class Anomaly:
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

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["verdict"] = self.verdict.value
        d["edge"] = self.edge.value
        d["counterfactuals"] = [{**asdict(c)} for c in self.counterfactuals]
        return d


PROFILE_PROMPT = """\
You are decomposing a single reported failure. You will not be shown any other case.

Report:
  process:         {process}
  reported pain:   {pain}
  current carrier: {current_carrier}
  failure mode:    {failure_mode}

Answer strictly as JSON with these keys:
  hidden_function     - the function the current arrangement actually performs
  inputs              - what goes into that function
  outputs             - what comes out of it
  carrier             - who or what performs it today
  failure_class       - one of: absence, conflict, corruption, latency, unverified, capacity, other
  failure_mechanism   - one sentence: the causal reason the failure occurs
  repair              - the MINIMAL change that would make this specific failure stop occurring.
                        State it as a capability, not as a product.
  confidence          - 0.0 to 1.0

Do not speculate beyond the report. If the report does not support a field, say so
in that field and lower the confidence.
"""

COUNTERFACTUAL_PROMPT = """\
A proposed change is described below. Separately, an unrelated failure is described.

Proposed change:
  {repair}

Failure:
  process:           {process}
  reported pain:     {pain}
  failure mechanism: {failure_mechanism}

Question: if the proposed change were fully and perfectly in place, would THIS
failure stop occurring?

Answer strictly as JSON:
  removes_failure - true, false, or null if the information is insufficient
  reason          - one sentence

Answer false if the failure would still occur for its own reasons, even if the
change would help in some other way. Partial mitigation is false, not true.
"""


class JudgeProtocol(Protocol):
    def profile(self, prompt: str) -> Dict[str, Any]: ...
    def counterfactual(self, prompt: str) -> Dict[str, Any]: ...


def profile_anomaly(anomaly: Anomaly, judge: JudgeProtocol) -> MechanismProfile:
    raw = judge.profile(PROFILE_PROMPT.format(
        process=anomaly.process,
        pain=anomaly.pain,
        current_carrier=anomaly.current_carrier,
        failure_mode=anomaly.failure_mode,
    ))
    try:
        fclass = FailureClass(str(raw.get("failure_class", "other")).lower())
    except ValueError:
        fclass = FailureClass.OTHER

    return MechanismProfile(
        anomaly_id=anomaly.id,
        hidden_function=raw.get("hidden_function", ""),
        inputs=raw.get("inputs", ""),
        outputs=raw.get("outputs", ""),
        carrier=raw.get("carrier", anomaly.current_carrier),
        failure_class=fclass,
        failure_mechanism=raw.get("failure_mechanism", ""),
        repair=raw.get("repair", ""),
        confidence=float(raw.get("confidence", 0.0)),
        evidence_count=anomaly.evidence_count,
    )


def _cross_test(repair_profile: MechanismProfile,
                target: Anomaly,
                target_profile: MechanismProfile,
                judge: JudgeProtocol) -> CounterfactualResult:
    raw = judge.counterfactual(COUNTERFACTUAL_PROMPT.format(
        repair=repair_profile.repair,
        process=target.process,
        pain=target.pain,
        failure_mechanism=target_profile.failure_mechanism,
    ))
    val = raw.get("removes_failure", None)
    if val is not None:
        val = bool(val)
    return CounterfactualResult(
        repair_from=repair_profile.anomaly_id,
        applied_to=target.id,
        removes_failure=val,
        reason=raw.get("reason", ""),
    )


def same_mechanism(left: Anomaly,
                   right: Anomaly,
                   left_profile: MechanismProfile,
                   right_profile: MechanismProfile,
                   judge: JudgeProtocol,
                   min_confidence: float = 0.5,
                   min_evidence: int = 1) -> GateDecision:
    reasons = []

    thin = [p.anomaly_id for p in (left_profile, right_profile)
            if p.confidence < min_confidence or p.evidence_count < min_evidence]
    if thin:
        reasons.append(
            f"evidence below floor for {sorted(thin)}: "
            f"need confidence>={min_confidence}, evidence_count>={min_evidence}"
        )
        return GateDecision(Verdict.INSUFFICIENT_DATA, EdgeType.UNRESOLVED,
                            left.id, right.id, reasons, [])

    lc, rc = left_profile.failure_class, right_profile.failure_class
    if lc != rc and FailureClass.OTHER not in (lc, rc):
        reasons.append(
            f"failure_class differs: {lc.value} vs {rc.value}; "
            "a repair for one shape does not remove the other"
        )
        return GateDecision(Verdict.DIFFERENT_MECHANISMS, EdgeType.RELATED_DISTINCT,
                            left.id, right.id, reasons, [], short_circuited=True)

    cf = [
        _cross_test(left_profile, right, right_profile, judge),
        _cross_test(right_profile, left, left_profile, judge),
    ]

    if any(c.removes_failure is None for c in cf):
        reasons.append("counterfactual undecidable in at least one direction")
        return GateDecision(Verdict.INSUFFICIENT_DATA, EdgeType.UNRESOLVED,
                            left.id, right.id, reasons, cf)

    if all(c.removes_failure for c in cf):
        reasons.append("each anomaly's own repair removes the other's failure")
        return GateDecision(Verdict.SAME_MECHANISM, EdgeType.MERGED,
                            left.id, right.id, reasons, cf)

    failed = [f"{c.repair_from}->{c.applied_to}: {c.reason}"
              for c in cf if not c.removes_failure]
    reasons.append("counterfactual fails in at least one direction: " + "; ".join(failed))
    return GateDecision(Verdict.DIFFERENT_MECHANISMS, EdgeType.RELATED_DISTINCT,
                        left.id, right.id, reasons, cf)


def gate_pair(left: Anomaly, right: Anomaly, judge: JudgeProtocol,
              **kwargs) -> GateDecision:
    lp = profile_anomaly(left, judge)
    rp = profile_anomaly(right, judge)
    return same_mechanism(left, right, lp, rp, judge, **kwargs)
