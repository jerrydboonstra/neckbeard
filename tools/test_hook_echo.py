#!/usr/bin/env python3
"""hook-echo-traced: a shell hook that prints text it builds at run time is traced from its own script, not left unresolved.
Every case runs inventory.py as a command with HOME, CLAUDE_CONFIG_DIR and --project-dir all set to one empty folder. The fixture
tools/fixtures/read-status/hooks-echo-traced is a copy of imagegen's hooks/session-start.sh (its .fx names are renamed in a
copy, so neckbeard's own inventory does not find a hook in this repo); the other cases write one hook script into a temporary
plugin. A stop case names the line that stopped the trace in the hook's unresolved_hooks entry."""
import atexit, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INVENTORY = ROOT / "skills" / "neckbeard" / "inventory.py"
EMPTY = tempfile.mkdtemp(prefix="hook-echo-empty-")
TEMPS = [EMPTY]
atexit.register(lambda: [shutil.rmtree(t, ignore_errors=True) for t in TEMPS])
FX = Path(tempfile.mkdtemp(prefix="hook-echo-fx-")) / "read-status"
TEMPS.append(str(FX.parent))
shutil.copytree(ROOT / "tools" / "fixtures" / "read-status", FX, symlinks=True)
for _p in sorted(FX.rglob("*.fx")):
    _p.rename(_p.with_suffix(""))
failures = []


def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        failures.append(name)


def dossier(target, *extra):
    env = {"PATH": os.environ["PATH"], "HOME": EMPTY, "CLAUDE_CONFIG_DIR": EMPTY}
    r = subprocess.run([sys.executable, str(INVENTORY), str(target), "--project-dir", EMPTY, *extra], env=env, capture_output=True, text=True)
    return {"error": r.stderr[-400:]} if r.returncode else json.loads(r.stdout)


def fixture(name):
    return FX / name


def got(target, section, state, *needles):
    rs = (dossier(target).get("target", {}).get("read_status") or {}).get(section) or {}
    notes = " | ".join(rs.get("notes") or [])
    return rs.get("state") == state and all(n in notes for n in needles), f"{section}: {rs!r}"


def tmp_tree(files):
    d = Path(tempfile.mkdtemp(prefix="hook-echo-"))
    TEMPS.append(d)
    for rel, v in files.items():
        (d / rel).parent.mkdir(parents=True, exist_ok=True)
        (d / rel).write_text(v)
    return d


PLUGIN = {".claude-plugin/plugin.json": '{"name": "g", "version": "1.0.0"}\n'}

# ---------------------------------------------------------------- hook-echo-traced: a shell hook that prints text it builds at run time
HOOK_CMD = 'bash "${CLAUDE_PLUGIN_ROOT}/hooks/run.sh"'


def shell_hook(script, cmd=HOOK_CMD):
    """The hooks section of a plugin whose one SessionStart hook runs hooks/run.sh with this text."""
    hj = json.dumps({"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": cmd}]}]}})
    d = dossier(tmp_tree({**PLUGIN, "hooks/hooks.json": hj, "hooks/run.sh": script}))
    return d.get("target", {}).get("hooks") or {}, d


def built_entry(h):
    return next((e for e in h.get("injected_content") or [] if e.get("built_at_run_time")), None)


def traced(script, template, writes=None, cmd=HOOK_CMD):
    h, d = shell_hook(script, cmd)
    e = built_entry(h)
    ok = not h.get("unresolved_hooks") and e is not None and e.get("template") == template and (writes is None or e.get("writes") == writes)
    return ok, repr((h.get("unresolved_hooks"), e))


def stopped(script, line, cmd=HOOK_CMD, extra=""):
    h, d = shell_hook(script, cmd)
    u = h.get("unresolved_hooks") or []
    rs = (d.get("target", {}).get("read_status") or {}).get("hooks") or {}
    want = f"(line {line}:" if line else extra
    return (len(u) == 1 and want in u[0] and extra in u[0] and not built_entry(h) and rs.get("state") == "partial"), repr((u, built_entry(h)))


fx = fixture("hooks-echo-traced")
h = (dossier(fx).get("target") or {}).get("hooks") or {}
e = built_entry(h)
check("HE1. an imagegen-shaped hook: hooks read, no unresolved note, template and writes on the dossier entry",
      got(fx, "hooks", "read")[0] and not h.get("unresolved_hooks") and e is not None
      and e["template"] == ["imagegen doctor: \u2026 missing; run skills/imagegen/doctor.sh for fixes"]
      and e["writes"] == ["mkdir -p \u2026", ": > \u2026"] and e["events"] == ["SessionStart"], repr((h.get("unresolved_hooks"), e)))
STOPS = {
    "HE2 FOO=1 cat f": ("#!/bin/sh\nFOO=1 cat f\nexit 0\n", 2),
    "HE2 if cat f": ("#!/bin/sh\nif cat f; then\n:\nfi\nexit 0\n", 2),
    "HE2 pipe": ("#!/bin/sh\ntrue | cat f\nexit 0\n", 2),
    "HE2 2>&1": ("#!/bin/sh\necho x 2>&1\nexit 0\n", 2),
    "HE2 bare exit after >&2": ("#!/bin/sh\necho msg >&2\nexit\n", 3),
    "HE2 PATH assignment": ("#!/bin/sh\nPATH=./bin\nmkdir d\nexit 0\n", 2),
    "HE2 export": ("#!/bin/sh\nexport X=1\nexit 0\n", 2),
    "HE2 mkdir -pv": ("#!/bin/sh\nmkdir -pv d\nexit 0\n", 2),
    "HE2 fd 3": ("#!/bin/sh\nmkdir d 3>&1\nexit 0\n", 2),
    "HE2 echo >> file": ("#!/bin/sh\necho x >> CLAUDE.md\nexit 0\n", 2),
    "HE2 ${y:?msg}": ("#!/bin/sh\nx=${y:?msg}\nexit 0\n", 2),
    "HE2 last line not exit": ("#!/bin/sh\necho hi\ntrue\n", 3),
    "HE2 printed file text": ("#!/bin/sh\ns=$(cat \"$root/SKILL.md\"); printf '%s' \"$s\"\nexit 0\n", 2),
    "HE2 echo $(head file)": ("#!/bin/sh\necho \"$(head x.md)\"\nexit 0\n", 2),
    "HE2 sed -n file": ("#!/bin/sh\ns=$(sed -n '1,20p' \"$root/SKILL.md\"); echo \"$s\"\nexit 0\n", 2),
    "HE2 grep -e file": ("#!/bin/sh\ns=$(grep -e x f); echo \"$s\"\nexit 0\n", 2),
    "HE2 unbalanced quote": ("#!/bin/sh\necho \"oops\nexit 0\n", 2),
}
for name, (script, line) in STOPS.items():
    check(f"{name}: stays unresolved and its unresolved_hooks entry names line {line}", *stopped(script, line))
check("HE1. ... bytes is the literal template text (66) and injected_bytes_total_estimate adds it",
      e is not None and e["bytes"] == len("imagegen doctor:  missing; run skills/imagegen/doctor.sh for fixes") and h.get("injected_bytes_total_estimate") == e["bytes"],
      repr((e and e.get("bytes"), h.get("injected_bytes_total_estimate"))))
sys.path.insert(0, str(ROOT / "skills" / "neckbeard"))
import inventory   # noqa: E402
_two = {"has_hooks": True, "injected_content": [{"file": "a.md", "bytes": 5}, {"file": "hooks/run.sh", "bytes": 0, "events": ["Stop"], "built_at_run_time": True, "template": [], "writes": ["touch \u2026"]}]}
_one = {"has_hooks": True, "injected_content": [{"file": "a.md", "bytes": 5}]}
check("HE1. a writes-only entry is not an instruction source (classifiable_items counts the same with and without it)",
      inventory.classifiable_items({"hooks": _two}) == inventory.classifiable_items({"hooks": _one}) == 1, repr((inventory.classifiable_items({"hooks": _two}), inventory.classifiable_items({"hooks": _one}))))
MORE_STOPS = {
    "heredoc": "#!/bin/sh\ncat <<EOF\nhi\nEOF\nexit 0\n", "eval": "#!/bin/sh\neval \"$x\"\nexit 0\n",
    "source": "#!/bin/sh\nsource ./lib.sh\nexit 0\n", ". file": "#!/bin/sh\n. ./lib.sh\nexit 0\n",
    "function": "#!/bin/sh\nf() { echo hi; }\nexit 0\n", "for": "#!/bin/sh\nfor i in 1 2; do echo $i; done\nexit 0\n",
    "case": "#!/bin/sh\ncase $x in a) echo hi;; esac\nexit 0\n", "background": "#!/bin/sh\nsleep 1 &\nexit 0\n",
    ">&1": "#!/bin/sh\necho hi >&1\nexit 0\n", "3>&2": "#!/bin/sh\necho hi 3>&2\nexit 0\n",
    "$((...))": "#!/bin/sh\nx=$((1/0))\nexit 0\n", "set": "#!/bin/sh\nset -e\nexit 0\n", "shift": "#!/bin/sh\nshift\nexit 0\n",
    "unset": "#!/bin/sh\nunset x\nexit 0\n", "readonly": "#!/bin/sh\nreadonly x=1\nexit 0\n", "exec": "#!/bin/sh\nexec cat f\nexit 0\n",
    "process substitution": "#!/bin/sh\necho <(cat f)\nexit 0\n", "exit 2": "#!/bin/sh\necho hi\nexit 2\n",
}
for name, script in MORE_STOPS.items():
    h_, d_ = shell_hook(script)
    u_ = h_.get("unresolved_hooks") or []
    check(f"HE2 more stops: {name} leaves the hook unresolved with a line named", len(u_) == 1 and "(line " in u_[0] and not built_entry(h_), repr(u_))
check("HE2 control: a plain echo and exit 0 does trace", *traced("#!/bin/sh\necho hi\nexit 0\n", ["hi"]))
check("HE3. the hook command runs more than the script: unresolved, with the note",
      *stopped("#!/bin/sh\necho hi\nexit 0\n", None, cmd='${CLAUDE_PLUGIN_ROOT}/hooks/run.sh && cat x', extra="(the hook command runs more than the script)"))
check("HE4. printf with %s: the template shows an ellipsis for it", *traced('#!/bin/sh\nprintf "%s done\\n" "$x"\nexit 0\n', ["\u2026 done"]))
check("HE4. an unquoted glob in echo shows an ellipsis", *traced("#!/bin/sh\necho *.txt\nexit 0\n", ["\u2026"]))


print(f"test_hook_echo: {'all passed' if not failures else str(len(failures)) + ' failed'}")
sys.exit(1 if failures else 0)
