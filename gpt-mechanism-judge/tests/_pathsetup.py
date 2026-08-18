"""Import-path setup shared by every test module - adds this package's
src/ to sys.path so tests can `import gpt_mechanism_judge` without
installing the package."""

import sys
from pathlib import Path

_SRC = str(Path(__file__).resolve().parents[1] / "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
