"""Mouser Electronics Search API executor.

Official, public, free, self-serve API confirmed during the Slice 03
design review (mouser.com/api-hub -- key via a request form, 1-2 business
day approval, rate-limited 30 calls/min / 1000 calls/day). Mouser's own
published field list explicitly includes lead time, availability, and
pricing -- the most complete single-call match to what C3 needs of any of
the five providers.

Same schema caveat as digikey.py: this session could not reach
mouser.com/api-hub to pull the literal response JSON (same egress block).
The field parsing below matches Mouser's publicly documented field names
and known response shape, not an independently re-fetched schema -- flag
for one-time live verification before relying on it for a real weekly run.

Simpler auth than DigiKey: a single API key as a query parameter, no OAuth
token exchange.
"""

from __future__ import annotations

import os
import re
from typing import Any, Dict, Optional

from .envelope import ExecutorSubmission
from .transport import Transport

SEARCH_URL_TEMPLATE = "https://api.mouser.com/api/v1/search/keyword?apiKey={api_key}"

API_KEY_ENV = "MOUSER_API_KEY"

_LEAD_TIME_WEEKS_RE = re.compile(r"(\d+(?:\.\d+)?)\s*week", re.IGNORECASE)
_LEAD_TIME_DAYS_RE = re.compile(r"(\d+(?:\.\d+)?)\s*day", re.IGNORECASE)
_PRICE_RE = re.compile(r"[\d.,]+")
_LEADING_QUANTITY_RE = re.compile(r"^\s*([\d,]+)\s")


def credentials_available(env: Optional[dict] = None) -> bool:
    env = env if env is not None else os.environ
    return bool(env.get(API_KEY_ENV))


def _parse_lead_time_days(lead_time_text: Optional[str]) -> Optional[float]:
    if not lead_time_text:
        return None
    weeks_match = _LEAD_TIME_WEEKS_RE.search(lead_time_text)
    if weeks_match:
        return float(weeks_match.group(1)) * 7
    days_match = _LEAD_TIME_DAYS_RE.search(lead_time_text)
    if days_match:
        return float(days_match.group(1))
    return None


def _parse_availability(availability_text: Optional[str]) -> str:
    if not availability_text:
        return "unknown"
    text = availability_text.lower()
    if "obsolete" in text or "discontinued" in text or "not for new design" in text:
        return "discontinued"
    if "backorder" in text or "back order" in text:
        return "backorder"
    if "out of stock" in text:
        return "out_of_stock"
    # A leading quantity ("1500 In Stock" / "0 In Stock") is more specific
    # than the word "stock" alone -- check it before the generic phrase
    # match below, or "0 In Stock" would false-positive as in_stock.
    quantity_match = _LEADING_QUANTITY_RE.match(availability_text)
    if quantity_match and "stock" in text:
        quantity = int(quantity_match.group(1).replace(",", ""))
        return "in_stock" if quantity > 0 else "out_of_stock"
    if "in stock" in text:
        return "in_stock"
    return "unknown"


def _parse_price(price_text: Optional[str]) -> Optional[float]:
    if not price_text:
        return None
    match = _PRICE_RE.search(price_text.replace(",", ""))
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def normalize_part_response(part: Dict[str, Any], identity_field_names) -> Dict[str, Any]:
    manufacturer = part.get("Manufacturer")
    mpn = part.get("ManufacturerPartNumber")
    package = part.get("Package") or part.get("PackagingType")

    identity_candidates = {"manufacturer": manufacturer, "mpn": mpn, "package": package}
    identity_values = {k: v for k, v in identity_candidates.items() if k in identity_field_names and v is not None}

    price_breaks = part.get("PriceBreaks") or []
    price = None
    currency = None
    if price_breaks:
        first_break = price_breaks[0]
        price = _parse_price(first_break.get("Price"))
        currency = first_break.get("Currency")

    return {
        "price": price,
        "currency": currency,
        "unit": "each" if price is not None else None,
        "quantity_basis": "each_qty1" if price is not None else None,
        "lead_time_days": _parse_lead_time_days(part.get("LeadTime")),
        "availability": _parse_availability(part.get("Availability")),
        "quote_type": "list_price",
        "identity_values": identity_values,
    }


def run(
    panel_item: Dict[str, Any],
    transport: Transport,
    fetched_at: str,
    executor_id: str = "automation:gh-actions-executor:v1",
    env: Optional[dict] = None,
) -> ExecutorSubmission:
    env = env if env is not None else os.environ
    panel_item_id = panel_item["panel_item_id"]
    provider = panel_item.get("provider", "provider_e_mouser")
    requested_url = panel_item.get("source_url", "https://www.mouser.com/")

    if not credentials_available(env):
        return ExecutorSubmission(
            panel_item_id=panel_item_id, provider=provider, requested_url=requested_url,
            fetched_at=fetched_at, capture_method="api", executor=executor_id,
            outcome="credentials_error", error_category="missing_credentials",
            notes=f"{API_KEY_ENV} not set in environment.",
        )

    api_key = env[API_KEY_ENV]
    pinned_mpn = panel_item.get("pinned_identity", {}).get("mpn")
    keyword = pinned_mpn or panel_item.get("label", "")
    search_url = SEARCH_URL_TEMPLATE.format(api_key=api_key)

    result = transport.post_json(search_url, payload={"SearchByKeywordRequest": {"keyword": keyword, "records": 1}})

    if result.error_kind == "timeout":
        return ExecutorSubmission(
            panel_item_id=panel_item_id, provider=provider, requested_url=requested_url,
            fetched_at=fetched_at, capture_method="api", executor=executor_id, outcome="timeout",
        )
    if result.error_kind == "network":
        return ExecutorSubmission(
            panel_item_id=panel_item_id, provider=provider, requested_url=requested_url,
            fetched_at=fetched_at, capture_method="api", executor=executor_id,
            outcome="executor_network_blocked",
        )
    if result.status == 429:
        return ExecutorSubmission(
            panel_item_id=panel_item_id, provider=provider, requested_url=requested_url,
            fetched_at=fetched_at, capture_method="api", executor=executor_id,
            outcome="api_quota_error", http_status=429, raw_payload=result.body,
        )
    if result.status in (401, 403):
        return ExecutorSubmission(
            panel_item_id=panel_item_id, provider=provider, requested_url=requested_url,
            fetched_at=fetched_at, capture_method="api", executor=executor_id,
            outcome="credentials_error", http_status=result.status, raw_payload=result.body,
        )
    if not result.ok:
        return ExecutorSubmission(
            panel_item_id=panel_item_id, provider=provider, requested_url=requested_url,
            fetched_at=fetched_at, capture_method="api", executor=executor_id,
            outcome="parse_error", http_status=result.status, raw_payload=result.body,
        )

    try:
        body = result.json_body or {}
    except ValueError:
        return ExecutorSubmission(
            panel_item_id=panel_item_id, provider=provider, requested_url=requested_url,
            fetched_at=fetched_at, capture_method="api", executor=executor_id,
            outcome="parse_error", error_category="non_json_response", raw_payload=result.body,
        )

    errors = body.get("Errors") or []
    if errors:
        error_codes = {str(e.get("Code", "")).lower() for e in errors if isinstance(e, dict)}
        if any("quota" in c or "limit" in c for c in error_codes):
            outcome = "api_quota_error"
        elif any("key" in c or "auth" in c for c in error_codes):
            outcome = "credentials_error"
        else:
            outcome = "parse_error"
        return ExecutorSubmission(
            panel_item_id=panel_item_id, provider=provider, requested_url=requested_url,
            fetched_at=fetched_at, capture_method="api", executor=executor_id,
            outcome=outcome, error_category="mouser_api_error", raw_payload=result.body,
        )

    parts = (body.get("SearchResults") or {}).get("Parts") or []
    if not parts:
        return ExecutorSubmission(
            panel_item_id=panel_item_id, provider=provider, requested_url=requested_url,
            fetched_at=fetched_at, capture_method="api", executor=executor_id,
            outcome="source_missing", error_category="no_part_in_response", raw_payload=result.body,
        )

    observation = normalize_part_response(parts[0], panel_item.get("identity_fields", []))
    return ExecutorSubmission(
        panel_item_id=panel_item_id, provider=provider, requested_url=requested_url,
        fetched_at=fetched_at, capture_method="api", executor=executor_id,
        outcome="ok", http_status=result.status, raw_payload=result.body, observation=observation,
    )
