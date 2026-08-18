"""Per-critic redaction of the disagreement set - the mechanism that
makes task §4's hard rule ("Claude MUST NOT receive Claude's original
analysis" / "GPT MUST NOT receive GPT's original analysis") actually
true, not just documented.

A raw `Disagreement` carries BOTH `claude_value` and `gpt_value` for a
field (it has to - that is what "disagreement" means). If the Claude
Falsifier were shown that object directly, it would see its own prior
`claude_value` sitting right next to GPT's value - a straightforward
self-review leak. `redact_for_critic` strips the critic's own value from
every entry before anything is ever formatted into a prompt, leaving
only the field name and the OTHER provider's value (the actual analysis
under review) - the exact and only thing the Falsifier prompt template
(falsify.py) is allowed to see about the disagreement.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .models import Disagreement


def redact_for_critic(disagreements: List[Disagreement], *, critic_is_claude: bool) -> List[Dict[str, Any]]:
    """Returns one `{"field": ..., "target_value": ...}` dict per
    disagreement, where `target_value` is always the OTHER provider's
    value - never the critic's own. `critic_is_claude=True` means "this
    is being built for the Claude Falsifier, which is reviewing GPT's
    analysis", so `target_value` = `gpt_value`; `critic_is_claude=False`
    means the reverse."""
    redacted = []
    for d in disagreements:
        target_value = d.gpt_value if critic_is_claude else d.claude_value
        redacted.append({"field": d.field, "target_value": target_value})
    return redacted
