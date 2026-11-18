#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""tools/positions, the positions layer (report-positions): a fixture plugin written for this test, a golden OUT.

    python3 tools/test_positions.py
"""
import json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
fails = 0


def chk(name, ok, detail=""):
    global fails
    fails += not ok
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + ("" if ok else f": {detail}"))


def run(*args):
    r = subprocess.run([sys.executable, os.path.join(HERE, "positions"), *args], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


d = tempfile.mkdtemp()
skill = """---
name: fx
description: Always be brief. Never ramble.
---

# Fixture

You are a careful assistant. Never skip the checklist. Greet the user.

Some background prose with nothing to act on.

- Always run the tests before you commit.
- Keep comments short.
- Chat freely.

```
Never do this inside a fence.
```

| Rule | Detail |
| --- | --- |
| Dependencies | Never add a package for one call |

## Pushes

Do not push without a go-ahead.
Stop after the release.
"""
dossier = {"target": {
    "skills": [{"source": "skills/fx/SKILL.md", "text": skill, "companion_files": [{"path": "skills/fx/roles/w.md", "text": "# W\n\nChat freely.\n"}]}],
    "commands": [{"source": "commands/c.md", "text": "Always run the tests before you commit.\n"}],
    "agents": [], "rule_files": [],
    "hooks": {"injected_content": [
        {"file": "hooks/h.js", "text": "Always stay concise.\nUse the cache.\n"},
        {"file": "hooks/run.sh", "resolved_file": "hooks/inj.md", "text": "\nNever commit secrets.\n"},
        {"file": "hooks/none.md", "bytes": 4}]}}}
D = os.path.join(d, "dossier.json")
json.dump(dossier, open(D, "w"))
P = lambda quote, file, line, also=(): {"quote": quote, "file": file, "line": line, "also_in": list(also)}
golden = {"topics": [
    {"name": "Tests", "positions": [P("Always run the tests before you commit.", "commands/c.md", 1, ["skills/fx/SKILL.md:12"])]},
    {"name": "Code style and comments", "positions": [P("Keep comments short.", "skills/fx/SKILL.md", 13)]},
    {"name": "Dependencies", "positions": [P("Dependencies | Never add a package for one call", "skills/fx/SKILL.md", 22)]},
    {"name": "Commits and git", "positions": [P("Never commit secrets.", "hooks/inj.md", 2)]},
    {"name": "Pushes and releases", "positions": [P("Do not push without a go-ahead.", "skills/fx/SKILL.md", 26),
                                                  P("Stop after the release.", "skills/fx/SKILL.md", 27)]},
    {"name": "State and files", "positions": [P("Use the cache.", "hooks/h.js", None)]},
    {"name": "other", "positions": [P("Always stay concise.", "hooks/h.js", None), P("Never skip the checklist.", "skills/fx/SKILL.md", 8)]},
]}
O1, O2 = os.path.join(d, "o1.json"), os.path.join(d, "o2.json")
code, out = run(D, O1)
got = json.load(open(O1))
chk("1. golden OUT: topics, quotes, files, lines, other last, empty topics left out, a hook with no resolved file has no line",
    code == 0 and got == golden, json.dumps(got, indent=1))
chk("1b. prints the count", "9 positions in 7 topics" in out, out)
chk("1c. a duplicate quote is listed once, under the first file in path order, with the other place in also_in",
    got["topics"][0]["positions"][0]["file"] == "commands/c.md" and got["topics"][0]["positions"][0]["also_in"] == ["skills/fx/SKILL.md:12"])

run(D, O2)
chk("2. two runs give byte-identical OUT", open(O1, "rb").read() == open(O2, "rb").read())

quotes = [p["quote"] for t in got["topics"] for p in t["positions"]]
chk("3. lines in a code fence or frontmatter, and prose with no directive word, are never positions",
    not any("fence" in q or "ramble" in q or "brief" in q or "background" in q or "Greet" in q or "Chat freely" in q for q in quotes), quotes)
chk("3b. a table's header row is not a position", not any(q.startswith("Rule |") for q in quotes), quotes)

reader = os.path.join(d, "reader")
os.makedirs(reader)
open(os.path.join(reader, "CLAUDE.md"), "w").write("Never use tabs.\nAlways run the linter.\n")
O3 = os.path.join(d, "o3.json")
code, out = run(D, O3, "--reader", reader)
chk("4. given a reader folder, the tool reads none of it: no reader line in OUT, and OUT is the same as without it",
    code == 0 and b"tabs" not in open(O3, "rb").read() and b"linter" not in open(O3, "rb").read() and open(O3, "rb").read() == open(O1, "rb").read(), out)

code, out = run(D)
chk("usage error with one argument", code != 0 and "usage" in out, out)
sys.exit(1 if fails else 0)
