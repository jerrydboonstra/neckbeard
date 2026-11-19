#!/usr/bin/env python3
"""tools/vet's 2.0 layout (report-assembly-2-0): the title, the header line, the Contents list and the three layers (the summary rows,
the facts, the positions) of a published and a fit report, vet's own checks on the report it assembled, and that a renderer that fails
stops the run before the judge. Run end to end against the fake `claude` in tools/vet_harness.py. Split from tools/test_vet.py to
stay under the test-module size cap.

    python3 tools/test_vet_layers.py
"""
import json, os, re, shutil, subprocess, sys, tempfile

import vet_harness
from vet_harness import *


judges = lambda r: isolated(r, "ANSWERING JUDGE") + isolated(r, "PROSE JUDGE")
hline = lambda r: r["text"].split("\n")[2]   # the header line, which vet --check reads

# 0c. the 2.0 layout (report-assembly-2-0): the title, the header line, a Contents list, then three layers, each opened by a `---`
# rule and its label line and then its heading. tools/vet writes no card markup: the layers are what the renderers print.
HEADINGS = ["## How it affects you", "## What it adds", "## Where it takes a position"]
LABELS = ["**1 \u00b7 Summary \u00b7 carries a judgement**", "**2 \u00b7 Facts \u00b7 written by code \u00b7 no judgement**", "**3 \u00b7 Positions \u00b7 the plugin's own words \u00b7 no judgement**"]
SQUARES = "\U0001F7E9\U0001F7E8\U0001F7E7\U0001F7E5"
MARKERS = "\U0001F7E2\U0001F7E1\U0001F534"
FIT_CARDS = ("Why this verdict", "Conflicts", "Already covered", "Keep", "Dropped", "Do this", "Proposed rules patch")


def at(text, needle):
    return text.find("\n" + needle + "\n")


def layers(text):
    """The three layers' texts: from the layer's rule to the next layer's rule, the last to the end of the report."""
    cuts = [text.find("\n---\n\n" + l + "\n") for l in LABELS] + [len(text)]
    return [text[cuts[i]:cuts[i + 1]] if cuts[i] >= 0 else "" for i in range(3)]


def ordered(text):
    spots = [at(text, "**Contents**")] + [at(text, x) for pair in zip(LABELS, HEADINGS) for x in pair]
    return all(s >= 0 for s in spots) and spots == sorted(spots)


r = run("layers-facts", commit=True, extra=("--facts",), fake_body=NO_CLAUDE)
L1, L2, L3 = layers(r["text"])
chk("layers: a published report: exit 0, the 2.0 title, the header line on line 3", (r["rc"], r["title"], hline(r).startswith("`") and " \u00b7 made by neckbeard " in hline(r)), (0, TITLE, True))
# report-glance-title-2-0: the plugin is named once in the title (no version, no layer list); the header line carries the source, its version and
# commit, then "made by neckbeard <version>"; the summary layer has no fold and one card of colour rules
chk("glance-title: a published title is '# 🔍 <plugin>' alone, and the version is in the header line only", (r["title"], r["text"].count("how it affects you, what it adds, where it takes a position")), (TITLE, 0))
chk("glance-title: the header line: date, source, its version @ commit, then made by neckbeard <its version>", re.fullmatch(r"`\d{4}-\d\d-\d\d` \u00b7 demo 1\.0\.0 @ `[0-9a-f]+` \u00b7 made by neckbeard " + re.escape(NBV), hline(r)) is not None, True)
chk("glance-title: the summary layer holds no 'At a glance in full' fold, and one card, the colour rules, after the table", ("At a glance in full" in L1, L1.count("<details><summary><b>How the colours are set</b>"), 0 <= L1.find("| | Row |") < L1.find("How the colours are set")), (False, 1, True))
chk("glance-title: the Cost row names its unit", re.search(r"\| Cost \| adds [\d,]+ characters to every session", L1) is not None, True)
chk("layers: the Contents list, then each layer's rule, label line and heading, in order", (ordered(r["text"]), all("\n---\n\n" + l + "\n\n" + h + "\n" in r["text"] for l, h in zip(LABELS, HEADINGS))), (True, True))
contents = r["text"].partition("**Contents**")[2].split("\n---\n", 1)[0]
chk("layers: Contents has one numbered line per layer, with its anchor", [x in contents for x in ("1. [How it affects you](#how-it-affects-you)", "2. [What it adds](#what-it-adds)", "3. [Where it takes a position](#where-it-takes-a-position)")], [True] * 3)
chk("layers: in a published report the first Contents line leaves out the fit and the verdict, and is there", ("how it affects you" in (contents.split("\n") + ["", "", ""])[2].lower(), [w in (contents.split("\n") + ["", "", ""])[2].lower() for w in ("fit", "verdict")]), (True, [False, False]))
chk("layers: the summary layer holds the five rows from tools/summary", [re.search(r"^\| [" + SQUARES + r"] \| " + n + r" \|", L1, re.M) is not None for n in ("Cost", "Reach", "Leaves state", "Live surface", "Read completeness")], [True] * 5)
chk("layers: a published report has no verdict strip and no fit card", ("\n> **" in r["text"], any("<b>" + c + "</b>" in r["text"] for c in FIT_CARDS)), (False, False))
chk("layers: no judgement colour inside What it adds, no read marker outside it (Contents included)", (any(q in L2 for q in SQUARES), any(m in r["text"].replace(L2, "") for m in MARKERS)), (False, False))
chk("layers: What it adds holds part 1's six cards and the commit vet holds", (all(re.search(r"^<details><summary>[" + MARKERS + r"] <b>" + h + r"</b>", L2, re.M) for h in ("Injects", "Hooks", "Subagents and commands", "State it may leave", "Reaches outside the session", "Source")), f"Commit: {r['sha']}" in L2 and r["sha"] != ""), (True, True))
chk("layers: Where it takes a position holds tools/positions-layer's cards", ("<b>Commits and git</b>" in L3, L3.count("\n## ")), (True, 1))
chk("layers: the closing line ends the report", r["text"].rstrip("\n").split("\n")[-1] == "No reader's rules were read: this report lists facts only and carries no verdict.", True)
chk("layers: no reader rule or local path in the report", ("READER" in r["text"], os.path.realpath(r["target"]) in r["text"], "/tmp" in r["text"]), (False, False, False))
# the excerpt of the report vet really writes: the summary table and one line per facts card (drift between vet and tools/excerpts shows here)
ex_root = tempfile.mkdtemp()
try:
    os.makedirs(os.path.join(ex_root, "tools")); os.makedirs(os.path.join(ex_root, "examples"))
    shutil.copy(os.path.join(HERE, "excerpts"), os.path.join(ex_root, "tools", "excerpts"))
    open(os.path.join(ex_root, "examples", "demo.md"), "w", encoding="utf-8").write(r["text"])
    open(os.path.join(ex_root, "CASE-STUDIES.md"), "w").write("<!-- report:demo -->\nold\n<!-- /report -->\n")
    xr = subprocess.run([sys.executable, os.path.join(ex_root, "tools", "excerpts")], capture_output=True, text=True)
    ex_text = open(os.path.join(ex_root, "CASE-STUDIES.md"), encoding="utf-8").read()
finally:
    shutil.rmtree(ex_root)
chk("layers: tools/excerpts reads the report vet --facts wrote: its summary table and one line per facts card, no card body",
    (xr.returncode, "| Cost |" in ex_text and "| Read completeness |" in ex_text, len([l for l in ex_text.splitlines() if l.startswith("> - ")]), "Load timing" in ex_text), (0, True, 6, False))
r0 = run("part1-no-commit", extra=("--facts",), fake_body=NO_CLAUDE)
chk("layers: with no git commit the Source card says commit not given", "Commit: commit not given" in r0["text"], True)

r = run("layers-fit", commit=True, units="units-install", extra=("--note", "A self-vetting notice."))
L1, L2, L3 = layers(r["text"])
chk("layers: a fit report: exit 0, the title ends against the sample reader", (r["rc"], r["title"]), (0, TITLE + " \u00b7 against the sample reader"))
chk("layers: a fit report holds the same layers in order", ordered(r["text"]), True)
strip, last_row = r["text"].find("\n> **\U0001F7E9 INSTALL**"), r["text"].find("| Read completeness |")
cards = [r["text"].find("<b>" + c + "</b>") for c in FIT_CARDS]
chk("layers: the strip and the seven fit cards come after the summary rows, inside layer 1", (0 < last_row < strip < cards[0], cards == sorted(cards) and all(c > 0 for c in cards), all(c in L1 for c in ("<b>Why this verdict</b>", "<b>Proposed rules patch</b>"))), (True, True, True))
why = r["text"].split("<b>Why this verdict</b>", 1)[1].split("<b>Conflicts</b>", 1)[0]
chk("layers: the Baseline line, the Judge line and the --note sentence each appear once, inside Why this verdict, in order",
    ([r["text"].count(x) for x in ("\nBaseline: ", "\nJudge: ", "A self-vetting notice.")], 0 < why.find("A self-vetting notice.") < why.find("Verdict is relative") < why.find("Baseline: ") < why.find("Judge: ") < why.find("Rule files")), ([1, 1, 1], True))
chk("layers: no read marker outside What it adds", any(m in r["text"].replace(L2, "") for m in MARKERS), False)
first_line = (r["text"].partition("**Contents**")[2].split("\n") + ["", "", ""])[2].lower()
chk("layers: a fit report's first Contents line names the fit and the verdict", [w in first_line for w in ("fit", "verdict")], [True, True])

for tool in ("summary", "positions", "positions-layer"):
    for mode, kw in (("published", dict(extra=("--facts",), fake_body=NO_CLAUDE)), ("fit", dict(units="units-install"))):
        r = vet_with_tool(tool, "import sys\nsys.stderr.write('%s: broken on purpose\\n')\nsys.exit(2)\n" % tool, **kw)
        chk(f"layers: a {mode} report: when tools/{tool} exits non-zero vet stops with its stderr and writes no report",
            (r["rc"] != 0, r["report"], f"{tool}: broken on purpose" in r["out"]), (True, False, True))
        if mode == "fit":   # the renderers run before the judge, so a broken one costs no judge call
            chk(f"layers: with tools/{tool} broken no find, confirm, answering or prose call is made",
                [c["prompt"][:40] for c in r["calls"] if "single word ok" not in c["prompt"]], [])

# vet's own checks on the report it assembled: the three layer headings in order, and no verdict in a published report
r = vet_with_tool("positions-layer", "import sys\nprint('Nothing to see.')\n", extra=("--facts",), fake_body=NO_CLAUDE)
chk("layers: a positions layer with no '## Where it takes a position' heading: vet stops naming it and writes no report",
    (r["rc"] != 0, r["report"], "Where it takes a position" in r["out"]), (True, False, True))
r = vet_with_tool("summary", "import sys\nprint('| | Row | In short |\\n|---|---|---|\\n\\n> **\\U0001F7E9 INSTALL** \\u00b7 fine  ')\n", extra=("--facts",), fake_body=NO_CLAUDE)
chk("layers: a verdict strip in a published report is refused and no report is written", (r["rc"] != 0, r["report"], "verdict" in r["out"]), (True, False, True))
r = vet_with_tool("summary", "import sys\nprint('<details><summary><b>Why this verdict</b></summary>\\n\\nx\\n\\n</details>')\n", extra=("--facts",), fake_body=NO_CLAUDE)
chk("layers: a fit card in a published report is refused and no report is written", (r["rc"] != 0, r["report"], "fit card" in r["out"]), (True, False, True))
r = vet_with_tool("part1", REAL_PART1 + "if __name__ == '__main__':\n    import sys\n    print('read in full' if sys.argv[1] == '--read-state' else 'Not a heading.')\n", extra=("--facts",), fake_body=NO_CLAUDE)
chk("layers: a facts layer with no '## What it adds' heading is refused and no report is written", (r["rc"] != 0, r["report"], "What it adds" in r["out"]), (True, False, True))

sys.exit(vet_harness.summary("test_vet_layers"))
