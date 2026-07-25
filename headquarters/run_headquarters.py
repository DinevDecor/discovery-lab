"""Convenience entry point — mirrors observation-agent's own
run_observation_agent.py. `python3 run_headquarters.py [--config ...]
[--reports-dir ...]`."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from headquarters.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
