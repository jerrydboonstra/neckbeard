#!/usr/bin/env python3
"""hook-inline-require: a hook command that is `node -e` with one require of a plugin script names that script, in tools/part1 and in
the inventory. Fixtures: tools/fixtures/part1/hooks-inline-require.dossier.json (six hook commands, rendered by tools/part1) and the
plugin tree tools/fixtures/read-status/hooks-inline-require (its .fx names renamed in a copy, so neckbeard's own inventory finds no hook
in this repo). The two copies of the recogniser, inline_require_script, are kept equal here, as test_part1 keeps the plugin-root expanders."""
import importlib.machinery, importlib.util, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
NB = os.path.dirname(HERE)
PART1 = os.path.join(HERE, "part1")
INVENTORY = os.path.join(NB, "skills", "neckbeard", "inventory.py")
INVENTORY_HOOKS = os.path.join(NB, "skills", "neckbeard", "inventory_hooks.py")
TEMPS = []
fail = checks = 0


def chk(name, ok, detail=""):
    global fail, checks
    checks += 1
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        fail += 1


def tmp():
    d = tempfile.mkdtemp(prefix="hir-test-")
    TEMPS.append(d)
    return d


def load_expander(path, name):
    """A function from a script, loaded by path (tools/part1 has no .py name)."""
    modname = "loaded_" + re.sub(r"\W", "_", os.path.basename(path))
    loader = importlib.machinery.SourceFileLoader(modname, path)
    mod = importlib.util.module_from_spec(importlib.util.spec_from_loader(modname, loader))
    loader.exec_module(mod)
    return getattr(mod, name)


def hook_lines(dossier):
    """{event: printed script} from the Hooks card tools/part1 renders for a dossier."""
    out = subprocess.run([sys.executable, PART1, dossier], capture_output=True, text=True).stdout
    card = out.split("### Hooks\n", 1)[-1].split("\n### ", 1)[0]
    return {m.group(1): m.group(2) for m in (re.match(r"^\s*- (\w+)(?: \([^)]*\))?: (.*)$", l) for l in card.split("\n")) if m}


# ---------------------------------------------------------------- hook-inline-require: `node -e require(...)` names its script
UNP = "<unparsed command>"
hl = hook_lines(os.path.join(HERE, "fixtures", "part1", "hooks-inline-require.dossier.json"))
chk("HIR2. when a hook runs node -e with one require of a script joined to process.env.CLAUDE_PLUGIN_ROOT (join or resolve, either quote, the backslash fix, spaces), tools/part1 names that script",
    all(hl.get(e) == "hooks/greet-session.js" for e in ("SessionStart", "SubagentStart", "UserPromptSubmit")), hl)
chk("HIR4. when the body holds that require plus other code, the path holds a .. segment, or the interpreter is not node, tools/part1 prints <unparsed command>",
    all(hl.get(e) == UNP for e in ("Stop", "PreToolUse", "PostToolUse")), hl)

HIR_CMD = "node -e \"require(require('path').join(process.env.CLAUDE_PLUGIN_ROOT,'hooks/greet-session.js'))\""


def hir_tree(command=None):
    """A plugin tree from the hooks-inline-require fixture (its .fx names renamed), the hook command optionally replaced."""
    d = os.path.join(tmp(), "plugin")
    shutil.copytree(os.path.join(HERE, "fixtures", "read-status", "hooks-inline-require"), d)
    for f in [os.path.join(r, n) for r, _, ns in os.walk(d) for n in ns if n.endswith(".fx")]:
        os.rename(f, f[:-3])
    if command is not None:
        json.dump({"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": command}]}]}}, open(os.path.join(d, "hooks", "hooks.json"), "w"))
    return d


def hir_hooks(command=None):
    e = tmp()
    r = subprocess.run([sys.executable, INVENTORY, hir_tree(command), "--project-dir", e],
                       env={"PATH": os.environ["PATH"], "HOME": e, "CLAUDE_CONFIG_DIR": e}, capture_output=True, text=True)
    return json.loads(r.stdout)["target"]["hooks"] if r.returncode == 0 else {"error": r.stderr[-300:]}


h = hir_hooks()
chk("HIR3. when the inventory reads that plugin, it identifies hooks/greet-session.js as the hook's script and reads it (no unidentifiable hook, one script, the script named in the unresolved note)",
    not h.get("unidentifiable_hooks") and h.get("hook_scripts") == 1 and h.get("unresolved_hooks") == ["SessionStart: hooks/greet-session.js"], h)
for what, cmd in (("extra code", HIR_CMD.replace("require(require", "console.log(1);require(require", 1)),
                  ("a .. segment", HIR_CMD.replace("hooks/greet-session.js", "hooks/../hooks/greet-session.js"))):
    h = hir_hooks(cmd)
    chk(f"HIR4. when the require form has {what}, the inventory does not identify the script",
        len(h.get("unidentifiable_hooks") or []) == 1 and not h.get("unresolved_hooks"), h)

HIR_FORMS = [HIR_CMD, HIR_CMD.replace("'", '"').replace('node -e "', "node -e '", 1)[:-1] + "'",
             HIR_CMD.replace(".join(", ".resolve(", 1),
             HIR_CMD.replace("CLAUDE_PLUGIN_ROOT,", "CLAUDE_PLUGIN_ROOT.split(String.fromCharCode(92)).join('/'),", 1),
             HIR_CMD.replace(",'hooks", " , 'hooks", 1), "node -e \"require(require('path').join(process.env.CLAUDE_PLUGIN_ROOT,'x.js'))\"",
             HIR_CMD.replace("require(require", "console.log(1);require(require", 1), HIR_CMD.replace("hooks/greet", "../greet"),
             HIR_CMD.replace("hooks/greet", "/abs/greet"), HIR_CMD.replace("hooks/greet-session.js", "a b.js"), HIR_CMD.replace("node", "bash", 1),
             HIR_CMD.replace("-e", "-p", 1), HIR_CMD.replace("CLAUDE_PLUGIN_ROOT", "OTHER_ROOT"), HIR_CMD + " extra", "node -e", "node", "", "node -e '", "node hooks/x.js"]
try:
    sys.path.insert(0, os.path.dirname(INVENTORY_HOOKS))
    inv = load_expander(INVENTORY_HOOKS, "inline_require_script")
    mine = load_expander(PART1, "inline_require_script")
    ans = [mine(c) for c in HIR_FORMS]
    bad = [c for c in HIR_FORMS if inv(c) != mine(c)]
    chk(f"HIR5. tools/part1's copy of the node -e require recogniser agrees with inventory_hooks.py's on {len(HIR_FORMS)} commands, and each form it allows gives its script",
        not bad and ans[:6] == ["hooks/greet-session.js"] * 5 + ["x.js"] and all(a is None for a in ans[6:]), (bad, ans))
except Exception as e:
    chk("HIR5. tools/part1's copy of the node -e require recogniser agrees with inventory_hooks.py's", False, f"{type(e).__name__}: {e}")


for t_ in TEMPS:
    shutil.rmtree(t_, ignore_errors=True)
print(f"test_hook_inline_require: {fail} failed" if fail else "test_hook_inline_require: all passed")
sys.exit(1 if fail else 0)
