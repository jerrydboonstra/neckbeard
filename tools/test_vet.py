#!/usr/bin/env python3
"""tools/vet, the headless gallery method, run end to end against a fake `claude`: the --units prototype, part 1, the
report checks, --facts, --reader, the badge and report-check. The judge and login checks are in tools/test_vet_judge.py;
the fake `claude` and the helpers both share are in tools/vet_harness.py.

    python3 tools/test_vet.py
"""
import json, os, re, shutil, subprocess, sys, tempfile

import vet_harness
from vet_harness import *


# 0. --units (prototype): the verdict comes from the per-unit answers, and the banner must carry it
r = run("units", extra=("--units",), units="units-install")
chk("units: answers that compute INSTALL, banner INSTALL: exit 0", r["rc"], 0)
chk("units: the judge got the unit list and the written tests", "UNITS PROTOTYPE" in judge(r)[0]["prompt"] and "new-standing" in judge(r)[0]["prompt"], True)
r = run("units-mismatch", extra=("--units",), units="units-mismatch")
chk("units: banner INSTALL but answers compute COPY RULES: refused", (r["rc"], "computed verdict is COPY RULES" in r["out"]), (1, True))
r = run("units-missing", extra=("--units",), units="units-none")
chk("units: an answer missing for a unit: refused", (r["rc"], "answers were refused" in r["out"]), (1, True))
# 0a. verdict-stability-rules: the units path is the default; the verdict and counts come from code
STRIP = re.compile(r"^> \*\*(.+?)\*\* \u00b7 (.*?)  $", re.M)
KINDS = ("FIND PASS", "CONFIRM CALL", "ANSWERING JUDGE", "PROSE JUDGE", "Vet one plugin")
def first(r, word):
    return next(iter(isolated(r, word)), {"prompt": ""})["prompt"]
def kinds(r):
    return [next((k for k in KINDS if k in c["prompt"]), "?") for c in r["calls"] if "single word ok" not in c["prompt"]]
r = run("order", units="units-install", finds="one", confirm="yes")
chk("order: with no --units the calls are three find passes, one confirm, the answering judge, then the prose judge, and never the whole-report call (Done when 1)",
    (r["rc"], kinds(r)), (0, ["FIND PASS"] * 3 + ["CONFIRM CALL", "ANSWERING JUDGE", "PROSE JUDGE"]))
chk("order: the report's strip and counts are units-verdict's (a kept skill with a confirmed conflict is INSTALL WITH CHANGES, one conflict, one kept)",
    (STRIP.search(r["text"]) and STRIP.search(r["text"]).group(1), "\u26d4 **1** conflicts" in r["text"], "\U0001F7E9 **1** keep" in r["text"]), ("\U0001F7E8 INSTALL WITH CHANGES", True, True))
chk("order: the report has the strip and the seven fit cards", [n for n in re.findall(r"^<details><summary>\S+ <b>(.*?)</b>", r["text"], re.M) if n in ("Why this verdict", "Conflicts", "Already covered", "Keep", "Dropped", "Do this", "Proposed rules patch")],
    ["Why this verdict", "Conflicts", "Already covered", "Keep", "Dropped", "Do this", "Proposed rules patch"])
chk("order: the units, answers and prose are kept beside the report", [f for f in ("report.units.json", "report.answers.json", "report.prose.json") if f in r["side_left"]], ["report.units.json", "report.answers.json", "report.prose.json"])
r = run("units-noop", extra=("--units",), units="units-install")
chk("--units stays accepted and changes nothing: same calls, exit 0", (r["rc"], kinds(r)), (0, ["FIND PASS"] * 3 + ["ANSWERING JUDGE", "PROSE JUDGE"]))
u = run("usage", extra=("--bogus",), fake_body=NO_CLAUDE)
chk("--units is a no-op, said in the usage line", "--units is a no-op" in u["out"], True)
r = run("prose-states", units="units-install", fake_env=dict(FAKE_PROSE="states"))
chk("prose: a judge text that states its own verdict and counts changes neither the strip nor the counts, and vet does not refuse (Done when 3)",
    (r["rc"], STRIP.search(r["text"]).group(1) if STRIP.search(r["text"]) else None, "\u26d4 **0** conflicts" in r["text"], "99 conflicts" in r["text"].split("<details>")[0]), (0, "\U0001F7E9 INSTALL", True, False))
p_ = first(r, "PROSE JUDGE")
chk("prose: the prose judge gets the computed verdict, counts and unit records, and is asked for why, do_this and patch only",
    ("INSTALL" in p_, '"counts"' in p_, "u1" in p_, all(w in p_ for w in ("why", "do_this", "patch")), "banner" in p_.lower()), (True, True, True, True, False))
a_ = first(r, "ANSWERING JUDGE")
chk("answering judge: asked for covered_by, held_in and star; no verdict banner, counts or tool run asked of it",
    (all(w in a_ for w in ("covered_by", "held_in", "star")), "banner" in a_.lower(), "units-verdict" in a_, "units-confirm" in a_), (True, False, False, False))
r = run("confirm-fields", units="units-install", finds="one", confirm="yes")
c = first(r, "CONFIRM CALL")
chk("confirm: the call asks for hard_stop and sees the reader file's label and heading", ("hard_stop" in c, "rules/safety.md" in c, "Safety: hard stops" in c), (True, True, True))
r = run("hardstop", units="units-install", finds="one", confirm="yes", fake_env=dict(FAKE_HARDSTOP="0"))
chk("confirm: a conflict confirmed with hard_stop false is drawn \U0001F7E7 in the Conflicts card, true \U0001F7E5", ("| \U0001F7E7 |" in r["text"], "| \U0001F7E5 |" in r["text"]), (True, False))
r = run("hardstop-yes", units="units-install", finds="one", confirm="yes")
chk("confirm: a conflict confirmed with hard_stop true is \U0001F7E5 and names the file it is held in", ("| \U0001F7E5 |" in r["text"], "| rules/safety.md |" in r["text"]), (True, True))
r = run("header", units="units-install")
lines = r["text"].split("\n")
chk("header: vet writes the title and the header line itself, in the form --check reads", (lines[0], bool(re.match(r"^`\d{4}-\d\d-\d\d` \u00b7 neckbeard \S+ \u00b7 demo 1.0.0", lines[2]))), ("# \U0001F50D demo 1.0.0 \u00b7 vetted against the sample reader", True))
chk("header: the Baseline sits inside Why this verdict, with the Verdict is relative line and the Rule files block", ("<b>Why this verdict</b>" in r["text"] and r["text"].find("Baseline: ") > r["text"].find("<b>Why this verdict</b>"), "Verdict is relative to the [sample reader]" in r["text"], "<details><summary>Rule files</summary>" in r["text"]), (True, True, True))

# 0a2. tools/fit renders units-verdict --json and the prose into the strip and seven fit cards (Done when 2)
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
for verdict_, mark in (("INSTALL", "\U0001F7E9"), ("INSTALL WITH CHANGES", "\U0001F7E8"), ("COPY RULES, SKIP PLUGIN", "\U0001F7E8"), ("SKIP PLUGIN", ""), ("DON'T INSTALL", "\U0001F7E5")):
    alt = tempfile.mkdtemp()
    try:
        json.dump({**v, "verdict": verdict_}, open(os.path.join(alt, "v.json"), "w"))
        p = subprocess.run([sys.executable, FIT, os.path.join(alt, "v.json"), os.path.join(FX, "prose.json"), *FITARGS], capture_output=True, text=True)
        first = p.stdout.split("\n")[0]
        chk("fit: the strip's colour for " + verdict_, first.startswith("> **" + (mark + " " if mark else "") + verdict_ + "**"), first)
    finally:
        shutil.rmtree(alt)
rc, out, err = fit(*FITARGS, prose="prose-hostile.json")
chk("fit: a hostile prose text (</details>, a | and a newline) closes no card early and breaks no table", (rc, out.count("<details>"), out.count("</details>")), (0, 9, 9))
rc, out, err = fit(*FITARGS, verdict="verdict-empty.json")
chk("fit: a report with nothing kept, covered or in conflict still prints seven cards, each saying None", (rc, len(re.findall(r"^<details><summary>\S+ <b>(?:Conflicts|Already covered|Keep)</b>", out, re.M)), out.count("\nNone.\n")), (0, 3, 3))

# 0b. --units pools three find passes and confirms each candidate alone; only confirmed conflicts count
r = run("units-find-none", extra=("--units",), units="units-install")
chk("pool: three find passes, no candidates, no confirm call, exit 0", (r["rc"], len(isolated(r, "FIND PASS")), len(isolated(r, "CONFIRM CALL"))), (0, 3, 0))
r = run("units-confirmed", extra=("--units",), units="units-install", finds="one", confirm="yes")
chk("pool: the same candidate in three passes is confirmed once", len(isolated(r, "CONFIRM CALL")), 1)
chk("confirm: a confirmed conflict counts, so INSTALL becomes INSTALL WITH CHANGES and the banner is refused",
    (r["rc"], "computed verdict is INSTALL WITH CHANGES" in r["out"]), (1, True))
c = isolated(r, "CONFIRM CALL")[0]
chk("confirm: the call sees the sentence and the written test, not the units or the dossier",
    ("Always run the tests before you commit." in c["prompt"], "Never run anything destructive without my explicit go-ahead" in c["prompt"], "permits, with no limit" in c["prompt"], "UNITS:" in c["prompt"], "dossier" in c["prompt"].lower()),
    (True, True, True, False, False))
chk("confirm: the reader rule is the reader's own text; the finder's argument never reaches the call",
    ("FINDER ARGUMENT" in c["prompt"], "rules/safety.md: 1. **Never run anything destructive" in c["prompt"]), (False, True))
chk("confirm: the call is allowed no tools", c["args"][c["args"].index("--allowedTools") + 1], "")
r = run("units-rejected", extra=("--units",), units="units-install", finds="one", confirm="no")
chk("confirm: a rejected candidate does not count, exit 0", (r["rc"], "0 of 1 candidates confirmed" in r["out"]), (0, True))
r = run("units-flaky", extra=("--units",), units="units-install", finds="one", confirm="flaky")
chk("confirm: a call with no JSON is retried once, and the second answer counts", (len(isolated(r, "CONFIRM CALL")), "computed verdict is INSTALL WITH CHANGES" in r["out"]), (2, True))
r = run("units-garbage", extra=("--units",), units="units-install", finds="one", confirm="garbage")
chk("confirm: two calls with no JSON fail the vet and show what was said", (r["rc"], "gave no usable answer: 'no json here" in r["out"]), (1, True))
r = run("units-late", extra=("--units",), units="units-install", finds="late", confirm="yes")
chk("pool: a candidate found in one pass of three is still confirmed", (len(isolated(r, "CONFIRM CALL")), "computed verdict is INSTALL WITH CHANGES" in r["out"]), (1, True))
r = run("units-invented", extra=("--units",), units="units-install", finds="invented", confirm="yes")
chk("pool: a quote that is not in the unit is dropped before any confirm call", (r["rc"], len(isolated(r, "CONFIRM CALL"))), (0, 0))
chk("cost: the vet prints calls and dollars", "units cost: 3 find and confirm calls, $0.03" in r["out"], True)
r = run("no-units")
chk("without --units the prompt has no unit list", "UNITS PROTOTYPE" in judge(r)[0]["prompt"], False)

# 0c. part 1 ("What it adds", tools/part1) goes in the report immediately before At a glance, and nothing else moves
r = run("part1", commit=True)
t = re.sub(r"\n`\d{4}-\d\d-\d\d` \u00b7 neckbeard [^\n]*\n\nBaseline: .*?</details>\n", "", r["text"], count=1, flags=re.S)   # the baseline block is tools/vet's own, tested below
head = "# 🔍 demo 1.0.0 · vetted against the sample reader\n\n> ## 🟩 INSTALL · add the one skill\n> Fine.\n\n"
glance = "## ⚡ At a glance\n\nOne line.\n"
sec, _, rest = t[len(head):].partition(glance)
chk("part1: exit 0, the report is the judge's text with one section in front of At a glance",
    (r["rc"], t.startswith(head), sec.startswith("## What it adds\n"), sec.count("## What it adds\n"), rest), (0, True, True, 1, ""))
chk("part1: the section ends with a blank line, and holds the six cards", (sec.endswith("\n\n"), all(re.search(r"^<details><summary>[\U0001F7E2\U0001F7E1\U0001F534] <b>" + h + r"</b>", sec, re.M) for h in ("Injects", "Hooks", "Subagents and commands", "State it may leave", "Reaches outside the session", "Source"))), (True, True))
chk("part1: the commit vet holds goes into the Source card", f"Commit: {r['sha']}" in sec and r["sha"] != "", True)
chk("part1: no reader rule or local path in the section", ("READER" in sec, os.path.realpath(r["target"]) in sec, "/tmp" in sec), (False, False, False))
r = run("part1-no-commit")
chk("part1: with no git commit the section says commit not given", "Commit: commit not given" in r["text"], True)
# a copy of vet with a tools/part1 that fails, or that prints a heading of its own: vet dies and says so
def vet_with_part1(script, **kw):
    fake = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(fake, "tools"))
        shutil.copy(VET, os.path.join(fake, "tools", "vet"))
        shutil.copy(os.path.join(HERE, "badge-logo"), os.path.join(fake, "tools", "badge-logo"))
        for link in ("skills", "examples", ".claude-plugin"):
            os.symlink(os.path.join(NB, link), os.path.join(fake, link))
        open(os.path.join(fake, "tools", "part1"), "w").write(script)
        os.chmod(os.path.join(fake, "tools", "part1"), 0o755)
        return run("part1-fake", vet=os.path.join(fake, "tools", "vet"), **kw)
    finally:
        shutil.rmtree(fake)


r = vet_with_part1("import sys\nsys.stderr.write('part1: cannot read a dossier\\n')\nsys.exit(2)\n")
chk("part1: when tools/part1 exits non-zero vet dies with 'part 1 could not be rendered' and part1's own message",
    (r["rc"], "part 1 could not be rendered" in r["out"], "part1: cannot read a dossier" in r["out"]), (1, True, True))
r = vet_with_part1("print('## What it adds\\n\\n## \\u26a1 At a glance')\n")
chk("part1: a section that holds the At a glance heading itself fails vet", (r["rc"], "At a glance" in r["out"]), (1, True))
r = run("part1-missing-heading", report="noglance")
chk("part1: a report with no At a glance heading fails vet, and the message names it", (r["rc"], "At a glance" in r["out"]), (1, True))

# 1. a web session: the judge logs in with the reader copy as its config folder
r = run("web")
chk("web: exit 0", r["rc"], 0)
chk("web: report written", r["report"], True)
chk("web: judge uses the reader", "judge: reader" in r["out"], True)
j = judge(r)
chk("web: one judge call", len(j), 1)
chk("web: judge may Edit", bool(j) and "Edit" in j[0]["args"][j[0]["args"].index("--allowedTools") + 1].split(","), True)
chk("web: judge config is a copy, not the checkout",
    bool(j) and j[0]["cfg"] != "" and not os.path.realpath(j[0]["cfg"]).startswith(os.path.realpath(NB)), True)
chk("web: judge starts outside the target", bool(j) and not os.path.realpath(j[0]["cwd"]).startswith(os.path.realpath(r["target"])), True)
chk("web: examples/reader untouched", r["reader_untouched"], True)
chk("web: temp folder removed", r["temp_left"], [])
chk("web: title names the sample reader", r["title"], "# 🔍 demo 1.0.0 · vetted against the sample reader")

header = lambda r: next(l for l in judge(r)[0]["prompt"].splitlines() if l.startswith("Header line"))
chk("web: header names the target plainly", header(r).endswith("· demo 1.0.0"), True)

# 1b. a target with a GitHub origin: the header links it once, and the ssh form becomes https
r = run("remote", remote="git@github.com:someone/demo.git")
chk("remote: title uses the repo's short name", r["title"], "# 🔍 demo 1.0.0 · vetted against the sample reader")
chk("remote: header links the repo once", "· [someone/demo](https://github.com/someone/demo) 1.0.0" in header(r)
    and header(r).count("https://github.com/someone/demo") == 1, True)

# 1c. --repo names the public repo over a private origin, and --note leads the reader paragraph
r = run("repo", remote="https://github.com/someone/demo-dev.git",
        extra=("--repo", "https://github.com/someone/demo", "--note", "Same author, so a self-vetting."))
chk("repo: header names the public repo", "· [someone/demo](https://github.com/someone/demo) 1.0.0" in header(r), True)
chk("repo: note leads the paragraph", '"Same author, so a self-vetting. Verdict is relative' in judge(r)[0]["prompt"], True)

# 2. a Mac: the reader copy can't log in, so the judge falls back to the caller's config and says so
r = run("mac", login="default")
chk("mac: exit 0", r["rc"], 0)
chk("mac: falls back to own config", "judge: own" in r["out"] and "can't log in" in r["out"], True)
j = judge(r)
chk("mac: judge has no config folder", bool(j) and j[0]["cfg"], "")

# 2b. bash 3.2 (the Mac's /bin/bash, what `env bash` finds without Homebrew): the judge's empty config array is expanded under set -u
# (vet-bash32-empty-cfg). Where /bin/bash is 3.2 this is the failing case on an unfixed vet; elsewhere it still has to pass.
if os.path.exists("/bin/bash"):
    r = run("bash32-own", login="default", extra=("--judge", "own"), shell="/bin/bash")
    chk("bash 3.2: --judge own runs the judge past the empty config array, exit 0, report written",
        (r["rc"], r["report"], len(judge(r)), "unbound variable" in r["out"]), (0, True, 1, False))
    r = run("bash32-units", login="default", units="units-install", extra=("--units", "--judge", "own"), shell="/bin/bash")
    chk("bash 3.2: --units --judge own gets its isolated calls past the empty config array too",
        (r["rc"], len(isolated(r, "FIND PASS")), "unbound variable" in r["out"]), (0, 3, False))

# 2c. no other empty-array expansion under set -u in the bash scripts of tools/ (vet-repeat's "${reports[@]}" is behind its own
# count check, at least two); a new one needs the ${a[@]+"${a[@]}"} form or the same guard
bare = []
for name in sorted(os.listdir(os.path.dirname(VET))):
    path = os.path.join(os.path.dirname(VET), name)
    if os.path.isfile(path) and not name.endswith((".py", ".md", ".txt")):
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = f.read().split("\n")
        if lines and lines[0].startswith("#!") and "bash" in lines[0] and any(l.strip() == "set -u" for l in lines):
            bare += [(name, m) for l in lines if not l.lstrip().startswith("#") for m in re.findall(r'(?<![+])"\$\{(\w+)\[@\]\}"', l)]
chk("no unguarded empty-array expansion under set -u in tools/", sorted(bare), [("vet-repeat", "reports")])

# 3. --judge reader on a Mac: no fallback, so the run fails
r = run("forced", login="default", uname="Darwin", extra=("--judge", "reader"))
chk("forced reader: exit 1, no report, one line naming the reason and --judge own", (r["rc"], r["report"], "--judge reader can't log in" in r["out"], "reader mode logs in only on Linux" in r["out"], "--judge own" in r["out"]), (1, False, True, True, True))

# 4. the judge writes no report
r = run("none", report="none")
chk("no report: exit 1", r["rc"], 1)
chk("no report: says so", "wrote no report" in r["out"], True)

# 5. a report with no verdict banner
r = run("noverdict", report="noverdict")
chk("no verdict: exit 1", r["rc"], 1)

# 6. a report that names the target's local path
r = run("leak", report="leak")
chk("leak: exit 1", r["rc"], 1)
chk("leak: says so", "names a local path" in r["out"], True)

# 7. --check, the staleness check a plugin's CI runs: python3 only, no claude on PATH
def check(header, version="1.0.0"):
    tmp = tempfile.mkdtemp()
    try:
        bindir = os.path.join(tmp, "bin"); os.mkdir(bindir)
        for tool in ("bash", "python3"):
            os.symlink(shutil.which(tool), os.path.join(bindir, tool))
        target = os.path.join(tmp, "demo")
        os.makedirs(os.path.join(target, ".claude-plugin"))
        json.dump({"name": "demo", "version": version}, open(os.path.join(target, ".claude-plugin", "plugin.json"), "w"))
        report = os.path.join(tmp, "report.md")
        open(report, "w").write("# 🔍 demo · vetted against the sample reader\n\n> ## 🟩 INSTALL · fine\n\n" + header + "\n")
        env = {"PATH": bindir, "HOME": tmp}
        p = subprocess.run([VET, "--check", report, target], env=env, capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr
    finally:
        shutil.rmtree(tmp)

linked = "`2026-10-04` · neckbeard 1.12.9 · [someone/demo](https://github.com/someone/demo) 1.0.0 @ `abc1234`"
rc, out = check(linked)
chk("check: matching version passes with no claude", (rc, "current (1.0.0)" in out), (0, True))
rc, out = check("`2026-10-04` · neckbeard 1.12.9 · demo 1.0.0", version="1.1.0")
chk("check: older report fails", (rc, "vets 1.0.0, but" in out and "is 1.1.0" in out), (1, True))
rc, out = check("`2026-10-04` · neckbeard 1.12.9 · demo 1.0.0")
chk("check: plain name, no commit passes", rc, 0)
rc, out = check("Vetted some time ago.")
chk("check: no header fails", (rc, "no header line" in out), (1, True))

# 8. --facts: the report with no reader, no verdict and no model call
r = run("facts", extra=("--facts",), fake_body=NO_CLAUDE)
chk("facts: written, exit 0, claude never called", (r["rc"], r["report"], r["calls"]), (0, True, []))
chk("facts: title line", r["title"], "# \U0001F50D demo 1.0.0 \u00b7 what it adds")
chk("facts: no verdict, no reader", [w in r["text"] for w in ("vetted against", "At a glance", "sample reader", "\U0001F7E5", "\U0001F7E7", "\U0001F7E8", "\U0001F7E9")], [False] * 7)
chk("facts: closing line", r["text"].rstrip("\n").endswith("No reader's rules were read: this report lists facts only and carries no verdict."), True)
chk("facts: carries part 1", "\n## What it adds\n" in r["text"], True)
chk("facts: temp folder removed", r["temp_left"], [])
r2 = run("facts-again", extra=("--facts",), fake_body=NO_CLAUDE)
chk("facts: twice on one day, byte-identical", (r["report"], r2["report"], r["text"] == r2["text"]), (True, True, True))
# claude need not be on PATH at all: a PATH holding only the tools vet itself uses
def facts_without_claude():
    tmp = tempfile.mkdtemp()
    try:
        bindir = os.path.join(tmp, "bin"); os.mkdir(bindir)
        for tool in ("bash", "python3", "git", "sed", "date", "grep", "mktemp", "dirname", "basename", "mv", "rm", "mkdir", "cat", "cp", "tr", "head", "sort", "env"):
            if shutil.which(tool):
                os.symlink(shutil.which(tool), os.path.join(bindir, tool))
        target = os.path.join(tmp, "demo"); os.makedirs(os.path.join(target, ".claude-plugin"))
        json.dump({"name": "demo", "version": "1.0.0"}, open(os.path.join(target, ".claude-plugin", "plugin.json"), "w"))
        out = os.path.join(tmp, "out.md")
        p = subprocess.run([VET, target, out, "--facts"], env={"PATH": bindir, "HOME": tmp, "TMPDIR": tmp}, capture_output=True, text=True)
        return p.returncode, os.path.exists(out), "claude" in (p.stdout + p.stderr)
    finally:
        shutil.rmtree(tmp)
chk("facts: runs with no claude on PATH", facts_without_claude(), (0, True, False))
def facts_check_text(text, version):
    tmp = tempfile.mkdtemp()
    try:
        target = os.path.join(tmp, "demo"); os.makedirs(os.path.join(target, ".claude-plugin"))
        json.dump({"name": "demo", "version": version}, open(os.path.join(target, ".claude-plugin", "plugin.json"), "w"))
        report = os.path.join(tmp, "report.md"); open(report, "w", encoding="utf-8").write(text)
        return subprocess.run([VET, "--check", report, target], capture_output=True, text=True).returncode
    finally:
        shutil.rmtree(tmp)
def facts_check(version):
    tmp = tempfile.mkdtemp()
    try:
        target = os.path.join(tmp, "demo"); os.makedirs(os.path.join(target, ".claude-plugin"))
        json.dump({"name": "demo", "version": version}, open(os.path.join(target, ".claude-plugin", "plugin.json"), "w"))
        report = os.path.join(tmp, "report.md"); open(report, "w", encoding="utf-8").write(r["text"])
        return subprocess.run([VET, "--check", report, target], capture_output=True, text=True).returncode
    finally:
        shutil.rmtree(tmp)
chk("facts: --check passes on the same version", facts_check("1.0.0"), 0)
chk("facts: --check fails on a new version", facts_check("1.1.0"), 1)
for flags in (["--units"], ["--judge", "reader"], ["--model", "opus"], ["--note", "x"]):
    u = run("facts-usage", extra=("--facts", *flags), fake_body=NO_CLAUDE)
    chk("facts with " + flags[0] + ": usage", (u["rc"], "[--facts]" in u["out"], u["report"]), (2, True, False))
u = run("facts-repo", extra=("--facts", "--repo", "https://github.com/someone/demo"), fake_body=NO_CLAUDE)
chk("facts: --repo still applies", (u["rc"], "[someone/demo](https://github.com/someone/demo) 1.0.0" in u["text"]), (0, True))
u = run("facts-rules", extra=("--facts",), fake_body=NO_CLAUDE, rules_above=True)
chk("facts: a rule file in force is refused, naming it", (u["rc"], u["report"], "the dossier read:" in u["out"] and "CLAUDE.md" in u["out"]), (1, False, True))
# the group's guard: one header writer, byte for byte
j = run("judged-header", commit=True)
f = run("facts-header", commit=True, extra=("--facts",), fake_body=NO_CLAUDE)
want = [l.split("Header line to use: ", 1)[1] for c in judge(j) for l in c["prompt"].split("\n") if l.startswith("Header line to use: ")]
got = [l for l in f["text"].split("\n") if l.startswith("`") and " \u00b7 neckbeard " in l]
chk("facts and judged header lines are equal", (len(want), got), (1, want))
chk("judged title still says vetted", j["title"], "# \U0001F50D demo 1.0.0 \u00b7 vetted against the sample reader")

# 9. --reader and the baseline line
BASELINE = re.compile(r"^Baseline: (.+) \u00b7 (\d+) rule files \u00b7 (\d+) bytes \u00b7 sha256 ([0-9a-f]{12})$", re.M)

r = run("baseline-default")
m = BASELINE.search(r["text"])
chk("baseline: default reader names the sample reader, 4 rule files, a 12-hex fingerprint", (m.group(1), m.group(2)) if m else None, ("the sample reader", str(len(reader_files()))))
chk("baseline: byte total is the files' own", int(m.group(3)) if m else None, sum(os.path.getsize(os.path.join(DEFAULT_READER, f)) for f in reader_files()))
chk("baseline: the file list is a details block of relative paths", [w in r["text"] for w in ("<details><summary>Rule files</summary>", "- `rules/safety.md`", "</details>")], [True] * 3)
chk("baseline: the title still says the sample reader", r["title"], "# \U0001F50D demo 1.0.0 \u00b7 vetted against the sample reader")

tmp = tempfile.mkdtemp()
try:
    os.makedirs(os.path.join(tmp, "one")); os.makedirs(os.path.join(tmp, "two", "deeper"))
    a = reader_copy(os.path.join(tmp, "one"), "readerdir")
    b = reader_copy(os.path.join(tmp, "two", "deeper"), "readerdir")
    c = reader_copy(tmp, "changed", edit=b" ")
    ra, rb, rc_ = (run("fp", extra=("--reader", d)) for d in (a, b, c))
    fp = lambda x: (BASELINE.search(x["text"]) or [None] * 5)[4]
    chk("reader: two paths, one fingerprint", (fp(ra) is not None, fp(ra) == fp(rb)), (True, True))
    chk("reader: one byte changed, a different fingerprint", fp(rc_) not in (None, fp(ra)), True)
    chk("reader: label is the folder's basename", BASELINE.search(ra["text"]).group(1) if BASELINE.search(ra["text"]) else None, "readerdir")
    chk("reader: title names the label", ra["title"], "# \U0001F50D demo 1.0.0 \u00b7 vetted against readerdir")
    leaks = [x for d in (a, os.path.dirname(a)) for x in (d, os.path.realpath(d))]   # macOS prints /private/var for /var
    chk("reader: no absolute path of the folder in the report", ([x for x in leaks if x in ra["text"] + ra["out"]], ra["rc"]), ([], 0))
    # a judge that wrote its header line: the Baseline goes right under it, and --check reads the report
    h = run("judge-header", extra=("--reader", a), report="header")
    hl = h["text"].split("\n")
    chk("reader: the Baseline block sits under the judge's header line", (h["rc"], hl[2].startswith("`") and " \u00b7 neckbeard " in hl[2], hl[3], hl[4].startswith("Baseline: readerdir \u00b7 4 rule files")), (0, True, "", True))
    chk("reader: that report carries one header line and one Baseline", (sum(1 for l in hl if " \u00b7 neckbeard " in l), sum(1 for l in hl if l.startswith("Baseline: "))), (1, 1))
    chk("reader: --check passes on it", facts_check_text(h["text"], "1.0.0"), 0)
    # a non-default folder that happens to be named "the sample reader" is still not the default
    os.makedirs(os.path.join(tmp, "named"))
    named = reader_copy(os.path.join(tmp, "named"), "the sample reader")
    rn = run("named-like-default", extra=("--reader", named))
    pn = [l for c in judge(rn) for l in c["prompt"].split("\n") if l.startswith("Put this paragraph")]
    chk("reader: a folder named like the default gets the non-default paragraph and citation", (len(pn), "](" not in pn[0], "examples/reader/..." in "\n".join(c["prompt"] for c in judge(rn)), "rule files (fingerprint %s)" % fp(rn) in pn[0]), (1, True, False, True))
    # a path-only change (one rule file renamed) changes the fingerprint too
    moved = reader_copy(tmp, "moved")
    os.rename(os.path.join(moved, "rules", "safety.md"), os.path.join(moved, "rules", "safe.md"))
    chk("reader: a renamed rule file, a different fingerprint", fp(run("fp-moved", extra=("--reader", moved))) not in (None, fp(ra)), True)
    # the default named on the command line is still the sample reader
    d = run("explicit-default", extra=("--reader", DEFAULT_READER))
    chk("reader: --reader examples/reader keeps the sample reader label", (d["title"], (BASELINE.search(d["text"]) or [0, 0])[1], fp(d) == (BASELINE.search(r["text"]) or [0] * 5)[4]), ("# \U0001F50D demo 1.0.0 \u00b7 vetted against the sample reader", "the sample reader", True))
    # vet --check reads a judged report that carries the Baseline block
    chk("reader: --check passes on a judged report with a Baseline block", facts_check_text(ra["text"], "1.0.0"), 0)
    prompt = [l for c in judge(ra) for l in c["prompt"].split("\n") if l.startswith("Put this paragraph")]
    want = "Verdict is relative to readerdir's 4 rule files (fingerprint %s), not a judgment of the plugin's quality." % fp(ra)
    chk("reader: the verdict paragraph names the label, count and fingerprint, and links nothing", (len(prompt), want in prompt[0] and "](" not in prompt[0]), (1, True))
    default_prompt = [l for c in judge(r) for l in c["prompt"].split("\n") if l.startswith("Put this paragraph")]
    chk("reader: the default verdict paragraph is unchanged", "Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment" in default_prompt[0], True)
    # a reader with no rule files: the facts report, no claude call, exit 0
    empty = os.path.join(tmp, "emptyreader"); os.mkdir(empty)
    open(os.path.join(empty, "notes.txt"), "w").write("not a rule file\n")
    e = run("empty-reader", extra=("--reader", empty), fake_body=NO_CLAUDE)
    chk("reader: no rule files gives the facts report, no claude call, exit 0", (e["rc"], e["calls"], e["title"], "no rule files" in e["out"]), (0, [], "# \U0001F50D demo 1.0.0 \u00b7 what it adds", True))
    chk("reader: that report has no baseline and no verdict", ("Baseline:" in e["text"], "vetted against" in e["text"]), (False, False))
    chk("reader: a missing folder is an error", run("no-reader", extra=("--reader", os.path.join(tmp, "nope")))["rc"], 1)
    chk("reader: an empty --reader is a usage error", run("empty-arg", extra=("--reader", ""), fake_body=NO_CLAUDE)["rc"], 2)
    chk("reader: --facts with --reader is a usage error", run("facts-reader", extra=("--facts", "--reader", a), fake_body=NO_CLAUDE)["rc"], 2)
finally:
    shutil.rmtree(tmp)

# 10. the badge line: stdout's last line when --facts writes OUT
LOGO = open(os.path.join(HERE, "badge-logo"), encoding="utf-8").read().strip()
def badge_of(res):
    lines = [l for l in res["stdout"].split("\n") if l.strip()]
    return lines[-1] if lines else ""
def big_skill(target):   # a SKILL.md past the read limit: the skills section is read in part
    open(os.path.join(target, "skills", "demo", "SKILL.md"), "a").write("x" * 250000 + "\n")
def bad_mcp(target):     # an .mcp.json that is not JSON: the mcp_servers section failed
    open(os.path.join(target, ".mcp.json"), "w").write("{not json")
for case, setup, state, colour in (("read", None, "read in full", "brightgreen"), ("partial", big_skill, "partly read", "yellow"), ("failed", bad_mcp, "something unread", "red")):
    b = run("badge-" + case, extra=("--facts",), fake_body=NO_CLAUDE, setup=setup)
    msg = "1.0.0%20%C2%B7%20" + state.replace(" ", "%20")
    want_url = "https://img.shields.io/badge/neckbeard-" + msg + "-" + colour + "?logo=" + LOGO
    chk("badge: " + case + " reads " + state + ", " + colour, (b["rc"], badge_of(b).startswith("[![neckbeard: 1.0.0 \u00b7 " + state + "](" + want_url + ")]")), (0, True))
    sec_ = b["text"].split("## What it adds\n", 1)[1].split("\nLoad timing is", 1)[0]
    summ_ = "".join(l for l in sec_.split("\n") if l.startswith("<details><summary>"))   # the legend line holds all three markers
    word_ = "something unread" if "\U0001F534" in summ_ else "partly read" if "\U0001F7E1" in summ_ else "read in full"
    chk("badge: " + case + ": the badge word equals the overall read state of the cards in the report it wrote", (state, word_, len(re.findall(r"<details><summary>[\U0001F7E2\U0001F7E1\U0001F534] <b>", sec_))), (state, state, 6))
    chk("badge: " + case + ": the cards hold no judgement square (\U0001F7E9\U0001F7E8\U0001F7E7\U0001F7E5)", [q in sec_ for q in "\U0001F7E9\U0001F7E8\U0001F7E7\U0001F7E5"], [False] * 4)
# inventory cannot yield a read hooks section with an untraced injected text (it marks that section partial), so the hsec
# rule that changes the badge word is shown here instead: vet's word is whatever `tools/part1 --read-state` prints, never its own
FAKE_P1 = ("import sys\nif sys.argv[1] == '--read-state':\n    print('%s')\n    sys.exit(0)\n"
           "print('## What it adds\\n\\n<details><summary>\\U0001F7E2 <b>Injects</b></summary>\\n\\n- x\\n\\n</details>\\n')\n")
for word_, colour_ in (("something unread", "red"), ("partly read", "yellow"), ("read in full", "brightgreen")):
    r = vet_with_part1(FAKE_P1 % word_, extra=("--facts",), fake_body=NO_CLAUDE)
    chk("badge: vet takes the word from `tools/part1 --read-state` (" + word_ + "), whatever the cards say",
        (r["rc"], "neckbeard: 1.0.0 \u00b7 " + word_ + "](" in badge_of(r), "-" + colour_ + "?logo=" in badge_of(r)), (0, True, True))
vet_src = open(VET, encoding="utf-8").read()
chk("badge: tools/vet computes no state from read_status itself: it holds neither `not-applicable` nor `\"failed\"`, and takes the word from tools/part1 --read-state", ("not-applicable" in vet_src, '"failed"' in vet_src, "--read-state" in vet_src), (False, False, True))
chk("badge: linked to OUT's path as given", badge_of(b).endswith("](" + b["outpath"] + ")"), True)
tmp = tempfile.mkdtemp()
try:
    os.makedirs(os.path.join(tmp, ".claude-plugin"))
    json.dump({"name": "demo", "version": "1.0.0"}, open(os.path.join(tmp, ".claude-plugin", "plugin.json"), "w"))
    rel = subprocess.run([VET, ".", "docs/neckbeard-report.md", "--facts"], cwd=tmp, capture_output=True, text=True)
    odd = subprocess.run([VET, ".", "my docs/r(1).md", "--facts"], cwd=tmp, capture_output=True, text=True)
    chk("badge: spaces and parens in OUT are escaped in the link", (odd.returncode, odd.stdout.rstrip("\n").endswith("](my%20docs/r%281%29.md)")), (0, True))
    chk("badge: a relative OUT stays relative in the link", (rel.returncode, rel.stdout.rstrip("\n").endswith("](docs/neckbeard-report.md)")), (0, True))
finally:
    shutil.rmtree(tmp)
chk("badge: the report path line moved to stderr", ("vet: facts report " in b["stdout"], "vet: facts report " in b["out"]), (False, True))
b = run("badge-escape", extra=("--facts",), fake_body=NO_CLAUDE, version="1.2.3-rc_1")
chk("badge: a version 1.2.3-rc_1 is escaped 1.2.3--rc__1", "badge/neckbeard-1.2.3--rc__1%20%C2%B7%20read%20in%20full-brightgreen?logo=" in badge_of(b), True)
chk("badge: the judged path prints no badge", "img.shields.io" in run("badge-judged")["stdout"], False)

# 11. make report-check: the tagged report must name the tagged version
def report_check(report_version, tag_after=False, at="`v1.2.0`"):
    tmp = tempfile.mkdtemp()
    try:
        for d in (".claude-plugin", "docs", "tools"):
            os.makedirs(os.path.join(tmp, d))
        shutil.copy(os.path.join(NB, "Makefile"), tmp)
        shutil.copy(VET, os.path.join(tmp, "tools", "vet"))
        json.dump({"name": "demo", "version": "1.2.0"}, open(os.path.join(tmp, ".claude-plugin", "plugin.json"), "w"))
        open(os.path.join(tmp, "docs", "neckbeard-report.md"), "w", encoding="utf-8").write(
            "# \U0001F50D demo %s \u00b7 what it adds\n\n`2026-11-12` \u00b7 neckbeard 1.17.0 \u00b7 demo %s @ %s\n" % (report_version, report_version, at))
        git = lambda *a: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=tmp, check=True, capture_output=True)
        git("init", "-q"); git("add", "-A"); git("commit", "-q", "-m", "x"); git("tag", "-a", "v1.2.0", "-m", "x")
        # the working tree is made right after the tag: the check must read the tagged tree, not this one
        open(os.path.join(tmp, "docs", "neckbeard-report.md"), "w", encoding="utf-8").write(
            "# \U0001F50D demo 1.2.0 \u00b7 what it adds\n\n`2026-11-12` \u00b7 neckbeard 1.17.0 \u00b7 demo 1.2.0 @ `v1.2.0`\n")
        p = subprocess.run(["make", "--no-print-directory", "report-check"], cwd=tmp, capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr
    finally:
        shutil.rmtree(tmp)
rc, out = report_check("1.1.0")
chk("report-check: a tagged report naming an older version fails, though the working tree is right", (rc != 0, "vets 1.1.0" in out), (True, True))
rc, out = report_check("1.2.0")
chk("report-check: a tagged report naming the tagged version passes", rc, 0)
makefile = open(os.path.join(NB, "Makefile"), encoding="utf-8").read()
release = makefile.split("\nrelease:", 1)[1].split("\ndeploy:", 1)[0]
chk("release runs report-check before any push, and stops when it fails", (bool(re.search(r"^\t@\$\(MAKE\) --no-print-directory report-check \|\| \{ [^}]*exit 1; \}$", release, re.M)), release.find("report-check") < release.find("git push")), (True, True))
readme = open(os.path.join(NB, "README.md"), encoding="utf-8").read()
chk("README: the neckbeard badge links the published report, with the logo the code uses", ("[![neckbeard: " in readme, "](docs/neckbeard-report.md)" in readme, "logo=" + LOGO in readme), (True, True, True))
badge_line = readme.split("\n")[4]
chk("README line 5: badges read CI, license, release, CodeQL, neckbeard", [re.sub(r":.*", "", a) for a in re.findall(r"\[!\[([^\]]*)\]", badge_line)], ["CI", "license", "release", "CodeQL", "neckbeard"])
chk("the logo is URL-encoded: none of + & # ( ) [ ] = or a space raw", [c for c in "+&#()[]= " if c in LOGO], [])
b = run("badge-precedence", extra=("--facts",), fake_body=NO_CLAUDE, setup=lambda t: (big_skill(t), bad_mcp(t)))
chk("badge: a partial and a failed section give red, not yellow", "-red?logo=" in badge_of(b), True)

# 12. the header's label names what was read: "+ uncommitted changes" on a dirty checkout, the tag under --release-tag
def dirty(target):   # a commit, then a tracked file changed after it
    for c in (["init", "-q"], ["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "x"]):
        subprocess.run(["git", *c], cwd=target, check=True)
    open(os.path.join(target, "skills", "demo", "SKILL.md"), "a").write("One more rule.\n")
def untracked_only(target):   # a commit, then a new untracked file only
    dirty(target)
    subprocess.run(["git", "checkout", "-q", "--", "."], cwd=target, check=True)
    open(os.path.join(target, "new.txt"), "w").write("x\n")
def header_of(r): return next((l for l in r["text"].splitlines() if " · neckbeard " in l), "")
def source_commit(r): return next((l for l in r["text"].splitlines() if l.startswith("- Commit: ")), "")
d = run("dirty", extra=("--facts",), fake_body=NO_CLAUDE, setup=dirty)
chk("label: a tracked file changed after the commit: the header ends '+ uncommitted changes'", header_of(d).endswith(" + uncommitted changes`"), True)
chk("label: the Source 'Commit:' line shows the same label", re.fullmatch(r"- Commit: [0-9a-f]+ \+ uncommitted changes", source_commit(d)) is not None, True)
u = run("untracked", extra=("--facts",), fake_body=NO_CLAUDE, setup=untracked_only)
chk("label: an untracked file alone does not count as uncommitted", ("uncommitted" in header_of(u), "uncommitted" in source_commit(u)), (False, False))
c = run("clean-label", extra=("--facts",), fake_body=NO_CLAUDE, commit=True)
chk("label: a clean checkout is unchanged: '@ `<sha>`' and a bare sha in Source", (header_of(c).endswith(" @ `%s`" % c["sha"]), source_commit(c)), (True, "- Commit: " + c["sha"]))
t1 = run("release-tag", extra=("--facts", "--release-tag", "v9.9.9"), fake_body=NO_CLAUDE, commit=True)
chk("--release-tag: the header names the tag and no sha", (t1["rc"], header_of(t1).endswith(" @ `v9.9.9`"), t1["sha"] in header_of(t1)), (0, True, False))
chk("--release-tag: the Source line names the tag and no sha", (source_commit(t1), t1["sha"] in t1["text"]), ("- Commit: v9.9.9", False))
t2 = run("release-tag-dirty", extra=("--facts", "--release-tag", "v9.9.9"), fake_body=NO_CLAUDE, setup=dirty)
chk("--release-tag wins over uncommitted changes", ("uncommitted" in t2["text"], header_of(t2).endswith(" @ `v9.9.9`")), (False, True))
t3 = run("release-tag-judged", extra=("--release-tag", "v9.9.9"))
chk("--release-tag with a judged run: a usage error, no report, no judge call", (t3["rc"], t3["report"], len(t3["calls"]), "usage:" in t3["out"]), (2, False, 0, True))
chk("usage names --release-tag", "--facts takes only --repo and --release-tag" in t3["out"], True)
rc, out = report_check("1.2.0", at="`cd202ff`")
chk("report-check: a tagged report naming a commit, not the tag, fails", (rc != 0, "v1.2.0" in out), (True, True))
rc, out = report_check("1.2.0", at="`v1.1.0`")
chk("report-check: a tagged report naming another tag fails, and says which tag it wanted", (rc != 0, "must name the tag" in out and "v1.2.0" in out), (True, True))
rc, out = report_check("1.2.0", at="`v1.2.0`")
chk("report-check: a tagged report naming the tag passes", rc, 0)
chk("--check still passes on a report whose header carries '@ `<sha> + uncommitted changes`'", facts_check_text("# \U0001F50D demo 1.0.0 \u00b7 what it adds\n\n`2026-11-12` \u00b7 neckbeard 1.17.0 \u00b7 demo 1.0.0 @ `abc1234 + uncommitted changes`\n", "1.0.0"), 0)
chk("--release-tag with a backtick, a slash, a space or a newline: a usage error", [subprocess.run([VET, ".", "/dev/null", "--facts", "--release-tag", v], capture_output=True, text=True).returncode for v in ("v1`x", "/private/x", "v 1", "v1\nx")], [2, 2, 2, 2])
chk("--release-tag with no value or an empty one: a usage error", [subprocess.run([VET, ".", "/dev/null", "--facts", "--release-tag", *a], capture_output=True, text=True).returncode for a in ([], [""])], [2, 2])
report = makefile.split("\nreport:", 1)[1].split("\nreport-check:", 1)[0]
chk("make report passes --release-tag v$(VERSION)", "--release-tag v$(VERSION)" in report, True)

sys.exit(vet_harness.summary("test_vet"))
