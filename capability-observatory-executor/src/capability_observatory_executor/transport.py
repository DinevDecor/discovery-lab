"""The one seam where this executor actually touches the network.

Every fetch (digikey.py, mouser.py, automationdirect.py) goes through
HttpResult / Transport.get() / Transport.post_form(), never urllib
directly. This exists for exactly one reason: tests need to run offline
and deterministic (project rule, capability-observatory/README.md and
CLAUDE.md both say so) without live network access, and dependency
injection is the smallest mechanism that allows that -- a test passes a
FakeTransport; real runs use RealTransport, which is the only thing in
this whole package that imports urllib.

Stdlib only, matching the rest of this repo's zero-dependency convention
(no requests, no httpx -- see capability-observatory/tests/test_safety.py's
own ban list for that package).
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Dict, Optional, Protocol


@dataclass(frozen=True)
class HttpResult:
    """Uniform shape whether the request succeeded, was rejected by the
    server, or never got a response at all."""
    ok: bool
    status: Optional[int]
    body: str
    final_url: str
    error_kind: Optional[str] = None   # "network" | "timeout" | None

    @property
    def json_body(self):
        return json.loads(self.body) if self.body else None


class Transport(Protocol):
    def get(self, url: str, headers: Optional[Dict[str, str]] = None, timeout: float = 15.0) -> HttpResult: ...

    def post_form(
        self, url: str, data: Dict[str, str], headers: Optional[Dict[str, str]] = None, timeout: float = 15.0
    ) -> HttpResult: ...

    def post_json(
        self, url: str, payload: dict, headers: Optional[Dict[str, str]] = None, timeout: float = 15.0
    ) -> HttpResult: ...


class RealTransport:
    """Plain, honestly-identified HTTP client. No stealth headers, no
    proxy rotation, no CAPTCHA handling, no retries-through-a-challenge --
    a normal client making a normal request, exactly what Section 3 of the
    Slice 03 design doc requires."""

    def __init__(self, user_agent: str = "discovery-lab-capability-observatory-executor/1.0"):
        self.user_agent = user_agent

    def _do(self, request: urllib.request.Request, timeout: float) -> HttpResult:
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = response.read().decode("utf-8", errors="replace")
                return HttpResult(
                    ok=True, status=response.status, body=body,
                    final_url=response.geturl(),
                )
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
            return HttpResult(
                ok=False, status=exc.code, body=body,
                final_url=getattr(exc, "url", request.full_url) or request.full_url,
                error_kind=None,
            )
        except TimeoutError:
            return HttpResult(ok=False, status=None, body="", final_url=request.full_url, error_kind="timeout")
        except urllib.error.URLError as exc:
            reason = str(getattr(exc, "reason", exc))
            error_kind = "timeout" if "timed out" in reason.lower() else "network"
            return HttpResult(ok=False, status=None, body="", final_url=request.full_url, error_kind=error_kind)

    def get(self, url: str, headers: Optional[Dict[str, str]] = None, timeout: float = 15.0) -> HttpResult:
        req_headers = {"User-Agent": self.user_agent}
        req_headers.update(headers or {})
        request = urllib.request.Request(url, headers=req_headers, method="GET")
        return self._do(request, timeout)

    def post_form(
        self, url: str, data: Dict[str, str], headers: Optional[Dict[str, str]] = None, timeout: float = 15.0
    ) -> HttpResult:
        req_headers = {"User-Agent": self.user_agent, "Content-Type": "application/x-www-form-urlencoded"}
        req_headers.update(headers or {})
        body = urllib.parse.urlencode(data).encode("utf-8")
        request = urllib.request.Request(url, data=body, headers=req_headers, method="POST")
        return self._do(request, timeout)

    def post_json(
        self, url: str, payload: dict, headers: Optional[Dict[str, str]] = None, timeout: float = 15.0
    ) -> HttpResult:
        req_headers = {"User-Agent": self.user_agent, "Content-Type": "application/json"}
        req_headers.update(headers or {})
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(url, data=body, headers=req_headers, method="POST")
        return self._do(request, timeout)


class FakeTransport:
    """Deterministic, offline stand-in for tests. Programmed with a fixed
    list of responses, returned in call order -- never touches a socket."""

    def __init__(self, responses: list):
        self._responses = list(responses)
        self.calls = []

    def _next(self, kind: str, url: str) -> HttpResult:
        self.calls.append((kind, url))
        if not self._responses:
            raise AssertionError("FakeTransport exhausted -- test issued more requests than programmed")
        return self._responses.pop(0)

    def get(self, url: str, headers: Optional[Dict[str, str]] = None, timeout: float = 15.0) -> HttpResult:
        return self._next("GET", url)

    def post_form(
        self, url: str, data: Dict[str, str], headers: Optional[Dict[str, str]] = None, timeout: float = 15.0
    ) -> HttpResult:
        return self._next("POST_FORM", url)

    def post_json(
        self, url: str, payload: dict, headers: Optional[Dict[str, str]] = None, timeout: float = 15.0
    ) -> HttpResult:
        return self._next("POST_JSON", url)
