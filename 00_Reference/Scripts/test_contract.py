"""Portable unit coverage for policy, provenance, and report decisions."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from verification_contract import (IncompleteVerification, validate_behavior, validate_configuration,
                                   load_profile, write_json)


class Contracts(unittest.TestCase):
    def setUp(self):
        self.context = {"run_id": "current", "binary_sha256": "abc"}
        self.report = {"schema_version": 1, "status": "PASS", "context": self.context,
                       "checks": [{"name": "boot", "passed": True}], "passed": 1, "failed": 0}
        config = {"Id": "NY8B062D", "HighOsc": "IRC", "LowOsc": "IRC", "IrcFreq": "FREQ_4",
                  "InstructionClock": "Clock4", "Wdt": "ENABLE", "WdtEvent": "Reset",
                  "WdtTimeBase": "Ms250", "LvrSetting": "RegisterControl", "LvrVoltage": "V24",
                  "PowerOnClock": "High", "ReadIoSource": "FromRegister", "Pins": []}
        self.profile = {"schema_version": 1, "chip": "NY8B062D", "configuration": config,
                        "clock": {"oscillator_hz": 4000000, "instruction_divider": 4},
                        "timer": {"reload": 624, "prescaler": 16},
                        "behavior": {"required_checks": ["boot"], "tick_period_us": 10000}}
        self.actual = dict(config, cb_sha256="cb")

    def test_successful_report(self):
        self.assertEqual(validate_behavior(self.report, self.context, ["boot"]), 1)

    def test_failed_status(self):
        self.report["status"] = "FAILED"
        with self.assertRaises(ValueError): validate_behavior(self.report, self.context, ["boot"])

    def test_positive_passed_count_with_failures(self):
        self.report["failed"] = 1
        with self.assertRaises(ValueError): validate_behavior(self.report, self.context, ["boot"])

    def test_failed_check(self):
        self.report["checks"][0]["passed"] = False
        with self.assertRaises(ValueError): validate_behavior(self.report, self.context, ["boot"])

    def test_report_counts(self):
        for value in (2, True, "1"):
            self.report["passed"] = value
            with self.assertRaises(ValueError): validate_behavior(self.report, self.context, ["boot"])

    def test_missing_required_check(self):
        with self.assertRaises(ValueError): validate_behavior(self.report, self.context, ["boot", "sleep"])

    def test_duplicate_checks(self):
        self.report["checks"] *= 2
        self.report["passed"] = 2
        with self.assertRaises(ValueError): validate_behavior(self.report, self.context, ["boot"])

    def test_stale_build_context(self):
        with self.assertRaises(ValueError): validate_behavior(self.report, {"run_id": "new"}, ["boot"])

    def test_empty_check_report(self):
        self.report["checks"] = []
        with self.assertRaises(IncompleteVerification): validate_behavior(self.report, self.context, ["boot"])

    def test_verified_clock(self):
        self.assertEqual(validate_configuration(self.profile, self.actual, "cb")["instruction_hz"], 1000000)

    def test_changed_configuration(self):
        for key, value in [("Wdt", "DISABLE"), ("InstructionClock", "Clock2"), ("LvrVoltage", "V16"), ("WdtTimeBase", "Ms15")]:
            actual = dict(self.actual, **{key: value})
            with self.assertRaises(ValueError): validate_configuration(self.profile, actual, "cb")

    def test_clock_profile_and_timer_agree(self):
        profile = deepcopy(self.profile)
        profile["configuration"]["InstructionClock"] = "Clock2"
        profile["clock"]["instruction_divider"] = 2
        actual = dict(self.actual, InstructionClock="Clock2")
        with self.assertRaises(ValueError): validate_configuration(profile, actual, "cb")

    def test_configuration_hash_binding(self):
        with self.assertRaises(ValueError): validate_configuration(self.profile, self.actual, "changed")

    def test_missing_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(IncompleteVerification): load_profile(directory)

    def test_profile_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            write_json(Path(directory) / "Project_Profile.json", self.profile)
            self.assertEqual(load_profile(directory)["chip"], "NY8B062D")


if __name__ == "__main__":
    unittest.main(verbosity=2)
