"""Explicit configuration policy and build-bound software evidence."""
from pathlib import Path
from fractions import Fraction
import hashlib
import json
import os


class IncompleteVerification(ValueError):
    """Required verification inputs remain to be supplied."""


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def input_hashes(project):
    project = Path(project)
    names = {"Makefile", "Project_Profile.json", "behavior_tests.py"}
    extensions = {".c", ".h", ".cb", ".naprj", ".NySln"}
    result = {}
    for path in sorted(project.rglob("*")):
        relative = path.relative_to(project)
        if any(part in {"OBJ", "Delivery", "Vendor_Original", "__pycache__"} for part in relative.parts):
            continue
        if path.is_symlink():
            raise ValueError("Project inputs require regular local files: " + str(relative))
        if path.is_file() and (path.name in names or path.suffix in extensions):
            result[relative.as_posix()] = sha256(path)
    return result


def load_profile(project):
    path = Path(project) / "Project_Profile.json"
    if not path.is_file():
        raise IncompleteVerification("Supply Project_Profile.json with configuration and required scenarios")
    profile = read_json(path)
    if profile.get("schema_version") != 1:
        raise ValueError("Project profile requires schema_version 1")
    config = profile.get("configuration", {})
    required = {"Id", "HighOsc", "LowOsc", "IrcFreq", "InstructionClock", "Wdt", "WdtEvent",
                "WdtTimeBase", "LvrSetting", "LvrVoltage", "PowerOnClock", "ReadIoSource", "Pins"}
    if set(config) != required or config.get("Id") != profile.get("chip"):
        raise ValueError("Project profile requires an exact chip configuration and pin table")
    if config["Wdt"] != "ENABLE":
        raise ValueError("Project policy requires WDT ENABLE")
    checks = profile.get("behavior", {}).get("required_checks")
    if not isinstance(checks, list) or not checks or any(not isinstance(c, str) or not c for c in checks):
        raise IncompleteVerification("Supply named required behavior scenarios")
    if len(checks) != len(set(checks)):
        raise ValueError("Required scenario names must be unique")
    return profile


def validate_configuration(profile, actual, cb_hash):
    if actual.get("cb_sha256") != cb_hash:
        raise ValueError("Configuration readback must identify the current cb SHA256")
    for key, value in profile["configuration"].items():
        observed = actual.get(key)
        if key == "Pins":
            canonical = lambda rows: sorted((r["Port"], r["Bit"], r["Type"]) for r in rows)
            if canonical(observed or []) != canonical(value):
                raise ValueError("Configuration Pins must match the project profile")
        elif observed != value:
            raise ValueError(f"Configuration {key}: expected {value}, observed {observed}")
    if actual["Wdt"] != "ENABLE":
        raise ValueError("Configuration requires WDT ENABLE")
    frequency = {"FREQ_4": 4_000_000}.get(actual["IrcFreq"])
    divider = {"Clock2": 2, "Clock4": 4}.get(actual["InstructionClock"])
    if actual["HighOsc"] != "IRC" or actual["PowerOnClock"] != "High" or frequency is None or divider is None:
        raise ValueError("Supply a verified clock backend for this oscillator configuration")
    if profile.get("clock") != {"oscillator_hz": frequency, "instruction_divider": divider}:
        raise ValueError("Clock calculation must match the decoded oscillator and instruction divider")
    instruction_hz = frequency // divider
    timer = profile.get("timer")
    if timer:
        period = Fraction((timer["reload"] + 1) * timer["prescaler"] * 1_000_000, instruction_hz)
        if period != profile["behavior"].get("tick_period_us"):
            raise ValueError("Behavior tick period must match the decoded clock and timer calculation")
    return {"instruction_hz": instruction_hz, "instruction_period_us": str(Fraction(1_000_000, instruction_hz))}


def validate_behavior(report, context, required_checks):
    if report.get("schema_version") != 1 or report.get("status") != "PASS":
        raise ValueError("Behavior report requires schema_version 1 and status PASS")
    if report.get("context") != context:
        raise ValueError("Behavior evidence must bind the current build context")
    checks = report.get("checks")
    if not isinstance(checks, list) or not checks:
        raise IncompleteVerification("Behavior evidence requires named check results")
    names = []
    for check in checks:
        if not isinstance(check, dict) or not isinstance(check.get("name"), str) or check.get("passed") is not True:
            raise ValueError("Each behavior scenario must carry a successful boolean result")
        names.append(check["name"])
    if len(names) != len(set(names)) or not set(required_checks).issubset(names):
        raise ValueError("Behavior evidence must cover each unique required scenario")
    if type(report.get("passed")) is not int or report["passed"] != len(checks):
        raise ValueError("Behavior passed count must equal the scenario count")
    if type(report.get("failed")) is not int or report["failed"] != 0:
        raise ValueError("Behavior failed count must equal zero")
    return len(checks)


def load_build_context(project):
    project = Path(project)
    context = read_json(project / "Build_Context.json")
    if context["inputs"] != input_hashes(project):
        raise ValueError("Build context requires the current project inputs")
    if context["binary_sha256"] != sha256(project / context["binary"]):
        raise ValueError("Build context requires the current firmware SHA256")
    if context["configuration_sha256"] != sha256(project / "Configuration_Readback.json"):
        raise ValueError("Build context requires the current configuration readback")
    return context, read_json(project / "Configuration_Readback.json")


class BehaviorSuite:
    """Write an explicit result on success and on the first failed scenario."""
    def __init__(self, project, method):
        self.project = Path(project)
        self.context, self.configuration = load_build_context(project)
        self.method = method
        self.checks = []

    def check(self, name, condition):
        passed = bool(condition)
        self.checks.append({"name": name, "passed": passed})
        if not passed:
            self.finish()
            raise SystemExit("Behavior scenario requires attention: " + name)

    def finish(self, **details):
        failed = sum(c["passed"] is False for c in self.checks)
        report = {"schema_version": 1, "status": "FAILED" if failed else "PASS", "method": self.method,
                  "context": self.context, "checks": self.checks, "passed": len(self.checks) - failed,
                  "failed": failed, **details}
        write_json(self.project / "Behavior_Verification.json", report)
        print(json.dumps({"status": report["status"], "passed": report["passed"], "failed": failed}))
        return report
