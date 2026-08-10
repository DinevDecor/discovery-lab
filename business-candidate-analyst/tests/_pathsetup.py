"""Import-path setup shared by every test module - adds src/ to
sys.path so tests can `import business_candidate_analyst` without
installing the package."""

import sys
from pathlib import Path

_SRC = str(Path(__file__).resolve().parents[1] / "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
