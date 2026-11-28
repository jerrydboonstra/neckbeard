#!/usr/bin/env python3
"""persist-tiers: the persistence scan tells a file in which it finds a write ("writes") from one that only names a home path
("mentions"), counts writes made through a shell variable assigned a home path in any shell file, and records both in
target.persistence_detail. Each case builds a small tree and reads its dossier in this process. The last check is the guard against
a second scan growing outside the shared one."""
import atexit, glob, os, re, shutil, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
NB = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(NB, "skills", "neckbeard"))
import inventory  # noqa: E402

fail = checks = 0


def chk(name, ok, detail=""):
    global fail, checks
    checks += 1
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        fail += 1


def tree(files):
    d = tempfile.mkdtemp(prefix="persist-tiers-")
    atexit.register(shutil.rmtree, d, True)
    for rel, text in files.items():
        p = os.path.join(d, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(text)
    return d


def target(files):
    return inventory.inventory_target(tree(files))


def tiers(files):
    """{path: tier} for the listed files; a listed file with no detail entry reads "untiered"."""
    t = target(files)
    detail = {e["path"]: e["tier"] for e in t.get("persistence_detail") or []}
    return {p: detail.get(p, "untiered") for p in t["persistence_candidates"]}


def one(text, name="a.sh"):
    return tiers({name: text}).get(name)


def each(label, want, cases, run=one):
    got = {c: run(c) for c in cases}
    wrong = {c: g for c, g in got.items() if g != want}
    chk(label, not wrong, f"want {want!r}, got {wrong}")


# ------------------------------------------------------------ comments and .replace
each("1. home-path text only on # comment lines is in neither list", None,
     ["#!/bin/sh\n# see ~/.config/x\n  # and \"$HOME/.cache/y\"\n", "// reads ~/.claude/settings\n"])
each("1. a home-path pattern on a code line, or on the #! line, is a mention", "mentions",
     ['#!/bin/sh\ncat "$HOME/.config/x"\n', "#!/home/u/.local/bin/sh\n", "x = 1  # ~/.config/x\n"])
each("2. a write on a # line inside a heredoc is a write", "writes", ["cat <<EOF\n# > ~/.foo\nEOF\n"])
each('3. s.replace() in a file without pathlib is in neither list', None, ['s = s.replace("a", "b")\n'],
     run=lambda t: one(t, "a.py"))
each("4. os.replace(), and .replace() in a file that uses pathlib, are writes", "writes",
     ["import os\nos.replace(a, b)\n", "from pathlib import Path\np.replace(t)\n", "import pathlib\np.replace(t)\n",
      "q = Path(x)\nq.replace(t)\n"], run=lambda t: one(t, "a.py"))
each("4. the other write calls still count as writes", "writes",
     ["p.rename(t)\n", "p.write_text(s)\n", "shutil.rmtree(d)\n", "open(f, 'w')\n"], run=lambda t: one(t, "a.py"))

# ------------------------------------------------------------ writes through a shell variable
SET = "STATE=$HOME/.local/state/x\n"
got = tiers({"a.sh": SET, "b.sh": 'mkdir -p "$STATE"\ncat > "$STATE/f"\n'})
chk("5. the file that writes through another file's variable writes, the one that assigns it mentions",
    got == {"a.sh": "mentions", "b.sh": "writes"}, got)


def through(command):
    return tiers({"a.sh": SET, "b.sh": command + "\n"}).get("b.sh")


each("5. every write target through the variable", "writes", [
    'echo > "$STATE/f"', "echo >> $STATE/f", "echo >${STATE}/f", 'echo 2> "${STATE}/log"', 'mkdir -p "$STATE"', "touch a $STATE/f",
    "tee -a $STATE/f", 'rm -rf "$STATE"', 'cp a b "$STATE/"', "mv a $STATE", 'cp a "$STATE/my file" 2>/dev/null', 'cp a "$STATE" # keep',
    'x=$(mkdir -p "$STATE")', "true && rm $STATE/f", "if x; then touch $STATE; fi", 'mkdir -p \\\n  "$STATE"', 'cp a "$STATE" 2>&1 | cat',
    '# mkdir "$STATE"', 'sudo mkdir -p "$STATE"', 'if mkdir "$STATE"; then', 'cp "a;b" $STATE/f', 'cp "a|b && c" "$STATE"',
    "mkdir 'x;y' $STATE", "echo don't; cp a $STATE; echo 'b'",
], run=through)
each("5. a closing quote or bracket around cp and mv does not hide the target", "writes", [
    "sh -c 'cp template \"$STATE/settings.json\"'", '( cp template "$STATE/settings.json" )', 'x=$( mv a "$STATE/f" )',
    'echo "$( cp a "$STATE/f" )"', "sh -c 'cp t $STATE/f' sh", "echo $(cp t $STATE) done", 'x=` mv a "$STATE/f" `',
    '{ cp a "$STATE/f" }', 'ssh h "cp a $STATE/f"',
], run=through)
each("5. a redirect continued onto the next line keeps its target", "writes", [
    'cat template > \\\n  "$STATE/settings.json"', 'cat template >> \\\n  "$STATE/settings.json"', "cat t >\\\n$STATE/f",
], run=through)
each("5. reading through the variable is not a write", None, [
    'cat "$STATE/f"', 'cp "$STATE/f" /dev/null', 'mv "$STATE/f" ./here', "ls $STATE; rm ./x", "grep x < $STATE/f",
    "mkdir -p ./d && ls $STATE", 'tee ./log < "$STATE/f"', '( cp "$STATE/f" ./here )', 'x=$( mv "$STATE/f" ./y )',
], run=through)


def assigned(line):
    return tiers({"a.sh": line + "\n", "b.sh": 'touch "$V"\n'}).get("b.sh")


each("5. every assignment form collects the variable", "writes", [
    "V=$HOME/x", 'V="$HOME/x y"', "V='~/x'", "local V=~/x", "export V=${HOME}/x", "readonly V=$XDG_STATE_HOME", "declare -x -r V=/home/u/x",
    "A=1 V=/Users/u/x", "local a b=2 V=$HOME/x", 'V="${X:-$HOME/.local/state}"', "V=${XDG_CACHE_HOME:-/tmp}", "# V=$HOME/x",
    "if true; then V=$HOME/x; fi", 'V="$HOME"/.local/state/x', 'V="${HOME}"/x', "V='/home'/u/x",
], run=assigned)
each("5. a value with no home path literal does not collect the variable", None, [
    "V=$HOME", "V=/tmp/x", "V=https://example.com/home/u/x", "V=file:///Users/u/x", "V=/home/<user>/x", "V=./rel/~x",
    "run --V=$HOME/x", 'V="$HOME"', 'V="$HOME" x/y',
], run=assigned)
got = tiers({"setup": "#!/usr/bin/env bash\nV=$HOME/x\n", "use": "#!/bin/sh\ntouch $V\n", "z.zsh": "rm $V\n",
             "n.py": "touch $V\n", "other": "#!/usr/bin/env fish\ntouch $V\n"})
chk("5. shell files are .sh, .bash, .zsh and extension-less files whose #! names sh, bash or zsh",
    got == {"use": "writes", "z.zsh": "writes"}, got)

got = one('f() {\n  local st=$HOME/.local/state/x\n  cat "$st/f"\n}\n')
chk("6. a variable assigned a home path and only read through is a mention", got == "mentions", got)
got = tiers({"a.sh": "st=$HOME/.local/state/x\n", "b.sh": 'echo x > "$status"\ntouch ${stx} $st_dir\n'})
chk("6b. st does not match $status, ${stx} or $st_dir", got == {"a.sh": "mentions"}, got)

# ------------------------------------------------------------ the dossier
FILES = {"z/b.sh": "touch $HOME/x\n", "a.sh": "cat ~/.config/y\n", "m.py": "open(f, 'w')\n"}
WANT = [{"path": "a.sh", "tier": "mentions"}, {"path": "m.py", "tier": "writes"}, {"path": "z/b.sh", "tier": "writes"}]
for label, extra in (("a plain folder", {}), ("a plugin", {".claude-plugin/plugin.json": '{"name": "p", "version": "1.0.0"}\n'})):
    t = target({**FILES, **extra})
    chk(f"7. {label}: persistence_detail has one entry per persistence_candidates path, in the same order",
        t.get("persistence_detail") == WANT and t["persistence_candidates"] == [e["path"] for e in WANT],
        (t.get("persistence_candidates"), t.get("persistence_detail")))
    inventory.add_read_status(t)
    chk(f"7. {label}: persistence_detail has no read_status entry", "persistence_candidates" in t["read_status"]
        and "persistence_detail" not in t["read_status"], sorted(t["read_status"]))
t = inventory.inventory_target(os.path.join(tree({"CLAUDE.md": "Do x.\n"}), "CLAUDE.md"))
chk("7. a rule-file target has neither key", "persistence_detail" not in t and "persistence_candidates" not in t, sorted(t))

setters = [os.path.basename(p) for p in glob.glob(os.path.join(NB, "skills", "neckbeard", "*.py")) if '"persistence_candidates":' in open(p).read()]
chk("7. only persistence_keys sets persistence_candidates, so no builder sets it without the detail", setters == ["inventory_persist.py"], setters)

got = inventory.settings_writers(tree({"mention.sh": 'cat "$HOME/.claude/settings.json"\n', "write.py": "open('settings.json', 'w')\n"}))
chk("8. settings_writers returns only files that write", got == ["write.py"], got)

# ------------------------------------------------------------ guard: one scan, in one place
SCAN = ("inventory_hooks.py", "inventory_persist.py", "hook_shell.py")
SECOND_SCAN = re.compile(r"/dev/(?:null|stdout|stderr|tty|fd)|re\.compile\(.*(?:writeFileSync|write_text|>>\?|shutil)")


def second_scans(files):
    out = []
    for path in files:
        with open(path) as f:
            out += [f"{os.path.relpath(path, NB)}:{n}" for n, line in enumerate(f, 1) if SECOND_SCAN.search(line)]
    return out


others = [p for p in glob.glob(os.path.join(NB, "skills", "neckbeard", "*.py")) if os.path.basename(p) not in SCAN]
others += [os.path.join(HERE, "part1"), os.path.join(HERE, "summary")]
hits = second_scans(others)
chk("guard: no device list or write pattern outside the shared scan", not hits, hits)
planted = tree({"x.py": 'if target == "/dev/null":\n', "y.py": 'W = re.compile(r">>?\\s*~")\n'})
chk("guard: the check finds a planted device literal and a planted write pattern (seen to fail)",
    len(second_scans(sorted(glob.glob(os.path.join(planted, "*.py"))))) == 2)

print(f"{checks - fail}/{checks} checks pass")
sys.exit(1 if fail else 0)
