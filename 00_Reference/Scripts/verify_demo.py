"""Compatibility runner; provide a project directory explicitly."""
from pathlib import Path
import runpy,sys
if len(sys.argv)!=2:raise SystemExit('Usage: python verify_demo.py PROJECT_DIRECTORY')
p=Path(sys.argv[1]).resolve()/'behavior_tests.py'
if not p.is_file():raise SystemExit('Behavior tests missing; no PASS can be claimed')
runpy.run_path(str(p),run_name='__main__')
