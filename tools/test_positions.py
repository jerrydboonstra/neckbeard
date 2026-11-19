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

- Always run the tests before you finish.
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
# TOML commands: the prompt's own words, no key or delimiters, the description left out, true line numbers for a prompt written
# over several lines, the prompt's line for one written on a line with \\n escapes.
toml_one = 'description = "Always ramble here."\nprompt = "Ask first. Stop after the review.\\nUse the plan."\n'
toml_many = 'description = "d"\nprompt = """\nDo not push to main.\n\n- Always commit often.\n"""\n'
# The shapes the inventory writes (skills/neckbeard/inventory_parts.py): a skill's "source" is its relative path and its "path"
# absolute; a command's "source" is the kind and its "path" relative; the root CLAUDE.md is source "target-CLAUDE.md" with an
# absolute path; a hook's injected file is {"file", "bytes"}, and a hook built at run time adds its "template" lines.
dossier = {"target": {
    "skills": [{"source": "skills/fx/SKILL.md", "path": "/abs/root/skills/fx/SKILL.md", "text": skill,
                "companion_files": [{"path": "skills/fx/roles/w.md", "text": "# W\n\nChat freely.\n"}]}],
    "commands": [{"source": "command", "path": "commands/c.md", "text": "Always run the tests before you finish.\n"},
                 {"source": "command", "path": "commands/t.toml", "text": toml_one},
                 {"source": "command", "path": "commands/u.toml", "text": toml_many}],
    "agents": [],
    "rule_files": [{"source": "target-CLAUDE.md", "path": "/abs/root/CLAUDE.md", "text": "Always use tabs.\n"},
                   {"source": "target-CLAUDE.md import", "path": "/abs/root/docs/imp.md", "text": "Never fetch the page.\n"}],
    "hooks": {"injected_content": [
        {"file": "skills/fx/SKILL.md", "bytes": 400},
        {"file": "hooks/h.sh", "bytes": 60, "events": ["SessionStart"], "built_at_run_time": True,
         "template": ["Always stay concise.", "Use the cache.", "Never commit secrets."], "writes": [], "at_least": False}]}}}
D = os.path.join(d, "dossier.json")
json.dump(dossier, open(D, "w"))
P = lambda quote, file, line, also=(): {"quote": quote, "file": file, "line": line, "also_in": list(also)}
golden = {"topics": [
    {"name": "Asking vs proceeding", "positions": [P("Ask first.", "commands/t.toml", 2)]},
    {"name": "Tests", "positions": [P("Always run the tests before you finish.", "commands/c.md", 1, ["skills/fx/SKILL.md:12"])]},
    {"name": "Code style and comments", "positions": [P("Keep comments short.", "skills/fx/SKILL.md", 13)]},
    {"name": "Dependencies", "positions": [P("Dependencies | Never add a package for one call", "skills/fx/SKILL.md", 22)]},
    {"name": "Commits and git", "positions": [P("Always commit often.", "commands/u.toml", 5), P("Never commit secrets.", "hooks/h.sh", None)]},
    {"name": "Pushes and releases", "positions": [P("Do not push to main.", "commands/u.toml", 3), P("Do not push without a go-ahead.", "skills/fx/SKILL.md", 26),
                                                  P("Stop after the release.", "skills/fx/SKILL.md", 27)]},
    {"name": "Reviews and audits", "positions": [P("Stop after the review.", "commands/t.toml", 2)]},
    {"name": "State and files", "positions": [P("Use the cache.", "hooks/h.sh", None)]},
    {"name": "Network", "positions": [P("Never fetch the page.", "docs/imp.md", 1)]},
    {"name": "other", "positions": [P("Always use tabs.", "CLAUDE.md", 1), P("Use the plan.", "commands/t.toml", 2), P("Always stay concise.", "hooks/h.sh", None),
                                    P("Never skip the checklist.", "skills/fx/SKILL.md", 8)]},
]}
O1, O2 = os.path.join(d, "o1.json"), os.path.join(d, "o2.json")
code, out = run(D, O1)
got = json.load(open(O1))
chk("1. golden OUT: topics, quotes, files, lines, other last, empty topics left out, a command is named by its path, a root CLAUDE.md and an import by their relative path, hook template text has no line",
    code == 0 and got == golden, json.dumps(got, indent=1))
chk("1b. prints the count", "16 positions in 10 topics" in out, out)
chk("1c. a duplicate quote is listed once, under the first file in path order, with the other place in also_in",
    [(p["file"], p["also_in"]) for t in got["topics"] for p in t["positions"] if p["quote"].startswith("Always run")] == [("commands/c.md", ["skills/fx/SKILL.md:12"])])

run(D, O2)
chk("2. two runs give byte-identical OUT", open(O1, "rb").read() == open(O2, "rb").read())

quotes = [p["quote"] for t in got["topics"] for p in t["positions"]]
chk("3. lines in a code fence or frontmatter, and prose with no directive word, are never positions",
    not any("fence" in q or "ramble" in q or "brief" in q or "background" in q or "Greet" in q or "Chat freely" in q or "ramble" in q for q in quotes), quotes)
chk("3b. a table's header row is not a position", not any(q.startswith("Rule |") for q in quotes), quotes)

reader = os.path.join(d, "reader")
os.makedirs(reader)
open(os.path.join(reader, "CLAUDE.md"), "w").write("Never use semicolons.\nAlways run the linter.\n")
O3 = os.path.join(d, "o3.json")
code, out = run(D, O3, "--reader", reader)
chk("4. given a reader folder, the tool reads none of it: no reader line in OUT, and OUT is the same as without it",
    code == 0 and b"semicolons" not in open(O3, "rb").read() and b"linter" not in open(O3, "rb").read() and open(O3, "rb").read() == open(O1, "rb").read(), out)

# Quotes that tie on (file, line): four on one line of a command, and four from one hook template (no line, so line 0). The sort
# key once stopped at file and line, so a tie kept the iteration order of a string set, which PYTHONHASHSEED changes.
def seeded(dossier, name):
    """Run tools/positions under PYTHONHASHSEED 0 to 15: (every seed exited 0, the set of OUT bytes, each seed's parsed OUT)."""
    path = os.path.join(d, name + ".json")
    json.dump(dossier, open(path, "w"))
    ok, outs, parsed = True, set(), []
    for seed in range(16):
        out_path = os.path.join(d, f"{name}{seed}.out.json")
        r = subprocess.run([sys.executable, os.path.join(HERE, "positions"), path, out_path], capture_output=True, text=True,
                           env={**os.environ, "PYTHONHASHSEED": str(seed)})
        if r.returncode != 0:
            ok = False
            continue
        outs.add(open(out_path, "rb").read())
        parsed.append(json.load(open(out_path)))
    return ok, outs, parsed


def quotes_of(got):
    return [p["quote"] for t in got["topics"] for p in t["positions"]]


four = ["Always run the tests.", "Never skip the tests.", "Run the tests twice.", "Do not skip the tests."]
tie_dossier = {"target": {"skills": [], "agents": [], "hooks": {}, "rule_files": [], "commands": [
    {"source": "command", "path": "commands/tie.md", "text": " ".join(four) + "\n"}]}}
ok, outs, parsed = seeded(tie_dossier, "tie")
chk("5. quotes on one line keep one order under PYTHONHASHSEED 0 to 15, every run exiting 0", ok and len(outs) == 1, f"ok={ok}, {len(outs)} different outputs")
chk("5b. the tie fixture holds four quotes, all on line 1", bool(parsed) and all(len(quotes_of(g)) == 4 and all(p["line"] == 1 for t in g["topics"] for p in t["positions"]) for g in parsed), parsed[:1])
chk("5c. in every seed, quotes on one line are in quote order", bool(parsed) and all(quotes_of(g) == sorted(four) for g in parsed), [quotes_of(g) for g in parsed][:2])

hook_dossier = {"target": {"skills": [], "agents": [], "commands": [], "rule_files": [], "hooks": {"injected_content": [
    {"file": "hooks/h.sh", "bytes": 60, "events": ["SessionStart"], "built_at_run_time": True, "writes": [], "at_least": False,
     "template": four}]}}}
ok, outs, parsed = seeded(hook_dossier, "hook")
chk("6. hook-template quotes (no line) keep one order under PYTHONHASHSEED 0 to 15, every run exiting 0", ok and len(outs) == 1, f"ok={ok}, {len(outs)} different outputs")
chk("6b. in every seed the hook fixture holds four quotes with no line, in quote order", bool(parsed) and all(quotes_of(g) == sorted(four) and all(p["line"] is None for t in g["topics"] for p in t["positions"]) for g in parsed), [quotes_of(g) for g in parsed][:2])

code, out = run(D)
chk("usage error with one argument", code != 0 and "usage" in out, out)
sys.exit(1 if fails else 0)
