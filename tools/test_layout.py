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

check("skills/neckbeard: inventory_hooks.py defines inventory_hooks and hooks_outside_manifest, and inventory.py defines neither",
      {"inventory_hooks", "hooks_outside_manifest"} <= _defs("inventory_hooks.py") and not ({"inventory_hooks", "hooks_outside_manifest"} & _defs("inventory.py")))

check("skills/neckbeard: inventory_parts.py defines mcp_servers and inventory_skills, and inventory.py defines neither",
      {"mcp_servers", "inventory_skills"} <= _defs("inventory_parts.py") and not ({"mcp_servers", "inventory_skills"} & _defs("inventory.py")))

# the read cap: neckbeard's own report reads in full, so no shipped file is over the 50,000 bytes it reads of one file
BOUND = 40_000
_big = {f.name: f.stat().st_size for f in (ROOT / "skills" / "neckbeard").glob("*.py") if f.stat().st_size > BOUND}
check(f"every .py under skills/neckbeard is at most {BOUND:,} bytes (room under the 50,000-byte read cap)" + ("" if not _big else f": {_big!r}"), not _big)
check("skills/neckbeard: inventory_dossier.py defines inventory_target and add_read_status, and inventory.py defines neither",
      {"inventory_target", "add_read_status"} <= _defs("inventory_dossier.py") and not ({"inventory_target", "add_read_status"} & _defs("inventory.py")))
with tempfile.TemporaryDirectory() as _d:
    _out = Path(_d) / "d.json"
    _proj = Path(_d) / "proj"; _proj.mkdir()
    subprocess.run([sys.executable, str(ROOT / "skills" / "neckbeard" / "inventory.py"), str(ROOT), "--project-dir", str(_proj), "--out", str(_out)],
                   capture_output=True, text=True)
    import json
    _notes = []
    try:
        for _sec in (json.loads(_out.read_text())["target"].get("read_status") or {}).values():
            _notes += [n for n in (_sec.get("notes") or []) if isinstance(n, str)] if isinstance(_sec, dict) else []
    except Exception as e:
        _notes = [f"could not read the dossier: {e!r}"]
_capped = [n for n in _notes if "read capped" in n or (n.startswith("skills/") and "could not" in n) or n.startswith("could not read the dossier")]
check("the inventory of this repo's own tree carries no 'read capped' note naming any file, and no unreadable note naming a file under skills/" + ("" if not _capped else f": {_capped!r}"), not _capped)
_rep = (ROOT / "docs" / "neckbeard-report.md").read_text()
check("docs/neckbeard-report.md lists no file as read capped", "read capped" not in _rep)
_tbig = {f.name: f.stat().st_size for f in (ROOT / "tools").glob("*.py") if f.name.startswith("test_") or f.name == "vet_harness.py"}
_tbig = {k: v for k, v in _tbig.items() if v > BOUND}
check(f"every test module and helper under tools/ is at most {BOUND:,} bytes" + ("" if not _tbig else f": {_tbig!r}"), not _tbig)

# find_up stops at HOME: inventory.py's wrapper hands inventory_core the value of inventory.HOME at call time
sys.path.insert(0, str(ROOT / "skills" / "neckbeard"))
import inventory
with tempfile.TemporaryDirectory() as _d:
    _above = Path(_d).resolve()
    (_above / "CLAUDE.md").write_text("rules\n")
    _home = _above / "home"
    (_home / "proj" / "sub").mkdir(parents=True)
    _was, inventory.HOME = inventory.HOME, str(_home)
    try:
        _got = inventory.find_up(str(_home / "proj" / "sub"), "CLAUDE.md")
        (_home / "proj" / "CLAUDE.md").write_text("mine\n")
        _near = inventory.find_up(str(_home / "proj" / "sub"), "CLAUDE.md")
    finally:
        inventory.HOME = _was
check("inventory.find_up stops at HOME (a CLAUDE.md above it is not found) and still finds one below it", _got is None and _near == str(_home / "proj" / "CLAUDE.md"))

# The publish guide clones the tag it documents: its --branch pins must name the manifest version.
import json, re
def _guide_pins(guide, version):
    pins = set(re.findall(r"--branch v(\S+)", guide))
    return bool(pins) and pins == {version}
_ver = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())["version"]
_guide = (ROOT / "docs" / "publish-your-report.md").read_text()
check("docs/publish-your-report.md pins the clone to the manifest version", _guide_pins(_guide, _ver))
check("the guide check fails when the manifest version moves on (seen to fail)", not _guide_pins(_guide, _ver + ".1"))
check("the guide check fails on a guide that pins an older tag (seen to fail)", not _guide_pins(_guide.replace("--branch v" + _ver, "--branch v0.0.1"), _ver))

# The guide tells a reader who vetted someone else's plugin how to invite its author.
check("docs/publish-your-report.md has an \"Invite an author\" section", "\n## Invite an author\n" in _guide)

# The plugin directory takes its listing icon from .claude-plugin/icon.png: a square PNG of 512 to 2048 px, under 2 MB.
def _png_size(data):
    return (int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")) if data[:8] == b"\x89PNG\r\n\x1a\n" else None
_icon = ROOT / ".claude-plugin" / "icon.png"
_bytes = _icon.read_bytes() if _icon.is_file() else b""
check("the listing icon .claude-plugin/icon.png is a 1024 px square PNG under 2 MB", _png_size(_bytes) == (1024, 1024) and len(_bytes) < 2_000_000)
check("the icon check refuses a file that is not a PNG (seen to fail)", _png_size(b"RIFF....WEBPVP8 ") is None)

print(f"test_layout: {'all passed' if not failures else str(len(failures)) + ' failed'}")
sys.exit(1 if failures else 0)
