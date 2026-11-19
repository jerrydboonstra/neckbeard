#!/usr/bin/env python3
"""tools/guard.sh, the private-words check `make release` runs before it pushes anything.

Each case builds a scratch git repo, writes a word list outside it, and runs the script (or `make guard`) there. The
words are made-up ones. Nothing here reads neckbeard's own tree for words, calls a model or uses the network.

    python3 tools/test_guard.py
"""
import os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUARD = os.path.join(ROOT, "tools", "guard.sh")
WORD = "quuxbert"
fail = checks = 0


def chk(name, got, want):
    global fail, checks
    checks += 1
    ok = got == want
    fail += not ok
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + ("" if ok else f": {got!r}, wanted {want!r}"))


def sh(cwd, *a):
    subprocess.run(a, cwd=cwd, capture_output=True, check=True)


def scratch(files, words=None, track=True):
    """A scratch repo holding `files` (name -> bytes), and a word list beside it (a path outside the repo, or None)."""
    d = tempfile.mkdtemp()
    repo = os.path.join(d, "repo")
    os.makedirs(repo)
    sh(repo, "git", "init", "-q")
    for name, data in files.items():
        os.makedirs(os.path.dirname(os.path.join(repo, name)), exist_ok=True)
        with open(os.path.join(repo, name), "wb") as f:
            f.write(data)
    if track:
        sh(repo, "git", "add", "-A")
    lst = None
    if words is not None:
        lst = os.path.join(d, "words.txt")
        with open(lst, "w") as f:
            f.write(words)
    return d, repo, lst


def guard(repo, lst, **env):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GUARD_")}
    if lst is not None:
        e["GUARD_WORDS"] = lst
    e.update(env)
    p = subprocess.run(["bash", GUARD], cwd=repo, env=e, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


print("the word check")
LIST = f"# a comment\n\nother\n{WORD}\n"
d, repo, lst = scratch({"notes.md": f"line one\nsay {WORD}, then stop\n".encode()}, LIST)
code, out, err = guard(repo, lst)
chk("a whole word in a tracked file exits 1 and prints file:line", (code, "notes.md:2" in out + err), (1, True))
chk("it names the list line (comments and blanks counted) and never the word", ("list line 4" in out + err, WORD in out + err), (True, False))
shutil.rmtree(d)

for label, text in [("inside a longer word (letters)", f"un{WORD}s\n"), ("touched by a digit", f"{WORD}2\n"),
                    ("touched by an underscore", f"_{WORD}\n"), ("in a different case", f"{WORD.upper()}\n")]:
    d, repo, lst = scratch({"a.txt": text.encode()}, LIST)
    chk(f"a listed word {label} exits 0", guard(repo, lst)[0], 0)
    shutil.rmtree(d)

d, repo, lst = scratch({"a.txt": f"{WORD}\n".encode()}, f"{WORD}\r\n")
chk("a list with Windows line ends still finds the word", guard(repo, lst)[0], 1)
shutil.rmtree(d)

d, repo, lst = scratch({"a.txt": f"a -{WORD} b\n{WORD}.y\n".encode()}, f"-{WORD}\n{WORD}.y\n")
code, out, err = guard(repo, lst)
chk("a word starting with a dash, and one with a dot (a fixed string, not a pattern), both match as written", (code, out.count("(list line")), (1, 2))
shutil.rmtree(d)

d, repo, lst = scratch({"a.txt": f"({WORD}).\n".encode()}, LIST)
chk("a word between punctuation is a whole word", guard(repo, lst)[0], 1)
shutil.rmtree(d)

d, repo, lst = scratch({"a.txt": b"clean\n", "b.txt": f"{WORD}\n".encode()}, LIST, track=False)
sh(repo, "git", "add", "a.txt")
chk("an untracked file is not read", guard(repo, lst)[0], 0)
shutil.rmtree(d)

d, repo, lst = scratch({"a.txt": b"clean\n"}, LIST)
chk("the list file, outside the repo, is never scanned", guard(repo, lst)[0], 0)
shutil.rmtree(d)

d, repo, lst = scratch({"blob.bin": b"\x00\x01" + WORD.encode() + b"\x00\n"}, LIST)
chk("a binary file holding a listed word exits 0", guard(repo, lst)[0], 0)
shutil.rmtree(d)

print("the list")
d, repo, lst = scratch({"a.txt": b"clean\n"})
code, out, err = guard(repo, None, GUARD_REQUIRE_WORDS="1")
chk("GUARD_REQUIRE_WORDS=1 with no GUARD_WORDS exits 1", code, 1)
code, out, err = guard(repo, None)
chk("neither set: exit 0 with a stderr line", (code, bool(err.strip())), (0, True))
code, out, err = guard(repo, os.path.join(d, "missing.txt"))
chk("GUARD_WORDS naming a missing file exits 2", code, 2)
shutil.rmtree(d)

d, repo, lst = scratch({"sub/a.txt": f"{WORD}\n".encode()}, LIST)
code, out, err = guard(os.path.join(repo, "sub"), lst)
chk("run from a subfolder it still searches the whole repo", (code, "sub/a.txt:1" in out), (1, True))
shutil.rmtree(d)

d, repo, lst = scratch({"a.txt": b"clean\n"}, LIST)
code, out, err = guard(repo, lst + "-gone")
chk("the unreadable-list message holds no path", (code, os.path.basename(d) in out + err, "unreadable" in err), (2, False, True))
code, out, err = guard(repo, "")
chk("an empty GUARD_WORDS is the same as unset", (code, bool(err.strip())), (0, True))
code, out, err = guard(repo, "", GUARD_REQUIRE_WORDS="1")
chk("an empty GUARD_WORDS with GUARD_REQUIRE_WORDS=1 exits 1", code, 1)
code, out, err = guard(repo, lst, GUARD_REQUIRE_WORDS="1")
chk("a clean tree with a list and GUARD_REQUIRE_WORDS=1 exits 0", code, 0)
shutil.rmtree(d)

print("make guard, and the release recipe")
d, repo, lst = scratch({"a.txt": f"{WORD}\n".encode()}, LIST)
os.makedirs(os.path.join(repo, "tools"))
if os.path.exists(GUARD):
    shutil.copy(GUARD, os.path.join(repo, "tools", "guard.sh"))
os.makedirs(os.path.join(repo, ".claude-plugin"))
shutil.copy(os.path.join(ROOT, ".claude-plugin", "plugin.json"), os.path.join(repo, ".claude-plugin"))
shutil.copy(os.path.join(ROOT, "Makefile"), repo)
p = subprocess.run(["make", "guard", f"PRIVATE_WORDS={lst}"], cwd=repo, capture_output=True, text=True)
chk("make guard passes PRIVATE_WORDS as GUARD_WORDS", (p.returncode != 0, "a.txt:1" in p.stdout + p.stderr, WORD in p.stdout + p.stderr), (True, True, False))
for req, want in [({}, 0), ({"GUARD_REQUIRE_WORDS": "1"}, 1)]:
    e = {k: v for k, v in os.environ.items() if not k.startswith("GUARD_")}
    e.update(req)
    p = subprocess.run(["make", "guard"], cwd=repo, env=e, capture_output=True, text=True)
    chk("make guard with PRIVATE_WORDS empty " + ("and GUARD_REQUIRE_WORDS=1 fails" if want else "skips and exits 0"),
        (p.returncode != 0, bool(p.stderr.strip())), (bool(want), True))
shutil.rmtree(d)

text = open(os.path.join(ROOT, "Makefile")).read()
m = re.search(r"^release:.*\n((?:\t.*\n)+)", text, re.M)
recipe = m.group(1) if m else ""
g, push = recipe.find("GUARD_REQUIRE_WORDS=1"), recipe.find("tools/release-push")
chk("the release recipe runs the guard with GUARD_REQUIRE_WORDS=1 before tools/release-push", (g != -1, push != -1, -1 < g < push), (True, True, True))
chk("the guard target sits outside the release recipe and has a help line", ("\nguard:" in text, "\nguard: ## " in text, "guard:" in recipe), (True, True, False))

print(f"\n{checks - fail} passed, {fail} failed")
sys.exit(1 if fail else 0)
