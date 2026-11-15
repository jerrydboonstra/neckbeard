#!/usr/bin/env python3
"""The plugin layout guard and the tools/neckbeard wrapper. Each guard case is seen to fail, not only to pass."""
import os, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUARD = ROOT / "tools" / "check-no-bin"
failures = []


def check(name, ok):
    print(("ok   " if ok else "FAIL ") + name)
    if not ok:
        failures.append(name)


def guard(setup):
    with tempfile.TemporaryDirectory() as d:
        setup(Path(d))
        return subprocess.run([str(GUARD), d], capture_output=True, text=True).returncode


check("guard passes on a tree with no bin/", guard(lambda d: None) == 0)
check("guard fails on an empty bin/", guard(lambda d: (d / "bin").mkdir()) == 1)
check("guard fails on a bin/ holding a script", guard(lambda d: ((d / "bin").mkdir(), (d / "bin" / "x").write_text("#!/bin/sh\n"))) == 1)
check("guard fails on a dangling symlink named bin", guard(lambda d: os.symlink("nowhere", d / "bin")) == 1)
check("the repo itself has no bin/", subprocess.run([str(GUARD)], capture_output=True).returncode == 0)

with tempfile.TemporaryDirectory() as cwd:
    r = subprocess.run([str(ROOT / "tools" / "neckbeard"), "--help"], cwd=cwd, capture_output=True, text=True)
    check("tools/neckbeard runs inventory.py from any directory", r.returncode == 0 and "usage: inventory.py" in r.stdout)

import ast
def _defs(name):
    p = ROOT / "skills" / "neckbeard" / name
    return {n.name for n in ast.parse(p.read_text()).body if isinstance(n, ast.FunctionDef)} if p.is_file() else set()
check("skills/neckbeard: inventory_core.py defines _within and inventory.py does not (the containment guard in one place)",
      "_within" in _defs("inventory_core.py") and "_within" not in _defs("inventory.py"))

print(f"test_layout: {'all passed' if not failures else str(len(failures)) + ' failed'}")
sys.exit(1 if failures else 0)
