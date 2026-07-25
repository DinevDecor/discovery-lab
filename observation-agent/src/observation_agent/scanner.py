"""Read-only filesystem walking. No function in this module opens a
file in write/append mode, deletes anything, or invokes any external
process. See tests/test_safety.py for a static check enforcing this
across the whole package, not just this module."""

from __future__ import annotations

import os
from pathlib import Path


def walk_files(
    root: str,
    excluded_dirs: list[str],
    extensions: list[str] | None = None,
) -> list[Path]:
    """Return every file under `root` (recursively), skipping
    `excluded_dirs` by name at any depth, optionally filtered by
    extension. Read-only: os.walk does not modify anything it visits."""
    root_path = Path(root)
    if not root_path.exists():
        return []

    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in excluded_dirs]
        for fname in filenames:
            p = Path(dirpath) / fname
            if extensions is None or p.suffix in extensions:
                found.append(p)
    return found


def read_text(path: Path) -> str | None:
    """Read a file as UTF-8 text, tolerating decode errors by
    returning None rather than raising — a binary or corrupt file is
    reported as unreadable, not crashed on."""
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return -1


def newest_mtime(paths: list[Path]) -> float | None:
    mtimes = []
    for p in paths:
        try:
            mtimes.append(p.stat().st_mtime)
        except OSError:
            continue
    return max(mtimes) if mtimes else None
