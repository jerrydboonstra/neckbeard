#!/usr/bin/env python3
"""tools/mutate-selfcheck credits a crash to the case that was running.

    python3 tools/test_mutate_selfcheck.py
"""
import importlib.machinery, importlib.util, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
loader = importlib.machinery.SourceFileLoader("mutate_selfcheck", os.path.join(HERE, "mutate-selfcheck"))
spec = importlib.util.spec_from_loader("mutate_selfcheck", loader)
m = importlib.util.module_from_spec(spec)
loader.exec_module(m)

fails = 0
def chk(name, got, want):
    global fails
    ok = got == want
    fails += not ok
    print(f"  {'ok' if ok else 'FAIL'}  {name}" + ("" if ok else f": got {got!r}, want {want!r}"))

base = subprocess.run([sys.executable, os.path.join(m.SKILL, "selfcheck.py")], capture_output=True, text=True)
order = m.OK_RE.findall(base.stdout)
m.ORDER[:] = order

# pure helper: the case after the last one printed; none printed means the first
chk("crash after two cases", m.crashed_case("  ok   a: x\n  FAIL b: y\n", ["a", "b", "c"]), "c")
chk("crash before any case", m.crashed_case("-- header --\n", ["a", "b"]), "a")
chk("crash in the last case", m.crashed_case("  ok   a: x\n  ok   b: y\n", ["a", "b"]), None)

# end to end: classifiable_items raising crashes the loop-driven first section; the credit goes to
# its first case, not to a later literal chk(...) call
src = open(os.path.join(m.SKILL, "inventory.py")).read()
boom = src + "\n\ndef _boom(*a, **k):\n    raise RuntimeError('mutant')\n\n\nclassifiable_items = _boom\n"
_, code, failed, crash = m.run_one(("crash in a loop case", boom))
chk("a crash inside a loop case is credited to that case", (crash, failed), (True, [order[0]]))

# several modules: a snippet is found in whichever inventory*.py holds it (exactly once across them), the mutant is written
# to that file, and the generic mutants cover every inventory*.py. A scratch skill folder with a stub selfcheck keeps it fast.
import shutil, tempfile
scratch = tempfile.mkdtemp(prefix="msc-")
try:
    def write(name, text):
        with open(os.path.join(scratch, name), "w") as f:
            f.write(text)
    write("inventory.py", "from inventory_core import keep\nTOP = 1\n")
    write("inventory_core.py", "def keep(x):\n    if x:\n        return 'MUTANT-ME'\n    return None\n")
    write("selfcheck.py", "import os, sys\nhere = os.path.dirname(os.path.abspath(__file__))\n"
          "core = open(os.path.join(here, 'inventory_core.py')).read()\n"
          "top = open(os.path.join(here, 'inventory.py')).read()\n"
          "bad = ('BROKEN' in core) or ('GONE' in top)\n"
          "print('  ' + ('FAIL' if 'BROKEN' in core else 'ok  ') + ' guarded case: x')\n"
          "print('  ' + ('FAIL' if 'GONE' in top else 'ok  ') + ' top case: y')\nsys.exit(1 if bad else 0)\n")
    real_skill, m.SKILL = m.SKILL, scratch
    try:
        files = m.apply_snippets(scratch, [("'MUTANT-ME'", "'BROKEN'")])
        chk("a snippet that lives in inventory_core.py is found there and only that file is rewritten", sorted(files), ["inventory_core.py"])
        _, code, failed, crash = m.run_one(("core snippet", files))
        chk("run_one writes the mutant to the file that holds the snippet, so the case fails", (failed, crash), (["guarded case"], False))
        def exits(subs):
            try:
                m.apply_snippets(scratch, subs)
            except SystemExit as e:
                return str(e.code)
            return ""
        chk("a snippet that occurs in no module stops the run, naming it", "NOPE" in exits([("NOPE", "x")]), True)
        write("inventory.py", "from inventory_core import keep\nTOP = 1\nSECOND = 'ALSO-ME'\n")
        two = m.apply_snippets(scratch, [("'MUTANT-ME'", "'BROKEN'"), ("'ALSO-ME'", "'GONE'")])
        chk("two snippets, one in each module (as the NO .claude/ case has): both files come back, each with its own edit",
            (sorted(two), "'BROKEN'" in two.get("inventory_core.py", ""), "'GONE'" in two.get("inventory.py", ""), "'MUTANT-ME'" in two.get("inventory.py", "")), (["inventory.py", "inventory_core.py"], True, True, False))
        _, code2, failed2, crash2 = m.run_one(("two files", two))
        chk("run_one writes both files of a two-module case: the case that reads each file fails", (sorted(failed2), crash2), (["guarded case", "top case"], False))
        write("inventory.py", "from inventory_core import keep\nTOP = 'MUTANT-ME'\n")
        chk("a snippet that occurs once in each of two modules stops the run: it must occur once across them", "2 times" in exits([("'MUTANT-ME'", "'BROKEN'")]), True)
        write("inventory.py", "from inventory_core import keep\nTOP = 1\n")
        descs = [d for d, _ in m.all_mutants(scratch)]
        chk("generic mutants are made for inventory_core.py too, named by file", any(d.startswith("inventory_core.py ") for d in descs), True)
    finally:
        m.SKILL = real_skill
finally:
    shutil.rmtree(scratch, ignore_errors=True)
sys.exit(1 if fails else 0)
