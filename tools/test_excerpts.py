#!/usr/bin/env python3
"""tools/excerpts quotes a report in README.md and CASE-STUDIES.md: a fit report as its How it affects you table and its verdict strip, a facts report as its title line, its source line, the table
and one line per facts card (read marker, name and gist). A report without the 2.0 summary table is refused.
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


# The 2.0 layout (report-assembly-2-0): the report opens with the "How it affects you" summary table, the facts are cards under
# "What it adds", and a fit report's verdict is a strip inside the first layer. A report in the old layout is refused.
SUMMARY = """| | Row | In short |
|---|---|---|
| 🟩 | Cost | adds 13 characters to every session, ~3 tokens (13 skill descriptions, 0 agent descriptions, 0 rule files, 0 hook text) |
| 🟨 | Reach | a hook in every main session |
| 🟩 | Leaves state | nothing found |
| 🟩 | Live surface | no hook commands, MCP servers or mods found |
| 🟩 | Read completeness | read in full |

<details><summary><b>How the colours are set</b></summary>

The colours follow written rules. Each is checked top to bottom, and the first match wins.

</details>

The colours follow written rules.
"""
LAYERS = """# 🔍 demo 1.2.3 · how it affects you, what it adds, where it takes a position{tail}

`2026-11-15` · neckbeard 2.0.0 · [a/demo](https://github.com/a/demo) 1.2.3 @ `abc1234`

**Contents**

1. [How it affects you](#how-it-affects-you): cost, reach, state and live surface at a glance.
2. [What it adds](#what-it-adds): what the plugin loads. No judgement.
3. [Where it takes a position](#where-it-takes-a-position): by topic. No judgement.

---

**1 · Summary · carries a judgement**

## How it affects you

""" + SUMMARY + """{strip}
---

**2 · Facts · written by code · no judgement**

## What it adds

🟢 read in full · 🟡 partly read · 🔴 something unread

<details><summary>🟢 <b>Injects</b> · 1 skills · ~3 tokens on demand &amp; more</summary>

- Skills:
  - demo: description every session (13 chars)

</details>

<details><summary>🟡 <b>Hooks</b> · partly read</summary>

- Hooks: partly read

</details>

<details><summary>🟢 <b>R&amp;D &lt;tools&gt;</b> · a &amp; b</summary>

- x

</details>

---

**3 · Positions · the plugin's own words · no judgement**

## Where it takes a position

<details><summary><b>Commits and git</b> · 1 · "Always run the tests."</summary>

- "Always run the tests."

</details>

No reader's rules were read: this report lists facts only and carries no verdict.
"""
NEW_FACTS = LAYERS.format(tail="", strip="")
STRIP = """> **🟨 COPY RULES, SKIP PLUGIN** · keep one rule as text  
> ⛔ **0** conflicts · 🔁 **1** covered · 🟩 **1** keep (1 rule) · 🗑️ **2** dropped  
> *against the sample reader (demo)*

<details><summary>📝 <b>Why this verdict</b> · keep one rule as text</summary>

It injects little. Verdict is relative to the sample reader.

</details>
"""
NEW_FIT = LAYERS.format(tail=" · against the sample reader", strip=STRIP)

r, text = run(NEW_FACTS)
check("2.0 facts: excerpted, not refused", r.returncode == 0, r.stderr)
check("2.0 facts: the title and the header line are quoted", "> # 🔍 demo 1.2.3 · how it affects you, what it adds, where it takes a position" in text and "`2026-11-15` · neckbeard 2.0.0 · [a/demo]" in text, text)
check("2.0 facts: the summary table is quoted whole, rows and header", all(s in text for s in ("| | Row | In short |", "| 🟩 | Cost | adds 13 characters to every session", "| 🟨 | Reach | a hook in every main session", "| 🟩 | Read completeness | read in full |")), text)
check("2.0 facts: one line per facts card: read marker, name and gist, unescaped",
      "\n> - 🟢 **Injects** · 1 skills · ~3 tokens on demand & more\n" in text and "\n> - 🟡 **Hooks** · partly read\n" in text, text)
check("2.0 facts: the card bodies, the colour-rules card, the footer, the positions layer and the closing line are left out",
      not any(s in text for s in ("demo: description every session", "How the colours are set", "colours follow written rules", "Commits and git", "No reader's rules", "Contents")), text)
check("2.0 facts: a card's name and gist are unescaped too", "\n> - 🟢 **R&D <tools>** · a & b\n" in text, text)
check("2.0 facts: no line is quoted twice", len([l for l in text.splitlines() if l.startswith("> - ")]) == 3, text)

r, text = run(NEW_FIT)
check("2.0 fit: excerpted, not refused", r.returncode == 0, r.stderr)
check("2.0 fit: the summary table and the verdict strip are both there, the table first",
      "| 🟩 | Cost |" in text and "> **🟨 COPY RULES, SKIP PLUGIN** · keep one rule as text" in text and text.index("| 🟩 | Cost |") < text.index("COPY RULES"), text)
check("2.0 fit: the strip keeps its counts and its reader line", "⛔ **0** conflicts" in text and "*against the sample reader (demo)*" in text, text)
check("2.0 fit: the cards and the facts layer are left out", not any(s in text for s in ("Why this verdict", "Verdict is relative", "Injects", "Commits and git")), text)

with tempfile.TemporaryDirectory() as d:
    root = Path(d)
    (root / "tools").mkdir()
    shutil.copy(SCRIPT, root / "tools" / "excerpts")
    (root / "examples").mkdir()
    (root / "examples" / "demo.md").write_text(NEW_FACTS)
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
    (root / "docs" / "own-report.md").write_text(NEW_FACTS)
    (root / "README.md").write_text("top\n<!-- report:docs/own-report -->\nold\n<!-- /report -->\n")
    ex = [sys.executable, str(root / "tools" / "excerpts")]
    r = subprocess.run(ex, capture_output=True, text=True)
    text = (root / "README.md").read_text()
    check("README.md takes a marker too, and a name with a folder reads that file in the repo",
          r.returncode == 0 and "\n> - 🟢 **Injects**" in text and "old" not in text, r.stderr + text)

# odd 2.0 reports: a card body with a rule line, and a "> **" line outside the summary layer
ODD = NEW_FACTS.replace("- Skills:\n  - demo: description every session (13 chars)", "- Skills:\n\n---\n\n  - demo: description every session (13 chars)")
r, text = run(ODD)
check("2.0 facts: a '---' line inside a card body does not end the card list", "\n> - 🟡 **Hooks** · partly read\n" in text and "R&D" in text, text)
ODD2 = NEW_FACTS.replace("- Hooks: partly read\n", "- Hooks: partly read\n> **x**\n")
r, text = run(ODD2)
ODD3 = NEW_FACTS.replace("**Contents**\n", "**Contents**\n\n> **quoted note**\n")
r, text = run(ODD3)
check("2.0 facts: a '> **' line before the summary layer does not make it a fit report", "\n> - 🟢 **Injects**" in text and "quoted note" not in text, text)
check("2.0 facts: a '> **' line in a card body does not make it a fit report", "\n> - 🟢 **Injects**" in text and "COPY RULES" not in text, text)

# A report in the old layout, or one with no summary table, is refused: nothing quotes one now that the gallery is regenerated.
for name, old in (("an old-layout facts report", FACTS), ("an old-layout fit report", FIT), ("a report with nothing recognisable", "# demo\n\nnothing recognisable here\n")):
    r, text = run(old)
    check(f"{name} exits with the 'neither a fit report nor a facts report' message and leaves the page as it was",
          r.returncode != 0 and "is neither a fit report" in r.stderr and "old text" in text, r.stderr + text)

ROOT = SCRIPT.parent.parent
for doc in ("README.md", "CASE-STUDIES.md"):
    body = (ROOT / doc).read_text()
    blocks = re.findall(r"<!-- report:[\w./-]+ -->\n(.*?)\n<!-- /report -->", body, re.S)
    bare = [l for b in blocks for l in b.splitlines() if l.rstrip().endswith(":")]
    check(f"{doc}: no line in a report block ends in a colon", bool(blocks) and not bare, "; ".join(bare) or "no report blocks found")

sys.exit(1 if failures else 0)
