"""
AURA AI - Acceptance Test Suite
Verifies all 8 acceptance checks defined in Section 11 of the specification.
"""

import os
import sys
import tempfile
import unittest
from core import (
    init_db,
    analyze_call,
    upsert_contact,
    get_contact_category,
    get_setting,
    set_setting,
    offline_fallback_extractor,
    scan_security_signals,
)

# Standard Test Samples from Section 9
SAMPLE_NORMAL = "Hi, this is Rahul. I'm calling about tonight's study group, can we move it to 8 pm?"
SAMPLE_URGENT = "This is Priya from City Hospital. Your father was admitted this morning, please call back urgently."
SAMPLE_SCAM_BANK = "Hello, this is SBI customer care. Your account will be blocked in ten minutes. Tell me your OTP immediately to verify."
SAMPLE_SCAM_PRIZE = "Congratulations! You have won a lucky draw prize of Rs 50,000. Pay a processing fee and claim at http://bit.ly/claim-now"


class TestAuraAcceptanceChecks(unittest.TestCase):
    def setUp(self):
        """Create an isolated temporary SQLite database for clean test runs."""
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.temp_db_fd)
        init_db(self.temp_db_path)

    def tearDown(self):
        """Clean up temporary test database."""
        if os.path.exists(self.temp_db_path):
            try:
                os.remove(self.temp_db_path)
            except OSError:
                pass

    def test_check_1_scam_bank(self):
        """
        Check 1: Scam bank sample -> risk High (score >= 6),
        signals include Credential request + Urgency + Threat,
        priority Low, action 'Do not engage. Review in Security Centre'.
        """
        result = analyze_call(SAMPLE_SCAM_BANK, db_path=self.temp_db_path)

        self.assertEqual(result["risk"], "High", "Bank scam must be classified as High risk.")
        self.assertGreaterEqual(result["score"], 6, "Bank scam score must be >= 6.")

        signal_names = [s["signal"] for s in result["signals"]]
        self.assertIn("Credential request", signal_names, "Should detect Credential request signal.")
        self.assertIn("Urgency", signal_names, "Should detect Urgency signal.")
        self.assertIn("Threat", signal_names, "Should detect Threat signal.")

        # High risk calls must have priority forced to Low
        self.assertEqual(result["priority"], "Low", "High-risk call priority must be forced to Low.")
        self.assertEqual(
            result["action"],
            "Do not engage. Review in Security Centre",
            "Action for High risk call must be 'Do not engage. Review in Security Centre'.",
        )

    def test_check_2_scam_prize(self):
        """
        Check 2: Scam prize sample -> risk High,
        signals include Reward claim + Suspicious link + Money request.
        """
        result = analyze_call(SAMPLE_SCAM_PRIZE, db_path=self.temp_db_path)

        self.assertEqual(result["risk"], "High", "Prize scam must be classified as High risk.")
        signal_names = [s["signal"] for s in result["signals"]]
        self.assertIn("Reward claim", signal_names, "Should detect Reward claim signal.")
        self.assertIn("Suspicious link", signal_names, "Should detect Suspicious link signal.")
        self.assertIn("Money request", signal_names, "Should detect Money request signal.")

    def test_check_3_normal_trusted_contact(self):
        """
        Check 3: Normal Rahul sample with Rahul saved as trusted ->
        risk Low, action 'Notify immediately (trusted contact)'.
        """
        # Save Rahul as trusted contact in DB
        upsert_contact("Rahul", "trusted", db_path=self.temp_db_path)
        self.assertEqual(get_contact_category("Rahul", db_path=self.temp_db_path), "trusted")

        result = analyze_call(SAMPLE_NORMAL, db_path=self.temp_db_path)

        self.assertEqual(result["risk"], "Low", "Rahul study group call must be Low risk.")
        self.assertEqual(result["category"], "trusted", "Caller category should be trusted.")
        self.assertEqual(
            result["action"],
            "Notify immediately (trusted contact)",
            "Handling action should notify immediately for trusted contact.",
        )

    def test_check_4_urgent_hospital(self):
        """
        Check 4: Urgent hospital sample -> risk Low, priority High,
        action contains 'Notify immediately'.
        """
        result = analyze_call(SAMPLE_URGENT, availability="Busy", db_path=self.temp_db_path)

        self.assertEqual(result["risk"], "Low", "Hospital sample risk must be Low.")
        self.assertEqual(result["priority"], "High", "Hospital sample priority must be High.")
        self.assertIn(
            "Notify immediately",
            result["action"],
            "Handling action must contain 'Notify immediately'.",
        )

    def test_check_5_offline_fallback(self):
        """
        Check 5: With no API key set, all four samples still work
        and show engine 'offline-fallback'.
        """
        # Save previous key if present and temporarily unset
        old_key = os.environ.pop("ANTHROPIC_API_KEY", None)
        try:
            samples = [
                SAMPLE_NORMAL,
                SAMPLE_URGENT,
                SAMPLE_SCAM_BANK,
                SAMPLE_SCAM_PRIZE,
            ]
            for sample in samples:
                res = analyze_call(sample, db_path=self.temp_db_path)
                self.assertEqual(
                    res["engine"],
                    "offline-fallback",
                    f"Engine must be 'offline-fallback' for sample: {sample[:30]}",
                )
                self.assertTrue(res["message"], "Summary message must not be empty.")
                self.assertIn(res["risk"], ["Low", "Medium", "High"])
        finally:
            if old_key is not None:
                os.environ["ANTHROPIC_API_KEY"] = old_key

    def test_check_6_status_persistence(self):
        """
        Check 6: Changing status in the sidebar persists after refreshing the page.
        """
        set_setting("status", "Do Not Disturb", db_path=self.temp_db_path)
        self.assertEqual(get_setting("status", db_path=self.temp_db_path), "Do Not Disturb")

        set_setting("status", "Available", db_path=self.temp_db_path)
        self.assertEqual(get_setting("status", db_path=self.temp_db_path), "Available")

        set_setting("status", "Busy", db_path=self.temp_db_path)
        self.assertEqual(get_setting("status", db_path=self.temp_db_path), "Busy")

    def test_check_7_security_centre_blocking(self):
        """
        Check 7: Blocking from the Security Centre only happens after clicking
        the approve button, and a later call from that caller shows
        'Rejected: caller is on your blocked list'.
        """
        caller_name = "SuspectCaller99"

        # Initially, caller is unknown (not blocked)
        initial_cat = get_contact_category(caller_name, db_path=self.temp_db_path)
        self.assertEqual(initial_cat, "unknown", "Caller should start as unknown.")

        # Simulate user explicitly approving block action
        upsert_contact(caller_name, "blocked", db_path=self.temp_db_path)
        updated_cat = get_contact_category(caller_name, db_path=self.temp_db_path)
        self.assertEqual(updated_cat, "blocked", "Caller should now be marked blocked.")

        # Later call from that caller
        call_res = analyze_call(
            "Hello, please transfer the money to our account right now.",
            caller_id=caller_name,
            db_path=self.temp_db_path,
        )
        self.assertEqual(
            call_res["action"],
            "Rejected: caller is on your blocked list",
            "Subsequent calls from blocked caller must be rejected.",
        )

    def test_check_8_empty_input_handling(self):
        """
        Check 8: Empty input never causes an unhandled error or crash.
        """
        # Passing empty or whitespace string to analyze_call raises handled ValueError
        for empty_text in ["", "   ", "\t\n  \r\n"]:
            with self.assertRaises(ValueError):
                analyze_call(empty_text, db_path=self.temp_db_path)

        # Fallback extractor handles empty gracefully without crashing
        res = offline_fallback_extractor("", availability="Busy")
        self.assertEqual(res["caller"], "Unknown")
        self.assertEqual(res["engine"], "offline-fallback")


if __name__ == "__main__":
    unittest.main(verbosity=2)
