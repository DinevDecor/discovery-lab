"""Portfolio Engine. Builds one entry per configured repository — the
same fixed, human-curated 5-repo scope observation-agent already uses
(PROP-0001's own no-dynamic-discovery rule), not a dynamically
discovered project list."""

from __future__ import annotations

from .collector import Collected, RepoSnapshot
from .models import Confidence, Evidence, Finding, PortfolioEntry

_STATUS_KEYS = ("status", "Project Status", "Architecture Status", "Current verdict")
_STEP_KEYS = ("current_step", "Current next action", "next_action")
_DATE_KEYS = ("updated_at",)


def _first_present(fields: dict[str, str], keys: tuple[str, ...]) -> str | None:
    for k in keys:
        if k in fields and fields[k].strip():
            return fields[k].strip()
    return None


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return f"{cut}..."


def _current_state(snap: RepoSnapshot) -> str:
    status = _first_present(snap.state_fields, _STATUS_KEYS)
    step = _first_present(snap.state_fields, _STEP_KEYS)
    if status and step:
        return f"{status} — {_truncate(step, 110)}"
    if status:
        return status
    if step:
        return _truncate(step, 150)
    return "UNKNOWN — no parseable state file found"


def _last_progress(snap: RepoSnapshot) -> str:
    return _first_present(snap.state_fields, _DATE_KEYS) or "INSUFFICIENT_EVIDENCE (no updated_at-equivalent field found)"


def project_health_score(
    repo_name: str, snap: RepoSnapshot, drift_findings: list[Finding], scanned: list[str], has_log: bool
) -> float:
    """Mean of three components, each in 0..1:
    (1) 1.0 if the state file yielded >=2 parseable fields, else 0.0;
    (2) 1.0 if this repo was SCANned in the latest Observation Agent
        run, else 0.0 (omitted from the average if no execution log
        exists at all, rather than penalizing every project for a
        missing report);
    (3) 1.0 minus 0.5 per MISMATCH-confidence drift finding naming
        this repo, floored at 0.0.
    """
    components = [1.0 if len(snap.state_fields) >= 2 else 0.0]
    if has_log:
        components.append(1.0 if repo_name in scanned else 0.0)
    mismatches = [
        f for f in drift_findings if f.confidence == Confidence.MISMATCH and repo_name in f.affected
    ]
    components.append(max(0.0, 1.0 - 0.5 * len(mismatches)))
    return sum(components) / len(components)


def risk_level(repo_name: str, snap: RepoSnapshot, drift_findings: list[Finding], skipped: list[str]) -> str:
    mismatches = [
        f for f in drift_findings if f.confidence == Confidence.MISMATCH and repo_name in f.affected
    ]
    if mismatches or repo_name in skipped:
        return "HIGH" if mismatches else "MEDIUM"
    insufficient = [
        f
        for f in drift_findings
        if f.confidence == Confidence.INSUFFICIENT_EVIDENCE and repo_name in f.affected and not f.is_opportunity
    ]
    if insufficient or len(snap.state_fields) < 2:
        return "MEDIUM"
    return "LOW"


def entry_confidence(snap: RepoSnapshot, scanned: list[str], has_log: bool) -> str:
    has_state = len(snap.state_fields) >= 2
    was_scanned = has_log and snap.name in scanned
    if has_state and (was_scanned or not has_log):
        return "HIGH"
    if has_state or was_scanned:
        return "MEDIUM"
    return "LOW"


def build_portfolio(
    collected: Collected, drift_findings: list[Finding], previous_scores: dict[str, float] | None = None
) -> list[PortfolioEntry]:
    previous_scores = previous_scores or {}
    entries: list[PortfolioEntry] = []
    scanned = collected.observation.scanned_repos
    skipped = collected.observation.skipped_repos
    has_log = bool(collected.observation.log_path)

    for repo_name, snap in collected.repos.items():
        score = project_health_score(repo_name, snap, drift_findings, scanned, has_log)
        prev = previous_scores.get(repo_name)
        if prev is None:
            trend = "N/A (first execution, no prior snapshot)"
        elif score > prev + 0.05:
            trend = "▲ Improving"
        elif score < prev - 0.05:
            trend = "▼ Needs attention"
        else:
            trend = "■ Stable"

        own_findings = [f for f in drift_findings if repo_name in f.affected]
        evidence = [Evidence(repo_name, f"state file: {snap.state_file_path or 'none'}")]
        evidence += [Evidence(repo_name, f.title) for f in own_findings[:3]]

        entries.append(
            PortfolioEntry(
                name=repo_name,
                purpose=snap.purpose or "INSUFFICIENT_EVIDENCE (no README purpose paragraph found)",
                current_state=_current_state(snap),
                trend=trend,
                dependencies="INSUFFICIENT_EVIDENCE (v1.0 does not parse a dependency graph — see README Limitations)",
                last_meaningful_progress=_last_progress(snap),
                risk_level=risk_level(repo_name, snap, drift_findings, skipped),
                confidence=entry_confidence(snap, scanned, has_log),
                health_score=f"{round(score * 100)}%",
                evidence=evidence,
            )
        )
    return entries
