#!/usr/bin/env python3
"""tools/vet-stability on reports built in the shape tools/vet writes.

    python3 tools/test_vet_stability.py
"""
import os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "vet-stability")
fails = 0


def report(verdict, conflicts, covered=2):
    rows = "\n".join(f'| {i + 1} | "{say}" (`{src}`) | "a rule" | `{held}` | 🟥 |' for i, (src, say, held) in enumerate(conflicts))
    return f"""# 🔍 x 1.0 · vetted against the sample reader

> ## 🟧 {verdict} · reason
> Summary.

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **{len(conflicts)}** | 🟥 |
| 🔁 | **already covered** | **{covered}** | ⬜ |
| 🆕 | **new, standing rule** | **1** | 🟩 |
| 🆕 | **new, on-demand skill** | **3** | 🟩 |
| 🗑️ | **dropped** (persona, extras, no value) | **0** | |

## ⛔ Conflicts: {len(conflicts)}

| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
{rows}

## 🟩 Keep: 4
"""


def run(*texts):
    d = tempfile.mkdtemp()
    paths = []
    for i, t in enumerate(texts):
        p = os.path.join(d, f"r{i}.md")
        open(p, "w").write(t)
        paths.append(p)
    r = subprocess.run([sys.executable, TOOL, *paths], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def chk(name, ok, detail=""):
    global fails
    fails += not ok
    print(f"  {'ok' if ok else 'FAIL'}  {name}" + ("" if ok else f": {detail}"))


A = ("skills/a/SKILL.md", "Always name the model", "rules/engineering.md rule 6")
B = ("skills/b/SKILL.md", "Word each commit", "rules/engineering.md rule 7")
A2 = ("skills/a/SKILL.md", "Specify a model on every dispatch", "rules/engineering.md rule 6")

rc, out = run(report("INSTALL", [A, B]), report("INSTALL", [A, B]))
chk("two identical reports are stable", rc == 0 and "stable" in out and "found in 2 of 2" in out, out)
rc, out = run(report("INSTALL", [A, B]), report("COPY RULES, SKIP PLUGIN", [A, B]))
chk("a different verdict is not stable", rc == 1 and "INSTALL in 1 of 2" in out, out)
rc, out = run(report("INSTALL", [A, B]), report("INSTALL", [A]), report("INSTALL", [A, B]))
chk("a conflict found in 2 of 3 is reported as such, and the set is not stable",
    rc == 1 and "found in 2 of 3" in out and "found in 3 of 3" in out, out)
rc, out = run(report("INSTALL", [A]), report("INSTALL", [A2]))
chk("the same finding worded differently counts once", rc == 0 and "found in 2 of 2" in out and out.count("conflict found") == 1, out)
rc, out = run(report("INSTALL", []), report("INSTALL", []))
chk("no conflicts anywhere is stable", rc == 0 and "no conflicts" in out, out)
rc, out = run("# no banner here\n", report("INSTALL", [A]))
chk("a report with no verdict banner is refused", rc == 2 and "no verdict banner" in out, out)
rc, out = run(report("INSTALL", [A]))
chk("one report is a usage error", rc == 2, out)
sys.exit(1 if fails else 0)
