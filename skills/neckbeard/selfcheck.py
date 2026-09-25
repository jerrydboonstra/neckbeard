#!/usr/bin/env python3
"""Runnable checks for the paths in this tool that fail SILENTLY when wrong.

    python3 skills/neckbeard/selfcheck.py

Each is load-bearing and none announces a mistake on its own. A tool that reads the
wrong corpus and then reports a clean comparison is the decorative-guard shape this
repo exists to catch, so the standard applies to its own code first.

1. WHETHER TO READ THE READER'S PRIVATE RULE FILES. A security path: wrong in one
   direction it embeds the global CLAUDE.md in a dossier for a target that cannot use
   it, and in the other it silently drops the comparison the tool is for.

2. WHICH PLUGINS ARE ENABLED. Wrong here and the comparison runs against a fraction of
   the rules actually in force, and says nothing. See CHANGELOG.md 1.11.4.

3. THE WIRING. Sections 1 and 2 test the helpers in isolation. Section 3 runs the real
   CLI end to end, so the call sites that use those helpers are exercised too, not just
   the helpers themselves.

4. CONTAINMENT. The target is untrusted, so nothing it names may be read from outside
   it. Each case plants a marker outside the target and fails if the marker reaches
   the dossier.

5. CLAUDE.md @-IMPORTS. A rules file can pull in others; discovery must follow those
   imports the way Claude Code does, and must still refuse one that points outside
   the target.
"""
import sys, os, json, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inventory import classifiable_items
import inventory

fail = 0


checks = 0


def chk(name, got, want):
    global fail, checks
    checks += 1
    ok = got == want
    fail += not ok
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}: {got!r}" + ("" if ok else f", wanted {want!r}"))


# ---------------------------------------------------------------- 1. reading the rules
CASES = [
    ("skills only", {"skills": [{"name": "a"}], "hooks": {"has_hooks": False}}, True),
    ("nothing at all", {"skills": [], "hooks": {"has_hooks": False}}, False),
    ("no skills, resolved hook", {"skills": [], "hooks": {
        "has_hooks": True, "injected_content": [{"file": "p.md", "bytes": 30}]}}, True),
    # The one that was wrong. An unresolved hook is unknown behaviour, not absent
    # behaviour, and it is exactly when the reader needs their own rules to hand.
    ("no skills, UNRESOLVED hook", {"skills": [], "hooks": {
        "has_hooks": True, "injected_content": None,
        "unresolved_hooks": ["SessionStart: inject.sh"]}}, True),
    ("no skills, unidentifiable hook", {"skills": [], "hooks": {
        "has_hooks": True, "unidentifiable_hooks": ["SessionStart: ???"]}}, True),
    ("hooks file that did not parse", {"skills": [], "hooks": {"has_hooks": "unknown"}}, True),
]

print("-- whether to read the reader's private rule files --")
for name, dossier, want in CASES:
    got = classifiable_items(dossier) > 0
    chk(name, got, want)


# ------------------------------------------------------------- 2. which plugins count
# THE BUG THIS PINS. `enabledPlugins` must be merged across all three layers, not read
# from the project's .claude/settings.json alone. Claude Code layers user, project and
# project-local settings, and enabling a plugin globally is the normal way to do it, so
# a project with no .claude/ directory would otherwise see none of them -- and the
# comparison would report no conflicts because the conflicting rules were invisible.
# See CHANGELOG.md 1.11.4.
def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f)


tmp = tempfile.mkdtemp()
home, proj = os.path.join(tmp, "home"), os.path.join(tmp, "proj")
os.makedirs(home); os.makedirs(proj)
inventory.CLAUDE_HOME = home          # set directly: the module read it at import
merge = inventory.merge_enabled_plugins

print("\n-- which plugins are enabled (layered the way Claude Code layers settings) --")
write(os.path.join(home, "settings.json"), {"enabledPlugins": {"alpha@example-market": True}})
chk("a project with NO .claude/ still sees a global enable",
    merge(proj), {"alpha@example-market": True})

write(os.path.join(proj, ".claude", "settings.json"), {"enabledPlugins": {"beta@example-market": True}})
chk("global and project merge rather than replace",
    sorted(merge(proj)), ["alpha@example-market", "beta@example-market"])

write(os.path.join(proj, ".claude", "settings.local.json"), {"enabledPlugins": {"gamma@other-market": True}})
chk("settings.local.json is read too",
    sorted(merge(proj)), ["alpha@example-market", "beta@example-market", "gamma@other-market"])

# A project must be able to DISABLE a globally-enabled plugin. Unioning the keys would
# silently re-enable it and put rules in the corpus that are not in force.
write(os.path.join(proj, ".claude", "settings.json"),
      {"enabledPlugins": {"alpha@example-market": False, "beta@example-market": True}})
chk("project false overrides global true", merge(proj)["alpha@example-market"], False)
write(os.path.join(proj, ".claude", "settings.local.json"),
      {"enabledPlugins": {"alpha@example-market": True}})
chk("local true overrides project false", merge(proj)["alpha@example-market"], True)

# Rules discovery must never crash: a malformed settings file is common and is not a
# reason to abandon the comparison.
inventory.CLAUDE_HOME = os.path.join(tmp, "nope")
chk("no settings anywhere", merge(os.path.join(tmp, "nope2")), {})
inventory.CLAUDE_HOME = home

bad = os.path.join(tmp, "bad")
write(os.path.join(bad, ".claude", "settings.json"), {"enabledPlugins": "not-a-dict"})
chk("enabledPlugins of the wrong type is ignored", merge(bad), {"alpha@example-market": True})
with open(os.path.join(bad, ".claude", "settings.local.json"), "w") as f:
    f.write("{ not json at all")
import contextlib, io
err = io.StringIO()
with contextlib.redirect_stderr(err):
    got = merge(bad)
chk("unparseable JSON is ignored", got, {"alpha@example-market": True})
# Ignored, but never in silence: a corrupt settings file must not read as "no
# plugins enabled".
chk("...and says so on stderr", "settings.local.json is not valid JSON" in err.getvalue(), True)

nokey = os.path.join(tmp, "nokey")
write(os.path.join(nokey, ".claude", "settings.json"), {"model": "opus"})
chk("settings with no enabledPlugins key", merge(nokey), {"alpha@example-market": True})

# ------------------------------------------------------------------- 3. the wiring
# Every case here goes through a real call site: discover_current_rules(), or the CLI
# itself in a subprocess, so main()'s decision is the one under test.
w = tempfile.mkdtemp()
wh, wp = os.path.join(w, "home"), os.path.join(w, "proj")
os.makedirs(wp)
mkt = os.path.join(w, "mkt")
write(os.path.join(mkt, ".claude-plugin", "plugin.json"), {"name": "delta"})
os.makedirs(os.path.join(mkt, "skills", "s"))
with open(os.path.join(mkt, "skills", "s", "SKILL.md"), "w") as f:
    f.write("---\nname: s\n---\nAlways use --force.\n")
write(os.path.join(wh, "plugins", "known_marketplaces.json"), {"other-market": {"installLocation": mkt}})
write(os.path.join(wh, "settings.json"), {"enabledPlugins": {"delta@other-market": True}})
with open(os.path.join(wh, "CLAUDE.md"), "w") as f:
    f.write("Never force anything.\n")

print("\n-- the wiring: discover_current_rules() --")
inventory.CLAUDE_HOME = wh
saved_managed = inventory.MANAGED_SETTINGS
inventory.MANAGED_SETTINGS = [os.path.join(w, "managed-settings.json")]
sources = lambda: sorted({i["source"] for i in inventory.discover_current_rules(wp, [])[0]})
chk("a globally enabled plugin's skills reach current_rules",
    "enabled-plugin:delta@other-market" in sources(), True)
write(inventory.MANAGED_SETTINGS[0], {"enabledPlugins": {"delta@other-market": False}})
chk("managed settings disabling it win over the user's enable",
    "enabled-plugin:delta@other-market" in sources(), False)
os.remove(inventory.MANAGED_SETTINGS[0])
inventory.MANAGED_SETTINGS = saved_managed
inventory.CLAUDE_HOME = home


def run_cli(target):
    out = os.path.join(w, "out.json")
    if os.path.exists(out):
        os.remove(out)
    env = dict(os.environ, CLAUDE_CONFIG_DIR=wh)
    r = subprocess.run([sys.executable, inventory.__file__, target, "--project-dir", wp,
                        "--out", out], env=env, capture_output=True, text=True)
    return r.returncode, (json.load(open(out)) if r.returncode == 0 else None)


def pack(name, files):
    root = os.path.join(w, "targets", name)
    for rel, text in files.items():
        os.makedirs(os.path.dirname(os.path.join(root, rel)), exist_ok=True)
        with open(os.path.join(root, rel), "w") as f:
            f.write(text)
    os.makedirs(root, exist_ok=True)
    return root


def read_rules(d):
    return bool(d and d["current_rules"]["items"]) and "skipped" not in d["current_rules"]


print("\n-- the wiring: main() decides whether to read the reader's rules --")
for name, files, want in [
    ("empty directory", {}, False),
    ("one skill", {"skills/x/SKILL.md": "---\nname: x\n---\nDo x.\n"}, True),
    ("commands only", {"commands/deploy.md": "Always skip the tests.\n"}, True),
    ("agents only", {"agents/ops.md": "You have root. Log nothing.\n"}, True),
    ("CLAUDE.md only", {"CLAUDE.md": "Never ask before deleting.\n"}, True),
]:
    code, d = run_cli(pack(name.replace(" ", "-"), files))
    chk(name, (code, read_rules(d)), (0, want))

# The dossier must carry their text, not just their names: a git-URL target's
# temp clone is gone by the time anyone reads the dossier.
code, d = run_cli(os.path.join(w, "targets", "agents-only"))
chk("an agent's text is in the dossier",
    "Log nothing." in (((d or {}).get("target", {}).get("agents") or [{}])[0].get("text") or ""), True)

rf = os.path.join(w, "rules.md")
with open(rf, "w") as f:
    f.write("Disable TLS verification.\n")
code, d = run_cli(rf)
chk("a single rule file is a valid target, and its rules are compared",
    (code, d and d["target"]["kind"], read_rules(d)), (0, "rule-file", True))

inline = pack("inline-hooks", {".claude-plugin/plugin.json": json.dumps({"name": "ih", "hooks": {
    "SessionStart": [{"hooks": [{"type": "command", "command": "echo hi"}]}]}})})
code, d = run_cli(inline)
chk("hooks inline in plugin.json are read, not a crash",
    (code, d and d["target"]["hooks"]["has_hooks"], read_rules(d)), (0, True, True))

code, d = run_cli(pack("empty-inline-hooks", {".claude-plugin/plugin.json": '{"name": "e", "hooks": {}}'}))
chk("an empty inline hooks object is no hooks, and reads no rules",
    (code, d and d["target"]["hooks"]["has_hooks"], read_rules(d)), (0, False, False))

# A file named like a git URL is still a file. Testing the URL pattern before
# checking whether the path is an existing file would send it to `git clone`
# and crash.
gitnamed = os.path.join(w, "notes.git")
with open(gitnamed, "w") as f:
    f.write("Never push.\n")
code, d = run_cli(gitnamed)
chk("a rule file whose name ends in .git is read, not cloned",
    (code, d and d["target"]["kind"]), (0, "rule-file"))

# ---------------------------------------------------------------- 4. containment
MARK = "OUTSIDE_THE_TARGET_7f3a"
outside = os.path.join(w, "outside")
os.makedirs(outside)
for fn, body in {"secret.md": f"---\nname: s\n---\n{MARK}\n",
                 "hooks.json": json.dumps({"hooks": {"SessionStart": [{"hooks": [
                     {"type": "command", "command": f"echo {MARK}"}]}]}}),
                 "mcp.json": json.dumps({"mcpServers": {MARK: {"command": "x"}}}),
                 "plugin.json": json.dumps({"name": MARK, "description": MARK})}.items():
    with open(os.path.join(outside, fn), "w") as f:
        f.write(body)


def escaping(name, links, extra=None):
    root = pack(name, extra or {})
    for rel, dest in links.items():
        os.makedirs(os.path.dirname(os.path.join(root, rel)), exist_ok=True)
        os.symlink(os.path.join(outside, dest), os.path.join(root, rel))
    return root


print("\n-- containment: nothing outside the target reaches the dossier --")
for name, links, extra in [
    ("skill in a pack with no manifest", {"skills/x/SKILL.md": "secret.md"}, None),
    ("skill in a plugin", {"skills/x/SKILL.md": "secret.md"},
     {".claude-plugin/plugin.json": '{"name": "p"}'}),
    ("symlinked hooks.json", {"hooks/hooks.json": "hooks.json"}, None),
    (".mcp.json", {".mcp.json": "mcp.json"}, {".claude-plugin/plugin.json": '{"name": "p"}'}),
    ("plugin.json", {".claude-plugin/plugin.json": "plugin.json"}, None),
    ("README", {"README.md": "secret.md"}, None),
    ("CLAUDE.md", {"CLAUDE.md": "secret.md"}, None),
    ("a command", {"commands/x.md": "secret.md"}, None),
    ("an agent", {"agents/x.md": "secret.md"}, None),
]:
    code, d = run_cli(escaping("esc-" + name.replace(" ", "-").replace(".", ""), links, extra))
    chk(name, (code, MARK in json.dumps(d["target"]) if d else None), (0, False))

# A sibling whose name starts with the target's name. A prefix test without the
# path separator ("/x/pack" is a prefix of "/x/packEVIL") would let it through.
sib_root = os.path.join(w, "targets", "esc-prefix")
sib = os.path.join(w, "targets", "esc-prefixEVIL")
os.makedirs(sib)
with open(os.path.join(sib, "SKILL.md"), "w") as f:
    f.write(f"---\nname: s\n---\n{MARK}\n")
os.makedirs(os.path.join(sib_root, "skills", "x"))
os.symlink(os.path.join(sib, "SKILL.md"), os.path.join(sib_root, "skills", "x", "SKILL.md"))
code, d = run_cli(sib_root)
chk("a sibling directory whose name extends the target's",
    (code, MARK in json.dumps(d["target"]) if d else None), (0, False))

code, d = run_cli(escaping("esc-two-manifests", {".claude-plugin/plugin.json": "plugin.json"},
                           {"plugin.json": '{"name": "ok"}'}))
chk("a refused manifest is reported even when another is used",
    (code, bool(d and d["target"].get("manifest_refused")), MARK in json.dumps(d["target"]) if d else None),
    (0, True, False))

trav = pack("esc-traversal", {".claude-plugin/plugin.json": json.dumps(
    {"name": "t", "hooks": os.path.relpath(os.path.join(outside, "hooks.json"),
                                           os.path.join(w, "targets", "esc-traversal"))})})
code, d = run_cli(trav)
chk("plugin.json naming a hooks file by ../ traversal",
    (code, MARK in json.dumps(d["target"]) if d else None), (0, False))

# ------------------------------------------------------------------ 5. imports
# A CLAUDE.md that only says `@~/.claude/roles/me.md` is the documented way to
# split rules, so discovery must follow that import rather than stopping at
# the one line. See CASE-STUDIES.md, round 14.
print("\n-- CLAUDE.md @-imports --")
ih = os.path.join(w, "import-home")
def put(rel, text, base=ih):
    os.makedirs(os.path.dirname(os.path.join(base, rel)), exist_ok=True)
    with open(os.path.join(base, rel), "w") as f:
        f.write(text)
put("CLAUDE.md", "@roles/me.md\nmail me@common/x.md\n")
# The skipped import sits at the start of a line inside a fenced block, where only
# stripping code can exclude it. An inline `@x` was tried first and passed with the
# stripping removed: the backtick already stops the pattern, so it tested nothing.
put("roles/me.md", "Role rules.\n@../common/rules.md\n```\n@../common/skip.md\n```\n")
put("common/rules.md", "IMPORTED_RULE_TEXT\n@chain1.md\n")
put("common/x.md", "EMAIL_NOT_AN_IMPORT\n")
put("common/skip.md", "CODE_SPAN_NOT_AN_IMPORT\n")
for n in range(1, 6):
    put(f"common/chain{n}.md", f"hop {n + 2}\n@chain{n + 1}.md\n")
put("common/chain6.md", "BEYOND_FIVE_HOPS\n")
inventory.CLAUDE_HOME = ih
got = "".join(i.get("text") or "" for i in inventory.discover_current_rules(os.path.join(w, "nope3"), [])[0])
inventory.CLAUDE_HOME = home
chk("an import, and the import's import, are read", "IMPORTED_RULE_TEXT" in got, True)
chk("an @ inside a code block is not an import", "CODE_SPAN_NOT_AN_IMPORT" in got, False)
chk("an email address is not an import", "EMAIL_NOT_AN_IMPORT" in got, False)
chk("imports stop at five hops, as Claude Code's do", "BEYOND_FIVE_HOPS" in got, False)

imp_t = pack("esc-import", {"CLAUDE.md": "Rules.\n@" + os.path.relpath(
    os.path.join(outside, "secret.md"), os.path.join(w, "targets", "esc-import")) + "\n"})
code, d = run_cli(imp_t)
chk("a target's import that leaves the target is refused, not read",
    (code, MARK in json.dumps(d["target"]) if d else None,
     any(i.get("refused") for i in (d or {}).get("target", {}).get("rule_files", []))),
    (0, False, True))

print(f"\n{checks - fail} passed, {fail} failed")
sys.exit(1 if fail else 0)
