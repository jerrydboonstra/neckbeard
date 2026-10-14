#!/usr/bin/env python3
"""tools/vet, the headless gallery method, run end to end against a fake `claude`.

The inventory is real; the judge is a fake `claude` on PATH that logs how it was
started (folder, config folder, arguments), writes into its config folder the way
the real one does, and writes the report the prompt names in the shape a case asks
for. FAKE_LOGIN=env logs in with any config folder, as a web session does;
FAKE_LOGIN=default logs in only with the default one, as a Mac does.

    python3 tools/test_vet.py
"""
import json, os, shutil, subprocess, sys, tempfile

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
out = re.search(r"REPORT FILE \(the only file you create\): (\S+)", prompt).group(1)
target = re.search(r"checked out at (\S+)", prompt).group(1).rstrip(",")
mode = os.environ.get("FAKE_REPORT", "good")
body = {"good": "> ## 🟩 INSTALL · add the one skill\n> Fine.\n",
        "noverdict": "# 🔍 demo\n\nNo banner here.\n",
        "leak": "> ## 🟩 INSTALL · fine\n> Read " + target + "/skills/demo/SKILL.md.\n"}.get(mode)
if body is not None:
    open(out, "w").write("# 🔍 demo 1.0.0\n\n" + body)
print("🟩 INSTALL · 0/0/0/1/0")
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


def run(case, login="env", report="good", extra=(), remote=None):
    tmp = tempfile.mkdtemp()
    try:
        bindir = os.path.join(tmp, "bin"); os.mkdir(bindir)
        fake = os.path.join(bindir, "claude")
        open(fake, "w").write(FAKE_CLAUDE); os.chmod(fake, 0o755)
        target = os.path.join(tmp, "demo")
        os.makedirs(os.path.join(target, ".claude-plugin"))
        os.makedirs(os.path.join(target, "skills", "demo"))
        json.dump({"name": "demo", "version": "1.0.0"}, open(os.path.join(target, ".claude-plugin", "plugin.json"), "w"))
        open(os.path.join(target, "skills", "demo", "SKILL.md"), "w").write(
            "---\nname: demo\ndescription: A demo skill.\n---\n\nAlways run the tests before you commit.\n")
        if remote:
            for c in (["init", "-q"], ["remote", "add", "origin", remote]):
                subprocess.run(["git", *c], cwd=target, check=True)
        out = os.path.join(tmp, "out", "report.md")
        log = os.path.join(tmp, "claude.log")
        # a cloud container rewrites git@github.com: to https itself through GIT_CONFIG_*, which would hide vet's own rewrite
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_CONFIG_DIR" and not k.startswith("GIT_CONFIG")}
        env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                   PATH=bindir + os.pathsep + env["PATH"], FAKE_LOG=log, FAKE_LOGIN=login, FAKE_REPORT=report,
                   TMPDIR=os.path.join(tmp, "t"))
        os.mkdir(env["TMPDIR"])
        before = reader_files()
        p = subprocess.run([VET, ".", out, *extra], env=env, cwd=target, capture_output=True, text=True)
        calls = [json.loads(l) for l in open(log)] if os.path.exists(log) else []
        title = open(out, encoding="utf-8").readline().rstrip("\n") if os.path.exists(out) else None
        res = dict(rc=p.returncode, out=p.stdout + p.stderr, calls=calls, report=os.path.exists(out), title=title,
                   reader_untouched=reader_files() == before, temp_left=os.listdir(env["TMPDIR"]), target=target)
        if os.environ.get("VERBOSE"):
            print(case, res)
        return res
    finally:
        shutil.rmtree(tmp)


judge = lambda r: [c for c in r["calls"] if "--allowedTools" in c["args"]]

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

print(f"test_vet: {checks - fail}/{checks} checks passed")
sys.exit(1 if fail else 0)
