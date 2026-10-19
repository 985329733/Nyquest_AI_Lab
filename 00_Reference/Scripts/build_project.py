"""Build transaction with explicit inputs and current verification evidence."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import uuid
from project_paths import ROOT, validate, repair
from project_info import info, assignments
from toolchain import resolve_tools
from verification_contract import (IncompleteVerification, input_hashes, load_profile, read_json,
                                   sha256, validate_behavior, validate_configuration, write_json)
from verify_artifacts import verify


def clone_project(source):
    root = ROOT / "00_Reference/Validation/Build_Runs"
    root.mkdir(parents=True, exist_ok=True)
    destination = root / (source.name + "_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns("OBJ", "Delivery", "Vendor_Original", "__pycache__"))
    repair(destination)
    return destination


def run(command, project, log, env=None):
    with subprocess.Popen([str(c) for c in command], cwd=project, env=env, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace") as process:
        for line in process.stdout:
            print(line, end="", flush=True)
            log.write(line)
            log.flush()
        code = process.wait()
    if code:
        raise ValueError(f"Command requires exit code zero; observed {code}: {command[0]}")


def build(project, isolated=False):
    source = Path(project)
    source = (ROOT / source).resolve() if not source.is_absolute() else source.resolve()
    if ROOT not in source.parents or not (source / "Makefile").is_file():
        raise ValueError("Select a generated project inside the workspace")
    if "Official_C" in source.relative_to(ROOT).parts:
        raise ValueError("Build a generated project copied from the vendor original")
    project = clone_project(source) if isolated else source
    print("Build directory: " + str(project), flush=True)
    workflow_path = project / "Workflow_Verification.json"
    workflow = {"schema_version": 1, "Status": "RUNNING", "run_id": str(uuid.uuid4()),
                "Scope": "Configuration, compiler, static resources and project software scenarios",
                "bench": "UNTESTED", "vendor_simulator": "NOT_RUN"}
    write_json(workflow_path, workflow)
    try:
        validate(project)
        profile = load_profile(project)
        meta = info(project)
        if profile["chip"] != meta["chip"]:
            raise ValueError("Project profile chip must match the vendor project")
        tools = resolve_tools()
        stem = meta["output"]
        cb = (project / assignments(project / "Makefile")["CB_FILE"].strip()).resolve()
        if cb.parent != project or not cb.is_file():
            raise ValueError("CB_FILE must identify a project configuration file")
        for name in [stem + ext for ext in (".bin", ".elf", ".map", ".link.lst")] + [
                "Build_Verification.json", "Behavior_Verification.json", "Build_Context.json", "Configuration_Readback.json"]:
            (project / name).unlink(missing_ok=True)
        (project / "OBJ").mkdir(exist_ok=True)
        inputs = input_hashes(project)
        with (project / "build.log").open("w", encoding="utf-8") as log:
            run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                 ROOT / "00_Reference/Scripts/Inspect-Configuration.ps1", "-ProjectDir", project,
                 "-Chip", meta["chip"], "-ConfigBlock", cb], project, log)
            actual = read_json(project / "Configuration_Readback.json")
            clock = validate_configuration(profile, actual, sha256(cb))
            env = dict(os.environ, PYTHONIOENCODING="utf-8")
            env["PATH"] = str(tools["compiler"].parent) + os.pathsep + str(tools["assembler"].parent) + os.pathsep + env["PATH"]
            run([tools["make"], "-B", "all", "SHOW_CMD=1", "BASE_ROOT=" + ROOT.as_posix()], project, log, env)
            log.flush()
            if re.search(r"(?im)(^\s*msg\s*\{|\b(?:warning|error)\s+\d+\s*:)", (project / "build.log").read_text(encoding="utf-8")):
                raise ValueError("Compiler diagnostics require resolution")
            for ext in (".bin", ".elf", ".map", ".link.lst"):
                path = project / (stem + ext)
                if not path.is_file() or path.stat().st_size == 0:
                    raise ValueError("Compiler must produce a current " + ext + " artifact")
            artifact = verify(project)
            context = {"run_id": workflow["run_id"], "binary": artifact["binary"],
                       "binary_sha256": artifact["sha256"], "configuration_sha256": sha256(project / "Configuration_Readback.json"),
                       "profile_sha256": sha256(project / "Project_Profile.json"), "inputs": inputs,
                       "instruction_hz": clock["instruction_hz"]}
            write_json(project / "Build_Context.json", context)
            if not (project / "behavior_tests.py").is_file():
                raise IncompleteVerification("Supply project behavior_tests.py")
            run([sys.executable, project / "behavior_tests.py"], project, log, env)
            if not (project / "Behavior_Verification.json").is_file():
                raise IncompleteVerification("Behavior runner must write its current report")
            count = validate_behavior(read_json(project / "Behavior_Verification.json"), context, profile["behavior"]["required_checks"])
        if inputs != input_hashes(project) or context["binary_sha256"] != sha256(project / artifact["binary"]) or context["configuration_sha256"] != sha256(project / "Configuration_Readback.json"):
            raise ValueError("Verified inputs and outputs must remain stable through all build stages")
        workflow.update(Status="PASS", context=context, behavior_checks=count, clock=clock,
                        tool_sha256={name: sha256(path) for name, path in tools.items()},
                        completed_utc=datetime.now(timezone.utc).isoformat())
    except Exception as error:
        workflow.update(Status="INCOMPLETE" if isinstance(error, IncompleteVerification) else "FAILED", Reason=str(error))
        write_json(workflow_path, workflow)
        print(json.dumps(workflow), file=sys.stderr)
        return 1, project
    write_json(workflow_path, workflow)
    print(f"PASS: {count} project software checks; bench status UNTESTED", flush=True)
    return 0, project


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project")
    parser.add_argument("--isolated", action="store_true")
    args = parser.parse_args()
    if not args.project:
        choices = sorted(p for p in (ROOT / "02_Projects").iterdir() if (p / "Makefile").is_file())
        for number, path in enumerate(choices, 1):
            print(f"{number}. {path.name}")
        selected = int(input("Select project number: "))
        if not 1 <= selected <= len(choices):
            raise ValueError("Select a listed project number")
        args.project = choices[selected - 1]
    return build(args.project, args.isolated)[0]


if __name__ == "__main__":
    sys.exit(main())
