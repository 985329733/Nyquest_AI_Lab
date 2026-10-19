"""Build qualified reference templates from local vendor projects and public recipes."""
from pathlib import Path
from datetime import datetime
import argparse
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from project_paths import ROOT, repair
from build_project import build
from verification_contract import read_json, write_json, sha256


def materialize(recipe):
    description = read_json(recipe / "Recipe.json")
    chip, stem = description["chip"], description["output"]
    destination = ROOT / "00_Reference/Templates" / (chip + "_Validated")
    if destination.exists():
        raise ValueError("Reference template already present: " + str(destination))
    official = ROOT / "00_Reference/Templates/Official_C" / description["vendor_project"]
    if not official.is_file():
        raise ValueError("Import the official project: " + str(official))
    work = ROOT / "00_Reference/Validation/Reference_Setup" / (chip + "_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
    shutil.copytree(official.parent, work)
    shutil.copytree(official.parent, work / "Vendor_Original")
    old = work / official.name
    tree = ET.parse(old)
    group = tree.getroot().find("PropertyGroup")
    for key, value in {"AssemblyName": stem, "RootNamespace": stem, "InitializeBss": "True",
                       "Bank0Only": "True", "ReservedRam": "8", "ReservedInterruptRam": "2"}.items():
        node = group.find(key)
        if node is None: node = ET.SubElement(group, key)
        node.text = value
    for node in tree.getroot().iter():
        name = node.get("Include", "")
        if name.lower().endswith(".cb"):
            node.set("Include", ("Config Block: " if name.startswith("Config Block:") else "") + stem + ".cb")
    old.unlink()
    tree.write(work / (stem + ".naprj"), encoding="utf-8", xml_declaration=True)
    solution = official.parent.parent / (official.stem + ".NySln")
    content = solution.read_text(encoding="utf-8-sig")
    content = content.replace(official.stem + "\\" + official.name, stem + ".naprj").replace(official.stem, stem)
    (work / (stem + ".NySln")).write_text(content, encoding="utf-8-sig")
    for source in recipe.rglob("*"):
        if source.is_file() and source.name != "Recipe.json":
            target = work / source.relative_to(recipe)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    for source in work.glob("*.cb"): source.unlink()
    subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                    str(ROOT / "00_Reference/Scripts/Configure-FromProfile.ps1"), "-Profile",
                    str(work / "Project_Profile.json"), "-Target", str(work / (stem + ".cb"))], check=True)
    vendor = (ROOT / "00_Reference/Templates/Vendor_Makefile/makefile_ny8C.template").read_text()
    values = {"ICBody": chip, "ClientName": "AI_Base", "ConfigBlockSp": stem + ".cb", "HostTool": "NYIDE",
              "CFiles": "main.c", "ProjectName": stem, "ProjectNameDealWithSpace": stem,
              "NYC_NY8_Path": "$(BASE_ROOT)/00_Reference/Tools/NYC_NY8/app", "LinkLib": description["model"],
              "InitBss": "1", "MapFlag": "--mapfile", "ListFlag": "--disasm", "DebugFlag": "-g",
              "DebugFlag_C": "--debug", "CInit": "--cinit", "ProgramChecksum": "--programchecksum",
              "IncludePath": '-I"$(BASE_ROOT)/00_Reference/include"', "ReservedRamFlag": "--stack-size 8",
              "ReservedInterruptRamFlag": "--backup-stk 2", "CodeOptimizationFlag": "--opt-code-size", "CultureString": "--lang en-us"}
    keys = set(re.findall(r"%%(\w+)%%", vendor))
    optional = {"AsmFiles", "AsmIncludePath", "AsmListFlag", "BackupForInterrupt", "BankselOptFlag",
                "ClearRamFlag", "CodeChecksum", "DisableWarning", "EEPROMLibrary", "EEPROMTimeout",
                "GenFpgaFile", "LibraryFiles", "LinkerArguments", "SpacePathRule", "TempFolder", "VPath"}
    if keys - values.keys() - optional:
        raise ValueError("Verify vendor Makefile placeholders: " + str(keys - values.keys() - optional))
    # The original template defines optional empty fields alongside explicit build values.
    (work / "Makefile").write_text(re.sub(r"%%(\w+)%%", lambda m: values.get(m[1], ""), vendor), encoding="ascii")
    repair(work)
    code, _ = build(work)
    if code: raise ValueError("Reference qualification requires all build stages to pass")
    report = {"status": "PASS", "chip": chip, "firmware_sha256": sha256(work / (stem + ".bin")),
              "scope": "Configuration, real compiler and reference software scenarios; bench UNTESTED"}
    write_json(work / "Qualification_Verification.json", report)
    shutil.copytree(work, destination, ignore=shutil.ignore_patterns("OBJ", "Vendor_Original", "__pycache__"))
    repair(destination)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recipes", type=Path, default=ROOT / "examples")
    args = parser.parse_args()
    for recipe in sorted(args.recipes.iterdir()):
        if (recipe / "Recipe.json").is_file():
            print(materialize(recipe))
