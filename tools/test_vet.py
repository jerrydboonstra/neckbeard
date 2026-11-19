#!/usr/bin/env python3
"""tools/vet, the headless gallery method, run end to end against a fake `claude`: the --units prototype, part 1, the
report checks, --facts, --reader, the badge and report-check. The judge and login checks are in tools/test_vet_judge.py;
the fake `claude` and the helpers both share are in tools/vet_harness.py.

    python3 tools/test_vet.py
"""
import json, os, re, shutil, subprocess, sys, tempfile

import vet_harness
from vet_harness import *


judges = lambda r: isolated(r, "ANSWERING JUDGE") + isolated(r, "PROSE JUDGE")   # the two calls that judge
hline = lambda r: r["text"].split("\n")[2]   # the header line, which vet --check reads
vline = lambda r: next((l for l in r["text"].split("\n") if "Verdict is relative to" in l), "")   # the paragraph in Why this verdict
def first(r, word):
    return next(iter(isolated(r, word)), {"prompt": ""})["prompt"]

# 0. the answers: the answering judge gets the unit list and the written tests; the verdict is units-verdict's, whatever the answers compute
r = run("units", units="units-install")
chk("units: answers that compute INSTALL: exit 0, strip INSTALL", (r["rc"], "> **\U0001F7E9 INSTALL**" in r["text"]), (0, True))
chk("units: the answering judge got the unit list and the tests", ("ANSWERING JUDGE" in first(r, "ANSWERING JUDGE") and "new-standing" in first(r, "ANSWERING JUDGE"), "UNITS:" in first(r, "ANSWERING JUDGE")), (True, True))
r = run("units-mismatch", units="units-mismatch")
chk("units: answers that compute COPY RULES give that strip, no refusal", (r["rc"], "> **\U0001F7E8 COPY RULES, SKIP PLUGIN**" in r["text"]), (0, True))
r = run("units-missing", units="units-none")
chk("units: an answer missing for a unit: refused", (r["rc"], "answers were refused" in r["out"]), (1, True))
# 0b. --units pools three find passes and confirms each candidate alone; only confirmed conflicts count
r = run("units-find-none", units="units-install")
chk("pool: three find passes, no candidates, no confirm call, exit 0", (r["rc"], len(isolated(r, "FIND PASS")), len(isolated(r, "CONFIRM CALL"))), (0, 3, 0))
r = run("units-confirmed", units="units-install", finds="one", confirm="yes")
chk("pool: the same candidate in three passes is confirmed once", len(isolated(r, "CONFIRM CALL")), 1)
chk("confirm: a confirmed conflict counts, so INSTALL becomes INSTALL WITH CHANGES in the strip",
    (r["rc"], "> **\U0001F7E8 INSTALL WITH CHANGES**" in r["text"]), (0, True))
c = next(iter(isolated(r, "CONFIRM CALL")), {"prompt": "", "args": ["--allowedTools", "?"]})
chk("confirm: the call sees the sentence and the written test, not the units or the dossier",
    ("Always run the tests before you commit." in c["prompt"], "Never run anything destructive without my explicit go-ahead" in c["prompt"], "permits, with no limit" in c["prompt"], "UNITS:" in c["prompt"], "dossier" in c["prompt"].lower()),
    (True, True, True, False, False))
chk("confirm: the reader rule is the reader's own text; the finder's argument never reaches the call",
    ("FINDER ARGUMENT" in c["prompt"], "rules/safety.md: 1. **Never run anything destructive" in c["prompt"]), (False, True))
chk("confirm: the call is allowed no tools", c["args"][c["args"].index("--allowedTools") + 1], "")
r = run("units-rejected", units="units-install", finds="one", confirm="no")
chk("confirm: a rejected candidate does not count, exit 0", (r["rc"], "0 of 1 candidates confirmed" in r["out"]), (0, True))
r = run("units-flaky", units="units-install", finds="one", confirm="flaky")
chk("confirm: a call with no JSON is retried once, and the second answer counts", (len(isolated(r, "CONFIRM CALL")), "> **\U0001F7E8 INSTALL WITH CHANGES**" in r["text"]), (2, True))
r = run("units-garbage", units="units-install", finds="one", confirm="garbage")
chk("confirm: two calls with no JSON fail the vet and show what was said", (r["rc"], "gave no usable answer: 'no json here" in r["out"]), (1, True))
r = run("units-late", units="units-install", finds="late", confirm="yes")
chk("pool: a candidate found in one pass of three is still confirmed", (len(isolated(r, "CONFIRM CALL")), "> **\U0001F7E8 INSTALL WITH CHANGES**" in r["text"]), (1, True))
r = run("units-invented", units="units-install", finds="invented", confirm="yes")
chk("pool: a quote that is not in the unit is dropped before any confirm call", (r["rc"], len(isolated(r, "CONFIRM CALL"))), (0, 0))
chk("cost: the vet prints calls and dollars", "units cost: 5 calls, $0.05" in r["out"], True)

r = vet_with_tool("part1", "import sys\nsys.stderr.write('part1: cannot read a dossier\\n')\nsys.exit(2)\n")
chk("part1: when tools/part1 exits non-zero vet dies with 'part 1 could not be rendered' and part1's own message",
    (r["rc"], "part 1 could not be rendered" in r["out"], "part1: cannot read a dossier" in r["out"]), (1, True, True))

# 1. a web session: the judge logs in with the reader copy as its config folder
r = run("web")
chk("web: exit 0", r["rc"], 0)
chk("web: report written", r["report"], True)
chk("web: judge uses the reader", "judge: reader" in r["out"], True)
j = judges(r)
chk("web: two judge calls, the answering judge and the prose judge", len(j), 2)
chk("web: no judge call may run Bash or Edit", all(not {"Bash", "Edit"} & set(c["args"][c["args"].index("--allowedTools") + 1].split(",")) for c in j), True)
chk("web: every call's config is a copy, not the checkout",
    bool(r["calls"]) and all(c["cfg"] != "" and not os.path.realpath(c["cfg"]).startswith(os.path.realpath(NB)) for c in r["calls"] if "single word ok" not in c["prompt"]), True)
chk("web: every call starts outside the target", bool(j) and all(not os.path.realpath(c["cwd"]).startswith(os.path.realpath(r["target"])) for c in j), True)
chk("web: examples/reader untouched", r["reader_untouched"], True)
chk("web: temp folder removed", r["temp_left"], [])
chk("web: title names the sample reader", r["title"], TITLE + " · against the sample reader")

header = hline
chk("web: header names the target plainly, then who made it", re.fullmatch(r"`\d{4}-\d\d-\d\d` · demo 1\.0\.0 · made by neckbeard \d+\.\d+\.\d+", header(r)) is not None, True)

# 1b. a target with a GitHub origin: the header links it once, and the ssh form becomes https
r = run("remote", remote="git@github.com:someone/demo.git")
chk("remote: title uses the repo's short name", r["title"], TITLE + " · against the sample reader")
chk("remote: header links the repo once", "· [someone/demo](https://github.com/someone/demo) 1.0.0" in header(r)
    and header(r).count("https://github.com/someone/demo") == 1, True)

# 1c. --repo names the public repo over a private origin, and --note leads the reader paragraph
r = run("repo", remote="https://github.com/someone/demo-dev.git",
        extra=("--repo", "https://github.com/someone/demo", "--note", "Same author, so a self-vetting."))
chk("repo: header names the public repo", "· [someone/demo](https://github.com/someone/demo) 1.0.0" in header(r), True)
chk("repo: note leads the paragraph", "Same author, so a self-vetting. Verdict is relative" in vline(r), True)

# 2. a Mac: the reader copy can't log in, so the judge falls back to the caller's config and says so
r = run("mac", login="default")
chk("mac: exit 0", r["rc"], 0)
chk("mac: falls back to own config", "judge: own" in r["out"] and "can't log in" in r["out"], True)
j = judges(r)
chk("mac: judges have no config folder", bool(j) and all(c["cfg"] == "" for c in j), True)

# 2b. bash 3.2 (the Mac's /bin/bash, what `env bash` finds without Homebrew): the judge's empty config array is expanded under set -u
# (vet-bash32-empty-cfg). Where /bin/bash is 3.2 this is the failing case on an unfixed vet; elsewhere it still has to pass.
if os.path.exists("/bin/bash"):
    r = run("bash32-own", login="default", extra=("--judge", "own"), shell="/bin/bash")
    chk("bash 3.2: --judge own runs the judge past the empty config array, exit 0, report written",
        (r["rc"], r["report"], len(judges(r)), "unbound variable" in r["out"]), (0, True, 2, False))
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

# 4. the prose judge writes no prose file
r = run("none", units="units-install", fake_env=dict(FAKE_PROSE="none"))
chk("no prose: exit 1, no report", (r["rc"], r["report"]), (1, False))
chk("no prose: says so", "wrote no prose" in r["out"], True)

# 6. a prose text that names a local path
r = run("leak", units="units-install", fake_env=dict(FAKE_PROSE="leak"))
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
rc, out = check("`2026-11-18` · [someone/demo](https://github.com/someone/demo) 1.0.0 @ `v1.0.0` · made by neckbeard 2.0.0")
chk("check: the 2.0 header (version, commit, then made by neckbeard) passes", (rc, "current (1.0.0)" in out), (0, True))
rc, out = check("`2026-11-18` · demo 1.0.0 · made by neckbeard 2.0.0", version="1.1.0")
chk("check: the 2.0 header with no commit reads its version too", (rc, "vets 1.0.0, but" in out), (1, True))
rc, out = check("Vetted some time ago.")
chk("check: no header fails", (rc, "no header line" in out), (1, True))

# 8. --facts: the report with no reader, no verdict and no model call
r = run("facts", extra=("--facts",), fake_body=NO_CLAUDE)
chk("facts: written, exit 0, claude never called", (r["rc"], r["report"], r["calls"]), (0, True, []))
chk("facts: title line", r["title"], TITLE)
chk("facts: no verdict, no reader", [w in r["text"] for w in ("vetted against", "sample reader")], [False] * 2)
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
want = [hline(j)]
got = [l for l in f["text"].split("\n") if l.startswith("`") and " \u00b7 made by neckbeard " in l]
chk("facts and judged header lines are equal", (len(want), got), (1, want))
chk("judged title names the reader it is against", j["title"], TITLE + " \u00b7 against the sample reader")

# 9. --reader and the baseline line
BASELINE = re.compile(r"^Baseline: (.+) \u00b7 (\d+) rule files \u00b7 (\d+) bytes \u00b7 sha256 ([0-9a-f]{12})$", re.M)

r = run("baseline-default")
m = BASELINE.search(r["text"])
chk("baseline: default reader names the sample reader, 4 rule files, a 12-hex fingerprint", (m.group(1), m.group(2)) if m else None, ("the sample reader", str(len(reader_files()))))
chk("baseline: byte total is the files' own", int(m.group(3)) if m else None, sum(os.path.getsize(os.path.join(DEFAULT_READER, f)) for f in reader_files()))
chk("baseline: the file list is a details block of relative paths", [w in r["text"] for w in ("<details><summary><b>Rule files</b></summary>", "- `rules/safety.md`", "</details>")], [True] * 3)
chk("baseline: the title still names the sample reader", r["title"], TITLE + " \u00b7 against the sample reader")

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
    chk("reader: title names the label", ra["title"], TITLE + " \u00b7 against readerdir")
    leaks = [x for d in (a, os.path.dirname(a)) for x in (d, os.path.realpath(d))]   # macOS prints /private/var for /var
    chk("reader: no absolute path of the folder in the report", ([x for x in leaks if x in ra["text"] + ra["out"]], ra["rc"]), ([], 0))
    # the header line is vet's own, and the Baseline block sits inside Why this verdict, under its paragraph; --check reads the report
    h = run("header-reader", extra=("--reader", a))
    hl = h["text"].split("\n")
    chk("reader: the header line is line 3, and the Baseline block is in the Why card", (h["rc"], hl[2].startswith("`") and " \u00b7 made by neckbeard " in hl[2], h["text"].find("Baseline: readerdir \u00b7 4 rule files") > h["text"].find("<b>Why this verdict</b>") > 0), (0, True, True))
    chk("reader: that report carries one header line and one Baseline", (sum(1 for l in hl if " \u00b7 made by neckbeard " in l), sum(1 for l in hl if l.startswith("Baseline: "))), (1, 1))
    chk("reader: --check passes on it", facts_check_text(h["text"], "1.0.0"), 0)
    # a non-default folder that happens to be named "the sample reader" is still not the default
    os.makedirs(os.path.join(tmp, "named"))
    named = reader_copy(os.path.join(tmp, "named"), "the sample reader")
    rn = run("named-like-default", extra=("--reader", named))
    pn = [vline(rn)]
    chk("reader: a folder named like the default gets the non-default paragraph and citation", (len(pn), "](" not in pn[0], "examples/reader/..." in "\n".join(c["prompt"] for c in judges(rn)), "rule files (fingerprint %s)" % fp(rn) in pn[0]), (1, True, False, True))
    # a path-only change (one rule file renamed) changes the fingerprint too
    moved = reader_copy(tmp, "moved")
    os.rename(os.path.join(moved, "rules", "safety.md"), os.path.join(moved, "rules", "safe.md"))
    chk("reader: a renamed rule file, a different fingerprint", fp(run("fp-moved", extra=("--reader", moved))) not in (None, fp(ra)), True)
    # the default named on the command line is still the sample reader
    d = run("explicit-default", extra=("--reader", DEFAULT_READER))
    chk("reader: --reader examples/reader keeps the sample reader label", (d["title"], (BASELINE.search(d["text"]) or [0, 0])[1], fp(d) == (BASELINE.search(r["text"]) or [0] * 5)[4]), (TITLE + " \u00b7 against the sample reader", "the sample reader", True))
    # vet --check reads a judged report that carries the Baseline block
    chk("reader: --check passes on a judged report with a Baseline block", facts_check_text(ra["text"], "1.0.0"), 0)
    prompt = [vline(ra)]
    want = "Verdict is relative to readerdir's 4 rule files (fingerprint %s), not a judgment of the plugin's quality." % fp(ra)
    chk("reader: the verdict paragraph names the label, count and fingerprint, and links nothing", (len(prompt), want in prompt[0] and "](" not in prompt[0]), (1, True))
    default_prompt = [vline(r)]
    chk("reader: the default verdict paragraph is unchanged", "Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment" in default_prompt[0], True)
    # a reader with no rule files: the facts report, no claude call, exit 0
    empty = os.path.join(tmp, "emptyreader"); os.mkdir(empty)
    open(os.path.join(empty, "notes.txt"), "w").write("not a rule file\n")
    e = run("empty-reader", extra=("--reader", empty), fake_body=NO_CLAUDE)
    chk("reader: no rule files gives the facts report, no claude call, exit 0", (e["rc"], e["calls"], e["title"], "no rule files" in e["out"]), (0, [], TITLE, True))
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
FAKE_P1 = ("if __name__ == '__main__':\n    import sys\n    if sys.argv[1] == '--read-state':\n        print('%s')\n        sys.exit(0)\n"
           "    print('## What it adds\\n\\n<details><summary>\\U0001F7E2 <b>Injects</b></summary>\\n\\n- x\\n\\n</details>\\n')\n")
for word_, colour_ in (("something unread", "red"), ("partly read", "yellow"), ("read in full", "brightgreen")):
    r = vet_with_tool("part1", REAL_PART1 + FAKE_P1 % word_, extra=("--facts",), fake_body=NO_CLAUDE)
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
def report_check(report_version, tag_after=False, at="`v1.2.0`", old=False):
    tmp = tempfile.mkdtemp()
    try:
        for d in (".claude-plugin", "docs", "tools"):
            os.makedirs(os.path.join(tmp, d))
        shutil.copy(os.path.join(NB, "Makefile"), tmp)
        shutil.copy(VET, os.path.join(tmp, "tools", "vet"))
        json.dump({"name": "demo", "version": "1.2.0"}, open(os.path.join(tmp, ".claude-plugin", "plugin.json"), "w"))
        open(os.path.join(tmp, "docs", "neckbeard-report.md"), "w", encoding="utf-8").write(
            ("# \U0001F50D demo\n\n`2026-11-12` \u00b7 demo %s @ %s \u00b7 made by neckbeard 2.0.0\n" if not old else "# \U0001F50D demo %s \u00b7 what it adds\n\n`2026-11-12` \u00b7 neckbeard 1.17.0 \u00b7 demo %s @ %s\n") % ((report_version, at) if not old else (report_version, report_version, at)))
        git = lambda *a: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=tmp, check=True, capture_output=True)
        git("init", "-q"); git("add", "-A"); git("commit", "-q", "-m", "x"); git("tag", "-a", "v1.2.0", "-m", "x")
        # the working tree is made right after the tag: the check must read the tagged tree, not this one
        open(os.path.join(tmp, "docs", "neckbeard-report.md"), "w", encoding="utf-8").write(
            "# \U0001F50D demo\n\n`2026-11-12` \u00b7 demo 1.2.0 @ `v1.2.0` \u00b7 made by neckbeard 2.0.0\n")
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
NBV = json.load(open(os.path.join(NB, ".claude-plugin", "plugin.json")))["version"]
def header_of(r): return next((l for l in r["text"].splitlines() if " · made by neckbeard " in l), "")
def source_commit(r): return next((l for l in r["text"].splitlines() if l.startswith("- Commit: ")), "")
d = run("dirty", extra=("--facts",), fake_body=NO_CLAUDE, setup=dirty)
chk("label: a tracked file changed after the commit: the header ends '+ uncommitted changes'", header_of(d).removesuffix(" · made by neckbeard " + NBV).endswith(" + uncommitted changes`"), True)
chk("label: the Source 'Commit:' line shows the same label", re.fullmatch(r"- Commit: [0-9a-f]+ \+ uncommitted changes", source_commit(d)) is not None, True)
u = run("untracked", extra=("--facts",), fake_body=NO_CLAUDE, setup=untracked_only)
chk("label: an untracked file alone does not count as uncommitted", ("uncommitted" in header_of(u), "uncommitted" in source_commit(u)), (False, False))
c = run("clean-label", extra=("--facts",), fake_body=NO_CLAUDE, commit=True)
chk("label: a clean checkout is unchanged: '@ `<sha>`' and a bare sha in Source", (header_of(c).removesuffix(" · made by neckbeard " + NBV).endswith(" @ `%s`" % c["sha"]), source_commit(c)), (True, "- Commit: " + c["sha"]))
t1 = run("release-tag", extra=("--facts", "--release-tag", "v9.9.9"), fake_body=NO_CLAUDE, commit=True)
chk("--release-tag: the header names the tag and no sha", (t1["rc"], header_of(t1).removesuffix(" · made by neckbeard " + NBV).endswith(" @ `v9.9.9`"), t1["sha"] in header_of(t1)), (0, True, False))
chk("--release-tag: the Source line names the tag and no sha", (source_commit(t1), t1["sha"] in t1["text"]), ("- Commit: v9.9.9", False))
t2 = run("release-tag-dirty", extra=("--facts", "--release-tag", "v9.9.9"), fake_body=NO_CLAUDE, setup=dirty)
chk("--release-tag wins over uncommitted changes", ("uncommitted" in t2["text"], header_of(t2).removesuffix(" · made by neckbeard " + NBV).endswith(" @ `v9.9.9`")), (False, True))
t3 = run("release-tag-judged", extra=("--release-tag", "v9.9.9"))
chk("--release-tag with a judged run: a usage error, no report, no judge call", (t3["rc"], t3["report"], len(t3["calls"]), "usage:" in t3["out"]), (2, False, 0, True))
chk("usage names --release-tag", "--facts takes only --repo and --release-tag" in t3["out"], True)
rc, out = report_check("1.2.0", at="`cd202ff`")
chk("report-check: a tagged report naming a commit, not the tag, fails", (rc != 0, "v1.2.0" in out), (True, True))
rc, out = report_check("1.2.0", at="`v1.1.0`")
chk("report-check: a tagged report naming another tag fails, and says which tag it wanted", (rc != 0, "must name the tag" in out and "v1.2.0" in out), (True, True))
rc, out = report_check("1.2.0", at="`v1.2.0`")
chk("report-check: a tagged report naming the tag passes", rc, 0)
rc, out = report_check("1.2.0", old=True)
chk("report-check: the pre-2.0 header (neckbeard first, no 'made by') is refused, so a stale report cannot be tagged", (rc != 0, "must name the tag" in out), (True, True))
chk("--check still passes on a report whose header carries '@ `<sha> + uncommitted changes`'", facts_check_text("# \U0001F50D demo 1.0.0 \u00b7 what it adds\n\n`2026-11-12` \u00b7 neckbeard 1.17.0 \u00b7 demo 1.0.0 @ `abc1234 + uncommitted changes`\n", "1.0.0"), 0)
chk("--release-tag with a backtick, a slash, a space or a newline: a usage error", [subprocess.run([VET, ".", "/dev/null", "--facts", "--release-tag", v], capture_output=True, text=True).returncode for v in ("v1`x", "/private/x", "v 1", "v1\nx")], [2, 2, 2, 2])
chk("--release-tag with no value or an empty one: a usage error", [subprocess.run([VET, ".", "/dev/null", "--facts", "--release-tag", *a], capture_output=True, text=True).returncode for a in ([], [""])], [2, 2])
report = makefile.split("\nreport:", 1)[1].split("\nreport-check:", 1)[0]
chk("make report passes --release-tag v$(VERSION)", "--release-tag v$(VERSION)" in report, True)

sys.exit(vet_harness.summary("test_vet"))
