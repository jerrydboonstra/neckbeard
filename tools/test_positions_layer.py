#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""tools/positions-layer (positions-render): the "Where it takes a position" layer, one card per topic, from tools/positions' JSON.

    python3 tools/test_positions_layer.py

Fixtures: tools/fixtures/positions-layer/*.json. The numbers match the item's Done when points."""
import json, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FX = os.path.join(HERE, "fixtures", "positions-layer")
TOOL = os.path.join(HERE, "positions-layer")
sys.path.insert(0, HERE)
from cards import card
fails = 0


def chk(name, ok, detail=""):
    global fails
    fails += not ok
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + ("" if ok else f": {detail}"))


def run(*args):
    r = subprocess.run([sys.executable, TOOL, *args], capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def fx(name):
    return os.path.join(FX, name + ".positions.json")


HEAD = "## Where it takes a position"
code, out, err = run(fx("two-topics"))
lines = out.split("\n")
summaries = [l for l in lines if l.startswith("<details><summary>")]
chk("1. heading first, then one block-quote note line", code == 0 and lines[0] == HEAD and lines[2].startswith("> "), out)
note = lines[2] if len(lines) > 2 else ""
chk("1b. the note says what is read and what is not quoted", all(w in note for w in ("instruction files", "template", "not quoted")), note)
chk("1c. one card per topic, in the JSON's order, no marker, count and first quote in the gist",
    summaries == ['<details><summary><b>Testing</b> · 2 · "Always run the tests before you finish."</summary>',
                  '<details><summary><b>other</b> · 2 · "Use `make check` for a hook."</summary>'], summaries)
chk("1d. one list item per position, quote then place, also_in as plain text",
    '- "Always run the tests before you finish." `skills/fx/SKILL.md:12` (also in `commands/c.md:3`, `agents/a.md:7`)' in out
    and '- "Never skip the checklist." `skills/fx/SKILL.md:8`' in out, out)
chk("1e. byte-identical on a second run", out != "" and run(fx("two-topics"))[1] == out)
chk("1f. an empty marker leaves no stray space before the name", "<summary><b>" in out and "<summary> <b>" not in out)
chk("1g. card() with an empty marker drops the marker and its space", card("", "N", "g", [])[0] == "<details><summary><b>N</b> · g</summary>", card("", "N", "g", [])[0])

code, out, _ = run(fx("two-topics"), "--repo", "https://github.com/o/r", "--commit", "abc1234")
chk("2. each place is a link to repo/blob/commit/file#L<line>",
    "[`skills/fx/SKILL.md:12`](https://github.com/o/r/blob/abc1234/skills/fx/SKILL.md#L12)" in out, out)
chk("2b. a null-line place links to the file with no #L", "[`hooks/session.sh`](https://github.com/o/r/blob/abc1234/hooks/session.sh)" in out, out)
chk("2c. also_in places stay plain text", "(also in `commands/c.md:3`" in out and "](https://github.com/o/r/blob/abc1234/commands" not in out, out)
for label, extra in (("no --repo", ["--commit", "abc1234"]), ("a non-GitHub repo", ["--repo", "https://example.com/o/r", "--commit", "abc1234"]),
                     ("a commit with a space", ["--repo", "https://github.com/o/r", "--commit", "abc1234 + uncommitted changes"]),
                     ("no --commit", ["--repo", "https://github.com/o/r"])):
    code, o, _ = run(fx("two-topics"), *extra)
    chk(f"2d. {label}: every place is plain code text", code == 0 and "](" not in o and "`skills/fx/SKILL.md:12`" in o, o)

code, o, _ = run(fx("hostile"), "--repo", "https://github.com/o/r", "--commit", "abc1234")
chk("2e. a path in a link is percent-encoded", "blob/abc1234/a%20b/c.md" not in o and "](https://github.com/o/r/blob/abc1234/skills/s/SKILL.md#L5)" in o, o)

code, out, _ = run(fx("hostile"))
chk("3. a quote holding </details> or <script> opens no tag and cannot close the card early",
    code == 0 and out.count("</details>") == 1 and "<script" not in out and "&lt;/details>" in out and "&lt;script>" in out, out)
chk("3b. an absolute path shows as its basename", "/Users/someone" not in out and "file.txt" in out, out)
chk("3c. a quote cannot become an image or a link; backticks and brackets are escaped",
    "![](" not in out and "[a](" not in out and "\\[a\\]" in out and "\\`unpaired" in out, out)
chk("3d. also_in places go through safe() too", "also in `a b/c.md:1`" in out, out)

code, out, _ = run(fx("long-first"))
m = re.search(r'<summary><b>Long</b> · 1 · "(.*?)"</summary>', out)
chk("4. a first quote over 60 characters is cut at 60 with an ellipsis in the gist",
    bool(m) and len(m.group(1)) == 60 and m.group(1).endswith("…") and m.group(1)[:59] == ("Always " + "word " * 30)[:59], out)
code, out, _ = run(fx("hostile"))
body = [l for l in out.split("\n") if l.startswith('- "x')]
chk("4b. a quote over 200 characters is cut by safe() in the body", len(body) == 1 and "x" * 199 + "…" in body[0] and "x" * 200 not in body[0], body)

code, out, _ = run(fx("no-topics"))
chk("5. no topics: heading, note line, 'No positions found.', exit 0",
    code == 0 and out.split("\n")[0] == HEAD and "No positions found." in out and "<details>" not in out, out)
code, out, err = run(fx("no-list"))
chk("5b. JSON without a topics list exits 2 with one line on stderr", code == 2 and len(err.strip().split("\n")) == 1 and "can't open file" not in err, err)
code, out, err = run(os.path.join(FX, "missing.positions.json"))
chk("5c. a missing file exits 2 with one line on stderr", code == 2 and len(err.strip().split("\n")) == 1 and "can't open file" not in err, err)
d = tempfile.mkdtemp()
open(os.path.join(d, "bad.json"), "w").write("{not json")
code, out, err = run(os.path.join(d, "bad.json"))
chk("5d. an unreadable file exits 2", code == 2 and len(err.strip().split("\n")) == 1 and "can't open file" not in err, err)

for name in ("two-topics", "hostile", "no-topics", "long-first"):
    o = run(fx(name))[1]
    chk(f"6. {name}: no read marker and no judgement colour", HEAD in o and not re.search("[\U0001F7E2\U0001F7E1\U0001F534\U0001F7E9\U0001F7E8\U0001F7E7\U0001F7E5]", o))
sys.exit(1 if fails else 0)
