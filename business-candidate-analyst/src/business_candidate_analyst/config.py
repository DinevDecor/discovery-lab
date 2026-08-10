"""Loads config/thresholds.json. Every numeric/keyword constant used by
signature.py, dimensions.py and lifecycle.py lives in that file, not
scattered as magic numbers in code, so the rubric is inspectable and
auditable without reading source."""

from __future__ import annotations

import json
import os
from typing import Any, Dict

_DEFAULT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "config", "thresholds.json",
)


def load_thresholds(path: str = None) -> Dict[str, Any]:
    with open(path or _DEFAULT_PATH, encoding="utf-8") as f:
        return json.load(f)
