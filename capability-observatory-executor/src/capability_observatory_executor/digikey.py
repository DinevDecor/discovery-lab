"""DigiKey Product Information API executor.

Official, public, self-serve API confirmed to exist at
developer.digikey.com (Product Information V4: ProductSearch,
ProductDetails, ProductPricing) during the Slice 03 design review --
verified via the developer portal's own published page list, not assumed.
Preferred over HTML capture per that design doc's Section 4: highest-
confidence path of the five providers.

Schema caveat, stated plainly rather than hidden: this session could not
reach developer.digikey.com to pull the literal response JSON schema (the
same network egress block documented in the Slice 03 design doc's Section
0 applies to developer.digikey.com too). The field paths below
(PRODUCT_PATH, MANUFACTURER_PATH, etc.) are a best-effort mapping based on
DigiKey's publicly described field categories (real-time pricing,
availability, manufacturer product number), NOT independently verified
against a fetched schema document. Treat this as needing a one-time live
check against a sandbox app's actual response before relying on it for a
real weekly run -- flagged in the executor health report until that check
happens (see health.py).

If the API omits a field, the normalized observation carries None for it.
Nothing here ever infers or guesses a value the API did not return.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

from .envelope import ExecutorSubmission
from .transport import HttpResult, Transport

TOKEN_URL = "https://api.digikey.com/v1/oauth2/token"
PRODUCT_DETAILS_URL_TEMPLATE = "https://api.digikey.com/products/v4/search/{product_number}/productdetails"
KEYWORD_SEARCH_URL = "https://api.digikey.com/products/v4/search/keyword"

CLIENT_ID_ENV = "DIGIKEY_CLIENT_ID"
CLIENT_SECRET_ENV = "DIGIKEY_CLIENT_SECRET"


def credentials_available(env: Optional[dict] = None) -> bool:
    env = env if env is not None else os.environ
    return bool(env.get(CLIENT_ID_ENV)) and bool(env.get(CLIENT_SECRET_ENV))


def fetch_access_token(transport: Transport, client_id: str, client_secret: str) -> HttpResult:
    return transport.post_form(
        TOKEN_URL,
        data={"grant_type": "client_credentials", "client_id": client_id, "client_secret": client_secret},
    )


def normalize_product_response(body: Dict[str, Any], identity_field_names) -> Dict[str, Any]:
    """Best-effort extraction, defensive against any of these keys being
    absent -- see module docstring. Returns a C3 `observation` payload
    shape (price, currency, unit, quantity_basis, lead_time_days,
    availability, quote_type, identity_values)."""
    product = body.get("Product") or body.get("product") or {}

    manufacturer = (
        (product.get("Manufacturer") or {}).get("Name")
        or product.get("ManufacturerName")
    )
    mpn = product.get("ManufacturerProductNumber") or product.get("ManufacturerPartNumber")
    package = (
        (product.get("Package") or {}).get("Value")
        or product.get("PackageType")
    )

    identity_candidates = {"manufacturer": manufacturer, "mpn": mpn, "package": package}
    identity_values = {k: v for k, v in identity_candidates.items() if k in identity_field_names and v is not None}

    price = product.get("UnitPrice")
    if price is None:
        standard_pricing = product.get("StandardPricing") or []
        if standard_pricing:
            price = standard_pricing[0].get("UnitPrice")

    quantity_available = product.get("QuantityAvailable")
    if quantity_available is None:
        availability = "unknown"
    elif quantity_available > 0:
        availability = "in_stock"
    else:
        availability = "out_of_stock"

    status = (product.get("ProductStatus") or {}).get("Status")
    if status and "discontinued" in str(status).lower():
        availability = "discontinued"

    lead_time_days = None
    lead_weeks = product.get("ManufacturerLeadWeeks")
    if lead_weeks is not None:
        try:
            lead_time_days = float(lead_weeks) * 7
        except (TypeError, ValueError):
            lead_time_days = None

    return {
        "price": price,
        "currency": product.get("Currency") if price is not None else None,
        "unit": "each" if price is not None else None,
        "quantity_basis": "each_qty1" if price is not None else None,
        "lead_time_days": lead_time_days,
        "availability": availability,
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
    provider = panel_item.get("provider", "provider_d_digikey")
    requested_url = panel_item.get("source_url", "https://www.digikey.com/")

    if not credentials_available(env):
        return ExecutorSubmission(
            panel_item_id=panel_item_id, provider=provider, requested_url=requested_url,
            fetched_at=fetched_at, capture_method="api", executor=executor_id,
            outcome="credentials_error", error_category="missing_credentials",
            notes=f"{CLIENT_ID_ENV} / {CLIENT_SECRET_ENV} not set in environment.",
        )

    client_id = env[CLIENT_ID_ENV]
    client_secret = env[CLIENT_SECRET_ENV]

    token_result = fetch_access_token(transport, client_id, client_secret)
    if token_result.error_kind == "timeout":
        return ExecutorSubmission(
            panel_item_id=panel_item_id, provider=provider, requested_url=TOKEN_URL,
            fetched_at=fetched_at, capture_method="api", executor=executor_id,
            outcome="timeout", error_category="oauth_token_timeout",
        )
    if token_result.error_kind == "network":
        return ExecutorSubmission(
            panel_item_id=panel_item_id, provider=provider, requested_url=TOKEN_URL,
            fetched_at=fetched_at, capture_method="api", executor=executor_id,
            outcome="executor_network_blocked", error_category="oauth_token_network_failure",
        )
    if not token_result.ok:
        outcome = "credentials_error" if token_result.status in (400, 401, 403) else "parse_error"
        return ExecutorSubmission(
            panel_item_id=panel_item_id, provider=provider, requested_url=TOKEN_URL,
            fetched_at=fetched_at, capture_method="api", executor=executor_id,
            outcome=outcome, http_status=token_result.status,
            error_category="oauth_token_rejected", raw_payload=token_result.body,
        )

    token_body = token_result.json_body or {}
    access_token = token_body.get("access_token")
    if not access_token:
        return ExecutorSubmission(
            panel_item_id=panel_item_id, provider=provider, requested_url=TOKEN_URL,
            fetched_at=fetched_at, capture_method="api", executor=executor_id,
            outcome="credentials_error", error_category="oauth_token_missing_in_response",
            raw_payload=token_result.body,
        )

    pinned_mpn = panel_item.get("pinned_identity", {}).get("mpn")
    if pinned_mpn:
        product_url = PRODUCT_DETAILS_URL_TEMPLATE.format(product_number=pinned_mpn)
        product_result = transport.get(
            product_url,
            headers={"Authorization": f"Bearer {access_token}", "X-DIGIKEY-Client-Id": client_id},
        )
    else:
        product_url = KEYWORD_SEARCH_URL
        product_result = transport.post_json(
            product_url,
            payload={"Keywords": panel_item.get("label", ""), "Limit": 1},
            headers={"Authorization": f"Bearer {access_token}", "X-DIGIKEY-Client-Id": client_id},
        )

    if product_result.error_kind == "timeout":
        return ExecutorSubmission(
            panel_item_id=panel_item_id, provider=provider, requested_url=product_url,
            fetched_at=fetched_at, capture_method="api", executor=executor_id, outcome="timeout",
        )
    if product_result.error_kind == "network":
        return ExecutorSubmission(
            panel_item_id=panel_item_id, provider=provider, requested_url=product_url,
            fetched_at=fetched_at, capture_method="api", executor=executor_id,
            outcome="executor_network_blocked",
        )
    if product_result.status == 429:
        return ExecutorSubmission(
            panel_item_id=panel_item_id, provider=provider, requested_url=product_url,
            fetched_at=fetched_at, capture_method="api", executor=executor_id,
            outcome="api_quota_error", http_status=429, raw_payload=product_result.body,
        )
    if not product_result.ok:
        outcome = "credentials_error" if product_result.status in (401, 403) else "parse_error"
        return ExecutorSubmission(
            panel_item_id=panel_item_id, provider=provider, requested_url=product_url,
            fetched_at=fetched_at, capture_method="api", executor=executor_id,
            outcome=outcome, http_status=product_result.status, raw_payload=product_result.body,
        )

    try:
        body = product_result.json_body or {}
    except ValueError:
        return ExecutorSubmission(
            panel_item_id=panel_item_id, provider=provider, requested_url=product_url,
            fetched_at=fetched_at, capture_method="api", executor=executor_id,
            outcome="parse_error", error_category="non_json_response", raw_payload=product_result.body,
        )

    products = body.get("Products") if isinstance(body.get("Products"), list) else None
    single_product = products[0] if products else (body if body.get("Product") or body.get("ManufacturerProductNumber") else None)
    if single_product is None:
        return ExecutorSubmission(
            panel_item_id=panel_item_id, provider=provider, requested_url=product_url,
            fetched_at=fetched_at, capture_method="api", executor=executor_id,
            outcome="source_missing", error_category="no_product_in_response", raw_payload=product_result.body,
        )

    observation = normalize_product_response(single_product, panel_item.get("identity_fields", []))
    return ExecutorSubmission(
        panel_item_id=panel_item_id, provider=provider, requested_url=product_url,
        fetched_at=fetched_at, capture_method="api", executor=executor_id,
        outcome="ok", http_status=product_result.status, raw_payload=product_result.body,
        observation=observation,
    )
