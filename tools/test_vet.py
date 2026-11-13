#!/usr/bin/env python3
"""tools/vet, the headless gallery method, run end to end against a fake `claude`.

The inventory is real; the judge is a fake `claude` on PATH that logs how it was
started (folder, config folder, arguments), writes into its config folder the way
the real one does, and writes the report the prompt names in the shape a case asks
for. FAKE_LOGIN=env logs in with any config folder, as a web session does;
FAKE_LOGIN=default logs in only with the default one, as a Mac does.

    python3 tools/test_vet.py
"""
import json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
NB = os.path.dirname(HERE)
VET = os.environ.get("VET_SCRIPT", os.path.join(HERE, "vet"))

FAKE_CLAUDE = r'''#!/usr/bin/env python3
import json, os, re, sys
cfg = os.environ.get("CLAUDE_CONFIG_DIR", "")
args = sys.argv[1:]
prompt = args[-1] if args and not args[-1].startswith("-") and "ok" in args[-1] else sys.stdin.read()
with open(os.environ["FAKE_LOG"], "a") as f:
    f.write(json.dumps({"cwd": os.getcwd(), "cfg": cfg, "args": args, "prompt": prompt}) + "\n")
if os.environ.get("FAKE_LOGIN") == "default" and cfg:
    print("Not logged in · Please run /login"); sys.exit(1)
if cfg:
    os.makedirs(os.path.join(cfg, "backups"), exist_ok=True)
if "single word ok" in prompt:
    print("ok"); sys.exit(0)
def reply(text):
    if "--output-format" in args and args[args.index("--output-format") + 1] == "json":
        print(json.dumps({"result": text, "total_cost_usd": 0.01, "duration_ms": 1000}))
    else:
        print(text)
    sys.exit(0)
m = re.search(r"Write (\S+) as JSON, \{\"conflicts\"", prompt)
if "FIND PASS" in prompt and m:
    mode = os.environ.get("FAKE_FINDS", "none")
    n = m.group(1).rsplit("-", 1)[1][0]
    quote = {"one": "Always run the tests before you commit.", "invented": "Never run the tests."}.get(mode)
    if mode == "late" and n == "3":
        quote = "Always run the tests before you commit."
    units = json.load(open(re.search(r"UNITS: (\S+)\. Each unit", prompt).group(1)))["units"]
    found = [{"id": units[0]["id"], "quote": quote, "reader_rule": 'safety.md: "Never run anything destructive without my explicit go-ahead in this conversation" (FINDER ARGUMENT: the permission is unlimited)'}] if quote else []
    json.dump({"conflicts": found}, open(m.group(1), "w"))
    reply(str(len(found)))
if "CONFIRM CALL" in prompt:
    if os.environ.get("FAKE_CONFIRM") == "flaky" and not os.path.exists(os.environ["FAKE_LOG"] + ".flaky"):
        open(os.environ["FAKE_LOG"] + ".flaky", "w").close()
        reply("I would rather not say.")
    if os.environ.get("FAKE_CONFIRM") == "garbage":
        reply("no json here")
    reply(json.dumps({"conflict": os.environ.get("FAKE_CONFIRM") in ("yes", "flaky"), "why": "fake"}))
out = re.search(r"REPORT FILE \(the only file you create\): (\S+)", prompt).group(1)
target = re.search(r"checked out at (\S+)", prompt).group(1).rstrip(",")
mode = os.environ.get("FAKE_REPORT", "good")
GLANCE = "\n## ⚡ At a glance\n\nOne line.\n"
body = {"good": "> ## 🟩 INSTALL · add the one skill\n> Fine.\n" + GLANCE,
        "noglance": "> ## 🟩 INSTALL · add the one skill\n> Fine.\n\n## Details\n\nText.\n",
        "noverdict": "# 🔍 demo\n\nNo banner here.\n",
        "leak": "> ## 🟩 INSTALL · fine\n> Read " + target + "/skills/demo/SKILL.md.\n" + GLANCE}.get(mode)
if body is not None:
    open(out, "w").write("# 🔍 demo 1.0.0\n\n" + body)
m = re.search(r"Write the answers to (\S+) as JSON", prompt)
if m:
    units = json.load(open(re.search(r"UNITS: (\S+)\. Each unit", prompt).group(1)))["units"]
    pick = {"units-install": ("keep", "none"), "units-mismatch": ("drop", "new-standing")}.get(os.environ.get("FAKE_UNITS", ""))
    answers = [{"id": u["id"], "skill": pick[0], "rules": pick[1], "conflicts": [], "why": "x"} for u in units] if pick else []
    json.dump({"answers": answers}, open(m.group(1), "w"))
reply("🟩 INSTALL · 0/0/0/1/0")
'''

fail = checks = 0


def chk(name, got, want):
    global fail, checks
    checks += 1
    if got != want:
        fail += 1
        print(f"FAIL {name}: got {got!r}, want {want!r}")


def reader_files():
    root = os.path.join(NB, "examples", "reader")
    return sorted(os.path.relpath(os.path.join(d, f), root) for d, _, fs in os.walk(root) for f in fs)


def run(case, login="env", report="good", extra=(), remote=None, units="", finds="none", confirm="no", commit=False, vet=None, fake_body=None, rules_above=False):
    tmp = tempfile.mkdtemp()
    try:
        bindir = os.path.join(tmp, "bin"); os.mkdir(bindir)
        fake = os.path.join(bindir, "claude")
        open(fake, "w").write(fake_body or FAKE_CLAUDE); os.chmod(fake, 0o755)
        target = os.path.join(tmp, "demo")
        os.makedirs(os.path.join(target, ".claude-plugin"))
        os.makedirs(os.path.join(target, "skills", "demo"))
        json.dump({"name": "demo", "version": "1.0.0"}, open(os.path.join(target, ".claude-plugin", "plugin.json"), "w"))
        open(os.path.join(target, "skills", "demo", "SKILL.md"), "w").write(
            "---\nname: demo\ndescription: A demo skill.\n---\n\nAlways run the tests before you commit.\n")
        if remote:
            for c in (["init", "-q"], ["remote", "add", "origin", remote]):
                subprocess.run(["git", *c], cwd=target, check=True)
        sha = ""
        if commit:
            for c in (["init", "-q"], ["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "x"]):
                subprocess.run(["git", *c], cwd=target, check=True, env={**os.environ, "GIT_AUTHOR_DATE": "2026-01-01T00:00:00Z", "GIT_COMMITTER_DATE": "2026-01-01T00:00:00Z"})  # a fixed date, so two targets get one sha
            sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=target, capture_output=True, text=True).stdout.strip()
        out = os.path.join(tmp, "out", "report.md")
        log = os.path.join(tmp, "claude.log")
        # a cloud container rewrites git@github.com: to https itself through GIT_CONFIG_*, which would hide vet's own rewrite
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_CONFIG_DIR" and not k.startswith("GIT_CONFIG")}
        env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                   PATH=bindir + os.pathsep + env["PATH"], FAKE_LOG=log, FAKE_LOGIN=login, FAKE_REPORT=report, FAKE_UNITS=units, FAKE_FINDS=finds, FAKE_CONFIRM=confirm,
                   TMPDIR=os.path.join(tmp, "t"))
        os.mkdir(env["TMPDIR"])
        if rules_above:   # the dossier looks up from the throwaway project for a CLAUDE.md, and finds this one
            open(os.path.join(env["TMPDIR"], "CLAUDE.md"), "w").write("Always run the tests before you commit.\n")
        before = reader_files()
        p = subprocess.run([vet or VET, ".", out, *extra], env=env, cwd=target, capture_output=True, text=True)
        calls = [json.loads(l) for l in open(log)] if os.path.exists(log) else []
        title = open(out, encoding="utf-8").readline().rstrip("\n") if os.path.exists(out) else None
        res = dict(rc=p.returncode, out=p.stdout + p.stderr, calls=calls, report=os.path.exists(out), title=title,
                   text=open(out, encoding="utf-8").read() if os.path.exists(out) else "", sha=sha, reader_untouched=reader_files() == before, temp_left=os.listdir(env["TMPDIR"]), target=target)
        if os.environ.get("VERBOSE"):
            print(case, res)
        return res
    finally:
        shutil.rmtree(tmp)


judge = lambda r: [c for c in r["calls"] if "--allowedTools" in c["args"] and "--output-format" in c["args"] and c["args"][c["args"].index("--output-format") + 1] == "text"]
isolated = lambda r, word: [c for c in r["calls"] if word in c["prompt"]]

# 0. --units (prototype): the verdict comes from the per-unit answers, and the banner must carry it
r = run("units", extra=("--units",), units="units-install")
chk("units: answers that compute INSTALL, banner INSTALL: exit 0", r["rc"], 0)
chk("units: the judge got the unit list and the written tests", "UNITS PROTOTYPE" in judge(r)[0]["prompt"] and "new-standing" in judge(r)[0]["prompt"], True)
r = run("units-mismatch", extra=("--units",), units="units-mismatch")
chk("units: banner INSTALL but answers compute COPY RULES: refused", (r["rc"], "computed verdict is COPY RULES" in r["out"]), (1, True))
r = run("units-missing", extra=("--units",), units="units-none")
chk("units: an answer missing for a unit: refused", (r["rc"], "answers were refused" in r["out"]), (1, True))
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
chk("part1: the section ends with a blank line, and holds the six cards", (sec.endswith("\n\n"), all(f"### {h}\n" in sec for h in ("Injects", "Hooks", "Subagents and commands", "State it may leave", "Reaches outside the session", "Source"))), (True, True))
chk("part1: the commit vet holds goes into the Source card", f"Commit: {r['sha']}" in sec and r["sha"] != "", True)
chk("part1: no reader rule or local path in the section", ("READER" in sec, os.path.realpath(r["target"]) in sec, "/tmp" in sec), (False, False, False))
r = run("part1-no-commit")
chk("part1: with no git commit the section says commit not given", "Commit: commit not given" in r["text"], True)
# a copy of vet with a tools/part1 that fails, or that prints a heading of its own: vet dies and says so
def vet_with_part1(script):
    fake = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(fake, "tools"))
        shutil.copy(VET, os.path.join(fake, "tools", "vet"))
        for link in ("skills", "examples", ".claude-plugin"):
            os.symlink(os.path.join(NB, link), os.path.join(fake, link))
        open(os.path.join(fake, "tools", "part1"), "w").write(script)
        os.chmod(os.path.join(fake, "tools", "part1"), 0o755)
        return run("part1-fake", vet=os.path.join(fake, "tools", "vet"))
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

# 3. --judge reader on a Mac: no fallback, so the run fails
r = run("forced", login="default", extra=("--judge", "reader"))
chk("forced reader: exit 1", r["rc"], 1)

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
NO_CLAUDE = """#!/usr/bin/env python3
import json, os, sys
with open(os.environ["FAKE_LOG"], "a") as f:
    f.write(json.dumps({"cwd": os.getcwd(), "cfg": "", "args": sys.argv[1:], "prompt": ""}) + "\\n")
sys.exit(97)
"""
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
DEFAULT_READER = os.path.join(NB, "examples", "reader")

def reader_copy(parent, name="myreader", edit=None):
    dest = os.path.join(parent, name)
    shutil.copytree(DEFAULT_READER, dest)
    if edit:
        path = os.path.join(dest, "rules", "safety.md")
        open(path, "ab").write(edit)
    return dest

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

print(f"test_vet: {checks - fail}/{checks} checks passed")
sys.exit(1 if fail else 0)
