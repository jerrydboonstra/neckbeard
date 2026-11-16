#!/usr/bin/env python3
"""tools/excerpts quotes a report in CASE-STUDIES.md: a fit report as its verdict box and At-a-glance table, a facts report
(no verdict box) as its title line, its source line, and under "What it adds" each ### heading with its top-level bullets (a bullet ending in ":" says how many items it held).
Every case runs a copy of the script inside a throwaway tree, since the script finds its root from its own location."""
import re, shutil, subprocess, sys, tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "excerpts"
failures = []


def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        failures.append(name)


FACTS = """# 🔍 demo 1.2.3 · what it adds

`2026-11-15` · neckbeard 1.17.1 · [a/demo](https://github.com/a/demo) 1.2.3 @ `abc1234`

## What it adds

### Injects
- Skills:
  - demo: description every session (10 chars)
- Rule files: none

### Hooks
- Hooks: partly read
  - reaches subagents: unknown

## Notes

No reader's rules were read: this report lists facts only and carries no verdict.
"""
FIT = """# demo, fit report

> ## 🟩 install
> It fits the reader.
>
> Verdict is relative to the sample reader.

| | | |
|---|---|---|
| ⛔ conflicts | 0 | none |

## Later
text
"""


def run(report, *args):
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "tools").mkdir()
        shutil.copy(SCRIPT, root / "tools" / "excerpts")
        (root / "examples").mkdir()
        (root / "examples" / "demo.md").write_text(report)
        doc = root / "CASE-STUDIES.md"
        doc.write_text("intro\n\n<!-- report:demo -->\nold text\n<!-- /report -->\n\nend\n")
        r = subprocess.run([sys.executable, str(root / "tools" / "excerpts"), *args], capture_output=True, text=True)
        return r, doc.read_text()


r, text = run(FACTS)
check("a facts report is excerpted, not refused", r.returncode == 0, r.stderr)
check("facts: the title line is quoted", "> # 🔍 demo 1.2.3 · what it adds" in text, text)
check("facts: the source line is quoted", "`2026-11-15` · neckbeard 1.17.1 · [a/demo]" in text, text)
check("facts: each ### heading and its top-level bullets are quoted",
      all(s in text for s in ("### Injects", "- Skills:", "- Rule files: none", "### Hooks", "- Hooks: partly read")), text)
check("facts: sub-bullets and the closing note are left out",
      "demo: description every session" not in text and "reaches subagents" not in text and "No reader's rules" not in text, text)
check("facts: no verdict box is invented", "> ## " not in text and "| | | |" not in text, text)

r, text = run(FIT)
check("a fit report keeps its verdict box and At-a-glance table",
      r.returncode == 0 and "> 🟩 install\n> It fits the reader." in text and "| ⛔ conflicts | 0 | none |" in text, r.stderr + text)
check("fit: the closing 'Verdict is relative' note is left out", "Verdict is relative" not in text, text)

with tempfile.TemporaryDirectory() as d:
    root = Path(d)
    (root / "tools").mkdir()
    shutil.copy(SCRIPT, root / "tools" / "excerpts")
    (root / "examples").mkdir()
    (root / "examples" / "demo.md").write_text(FACTS)
    (root / "CASE-STUDIES.md").write_text("<!-- report:demo -->\nold\n<!-- /report -->\n")
    ex = [sys.executable, str(root / "tools" / "excerpts")]
    stale = subprocess.run(ex + ["--check"], capture_output=True, text=True)
    check("--check names a stale facts excerpt", stale.returncode == 1 and "demo" in stale.stderr, stale.stderr)
    subprocess.run(ex, capture_output=True, text=True)
    fresh = subprocess.run(ex + ["--check"], capture_output=True, text=True)
    check("--check passes once the excerpt is rewritten", fresh.returncode == 0, fresh.stderr)

with tempfile.TemporaryDirectory() as d:
    root = Path(d)
    (root / "tools").mkdir()
    shutil.copy(SCRIPT, root / "tools" / "excerpts")
    (root / "docs").mkdir()
    (root / "docs" / "own-report.md").write_text(FACTS)
    (root / "README.md").write_text("top\n<!-- report:docs/own-report -->\nold\n<!-- /report -->\n")
    ex = [sys.executable, str(root / "tools" / "excerpts")]
    r = subprocess.run(ex, capture_output=True, text=True)
    text = (root / "README.md").read_text()
    check("README.md takes a marker too, and a name with a folder reads that file in the repo",
          r.returncode == 0 and "> ### Injects" in text and "old" not in text, r.stderr + text)

# A bullet ending in ":" whose children the excerpt drops carries their count, so no quoted line ends bare.
COUNTS = FACTS.replace("## Notes", """### State it may leave
- Persistence candidates:
  - a.py
  - b.py
  - and 19 more, in: tools/ 19
- Agents:
- Commands:
\t- one
- Tabbed:
\t- x
\t- y
- Nested:
  - top
    - detail
- Lone overflow:
  - and 3 more, in:

## Notes""")
r, text = run(COUNTS)
check("facts: one child gives its count and its name, whole line",
      "\n> - Skills: 1 (demo)\n" in text, text)
check("facts: a child with no colon is named whole",
      "\n> - Commands: 1 (one)\n" in text, text)
check("facts: 'and N more' adds N to the listed lines",
      "\n> - Persistence candidates: 21 (see the full report)\n" in text, text)
check("facts: tab-indented children are counted", "\n> - Tabbed: 2 (see the full report)\n" in text, text)
check("facts: a nested detail is not a child", "\n> - Nested: 1 (top)\n" in text, text)
check("facts: a lone 'and N more' counts N and is not named", "\n> - Lone overflow: 3 (see the full report)\n" in text, text)
check("facts: a bullet ending in a colon with no children says none",
      "\n> - Agents: none\n" in text, text)
check("facts: a bullet with text after its colon is unchanged", "\n> - Hooks: partly read\n" in text, text)
check("facts: no quoted line ends in a colon", not any(l.rstrip().endswith(":") for l in text.splitlines() if l.startswith("> ")), text)

ROOT = SCRIPT.parent.parent
for doc in ("README.md", "CASE-STUDIES.md"):
    body = (ROOT / doc).read_text()
    blocks = re.findall(r"<!-- report:[\w./-]+ -->\n(.*?)\n<!-- /report -->", body, re.S)
    bare = [l for b in blocks for l in b.splitlines() if l.rstrip().endswith(":")]
    check(f"{doc}: no line in a report block ends in a colon", bool(blocks) and not bare, "; ".join(bare) or "no report blocks found")

sys.exit(1 if failures else 0)
