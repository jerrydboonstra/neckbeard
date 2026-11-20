#!/usr/bin/env python3
"""tools/release-push and tools/ci-wait.sh, the push half of `make release`, run end to end.

A fake world holds two bare remotes (origin, standing for GitHub, and a mirror), a checkout on main with the release
commit, and a fake `gh` that logs what origin's main, tags and release branch held at the moment CI was read, then answers
with the CI result the case asks for. Each case checks the order: the release branch on GitHub first, CI read on that
commit, and only then main, the tag and the other remotes; a red CI leaves main alone.

    python3 tools/test_release.py
"""
import os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

FAKE_GH = r'''#!/usr/bin/env python3
import os, subprocess, sys
home = os.environ["FAKE_HOME"]
def ls(*a):
    return subprocess.run(["git", "-C", os.path.join(home, "origin.git"), *a], capture_output=True, text=True).stdout.strip()
with open(os.path.join(home, "gh.log"), "a") as f:
    rel = ls("rev-parse", "-q", "--verify", "refs/heads/release/v1.1.0")
    f.write("main=" + ls("rev-parse", "refs/heads/main") + " tags=" + ls("tag") + " rel=" + rel + " args=" + " ".join(sys.argv[1:]) + "\n")
mode = os.environ.get("FAKE_CI", "success")
if mode == "later":   # a run that is going on the first look and has passed on the second
    seen = os.path.join(home, "looks")
    n = len(open(seen).read()) if os.path.exists(seen) else 0
    open(seen, "a").write("x")
    mode = "success" if n >= 1 else "running"
if mode == "running":
    print("in_progress\t\thttps://example.com/run/3")
elif mode == "success":
    print("completed\tsuccess\thttps://example.com/run/1")
elif mode == "failure":
    print("completed\tfailure\thttps://example.com/run/2")
'''

fail = checks = 0


def chk(name, got, want):
    global fail, checks
    checks += 1
    ok = got == want
    fail += not ok
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + ("" if ok else f": {got!r}, wanted {want!r}"))


def git(*a, cwd):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *a],
                          cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def world():
    """A fresh fake HOME with origin and mirror both at commit one, and a checkout holding commit two on main."""
    home = os.path.realpath(tempfile.mkdtemp())
    os.makedirs(os.path.join(home, "bin"))
    with open(os.path.join(home, "bin", "gh"), "w") as f:
        f.write(FAKE_GH)
    os.chmod(os.path.join(home, "bin", "gh"), 0o755)
    work = os.path.join(home, "work")
    os.makedirs(os.path.join(work, "tools"))
    for name in ("release-push", "ci-wait.sh"):
        shutil.copy(os.path.join(HERE, name), os.path.join(work, "tools", name))
    git("init", "-q", "-b", "main", cwd=work)
    with open(os.path.join(work, "f"), "w") as f:
        f.write("one\n")
    git("add", ".", cwd=work)
    git("commit", "-q", "-m", "one", cwd=work)
    for r in ("origin", "mirror"):
        git("clone", "-q", "--bare", work, os.path.join(home, r + ".git"), cwd=home)
        git("remote", "add", r, os.path.join(home, r + ".git"), cwd=work)
    with open(os.path.join(work, "f"), "w") as f:
        f.write("two\n")
    git("commit", "-q", "-am", "two", cwd=work)
    return home, work


def run(home, work, **env):
    # release-push makes the tag itself, so it needs an identity; useConfigOnly stops git guessing one on any machine
    ident = dict(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.com",
                 GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="user.useConfigOnly", GIT_CONFIG_VALUE_0="true")
    # a top-level environment, as in tools/test_make_hooks.py: under `make check` MAKELEVEL and MAKEFLAGS are set
    base = {k: v for k, v in os.environ.items() if k not in ("MAKELEVEL", "MAKEFLAGS", "MFLAGS")}
    e = dict(base, FAKE_HOME=home, PATH=os.path.join(home, "bin") + os.pathsep + os.environ["PATH"],
             CI_POLL="0", CI_GRACE="0", CI_REPO="o/r", VERSION="1.1.0", REMOTES="origin mirror", **ident, **env)
    try:
        r = subprocess.run(["bash", os.path.join(work, "tools", "release-push")], cwd=work, env=e, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:   # a wait with no bound never ends
        return 124, "timed out", ""
    log = open(os.path.join(home, "gh.log")).read() if os.path.exists(os.path.join(home, "gh.log")) else ""
    return r.returncode, r.stdout + r.stderr, log


def branch(home, remote, name="release/v1.1.0"):
    return subprocess.run(["git", "-C", os.path.join(home, remote + ".git"), "rev-parse", "-q", "--verify", "refs/heads/" + name],
                          capture_output=True, text=True).stdout.strip()


def head(home, remote):
    return subprocess.run(["git", "-C", os.path.join(home, remote + ".git"), "rev-parse", "refs/heads/main"],
                          capture_output=True, text=True).stdout.strip()


def tags(home, remote):
    return subprocess.run(["git", "-C", os.path.join(home, remote + ".git"), "tag"], capture_output=True, text=True).stdout.split()


print("-- release-push --")

home, work = world()
sha, before = git("rev-parse", "HEAD", cwd=work), head(home, "origin")
code, out, log = run(home, work)
chk("a passing CI releases: exit 0", code, 0)
chk("when CI was read, GitHub's main still held the old commit, the tag was not there, and release/v1.1.0 held the release",
    log.splitlines()[0].startswith(f"main={before} tags= rel={sha} ") if log else None, True)
chk("afterwards the release branch is gone from origin", branch(home, "origin"), "")
chk("the CI run was looked up by the release's sha", f"head_sha={sha}" in log, True)
chk("the tag and main reach origin and the mirror, and the tag points at the release",
    (head(home, "origin"), head(home, "mirror"), tags(home, "origin"), tags(home, "mirror"),
     git("rev-parse", "v1.1.0^{commit}", cwd=work)), (sha, sha, ["v1.1.0"], ["v1.1.0"], sha))
shutil.rmtree(home)

home, work = world()
before, before_o = head(home, "mirror"), head(home, "origin")
code, out, log = run(home, work, FAKE_CI="failure")
chk("a failing CI stops the release: exit 1, saying CI did not pass", (code, "CI didn't pass" in out), (1, True))
chk("a failing CI leaves no tag anywhere and the mirror untouched",
    (tags(home, "origin"), tags(home, "mirror"), head(home, "mirror"), git("tag", cwd=work)), ([], [], before, ""))
chk("a failing CI leaves GitHub's main alone and the release on release/v1.1.0, saying so",
    (head(home, "origin"), branch(home, "origin"), "main untouched" in out), (before_o, git("rev-parse", "HEAD", cwd=work), True))
shutil.rmtree(home)

home, work = world()
before = head(home, "mirror")
code, out, log = run(home, work, FAKE_CI="none")
chk("no CI run for the commit fails the release too, with no tag, the mirror untouched and origin's main unmoved",
    (code, tags(home, "mirror"), head(home, "mirror"), head(home, "origin")), (1, [], before, before))
chk("the wait for a missing run says CI starts when the release branch is pushed", "release branch is pushed" in out, True)
shutil.rmtree(home)

home, work = world()
code, out, log = run(home, work, FAKE_CI="later")
chk("a run still going on the first look is waited for, and the release goes through once it passes",
    (code, log.count("args=api"), tags(home, "mirror")), (0, 2, ["v1.1.0"]))
shutil.rmtree(home)

home, work = world()
before, before_o = head(home, "mirror"), head(home, "origin")
code, out, log = run(home, work, FAKE_CI="running", CI_WAIT="0")
chk("a run that never finishes ends the wait at CI_WAIT: exit 1, saying it has not finished, no tag, mirror and main untouched",
    (code, "hasn't finished" in out, tags(home, "mirror"), head(home, "mirror"), head(home, "origin"), git("tag", cwd=work)),
    (1, True, [], before, before_o, ""))
shutil.rmtree(home)

home, work = world()
git("tag", "-a", "v1.1.0", "-m", "old", "HEAD~1", cwd=work)
before = (head(home, "origin"), head(home, "mirror"))
code, out, log = run(home, work)
chk("a version whose tag is already on an older commit is refused as unbumped",
    (code, "bump the version" in out), (1, True))
chk("an unbumped version moves nothing: both remotes keep their main, no release branch is pushed, and CI is never read",
    ((head(home, "origin"), head(home, "mirror")), branch(home, "origin"), log), (before, "", ""))
shutil.rmtree(home)

home, work = world()
git("tag", "-a", "v1.1.0", "-m", "mine", cwd=work)
code, out, log = run(home, work)
chk("a tag already on the release commit is reused, not recreated, and the release goes through",
    (code, tags(home, "mirror"), "v1.1.0" in tags(home, "origin")), (0, ["v1.1.0"], True))
shutil.rmtree(home)

home, work = world()
git("push", "-q", "origin", "main", cwd=work)
git("checkout", "-q", "--detach", cwd=work)
code, out, log = run(home, work)
chk("a checkout that is not on main fails before anything is pushed", (code, tags(home, "mirror"), log), (1, [], ""))
shutil.rmtree(home)

home, work = world()
one = git("rev-parse", "HEAD~1", cwd=work)
git("push", "-q", "origin", f"{one}:refs/heads/release/v1.1.0", cwd=work)
code, out, log = run(home, work)
chk("a release branch left at an ancestor (a rerun after a fix) fast-forwards, and the release goes on",
    (code, tags(home, "mirror"), head(home, "origin"), branch(home, "origin")), (0, ["v1.1.0"], git("rev-parse", "HEAD", cwd=work), ""))
chk("the rerun's CI read saw the fast-forwarded branch", f"rel={git('rev-parse', 'HEAD', cwd=work)} " in log, True)
shutil.rmtree(home)

home, work = world()
git("checkout", "-q", "-b", "other", "HEAD~1", cwd=work)
with open(os.path.join(work, "g"), "w") as f:
    f.write("side\n")
git("add", ".", cwd=work)
git("commit", "-q", "-m", "side", cwd=work)
side = git("rev-parse", "HEAD", cwd=work)
git("push", "-q", "origin", f"{side}:refs/heads/release/v1.1.0", cwd=work)
git("checkout", "-q", "main", cwd=work)
before = (head(home, "origin"), head(home, "mirror"))
code, out, log = run(home, work)
chk("a release branch holding a commit that is not an ancestor is refused without force: exit 1, branch and both mains untouched, CI never read",
    (code, branch(home, "origin"), (head(home, "origin"), head(home, "mirror")), tags(home, "origin"), log), (1, side, before, [], ""))
chk("the refusal says how to go on", "delete" in out and "release/v1.1.0" in out, True)
shutil.rmtree(home)

def hook(home, remote, body):
    path = os.path.join(home, remote + ".git", "hooks", "update")
    with open(path, "w") as f:
        f.write("#!/bin/sh\n" + body + "\n")
    os.chmod(path, 0o755)


home, work = world()
hook(home, "origin", '[ "$3" = 0000000000000000000000000000000000000000 ] && exit 1; exit 0')   # origin refuses every delete
code, out, log = run(home, work)
chk("a refused delete of the release branch is a warning: exit 0, the tag and main are on both remotes",
    (code, "couldn't delete" in out, tags(home, "origin"), tags(home, "mirror"), head(home, "mirror")),
    (0, True, ["v1.1.0"], ["v1.1.0"], git("rev-parse", "HEAD", cwd=work)))
shutil.rmtree(home)

home, work = world()
before = head(home, "mirror")
hook(home, "origin", '[ "$1" = refs/heads/main ] && exit 1; exit 0')   # origin refuses main
code, out, log = run(home, work)
chk("origin refusing main after a green CI stops the release: exit 1, nothing on the mirror, the release branch is kept",
    (code, tags(home, "mirror"), head(home, "mirror"), branch(home, "origin") != ""), (1, [], before, True))
shutil.rmtree(home)

print("-- the workflow --")
wf = open(os.path.join(HERE, "..", ".github", "workflows", "self-check.yml")).read()
m = re.search(r"^on:\n  push:\n    branches: \[([^\]]*)\]", wf, re.M)
chk("CI runs on a push to main and to release/**", sorted(x.strip().strip("'\"") for x in m.group(1).split(",")) if m else None, ["main", "release/**"])

print(f"\n{checks - fail} passed, {fail} failed")
sys.exit(1 if fail else 0)
