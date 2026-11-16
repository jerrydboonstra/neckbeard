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


# ------------------------------------------------------------------ plugin inventory


READ_SECTIONS = ("skills", "agents", "commands", "rule_files", "hooks", "mcp_servers",
                 "persistence_candidates", "plugin_json", "marketplace")


def inventory_target(path, plugin_name=None, _read_root=False):
    if os.path.isfile(path):
        text = read_text(path)
        if text is None or "\x00" in text:
            sys.exit(f"{path}: not a readable text file, so there are no rules to read")
        # A CLAUDE.md's @-imports are part of its format, so they are followed,
        # still contained to its folder. Any other file is one trust boundary: a
        # downloaded rules.md must not gain a read of its sibling files by
        # naming them. The names it gives are listed, never read.
        notes = {s: [] for s in READ_SECTIONS}
        if os.path.basename(path) == "CLAUDE.md":
            rule_files, not_followed = with_imports("rule-file", path, root=os.path.dirname(path),
                                                    notes=notes["rule_files"]), []
        else:
            rule_files = [rule_item("rule-file", path)]
            not_followed = [m.group(1).rstrip(".,;:)]}\"'")
                            for m in _IMPORT_RE.finditer(_CODE_RE.sub(" ", text))]
        target = {
            "kind": "rule-file",
            "path": path,
            "is_plugin": False,
            "skills": [],
            "rule_files": rule_files,
            "hooks": {"has_hooks": False},
            "_read_notes": notes,
        }
        if not_followed:
            target["imports_not_followed"] = not_followed
        return target
    # A marketplace at the root: inventory the plugin it lists, not the root. With
    # one local plugin that is unambiguous; with several, --plugin picks, and
    # without it the root is read as before but its hooks are reported as unknown,
    # because the plugins that carry them were not read.
    notes = {s: [] for s in READ_SECTIONS}
    market = None if _read_root else marketplace_listing(path, notes["marketplace"])
    if market is not None:
        notes["_marketplace_seen"] = True  # a plugin's dossier has no marketplace key to show it
    local = [p for p in (market or {}).get("plugins", []) if p.get("status") == "local"]
    # A marketplace that lists the root itself ("./") makes the root a plugin in its own
    # right. With nested local plugins beside it, and no --plugin, the root is the default
    # target; --plugin may name the root's own entry. The root is read without its
    # marketplace (_read_root), so this does not recurse, and the marketplace is attached
    # after, with the root selected and a hint on each nested entry.
    root_entry = next((p for p in (market or {}).get("plugins", []) if p.get("status") == "the root itself"), None)
    if root_entry and ((plugin_name is None and local) or
                       (plugin_name is not None and plugin_name == root_entry.get("name"))):
        inventory_core._SKIP_DIRS = {os.path.realpath(p["dir"]) for p in local if p.get("dir")}
        try:
            sub = inventory_target(path, _read_root=True)
        finally:
            inventory_core._SKIP_DIRS = set()
        sub["_read_notes"]["marketplace"].extend(notes["marketplace"])
        sub["_read_notes"]["_marketplace_seen"] = True
        sub["marketplace"] = {"name": market.get("name"), "root": path,
                              "selected": root_entry["name"],
                              "selected_source": root_entry["source"],
                              "plugins": [{**{k: v for k, v in p.items() if k != "dir"},
                                           **({"hint": f"run again with --plugin {p['name']}"}
                                              if p.get("status") == "local" else {})}
                                          for p in market["plugins"]]}
        return sub
    if plugin_name is not None:
        chosen = next((p for p in local if p.get("name") == plugin_name), None)
        if not chosen:
            names = ", ".join(str(p.get("name")) for p in local) or "none"
            sys.exit(f"--plugin {plugin_name}: not a plugin in this repository's marketplace "
                     f"(local plugins: {names})")
    else:
        chosen = local[0] if len(local) == 1 else None
    if chosen:
        sub = inventory_target(chosen["dir"])
        sub["_read_notes"]["marketplace"].extend(notes["marketplace"])
        sub["marketplace"] = {"name": market.get("name"), "root": path,
                              "selected": chosen["name"],
                              "selected_source": chosen["source"],
                              "plugins": [{k: v for k, v in p.items() if k != "dir"}
                                          for p in market["plugins"]]}
        return sub
    plugin_json_path, manifest_refused, dangling = None, None, None
    for cand in (os.path.join(path, ".claude-plugin", "plugin.json"), os.path.join(path, "plugin.json")):
        if os.path.isfile(cand) and not _within(cand, path):
            manifest_refused = (f"{os.path.relpath(cand, path)} resolves outside the target "
                                "tree; not read, so this was inventoried as a plain pack")
            continue
        if os.path.isfile(cand):
            plugin_json_path = cand
            break
        if os.path.lexists(cand):
            dangling = os.path.relpath(cand, path)
    if dangling:
        if plugin_json_path:
            _note(notes["plugin_json"], f"{dangling}: not a readable file (a dangling symlink, or a folder); "
                                        f"{os.path.relpath(plugin_json_path, path)} was read instead", cause="target-fault")
        else:
            _note(notes["plugin_json"], f"{dangling}: not a readable file (a dangling symlink, or a folder); not read, "
                                        "so this was inventoried as a plain pack", "failed", cause="target-fault")
    if not plugin_json_path:
        # Generic pack: no plugin manifest, so no canonical layout. Search
        # broadly for skills.
        #
        # STILL CHECK FOR HOOKS. A directory can carry hooks/hooks.json with no
        # manifest at all, so asserting "no manifest means no hooks" without
        # looking would under-report a hook that reaches every subagent, which
        # is the worst direction for this tool to be wrong in. See
        # CASE-STUDIES.md, round 6.
        skills = inventory_skills(path, notes["skills"])
        readme = None
        for r in ("README.md", "readme.md"):
            if os.path.isfile(os.path.join(path, r)) and _within(os.path.join(path, r), path):
                readme = read_text(os.path.join(path, r), limit=4000)
                break
        hooks = inventory_hooks(path, {}, notes["hooks"])
        if market and market.get("plugins"):
            # The plugins this marketplace lists carry their own hooks, and none of
            # them was inventoried. A tree search would merge several plugins'
            # hooks into one list that no install ever produces, so say unknown.
            names = ", ".join(str(p.get("name")) for p in market["plugins"])
            hooks = {"has_hooks": "unknown", "events": {}, "hook_scripts": None,
                     "hook_registrations": None, "hooks_reach_subagents": None,
                     "marketplace_note": (
                         f"This is a marketplace listing {len(market['plugins'])} plugins "
                         f"({names}); each carries its own hooks and none was inventoried. "
                         "Run again with --plugin NAME for each one you would install.")}
        return {
            "kind": "generic-pack",
            "path": path,
            "is_plugin": False,
            "skills": skills,
            "hooks": hooks,
            **({"marketplace": {"name": market.get("name"),
                                "plugins": [{k: v for k, v in p.items() if k != "dir"}
                                            for p in market["plugins"]],
                                # a marketplace.json that failed to parse or was refused
                                # says so, rather than reading as one that lists nothing
                                **{k: market[k] for k in ("parse_error", "refused") if k in market}}}
               if market else {}),
            "mcp_servers": mcp_servers({}, path, notes["mcp_servers"]),
            "persistence_candidates": inventory_persistence(path, notes["persistence_candidates"]),
            "rule_files": target_rule_files(path, notes["rule_files"]),
            **dict(zip(("commands", "agents"), inventory_commands_agents(path, notes))),
            "readme_excerpt": readme,
            **({"manifest_refused": manifest_refused} if manifest_refused else {}),
            "_read_notes": notes,
        }
    skills = plugin_skills(path, notes["skills"])
    plugin_json = read_json(plugin_json_path)
    if not isinstance(plugin_json, dict):
        why = "is not valid JSON" if plugin_json is None else f"is a {type(plugin_json).__name__}, expected an object"
        _note(notes["plugin_json"], f"{os.path.relpath(plugin_json_path, path)}: {why}", "failed", cause="target-fault")
        plugin_json = {}
    return {
        "kind": "plugin",
        "path": path,
        "is_plugin": True,
        "plugin_json": {k: plugin_json.get(k) for k in ("name", "version", "description", "license")},
        "declares_hooks_in_manifest": "hooks" in plugin_json,
        "declares_agents_in_manifest": "agents" in plugin_json,
        "mcp_servers": mcp_servers(plugin_json, path, notes["mcp_servers"]),
        "skills": skills,
        "hooks": inventory_hooks(path, plugin_json, notes["hooks"]),
        "persistence_candidates": inventory_persistence(path, notes["persistence_candidates"]),
        "rule_files": target_rule_files(path, notes["rule_files"]),
        **dict(zip(("commands", "agents"), inventory_commands_agents(path, notes))),
        **({"manifest_refused": manifest_refused} if manifest_refused else {}),
        "_read_notes": notes,
    }


# ------------------------------------------------------------------ read status
def add_read_status(dossier):
    """Add `read_status` to a target dossier: for each of nine sections, whether it was read, partly
    read, failed or does not apply, so a reader of the dossier can tell an empty section from one that
    could not be read. Called once, in main(), right after inventory_target.

    Shape: {section: {"state": "read" | "partial" | "failed" | "not-applicable", "notes": [str], "causes": [str]}} for
    skills, agents, commands, rule_files, hooks, mcp_servers, persistence_candidates, plugin_json and
    marketplace. A note reads "<path relative to the target>: <reason>". `causes` is a list as long as `notes`,
    each "tool-limit" (neckbeard's limit) or "target-fault" (the plugin's); both _note and add take it as a
    required keyword, and tools/test_read_status.py scans the source so a site without one fails. Every other key of the dossier
    is as it was; this only adds.

    Where the notes come from. Each site below records its own note on the list inventory_target passed
    down (`notes=`), kept as target["_read_notes"] until this folds it in and deletes it. Reason keys
    the dossier already carries (refused, truncated, imports_not_followed, parse_error,
    malformed_entries, injected_content_note, unresolved_hooks, unidentifiable_hooks, marketplace_note,
    nested_plugins, search_incomplete, manifest_refused) are folded in here, in the section they
    belong to. A note's level sets the state: "failed" makes the section failed; "entry" makes a list
    section failed when no entry of it was read, else partial; any other note makes it partial. A
    section with no note is read. Not-applicable: a rule-file target has every section but rule_files;
    a generic pack has no plugin_json unless a manifest was refused or dangling; marketplace is
    not-applicable unless the target has a marketplace.json.

    Every site that turns a failed read or parse, a cap or a wrong-typed value into None, {}, [], "" or
    a skip records a note. They are, with a test each in tools/test_read_status.py:
      SK1 contained_skill -> skills: an unreadable SKILL.md is dropped (entry)
      SK2 contained_skill -> skills: a SKILL.md that resolves outside the tree is refused (key refused)
      SK3 skill_companions -> skills: an unreadable companion file has no text
      SK4 skill_companions -> skills: a companion past the 40 cap is listed without text (key skipped)
      SK5 skill_companions -> skills: folders deeper than 6 are not walked
      SK6 find_files -> skills: folders deeper than 6 are not searched (a generic pack)
      SK7 measure -> skills: a SKILL.md over the read limit is cut (key truncated)
      SK8 find_files -> skills: a symlinked folder is not entered, so a skill inside it is not read
      AG1 inventory_commands_agents -> agents: a dangling symlink or folder named *.md, or a file
          rule_item cannot read, is skipped (entry)
      AG2 inventory_commands_agents -> agents: a file that resolves outside the tree is refused
      CM1 inventory_commands_agents -> commands: as AG1
      CM2 inventory_commands_agents -> commands: as AG2
      RF1 target_rule_files -> rule_files: a CLAUDE.md that is a dangling symlink reads as absent (entry)
      RF2 target_rule_files -> rule_files: a CLAUDE.md that resolves outside the tree is refused
      RF3 claude_md_imports -> rule_files: an import that is a dangling symlink is skipped (entry); one
          that names no file at all is prose ("@someone") and says nothing
      RF4 claude_md_imports -> rule_files: imports past the 5-hop cap are not followed
      RF5 with_imports -> rule_files: an import that resolves outside the tree is refused (tested); a
          file or import that rule_item cannot read is dropped with a note (entry; untested, since it
          takes a file that exists and cannot be opened, and a test may not chmod one)
      RF6 inventory_target -> rule_files: a rule file other than CLAUDE.md follows no imports (key
          imports_not_followed)
      RF7 measure -> rule_files: a rule file over the read limit is cut (key truncated)
      HK1 inventory_hooks -> hooks: a hooks file that is not valid JSON, or whose events container, or
          plugin.json's own hooks value, is the wrong type (key parse_error)
      HK2 inventory_hooks -> hooks: a hooks file that resolves outside the tree (key refused)
      HK3 _merge_hook_list -> hooks: a listed hooks file that is missing, outside or not JSON
      HK4 inventory_hooks -> hooks: plugin.json names a hooks path that is not a file, so the search
          falls back to the tree (failed, whatever the search finds)
      HK5 _parse_events -> hooks: a malformed event, group or hook entry (key malformed_entries)
      HK6 _parse_events -> hooks: a hook script whose payload cannot be traced or whose script cannot
          be identified (keys unresolved_hooks, unidentifiable_hooks, injected_content_note)
      HK7 _parse_events -> hooks: a hook command that is not a string used to crash (failed)
      HK8 hooks_outside_manifest -> hooks: a JSON file that resolves outside the tree, or cannot be
          read, is not searched
      HK9 hooks_outside_manifest -> hooks: a JSON file that does not parse is read as not-hooks
      HK10 hooks_outside_manifest -> hooks: the search stops at max_reads (key search_incomplete;
          failed when nothing was found, else partial)
      HK11 hooks_outside_manifest -> hooks: hooks found only inside nested plugins (key nested_plugins)
      HK12 inventory_target -> hooks: a marketplace of several plugins has none of its hooks read (key
          marketplace_note)
      HK13 resolve_injected_text -> hooks: a hook script is read only to 20000 characters
      HK14 hooks_outside_manifest -> hooks: a JSON file over the read limit is not searched
      HK15 hooks_outside_manifest -> hooks: a JSON file whose size cannot be read (a dangling symlink)
      MC1 mcp_servers -> mcp_servers: .mcp.json exists and does not parse (absent is read, no entries)
      MC2 mcp_servers -> mcp_servers: .mcp.json parses to something that is not an object
      MC3 mcp_servers -> mcp_servers: mcpServers is not an object
      MC4 mcp_servers -> mcp_servers: plugin.json's mcpServers is a path, which is not followed
      MC8 mcp_servers -> mcp_servers: plugin.json's mcpServers is neither a path nor an object
      MC5 mcp_servers -> mcp_servers: a server entry that is not an object has no command or url
      MC6 mcp_servers -> mcp_servers: servers at the top of .mcp.json are a guess (ambiguity)
      MC7 mcp_servers -> mcp_servers: .mcp.json resolves outside the tree (refused)
      PS1 inventory_persistence -> persistence_candidates: a file that resolves outside the tree
      PS2 inventory_persistence -> persistence_candidates: an extension-less file over 200000 bytes, or
          one whose size cannot be read
      PS3 inventory_persistence -> persistence_candidates: a file read_text cannot read counted as "no
          match"
      PS4 inventory_persistence -> persistence_candidates: a script is read only to 50000 characters
      PJ1 inventory_target -> plugin_json: plugin.json does not parse (it read as {})
      PJ2 inventory_target -> plugin_json: plugin.json parses to something that is not an object (it
          crashed)
      PJ3 inventory_target -> plugin_json: plugin.json is a dangling symlink (read as a plain pack)
      PJ4 inventory_target -> plugin_json: a manifest that resolves outside the tree (key
          manifest_refused; partial when another manifest was read, failed for a generic pack)
      MK1 marketplace_listing -> marketplace: marketplace.json does not parse or lists no plugins
          (generic pack)
      MK2 marketplace_listing -> marketplace: the same at a plugin's root, where the dossier has no
          marketplace key
      MK3 marketplace_listing -> marketplace: marketplace.json is a dangling symlink
      MK4 marketplace_listing -> marketplace: an entry that is not an object is skipped
      MK5 marketplace_listing -> marketplace: an entry whose folder is missing
      MK6 marketplace_listing -> marketplace: an entry that resolves outside the tree
      MK7 marketplace_listing -> marketplace: marketplace.json resolves outside the tree
      MK8 marketplace_listing -> marketplace: an entry with no source string was never looked for
      LV1 add_live_mcp -> mcp_servers: --live-mcp names a server the target does not declare, or its
          declaration cannot be read (cause: target-fault when the target does not declare it or declares
          it wrongly, since the manifest lacks what was asked for; tool-limit when its manifest or .mcp.json
          resolves outside the tree)
      LV2 add_live_mcp -> mcp_servers: the live read was refused (a remote transport, a shell, eval or
          module command, an entrypoint or argument outside the tree, an unsafe environment name: tool-limit,
          neckbeard declined to run it; a declaration with no command, args that are not a list or an env that is
          not strings, or a command or entrypoint the declaration names that is missing or
          not executable: target-fault)
      LV3 add_live_mcp -> mcp_servers: the live read failed, or one of its lists did (a hang or a byte bound: tool-limit; a malformed or wrong
          reply, an error reply, a server that exits: target-fault)
    Folders: find_files, skill_companions, hooks_outside_manifest and inventory_persistence walk the tree
    with os.walk, which skips a folder it cannot list (onerror: "<folder>: folder could not be listed", untested
    because it takes a folder that exists and cannot be opened, which a test may not chmod) and does not enter
    a symlinked folder ("<folder>: a symlinked folder, not followed", tested as SK8 below); both make the section partial.
    Not noted: settings_writers re-reads files inventory_persistence just read, so a file it cannot
    read already has a persistence note; the reader's own rules (current_rules), which are
    reader-read-status's; a marketplace entry that is external, which is a choice the manifest makes.
    A site added to any inventory*.py module without a line here, or a line without a test, sends the item back at
    review: nothing else catches it."""
    private = dossier.pop("_read_notes", None) or {}
    kind, base = dossier.get("kind"), dossier.get("path") or ""
    if kind == "rule-file":
        base = os.path.dirname(base)   # an import is named from the folder the rule file sits in
    notes = {s: list(private.get(s) or []) for s in READ_SECTIONS}

    def add(section, text, level="partial", *, cause):
        n = _Note(text)
        n.level = level
        n.cause = cause
        notes[section].append(n)

    for section in ("skills", "agents", "commands", "rule_files"):
        for entry in dossier.get(section) or []:
            if not isinstance(entry, dict):
                continue
            rel = _rel(entry.get("path") or entry.get("source") or section, base) if base else (entry.get("path") or section)
            if entry.get("refused"):
                add(section, f"{rel}: {entry['refused']}", "entry", cause="tool-limit")
            if entry.get("truncated"):
                add(section, f"{rel}: read capped at {entry.get('read_limit', READ_LIMIT)} bytes", cause="tool-limit")
            for comp in entry.get("companion_files") or []:
                if comp.get("refused") or comp.get("skipped"):
                    add(section, f"{comp.get('path')}: {comp.get('refused') or comp.get('skipped')}", cause="tool-limit")
                elif comp.get("truncated"):
                    add(section, f"{comp.get('path')}: read capped at {comp.get('read_limit', READ_LIMIT)} bytes", cause="tool-limit")
    for imp in dossier.get("imports_not_followed") or []:
        add("rule_files", f"{os.path.basename(dossier.get('path') or '')}: import @{imp} not followed (only a CLAUDE.md follows its imports)", cause="tool-limit")

    hooks = dossier.get("hooks")
    if isinstance(hooks, dict):
        hf = hooks.get("hooks_file") or "hooks"
        if hooks.get("parse_error"):
            add("hooks", f"{hf}: {hooks['parse_error']}", "failed", cause="target-fault")
        if hooks.get("refused"):
            add("hooks", f"{hf}: {hooks['refused']}", "failed", cause="tool-limit")
        for m in hooks.get("malformed_entries") or []:
            add("hooks", f"{hf}: {m}", cause="target-fault")
        for key in ("unresolved_hooks", "unidentifiable_hooks"):
            if hooks.get(key):
                add("hooks", f"{hf}: {key.split('_')[0]} hooks: " + "; ".join(hooks[key]), cause="tool-limit")
        if hooks.get("injected_content_note"):
            add("hooks", f"{hf}: {hooks['injected_content_note']}", cause="tool-limit")
        if hooks.get("marketplace_note"):
            add("hooks", f".claude-plugin/marketplace.json: {hooks['marketplace_note']}", "failed", cause="tool-limit")
        for n in hooks.get("nested_plugins") or []:
            add("hooks", f"{n}: hooks found in a plugin nested in this directory; inventory it on its own", "failed", cause="tool-limit")
        if hooks.get("search_incomplete"):
            m = re.search(r" at (.+?)/, before", hooks["search_incomplete"])
            found = hooks.get("has_hooks") in (True, "partial")
            add("hooks", f"{m.group(1) + '/' if m else hooks.get('hooks_file') or 'hooks'}: {hooks['search_incomplete']}",
                "partial" if found else "failed", cause="tool-limit")
    if dossier.get("manifest_refused"):
        add("plugin_json", dossier["manifest_refused"], "partial" if kind == "plugin" else "failed", cause="tool-limit")

    na = set()
    if kind == "rule-file":
        na = set(READ_SECTIONS) - {"rule_files"}
    else:
        if kind == "generic-pack" and not notes["plugin_json"]:
            na.add("plugin_json")
        if not (dossier.get("marketplace") or notes["marketplace"] or private.get("_marketplace_seen")):
            na.add("marketplace")
    status = {}
    for section in READ_SECTIONS:
        ns = notes[section]
        if section in na:
            state = "not-applicable"
        elif any(n.level == "failed" for n in ns):
            state = "failed"
        elif ns:
            read = sum(1 for e in dossier.get(section) or [] if isinstance(e, dict) and e.get("text") is not None)
            listed = section in ("skills", "agents", "commands", "rule_files")
            state = "failed" if listed and read == 0 and any(n.level == "entry" for n in ns) else "partial"
        else:
            state = "read"
        status[section] = {"state": state, "notes": [str(n) for n in ns], "causes": [n.cause for n in ns]}
    dossier["read_status"] = status


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
        n += max(1, len(hooks.get("injected_content") or []))
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
