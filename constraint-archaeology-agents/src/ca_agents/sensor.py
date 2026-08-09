from __future__ import annotations
import hashlib, re
from .llm import call_claude, parse_json_object
from .models import Observation

SYSTEM = '''You are the Sensor Agent for Constraint Archaeology. Extract observations only. NEVER propose startup ideas, markets, products, or investment recommendations. Ignore popularity/upvotes. Look for concrete processes, handoffs, workarounds, repeated manual work, expensive intermediaries, normalized failure, waiting, duplicated data entry, or capability-price shifts. Return JSON only.

Product Hunt sources are vendor-written launch announcements, not firsthand problem reports: the "pain" a maker claims to solve is their own marketing framing, not a reporter's own experience of the constraint. Extract it only if the text names a concrete process/carrier/failure, mark evidence_quote from the announcement itself, and expect low confidence - this is a solution/emerging-market signal, not evidence that the pain is real.'''

# Product Hunt is a solution/announcement signal, not a firsthand problem
# report (see docs/reviews adversarial note + README adapter notes). Its
# self-reported confidence is capped structurally - not just by prompt
# instruction - so it can never look as strong as a direct pain report from
# a forum poster, and popularity/upvotes (never even passed into a Capture)
# have no path to raising it either.
_SOLUTION_SIGNAL_SOURCES = ("product_hunt",)
_SOLUTION_SIGNAL_CONFIDENCE_CAP = 0.55

def cap_confidence_for_source(source: str, confidence: float) -> float:
    if source in _SOLUTION_SIGNAL_SOURCES:
        return min(confidence, _SOLUTION_SIGNAL_CONFIDENCE_CAP)
    return confidence

def _fingerprint(process, pain, failure):
    s=re.sub(r"\W+"," ",(process+" "+pain+" "+failure).lower()).strip()
    return hashlib.sha256(s.encode()).hexdigest()[:20]

def extract_observation(capture, ordinal: int):
    prompt=f'''Source: {capture.source}\nURL: {capture.url}\nTitle: {capture.title}\nText:\n{capture.text[:7000]}\n\nReturn exactly one JSON object. If there is no concrete operational observation, return {{"skip":true}}. Otherwise fields: process, hidden_function_hint, current_carrier, pain, failure_mode, evidence_quote (<=25 words copied from source), confidence (0..1).'''
    obj=parse_json_object(call_claude(SYSTEM,prompt,1200))
    if obj.get("skip"):
        return None
    fp=_fingerprint(obj["process"],obj["pain"],obj["failure_mode"])
    oid=f"OBS-{capture.captured_at[:10].replace('-','')}-{ordinal:04d}-{fp[:6]}"
    confidence=cap_confidence_for_source(capture.source,float(obj.get("confidence",0.5)))
    return Observation(oid,capture.source,capture.url,capture.published_at,obj["process"],obj.get("hidden_function_hint",""),obj.get("current_carrier",""),obj["pain"],obj["failure_mode"],obj.get("evidence_quote",""),confidence,fp,capture.story_group)
