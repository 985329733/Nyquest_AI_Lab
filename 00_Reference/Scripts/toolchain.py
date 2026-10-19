"""Resolve workspace vendor tools and the machine-specific make executable."""
from pathlib import Path
import os
import shutil
from verification_contract import read_json

ROOT = Path(__file__).resolve().parents[2]


def resolve_tools():
    config_path = ROOT / "toolchain.local.json"
    config = read_json(config_path) if config_path.is_file() else {}
    make = os.environ.get("NYQUEST_MAKE") or config.get("make_path") or shutil.which("make.exe") or "C:/Nyquest/NYIDE/bin/toolchain/make.exe"
    sdk = ROOT / "00_Reference/Tools/NYC_NY8/app"
    assembler = ROOT / "00_Reference/Tools/NYASM/app"
    paths = {"make": Path(make), "compiler": sdk / "bin/sdcc.exe", "assembler": assembler / "nyas.exe",
             "linker": assembler / "nylinker.exe", "core": assembler / "Nyquest.Core.dll"}
    missing = [str(p) for p in paths.values() if not p.is_file()]
    if missing:
        raise ValueError("Run Setup.ps1 to supply these toolchain files: " + ", ".join(missing))
    return paths
