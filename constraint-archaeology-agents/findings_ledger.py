"""
findings_ledger
===============

Append-only audit stream for derived pipeline decisions.

  constraint-archaeology-agents/data/findings.jsonl

SCOPE OF THIS SLICE
    Dual-write only. Existing snapshot files stay authoritative for runtime
    behaviour. Nothing reads this ledger yet. No database, no expectations,
    no price sensors, no SUPERSEDES graph.

WHAT THIS MODULE IS NOT
    It does not classify anomalies, call a model, compute trust, understand
    Constraint Archaeology, or resolve expectations. Persistence stays dumb.

APPEND-ONLY, LITERALLY
    The only write path opens the file in "a" mode and writes one line.
    There is no code here that reads the file and writes it back. A logically
    newer result is a NEW record, never an edit of an old one.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence

LEDGER_VERSION = "1"
WRITER_VERSION = "0.1.0"

#: Only kinds the pipeline produces today. Do not add speculative kinds.
KNOWN_KINDS = frozenset({
    "anomaly",
    "mechanism_profile",
    "same_mechanism_decision",
    "ca_evaluation",
})

#: Envelope keys, in canonical order.
ENVELOPE_KEYS = (
    "finding_id",
    "kind",
    "recorded_at",
    "derived_from",
    "analyst",
    "analyst_version",
    "method_version",
    "origin",
    "payload",
)

CONSTRAINT_ARCHAEOLOGY_METHOD_VERSION = "0.5"


class FindingValidationError(ValueError):
    """Raised when a record does not satisfy the envelope contract."""


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _canonical(obj: Any) -> str:
    """Stable serialisation. Used for both hashing and the written line."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), default=str)


def make_finding_id(kind: str,
                    identity: Dict[str, Any],
                    derived_from: Sequence[str]) -> str:
    """Deterministic id from the record's LOGICAL identity.

    `recorded_at` is deliberately excluded: a retry of the same logical run
    must produce the same id, otherwise idempotency is impossible.

    `kind` is folded into both the hash input and the visible prefix, so two
    different kinds built from the same inputs cannot collide.
    """
    if kind not in KNOWN_KINDS:
        raise FindingValidationError(f"unknown kind: {kind!r}")
    material = _canonical({
        "v": LEDGER_VERSION,
        "kind": kind,
        "identity": identity,
        "derived_from": sorted(derived_from),
    })
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]
    return f"{kind}:{digest}"


# ---------------------------------------------------------------------------
# envelope
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Finding:
    finding_id: str
    kind: str
    recorded_at: str
    derived_from: List[str]
    analyst: str
    analyst_version: str
    method_version: Optional[str]
    payload: Dict[str, Any]
    origin: str = "generated"

    def to_envelope(self) -> Dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "kind": self.kind,
            "recorded_at": self.recorded_at,
            "derived_from": list(self.derived_from),
            "analyst": self.analyst,
            "analyst_version": self.analyst_version,
            "method_version": self.method_version,
            "origin": self.origin,
            "payload": self.payload,
        }


def validate(finding: Finding, allow_empty_provenance: bool = False) -> None:
    if finding.kind not in KNOWN_KINDS:
        raise FindingValidationError(f"unknown kind: {finding.kind!r}")

    if finding.origin != "generated":
        raise FindingValidationError(
            "Findings are derived; origin must be 'generated'. Raw evidence "
            "does not belong in this ledger."
        )

    for field in ("finding_id", "recorded_at", "analyst", "analyst_version"):
        value = getattr(finding, field)
        if not isinstance(value, str) or not value:
            raise FindingValidationError(f"{field} must be a non-empty string")

    if not finding.recorded_at.endswith("Z"):
        raise FindingValidationError("recorded_at must be UTC ISO ending in 'Z'")

    if not isinstance(finding.derived_from, list) or \
            any(not isinstance(x, str) or not x for x in finding.derived_from):
        raise FindingValidationError("derived_from must be a list of non-empty strings")

    if not finding.derived_from:
        # A finding with no provenance chain is invalid unless the caller says
        # explicitly why, and that reason is written into the record itself.
        if not allow_empty_provenance:
            raise FindingValidationError(
                f"{finding.kind} has empty derived_from; pass "
                "allow_empty_provenance=True and set payload['provenance_note']"
            )
        if not finding.payload.get("provenance_note"):
            raise FindingValidationError(
                "empty provenance requires payload['provenance_note'] stating why"
            )

    if finding.analyst == "constraint_archaeology" and \
            finding.method_version != CONSTRAINT_ARCHAEOLOGY_METHOD_VERSION:
        raise FindingValidationError(
            "constraint_archaeology findings must carry method_version="
            f"{CONSTRAINT_ARCHAEOLOGY_METHOD_VERSION!r}; got {finding.method_version!r}"
        )

    if finding.method_version is not None and not isinstance(finding.method_version, str):
        raise FindingValidationError("method_version must be a string or None")

    if not isinstance(finding.payload, dict):
        raise FindingValidationError("payload must be an object")


# ---------------------------------------------------------------------------
# writer
# ---------------------------------------------------------------------------

class FindingsLedger:
    """Narrow append-only writer.

    IDEMPOTENCY TRADEOFF
        Known ids are loaded once into memory at construction, and `append`
        skips ids already present. This is O(file) per process start and
        O(1) per write, which is right for the current scale (thousands of
        lines, one process per daily run).

        It is NOT safe against two writers appending concurrently: both could
        miss each other's ids. Today's runs are serialised by the scheduler,
        so the cheap version is correct. When that stops being true the fix is
        an advisory lock around append, or a sidecar id index — deliberately
        not built now, because an unused index is a maintenance cost with no
        current benefit.

        A database would solve this properly and is out of scope by
        instruction; the file format is chosen so the migration is a one-time
        replay of an append-only log.
    """

    def __init__(self, path: str, fsync: bool = False):
        self.path = path
        self.fsync = fsync
        self._known: set = set()
        self._load_known_ids()

    # -- read side is used ONLY for the id set; never for rewriting -------
    def _load_known_ids(self) -> None:
        if not os.path.exists(self.path):
            return
        with open(self.path, "r", encoding="utf-8") as fh:
            for line_no, line in enumerate(fh, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    # A corrupt line is history too. Skip it for the id set,
                    # never rewrite the file to "fix" it.
                    continue
                fid = rec.get("finding_id")
                if isinstance(fid, str):
                    self._known.add(fid)

    def has(self, finding_id: str) -> bool:
        return finding_id in self._known

    @property
    def known_count(self) -> int:
        return len(self._known)

    def append(self, finding: Finding, allow_empty_provenance: bool = False) -> bool:
        """Append one finding. Returns True if written, False if already present."""
        validate(finding, allow_empty_provenance=allow_empty_provenance)
        if finding.finding_id in self._known:
            return False

        os.makedirs(os.path.dirname(os.path.abspath(self.path)) or ".", exist_ok=True)
        line = _canonical(finding.to_envelope())
        with open(self.path, "a", encoding="utf-8") as fh:   # append mode only
            fh.write(line + "\n")
            fh.flush()
            if self.fsync:
                os.fsync(fh.fileno())
        self._known.add(finding.finding_id)
        return True

    def append_many(self, findings: Iterable[Finding], **kwargs) -> int:
        return sum(1 for f in findings if self.append(f, **kwargs))


# ---------------------------------------------------------------------------
# builders for the kinds produced today
# ---------------------------------------------------------------------------
# These exist so integration is one line at each write point and so provenance
# is stated explicitly by the caller rather than guessed here.

def build_anomaly(*, anomaly_id: str, observation_ids: Sequence[str],
                  payload: Dict[str, Any], analyst_version: str,
                  analyst: str = "anomaly_clusterer",
                  recorded_at: Optional[str] = None) -> Finding:
    identity = {"anomaly_id": anomaly_id}
    return Finding(
        finding_id=make_finding_id("anomaly", identity, observation_ids),
        kind="anomaly",
        recorded_at=recorded_at or utc_now_iso(),
        derived_from=list(observation_ids),
        analyst=analyst,
        analyst_version=analyst_version,
        method_version=None,
        payload={**payload, "anomaly_id": anomaly_id},
    )


def build_mechanism_profile(*, subject_id: str, derived_from: Sequence[str],
                            profile: Dict[str, Any], analyst_version: str,
                            analyst: str = "same_mechanism_gate",
                            recorded_at: Optional[str] = None) -> Finding:
    identity = {"subject_id": subject_id,
                "failure_class": profile.get("failure_class"),
                "repair": profile.get("repair")}
    return Finding(
        finding_id=make_finding_id("mechanism_profile", identity, derived_from),
        kind="mechanism_profile",
        recorded_at=recorded_at or utc_now_iso(),
        derived_from=list(derived_from),
        analyst=analyst,
        analyst_version=analyst_version,
        method_version=None,
        payload={**profile, "subject_id": subject_id},
    )


def build_same_mechanism_decision(*, left_id: str, right_id: str,
                                  verdict: str, edge: str,
                                  reasons: Sequence[str],
                                  counterfactuals: Sequence[Dict[str, Any]],
                                  short_circuited: bool,
                                  gate_version: str,
                                  derived_from: Sequence[str],
                                  analyst_version: str,
                                  analyst: str = "same_mechanism_gate",
                                  recorded_at: Optional[str] = None) -> Finding:
    """Every gate outcome is history: MERGED, RELATED_DISTINCT and UNRESOLVED.

    The pair is sorted in the identity so that gate(a,b) and gate(b,a) produce
    the same id, matching the gate's own order-independence.
    """
    pair = sorted([left_id, right_id])
    identity = {"pair": pair, "verdict": verdict, "gate_version": gate_version}
    return Finding(
        finding_id=make_finding_id("same_mechanism_decision", identity, derived_from),
        kind="same_mechanism_decision",
        recorded_at=recorded_at or utc_now_iso(),
        derived_from=list(derived_from),
        analyst=analyst,
        analyst_version=analyst_version,
        method_version=None,
        payload={
            "verdict": verdict,
            "edge": edge,
            "left_id": left_id,
            "right_id": right_id,
            "reasons": list(reasons),
            "counterfactuals": [dict(c) for c in counterfactuals],
            "short_circuited": bool(short_circuited),
            "gate_version": gate_version,
        },
    )


def build_ca_evaluation(*, subject_id: str, evidence_ids: Sequence[str],
                        payload: Dict[str, Any], adapter_version: str,
                        recorded_at: Optional[str] = None) -> Finding:
    """Constraint Archaeology output.

    `adapter_version` moves when our integration changes; `method_version`
    stays "0.5" because the frozen method does not. Keeping them separate is
    what lets infrastructure evolve without silently changing the method.
    """
    identity = {"subject_id": subject_id,
                "mechanism_verdict": payload.get("mechanism_verdict"),
                "capture_verdict": payload.get("capture_verdict"),
                "classification": payload.get("classification")}
    return Finding(
        finding_id=make_finding_id("ca_evaluation", identity, evidence_ids),
        kind="ca_evaluation",
        recorded_at=recorded_at or utc_now_iso(),
        derived_from=list(evidence_ids),
        analyst="constraint_archaeology",
        analyst_version=adapter_version,
        method_version=CONSTRAINT_ARCHAEOLOGY_METHOD_VERSION,
        payload={**payload, "subject_id": subject_id},
    )
