#!/usr/bin/env python3
"""Convenience entry point: `python run_reality_sensor.py --captures
<path>` from this directory. Equivalent to `python -m
reality_sensor.cli` with the default config/ and reports/ paths."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from reality_sensor.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
