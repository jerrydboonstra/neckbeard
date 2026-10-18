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
# A key the global layer never sets: with alpha, the last layer's True also equals the global True,
# so a merge that ignored every later layer still passed (found by sabotaging the merge).
write(os.path.join(proj, ".claude", "settings.json"),
      {"enabledPlugins": {"alpha@example-market": False, "beta@example-market": True, "delta@example-market": False}})
write(os.path.join(proj, ".claude", "settings.local.json"),
      {"enabledPlugins": {"alpha@example-market": True, "delta@example-market": True}})
chk("local true overrides project false", merge(proj)["delta@example-market"], True)

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


def run_cli(target, *extra):
    out = os.path.join(w, "out.json")
    if os.path.exists(out):
        os.remove(out)
    env = dict(os.environ, CLAUDE_CONFIG_DIR=wh)
    r = subprocess.run([sys.executable, inventory.__file__, target, "--project-dir", wp,
                        "--out", out, *extra], env=env, capture_output=True, text=True)
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

# A real, many-rule file, run against the public sample reader as the gallery
# runs it. Pins today's behaviour before rule files get their own report.
repo = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
reader = os.path.join(repo, "examples", "reader")
agents_md = os.path.join(repo, "examples", "targets", "tvykruta-agents.md")
out = os.path.join(w, "agents-md.json")
r = subprocess.run([sys.executable, inventory.__file__, agents_md, "--project-dir", wp, "--out", out],
                   env=dict(os.environ, CLAUDE_CONFIG_DIR=reader), capture_output=True, text=True)
ad = json.load(open(out)) if r.returncode == 0 else {}
t = ad.get("target", {})
files = t.get("rule_files") or []
text = files[0].get("text", "") if len(files) == 1 else ""
chk("a many-rule AGENTS.md is one lossless rule-file item, with nothing to install",
    (r.returncode, t.get("kind"), len(files), len(t.get("skills") or []), len(t.get("commands") or []),
     len(t.get("agents") or []), (t.get("hooks") or {}).get("has_hooks"),
     text.startswith("# Tomas Vykruta's `AGENTS.md` rules"), text.rstrip().endswith("8. Then pick the next system.")),
    (0, "rule-file", 1, 0, 0, 0, False, True, True))
# A standalone file is one trust boundary: naming a sibling must not get it read.
# A CLAUDE.md keeps its imports, because they are part of that format, but still
# only inside its own folder.
SIB = "SIBLING_SECRET_5c1e"
bound = os.path.join(w, "boundary", "inner")
os.makedirs(bound)
for fn, body in {"rules.md": "Be careful.\n@notes.md\n", "notes.md": f"{SIB}\n",
                 "CLAUDE.md": "Team rules.\n@notes.md\n@../outer.md\n"}.items():
    with open(os.path.join(bound, fn), "w") as f:
        f.write(body)
with open(os.path.join(w, "boundary", "outer.md"), "w") as f:
    f.write("OUTER_MARK_5c1e\n")
code, d = run_cli(os.path.join(bound, "rules.md"))
chk("a standalone rules.md does not read the sibling it names, and says so",
    (code, SIB in json.dumps(d), (d or {}).get("target", {}).get("imports_not_followed")),
    (0, False, ["notes.md"]))
code, d = run_cli(os.path.join(bound, "CLAUDE.md"))
rfs = (d or {}).get("target", {}).get("rule_files") or []
chk("a CLAUDE.md target follows its own import and refuses one outside its folder",
    (code, SIB in json.dumps(d), "OUTER_MARK_5c1e" in json.dumps(d), [bool(i.get("refused")) for i in rfs]),
    (0, True, False, [False, False, True]))
binf = os.path.join(w, "image.png")
with open(binf, "wb") as f:
    f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR")
code, d = run_cli(binf)
chk("a binary file is refused with an error, not read as an empty rule file", (code != 0, d), (True, None))

chk("an AGENTS.md run reads only the sample reader's rule files",
    sorted(os.path.relpath(i["path"], reader) for i in ad.get("current_rules", {}).get("items", [])),
    ["CLAUDE.md", "rules/engineering.md", "rules/safety.md", "skills/release-notes/SKILL.md"])

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

# ------------------------------------------------ 6. hooks that are not at the root
# Both cases reported "no hooks" for a plugin that has them, the worst direction for
# this tool to be wrong in. Found 2026-09-28 on three of four real plugins; see
# CHANGELOG.md 1.12.6.
print("\n-- hooks that are not where the root manifest says --")
SESSION_HOOK = json.dumps({"hooks": {"SessionStart": [{"hooks": [
    {"type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks/start.sh"}]}]}})


def plugin_files(name):
    return {f"plugins/{name}/.claude-plugin/plugin.json": json.dumps({"name": name}),
            f"plugins/{name}/hooks/hooks.json": SESSION_HOOK,
            f"plugins/{name}/hooks/start.sh": "cat \"$CLAUDE_PLUGIN_ROOT/skills/s/SKILL.md\"\n",
            f"plugins/{name}/skills/s/SKILL.md": "---\nname: s\n---\nAct without asking.\n"}


def market(entries):
    return json.dumps({"name": "m", "plugins": [{"name": n, "source": s} for n, s in entries]})


# The repo root is a marketplace, and its one plugin lives in plugins/<name>/.
one = pack("mkt-one", {".claude-plugin/marketplace.json": market([("kit", "./plugins/kit")]),
                       **plugin_files("kit")})
code, d = run_cli(one)
t = (d or {}).get("target", {})
chk("a marketplace's only plugin, in plugins/<name>/, is the one inventoried",
    (code, t.get("hooks", {}).get("has_hooks"), "SessionStart" in t.get("hooks", {}).get("events", {}),
     (t.get("marketplace") or {}).get("selected")), (0, True, True, "kit"))

two = pack("mkt-two", {".claude-plugin/marketplace.json": market([("a", "./plugins/a"), ("b", "./plugins/b")]),
                       **plugin_files("a"), **plugin_files("b")})
code, d = run_cli(two)
t = (d or {}).get("target", {})
chk("several plugins and none chosen: hooks are unknown, never false",
    (code, t.get("hooks", {}).get("has_hooks"),
     sorted(p["name"] for p in (t.get("marketplace") or {}).get("plugins", []))),
    (0, "unknown", ["a", "b"]))
code, d = run_cli(two, "--plugin", "b")
chk("--plugin picks one of several",
    (code, ((d or {}).get("target", {}).get("marketplace") or {}).get("selected"),
     (d or {}).get("target", {}).get("hooks", {}).get("has_hooks")), (0, "b", True))
code, d = run_cli(two, "--plugin", "nope")
chk("--plugin naming no plugin in the marketplace stops, rather than guessing", code != 0, True)

# No plugin manifest at all, and an installer
# that merges the "hooks" block of install.json into ~/.claude/settings.json.
inst = pack("installer-hooks", {
    "install.json": json.dumps({"skills": {"paths": ["skills/x"]}, "hooks": {
        "SubagentStart": [{"matcher": "", "hooks": [{"type": "command", "command": "node h.mjs"}]}]}}),
    "scripts/install.mjs": "fs.writeFileSync(path.join(os.homedir(), '.claude', 'settings.json'), s)\n",
    "skills/x/SKILL.md": "---\nname: x\n---\nDo x.\n"})
code, d = run_cli(inst)
h = (d or {}).get("target", {}).get("hooks", {})
chk("hooks in an installer's JSON are reported, with their reach",
    (code, h.get("has_hooks"), h.get("hooks_source"), h.get("hooks_reach_subagents")),
    (0, True, "outside-manifest", True))
chk("...and the script that writes settings.json is named",
    "scripts/install.mjs" in (h.get("settings_writers") or []), True)

# A folder of plugins with no marketplace manifest: each plugin's own hooks are found,
# but they are that plugin's, not an installer's for the whole folder.
nest = pack("plugin-folder", {k.replace("plugins/", ""): v
                              for k, v in {**plugin_files("a"), **plugin_files("b")}.items()})
code, d = run_cli(nest)
h = (d or {}).get("target", {}).get("hooks", {})
chk("a folder of plugins: hooks unknown, and the plugins named",
    (code, h.get("has_hooks"), h.get("nested_plugins")), (0, "unknown", ["a", "b"]))

# No false alarm: a "hooks" key that is not an object of Claude Code events, whether
# its values are not lists or its keys are not event names.
code, d = run_cli(pack("not-hooks", {"config.json": json.dumps({"hooks": {"retries": 3}}),
                                     "tools.json": json.dumps({"hooks": {"onSave": [{"command": "lint"}]}}),
                                     "skills/x/SKILL.md": "---\nname: x\n---\nDo x.\n"}))
chk("a 'hooks' key with no Claude Code event in it is not a hook",
    (code, (d or {}).get("target", {}).get("hooks", {}).get("has_hooks")), (0, False))

# Containment, as in section 4: a marketplace source and an installer file are both
# named by the untrusted target.
code, d = run_cli(pack("esc-mkt-source", {".claude-plugin/marketplace.json": market(
    [("x", os.path.relpath(outside, os.path.join(w, "targets", "esc-mkt-source")))])}))
chk("a marketplace source outside the target is refused, not inventoried",
    (code, MARK in json.dumps(d["target"]) if d else None), (0, False))
code, d = run_cli(escaping("esc-installer", {"install.json": "hooks.json"}))
chk("an installer JSON symlinked outside the target is not read",
    (code, MARK in json.dumps(d["target"]) if d else None), (0, False))

# Found by review after 1.12.6 shipped: the search stopped four levels down and said
# false for hooks below that, and a marketplace.json that failed to parse read as one
# that lists nothing. See CHANGELOG.md 1.12.7.
deep = pack("deep-hooks", {"a/b/c/d/e/f/install.json": SESSION_HOOK,
                           "skills/x/SKILL.md": "---\nname: x\n---\nDo x.\n"})
code, d = run_cli(deep)
chk("hooks six levels down are found",
    (code, (d or {}).get("target", {}).get("hooks", {}).get("has_hooks")), (0, True))
many = pack("many-json", {**{f"data/{i}.json": "{}" for i in range(3)},
                          "skills/x/SKILL.md": "---\nname: x\n---\nDo x.\n"})
h = inventory.hooks_outside_manifest(many, max_reads=2)
chk("a search that runs out of reads says unknown, never false",
    (h.get("has_hooks"), "stopped after 2" in (h.get("search_incomplete") or "")), ("unknown", True))
# ...and one that found some hooks before it ran out says it may have missed more.
part = pack("partial-hooks", {"a/install.json": SESSION_HOOK,
                              **{f"b/{i}.json": "{}" for i in range(3)},
                              "c/late.json": SESSION_HOOK.replace("SessionStart", "Stop")})
h = inventory.hooks_outside_manifest(part, max_reads=3)
chk("a search that found hooks and then ran out says it is incomplete",
    (h.get("has_hooks"), "Stop" in h.get("events", {}), "stopped after 3" in (h.get("search_incomplete") or "")),
    (True, False, True))
code, d = run_cli(pack("mkt-bad", {".claude-plugin/marketplace.json": "{not json",
                                   "skills/x/SKILL.md": "---\nname: x\n---\nDo x.\n"}))
chk("a marketplace.json that is not JSON says so",
    (code, ((d or {}).get("target", {}).get("marketplace") or {}).get("parse_error")),
    (0, "marketplace.json is not valid JSON; read it by hand"))

# The shell's default form, as Cat Herder writes it so one hook file serves several
# hosts. Matching only ${CLAUDE_PLUGIN_ROOT} reported all three of its hooks as
# unidentifiable, and the judge read the hook code by hand (verdict-stability-runs).
dflt = pack("root-default", {
    ".claude-plugin/plugin.json": json.dumps({"name": "dflt", "hooks": ["./hooks/claude.json"]}),
    "hooks/claude.json": json.dumps({"hooks": {"SessionEnd": [{"hooks": [{"type": "command",
        "command": "\"${CLAUDE_PLUGIN_ROOT:-${PLUGIN_ROOT}}/bin/meow\" _hook sessionend"}]}]}}),
    "bin/meow": "#!/usr/bin/env python3\nprint(build_text())\n",
    "skills/x/SKILL.md": "---\nname: x\n---\nDo x.\n"})
code, d = run_cli(dflt)
h = (d or {}).get("target", {}).get("hooks", {})
chk("a hook run as ${CLAUDE_PLUGIN_ROOT:-${PLUGIN_ROOT}}/bin/meow is identified",
    (code, h.get("unidentifiable_hooks"), "meow" in json.dumps(h)), (0, None, True))
root = "/r"
chk("each default form of CLAUDE_PLUGIN_ROOT expands to the plugin root",
    [inventory._expand_plugin_root(c, root) for c in (
        "${CLAUDE_PLUGIN_ROOT}/a", "$CLAUDE_PLUGIN_ROOT/a", "${CLAUDE_PLUGIN_ROOT:-x}/a",
        "${CLAUDE_PLUGIN_ROOT-x y}/a", "${CLAUDE_PLUGIN_ROOT:=${A:-${B}}}/a",
        "${CLAUDE_PLUGIN_ROOT:?unset}/a")],
    ["/r/a"] * 6)
chk("${CLAUDE_PLUGIN_ROOT:+word}, a longer name, and an unclosed brace are left alone",
    [inventory._expand_plugin_root(c, root) for c in (
        "${CLAUDE_PLUGIN_ROOT:+w}/a", "$CLAUDE_PLUGIN_ROOTS/a", "${CLAUDE_PLUGIN_ROOT:-x/a")],
    ["${CLAUDE_PLUGIN_ROOT:+w}/a", "$CLAUDE_PLUGIN_ROOTS/a", "${CLAUDE_PLUGIN_ROOT:-x/a"])

# ---------------------------------------------------------------- 6. what the judge reads
# A dossier that leaves out text the judge needs makes it open the files by hand, and two
# runs then read different text (Cat Herder's report at 178648f8a: 5 conflicts, then 2).
ev = lambda cmd: {"hooks": {"Stop": [{"hooks": [{"type": "command", "command": cmd}]}]}}
lst = pack("hooks-list", {
    ".claude-plugin/plugin.json": json.dumps({"name": "hl", "hooks": ["./hooks/a.json", "./hooks/b.json"]}),
    "hooks/a.json": json.dumps({"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": "echo a"}]}]}}),
    "hooks/b.json": json.dumps({"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "echo b"}]}]}}),
})
code, d = run_cli(lst)
hk = (d or {}).get("target", {}).get("hooks", {})
chk("plugin.json hooks given as a list of files are all read",
    (code, hk.get("has_hooks"), sorted(hk.get("events", {}))), (0, True, ["SessionStart", "Stop"]))

code, d = run_cli(pack("hooks-list-missing", {
    ".claude-plugin/plugin.json": json.dumps({"name": "hm", "hooks": ["./hooks/a.json", "./hooks/gone.json"]}),
    "hooks/a.json": json.dumps(ev("echo a"))}))
chk("a hooks list naming a file that is not there is unknown, not a partial answer",
    (code, ((d or {}).get("target", {}).get("hooks") or {}).get("has_hooks")), (0, "unknown"))

outside = os.path.join(w, "outside-hooks.json")
with open(outside, "w") as f:
    f.write(json.dumps(ev("echo " + MARK)))
code, d = run_cli(pack("hooks-list-outside", {
    ".claude-plugin/plugin.json": json.dumps({"name": "ho", "hooks": ["../../outside-hooks.json"]})}))
chk("a hooks list pointing outside the target is refused, and its text stays out",
    (code, ((d or {}).get("target", {}).get("hooks") or {}).get("has_hooks"), MARK in json.dumps(d)),
    (0, "unknown", False))

code, d = run_cli(pack("skill-companions", {
    ".claude-plugin/plugin.json": '{"name": "sc"}',
    "skills/herd/SKILL.md": "---\nname: herd\ndescription: d\n---\nSee roles/worker.md.\n",
    "skills/herd/roles/worker.md": "COMPANION_TEXT_ONLY_HERE\n",
    "skills/quiet/SKILL.md": "---\nname: quiet\ndescription: d\nuser-invocable: false\n---\nBody.\n"}))
sk = {x["name"]: x for x in (d or {}).get("target", {}).get("skills", [])}
chk("a skill's other Markdown files are in the dossier with their text",
    [(c["path"], "COMPANION_TEXT_ONLY_HERE" in (c["text"] or "")) for c in sk.get("herd", {}).get("companion_files", [])],
    [("skills/herd/roles/worker.md", True)])
# The target is untrusted: a skill folder that links to itself must not hang the inventory or
# list one file many times, and vendored folders must not use up the cap.
loop = pack("skill-loop", {".claude-plugin/plugin.json": '{"name": "sl"}',
                           "skills/s/SKILL.md": "---\nname: s\ndescription: d\n---\nBody.\n",
                           "skills/s/r.md": "ROLE_TEXT\n"})
for ln in ("a", "b"):
    os.symlink(".", os.path.join(loop, "skills", "s", ln))
try:
    r = subprocess.run([sys.executable, inventory.__file__, loop, "--project-dir", wp,
                        "--out", os.path.join(w, "loop.json")], env=dict(os.environ, CLAUDE_CONFIG_DIR=wh),
                       capture_output=True, text=True, timeout=30)
    cf = [c["path"] for c in json.load(open(os.path.join(w, "loop.json")))["target"]["skills"][0]["companion_files"]]
    chk("a skill folder that links to itself neither hangs nor lists a file twice",
        (r.returncode, cf), (0, ["skills/s/r.md"]))
except subprocess.TimeoutExpired:
    chk("a skill folder that links to itself neither hangs nor lists a file twice", "hung", "finishes")

many = {".claude-plugin/plugin.json": '{"name": "mn"}',
        "skills/s/SKILL.md": "---\nname: s\ndescription: d\n---\nBody.\n"}
for i in range(45):
    many[f"skills/s/scripts/node_modules/p/{i:02d}.md"] = f"vendored {i}\n"
    many[f"skills/s/refs/{i:02d}.md"] = f"ref {i}\n"
many["skills/s/zz-role.md"] = "REAL_ROLE\n"
code, d = run_cli(pack("skill-many", many))
cf = [(c["path"], c["text"] is not None) for c in (d or {})["target"]["skills"][0]["companion_files"]]
chk("vendored folders are pruned, and past 40 files the rest are named with no text",
    (len(cf), sum(t for _, t in cf), any(p.endswith("node_modules/p/00.md") for p, _ in cf),
     ("skills/s/zz-role.md", True) in cf, cf[-1]),
    (46, 40, False, True, ("skills/s/refs/44.md", False)))
chk("user-invocable is read from each skill's frontmatter (default true)",
    (sk.get("herd", {}).get("user_invocable"), sk.get("quiet", {}).get("user_invocable")), (True, False))

# ---------------------------------------------------------------- 7. frontmatter strict YAML can't read
# Claude Code is lenient, so the author never sees these; GitHub and stricter agents do.
fe = inventory.frontmatter_errors
chk("an unquoted ': ' in a description is flagged, with its line",
    [(e["line"]) for e in fe("---\nname: x\ndescription: Use when: the user asks\n---\nBody\n")], [3])
chk("a quoted description with ': ' is fine",
    fe('---\nname: x\ndescription: "Use when: the user asks"\n---\n'), [])
chk("a >- block with ': ' inside is fine",
    fe("---\nname: x\ndescription: >-\n  Use when: the user asks\n  and more\n---\n"), [])
chk("a continued unquoted value with ': ' is flagged",
    [e["line"] for e in fe("---\nname: x\ndescription: Use it\n  when: asked\n---\n")], [4])
chk("a value that starts with @ is flagged",
    [e["line"] for e in fe("---\nname: x\ndescription: @mention people\n---\n")], [3])
chk("a tab in indentation is flagged",
    [e["line"] for e in fe("---\nname: x\ndescription: >-\n\ttabbed\n---\n")], [4])
chk("an unclosed quote is flagged",
    [e["line"] for e in fe('---\nname: x\ndescription: "never closed\n---\n')], [3])
chk("frontmatter that never closes is flagged",
    [e["line"] for e in fe("---\nname: x\ndescription: d\nBody with no fence\n")], [1])
chk("a file with no frontmatter has no errors", fe("# Just a rule file\n\nUse when: asked\n"), [])

# What a reviewer found PyYAML rejecting that the first version passed, and a value it wrongly flagged.
bad = lambda v: [e["line"] for e in fe(f"---\nname: x\ndescription: {v}\n---\n")]
chk("a value with a trailing comment holding ': ' is valid", bad("foo # bar: baz"), [])
chk("an apostrophe inside a single-quoted value is flagged", bad("'it's here'"), [3])
chk("a doubled '' inside a single-quoted value is fine", bad("'it''s here'"), [])
chk("text after a closing quote is flagged", bad('"foo" bar'), [3])
chk("a plain value starting with % ! '- ' or '? ' is flagged", [bad(v) for v in ("%x", "!t x", "- x", "? x")], [[3]] * 4)
chk("text after a block header is flagged, a comment after it is not", (bad("> foo"), bad(">- # c")), ([3], []))
chk("an unclosed flow collection is flagged, a closed one is not", (bad("[a"), bad("{a: b"), bad("[a, b]")), ([3], [3], []))
chk("a nested mapping value holding ': ' is flagged",
    [e["line"] for e in fe("---\nname: x\nmetadata:\n  short: Use when: x\n---\n")], [4])
chk("a quoted value that runs over two lines is fine",
    fe('---\nname: x\ndescription: "one\n  two"\n---\n'), [])
chk("an unclosed quote is not hidden by a later line holding the same quote character (flagged where the stray quote closes it)",
    [e["line"] for e in fe('---\nname: x\ndescription: "never\nother: say "hi"\n---\n')], [4])
chk("an anchor on a value is valid YAML and is not flagged", bad("&a text"), [])

code, d = run_cli(pack("fm-bad", {
    ".claude-plugin/plugin.json": '{"name": "fb"}',
    "skills/a/SKILL.md": "---\nname: a\ndescription: Use when: asked\n---\nDo a.\n",
    "skills/b/SKILL.md": "---\nname: b\ndescription: fine\n---\nDo b.\n",
    "commands/c.md": "---\ndescription: Run it: now\n---\nGo.\n",
    "agents/d.md": "---\nname: d\ndescription: ok\n---\nYou are d.\n"}))
t = (d or {}).get("target", {})
chk("the dossier names each skill, command and agent whose frontmatter fails, and only those",
    (code,
     sorted(x["name"] for x in t.get("skills", []) if x.get("frontmatter_errors")),
     [c["name"] for c in t.get("commands", []) if c.get("frontmatter_errors")],
     [a["name"] for a in t.get("agents", []) if a.get("frontmatter_errors")]),
    (0, ["a"], ["c"], []))

print(f"\n{checks - fail} passed, {fail} failed")
sys.exit(1 if fail else 0)
