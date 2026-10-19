"""Import user-supplied vendor dependencies and qualify public reference recipes."""
from pathlib import Path
import argparse
import shutil
import sys
from project_paths import ROOT
from verification_contract import read_json, write_json, sha256


def copy_dependency(source, destination):
    source, destination = source.resolve(), destination.resolve()
    if source == destination: return
    if destination.exists():
        for path in source.rglob('*'):
            if path.is_file():
                other=destination/path.relative_to(source)
                if not other.is_file() or sha256(other)!=sha256(path):
                    raise ValueError("Dependency bytes require a fresh import directory: " + str(other))
        return
    shutil.copytree(source, destination)


def setup(args):
    (ROOT / "02_Projects").mkdir(parents=True, exist_ok=True)
    required = [(args.sdk / "bin/sdcc.exe"), (args.assembler / "nylinker.exe"),
                (args.nyide / "bin/toolchain/make.exe"),
                (args.nyide / "data/templates/project/makefile/makefile_ny8C.template")]
    for path in required:
        if not path.is_file(): raise ValueError("Supply vendor installation file: " + str(path))
    qualifications = read_json(ROOT / "00_Reference/Chip_Config/qualifications.json")
    for record in qualifications.values():
        source = args.datasheets / Path(record["datasheet"]).name
        if not source.is_file() or sha256(source) != record["datasheet_sha256"]:
            raise ValueError("Supply the matching datasheet SHA256: " + str(source))
    copy_dependency(args.sdk, ROOT / "00_Reference/Tools/NYC_NY8/app")
    copy_dependency(args.assembler, ROOT / "00_Reference/Tools/NYASM/app")
    copy_dependency(args.sdk / "include", ROOT / "00_Reference/include")
    for chip in qualifications:
        family = "NY8A" if chip.startswith("NY8A") else "NY8B"
        copy_dependency(args.examples / family / chip / "Template_C", ROOT / "00_Reference/Templates/Official_C" / family / chip)
    target = ROOT / "00_Reference/Templates/Vendor_Makefile/makefile_ny8C.template"
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists(): shutil.copy2(required[-1], target)
    for record in qualifications.values():
        target = ROOT / record["datasheet"]
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists(): shutil.copy2(args.datasheets / target.name, target)
        if sha256(target) != record["datasheet_sha256"]: raise ValueError("Workspace datasheet hash must match the qualification")
    write_json(ROOT / "toolchain.local.json", {"make_path": str(required[2].resolve())})
    from materialize_references import materialize
    results = []
    for recipe in sorted((ROOT / "examples").iterdir()):
        if (recipe / "Recipe.json").is_file(): results.append(materialize(recipe))
    write_json(ROOT / "Setup_Verification.json", {"status": "PASS", "references": results, "bench": "UNTESTED"})
    print("Setup complete: qualified reference templates are ready")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("sdk", "assembler", "nyide", "examples", "datasheets"):
        parser.add_argument("--" + name, type=Path, required=True)
    setup(parser.parse_args())
