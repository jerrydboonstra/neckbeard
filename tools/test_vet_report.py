#!/usr/bin/env python3
"""tools/vet's units path as the default (verdict-stability-rules): the order of the calls, the strip and cards the report carries,
a prose text that states its own verdict, the answering and prose prompts, hard_stop in the confirm call, and the header and Baseline
placement. Run end to end against the fake `claude` in tools/vet_harness.py. Split from tools/test_vet.py to stay under the test-module size cap.

    python3 tools/test_vet_report.py
"""
import json, os, re, shutil, subprocess, sys, tempfile

import vet_harness
from vet_harness import *

def first(r, word):
    return next(iter(isolated(r, word)), {"prompt": ""})["prompt"]
hline = lambda r: r["text"].split("\n")[2]   # the header line, which vet --check reads

# 0a. verdict-stability-rules: the units path is the default; the verdict and counts come from code
STRIP = re.compile(r"^> \*\*(.+?)\*\* \u00b7 (.*?)  $", re.M)
KINDS = ("FIND PASS", "CONFIRM CALL", "ANSWERING JUDGE", "PROSE JUDGE", "Vet one plugin")
def kinds(r):
    return [next((k for k in KINDS if k in c["prompt"]), "?") for c in r["calls"] if "single word ok" not in c["prompt"]]
r = run("order", units="units-install", finds="one", confirm="yes")
chk("order: three find passes, one confirm, the answering judge, the prose judge, never the whole-report call (Done when 1)",
    (r["rc"], kinds(r)), (0, ["FIND PASS"] * 3 + ["CONFIRM CALL", "ANSWERING JUDGE", "PROSE JUDGE"]))
chk("order: the strip and counts are units-verdict's (a kept skill with a confirmed conflict)",
    (STRIP.search(r["text"]) and STRIP.search(r["text"]).group(1), "\u26d4 **1** conflicts" in r["text"], "\U0001F7E9 **1** keep" in r["text"]), ("\U0001F7E8 INSTALL WITH CHANGES", True, True))
chk("order: the report has the strip and the seven fit cards", [n for n in re.findall(r"^<details><summary>\S+ <b>(.*?)</b>", r["text"], re.M) if n in ("Why this verdict", "Conflicts", "Already covered", "Keep", "Dropped", "Do this", "Proposed rules patch")],
    ["Why this verdict", "Conflicts", "Already covered", "Keep", "Dropped", "Do this", "Proposed rules patch"])
chk("order: the units, answers and prose are kept beside the report", [f for f in ("report.units.json", "report.answers.json", "report.verdict.json", "report.prose.json") if f in r["side_left"]], ["report.units.json", "report.answers.json", "report.verdict.json", "report.prose.json"])
r = run("units-noop", extra=("--units",), units="units-install")
chk("--units stays accepted and changes nothing: same calls, exit 0", (r["rc"], kinds(r)), (0, ["FIND PASS"] * 3 + ["ANSWERING JUDGE", "PROSE JUDGE"]))
u = run("usage", extra=("--bogus",), fake_body=NO_CLAUDE)
chk("--units is a no-op, said in the usage line", "--units is a no-op" in u["out"], True)
r = run("prose-states", units="units-install", fake_env=dict(FAKE_PROSE="states"))
chk("prose: a text that states its own verdict and counts changes neither strip nor counts, and vet does not refuse (Done when 3)",
    (r["rc"], STRIP.search(r["text"]).group(1) if STRIP.search(r["text"]) else None, "\u26d4 **0** conflicts" in r["text"], "99 conflicts" in r["text"].split("<details>")[0]), (0, "\U0001F7E9 INSTALL", True, False))
p_ = first(r, "PROSE JUDGE")
chk("prose: the judge gets the computed verdict, counts and records, and is asked for why, do_this and patch only",
    ("INSTALL" in p_, '"counts"' in p_, "u1" in p_, all(w in p_ for w in ("why", "do_this", "patch")), "banner" in p_.lower()), (True, True, True, True, False))
a_ = first(r, "ANSWERING JUDGE")
chk("answering judge: asked for covered_by, held_in and star; no banner, counts or tool run asked of it",
    (all(w in a_ for w in ("covered_by", "held_in", "star")), "banner" in a_.lower(), "units-verdict" in a_, "units-confirm" in a_), (True, False, False, False))
r = run("confirm-fields", units="units-install", finds="one", confirm="yes")
c = first(r, "CONFIRM CALL")
chk("confirm: the call asks for hard_stop and sees the reader file's label and heading", ("hard_stop" in c, "rules/safety.md" in c, "Safety: hard stops" in c), (True, True, True))
r = run("hardstop", units="units-install", finds="one", confirm="yes", fake_env=dict(FAKE_HARDSTOP="0"))
cardtext = lambda r, name: re.search(r"<b>" + name + r"</b>.*?\n</details>", r["text"], re.S).group(0) if re.search(r"<b>" + name + r"</b>", r["text"]) else ""
chk("confirm: a conflict confirmed with hard_stop false is drawn \U0001F7E7 in the Conflicts card, not \U0001F7E5", ("| \U0001F7E7 |" in cardtext(r, "Conflicts"), "| \U0001F7E5 |" in cardtext(r, "Conflicts")), (True, False))
r = run("hardstop-yes", units="units-install", finds="one", confirm="yes")
chk("confirm: hard_stop true is \U0001F7E5 in the Conflicts card, with the file it is held in", ("| \U0001F7E5 |" in cardtext(r, "Conflicts"), "| rules/safety.md |" in cardtext(r, "Conflicts")), (True, True))
r = run("header", units="units-install")
lines = r["text"].split("\n")
chk("header: vet writes the title and the header line itself, in the form --check reads", (lines[0], bool(re.match(r"^`\d{4}-\d\d-\d\d` \u00b7 neckbeard \S+ \u00b7 demo 1.0.0", lines[2]))), ("# \U0001F50D demo 1.0.0 \u00b7 how it affects you, what it adds, where it takes a position \u00b7 against the sample reader", True))
chk("header: Baseline, the Verdict is relative line and Rule files sit inside Why this verdict", ("<b>Why this verdict</b>" in r["text"] and r["text"].find("Baseline: ") > r["text"].find("<b>Why this verdict</b>"), "Verdict is relative to the [sample reader]" in r["text"], "<details><summary><b>Rule files</b></summary>" in r["text"]), (True, True, True))


sys.exit(vet_harness.summary("test_vet_report"))
