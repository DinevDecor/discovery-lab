from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from capability_observatory.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
