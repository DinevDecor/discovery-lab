from .broken_references import check_broken_references
from .orphan_files import check_orphan_files
from .registry_check import check_registry_entries
from .stale_state import check_stale_state
from .status_history_consistency import check_status_history_consistency

ALL_CHECKS = [
    "check_broken_references",
    "check_orphan_files",
    "check_registry_entries",
    "check_stale_state",
    "check_status_history_consistency",
]

__all__ = ALL_CHECKS
