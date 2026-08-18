"""Computes the Human Quality Audit's metrics and pre-registered
decision from a finished verdicts file. Never called during selection
or review - report generation is always a separate, later pass, so
nothing tallies live while a reviewer is still working (see
audit/README.md's blinding rule)."""

from __future__ import annotations

from dataclasses import dataclass

# Pre-registered before any of the 20 posts were reviewed (see the task
# that specified this audit). e_corroboration_worthy YES count:
#   <= FAIL_MAX            -> FAIL
#   FAIL_MAX < n <= ITERATE_MAX -> INSUFFICIENT_DATA_ITERATE
#   > ITERATE_MAX           -> PASS_CANDIDATE
FAIL_MAX = 4
ITERATE_MAX = 9
DENOMINATOR = 20


@dataclass
class AuditReportMetrics:
    total_selected: int
    available: int
    unavailable: int
    a_yes: int
    b_yes: int
    c_yes: int
    d_yes: int
    e_yes: int
    genuine_problem_rate: float
    consequence_rate: float
    noise_rate: float
    apparently_incremental_rate: float
    corroboration_worthy_rate: float
    decision: str
    decision_reason: str


def _get(v, k):
    return v[k] if isinstance(v, dict) else getattr(v, k)


def compute_report(verdicts: list, denominator: int = DENOMINATOR) -> AuditReportMetrics:
    """Rates are always computed over the fixed `denominator` (20 by
    default) - an UNAVAILABLE post counts as not-YES on every rubric
    question rather than shrinking the denominator, so a run with
    several unavailable posts cannot look artificially cleaner than one
    with none."""
    total = len(verdicts)
    unavailable = sum(1 for v in verdicts if _get(v, "availability") == "UNAVAILABLE")
    available = total - unavailable

    a_yes = sum(1 for v in verdicts if _get(v, "a_genuine_problem_report") == "YES")
    b_yes = sum(1 for v in verdicts if _get(v, "b_operational_economic_consequence") == "YES")
    c_yes = sum(1 for v in verdicts if _get(v, "c_noise") == "YES")
    d_yes = sum(1 for v in verdicts if _get(v, "d_incremental_vs_discovery_lab") == "YES")
    e_yes = sum(1 for v in verdicts if _get(v, "e_corroboration_worthy") == "YES")

    if e_yes <= FAIL_MAX:
        decision = "FAIL"
        decision_reason = (
            f"{e_yes}/{denominator} corroboration-worthy <= {FAIL_MAX} - X is producing too much "
            "noise for the current query/filter design. Do not integrate or schedule."
        )
    elif e_yes <= ITERATE_MAX:
        decision = "INSUFFICIENT_DATA_ITERATE"
        decision_reason = (
            f"{e_yes}/{denominator} corroboration-worthy - there is signal, but the current "
            "search/filter design is too weak. Do not integrate or schedule. A later Query "
            "Iteration 2 may be justified."
        )
    else:
        decision = "PASS_CANDIDATE"
        decision_reason = (
            f"{e_yes}/{denominator} corroboration-worthy - at least half the deterministic sample "
            "deserves independent corroboration. This still does not authorize integration or "
            "scheduling; the next gate is actual independent corroboration of a smaller subset."
        )

    return AuditReportMetrics(
        total_selected=total,
        available=available,
        unavailable=unavailable,
        a_yes=a_yes,
        b_yes=b_yes,
        c_yes=c_yes,
        d_yes=d_yes,
        e_yes=e_yes,
        genuine_problem_rate=round(a_yes / denominator, 4),
        consequence_rate=round(b_yes / denominator, 4),
        noise_rate=round(c_yes / denominator, 4),
        apparently_incremental_rate=round(d_yes / denominator, 4),
        corroboration_worthy_rate=round(e_yes / denominator, 4),
        decision=decision,
        decision_reason=decision_reason,
    )


def render_markdown(metrics: AuditReportMetrics, run_id: str) -> str:
    lines = [
        "# X Signal Probe - Run 1 Human Quality Audit",
        "",
        f"Run audited: {run_id}. 20 posts selected deterministically from Run 1's "
        "`candidate_incremental` observations - see `audit/run1-sample-*.json` for the frozen "
        "selection (algorithm, seed, and IDs, recorded before any rehydration).",
        "",
        "## Counts",
        f"- total selected: {metrics.total_selected}",
        f"- available: {metrics.available}",
        f"- unavailable (not replaced): {metrics.unavailable}",
        f"- A genuine problem report = YES: {metrics.a_yes}",
        f"- B operational/economic consequence = YES: {metrics.b_yes}",
        f"- C noise = YES: {metrics.c_yes}",
        f"- D incremental vs Discovery Lab = YES: {metrics.d_yes}",
        f"- E corroboration worthy = YES: {metrics.e_yes}",
        "",
        "## Rates (denominator fixed at 20 - an unavailable post counts as not-YES everywhere, "
        "never excluded from the denominator)",
        f"- genuine_problem_rate: {metrics.genuine_problem_rate}",
        f"- consequence_rate: {metrics.consequence_rate}",
        f"- noise_rate: {metrics.noise_rate}",
        f"- apparently_incremental_rate: {metrics.apparently_incremental_rate}",
        f"- corroboration_worthy_rate: {metrics.corroboration_worthy_rate}",
        "",
        f"## Decision: {metrics.decision}",
        metrics.decision_reason,
        "",
        "No decision outcome above authorizes integrating, scheduling, or promoting X to a "
        "production Discovery Lab source.",
    ]
    return "\n".join(lines) + "\n"
