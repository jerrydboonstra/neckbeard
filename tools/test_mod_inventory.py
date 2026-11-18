#!/usr/bin/env python3
"""mod-inventory: a plugin's Claude Code mods (the "modules" key of a hooks file) are listed in the dossier, make the hooks section
partly read, and print as a "Claude Code mods" card after Hooks. Every case runs inventory.py as a command with HOME,
CLAUDE_CONFIG_DIR and --project-dir all set to one empty folder. The plugin trees tools/fixtures/read-status/mods-* are copied with their
.fx names renamed (so neckbeard's own inventory finds no hook or mod in this repo); a mod path outside the tree points at
tools/fixtures/read-status/_outside.txt. The mod path base is the hooks file's own folder (the mods reference: `modules` is "an array
with one path, relative to this file"); an inline hooks object in plugin.json has no folder of its own, so its base is the plugin root."""
import atexit, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INVENTORY = ROOT / "skills" / "neckbeard" / "inventory.py"
PART1 = ROOT / "tools" / "part1"
EMPTY = tempfile.mkdtemp(prefix="mod-inv-empty-")
TEMPS = [EMPTY]
atexit.register(lambda: [shutil.rmtree(t, ignore_errors=True) for t in TEMPS])
FX = Path(tempfile.mkdtemp(prefix="mod-inv-fx-")) / "read-status"
TEMPS.append(str(FX.parent))
shutil.copytree(ROOT / "tools" / "fixtures" / "read-status", FX, symlinks=True)
for _p in sorted(FX.rglob("*.fx")):
    _p.rename(_p.with_suffix(""))
failures = []


def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        failures.append(name)


def dossier(target):
    env = {"PATH": os.environ["PATH"], "HOME": EMPTY, "CLAUDE_CONFIG_DIR": EMPTY}
    r = subprocess.run([sys.executable, str(INVENTORY), str(target), "--project-dir", EMPTY], env=env, capture_output=True, text=True)
    return {"error": r.stderr[-400:]} if r.returncode else json.loads(r.stdout)


def hooks_of(target):
    d = dossier(target)
    return d.get("target", {}).get("hooks") or {}, (d.get("target", {}).get("read_status") or {}).get("hooks") or {}, d


def tmp_tree(files):
    d = Path(tempfile.mkdtemp(prefix="mod-inv-"))
    TEMPS.append(d)
    for rel, v in files.items():
        (d / rel).parent.mkdir(parents=True, exist_ok=True)
        (d / rel).write_text(v)
    return d


def part1(d):
    p = Path(tempfile.mkdtemp(prefix="mod-inv-d-")); TEMPS.append(p)
    (p / "d.json").write_text(json.dumps(d))
    return subprocess.run([sys.executable, str(PART1), str(p / "d.json")], capture_output=True, text=True).stdout


def notes_of(rs):
    return " | ".join(rs.get("notes") or [])


# ---------------------------------------------------------------- MI2: a listed mod is in the dossier and makes hooks partly read
h, rs, d = hooks_of(FX / "mods-one")
check("MI2. when a hooks file lists one mod, the dossier's hooks.mods holds that one entry",
      h.get("mods") == [{"path": "hooks/band/register.tsx", "exists": True, "refused": False}], repr(h.get("mods")))
check("MI2. ... and read_status.hooks is partial, with a note naming the mod and that it runs unsandboxed (cause tool-limit)",
      rs.get("state") == "partial" and "hooks/band/register.tsx" in notes_of(rs) and "unsandboxed" in notes_of(rs) and rs.get("causes") == ["tool-limit"], repr(rs))
check("MI2. ... and an empty hooks object beside it adds no event", h.get("events") == {}, repr(h.get("events")))

# ---------------------------------------------------------------- MI3: tools/part1 prints the card after Hooks
out = part1(d)
heads = re.findall(r"<summary>\S+ <b>([^<]+)</b>", out)
check("MI3. when tools/part1 renders that dossier, it prints a Claude Code mods card right after Hooks (seven cards)",
      heads[:3] == ["Injects", "Hooks", "Claude Code mods"] and len(heads) == 7, heads)
card_text = out.split("<b>Claude Code mods</b>", 1)[-1].split("</details>", 1)[0]
summary = next((l for l in out.split("\n") if "<b>Claude Code mods</b>" in l), "")
check("MI3. ... naming the mod file, saying it runs inside the session with the user's permissions, unsandboxed, and counting 1 mod in the gist",
      "hooks/band/register.tsx" in card_text and "unsandboxed" in card_text and "permissions" in card_text and summary.endswith("· 1 mod</summary>"), (summary, card_text[:400]))
check("MI3. ... and the card's marker says partly read (the mod's source is not read)", "🟡 <b>Claude Code mods</b>" in out, out[:600])

# ---------------------------------------------------------------- MI4: outside, missing, wrong type
h, rs, d = hooks_of(FX / "mods-outside")
check("MI4. when a mod path points outside the tree, it is listed as refused and not opened, and hooks is partial with a tool-limit note",
      h.get("mods") == [{"path": "../_outside.txt", "exists": False, "refused": True}] and rs.get("state") == "partial"
      and "resolves outside the target tree" in notes_of(rs) and rs.get("causes") == ["tool-limit"] and "_outside" not in json.dumps({k: v for k, v in h.items() if k != "mods"}), repr((h.get("mods"), rs)))
h, rs, d = hooks_of(FX / "mods-missing")
check("MI4. when a mod file is missing, the entry says exists false and hooks is partial with a target-fault note naming it",
      h.get("mods") == [{"path": "hooks/gone.js", "exists": False, "refused": False}] and rs.get("state") == "partial" and "hooks/gone.js" in notes_of(rs)
      and rs.get("causes") == ["target-fault"], repr((h.get("mods"), rs)))
h, rs, d = hooks_of(FX / "mods-bad-type")
check("MI4. when modules is a string, no mods are recorded from it and hooks is partial with a target-fault note",
      h.get("mods") == [] and rs.get("state") == "partial" and "not a list of strings" in notes_of(rs) and rs.get("causes") == ["target-fault"], repr((h.get("mods"), rs)))
h, rs, d = hooks_of(tmp_tree({"hooks/hooks.json": json.dumps({"hooks": {}, "modules": ["./a.js", 3]}), "hooks/a.js": "export function register() {}\n"}))
check("MI4. when modules holds a non-string, it is not a list of strings: no mods recorded, and the note says so",
      h.get("mods") == [] and "not a list of strings" in notes_of(rs), repr((h.get("mods"), rs)))

# ---------------------------------------------------------------- MI5: modules is never an event
h, rs, d = hooks_of(FX / "mods-no-hooks-key")
check("MI5. when a hooks file is {\"modules\": [...]} with no hooks key, no event named modules appears, and the mod is listed",
      "modules" not in (h.get("events") or {}) and h.get("events") == {} and (h.get("mods") or [{}])[0].get("path") == "hooks/m.js", repr(h))
h, rs, d = hooks_of(tmp_tree({"hooks/hooks.json": json.dumps({"Stop": [{"hooks": [{"type": "command", "command": "bash hooks/s.sh"}]}], "modules": ["./m.js"]}),
                              "hooks/s.sh": "#!/bin/sh\nexit 0\n", "hooks/m.js": "export function register() {}\n"}))
check("MI5. ... and a top-level events file with a modules key keeps its events and lists the mod", sorted(h.get("events") or {}) == ["Stop"] and len(h.get("mods") or []) == 1, repr(h.get("events")))

# ---------------------------------------------------------------- a list of hooks files, an inline object, and a file with no modules
plug = json.dumps({"name": "g", "version": "1.0.0", "hooks": ["./hooks/a.json", "./hooks/b.json"]})
h, rs, d = hooks_of(tmp_tree({".claude-plugin/plugin.json": plug, "hooks/a.json": json.dumps({"hooks": {}, "modules": ["./x/one.js"]}),
                              "hooks/x/one.js": "export function register() {}\n", "hooks/b.json": "{not json"}))
check("MI6. when a later entry of a hooks list fails to parse, the mods gathered from the earlier entries are kept, and that entry adds its own note",
      [m["path"] for m in h.get("mods") or []] == ["hooks/x/one.js"] and h.get("parse_error") and "hooks/b.json" in notes_of(rs), repr((h.get("mods"), h.get("parse_error"), rs)))
plug = json.dumps({"name": "g", "version": "1.0.0", "hooks": ["./hooks/a.json", "./hooks/b.json"]})
h, rs, d = hooks_of(tmp_tree({".claude-plugin/plugin.json": plug, "hooks/a.json": json.dumps({"hooks": {}, "modules": ["./one.js"]}), "hooks/one.js": "x\n",
                              "hooks/b.json": json.dumps({"hooks": {}, "modules": ["./two.js"]}), "hooks/two.js": "x\n"}))
check("MI6. a hooks list joins every entry's mods in reading order", [m["path"] for m in h.get("mods") or []] == ["hooks/one.js", "hooks/two.js"], repr(h.get("mods")))
inline = json.dumps({"name": "g", "version": "1.0.0", "hooks": {"hooks": {}, "modules": ["./m/inline.js"]}})
h, rs, d = hooks_of(tmp_tree({".claude-plugin/plugin.json": inline, "m/inline.js": "export function register() {}\n"}))
check("MI6. an inline hooks object in plugin.json resolves its mod from the plugin root", [m["path"] for m in h.get("mods") or []] == ["m/inline.js"], repr(h.get("mods")))
h, rs, d = hooks_of(FX / "hooks-none")
check("MI7. a plugin whose hooks files have no modules key has no mods key in its hooks dossier (existing baselines stay as they are)", "mods" not in h, repr(sorted(h)))
check("MI7. ... and tools/part1 prints six cards for it, no mods card", len(re.findall(r"<summary>\S+ <b>", part1(d))) == 6)

print(f"test_mod_inventory: {len(failures)} failed" if failures else "test_mod_inventory: all passed")
sys.exit(1 if failures else 0)
