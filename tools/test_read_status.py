#!/usr/bin/env python3
"""target.read_status: the dossier says, for each section, whether it was read, partly read, failed, or
does not apply. Every case runs inventory.py as a command, with HOME, CLAUDE_CONFIG_DIR and --project-dir
all set to one empty directory, so no reader's rule text is ever read or compared.

Fixtures are trees under tools/fixtures/read-status/<name>/. A fixture with a baseline has its dossier from
8ac500d's inventory.py in _baselines/<name>.baseline.json (the fixture's real path written as <ROOT>, the fixtures folder's as <FX>): every
key but read_status must still match it. The fixtures that need many files, a big file or a deep folder are
built in a temporary directory here instead. An unreadable file is always a dangling symlink, never chmod 000
(it cannot be committed, and it passes under root)."""
import json, os, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INVENTORY = ROOT / "skills" / "neckbeard" / "inventory.py"
FX = ROOT / "tools" / "fixtures" / "read-status"
SECTIONS = ["skills", "agents", "commands", "rule_files", "hooks", "mcp_servers",
            "persistence_candidates", "plugin_json", "marketplace"]
EMPTY = tempfile.mkdtemp(prefix="read-status-empty-")
failures = []


def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        failures.append(name)


def dossier(target):
    env = {"PATH": os.environ["PATH"], "HOME": EMPTY, "CLAUDE_CONFIG_DIR": EMPTY}
    r = subprocess.run([sys.executable, str(INVENTORY), str(target), "--project-dir", EMPTY],
                       env=env, capture_output=True, text=True)
    if r.returncode:
        return {"error": r.stderr[-400:]}
    return json.loads(r.stdout)


def fixture(name):
    d = FX / name
    return d / "rules.md" if name.startswith("rulefile-") else d


def status(target):
    d = dossier(target)
    if "error" in d:
        return {"_error": d["error"]}
    return d["target"].get("read_status") or {}


def got(target, section, state, *needles):
    """True when the section has this state and every needle appears in one of its notes."""
    rs = status(target).get(section) or {}
    notes = " | ".join(rs.get("notes") or [])
    return rs.get("state") == state and all(n in notes for n in needles), f"{section}: {rs!r}"


def tmp_tree(files):
    """A temporary tree. A str value is a file's text, bytes a binary one, ("->", x) a symlink."""
    d = Path(tempfile.mkdtemp(prefix="read-status-"))
    for rel, v in files.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(v, tuple):
            os.symlink(v[1], p)
        else:
            p.write_text(v)
    return d


PLUGIN = {".claude-plugin/plugin.json": '{"name": "g", "version": "1.0.0"}\n'}
SKILL = "---\nname: a\ndescription: d\n---\nBody.\n"

# ---------------------------------------------------------------- Done when 1 to 4
check("1. a malformed .mcp.json: mcp_servers failed, note names .mcp.json", *got(fixture("mcp-malformed"), "mcp_servers", "failed", ".mcp.json"))
check("2. one agent a dangling symlink, one fine: agents partial, note names agents/bad.md", *got(fixture("agents-dangling"), "agents", "partial", "agents/bad.md"))
rf = fixture("rulefile-import")
check("3. a rule file with an import it does not follow: rule_files partial, import named", *got(rf, "rule_files", "partial", "sibling.md"))
check("3. ... and agents and commands are not-applicable",
      all(status(rf).get(s, {}).get("state") == "not-applicable" for s in ("agents", "commands")), repr(status(rf).get("agents")))
check("4. a plugin with no hooks: hooks read", *got(fixture("hooks-none"), "hooks", "read"))
check("4. hooks that cannot be traced: hooks partial, injected_content_note text in the notes",
      *got(fixture("hooks-untraced"), "hooks", "partial", "have unknown behaviour, which is not the same as none"))

# ---------------------------------------------------------------- Done when 5
bad = []
for base in sorted((FX / "_baselines").glob("*.baseline.json")):
    name = base.name[: -len(".baseline.json")]
    t = fixture(name)
    d = dossier(t)
    if "error" in d:
        bad.append(f"{name}: {d['error']}")
        continue
    target = d["target"]
    rs = target.pop("read_status", None)
    if not isinstance(rs, dict) or set(rs) != set(SECTIONS):
        bad.append(f"{name}: read_status sections {sorted(rs) if isinstance(rs, dict) else rs!r}")
    if "_read_notes" in target:
        bad.append(f"{name}: _read_notes left in the dossier")
    text = json.dumps(target)
    for real, mark in ((os.path.realpath(FX / name), "<ROOT>"), (os.path.realpath(FX), "<FX>")):
        text = text.replace(json.dumps(real)[1:-1], mark)
    if json.loads(text) != json.loads(base.read_text()):
        bad.append(f"{name}: a key other than read_status differs from the baseline")
check("5. every fixture with a baseline: nine sections, no _read_notes, every other key unchanged", not bad, "; ".join(bad[:4]))

# ---------------------------------------------------------------- Done when 6: one test per site
# add_read_status's docstring lists every site as "<id> <function> -> <section>: <what>". The ids there and the
# ids tested below must be the same set, so a site added to one and not the other is red.
def over(n):
    return "x" * n


def gen_companions():
    files = dict(PLUGIN); files["skills/a/SKILL.md"] = SKILL
    for i in range(42):
        files[f"skills/a/refs/r{i:02d}.md"] = "ref\n"
    return got(tmp_tree(files), "skills", "partial", "refs/r41.md")


def gen_companion_depth():
    files = dict(PLUGIN); files["skills/a/SKILL.md"] = SKILL
    files["skills/a/1/2/3/4/5/6/7/deep.md"] = "deep\n"
    return got(tmp_tree(files), "skills", "partial", "skills/a/1/2/3/4/5/6")


def gen_find_depth():
    return got(tmp_tree({"a/b/c/d/e/f/g/h/i/SKILL.md": SKILL}), "skills", "partial", "a/b/c/d/e/f/g")


def gen_big_skill():
    files = dict(PLUGIN); files["skills/a/SKILL.md"] = SKILL + over(250_000)
    return got(tmp_tree(files), "skills", "partial", "skills/a/SKILL.md", "read capped at 200000 bytes")


def gen_big_claude_md():
    return got(tmp_tree({"CLAUDE.md": "Rules.\n" + over(250_000)}), "rule_files", "partial", "CLAUDE.md", "read capped at 200000 bytes")


def gen_big_hook_script():
    files = dict(PLUGIN)
    files["hooks/hooks.json"] = '{"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks/run.sh"}]}]}}\n'
    files["hooks/run.sh"] = "#!/bin/sh\n" + over(25_000) + "\n"
    return got(tmp_tree(files), "hooks", "partial", "hooks/run.sh", "read capped at 20000 bytes")


def gen_big_json():
    return got(tmp_tree({"data/big.json": '{"k": "' + over(250_000) + '"}'}), "hooks", "partial", "data/big.json")


def gen_big_plain_file():
    return got(tmp_tree({"hookfile": over(250_000)}), "persistence_candidates", "partial", "hookfile")


def gen_big_script():
    return got(tmp_tree({"scripts/big.sh": "#!/bin/sh\n" + over(60_000) + "\n"}), "persistence_candidates", "partial", "scripts/big.sh", "read capped at 50000 bytes")


def search_cap():
    sys.path.insert(0, str(INVENTORY.parent))
    import inventory
    d = tmp_tree({"a/x.json": "{}", "b/y.json": "{}", "c/z.json": "{}"})
    found = tmp_tree({"a/hooks.json": '{"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "x"}]}]}}', "b/y.json": "{}"})
    out = []
    for root, expect in ((d, "failed"), (found, "partial")):
        hooks = inventory.hooks_outside_manifest(str(root), max_reads=1)
        dos = {"kind": "generic-pack", "hooks": hooks}
        try:
            inventory.add_read_status(dos)
        except Exception as e:  # red until add_read_status exists
            return False, repr(e)
        rs = dos.get("read_status", {}).get("hooks", {})
        out.append((rs.get("state"), expect, "b/: " in " ".join(rs.get("notes") or [])))
    return all(s == e and n for s, e, n in out), repr(out)


SITES = {
    "SK1": lambda: got(fixture("skill-unreadable"), "skills", "partial", "skills/b/SKILL.md"),
    "SK2": lambda: got(fixture("refused-entries"), "skills", "failed", "skills/x/SKILL.md"),
    "SK3": lambda: got(fixture("skill-companion"), "skills", "partial", "skills/a/bad.md"),
    "SK4": gen_companions,
    "SK5": gen_companion_depth,
    "SK6": gen_find_depth,
    "SK7": gen_big_skill,
    "AG1": lambda: got(fixture("agents-all-dangling"), "agents", "failed", "agents/bad.md"),
    "AG2": lambda: got(fixture("refused-entries"), "agents", "failed", "agents/a.md"),
    "CM1": lambda: got(fixture("commands-dangling"), "commands", "partial", "commands/bad.md"),
    "CM2": lambda: got(fixture("refused-entries"), "commands", "failed", "commands/c.md"),
    "RF1": lambda: got(fixture("claudemd-dangling"), "rule_files", "failed", "CLAUDE.md"),
    "RF2": lambda: got(fixture("refused-entries"), "rule_files", "failed", "CLAUDE.md"),
    "RF3": lambda: got(fixture("claudemd-dangling-import"), "rule_files", "partial", "gone.md"),
    "RF4": lambda: got(fixture("claudemd-hop-cap"), "rule_files", "partial", "a5.md", "5 hops"),
    "RF5": lambda: got(fixture("claudemd-import-outside"), "rule_files", "partial", "_outside.txt"),
    "RF6": lambda: got(fixture("rulefile-import"), "rule_files", "partial", "sibling.md"),
    "RF7": gen_big_claude_md,
    "HK1": lambda: got(fixture("hooks-bad-json"), "hooks", "failed", "hooks/h.json"),
    "HK2": lambda: got(fixture("hooks-refused"), "hooks", "failed", "_outside.json"),
    "HK3": lambda: got(fixture("hooks-list-missing"), "hooks", "failed", "hooks/nope.json"),
    "HK4": lambda: got(fixture("hooks-path-missing"), "hooks", "failed", "hooks/nope.json", "plugin.json"),
    "HK5": lambda: got(fixture("hooks-malformed-entry"), "hooks", "partial", "hooks/hooks.json", "Stop"),
    "HK6": lambda: got(fixture("hooks-untraced"), "hooks", "partial", "hooks/run.sh"),
    "HK7": lambda: got(fixture("hooks-nonstring-command"), "hooks", "failed", "hooks/hooks.json", "command"),
    "HK8": lambda: got(fixture("outside-links"), "hooks", "partial", "sub/link.json"),
    "HK9": lambda: got(fixture("hooks-search-bad-json"), "hooks", "partial", "data/broken.json"),
    "HK10": search_cap,
    "HK11": lambda: got(fixture("nested-plugins"), "hooks", "failed", "inner: "),
    "HK12": lambda: got(fixture("marketplace-multi"), "hooks", "failed", ".claude-plugin/marketplace.json", "marketplace listing"),
    "HK13": gen_big_hook_script,
    "HK14": gen_big_json,
    "MC1": lambda: got(fixture("mcp-malformed"), "mcp_servers", "failed", ".mcp.json"),
    "MC2": lambda: got(fixture("mcp-not-object"), "mcp_servers", "failed", ".mcp.json"),
    "MC3": lambda: got(fixture("mcp-wrong-type"), "mcp_servers", "failed", ".mcp.json", "mcpServers"),
    "MC4": lambda: got(fixture("mcp-path-string"), "mcp_servers", "failed", "given as a path (./servers.json), not followed"),
    "MC5": lambda: got(fixture("mcp-server-not-object"), "mcp_servers", "partial", ".mcp.json", "bad"),
    "MC6": lambda: got(fixture("mcp-ambiguity"), "mcp_servers", "partial", ".mcp.json", "top level"),
    "MC7": lambda: got(fixture("mcp-refused"), "mcp_servers", "failed", ".mcp.json"),
    "PS1": lambda: got(fixture("outside-links"), "persistence_candidates", "partial", "sub/run.sh"),
    "PS2": gen_big_plain_file,
    "PS3": lambda: got(fixture("persist-dangling"), "persistence_candidates", "partial", "scripts/x.sh"),
    "PS4": gen_big_script,
    "PJ1": lambda: got(fixture("plugin-json-malformed"), "plugin_json", "failed", ".claude-plugin/plugin.json"),
    "PJ2": lambda: got(fixture("plugin-json-list"), "plugin_json", "failed", ".claude-plugin/plugin.json"),
    "PJ3": lambda: got(fixture("plugin-json-dangling"), "plugin_json", "failed", ".claude-plugin/plugin.json"),
    "PJ4": lambda: got(fixture("manifest-refused-plugin"), "plugin_json", "partial", ".claude-plugin/plugin.json"),
    "MK1": lambda: got(fixture("marketplace-pack-broken"), "marketplace", "failed", "marketplace.json"),
    "MK2": lambda: got(fixture("marketplace-root-broken"), "marketplace", "failed", "marketplace.json"),
    "MK3": lambda: got(fixture("marketplace-dangling"), "marketplace", "failed", "marketplace.json"),
    "MK4": lambda: got(fixture("marketplace-entries"), "marketplace", "partial", ".claude-plugin/marketplace.json", "oops"),
    "MK5": lambda: got(fixture("marketplace-entries"), "marketplace", "partial", ".claude-plugin/marketplace.json", "gone"),
    "MK6": lambda: got(fixture("marketplace-entry-outside"), "marketplace", "partial", ".claude-plugin/marketplace.json", "elsewhere"),
}
sys.path.insert(0, str(INVENTORY.parent))
try:
    import inventory
    doc = inventory.add_read_status.__doc__ or ""
except (ImportError, AttributeError):
    doc = ""
listed = set(re.findall(r"^\s+([A-Z]{2}\d+)\s", doc, re.M))
check("6. add_read_status's docstring lists exactly the sites tested here", listed == set(SITES),
      f"only in the docstring: {sorted(listed - set(SITES))}; only tested: {sorted(set(SITES) - listed)}")
for sid, fn in SITES.items():
    try:
        ok, detail = fn()
    except Exception as e:
        ok, detail = False, repr(e)
    check(f"6. site {sid}", ok, detail)

# ---------------------------------------------------------------- Done when 7
f = FX
check("7. a marketplace_note (a marketplace listing several plugins): hooks failed",
      *got(f / "marketplace-multi", "hooks", "failed", ".claude-plugin/marketplace.json", "marketplace listing"))
check("7. an ambiguity (servers at the top of .mcp.json): mcp_servers partial", *got(f / "mcp-ambiguity", "mcp_servers", "partial", ".mcp.json", "top level"))
check("7. manifest_refused on a plugin: plugin_json partial", *got(f / "manifest-refused-plugin", "plugin_json", "partial", "plugin.json"))
check("7. manifest_refused on a generic pack: plugin_json failed", *got(f / "manifest-refused-pack", "plugin_json", "failed", "plugin.json"))
check("7. a truncated skill: skills partial", *gen_big_skill())
check("7. malformed_entries: hooks partial", *got(f / "hooks-malformed-entry", "hooks", "partial", "hooks/hooks.json", "Stop"))
check("7. a broken marketplace.json at a plugin root: marketplace failed", *got(f / "marketplace-root-broken", "marketplace", "failed", "marketplace.json"))
check("7. a generic pack with no manifest: plugin_json and marketplace not-applicable",
      all(status(f / "pack-plain").get(s, {}).get("state") == "not-applicable" for s in ("plugin_json", "marketplace")),
      repr(status(f / "pack-plain").get("plugin_json")))
check("7. a plugin with nothing wrong: every section read or not-applicable, never partial or failed",
      all(v.get("state") in ("read", "not-applicable") for v in status(f / "plugin-full").values()) and bool(status(f / "plugin-full")),
      repr(status(f / "plugin-full")))
check("7. a rule file: every section but rule_files not-applicable",
      all(status(fixture("rulefile-plain")).get(s, {}).get("state") == "not-applicable" for s in SECTIONS if s != "rule_files")
      and status(fixture("rulefile-plain")).get("rule_files", {}).get("state") == "read", repr(status(fixture("rulefile-plain"))))

print(f"test_read_status: {'all passed' if not failures else str(len(failures)) + ' failed'}")
sys.exit(1 if failures else 0)
