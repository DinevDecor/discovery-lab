"""Lifecycle state machine: never exceeds START_CLOCK_CANDIDATE /
BUY_CALENDAR_CANDIDATE automatically, never jumps WATCH straight to a
MAX_AUTOMATIC state in one round, and REJECTED is terminal (2026-08-15
approval, point 10: human gates remain hard).
"""

import _pathsetup  # noqa: F401
import unittest

from calendar_arbitrage_watch.gate import ReviewDecision
from calendar_arbitrage_watch.lifecycle import apply_review
from calendar_arbitrage_watch.models import (
    ARCHAEOLOGY, BUY_CALENDAR_CANDIDATE, CalendarAssessment, CHEAP_TEST, DISCOVERY,
    LIFECYCLE_STATES, REJECTED, REVIEW_CHALLENGED, REVIEW_CONFIRMED, REVIEW_KILLED,
    START_CLOCK_CANDIDATE, WATCH,
)


def _assessment(state: str, mode: str = DISCOVERY) -> CalendarAssessment:
    return CalendarAssessment(candidate_id="c1", mode=mode, lifecycle_state=state)


class LifecycleTests(unittest.TestCase):
    def test_killed_always_moves_to_rejected(self):
        for state in LIFECYCLE_STATES:
            decision = ReviewDecision("c1", REVIEW_KILLED, ["reason"], "REJECTED")
            new_state, _ = apply_review(_assessment(state), decision)
            self.assertEqual(new_state, REJECTED)

    def test_rejected_never_auto_revives(self):
        for outcome, max_state in ((REVIEW_CONFIRMED, START_CLOCK_CANDIDATE), (REVIEW_CHALLENGED, "WATCH")):
            decision = ReviewDecision("c1", outcome, ["reason"], max_state)
            new_state, reason = apply_review(_assessment(REJECTED), decision)
            self.assertEqual(new_state, REJECTED)
            self.assertIn("out of scope", reason)

    def test_watch_advances_to_cheap_test_first_never_straight_to_max_state(self):
        decision = ReviewDecision("c1", REVIEW_CONFIRMED, ["ok"], START_CLOCK_CANDIDATE)
        new_state, _ = apply_review(_assessment(WATCH), decision)
        self.assertEqual(new_state, CHEAP_TEST)

    def test_cheap_test_advances_to_the_allowed_max_state(self):
        decision = ReviewDecision("c1", REVIEW_CONFIRMED, ["ok"], START_CLOCK_CANDIDATE)
        new_state, _ = apply_review(_assessment(CHEAP_TEST), decision)
        self.assertEqual(new_state, START_CLOCK_CANDIDATE)

    def test_never_exceeds_mode_ceiling_even_if_gate_allows_more(self):
        """DISCOVERY mode's ceiling is START_CLOCK_CANDIDATE; even if a
        gate decision (hypothetically, or via a future bug) named
        BUY_CALENDAR_CANDIDATE as max_allowed_state, DISCOVERY-mode
        lifecycle must not reach it."""
        decision = ReviewDecision("c1", REVIEW_CONFIRMED, ["ok"], BUY_CALENDAR_CANDIDATE)
        new_state, _ = apply_review(_assessment(CHEAP_TEST, mode=DISCOVERY), decision)
        self.assertEqual(new_state, START_CLOCK_CANDIDATE)

    def test_archaeology_mode_ceiling_is_buy_calendar_candidate(self):
        decision = ReviewDecision("c1", REVIEW_CONFIRMED, ["ok"], BUY_CALENDAR_CANDIDATE)
        new_state, _ = apply_review(_assessment(CHEAP_TEST, mode=ARCHAEOLOGY), decision)
        self.assertEqual(new_state, BUY_CALENDAR_CANDIDATE)

    def test_no_lifecycle_state_beyond_the_two_candidate_states_exists(self):
        """Structural proof of the human gate: there is no 'APPLIED',
        'PAID', 'RESERVED', or 'CONTACTED' state to reach."""
        self.assertEqual(set(LIFECYCLE_STATES),
                          {WATCH, CHEAP_TEST, START_CLOCK_CANDIDATE, BUY_CALENDAR_CANDIDATE, REJECTED})

    def test_challenged_caps_at_watch_without_demoting_below_it(self):
        decision = ReviewDecision("c1", REVIEW_CHALLENGED, ["missing evidence"], "WATCH")
        new_state, _ = apply_review(_assessment(START_CLOCK_CANDIDATE), decision)
        self.assertEqual(new_state, WATCH)

    def test_confirmed_holds_state_when_already_at_or_above_supported_level(self):
        decision = ReviewDecision("c1", REVIEW_CONFIRMED, ["still fine"], START_CLOCK_CANDIDATE)
        new_state, reason = apply_review(_assessment(START_CLOCK_CANDIDATE), decision)
        self.assertEqual(new_state, START_CLOCK_CANDIDATE)
        self.assertIn("no change", reason)


if __name__ == "__main__":
    unittest.main()
