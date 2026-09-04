"""Guarded panel pinning: propose, never silently apply.

config/panel.json currently has source_url_pinned=false on all 20 items
(true as of the Slice 03 design review -- verified directly from the file,
not assumed). Per that panel file's own notes and the design doc's Section
7, pinning a real product URL/identity is an explicit, versioned panel
change (panel_version bump, added_in_panel_version on the pinned item),
never a silent overwrite -- and per this task's own instructions, never a
fabricated URL either.

This module's `apply_pin_proposal()` is the one function that is allowed
to write a pin into a panel dict, and it refuses to do so unless the
caller supplies a new panel_version that actually differs from the
current one. Nothing in this executor's own orchestration (cli.py) calls
it automatically -- a successful automated or human capture only produces
a PinProposal, written to a report file for a human to review and apply
via a separate, explicit, reviewed commit. This is a deliberate choice,
not a missing feature: an unattended job silently rewriting product
identity in the panel is exactly the "silent overwrite" the design
explicitly forbids.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional


class PinApplicationError(ValueError):
    pass


@dataclass(frozen=True)
class PinProposal:
    panel_item_id: str
    proposed_source_url: str
    proposed_source_url_pinned: bool
    proposed_identity_values: Dict[str, Any]
    evidence_capture_id: Optional[str]
    proposed_by_executor: str
    rationale: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def propose_pin(
    panel_item_id: str,
    proposed_source_url: str,
    proposed_identity_values: Dict[str, Any],
    proposed_by_executor: str,
    rationale: str,
    evidence_capture_id: Optional[str] = None,
) -> PinProposal:
    if not proposed_source_url or not proposed_identity_values:
        raise PinApplicationError(
            "a pin proposal must carry a real source_url and non-empty identity_values -- "
            "never propose a pin with fabricated or empty identity"
        )
    return PinProposal(
        panel_item_id=panel_item_id,
        proposed_source_url=proposed_source_url,
        proposed_source_url_pinned=True,
        proposed_identity_values=proposed_identity_values,
        evidence_capture_id=evidence_capture_id,
        proposed_by_executor=proposed_by_executor,
        rationale=rationale,
    )


def apply_pin_proposal(panel: Dict[str, Any], proposal: PinProposal, new_panel_version: str) -> Dict[str, Any]:
    """Returns a NEW panel dict with the proposal applied -- never mutates
    the input. Raises PinApplicationError, and changes nothing, unless
    new_panel_version genuinely differs from panel['panel_version'] and the
    target item exists. This is the structural guard: there is no code
    path in this module that pins an item without bumping panel_version."""
    current_version = panel.get("panel_version")
    if not new_panel_version or new_panel_version == current_version:
        raise PinApplicationError(
            f"new_panel_version ({new_panel_version!r}) must differ from the panel's "
            f"current panel_version ({current_version!r}) -- panel changes are explicit "
            f"and versioned, never a silent overwrite"
        )

    items = panel.get("items", [])
    target_index = next(
        (i for i, item in enumerate(items) if item.get("panel_item_id") == proposal.panel_item_id), None
    )
    if target_index is None:
        raise PinApplicationError(f"panel_item_id {proposal.panel_item_id!r} not found in panel")

    new_items = [dict(item) for item in items]
    target = new_items[target_index]
    target["source_url"] = proposal.proposed_source_url
    target["source_url_pinned"] = True
    target["pinned_identity"] = dict(proposal.proposed_identity_values)
    target["pinned_in_panel_version"] = new_panel_version

    new_panel = dict(panel)
    new_panel["panel_version"] = new_panel_version
    new_panel["items"] = new_items
    return new_panel
