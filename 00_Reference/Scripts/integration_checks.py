"""Vendor-backed regression of the complete build decision, in isolated copies."""
from pathlib import Path
from datetime import datetime
import shutil
import subprocess
import sys
from build_project import ROOT, clone_project, build
from verification_contract import read_json, write_json


def main():
    projects = sorted(p for p in (ROOT / "02_Projects").iterdir() if (p / "Makefile").is_file())
    if not projects: raise ValueError("Create a reference project with New-Project.ps1 first")
    source = next((p for p in projects if "NY8A051F" in p.name), projects[0])
    records = []
    for name in ("wdt", "clock", "failed_report", "stale_context", "missing_report", "missing_profile"):
        project = clone_project(source)
        expected = "INCOMPLETE" if name.startswith("missing_") else "FAILED"
        if name in ("wdt", "clock"):
            profile = read_json(project / "Project_Profile.json")
            profile["configuration"]["Wdt" if name == "wdt" else "InstructionClock"] = "DISABLE" if name == "wdt" else "Clock2"
            write_json(project / "Fault_Profile.json", profile)
            cb = next(project.glob("*.cb"))
            cb.unlink()
            subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                            str(ROOT / "00_Reference/Scripts/Configure-FromProfile.ps1"), "-Profile",
                            str(project / "Fault_Profile.json"), "-Target", str(cb)], check=True)
        elif name == "missing_profile":
            (project / "Project_Profile.json").unlink()
        elif name == "missing_report":
            (project / "behavior_tests.py").write_text("print('Scenario runner completed')\n", encoding="ascii")
        else:
            script = """from pathlib import Path
import json
p=Path(__file__).parent
context=json.loads((p/'Build_Context.json').read_text())
profile=json.loads((p/'Project_Profile.json').read_text())
checks=[{'name':n,'passed':True} for n in profile['behavior']['required_checks']]
report={'schema_version':1,'status':'PASS','passed':len(checks),'failed':0,'checks':checks,'context':context}
"""
            if name == "failed_report": script += "report.update(status='FAILED',failed=1)\n"
            else: script += "context['run_id']='previous-build'\n"
            script += "(p/'Behavior_Verification.json').write_text(json.dumps(report))\n"
            (project / "behavior_tests.py").write_text(script, encoding="ascii")
        code, _ = build(project)
        workflow = read_json(project / "Workflow_Verification.json")
        reason = {"wdt":"Configuration Wdt", "clock":"Configuration InstructionClock",
                  "failed_report":"status PASS", "stale_context":"current build context",
                  "missing_report":"write its current report", "missing_profile":"Supply Project_Profile"}[name]
        passed = code == 1 and workflow["Status"] == expected and reason in workflow.get("Reason", "")
        records.append({"case": name, "exit_code": code, "expected": expected, "observed": workflow["Status"],
                        "passed": passed, "reason": workflow.get("Reason"), "project": str(project.relative_to(ROOT))})
    report = {"status": "PASS" if all(r["passed"] for r in records) else "FAILED", "checks": records,
              "scope": "Vendor-backed build rejection checks in isolated projects; bench UNTESTED"}
    target = ROOT / "00_Reference/Validation" / ("Integration_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".json")
    write_json(target, report)
    print("Integration report: " + str(target))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
