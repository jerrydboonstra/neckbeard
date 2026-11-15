#!/usr/bin/env python3
"""tools/excerpts quotes a report in CASE-STUDIES.md: a fit report as its verdict box and At-a-glance table, a facts report
(no verdict box) as its title line, its source line, and under "What it adds" each ### heading with its top-level bullets.
Every case runs a copy of the script inside a throwaway tree, since the script finds its root from its own location."""
import shutil, subprocess, sys, tempfile
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

sys.exit(1 if failures else 0)
