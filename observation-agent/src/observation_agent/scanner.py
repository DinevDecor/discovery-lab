"""Read-only filesystem walking. No function in this module opens a
file in write/append mode, deletes anything, or invokes any external
process. See tests/test_safety.py for a static check enforcing this
across the whole package, not just this module."""

from __future__ import annotations

import os
from pathlib import Path


def _is_excluded_path(rel_dir: Path, excluded_path_parts: list[tuple[str, ...]]) -> bool:
    """True if `rel_dir` (relative to the scan root) is exactly one of
    the configured excluded_paths, or nested inside one. Path-segment
    aware — "observation-agent/reports" excludes that directory and
    everything under it, but never "observation-agent/reports-extra"
    (a naive string-prefix check would wrongly match that)."""
    dir_parts = rel_dir.parts
    for ex_parts in excluded_path_parts:
        if dir_parts[: len(ex_parts)] == ex_parts:
            return True
    return False


def walk_files(
    root: str,
    excluded_dirs: list[str],
    extensions: list[str] | None = None,
    excluded_paths: list[str] | None = None,
) -> list[Path]:
    """Return every file under `root` (recursively), skipping
    `excluded_dirs` by bare directory name at any depth (e.g. `.git`,
    `__pycache__`), optionally filtered by extension, and additionally
    skipping `excluded_paths` — explicit paths *relative to `root`*
    (e.g. `observation-agent/reports`) rather than bare names, for
    excluding one specific directory without also hiding every
    unrelated directory that happens to share its name elsewhere in
    the tree. Read-only: os.walk does not modify anything it visits."""
    root_path = Path(root)
    if not root_path.exists():
        return []

    excluded_path_parts = [Path(p).parts for p in (excluded_paths or [])]

    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root_path):
        current_dir = Path(dirpath)
        rel_dir = current_dir.relative_to(root_path)
        dirnames[:] = [
            d
            for d in dirnames
            if d not in excluded_dirs
            and not _is_excluded_path(rel_dir / d, excluded_path_parts)
        ]
        if _is_excluded_path(rel_dir, excluded_path_parts):
            continue
        for fname in filenames:
            p = current_dir / fname
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
