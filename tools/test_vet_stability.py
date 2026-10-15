#!/usr/bin/env python3
"""tools/vet-stability on reports built in the shape tools/vet writes.

    python3 tools/test_vet_stability.py
"""
import os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "vet-stability")
fails = 0


def report(verdict, conflicts, covered=2):
    rows = "\n".join(f'| {i + 1} | "{say}"' + (f" (`{src}`)" if src else "") + f' | "a rule" | {held} | 🟥 |' for i, (src, say, held) in enumerate(conflicts))
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


A = ("skills/a/SKILL.md", "Always name the model", "`rules/engineering.md` rule 6")
B = ("skills/b/SKILL.md", "Word each commit", "`rules/engineering.md` rule 7")
A2 = ("skills/a/SKILL.md", "Specify a model on every dispatch", "`rules/engineering.md` rule 6")

rc, out = run(report("INSTALL", [A, B]), report("INSTALL", [A, B]))
chk("two identical reports are stable", rc == 0 and "stable" in out and "found in 2 of 2" in out, out)
rc, out = run(report("INSTALL", [A, B]), report("COPY RULES, SKIP PLUGIN", [A, B]))
chk("a different verdict is not stable", rc == 1 and "INSTALL in 1 of 2" in out, out)
rc, out = run(report("INSTALL", [A, B]), report("INSTALL", [A]), report("INSTALL", [A, B]))
chk("a conflict found in 2 of 3 is reported as such, and the set is not stable",
    rc == 1 and "found in 2 of 3" in out and "found in 3 of 3" in out, out)
rc, out = run(report("INSTALL", [A]), report("INSTALL", [A2]))
chk("the same finding worded differently counts once", rc == 0 and "found in 2 of 2" in out and out.count("conflict found") == 1, out)
# the shape of examples/ponytail.md: no path in "it says"; the judge rewords the quote and changes the
# punctuation of "held in"; this is one finding per row, twice, so it must read as stable
P1 = (None, "skip it, say so in one line", "`examples/reader/rules/engineering.md` rule 4")
P2 = (None, "Never stall on an answer you can default", "`examples/reader/rules/safety.md` rule 5")
P1b = (None, "Do not skip it; say so once", "`examples/reader/rules/engineering.md`, rule 4")
P2b = (None, "Do not stall on an answer that has a default", "`examples/reader/rules/safety.md`  rule 5.")
rc, out = run(report("COPY RULES", [P1, P2]), report("COPY RULES", [P1b, P2b]))
chk("reworded findings with no path in \"it says\" and changed punctuation in \"held in\" are the same", rc == 0 and out.count("conflict found in 2 of 2") == 2 and "found in 1 of 2" not in out, out)
rc, out = run(report("COPY RULES", [P1, P2]), report("COPY RULES", [P1b]))
chk("a finding present in one report and not the other is still caught", rc == 1 and "found in 1 of 2" in out, out)
S1 = ("skills/a/SKILL.md", "x", "`rules/e.md` rule 6")
S2 = ("skills/b/SKILL.md", "y", "`rules/e.md` rule 6")
rc, out = run(report("INSTALL", [S1, S2]), report("INSTALL", [S1, S2]))
chk("two skills against one rule stay two findings", rc == 0 and out.count("conflict found in 2 of 2") == 2, out)
rc, out = run(report("INSTALL", [S1, S1]), report("INSTALL", [S1, S1]))
chk("rows that share source and rule are counted once, and the output says so", rc == 0 and "counted once" in out, out)
rc, out = run(report("INSTALL", []), report("INSTALL", []))
chk("no conflicts anywhere is stable", rc == 0 and "no conflicts" in out, out)
rc, out = run("# no banner here\n", report("INSTALL", [A]))
chk("a report with no verdict banner is refused", rc == 2 and "no verdict banner" in out, out)
rc, out = run(report("INSTALL", [A]))
chk("one report is a usage error", rc == 2, out)

# vet-repeat, with a stub for tools/vet that writes the next canned report
d = tempfile.mkdtemp()
canned = [report("INSTALL", [A]), report("INSTALL", [A]), report("COPY RULES, SKIP PLUGIN", [A, B])]
for i, t in enumerate(canned):
    open(os.path.join(d, f"canned{i}"), "w").write(t)
stub = os.path.join(d, "stub-vet")
open(stub, "w").write(f"""#!/usr/bin/env bash
n=$(cat {d}/count 2>/dev/null || echo 0); echo $((n + 1)) > {d}/count
[ -n "$STUB_FAIL_RUN" ] && [ "$STUB_FAIL_RUN" = "$((n + 1))" ] && exit 1
cp {d}/canned$n "$2"
""")
os.chmod(stub, 0o755)
def repeat(n, **env):
    open(os.path.join(d, "count"), "w").write("0")
    r = subprocess.run([os.path.join(HERE, "vet-repeat"), "tgt", os.path.join(d, "out"), str(n)], capture_output=True, text=True,
                       env={**os.environ, "VET_SCRIPT": stub, **env})
    return r.returncode, r.stdout + r.stderr
rc, out = repeat(2)
chk("vet-repeat of two agreeing runs is stable", rc == 0 and "stable" in out, out)
rc, out = repeat(3)
chk("vet-repeat of three disagreeing runs exits 1 and shows the spread", rc == 1 and "INSTALL in 2 of 3" in out, out)
rc, out = repeat(3, STUB_FAIL_RUN="3")
chk("a failed run is reported and fails the repeat, the others still compared", rc == 1 and "run 3 failed" in out and "2 reports" in out, out)
open(os.path.join(d, "canned0"), "w").write("no banner\n")
rc, out = repeat(2)
chk("an unparseable report makes vet-repeat exit 2, not 1", rc == 2, out)
rc, out = repeat(1)
chk("N of 1 is refused", rc == 2, out)
sys.exit(1 if fails else 0)
