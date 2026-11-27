#!/usr/bin/env python3
"""tools/vet names the target's commit and remote and says when a tracked file differs from HEAD, without running anything the
target's own git config or attributes name: an fsmonitor command, a filter driver, or a submodule's config.

Each target here is a repo whose config names a command that writes a marker file; vet runs with --facts (no model call) and the
marker must not appear. A plain `git status` in the same target is run last, to see that the trap is real.

    python3 tools/test_vet_target_git.py
"""
import os, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
VET = os.environ.get("VET_SCRIPT", os.path.join(HERE, "vet"))
ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.com",
           GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
fail = checks = 0


def chk(name, got, want):
    global fail, checks
    checks += 1
    ok = got == want
    fail += not ok
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + ("" if ok else f": {got!r}, wanted {want!r}"))


def git(*a, cwd):
    return subprocess.run(["git", "-c", "protocol.file.allow=always", *a], cwd=cwd, env=ENV, capture_output=True, text=True, check=True).stdout.strip()


def put(path, text, mode=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    if mode:
        os.chmod(path, mode)


def repo(top, *init):
    """A one-commit plugin repo at top, with a GitHub remote."""
    os.makedirs(top)
    git("init", "-q", "-b", "main", *init, cwd=top)
    put(os.path.join(top, ".claude-plugin", "plugin.json"), '{"name": "sample", "version": "0.1.0"}\n')
    put(os.path.join(top, "skills", "hello", "SKILL.md"), "---\nname: hello\ndescription: Says hello.\n---\n\nAlways say hello first.\n")
    put(os.path.join(top, "notes.txt"), "one\n")
    git("add", ".", cwd=top)
    git("commit", "-q", "-m", "one", cwd=top)
    git("remote", "add", "origin", "git@github.com:o/sample.git", cwd=top)


def stale(path):
    """Same bytes, an older mtime: git must reread the file to know it is unchanged, which is when it runs a clean filter."""
    old = time.time() - 3600
    os.utime(path, (old, old))


def vet(tmp, target):
    """The report's header line."""
    out = os.path.join(tmp, "report.md")
    if os.path.exists(out):
        os.remove(out)
    subprocess.run([VET, target, out, "--facts"], env=ENV, capture_output=True, text=True, timeout=300)
    line = open(out, encoding="utf-8").read().split("\n")[2] if os.path.exists(out) else ""
    if "made by neckbeard" not in line:
        chk(f"vet wrote a report with its header for {target}", line, "a header line")
    return line


def world():
    tmp = os.path.realpath(tempfile.mkdtemp())
    marker = os.path.join(tmp, "ran")
    script = os.path.join(tmp, "trap.sh")
    put(script, f"#!/bin/sh\necho x >> '{marker}'\ncat 2>/dev/null\n", 0o755)
    return tmp, os.path.join(tmp, "target"), marker, script


def sprung(marker, target):
    """vet left the marker unwritten; then a plain status in the target writes it, so the case can fail."""
    by_vet = os.path.exists(marker)
    stale(os.path.join(target, "notes.txt"))
    subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=target, env=ENV, capture_output=True, stdin=subprocess.DEVNULL)
    return by_vet, os.path.exists(marker)


def header_of(line, target):
    sha = git("rev-parse", "--short", "HEAD", cwd=target)
    return ("[o/sample](https://github.com/o/sample)" in line, f"@ `{sha}`" in line)


print("-- a plain repo --")
tmp, target, marker, script = world()
repo(target)
stale(os.path.join(target, "notes.txt"))
line = vet(tmp, target)
chk("a clean target: the header names its remote and commit", header_of(line, target), (True, True))
chk("a clean target with a stale mtime is not called changed", "uncommitted" in line, False)
index = open(os.path.join(target, ".git", "index"), "rb").read()
vet(tmp, target)
chk("vet leaves the target's index as it was", open(os.path.join(target, ".git", "index"), "rb").read() == index, True)
put(os.path.join(target, "notes.txt"), "two\n")
chk("a changed tracked file adds + uncommitted changes", "+ uncommitted changes`" in vet(tmp, target), True)
git("add", "notes.txt", cwd=target)
chk("so does a staged one", "+ uncommitted changes`" in vet(tmp, target), True)
chk("and a target that is a subfolder of the repo", "+ uncommitted changes`" in vet(tmp, os.path.join(target, "skills")), True)
git("worktree", "add", "-q", os.path.join(tmp, "wt"), cwd=target)
chk("a linked worktree is read as clean", "uncommitted" in vet(tmp, os.path.join(tmp, "wt")), False)
put(os.path.join(tmp, "wt", "notes.txt"), "three\n")
chk("and as changed when it is", "+ uncommitted changes`" in vet(tmp, os.path.join(tmp, "wt")), True)
shutil.rmtree(tmp)

print("-- a config that points elsewhere, and a missing index --")
tmp, target, marker, script = world()
repo(target)
put(os.path.join(tmp, "other", "notes.txt"), "not the target's file\n")
git("config", "core.worktree", os.path.join(tmp, "other"), cwd=target)
chk("the target's core.worktree does not choose the folder compared", "uncommitted" in vet(tmp, target), False)
git("config", "--unset", "core.worktree", cwd=target)
os.remove(os.path.join(target, ".git", "index"))
chk("a repo with no index is called changed, as git status would", "+ uncommitted changes`" in vet(tmp, target), True)
shutil.rmtree(tmp)

print("-- core.fsmonitor --")
tmp, target, marker, script = world()
repo(target)
git("config", "core.fsmonitor", script, cwd=target)
stale(os.path.join(target, "notes.txt"))
line = vet(tmp, target)
chk("vet runs no fsmonitor command, and a plain status would", sprung(marker, target), (False, True))
chk("the header still names the remote and commit", header_of(line, target), (True, True))
shutil.rmtree(tmp)

print("-- a filter driver --")
tmp, target, marker, script = world()
repo(target)
put(os.path.join(target, ".gitattributes"), "*.txt filter=trap\n")
git("add", ".gitattributes", cwd=target)
git("commit", "-q", "-m", "attributes", cwd=target)
git("config", "filter.trap.clean", script, cwd=target)
git("config", "filter.trap.required", "true", cwd=target)
stale(os.path.join(target, "notes.txt"))
line = vet(tmp, target)
chk("vet runs no clean filter, and a plain status would", sprung(marker, target), (False, True))
chk("the header still names the remote and commit", header_of(line, target), (True, True))
shutil.rmtree(tmp)

print("-- a submodule's own config --")
tmp, target, marker, script = world()
inner = os.path.join(tmp, "inner")
repo(inner)
repo(target)
git("submodule", "add", "-q", inner, "sub", cwd=target)
git("commit", "-q", "-m", "submodule", cwd=target)
git("config", "core.fsmonitor", script, cwd=os.path.join(target, "sub"))
stale(os.path.join(target, "sub", "notes.txt"))
line = vet(tmp, target)
chk("vet runs nothing a submodule's config names, and a plain status would", sprung(marker, target), (False, True))
shutil.rmtree(tmp)

print(f"test_vet_target_git: {'all passed' if not fail else str(fail) + ' of ' + str(checks) + ' failed'}")
sys.exit(1 if fail else 0)
