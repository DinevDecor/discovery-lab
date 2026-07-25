"""Import-path setup shared by every test module — adds src/ to
sys.path so tests can `import headquarters` without installing the
package. Same pattern as observation-agent/tests/_pathsetup.py."""

import sys
from pathlib import Path

_SRC = str(Path(__file__).resolve().parents[1] / "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
