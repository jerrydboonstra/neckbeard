#!/usr/bin/env python3
"""tools/deploy-host.sh, the per-machine half of `make deploy`, run end to end.

A fake HOME holds a git origin, a working checkout of it, the export clone at
~/.claude/plugin-src/neckbeard that the neckbeard marketplace points at, and a fake `claude` that logs each call with the folder it ran in and
lists four installs: user scope, a project, a project whose folder is gone, and a
git worktree whose record never moves (as Claude Code leaves it). Each case runs
the script as `make deploy` does and checks what it did and what it printed.

    python3 tools/test_deploy.py
"""
import json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DEPLOY = os.path.join(HERE, "deploy-host.sh")

FAKE_CLAUDE = r'''#!/usr/bin/env python3
import json, os, sys
home = os.environ["HOME"]
with open(os.path.join(home, "claude.log"), "a") as f:
    f.write(os.getcwd() + "\t" + " ".join(sys.argv[1:]) + "\n")
args = sys.argv[1:]
notes = os.path.join(home, "proj", "notes")
if args[:3] == ["plugin", "marketplace", "list"]:
    src = os.environ.get("FAKE_SOURCE", "directory")
    print(json.dumps([] if src == "none" else [
        {"name": "neckbeard", "source": src, "path": os.environ.get("FAKE_PATH") or os.path.join(home, ".claude", "plugin-src", "neckbeard") if src == "directory" else None}]))
elif args[:2] == ["plugin", "list"]:
    v = lambda m: "1.1.0" if os.path.exists(os.path.join(home, m)) else "1.0.0"
    print(json.dumps([
        {"id": "neckbeard@neckbeard", "version": v("updated-user"), "scope": "user"},
        {"id": "neckbeard@neckbeard", "version": v("updated-notes"), "scope": "project", "projectPath": notes},
        {"id": "neckbeard@neckbeard", "version": "0.9.0", "scope": "project", "projectPath": os.path.join(home, "gone")},
        {"id": "neckbeard@neckbeard", "version": "0.9.0", "scope": "project", "projectPath": notes + "-wt"},
        {"id": "other@else", "version": "3.0.0", "scope": "user"}]))
elif args[:2] == ["plugin", "update"]:
    cwd = os.path.realpath(os.getcwd())
    if cwd == os.path.realpath(home):
        open(os.path.join(home, "updated-user"), "w").close()
    elif cwd == os.path.realpath(notes) and not os.environ.get("FAKE_STAY_OLD"):
        open(os.path.join(home, "updated-notes"), "w").close()
'''

fail = checks = 0
SRC = lambda home: os.path.join(home, ".claude", "plugin-src", "neckbeard")
head = lambda home: subprocess.run(["git", "rev-parse", "HEAD"], cwd=SRC(home), capture_output=True, text=True).stdout.strip() if os.path.isdir(SRC(home)) else None


def chk(name, got, want):
    global fail, checks
    checks += 1
    ok = got == want
    fail += not ok
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + ("" if ok else f": {got!r}, wanted {want!r}"))


def git(*a, cwd):
    return subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def world():
    """A fresh fake HOME. Returns (home, sha of the release, sha one commit before it)."""
    home = os.path.realpath(tempfile.mkdtemp())
    os.makedirs(os.path.join(home, "bin"))
    with open(os.path.join(home, "bin", "claude"), "w") as f:
        f.write(FAKE_CLAUDE)
    os.chmod(os.path.join(home, "bin", "claude"), 0o755)
    ident = ["-c", "user.name=t", "-c", "user.email=t@example.com"]
    work = os.path.join(home, "work")
    os.makedirs(work)
    git("init", "-q", "-b", "main", cwd=work)
    with open(os.path.join(work, "README.md"), "w") as f:
        f.write("one\n")
    git("add", ".", cwd=work)
    git(*ident, "commit", "-q", "-m", "one", cwd=work)
    old = git("rev-parse", "HEAD", cwd=work)
    with open(os.path.join(work, "README.md"), "w") as f:
        f.write("two\n")
    git(*ident, "commit", "-q", "-am", "two", cwd=work)
    new = git("rev-parse", "HEAD", cwd=work)
    git("clone", "-q", "--bare", work, os.path.join(home, "origin.git"), cwd=home)
    git("clone", "-q", os.path.join(home, "origin.git"), SRC(home), cwd=home)
    notes = os.path.join(home, "proj", "notes")
    os.makedirs(notes)
    git("init", "-q", "-b", "main", cwd=notes)
    git(*ident, "commit", "-q", "--allow-empty", "-m", "n", cwd=notes)
    git("worktree", "add", "-q", notes + "-wt", cwd=notes)
    return home, new, old


def run(home, sha, url=None, **env):
    e = dict(os.environ, HOME=home, PATH=os.path.join(home, "bin") + os.pathsep + os.environ["PATH"], **env)
    r = subprocess.run(["bash", DEPLOY, "1.1.0", sha] + ([url] if url else []), env=e, capture_output=True, text=True)
    log = open(os.path.join(home, "claude.log")).read() if os.path.exists(os.path.join(home, "claude.log")) else ""
    return r.returncode, r.stdout + r.stderr, log


print("-- deploy-host.sh --")

home, new, old = world()
code, out, log = run(home, new)
chk("a released export deploys: exit 0, and it says so", (code, "== deployed" in out), (0, True))
chk("each install is updated from its own folder, and a gone folder is skipped",
    sorted(l.split("\t")[0] for l in log.splitlines() if "plugin update" in l),
    sorted([home, os.path.join(home, "proj", "notes"), os.path.join(home, "proj", "notes-wt")]))
chk("a stale worktree record is a note, not a failure",
    ("note 0.9.0  project " + os.path.join(home, "proj", "notes-wt") in out, "FAIL" in out), (True, False))
shutil.rmtree(home)

home, new, old = world()
git("reset", "-q", "--hard", old, cwd=SRC(home))
code, out, log = run(home, new)
chk("an export one commit behind is fast-forwarded to the release",
    (code, head(home)), (0, new))
shutil.rmtree(home)

home, new, old = world()
with open(os.path.join(SRC(home), "README.md"), "a") as f:
    f.write("unreleased edit\n")
code, out, log = run(home, new)
chk("an export with uncommitted changes is refused before any install is touched",
    (code, "uncommitted changes" in out, "plugin update" in log), (1, True, False))
shutil.rmtree(home)

home, new, old = world()
code, out, log = run(home, new, FAKE_STAY_OLD="1")
chk("an install still on the old version fails the deploy, naming it",
    (code, "FAIL 1.0.0  project " + os.path.join(home, "proj", "notes") + " (wanted 1.1.0)" in out), (1, True))
shutil.rmtree(home)

home, new, old = world()
code, out, log = run(home, new, FAKE_SOURCE="none")
chk("no neckbeard marketplace is a failure, not a quiet success",
    (code, "no neckbeard marketplace" in out), (1, True))
shutil.rmtree(home)

home, new, old = world()
code, out, log = run(home, new, FAKE_SOURCE="github")
chk("a GitHub-sourced marketplace needs no checkout, and still deploys",
    (code, "marketplace update neckbeard" in log, "== deployed" in out), (0, True, True))
shutil.rmtree(home)

home, new, old = world()
work = os.path.join(home, "work")
git("checkout", "-q", "-b", "feature/x", cwd=work)
with open(os.path.join(work, "README.md"), "a") as f:
    f.write("unreleased edit in the working checkout\n")
code, out, log = run(home, new)
chk("the working checkout on another branch, edited, changes nothing: the export deploys",
    (code, "== deployed" in out, head(home)), (0, True, new))
shutil.rmtree(home)

home, new, old = world()
code, out, log = run(home, new, FAKE_PATH=os.path.join(home, "work"))
chk("a marketplace that loads from the working checkout fails with the switch steps and touches no install",
    (code, "loads from " + os.path.join(home, "work") in out, "claude plugin marketplace add " + SRC(home) in out, "plugin update" in log), (1, True, True, False))
shutil.rmtree(home)

home, new, old = world()
shutil.rmtree(SRC(home))
code, out, log = run(home, new, url=os.path.join(home, "origin.git"))
chk("a missing export is cloned from the origin URL, then deployed",
    (code, "== deployed" in out, head(home)), (0, True, new))
shutil.rmtree(home)

home, new, old = world()
shutil.rmtree(SRC(home))
code, out, log = run(home, new)
chk("a missing export with no URL fails, says so, and prints the one-time clone step",
    (code, "no origin URL" in out, "git clone <that host's own origin URL> " + SRC(home) in out), (1, True, True))
shutil.rmtree(home)

home, new, old = world()
git("-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-q", "--allow-empty", "-m", "local", cwd=SRC(home))
code, out, log = run(home, new)
chk("an export with a commit of its own on top of the release is refused before any install is touched",
    (code, "is ahead of" in out, "plugin update" in log), (1, True, False))
shutil.rmtree(home)

home, new, old = world()
code, out, log = run(home, "0" * 40)
chk("a sha that is not on origin/main is refused before any install is touched",
    (code, "isn't on" in out, "plugin update" in log), (1, True, False))
shutil.rmtree(home)

print(f"\n{checks - fail} passed, {fail} failed")
sys.exit(1 if fail else 0)
