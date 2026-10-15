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
sys.exit(1 if fails else 0)
