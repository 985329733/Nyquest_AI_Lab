"""Export a manifest-selected public tree with a separate publication history."""
from pathlib import Path
from datetime import datetime
import argparse
import hashlib
import json
import re
import shutil
import zipfile
from project_paths import ROOT
from verification_contract import sha256, write_json

ROOT_FILES = ["README.md", "README.en.md", "LICENSE", "THIRD_PARTY.md", "CONTRIBUTING.md", "SECURITY.md",
              "AGENTS.md", "CLAUDE.md", "requirements.txt", "Build.ps1", "Build_Demo.cmd", "New-Project.ps1",
              "Add-Chip.ps1", "Repair-ProjectPaths.ps1", "Backup.ps1", "Setup.ps1", "Package-Project.ps1", "Export-OpenSource.ps1"]
SCRIPTS = ["add_chip.py", "backup_base.py", "build_project.py", "cpu_model.py", "project_info.py", "project_paths.py",
           "toolchain.py", "verification_contract.py", "verify_artifacts.py", "verify_demo.py", "verify_modules.py",
           "package_demo.py", "setup_workspace.py", "materialize_references.py", "export_source.py", "integration_checks.py",
           "test_contract.py", "test_validation.py", "Inspect-Configuration.ps1", "Configure-FromProfile.ps1"]
PUBLIC_IGNORE = """/00_Reference/Tools/
/00_Reference/Downloads/
/00_Reference/include/
/00_Reference/Docs/
/00_Reference/Templates/Official_C/
/00_Reference/Templates/Vendor_Makefile/
/00_Reference/Templates/*_Validated/
/00_Reference/Validation/
/02_Projects/
/toolchain.local.json
/Setup_Verification.json
/OpenSource_Release/
/dist/
**/OBJ/
**/__pycache__/
*.pyc
"""


def selected_files():
    selected = {name: ROOT / name for name in ROOT_FILES}
    for name in SCRIPTS:
        key = "00_Reference/Scripts/" + name
        selected[key] = ROOT / key
    for folder in ("01_Modules", "examples", "docs", ".github"):
        for path in (ROOT / folder).rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts:
                selected[path.relative_to(ROOT).as_posix()] = path
    for name in ("Product_Requirement_Template.md", "Bench_Test_Checklist.md", "Idle_Probe_Behavior.py"):
        key = "00_Reference/Templates/" + name
        selected[key] = ROOT / key
    for key in ("00_Reference/Chip_Specs.md", "00_Reference/Chip_Config/chips.json", "00_Reference/Chip_Config/qualifications.json",
                "00_Reference/Chip_Config/Chip_Evidence/NY8A051F.json"):
        selected[key] = ROOT / key
    return selected


def export(destination):
    destination = Path(destination).resolve()
    if destination.exists(): raise ValueError("Choose a fresh public source destination")
    if destination == ROOT or destination in ROOT.parents:
        raise ValueError("Choose a dedicated public source directory")
    selected = selected_files()
    blocked_extensions = {".bin", ".cb", ".elf", ".map", ".dll", ".exe", ".pdf", ".zip", ".naprj", ".NySln"}
    payload = {}
    for name, source in selected.items():
        if source.is_symlink() or source.suffix in blocked_extensions:
            raise ValueError("Public selection requires authored source files: " + name)
        content = source.read_bytes()
        text = content.decode("utf-8-sig")
        if re.search(r"(?i)(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----)", text):
            raise ValueError("Review credential-like content in " + name)
        payload[name] = content.replace(b"\r\n", b"\n")
    payload[".gitignore"] = PUBLIC_IGNORE.encode("utf-8")
    payload[".gitattributes"] = b"* text=auto eol=lf\n"
    manifest = [{"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()} for name, data in sorted(payload.items())]
    payload["PUBLIC_SOURCE_MANIFEST.json"] = (json.dumps(manifest, indent=2) + "\n").encode("utf-8")
    destination.mkdir(parents=True)
    for name, content in payload.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    (destination / "02_Projects").mkdir(exist_ok=True)
    archive = destination.with_suffix(".zip")
    with zipfile.ZipFile(archive, "x", zipfile.ZIP_DEFLATED) as output:
        for name, content in sorted(payload.items()): output.writestr(name, content)
    with zipfile.ZipFile(archive) as output:
        if output.testzip() is not None: raise ValueError("Public archive CRC must verify")
        for item in manifest:
            if hashlib.sha256(output.read(item["path"])).hexdigest() != item["sha256"]:
                raise ValueError("Public archive file hash must match: " + item["path"])
    report = {"status": "PASS", "source_directory": str(destination), "files": len(payload),
              "archive": str(archive), "archive_sha256": sha256(archive),
              "scope": "Explicit source selection, credential pattern scan, ZIP CRC and file SHA256"}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    export(parser.parse_args().destination)
