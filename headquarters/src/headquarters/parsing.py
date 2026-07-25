"""Small, tolerant text parsers for the heterogeneous artifact formats
this ecosystem actually uses. No third-party dependency (no PyYAML,
same constraint observation-agent already works under) and no attempt
to force one schema onto files that were never written to a shared
spec — STATE.md alone has three different real shapes across the five
configured repositories (fenced ```yaml, fenced plain-text, and no
fence at all). Every parser here degrades to an empty dict rather than
raising, so a malformed or absent file becomes an honest "no evidence"
result upstream, never a crash.
"""

from __future__ import annotations

import re

_FENCE = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)
_LOOSE_KV = re.compile(r"^([A-Za-z][\w /()\-]{1,40}?)\s*:\s+(\S.*)$")


def extract_fenced_blocks(text: str) -> list[str]:
    """Return the content of every fenced code block in `text`, in
    document order. Tag-agnostic (```yaml, ```, ```json all match)."""
    return [m.group(1) for m in _FENCE.finditer(text)]


def parse_fenced_key_values(fence_text: str) -> dict[str, str]:
    """Parse `key: value` lines from one fenced block's content.
    Indentation-sensitive continuation: a line that starts with
    whitespace is appended to the previous key's value (handles
    RECOMMENDATION-LEDGER.md's wrapped `summary:` fields) rather than
    being mistaken for a new field."""
    fields: dict[str, str] = {}
    last_key: str | None = None
    for raw_line in fence_text.splitlines():
        if not raw_line.strip():
            continue
        if raw_line[0] in (" ", "\t") and last_key is not None:
            fields[last_key] = f"{fields[last_key]} {raw_line.strip()}"
            continue
        m = re.match(r"^([A-Za-z_][\w]*)\s*:\s*(.*)$", raw_line)
        if m:
            key, value = m.group(1), m.group(2).strip()
            fields[key] = value
            last_key = key
        else:
            last_key = None
    return fields


def parse_loose_key_values(text: str) -> dict[str, str]:
    """Fallback for files with no fenced block at all (kod's
    PROJECT_STATE.md: `Key       : Value` lines under plain markdown
    headings). No continuation handling — every real example of this
    shape uses single-line values."""
    fields: dict[str, str] = {}
    for raw_line in text.splitlines():
        m = _LOOSE_KV.match(raw_line.strip())
        if m:
            key, value = m.group(1).strip(), m.group(2).strip()
            if key not in fields:
                fields[key] = value
    return fields


def parse_state_fields(text: str) -> dict[str, str]:
    """Best-effort field extraction for a state-like file: try the
    first fenced block first (covers the two fenced formats observed),
    fall back to loose parsing of the whole document (covers kod's
    unfenced format) if the fence yields fewer than 2 fields."""
    blocks = extract_fenced_blocks(text)
    if blocks:
        fields = parse_fenced_key_values(blocks[0])
        if len(fields) >= 2:
            return fields
    return parse_loose_key_values(text)


def parse_markdown_table(text: str) -> tuple[list[str], list[list[str]]]:
    """Parse the first Markdown pipe-table in `text`. Returns
    (headers, rows). Returns ([], []) if no table is found — callers
    must treat that as INSUFFICIENT_EVIDENCE, not an error."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "|" not in line:
            continue
        if i + 1 >= len(lines) or not re.match(r"^\s*\|?\s*:?-{2,}", lines[i + 1]):
            continue
        headers = [c.strip() for c in line.strip().strip("|").split("|")]
        rows: list[list[str]] = []
        for row_line in lines[i + 2:]:
            if "|" not in row_line or not row_line.strip():
                break
            cells = [c.strip() for c in row_line.strip().strip("|").split("|")]
            rows.append(cells)
        return headers, rows
    return [], []


def first_paragraph_after_title(text: str) -> str | None:
    """Return the first substantive paragraph after a README's `#
    Title` line — used as a Purpose fallback. Skips a lone `Status:
    ...` line, which several repos use as their second line."""
    lines = text.splitlines()
    started = False
    buf: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not started:
            if stripped.startswith("#"):
                started = True
            continue
        if not stripped:
            if buf:
                break
            continue
        if stripped.lower().startswith("status:") and not buf:
            continue
        if stripped.startswith("#"):
            break
        buf.append(stripped)
    return " ".join(buf) if buf else None
