#!/usr/bin/env python3
"""vet-nested-plugin-manifest: when a root marketplace lists the root itself ("./") and a nested local plugin, the
root is the default target; --plugin picks the root or the nested one. Every case runs inventory.py as a command
with HOME, CLAUDE_CONFIG_DIR and --project-dir all set to one empty directory. Fixtures are built in a temporary
folder here, so this repo's own inventory never finds their hooks files."""
import atexit, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

INVENTORY = Path(__file__).resolve().parent.parent / "skills" / "neckbeard" / "inventory.py"
EMPTY = tempfile.mkdtemp(prefix="nested-plugin-empty-")
atexit.register(lambda: shutil.rmtree(EMPTY, ignore_errors=True))
failures = []


def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        failures.append(name)


def tree(files):
    d = Path(tempfile.mkdtemp(prefix="nested-plugin-", dir=EMPTY)) / "repo"
    for rel, text in files.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    return d


def run(target, *extra):
    env = {"PATH": os.environ["PATH"], "HOME": EMPTY, "CLAUDE_CONFIG_DIR": EMPTY}
    r = subprocess.run([sys.executable, str(INVENTORY), str(target), "--project-dir", EMPTY, *extra],
                       env=env, capture_output=True, text=True)
    return r.returncode, (json.loads(r.stdout)["target"] if r.returncode == 0 else r.stderr[-300:])


def manifest(name):
    return json.dumps({"name": name, "version": "1.0.0", "description": "d"})


def hooks(cmd):
    return json.dumps({"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": cmd}]}]}})


SKILL = "---\nname: {n}\ndescription: d\n---\nbody\n"
ROOT_FILES = {
    ".claude-plugin/plugin.json": manifest("rootp"),
    "skills/rs/SKILL.md": SKILL.format(n="rs"),
    "hooks/hooks.json": hooks("echo root-hook"),
    "mods/x/.claude-plugin/plugin.json": manifest("x"),
    "mods/x/hooks/hooks.json": hooks("echo x-hook"),
}


def market(*entries):
    return json.dumps({"name": "m", "plugins": [{"name": n, "source": s} for n, s in entries]})


def names(t):
    return [s.get("name") for s in t.get("skills", [])]


def hook_text(t):
    return json.dumps(t.get("hooks"))


NESTED = tree({**ROOT_FILES, ".claude-plugin/marketplace.json": market(("rootp", "./"), ("x", "./mods/x"))})

# 1. no --plugin: the root is the target, the marketplace lists every entry, nested ones carry the hint
code, t = run(NESTED)
check("1. default target is the root plugin", code == 0 and t["kind"] == "plugin" and t["plugin_json"]["name"] == "rootp", t)
check("1. the root's skills are read", code == 0 and names(t) == ["rs"], t)
check("1. the root's hooks are read, not the nested plugin's",
      code == 0 and "root-hook" in hook_text(t) and "x-hook" not in hook_text(t), t)
mk = t.get("marketplace", {}) if code == 0 else {}
check("1. the marketplace lists both entries, the root selected",
      [p["name"] for p in mk.get("plugins", [])] == ["rootp", "x"] and mk.get("selected") == "rootp", mk)
hint = [p for p in mk.get("plugins", []) if p["name"] == "x"]
check("1. the nested entry carries the --plugin hint",
      bool(hint) and "--plugin x" in json.dumps(hint[0]) and not any("--plugin" in json.dumps(p) for p in mk.get("plugins", []) if p["name"] == "rootp"), mk)

# 2. --plugin names the root's own entry
code, t = run(NESTED, "--plugin", "rootp")
check("2. --plugin naming the root inventories the root", code == 0 and t["plugin_json"]["name"] == "rootp" and names(t) == ["rs"], t)

# 3. --plugin names the nested plugin: as today
code, t = run(NESTED, "--plugin", "x")
check("3. --plugin naming a nested plugin inventories it", code == 0 and t["plugin_json"]["name"] == "x" and "x-hook" in hook_text(t), t)

# 4. a root with no manifest that lists "./" and one local entry: the root is read as a pack
PACK = tree({"skills/rs/SKILL.md": SKILL.format(n="rs"), "mods/x/.claude-plugin/plugin.json": manifest("x"),
             ".claude-plugin/marketplace.json": market(("rootp", "./"), ("x", "./mods/x"))})
code, t = run(PACK)
check("4. no root manifest: the root is read as a pack with the marketplace attached",
      code == 0 and t["kind"] == "generic-pack" and names(t) == ["rs"] and t.get("marketplace", {}).get("selected") == "rootp", t)
check("4. its hooks are not reported unknown", code == 0 and t["hooks"].get("has_hooks") != "unknown" and "marketplace_note" not in t["hooks"], t)
code, t = run(PACK, "--plugin", "rootp")
check("4. --plugin naming a manifest-less root does not error", code == 0 and t["kind"] == "generic-pack", t)

# regression pins, passing today and after
code, t = run(tree({".claude-plugin/plugin.json": manifest("only"), "skills/rs/SKILL.md": SKILL.format(n="rs"),
                    ".claude-plugin/marketplace.json": market(("only", "./"))}))
check("pin: a root-only marketplace reads the root", code == 0 and t["plugin_json"]["name"] == "only", t)
code, t = run(tree({"plugins/a/.claude-plugin/plugin.json": manifest("a"), "plugins/a/skills/as/SKILL.md": SKILL.format(n="as"),
                    ".claude-plugin/marketplace.json": market(("a", "./plugins/a"))}))
check("pin: one local plugin and no root entry reads that plugin", code == 0 and t["plugin_json"]["name"] == "a", t)
code, t = run(tree({"plugins/a/.claude-plugin/plugin.json": manifest("a"), "plugins/b/.claude-plugin/plugin.json": manifest("b"),
                    ".claude-plugin/marketplace.json": market(("a", "./plugins/a"), ("b", "./plugins/b"))}))
check("pin: several local plugins and no root entry stay unresolved", code == 0 and t["hooks"].get("has_hooks") == "unknown", t)

sys.exit(1 if failures else 0)
