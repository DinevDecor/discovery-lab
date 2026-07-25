#!/usr/bin/env python3
"""Convenience entry point: `python run_research_sensor.py --captures
<path>` from this directory. Equivalent to `python -m
research_sensor.cli` with the default config/ and reports/ paths."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from research_sensor.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
