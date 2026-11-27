#!/usr/bin/env python3
"""tools/slim-tree: the slim copy of the plugin that each release publishes as branch `plugin`, which the plugin directory reads.

The publish cases run against a small repo and local bare remotes. The other cases build the slim tree from this repo's HEAD and
check the directory's limits, the README's links, that tools/vet writes the same facts report from it, and, where the claude CLI
is present, that `claude plugin validate` passes on it.

    python3 tools/test_slim.py
"""
import os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SLIM = os.path.join(HERE, "slim-tree")
fail = checks = 0


def chk(name, got, want):
    global fail, checks
    checks += 1
    ok = got == want
    fail += not ok
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + ("" if ok else f": {got!r}, wanted {want!r}"))


ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.com")


def git(*a, cwd):
    return subprocess.run(["git", *a], cwd=cwd, env=ENV, capture_output=True, text=True, check=True).stdout.strip()


def put(root, path, text):
    full = os.path.join(root, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(text)


def slim(*a, cwd, **env):
    """Run tools/slim-tree in cwd; a missing tool reads as exit 127 with no output, so every case fails by name."""
    if not os.path.isfile(SLIM):
        return 127, ""
    r = subprocess.run([sys.executable, SLIM, *a], cwd=cwd, env=dict(ENV, **env), capture_output=True, text=True, timeout=300)
    return r.returncode, r.stdout + r.stderr


SET = """# a test set
include .claude-plugin
include assets/in.png
include tools
include README.md
exclude tools/test_*.py   # tests
exclude tools/fixtures    # fixtures
"""

README = """![logo](./assets/logo.png) ![bundled](./assets/in.png)

[![badge](https://img.shields.io/x)](docs/report.md) [kept](tools/run) [gone](docs/a.md#part) [here](#top) [web](https://x.org/y)

```
[in a fence](docs/a.md)
```
"""

WANT_README = """![logo](https://raw.githubusercontent.com/o/r/v1.0.0/assets/logo.png) ![bundled](./assets/in.png)

[![badge](https://img.shields.io/x)](https://github.com/o/r/blob/v1.0.0/docs/report.md) [kept](tools/run) [gone](https://github.com/o/r/blob/v1.0.0/docs/a.md#part) [here](#top) [web](https://x.org/y)

```
[in a fence](docs/a.md)
```
"""


def world():
    """A repo tagged v1.0.0 holding files in and out of the set, and two bare remotes."""
    home = os.path.realpath(tempfile.mkdtemp())
    work = os.path.join(home, "work")
    os.makedirs(work)
    git("init", "-q", "-b", "main", cwd=work)
    for path, text in (("tools/slim-set", SET), ("README.md", README), (".claude-plugin/plugin.json", '{"name": "x", "version": "1.0.0"}\n'),
                       ("tools/run", "#!/bin/sh\n"), ("tools/test_x.py", "x\n"), ("tools/fixtures/f", "f\n"), ("docs/a.md", "a\n"),
                       ("assets/logo.png", "png\n"), ("assets/in.png", "png\n")):
        put(work, path, text)
    os.chmod(os.path.join(work, "tools", "run"), 0o755)
    git("add", ".", cwd=work)
    git("commit", "-q", "-m", "one", cwd=work)
    git("tag", "v1.0.0", cwd=work)
    for r in ("origin", "mirror"):
        git("init", "-q", "--bare", os.path.join(home, r + ".git"), cwd=home)
        git("remote", "add", r, os.path.join(home, r + ".git"), cwd=work)
    return home, work


def at(home, remote, *a):
    r = subprocess.run(["git", "-C", os.path.join(home, remote + ".git"), *a], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def files(home, remote):
    return at(home, remote, "ls-tree", "-r", "--name-only", "refs/heads/plugin").split()


print("-- publish --")
home, work = world()
code, out = slim("publish", "v1.0.0", "--repo", "o/r", cwd=work, REMOTES="origin mirror")
chk("the first publish exits 0", code, 0)
LISTED = [".claude-plugin/plugin.json", "README.md", "assets/in.png", "tools/run", "tools/slim-set"]
chk("each remote's plugin branch holds exactly the listed files", (files(home, "origin"), files(home, "mirror")), (LISTED, LISTED))
chk("the first commit is a root commit", at(home, "origin", "rev-list", "--count", "refs/heads/plugin"), "1")
chk("README.md is the rewritten one", at(home, "origin", "show", "refs/heads/plugin:README.md"), WANT_README.strip())
chk("another file is the tag's own, mode included", at(home, "origin", "ls-tree", "refs/heads/plugin", "tools/run"), git("ls-tree", "v1.0.0", "tools/run", cwd=work))
first = at(home, "origin", "rev-parse", "refs/heads/plugin")
code, out = slim("publish", "v1.0.0", "--repo", "o/r", cwd=work, REMOTES="origin mirror")
chk("publishing the same tag again adds no commit", (code, at(home, "origin", "rev-parse", "refs/heads/plugin")), (0, first))
put(work, "tools/new", "n\n")
git("add", ".", cwd=work)
git("commit", "-q", "-m", "two", cwd=work)
git("tag", "v1.1.0", cwd=work)
code, out = slim("publish", "v1.1.0", "--repo", "o/r", cwd=work, REMOTES="origin mirror")
chk("the next release adds one commit on the branch's last one", (code, at(home, "origin", "rev-parse", "refs/heads/plugin^")), (0, first))
chk("and its tree is the new slim copy", "tools/new" in files(home, "mirror"), True)
second = at(home, "origin", "rev-parse", "refs/heads/plugin")
code, out = slim("publish", "v1.0.0", "--repo", "o/r", "--strict", cwd=work, REMOTES="origin mirror")
chk("an older tag is refused, so a rerun can't take the branch back", (code, "v1.1.0 is newer" in out, at(home, "origin", "rev-parse", "refs/heads/plugin")), (1, True, second))
shutil.rmtree(home)

print("-- a push that fails --")
home, work = world()
git("remote", "add", "broken", os.path.join(home, "nowhere.git"), cwd=work)
code, out = slim("publish", "v1.0.0", "--repo", "o/r", cwd=work, REMOTES="broken origin")
chk("the release's step still exits 0", code, 0)
chk("it warns, naming the remote and the rerun command", ("broken" in out, "make slim-push TAG=v1.0.0" in out), (True, True))
chk("the other remote still got the branch", files(home, "origin"), LISTED)
code, out = slim("publish", "v1.0.0", "--repo", "o/r", "--strict", cwd=work, REMOTES="broken origin")
chk("the rerun target's --strict exits 1", code, 1)
code, out = slim("publish", "v9.9.9", "--repo", "o/r", cwd=work, REMOTES="origin")
chk("a tag that does not exist warns and exits 0", (code, "v9.9.9" in out), (0, True))
shutil.rmtree(home)

print("-- limits --")
home, work = world()
chk("a tree within the limits passes", slim("check", "HEAD", cwd=work)[0], 0)
put(work, "tools/big", "x" * (256 * 1024 + 1))
put(work, "tools/pic.png", "x" * (256 * 1024 + 1))
put(work, "tools/huge.png", "x" * (5 * 1024 * 1024 + 1))
os.symlink("run", os.path.join(work, "tools", "link"))
for i in range(520):
    put(work, f"tools/many/{i}", "x\n")
git("add", ".", cwd=work)
git("commit", "-q", "-m", "over", cwd=work)
code, out = slim("check", "HEAD", cwd=work)
chk("a file over 256 KiB, a symlink and over 512 files each fail it",
    (code, "tools/big" in out, "tools/link" in out, "512" in out), (1, True, True, True))
chk("an image may pass 256 KiB, and no file may pass 5 MiB", ("tools/pic.png" in out, "tools/huge.png" in out), (False, True))
shutil.rmtree(home)

print("-- this repo's slim tree --")
tmp = os.path.realpath(tempfile.mkdtemp())
tree, full = os.path.join(tmp, "slim"), os.path.join(tmp, "full")
os.makedirs(full)
subprocess.run(f"git -C '{ROOT}' archive HEAD | tar -x -C '{full}'", shell=True, check=True)
code, out = slim("check", "HEAD", cwd=ROOT)
chk("it is within the directory's limits and its README links resolve" + ("" if code == 0 else f" ({out.strip()[-300:]})"), code, 0)
code, out = slim("build", "HEAD", tree, cwd=ROOT)
chk("it builds", code, 0)
chk("it carries the icon, the logo, the skill and vet's default reader, and no fixtures or tests",
    [os.path.exists(os.path.join(tree, p)) for p in (".claude-plugin/icon.png", "assets/logo.webp", "skills/neckbeard/SKILL.md", "examples/reader/CLAUDE.md", "tools/fixtures", "tools/test_vet.py")],
    [True, True, True, True, False, False])
links = []
if os.path.isfile(os.path.join(tree, "README.md")):
    fenced = False
    for line in open(os.path.join(tree, "README.md"), encoding="utf-8"):
        if line.lstrip().startswith("```"):
            fenced = not fenced
        elif not fenced:
            links += re.findall(r"\]\(([^)\s]+)", line)
relative = [t.split("#")[0] for t in links if not re.match(r"[a-z][a-z0-9+.-]*:|#", t)]
chk("every relative link in its README names a file in it", (bool(links), [t for t in relative if not os.path.exists(os.path.join(tree, t))]), (True, []))

sample = os.path.join(tmp, "sample")
put(sample, ".claude-plugin/plugin.json", '{"name": "sample", "version": "0.1.0"}\n')
put(sample, "skills/hello/SKILL.md", "---\nname: hello\ndescription: Says hello.\n---\n\nAlways say hello first.\n")
reports = []
for i, checkout in enumerate((full, tree)):
    out_path = os.path.join(tmp, f"out{i}", "report.md")
    if os.path.isfile(os.path.join(checkout, "tools", "vet")):
        subprocess.run([os.path.join(checkout, "tools", "vet"), sample, out_path, "--facts"], capture_output=True, text=True, timeout=300)
    text = open(out_path, encoding="utf-8").read() if os.path.exists(out_path) else f"no report from {i}"
    reports.append(re.sub(r"`\d{4}-\d{2}-\d{2}`", "`DATE`", text))
chk("tools/vet --facts writes the same report from the slim tree as from the full repo, the date aside", reports[1] == reports[0] and reports[0].startswith("# "), True)

if shutil.which("claude"):
    r = subprocess.run(["claude", "plugin", "validate", tree], capture_output=True, text=True, timeout=300) if os.path.isdir(tree) else None
    chk("claude plugin validate passes on it, with its icon found", r is not None and r.returncode == 0 and "ICON_MISSING" not in r.stdout + r.stderr, True)
else:
    print("  skip  claude plugin validate: no claude CLI on this machine")
shutil.rmtree(tmp)

print("-- the release step --")
make = open(os.path.join(ROOT, "Makefile"), encoding="utf-8").read()
recipe = make.split("\nrelease: ", 1)[1].split("\n\n", 1)[0]
chk("make release publishes the slim branch, after the GitHub Release and without --strict",
    ("slim-tree publish" in recipe, 0 <= recipe.find("gh release create") < recipe.find("slim-tree publish"), "--strict" in recipe), (True, True, False))
chk("make slim-push reruns it alone, with --strict", re.search(r"^slim-push:.*\n(\t.*\n)*?\t.*slim-tree publish .*--strict", make, re.M) is not None, True)
chk("both pass the release's own remote list and repo",
    len(re.findall(r'REMOTES="\$\(REMOTES\)" \$\(PYTHON\) tools/slim-tree publish .*--repo \$\(GITHUB_REPO\)', make)), 2)

print(f"test_slim: {'all passed' if not fail else str(fail) + ' of ' + str(checks) + ' failed'}")
sys.exit(1 if fail else 0)
