"""The only module in the audit subsystem allowed to open a file in a
writing mode - mirrors probe.py/report.py's role in the discovery-run
package (tests/test_audit_safety.py enforces this). Every write stays
under x-signal-probe/audit/. None of these functions accept post text -
only already-built payload dicts or AuditVerdict objects, which
structurally cannot carry it (see audit_models.py)."""

from __future__ import annotations

import json
import os

from .audit_models import to_dict


def write_sample_file(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def append_verdict_line(path: str, verdict) -> None:
    """Append-only, flushed immediately, never read back by this module
    - the review loop that calls this must not re-open `path` for
    reading mid-session (see audit_review.py / review_audit_sample.py),
    which is what keeps a later reviewer's judgment blind to earlier
    ones within the same run."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(to_dict(verdict), ensure_ascii=False) + "\n")
        f.flush()


def write_report_file(path: str, markdown_text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(markdown_text)
