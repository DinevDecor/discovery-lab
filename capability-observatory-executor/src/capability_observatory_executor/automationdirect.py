"""AutomationDirect reachability probe + simple HTML capture.

Per the Slice 03 design doc's Section 4: AutomationDirect had a real but
unverified API signal (an on-site "Product API" reference and a live
community-forum thread titled "API for price and stock status on
AutomationDirect") that this session could not reach to confirm. Absent a
verified API, this module is the HTML-capture candidate -- gated by an
explicit reachability + robots.txt probe BEFORE any capture is attempted,
never assumed working.

Hard boundary, not a style choice: no stealth headers, no header spoofing
beyond an honestly-identified User-Agent, no proxy rotation, no CAPTCHA
handling, no retry-until-it-works-around-a-block. If the probe fails for
any reason, the classification is PROVIDER_BLOCKED or EXECUTOR_FAILURE and
the caller routes to HUMAN_FALLBACK -- this module never tries harder to
get through.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .envelope import ExecutorSubmission
from .transport import Transport

BASE_URL = "https://www.automationdirect.com/"
ROBOTS_URL = "https://www.automationdirect.com/robots.txt"


def _parse_robots_disallow_for_star(robots_text: str) -> List[str]:
    """Minimal robots.txt parser: Disallow rules under the first
    `User-agent: *` block only. Deliberately not a full RFC 9309
    implementation -- this executor only ever needs a yes/no on one path
    (the homepage / a category page), not general-purpose crawling."""
    disallows: List[str] = []
    in_star_block = False
    seen_star_block = False
    for raw_line in robots_text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip().lower()
        value = value.strip()
        if key == "user-agent":
            in_star_block = value == "*"
            if in_star_block:
                seen_star_block = True
        elif key == "disallow" and in_star_block:
            if value:
                disallows.append(value)
    if not seen_star_block:
        return []
    return disallows


def path_is_allowed(robots_text: str, path: str) -> bool:
    disallows = _parse_robots_disallow_for_star(robots_text)
    return not any(path.startswith(rule) for rule in disallows)


@dataclass(frozen=True)
class ProbeResult:
    classification: str   # "AUTOMATED_OK" | "PROVIDER_BLOCKED" | "EXECUTOR_FAILURE"
    reachable: bool
    robots_checked: bool
    robots_allowed: Optional[bool]
    detail: str


def probe(transport: Transport, base_url: str = BASE_URL, robots_url: str = ROBOTS_URL) -> ProbeResult:
    robots_result = transport.get(robots_url)
    if robots_result.error_kind == "network":
        return ProbeResult("EXECUTOR_FAILURE", reachable=False, robots_checked=False, robots_allowed=None,
                            detail="robots.txt fetch failed: executor network failure")
    if robots_result.error_kind == "timeout":
        return ProbeResult("EXECUTOR_FAILURE", reachable=False, robots_checked=False, robots_allowed=None,
                            detail="robots.txt fetch failed: timeout")

    robots_allowed = True
    robots_checked = False
    if robots_result.ok:
        robots_checked = True
        robots_allowed = path_is_allowed(robots_result.body, "/")
        if not robots_allowed:
            return ProbeResult("PROVIDER_BLOCKED", reachable=True, robots_checked=True, robots_allowed=False,
                                detail="robots.txt disallows the path this executor would fetch")

    page_result = transport.get(base_url)
    if page_result.error_kind == "network":
        return ProbeResult("EXECUTOR_FAILURE", reachable=False, robots_checked=robots_checked,
                            robots_allowed=robots_allowed, detail="homepage fetch failed: executor network failure")
    if page_result.error_kind == "timeout":
        return ProbeResult("EXECUTOR_FAILURE", reachable=False, robots_checked=robots_checked,
                            robots_allowed=robots_allowed, detail="homepage fetch failed: timeout")
    if page_result.status in (403, 429) or (page_result.status and 500 <= page_result.status < 600):
        return ProbeResult("PROVIDER_BLOCKED", reachable=False, robots_checked=robots_checked,
                            robots_allowed=robots_allowed, detail=f"homepage returned http_status={page_result.status}")
    if not page_result.ok:
        return ProbeResult("PROVIDER_BLOCKED", reachable=False, robots_checked=robots_checked,
                            robots_allowed=robots_allowed, detail=f"homepage returned http_status={page_result.status}")

    return ProbeResult("AUTOMATED_OK", reachable=True, robots_checked=robots_checked,
                        robots_allowed=robots_allowed, detail=f"homepage reachable, http_status={page_result.status}")


def run(
    panel_item: Dict[str, Any],
    probe_result: ProbeResult,
    transport: Transport,
    fetched_at: str,
    executor_id: str = "automation:gh-actions-executor:v1",
) -> ExecutorSubmission:
    panel_item_id = panel_item["panel_item_id"]
    provider = panel_item.get("provider", "provider_a_automationdirect")
    requested_url = panel_item.get("source_url", BASE_URL)

    if probe_result.classification == "EXECUTOR_FAILURE":
        return ExecutorSubmission(
            panel_item_id=panel_item_id, provider=provider, requested_url=requested_url,
            fetched_at=fetched_at, capture_method="html", executor=executor_id,
            outcome="executor_network_blocked", error_category="probe_failed",
            notes=probe_result.detail,
        )
    if probe_result.classification == "PROVIDER_BLOCKED":
        return ExecutorSubmission(
            panel_item_id=panel_item_id, provider=provider, requested_url=requested_url,
            fetched_at=fetched_at, capture_method="html", executor=executor_id,
            outcome="provider_access_blocked", error_category="probe_failed",
            notes=probe_result.detail,
        )

    if not panel_item.get("source_url_pinned", False):
        # Never fabricate a plausible-looking product URL. The panel item's
        # source_url is a bare category/homepage page (see
        # config/panel.json's own notes) -- there is no price to extract
        # from it. This is an honest non-result, not a failure of this
        # probe: the probe itself succeeded (see AUTOMATED_OK above).
        return ExecutorSubmission(
            panel_item_id=panel_item_id, provider=provider, requested_url=requested_url,
            fetched_at=fetched_at, capture_method="html", executor=executor_id,
            outcome="parse_error", error_category="panel_item_not_pinned_to_product_page",
            raw_payload=f"Probe succeeded ({probe_result.detail}); source_url is an unpinned category/homepage "
                        f"page, not a specific product page. No price/stock/lead-time was attempted.",
        )

    page_result = transport.get(requested_url)
    if page_result.error_kind == "network":
        return ExecutorSubmission(
            panel_item_id=panel_item_id, provider=provider, requested_url=requested_url,
            fetched_at=fetched_at, capture_method="html", executor=executor_id,
            outcome="executor_network_blocked",
        )
    if page_result.error_kind == "timeout":
        return ExecutorSubmission(
            panel_item_id=panel_item_id, provider=provider, requested_url=requested_url,
            fetched_at=fetched_at, capture_method="html", executor=executor_id, outcome="timeout",
        )
    if page_result.status == 404:
        return ExecutorSubmission(
            panel_item_id=panel_item_id, provider=provider, requested_url=requested_url,
            fetched_at=fetched_at, capture_method="html", executor=executor_id,
            outcome="source_missing", http_status=404, raw_payload=page_result.body,
        )
    if not page_result.ok:
        return ExecutorSubmission(
            panel_item_id=panel_item_id, provider=provider, requested_url=requested_url,
            fetched_at=fetched_at, capture_method="html", executor=executor_id,
            outcome="provider_access_blocked", http_status=page_result.status, raw_payload=page_result.body,
        )

    # A real weekly run needs a page-specific parser once a real product
    # page is pinned (Section 7 of the design doc) -- out of scope until
    # that pinning happens, since a parser for a URL that doesn't exist yet
    # would itself be a fabrication. Record the fetch as evidence, without
    # inventing extracted fields.
    return ExecutorSubmission(
        panel_item_id=panel_item_id, provider=provider, requested_url=requested_url,
        fetched_at=fetched_at, capture_method="html", executor=executor_id,
        outcome="parse_error", http_status=page_result.status, raw_payload=page_result.body,
        error_category="no_parser_implemented_for_this_product_page",
    )
