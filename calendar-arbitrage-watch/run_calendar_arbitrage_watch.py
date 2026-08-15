"""Entrypoint for Calendar Arbitrage Watch. No network, no LLM call, fully
deterministic - see CONTRACT.md.

Subcommands:
  add <file.json> [<file.json> ...]   validate + append + adversarial
                                        review + lifecycle transition +
                                        rebuild snapshot + write report
  report                                re-render the report from current
                                        ledger state, adding nothing
  rebuild                               rebuild data/calendar_candidates.json
                                        from data/calendar_events.jsonl only
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from calendar_arbitrage_watch.cli import main  # noqa: E402

if __name__ == "__main__":
    # --root must precede the subcommand: argparse hands everything after
    # a subparser's positional name to that subparser, so appending
    # --root at the end would not be recognized by the top-level parser.
    root = os.path.dirname(os.path.abspath(__file__))
    argv = sys.argv[1:] if "--root" in sys.argv else ["--root", root] + sys.argv[1:]
    sys.exit(main(argv))
