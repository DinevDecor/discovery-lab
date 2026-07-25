#!/usr/bin/env python3
"""Convenience entry point: `python run_observation_agent.py` from this
directory. Equivalent to `python -m observation_agent.cli` with the
default config.json and reports/ paths."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from observation_agent.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
