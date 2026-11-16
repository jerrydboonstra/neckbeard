#!/usr/bin/env python3
"""Mechanical half of neckbeard: read a target and the user's current rules,
emit one JSON dossier. Makes no judgment calls — that's the SKILL.md's job.

Usage:
  inventory.py <target> [--project-dir DIR] [--extra-rules PATH ...] [--out FILE] [--plugin NAME]

<target> is one of:
  - an installed plugin, "name@marketplace" (e.g. "ponytail@ponytail")
  - a local directory path (a cloned repo, a skill pack, a plugin source tree)
  - a single rule file (a CLAUDE.md or any markdown of rules)
  - a git URL (cloned read-only into a temp dir, depth 1)

Stdlib only. Read-only: never writes inside the target, never touches the
user's rule files, only ever writes to --out or a temp clone directory.
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import tempfile

# a caller that loads this file by path still finds its sibling modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inventory_core
from inventory_core import (  # noqa: F401  (each name stays reachable as inventory.<name>)
    READ_LIMIT, _Note, _name_from_path, _note, _prune_skipped, _rel, _walk_error, _walk_gaps, _within,
    find_files, find_project_root, frontmatter_errors, measure, note_frontmatter, read_json, read_text,
    rule_item, split_frontmatter,
)
from inventory_core import find_up as _core_find_up
from inventory_hooks import (  # noqa: F401  (each name stays reachable as inventory.<name>)
    SUBAGENT_EVENTS, SUBAGENT_TOOL_EVENTS, SUBAGENT_TOOL_EVENTS_LIKELY, PERSIST_PATTERNS, SCRIPT_EXTS,
    JS_REQUIRE_RE, PATH_JOIN_RE, _literal_path_candidates, resolve_injected_text, _expand_plugin_root,
    _identify_hook_script, inventory_hooks, _merge_hook_list, _parse_events, HOOK_EVENTS, NOT_HOOK_CONFIG,
    _hook_events_in, settings_writers, hooks_outside_manifest, inventory_persistence,
)
from inventory_parts import (  # noqa: F401  (each name stays reachable as inventory.<name>)
    marketplace_listing, mcp_servers, contained_skill, COMPANION_LIMIT, skill_companions, inventory_skills,
    plugin_skills, inventory_commands_agents, IMPORT_MAX_HOPS, _CODE_RE, _IMPORT_RE, claude_md_imports,
    with_imports, target_rule_files,
)
from inventory_dossier import (  # noqa: F401  (each name stays reachable as inventory.<name>)
    READ_SECTIONS, inventory_target, add_read_status,
)


HOME = os.path.expanduser("~")
CLAUDE_HOME = os.environ.get("CLAUDE_CONFIG_DIR", os.path.join(HOME, ".claude"))


def find_up(start, filename):
    """Walk up from start looking for filename; stop at $HOME or filesystem root."""
    return _core_find_up(start, filename, home=HOME)


# Where Claude Code reads file-based managed (enterprise) settings, per platform.
# A module-level list so selfcheck.py can point it at a fixture.
MANAGED_SETTINGS = {
    "darwin": ["/Library/Application Support/ClaudeCode/managed-settings.json"],
    "win32": [r"C:\Program Files\ClaudeCode\managed-settings.json"],
}.get(sys.platform, ["/etc/claude-code/managed-settings.json"])



# The helpers every other part uses (reading, notes, frontmatter, the containment guard, file search) live in inventory_core.py.


# ------------------------------------------------------------------ target resolution
def resolve_installed_plugin(name, marketplace):
    """Return a local directory for an installed plugin, or None."""
    installed = read_json(os.path.join(CLAUDE_HOME, "plugins", "installed_plugins.json")) or {}
    for rec in (installed.get("plugins") or {}).get(f"{name}@{marketplace}", []):
        p = rec.get("installPath")
        if p and os.path.isfile(os.path.join(p, ".claude-plugin", "plugin.json")):
            return p
    # installed_plugins.json's installPath is usually absent for a directory-
    # source marketplace, but not always: if that directory is itself a git
    # repo, Claude Code may cache it anyway, keyed to plugin.json's version,
    # and the cache can go stale silently if the version number never moves.
    # Verify a found installPath actually has the manifest before trusting it,
    # and fall back to the marketplace's own listing when it does not. See
    # CASE-STUDIES.md, round 2.
    markets = read_json(os.path.join(CLAUDE_HOME, "plugins", "known_marketplaces.json")) or {}
    m = markets.get(marketplace)
    if not m:
        return None
    loc = m.get("installLocation")
    if not loc:
        return None
    if os.path.isfile(os.path.join(loc, ".claude-plugin", "plugin.json")):
        mj = read_json(os.path.join(loc, ".claude-plugin", "plugin.json")) or {}
        if mj.get("name") == name:
            return loc  # single-plugin marketplace (e.g. "ponytail@ponytail")
    mkt_manifest = read_json(os.path.join(loc, ".claude-plugin", "marketplace.json")) or {}
    for entry in mkt_manifest.get("plugins", []):
        if entry.get("name") == name:
            return os.path.normpath(os.path.join(loc, entry.get("source", ".")))
    return None


def resolve_target(target, tmp_root):
    # An existing local directory is a local directory, whatever it is called.
    # Check that before testing for a git-URL pattern, or a local directory
    # named repo.git gets sent to git clone and crashes.
    if os.path.isdir(os.path.expanduser(target)):
        path = os.path.realpath(os.path.expanduser(target))
        return path, "local-path"
    # A single rule file (someone's CLAUDE.md, a pasted rules.md). The skill
    # vets one of these just as it vets a plugin or a directory.
    if os.path.isfile(os.path.expanduser(target)):
        return os.path.realpath(os.path.expanduser(target)), "local-file"
    if re.match(r"^(https?://|git@|ssh://).*|.*\.git$", target):
        dest = os.path.join(tmp_root, "clone")
        subprocess.run(["git", "clone", "--depth", "1", target, dest],
                        check=True, capture_output=True, text=True)
        return dest, "git-clone"
    if "@" in target and "/" not in target and os.sep not in target:
        name, marketplace = target.split("@", 1)
        path = resolve_installed_plugin(name, marketplace)
        if not path:
            sys.exit(f"could not resolve installed plugin '{target}' — pass a local path instead")
        return path, "installed-plugin"
    path = os.path.realpath(os.path.expanduser(target))
    if not os.path.isdir(path):
        sys.exit(f"not a directory: {path}")
    return path, "local-path"


# ------------------------------------------------------------------ settings layering
def merge_enabled_plugins(project_root):
    """Which plugins are enabled, merged the way Claude Code layers its settings.

    WHICH PLUGINS ARE ENABLED IS NOT ONE FILE. Claude Code reads the user's
    ~/.claude/settings.json, then the project's .claude/settings.json, then
    .claude/settings.local.json, each overriding the one before. Reading only
    the project file misses every plugin enabled globally, which is the normal
    way to enable one -- a project with no .claude/ directory at all can then
    see only a fraction of the rules actually in force, and the comparison
    reports no conflicts because the conflicting rules were invisible.

    Personal SKILLS were already read from CLAUDE_HOME, which is why under-
    reading enabled plugins here reads as an oversight rather than a decision.

    Later layers override earlier ones, including overriding true with false,
    so a project may legitimately disable a globally-enabled plugin and that
    is honoured rather than unioned away.

    See CHANGELOG.md 1.11.4."""
    merged = {}
    for settings_path in (
        os.path.join(CLAUDE_HOME, "settings.json"),
        os.path.join(project_root, ".claude", "settings.json"),
        os.path.join(project_root, ".claude", "settings.local.json"),
        # Managed settings sit above every other layer and nothing overrides
        # them, so an organisation that force-disables a plugin there must win.
        # MDM- and console-delivered policy is not readable from disk and
        # stays out of reach; see MANAGED_SETTINGS. See CASE-STUDIES.md,
        # round 14.
        *MANAGED_SETTINGS,
    ):
        if not os.path.isfile(settings_path):
            continue
        layer = read_json(settings_path)
        if layer is None:
            # Skipping a broken layer is right; skipping it in silence is not.
            # A corrupt settings.json read exactly like "no plugins enabled".
            print(f"warning: {settings_path} is not valid JSON; its enabledPlugins "
                  "were not read, so the rules of any plugin it enables are missing "
                  "from current_rules", file=sys.stderr)
            continue
        got = layer.get("enabledPlugins") if isinstance(layer, dict) else None
        if isinstance(got, dict):
            merged.update(got)
    return merged


# ------------------------------------------------------------------ current-rules discovery
def discover_current_rules(project_dir, extra_paths):
    items = []
    global_claude_md = os.path.join(CLAUDE_HOME, "CLAUDE.md")
    if os.path.isfile(global_claude_md):
        items.extend(with_imports("global-CLAUDE.md", global_claude_md))

    project_root = find_project_root(project_dir)
    proj_claude_md = find_up(project_dir, "CLAUDE.md")
    if proj_claude_md and proj_claude_md != global_claude_md:
        items.extend(with_imports("project-CLAUDE.md", proj_claude_md))

    for label, base in (("project-skill", os.path.join(project_root, ".claude", "skills")),
                         ("personal-skill", os.path.join(CLAUDE_HOME, "skills"))):
        for sm in glob.glob(os.path.join(base, "*", "SKILL.md")):
            it = rule_item(label, sm)
            if it:
                items.append(it)

    # Layered across user, project and project-local settings; see the function.
    for key, enabled in merge_enabled_plugins(project_root).items():
        if not enabled or "@" not in key:
            continue
        name, marketplace = key.split("@", 1)
        p = resolve_installed_plugin(name, marketplace)
        if p:
            for sm in find_files(p, {"SKILL.md"}):
                it = rule_item(f"enabled-plugin:{key}", sm)
                if it:
                    items.append(it)

    for extra in extra_paths or []:
        extra = os.path.expanduser(extra)
        if not os.path.exists(extra):
            print(f"warning: --extra-rules {extra} does not exist", file=sys.stderr)
            continue
        if os.path.isfile(extra):
            it = rule_item("extra", extra)
            if it:
                items.append(it)
        elif os.path.isdir(extra):
            # The user pointed here explicitly, so take every markdown file
            # rather than only the two canonical names: filtering by filename
            # would silently contribute nothing unless a file happened to be
            # named SKILL.md or CLAUDE.md, defeating the flag's purpose. See
            # CASE-STUDIES.md, round 7.
            found = 0
            for dirpath, dirnames, filenames in os.walk(extra):
                dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules")]
                for fn in sorted(filenames):
                    if fn.lower().endswith((".md", ".markdown", ".txt")):
                        it = rule_item("extra", os.path.join(dirpath, fn))
                        if it:
                            items.append(it)
                            found += 1
            if not found:
                print(f"warning: --extra-rules {extra} matched no readable rule files",
                      file=sys.stderr)

    seen, deduped = set(), []
    for it in items:
        if it["path"] not in seen:
            seen.add(it["path"])
            deduped.append(it)
    return deduped, project_root


# ------------------------------------------------------------------ main
def warn_about_embedded_rules(out_path, current_items):
    """A dossier embeds the full text of every rule file discovered, which is
    the point (the classification needs it) and also a hazard: those files are
    the user's global CLAUDE.md, their project rules, their personal skills and
    the skills of every plugin they have enabled. Writing that to disk is one
    `git add` away from publishing private configuration and identifiers. See
    CASE-STUDIES.md, round 9.

    A warning rather than redaction, because the text is load-bearing for the
    comparison. Say what is in the file and let the reader decide."""
    total = sum(len(i.get("text") or "") for i in current_items)
    if not total:
        return
    print(f"\nNOTE: {out_path} embeds {total:,} bytes from {len(current_items)} "
          f"of your rule files, verbatim:", file=sys.stderr)
    for i in current_items[:8]:
        print(f"  {i.get('bytes', 0):>7,}  {i.get('path')}", file=sys.stderr)
    if len(current_items) > 8:
        print(f"  ... and {len(current_items) - 8} more", file=sys.stderr)
    print("Those are your rules, not the target's. Do not commit this file, and "
          "check your .gitignore before you do anything else with it.\n", file=sys.stderr)


def classifiable_items(target_dossier):
    """How many things in the target the classification step can actually sort.

    Step 2 compares each item the target carries against the user's rules, so a
    target that carries none gives it nothing to do -- and `current_rules` is the
    expensive, sensitive half of the dossier: the verbatim text of the global
    CLAUDE.md, the project rules, every personal skill and every enabled plugin's
    skills. Reading and embedding all of that for a target with nothing
    classifiable wastes bytes and exposes those rules for no reason.

    Counts skills, rule files, commands, agents, and ANY hook at all -- not
    only the ones whose payload resolved. An unresolved hook is not "nothing to
    inject"; it is the case where the reader most needs their own rules in
    hand, because they are about to go read that script by hand. See
    CASE-STUDIES.md, round 11 and round 14.

    Deliberately fails toward INCLUDING the rules. Skipping them when there IS
    something to classify breaks the tool; carrying them when there is not only
    wastes bytes. So this returns a count and the caller skips on a hard zero,
    rather than judging whether the items found are worth comparing."""
    # Commands, agents and rule files carry instructions too; counting only
    # skills and hooks would skip the reader's rules for a pack of nothing but
    # commands/ and agents/. See CASE-STUDIES.md, round 14.
    n = sum(len(target_dossier.get(k) or [])
            for k in ("skills", "rule_files", "commands", "agents"))
    hooks = target_dossier.get("hooks") or {}
    if isinstance(hooks, dict) and hooks.get("has_hooks"):
        # a script traced as printing nothing but writing files carries no text for the reader to classify
        n += max(1, len([e for e in hooks.get("injected_content") or []
                         if not (isinstance(e, dict) and e.get("built_at_run_time") and not e.get("template"))]))
    return n


def add_live_mcp(target_dossier, path, name, timeout, max_bytes, max_pages=16, max_items=500):
    """--live-mcp NAME: put the server's live surface on its mcp_servers entry as `live`. Called in main()
    before add_read_status, so the notes it records (on target["_read_notes"]["mcp_servers"], through
    _note) are folded into read_status. The live root is the target's own folder: for a marketplace
    listing, the chosen plugin's folder. A refusal or a failed read (status "refused" or "error") keeps
    its status and message on `live` and adds a note naming the server (LV1 to LV3 below, in
    add_read_status's list). A name the target does not declare has no entry to carry `live`: it is
    a note too."""
    from mcp_live import find_declaration, inventory_live_mcp, refusal_cause   # only a --live-mcp run needs it
    notes = (target_dossier.get("_read_notes") or {}).get("mcp_servers")
    root = target_dossier.get("path") or path
    declaration, refusal = find_declaration(root, name)
    if refusal:
        _note(notes, f"live MCP server {name!r}: {refusal}", cause="tool-limit" if refusal_cause(refusal) == "tool-limit" else "target-fault")   # LV1
        return
    live = inventory_live_mcp(root, declaration, timeout=max(0.1, timeout), max_bytes=max(1024, max_bytes),
                               max_pages=max(1, max_pages), max_items=max(1, max_items))
    status = live.get("status")
    if status == "refused":
        _note(notes, f"live MCP server {name!r}: refused: {live.get('refusal')}", cause="target-fault" if live.get("cause") == "target-fault" else "tool-limit")   # LV2
    elif status != "ok":   # "error": the read failed; "partial": a list failed and the rest stands
        _note(notes, f"live MCP server {name!r}: {live.get('error')}", cause="tool-limit" if live.get("cause") == "tool-limit" else "target-fault")   # LV3
    for entry in (target_dossier.get("mcp_servers") or {}).get("servers") or []:
        if entry.get("name") == name:
            entry["live"] = live


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target")
    ap.add_argument("--project-dir", default=os.getcwd())
    ap.add_argument("--extra-rules", action="append", default=[])
    ap.add_argument("--out")
    ap.add_argument("--plugin", help="when the target is a marketplace listing several "
                                     "plugins, the one to inventory")
    ap.add_argument("--live-mcp", metavar="NAME", help="opt in to initialization and "
                    "metadata-only inventory of one declared local stdio MCP server")
    ap.add_argument("--live-mcp-timeout", type=float, default=8.0,
                    help=argparse.SUPPRESS)
    ap.add_argument("--live-mcp-max-bytes", type=int, default=1_000_000,
                    help=argparse.SUPPRESS)
    ap.add_argument("--live-mcp-max-pages", type=int, default=16, help=argparse.SUPPRESS)
    ap.add_argument("--live-mcp-max-items", type=int, default=500, help=argparse.SUPPRESS)
    args = ap.parse_args()

    with tempfile.TemporaryDirectory(prefix="neckbeard-") as tmp:
        path, resolution = resolve_target(args.target, tmp)
        target_dossier = inventory_target(path, args.plugin)
        if args.live_mcp:
            add_live_mcp(target_dossier, path, args.live_mcp, args.live_mcp_timeout, args.live_mcp_max_bytes,
                         args.live_mcp_max_pages, args.live_mcp_max_items)
        add_read_status(target_dossier)
        target_dossier["resolved_via"] = resolution
        target_dossier["requested_target"] = args.target
        if classifiable_items(target_dossier):
            current_items, project_root = discover_current_rules(args.project_dir, args.extra_rules)
            current = {"project_root": project_root, "items": current_items}
        else:
            # Nothing to compare against, so do not read -- let alone embed -- the
            # reader's private rule files. See classifiable_items().
            current_items, current = [], {
                "project_root": None,
                "items": [],
                "skipped": "The target carries no classifiable item (no skill, "
                           "hook, command, agent or rule file), so there is nothing for the "
                           "classification step to compare against and your rule "
                           "files were not read. Anything the target still needs "
                           "looked at -- unresolved hooks, an MCP server, "
                           "persistence -- is reported above, and reading it does "
                           "not need your rules.",
            }
        dossier = {
            "target": target_dossier,
            "current_rules": current,
        }
        out = json.dumps(dossier, indent=2, ensure_ascii=False)
        if args.out:
            with open(args.out, "w") as f:
                f.write(out)
            print(f"wrote {args.out}")
            warn_about_embedded_rules(args.out, current_items)
        else:
            print(out)


if __name__ == "__main__":
    main()
