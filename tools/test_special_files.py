#!/usr/bin/env python3
"""special-files: the inventory reads only regular files, so a named pipe, socket or device in a target can't block or flood it.
Every read that could block runs in a child process with a time limit, so this test ends even where the reader hangs."""
import atexit, json, os, shutil, socket, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
NB = os.path.dirname(HERE)
CODE = os.path.join(NB, "skills", "neckbeard")
fail = checks = 0


def chk(name, ok, detail=""):
    global fail, checks
    checks += 1
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        fail += 1


def tmp():
    d = tempfile.mkdtemp(prefix="special-")
    atexit.register(shutil.rmtree, d, True)
    return d


def child(code, *args):
    """CODE's printed JSON, run with the inventory importable; "hung" past 10 seconds."""
    try:
        r = subprocess.run([sys.executable, "-c", f"import json, os, sys\nsys.path.insert(0, {CODE!r})\nimport inventory_core\n" + code, *args],
                           capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        return "hung"
    return json.loads(r.stdout) if r.returncode == 0 else r.stderr[-300:]


def read(path, fn="read_text"):
    return child(f"v = inventory_core.{fn}(sys.argv[1])\nprint(json.dumps(v if v is None or not isinstance(v, str) else v[:20]))", path)


# ------------------------------------------------------------ the readers
d = tmp()
fifo, sock, reg, link, to_fifo = (os.path.join(d, n) for n in ("fifo", "sock", "reg.json", "link", "to-fifo"))
os.mkfifo(fifo)
s = socket.socket(socket.AF_UNIX)
here = os.getcwd()
os.chdir(d)   # a socket's path has a short limit: bind it by its name
s.bind("sock")
os.chdir(here)
with open(reg, "w") as f:
    f.write('{"a": 1}\n')
os.symlink(reg, link)
os.symlink(fifo, to_fifo)

for fn in ("read_text", "read_json"):
    for label, path in (("a named pipe", fifo), ("a link to a named pipe", to_fifo), ("a socket", sock), ("/dev/zero", "/dev/zero"),
                        ("/dev/null", "/dev/null"), ("a folder", d), ("a missing path", os.path.join(d, "no"))):
        got = read(path, fn)
        chk(f"2. {fn} of {label} returns None at once", got is None, got)
chk("3. read_text of a regular file and of a link to one", (read(reg), read(link)) == ('{"a": 1}\n', '{"a": 1}\n'), (read(reg), read(link)))
chk("3. read_json of a regular file and of a link to one", (read(reg, "read_json"), read(link, "read_json")) == ({"a": 1}, {"a": 1}))
# the path is swapped for a pipe between the check and the open: os.stat says "regular", the descriptor says otherwise
swapped = child("""real = os.stat
reg = real(sys.argv[2])
os.stat = lambda p, *a, **k: reg if p == sys.argv[1] else real(p, *a, **k)
print(json.dumps([inventory_core.read_text(sys.argv[1]), inventory_core.read_json(sys.argv[1])]))""", fifo, reg)
chk("2. a pipe swapped in after the check does not block the open and is refused", swapped == [None, None], swapped)

# ------------------------------------------------------------ a whole target
EMPTY = tmp()


def inventory(files, pipes):
    t = tmp()
    for rel, text in files.items():
        os.makedirs(os.path.dirname(os.path.join(t, rel)), exist_ok=True)
        with open(os.path.join(t, rel), "w") as f:
            f.write(text)
    for rel in pipes:
        os.makedirs(os.path.dirname(os.path.join(t, rel)), exist_ok=True)
        os.mkfifo(os.path.join(t, rel))
    try:
        r = subprocess.run([sys.executable, os.path.join(CODE, "inventory.py"), t, "--project-dir", EMPTY], capture_output=True, text=True,
                           timeout=10, env={"PATH": os.environ["PATH"], "HOME": EMPTY, "CLAUDE_CONFIG_DIR": EMPTY})
    except subprocess.TimeoutExpired:
        return "hung"
    return json.loads(r.stdout)["target"] if r.returncode == 0 else r.stderr[-300:]


def notes(t):
    return [n for s in t["read_status"].values() for n in s.get("notes") or []] if isinstance(t, dict) else []


PLUGIN = {".claude-plugin/plugin.json": '{"name": "p", "version": "1.0.0"}\n', "ok.sh": "echo 1 > ~/.foorc\n"}
t = inventory(PLUGIN, ["hook.sh"])
chk("1. a pipe named hook.sh beside a script: the inventory finishes", isinstance(t, dict), t)
chk("1. and the pipe is listed as not read, by its kind", "hook.sh: a named pipe, not read" in notes(t), notes(t))
chk("1. and the script beside it is still scanned", isinstance(t, dict) and "ok.sh" in t["persistence_candidates"], t)
t = inventory(PLUGIN, ["hooks/run"])
chk("1. an extension-less pipe too", "hooks/run: a named pipe, not read" in notes(t), (t if not isinstance(t, dict) else notes(t)))

NAMES = ["plugin.json", ".mcp.json", "CLAUDE.md", "AGENTS.md", "README.md", "hooks/hooks.json", "hooks/hooks.js", "skills/a/SKILL.md",
         "skills/a/notes.md", "agents/x.md", "commands/y.md", ".claude-plugin/marketplace.json", "settings.json", ".neckbeard.json",
         "package.json", "gemini-extension.json", ".codex-plugin/plugin.json", "SKILL.md", "rules/r.md", "x.py"]
hung = [n for n in NAMES if not isinstance(inventory({"ok.sh": "true\n"} if n == ".claude-plugin/marketplace.json" else
                                                      {k: v for k, v in PLUGIN.items() if k != n}, [n]), dict)]
chk("1. no file name the inventory looks for blocks it when it is a pipe", not hung, hung)

print(f"{checks - fail}/{checks} checks pass")
s.close()
sys.exit(1 if fail else 0)
