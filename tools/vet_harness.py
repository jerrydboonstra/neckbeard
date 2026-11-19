#!/usr/bin/env python3
"""The shared part of the tools/test_vet*.py modules (test_vet, test_vet_judge, test_vet_layers, test_vet_report, test_vet_session): tools/vet is run end to end against a fake `claude`.
Not a test module (no test_ prefix, so tools/test-parallel does not run it).

The inventory is real; the judge is a fake `claude` on PATH that logs how it was
started (folder, config folder, arguments), writes into its config folder the way
the real one does, and writes the report the prompt names in the shape a case asks
for. FAKE_LOGIN=env logs in with any config folder, as a web session does;
FAKE_LOGIN=default logs in only with the default one, as a Mac does.
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
cred = os.path.join(cfg, ".credentials.json") if cfg else ""
dm = re.search(r"DOSSIER \(already built, read-only\): (\S+)\.", prompt)
mark = os.environ.get("FAKE_SECRET", "")
with open(os.environ["FAKE_LOG"], "a") as f:
    f.write(json.dumps({"cwd": os.getcwd(), "cfg": cfg, "args": args, "prompt": prompt,
                        "cred_seen": bool(cred) and os.path.exists(cred),
                        "cred_mode": oct(os.stat(cred).st_mode & 0o777) if cred and os.path.exists(cred) else "",
                        "reader_cred_left": bool(__import__("glob").glob(os.path.join(os.environ.get("TMPDIR", "/nonexistent"), "neckbeard-vet.*", "reader", ".credentials.json"))),
                        "dossier_has_secret": bool(mark and dm and mark in open(dm.group(1), encoding="utf-8").read())}) + "\n")
if "single word ok" in prompt and (os.environ.get("FAKE_LOGIN") == "never" or (os.environ.get("FAKE_LOGIN") == "file" and not (cred and os.path.exists(cred)))):
    print(os.environ.get("FAKE_PROBE_MSG", "Not logged in · Please run /login")); sys.exit(1)   # a login that lives in the config folder's login file
if os.environ.get("FAKE_REFRESH") and cred and os.path.exists(cred) and "single word ok" not in prompt:
    open(cred, "w").write('{"claudeAiOauth": {"accessToken": "ROTATED", "refreshToken": "ROTATED", "expiresAt": 1}}')
if os.environ.get("FAKE_LOGIN") == "default" and cfg:
    print("Not logged in · Please run /login"); sys.exit(1)
if cfg:
    os.makedirs(os.path.join(cfg, "backups"), exist_ok=True)
if "single word ok" in prompt:
    print("ok"); sys.exit(0)
def reply(text):
    if "--output-format" in args and args[args.index("--output-format") + 1] == "json":
        print(json.dumps({"result": text + os.environ.get("FAKE_SAY", ""), "total_cost_usd": 0.01, "duration_ms": 1000}))
    else:
        print(text + os.environ.get("FAKE_SAY", ""))
    sys.exit(0)
m = re.search(r"Write (.+?) as JSON, \{\"conflicts\"", prompt)
if "FIND PASS" in prompt and m:
    mode = os.environ.get("FAKE_FINDS", "none")
    n = m.group(1).rsplit("-", 1)[1][0]
    if mode == "tokenanswer":   # the judge answers with the login and writes no candidates (pass 2), or leaves it in its file (the others)
        if n == "2":
            reply(os.environ["FAKE_SECRET"])
        json.dump({"conflicts": [], "note": os.environ["FAKE_SECRET"]}, open(m.group(1), "w")); reply("0")
    quote = {"one": "Always run the tests before you commit.", "invented": "Never run the tests."}.get(mode)
    if mode == "late" and n == "3":
        quote = "Always run the tests before you commit."
    units = json.load(open(re.search(r"UNITS: (.+?)\. Each unit", prompt).group(1)))["units"]
    found = [{"id": units[0]["id"], "quote": quote, "reader_rule": 'safety.md: "Never run anything destructive without my explicit go-ahead in this conversation" (FINDER ARGUMENT: the permission is unlimited)'}] if quote else []
    json.dump({"conflicts": found}, open(m.group(1), "w"))
    reply(str(len(found)))
if "CONFIRM CALL" in prompt:
    if os.environ.get("FAKE_CONFIRM") == "fail":   # the claude inside a call() exits non-zero with its own message
        sys.stderr.write("noise line\n" + os.environ.get("FAKE_FAIL_MSG", "fake-claude-error: quota exceeded") + "\n"); sys.exit(1)
    if os.environ.get("FAKE_CONFIRM") == "flaky" and not os.path.exists(os.environ["FAKE_LOG"] + ".flaky"):
        open(os.environ["FAKE_LOG"] + ".flaky", "w").close()
        reply("I would rather not say.")
    if os.environ.get("FAKE_CONFIRM") == "garbage":
        reply("no json here")
    reply(json.dumps({"conflict": os.environ.get("FAKE_CONFIRM") in ("yes", "flaky"), "hard_stop": os.environ.get("FAKE_HARDSTOP", "1") == "1", "why": "fake"}))
if "ANSWERING JUDGE" in prompt:   # the one call that answers every unit (verdict-stability-rules)
    m = re.search(r"Write the answers to (\S+) as JSON", prompt)
    units = json.load(open(re.search(r"UNITS: (.+?)\. Each unit", prompt).group(1)))["units"]
    pick = {"units-install": ("keep", "none"), "units-mismatch": ("drop", "new-standing"), "units-duplicate": ("drop", "duplicate")}.get(os.environ.get("FAKE_UNITS", ""))
    answers = []
    for u in units if pick else []:
        a = {"id": u["id"], "skill": pick[0], "rules": pick[1], "quote": "Always run the tests before you commit.", "conflicts": [], "why": "x"}
        if pick[1] == "duplicate":
            a.update(covered_by="Rule 1, Reuse before writing", held_in="rules/engineering.md")
        answers.append(a)
    json.dump({"answers": answers}, open(m.group(1), "w"))
    if os.environ.get("FAKE_SIDE"):
        open(m.group(1), "a").write(os.environ["FAKE_SIDE"])
    reply("done")
if "PROSE JUDGE" in prompt:   # the one call that writes the three free texts
    if os.environ.get("FAKE_JUDGE_FAIL"):   # exits non-zero with its message on stdout
        print("judge noise line"); print(os.environ.get("FAKE_FAIL_MSG", "fake-judge-error: out of credit")); sys.exit(1)
    m = re.search(r"Write the prose to (\S+) as JSON", prompt)
    why = {"states": "Verdict: 🟥 DON'T INSTALL, with 99 conflicts and 99 kept."}.get(os.environ.get("FAKE_PROSE", ""), "FAKE WHY.")
    if os.environ.get("FAKE_PROSE") == "secret":   # a prose text that holds the login's token
        why = "The login is " + os.environ.get("FAKE_SECRET", "") + "."
    if os.environ.get("FAKE_PROSE") == "leak":   # a prose text that names a local path
        why = "See " + os.environ["HOME"] + "/notes."
    if os.environ.get("FAKE_PROSE") != "none":   # "none": the judge writes no prose file
        json.dump({"why": why, "do_this": ["Fake step one."], "patch": "Fake patch."}, open(m.group(1), "w"))
    reply("done")
if os.environ.get("FAKE_JUDGE_FAIL") and "Vet one plugin" in prompt:   # the main judge exits non-zero with its message on stdout
    print("judge noise line"); print(os.environ.get("FAKE_FAIL_MSG", "fake-judge-error: out of credit")); sys.exit(1)
out = re.search(r"REPORT FILE \(the only file you create\): (\S+)", prompt).group(1)
target = re.search(r"checked out at (\S+)", prompt).group(1).rstrip(",")
mode = os.environ.get("FAKE_REPORT", "good")
GLANCE = "\n## ⚡ At a glance\n\nOne line.\n"
body = {"good": "> ## 🟩 INSTALL · add the one skill\n> Fine.\n" + GLANCE,
        "noglance": "> ## 🟩 INSTALL · add the one skill\n> Fine.\n\n## Details\n\nText.\n",
        "noverdict": "# 🔍 demo\n\nNo banner here.\n",
        "leak": "> ## 🟩 INSTALL · fine\n> Read " + target + "/skills/demo/SKILL.md.\n" + GLANCE,
        "secret": "> ## 🟩 INSTALL · fine\n> The login is " + os.environ.get("FAKE_SECRET", "") + ".\n" + GLANCE}.get(mode)
if mode == "header":   # a judge that wrote the header line it was given
    body = re.search(r"Header line to use: (.*)", prompt).group(1) + "\n\n> ## 🟩 INSTALL · add the one skill\n> Fine.\n" + GLANCE
if body is not None:
    open(out, "w").write("# 🔍 demo 1.0.0\n\n" + body)
m = re.search(r"Write the answers to (\S+) as JSON", prompt)
if m:
    units = json.load(open(re.search(r"UNITS: (.+?)\. Each unit", prompt).group(1)))["units"]
    pick = {"units-install": ("keep", "none"), "units-mismatch": ("drop", "new-standing")}.get(os.environ.get("FAKE_UNITS", ""))
    answers = [{"id": u["id"], "skill": pick[0], "rules": pick[1], "conflicts": [], "why": "x"} for u in units] if pick else []
    json.dump({"answers": answers}, open(m.group(1), "w"))
    if os.environ.get("FAKE_SIDE"):
        open(m.group(1), "a").write(os.environ["FAKE_SIDE"])
reply("🟩 INSTALL · 0/0/0/1/0")
'''

TITLE = "# \U0001F50D demo 1.0.0 \u00b7 how it affects you, what it adds, where it takes a position"

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


def run(case, login="env", report="good", extra=(), remote=None, units="units-install", finds="none", confirm="no", commit=False, vet=None, fake_body=None, rules_above=False, setup=None, version=None, caller=None, uname=None, fake_env=None, outname="report.md", shell=None):
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
        if version:
            json.dump({"name": "demo", "version": version}, open(os.path.join(target, ".claude-plugin", "plugin.json"), "w"))
        if setup:
            setup(target)
        if remote:
            for c in (["init", "-q"], ["remote", "add", "origin", remote]):
                subprocess.run(["git", *c], cwd=target, check=True)
        sha = ""
        if commit:
            for c in (["init", "-q"], ["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "x"]):
                subprocess.run(["git", *c], cwd=target, check=True, env={**os.environ, "GIT_AUTHOR_DATE": "2026-01-01T00:00:00Z", "GIT_COMMITTER_DATE": "2026-01-01T00:00:00Z"})  # a fixed date, so two targets get one sha
            sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=target, capture_output=True, text=True).stdout.strip()
        if uname:   # the host's kind is a thing vet asks `uname -s`, so a test says which one it is
            open(os.path.join(bindir, "uname"), "w").write("#!/bin/sh\necho %s\n" % uname); os.chmod(os.path.join(bindir, "uname"), 0o755)
        home = os.path.join(tmp, "home"); os.makedirs(os.path.join(home, ".claude"))   # never the real HOME or login
        out = os.path.join(tmp, "out", outname)
        log = os.path.join(tmp, "claude.log")
        # a cloud container rewrites git@github.com: to https itself through GIT_CONFIG_*, which would hide vet's own rewrite
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_CONFIG_DIR" and not k.startswith("GIT_CONFIG")}
        env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                   PATH=bindir + os.pathsep + env["PATH"], FAKE_LOG=log, FAKE_LOGIN=login, FAKE_REPORT=report, FAKE_UNITS=units, FAKE_FINDS=finds, FAKE_CONFIRM=confirm,
                   TMPDIR=os.path.join(tmp, "t"), HOME=home, **(fake_env or {}))
        os.mkdir(env["TMPDIR"])
        if caller is not None:   # the caller's config folder, through CLAUDE_CONFIG_DIR, holding these files
            env["CLAUDE_CONFIG_DIR"] = os.path.join(tmp, "caller"); os.makedirs(env["CLAUDE_CONFIG_DIR"])
            for name, text in caller.items():
                open(os.path.join(env["CLAUDE_CONFIG_DIR"], name), "w").write(text)
        if rules_above:   # the dossier looks up from the throwaway project for a CLAUDE.md, and finds this one
            open(os.path.join(env["TMPDIR"], "CLAUDE.md"), "w").write("Always run the tests before you commit.\n")
        before = reader_files()
        p = subprocess.run([*([shell] if shell else []), vet or VET, ".", out, *extra], env=env, cwd=target, capture_output=True, text=True)
        calls = [json.loads(l) for l in open(log)] if os.path.exists(log) else []
        title = open(out, encoding="utf-8").readline().rstrip("\n") if os.path.exists(out) else None
        res = dict(rc=p.returncode, out=p.stdout + p.stderr, stdout=p.stdout, outpath=out, calls=calls, report=os.path.exists(out), title=title,
                   text=open(out, encoding="utf-8").read() if os.path.exists(out) else "", sha=sha, caller_after={n: open(os.path.join(env["CLAUDE_CONFIG_DIR"], n)).read() for n in os.listdir(env["CLAUDE_CONFIG_DIR"]) if os.path.isfile(os.path.join(env["CLAUDE_CONFIG_DIR"], n))} if caller is not None else {}, cfg_left=[os.path.exists(c["cfg"]) for c in calls if c["cfg"] and c["cfg"] != env.get("CLAUDE_CONFIG_DIR")], side_left=sorted(f for f in os.listdir(os.path.dirname(out)) if f != outname) if os.path.isdir(os.path.dirname(out)) else [], reader_untouched=reader_files() == before, temp_left=os.listdir(env["TMPDIR"]), target=target)
        if os.environ.get("VERBOSE"):
            print(case, res)
        return res
    finally:
        shutil.rmtree(tmp)


# tools/summary imports tools/part1 as a module, so a fake part1 that is imported (its __name__ is "part1") takes the real one's functions
REAL_PART1 = "import importlib.machinery as m_, importlib.util as u_\nif __name__ != '__main__':\n    s_ = u_.spec_from_loader('real_part1', m_.SourceFileLoader('real_part1', %r)); r_ = u_.module_from_spec(s_); s_.loader.exec_module(r_)\n    globals().update({k: v for k, v in vars(r_).items() if not k.startswith('__')})\n" % os.path.join(HERE, "part1")
# a copy of vet with one tool replaced by SCRIPT (a part1 that fails, say): vet dies and says so
def vet_with_tool(tool, script, **kw):
    fake = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(fake, "tools"))
        shutil.copy(VET, os.path.join(fake, "tools", "vet"))
        for f_ in os.listdir(HERE):   # every other tool, as it is: only part1 is faked
            if f_ not in ("vet", tool, "__pycache__") and not os.path.exists(os.path.join(fake, "tools", f_)):
                os.symlink(os.path.join(HERE, f_), os.path.join(fake, "tools", f_))
        for link in ("skills", "examples", ".claude-plugin"):
            os.symlink(os.path.join(NB, link), os.path.join(fake, link))
        open(os.path.join(fake, "tools", tool), "w").write(script)
        os.chmod(os.path.join(fake, "tools", tool), 0o755)
        return run(tool + "-fake", vet=os.path.join(fake, "tools", "vet"), **kw)
    finally:
        shutil.rmtree(fake)


judge = lambda r: [c for c in r["calls"] if "--allowedTools" in c["args"] and "--output-format" in c["args"] and c["args"][c["args"].index("--output-format") + 1] == "text"]
isolated = lambda r, word: [c for c in r["calls"] if word in c["prompt"]]
judges = lambda r: isolated(r, "ANSWERING JUDGE") + isolated(r, "PROSE JUDGE")   # the two calls that judge

# shared with the judge module
NO_CLAUDE = """#!/usr/bin/env python3
import json, os, sys
with open(os.environ["FAKE_LOG"], "a") as f:
    f.write(json.dumps({"cwd": os.getcwd(), "cfg": "", "args": sys.argv[1:], "prompt": ""}) + "\\n")
sys.exit(97)
"""

DEFAULT_READER = os.path.join(NB, "examples", "reader")

def reader_copy(parent, name="myreader", edit=None):
    dest = os.path.join(parent, name)
    shutil.copytree(DEFAULT_READER, dest)
    if edit:
        path = os.path.join(dest, "rules", "safety.md")
        open(path, "ab").write(edit)
    return dest


def summary(name):
    """Print this module's count of passed checks and return its exit code."""
    print(f"{name}: {checks - fail}/{checks} checks passed")
    return 1 if fail else 0
