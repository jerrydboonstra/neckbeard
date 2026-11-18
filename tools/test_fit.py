#!/usr/bin/env python3
"""tools/fit, the fit report's verdict strip and seven fit cards (verdict-stability-rules, Done when 2): a golden test on a fixed
`units-verdict --json` and fixed prose, the strip's colour for each verdict, a hostile prose text, a report with nothing in its cards.
Split from tools/test_vet.py to stay under the test-module size cap. The fixtures are in tools/fixtures/fit/.

    python3 tools/test_fit.py
"""
import json, os, re, shutil, subprocess, sys, tempfile

import vet_harness
from vet_harness import *

FIT = os.path.join(HERE, "fit")
FX = os.path.join(HERE, "fixtures", "fit")
def fit(*args, verdict="verdict.json", prose="prose.json"):
    p = subprocess.run([sys.executable, FIT, os.path.join(FX, verdict), os.path.join(FX, prose), *args], capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr
FITARGS = ("--label", "the sample reader", "--target", "demo", "--verdict-text", "Verdict is relative to the sample reader.", "--baseline", os.path.join(FX, "baseline.md"))
rc, out, err = fit(*FITARGS)
chk("fit golden: a fixed units-verdict --json and fixed prose print the strip and the seven cards, byte for byte", (rc, out == open(os.path.join(FX, "expected.md"), encoding="utf-8").read()), (0, True))
if out != open(os.path.join(FX, "expected.md"), encoding="utf-8").read():
    import difflib
    print("".join(list(difflib.unified_diff(open(os.path.join(FX, "expected.md"), encoding="utf-8").read().splitlines(1), out.splitlines(1)))[:40]))
chk("fit golden: the seven cards are in mock-up v2's order", re.findall(r"^<details><summary>\S+ <b>(Why this verdict|Conflicts|Already covered|Keep|Dropped|Do this|Proposed rules patch)</b>", out, re.M),
    ["Why this verdict", "Conflicts", "Already covered", "Keep", "Dropped", "Do this", "Proposed rules patch"])
v = json.load(open(os.path.join(FX, "verdict.json")))
for verdict_, mark in (("INSTALL", "\U0001F7E9"), ("INSTALL WITH CHANGES", "\U0001F7E8"), ("COPY RULES, SKIP PLUGIN", "\U0001F7E8"), ("DON'T INSTALL", "\U0001F7E5")):
    alt = tempfile.mkdtemp()
    try:
        json.dump({**v, "verdict": verdict_}, open(os.path.join(alt, "v.json"), "w"))
        p = subprocess.run([sys.executable, FIT, os.path.join(alt, "v.json"), os.path.join(FX, "prose.json"), *FITARGS], capture_output=True, text=True)
        strip_line = p.stdout.split("\n")[0]
        chk("fit: the strip's colour for " + verdict_, strip_line.startswith("> **" + mark + " " + verdict_ + "**"), True)
    finally:
        shutil.rmtree(alt)
alt = tempfile.mkdtemp()
try:
    json.dump({**v, "verdict": "SKIP PLUGIN"}, open(os.path.join(alt, "v.json"), "w"))
    p = subprocess.run([sys.executable, FIT, os.path.join(alt, "v.json"), os.path.join(FX, "prose.json"), *FITARGS], capture_output=True, text=True)
    chk("fit: a verdict units-verdict cannot print is refused, exit 2, nothing on stdout", (p.returncode, p.stdout), (2, ""))
finally:
    shutil.rmtree(alt)
rc, out, err = fit(*FITARGS, prose="prose-hostile.json")
chk("fit: a hostile prose text (</details>, </summary>, a | and a newline) opens and closes the seven cards and the Rule files block, no more, and comes out escaped",
    (rc, out.count("<details>"), out.count("</details>"), "&lt;/details>" in out, "&lt;/summary>" in out), (0, 8, 8, True, True))
rc, out, err = fit(*FITARGS, verdict="verdict-empty.json")
chk("fit: a report with nothing kept, covered or in conflict still prints all seven cards, Conflicts, Already covered and Keep each saying None",
    (rc, re.findall(r"^<details><summary>\S+ <b>(Why this verdict|Conflicts|Already covered|Keep|Dropped|Do this|Proposed rules patch)</b>", out, re.M), out.count("\nNone.\n")),
    (0, ["Why this verdict", "Conflicts", "Already covered", "Keep", "Dropped", "Do this", "Proposed rules patch"], 3))


sys.exit(vet_harness.summary("test_fit"))
