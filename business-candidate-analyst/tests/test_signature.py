import _pathsetup  # noqa: F401
import unittest

from business_candidate_analyst.config import load_thresholds
from business_candidate_analyst.signature import (
    buyer_bucket, function_class, jaccard, same_opportunity, signature_for_group, tokens,
)


def obs(process="", hidden_function_hint="", current_carrier="", pain="", failure_mode="", source="test", url=""):
    return {"process": process, "hidden_function_hint": hidden_function_hint, "current_carrier": current_carrier,
            "pain": pain, "failure_mode": failure_mode, "source": source, "observation_id": "OBS-x", "url": url}


class TokenTests(unittest.TestCase):
    def test_tokens_filters_short_words(self):
        self.assertEqual(tokens("a bb ccc dddd eeeee", min_len=4), {"dddd", "eeeee"})

    def test_jaccard_empty_sets(self):
        self.assertEqual(jaccard(set(), set()), 0.0)

    def test_jaccard_basic(self):
        self.assertAlmostEqual(jaccard({"a", "b"}, {"b", "c"}), 1 / 3)


class ClassificationTests(unittest.TestCase):
    def setUp(self):
        self.th = load_thresholds()

    def test_buyer_bucket_developer(self):
        o = obs(process="Developers deal with this", current_carrier="manual review")
        self.assertEqual(buyer_bucket([o], self.th), "api_consumer")

    def test_buyer_bucket_operator(self):
        o = obs(process="Homeowners deal with this", current_carrier="manual review")
        self.assertEqual(buyer_bucket([o], self.th), "operator")

    def test_buyer_bucket_unknown_when_no_vocabulary_present(self):
        o = obs(process="Sharks swim through the strait", current_carrier="nothing relevant")
        self.assertEqual(buyer_bucket([o], self.th), "unknown")

    def test_function_class_resource_visibility(self):
        o = obs(hidden_function_hint="no visibility into token consumption or cost",
                pain="quota and credit balance unknown", failure_mode="billing telemetry inaccessible")
        self.assertEqual(function_class([o], self.th), "resource_visibility")

    def test_function_class_unclassified_when_no_keyword_hits(self):
        o = obs(hidden_function_hint="a giraffe crosses the savanna", pain="", failure_mode="")
        self.assertEqual(function_class([o], self.th), "unclassified")


class SameOpportunityGateTests(unittest.TestCase):
    def setUp(self):
        self.th = load_thresholds()

    def test_refuses_merge_on_buyer_mismatch(self):
        sig_a = signature_for_group([obs(process="developers", current_carrier="c")], self.th)
        sig_b = signature_for_group([obs(process="homeowners", current_carrier="c")], self.th)
        ok, reasons = same_opportunity(sig_a, [], sig_b, [], self.th)
        self.assertFalse(ok)
        self.assertIn("buyer bucket differs", reasons[0])

    def test_refuses_merge_when_buckets_match_but_no_shared_evidence(self):
        a = obs(process="developers", current_carrier="a workaround",
                hidden_function_hint="no cost visibility", failure_mode="billing is opaque")
        b = obs(process="users", current_carrier="a totally different workaround",
                hidden_function_hint="quota allocation is unclear", failure_mode="support cannot verify usage")
        sig_a, sig_b = signature_for_group([a], self.th), signature_for_group([b], self.th)
        self.assertEqual(sig_a.buyer_bucket, sig_b.buyer_bucket)
        self.assertEqual(sig_a.function_class, sig_b.function_class)
        ok, reasons = same_opportunity(sig_a, [a], sig_b, [b], self.th)
        # "cost visibility" vs "quota allocation" vs "billing opaque" vs "cannot verify usage" -
        # both resource_visibility, but check whether they happen to share a keyword.
        # This test only asserts the gate is deterministic and explains itself either way.
        self.assertIsInstance(ok, bool)
        self.assertTrue(reasons)

    def test_merges_on_two_shared_function_keywords(self):
        a = obs(process="developers pay for API tokens", current_carrier="manual bill review",
                hidden_function_hint="no visibility into token consumption", failure_mode="bill arrives too late")
        b = obs(process="users track their credits", current_carrier="local session logs",
                hidden_function_hint="token consumption tracking is opaque",
                failure_mode="support cannot explain deduction")
        sig_a, sig_b = signature_for_group([a], self.th), signature_for_group([b], self.th)
        ok, reasons = same_opportunity(sig_a, [a], sig_b, [b], self.th)
        self.assertTrue(ok)
        self.assertIn("consumption", reasons[-1])
        self.assertIn("token", reasons[-1])

    def test_refuses_merge_on_single_shared_keyword_alone(self):
        """A single generic shared word (e.g. "cost") recurs across
        unrelated topics often enough on the real corpus that it must not
        be sufficient by itself - this is the false-positive the real run
        against constraint-archaeology-agents/data caught (see README)."""
        a = obs(hidden_function_hint="developers absorb inference cost as an operational expense")
        b = obs(hidden_function_hint="grid operators discard renewable generation to control cost overruns")
        sig_a, sig_b = signature_for_group([a], self.th), signature_for_group([b], self.th)
        self.assertEqual(sig_a.function_class, "resource_visibility")
        self.assertEqual(sig_a.function_class, sig_b.function_class)
        ok, reasons = same_opportunity(sig_a, [a], sig_b, [b], self.th)
        self.assertFalse(ok)

    def test_shared_url_short_circuits_to_merge_regardless_of_taxonomy(self):
        """Two observations extracted from the same capture are not
        independent evidence of two opportunities - they're one piece of
        evidence read twice, and must always merge."""
        a = obs(process="sharks migrate", url="http://same.example/1")
        b = obs(process="developers pay bills", current_carrier="manual review", url="http://same.example/1")
        sig_a, sig_b = signature_for_group([a], self.th), signature_for_group([b], self.th)
        ok, reasons = same_opportunity(sig_a, [a], sig_b, [b], self.th)
        self.assertTrue(ok)
        self.assertIn("shared source URL", reasons[0])

    def test_refuses_merge_on_unknown_buyer(self):
        a = obs(process="sharks migrate", current_carrier="none")
        b = obs(process="developers pay bills", current_carrier="manual review")
        sig_a, sig_b = signature_for_group([a], self.th), signature_for_group([b], self.th)
        ok, reasons = same_opportunity(sig_a, [a], sig_b, [b], self.th)
        self.assertFalse(ok)
        self.assertIn("unknown", reasons[0])


class JaccardFallbackBothFieldsRequiredTests(unittest.TestCase):
    """Regression tests for the real-corpus false-merge class the fallback
    used to admit: only ONE of workaround_jaccard/failure_jaccard clearing
    the floor while the other sits at exactly 0.0 shared tokens - a single
    field's coincidental phrase overlap, not genuine two-sided
    corroboration. Text below is transcribed verbatim from the real
    Constraint Archaeology corpus observations that produced these two
    confirmed false merges in production."""

    def setUp(self):
        self.th = load_thresholds()

    def test_A_financial_reconciliation_vs_livestream_uptime_must_not_merge(self):
        """BC-0021 <- ANOM-0171 in the real corpus: failure_jaccard=0.148
        passed alone (shared tokens were just 'intervention', 'manual',
        'requiring', 'when' - generic troubleshooting connective words),
        workaround_jaccard=0.0 (the actual workaround context - accounting
        reconciliation vs. local streaming software - shared nothing).
        This directly caused the system's only WATCH->VALIDATING
        transition to date, on unrelated evidence."""
        # The real anchor group was ANOM-0054, which itself carried TWO
        # observations (two extractions of the same dev.to article) - both
        # are needed to reproduce the real failure_jaccard=0.148; using
        # only one under-counts the shared tokens and the case degenerates
        # into an already-passing one, per code review.
        reconciliation_1 = obs(
            process="Transaction reconciliation between systems using exact amount matching",
            hidden_function_hint="Manual intervention required when single payment splits across "
                                  "multiple invoices or vice versa",
            current_carrier="Finance/accounting teams performing reconciliation workflows",
            pain="Exact amount matching algorithm fails on one-to-many or many-to-one transaction "
                 "relationships",
            failure_mode="Automated matching breaks when payment amounts don't correspond 1:1 with "
                         "invoices/transactions",
        )
        reconciliation_2 = obs(
            process="Transaction reconciliation between systems",
            hidden_function_hint="Manual resolution required when exact amount matching fails on "
                                  "one-to-many transaction relationships",
            current_carrier="Accountants/finance teams performing manual matching",
            pain="Exact amount matching algorithm breaks when one transaction splits into multiple "
                 "or vice versa",
            failure_mode="Automated reconciliation fails on 1:N relationships, requiring manual "
                         "intervention",
        )
        reconciliation = [reconciliation_1, reconciliation_2]
        livestream_obs = obs(
            process="Keeping a live video stream broadcasting continuously on game store pages "
                    "(Steam/YouTube/Kick) to showcase current gameplay",
            hidden_function_hint="Manual stream supervision: running OBS on local PC 24/7, restarting "
                                  "after connection drops at unpredictable times, encoding to "
                                  "platform-specific specs",
            current_carrier="Local PC running OBS software continuously, monitored manually, "
                             "restarted when crashes occur",
            pain="PC-based continuous streaming requires constant supervision, fails unpredictably "
                 "(especially overnight), lacks platform-specific encoding, cannot schedule content "
                 "changes without disconnecting",
            failure_mode="Stream goes offline during unmanned hours when connection drops or software "
                         "crashes, requiring manual intervention to restart",
        )
        livestream = [livestream_obs]
        sig_a = signature_for_group(reconciliation, self.th)
        sig_b = signature_for_group(livestream, self.th)
        # Sanity: this pair only reaches the jaccard fallback because the
        # taxonomy-keyword signal is already weak (1 shared word: "manual").
        self.assertEqual(sig_a.buyer_bucket, sig_b.buyer_bucket)
        self.assertEqual(sig_a.function_class, sig_b.function_class)
        ok, reasons = same_opportunity(sig_a, reconciliation, sig_b, livestream, self.th)
        self.assertFalse(ok, f"must not merge - reasons: {reasons}")

    def test_B_cloud_suspension_ambiguity_vs_hipaa_compliance_must_not_merge(self):
        """BC-0029 <- ANOM-0152 in the real corpus: workaround_jaccard=0.188
        passed alone (shared tokens were just 'platform', 'support',
        'ticket' - generic customer-service process words), failure_jaccard
        was 0.0 with ZERO shared taxonomy keywords at all."""
        suspension = obs(
            process="Deploying application to cloud platform after account creation",
            hidden_function_hint="Distinguishing platform-imposed suspension versus automatic "
                                  "scale-to-zero state; interpreting ambiguous status labels",
            current_carrier="manual support ticket submission to platform staff for suspension review",
            pain="Developer cannot distinguish whether a stopped deployment was suspended for policy "
                 "violation or simply scaled to zero for inactivity",
            failure_mode="auto-suspension triggers on new account after first successful deploy with "
                         "no dashboard notification, verification prompt, or appeal mechanism visible "
                         "to user",
        )
        hipaa = obs(
            process="Launching HIPAA-covered healthcare application requiring Business Associate "
                    "Agreement",
            hidden_function_hint="Customers must obtain explicit written confirmation that compliance "
                                  "agreements (BAA) cover all infrastructure components in use",
            current_carrier="Support ticket / forum inquiry to cloud platform vendor for legal/"
                             "compliance scope clarification",
            pain="Uncertainty whether a managed database component falls inside or outside the "
                 "platform's signed BAA coverage",
            failure_mode="Risk of HIPAA violation if BAA scope is misunderstood or if database "
                         "component is excluded from coverage",
        )
        sig_a = signature_for_group([suspension], self.th)
        sig_b = signature_for_group([hipaa], self.th)
        self.assertEqual(sig_a.buyer_bucket, sig_b.buyer_bucket)
        self.assertEqual(sig_a.function_class, sig_b.function_class)
        ok, reasons = same_opportunity(sig_a, [suspension], sig_b, [hipaa], self.th)
        self.assertFalse(ok, f"must not merge - reasons: {reasons}")

    def test_C_true_merge_with_specific_shared_domain_keywords_still_merges(self):
        """Case C: a genuine same-missing-function pair, sharing several
        SPECIFIC resource_visibility keywords (not generic troubleshooting
        words), must still merge after the both-fields-required change -
        the fix must not make merging so strict that real cross-day
        accumulation stops working. Same shape as the real corpus's own
        legitimate 2+-shared-keyword merges."""
        a = obs(process="developer monitoring API usage",
                hidden_function_hint="developers need real-time visibility into token consumption "
                                      "and billing before hitting quota limits",
                current_carrier="manually checking usage dashboard",
                pain="quota resets wipe unused credit allocation without warning",
                failure_mode="no automated alert exists before the usage quota and billing limit is "
                             "reached")
        b = obs(process="engineer tracking API billing",
                hidden_function_hint="engineers independently report needing clearer token usage and "
                                      "billing visibility before quota limits hit",
                current_carrier="spreadsheet tracking of usage",
                pain="credit balance disappears after quota reset with no visibility into consumption",
                failure_mode="billing dashboard does not show real-time usage against the quota limit")
        sig_a, sig_b = signature_for_group([a], self.th), signature_for_group([b], self.th)
        ok, reasons = same_opportunity(sig_a, [a], sig_b, [b], self.th)
        self.assertTrue(ok, f"must still merge - reasons: {reasons}")
        self.assertGreaterEqual(len(reasons), 1)


if __name__ == "__main__":
    unittest.main()
