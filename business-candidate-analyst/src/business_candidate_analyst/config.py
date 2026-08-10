"""Loads config/thresholds.json. Every numeric/keyword constant used by
signature.py, dimensions.py and lifecycle.py lives in that file, not
scattered as magic numbers in code, so the rubric is inspectable and
auditable without reading source."""

from __future__ import annotations

import json
import os
from typing import Any, Dict

_CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config")
_DEFAULT_PATH = os.path.join(_CONFIG_DIR, "thresholds.json")
_DEFAULT_REARCHITECTURE_PATH = os.path.join(_CONFIG_DIR, "rearchitecture_thresholds.json")


def load_thresholds(path: str = None) -> Dict[str, Any]:
    with open(path or _DEFAULT_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_rearchitecture_thresholds(path: str = None) -> Dict[str, Any]:
    """Mode B's own config (config/rearchitecture_thresholds.json) - kept
    separate from Mode A's thresholds.json on purpose, see that file's
    top-level comment."""
    with open(path or _DEFAULT_REARCHITECTURE_PATH, encoding="utf-8") as f:
        return json.load(f)
