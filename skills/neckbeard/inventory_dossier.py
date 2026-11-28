#!/usr/bin/env python3
"""The dossier part of neckbeard's inventory: inventory_target reads a target's skills, commands, agents, rule files,
hooks, MCP servers, persistence candidates and manifests into one dictionary, and add_read_status says which sections
were read in full. Moved out of inventory.py with no change in behaviour, so no shipped file is over neckbeard's own
read cap. inventory.py imports each name from here, so `inventory.<name>` still resolves. It imports only from
inventory_core, inventory_hooks and inventory_parts, never from inventory.py. Stdlib only.
"""
import json
import os
import re
import sys
import inventory_core   # _SKIP_DIRS is set through the module, so the walkers see it
from inventory_core import (
    READ_LIMIT, _Note, _note, _rel, _within, read_json, read_text, rule_item,
)
from inventory_hooks import (
    inventory_hooks, persistence_keys,
)
from inventory_parts import (
    _CODE_RE, _IMPORT_RE, inventory_commands_agents, inventory_skills, marketplace_listing, mcp_servers,
    plugin_skills, target_rule_files, with_imports,
)


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
            **persistence_keys(path, notes["persistence_candidates"]),
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
        **persistence_keys(path, notes["persistence_candidates"]),
        "rule_files": target_rule_files(path, notes["rule_files"]),
        **dict(zip(("commands", "agents"), inventory_commands_agents(path, notes))),
        **({"manifest_refused": manifest_refused} if manifest_refused else {}),
        "_read_notes": notes,
    }


# ------------------------------------------------------------------ declared fixtures
def read_declared_fixtures(root):
    """The fixture folders a target declares in .neckbeard.json at its root ({"fixtures": ["tools/fixtures"]}).
    None when there is no such file; else (folders, ignored): the entries that name a folder under the root, and the
    entries left out (not a string, absolute, containing "..", or no folder inside the root). A file that does not
    parse, or has no "fixtures" list, declares nothing (the hooks search notes an invalid file itself)."""
    fp = os.path.join(root, ".neckbeard.json")
    if not os.path.lexists(fp):
        return None
    data = read_json(fp) if _within(fp, root) else None
    items = data.get("fixtures") if isinstance(data, dict) else None
    if not isinstance(items, list):
        return [], []
    folders, ignored = [], []
    for e in items:
        ok = isinstance(e, str) and e.strip() and not os.path.isabs(e) and ".." not in e.replace("\\", "/").split("/")
        if ok:
            d = os.path.join(root, e)
            ok = os.path.isdir(d) and _within(d, root) and os.path.normpath(e) != "."   # "." would declare the whole tree
        if ok:
            e = os.path.normpath(e)
            if e not in folders:
                folders.append(e)
        else:
            ignored.append(e)
    return folders, ignored


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
      HK16 read_mods -> hooks: a mod a hooks file lists exists; it runs with no sandbox and its source is not read (tool-limit)
      HK17 read_mods -> hooks: a mod path that resolves outside the tree is refused and not opened (tool-limit)
      HK18 read_mods -> hooks: a mod file that is not found (target-fault)
      HK19 read_mods -> hooks: "modules" is not a list of strings, so no mods are recorded from it (target-fault)
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
      PS4 inventory_persistence -> persistence_candidates: a script is read in full up to 2000000 characters
      PS5 inventory_persistence -> persistence_candidates: a write past byte 100000 of a script is found
      PS6 inventory_persistence -> persistence_candidates: 2000000-character hostile one-line files scan in under 10 seconds of CPU
      PS7 inventory_persistence -> persistence_candidates: a cp whose ~/ destination is on the next line (backslash continuation) is found
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
      DF1 add_read_status -> hooks: a .neckbeard.json fixtures entry that is not a string, is absolute or
          contains "..", or names no folder inside the target is left out of declared_fixtures
    Declared fixtures: a target may list fixture folders in .neckbeard.json at its root (the outer root when a
    marketplace selects a nested plugin). hooks_outside_manifest and inventory_persistence still walk them and report
    what they find; only the read-failure notes their own walk adds for a path inside one (marked from_scan: a
    file note, a folder that could not be listed, a symlinked folder) are kept under read_status[section]["declared"]
    instead of counting toward the state, in those two sections. A note is inside a declared folder when its text starts with that folder's path and a separator;
    its path is relative to the target, kept as the walk wrote it, relative to the target. Notes _parse_events adds, and every note from a path the manifest, a hooks
    config or a settings file points to, are counted as always. The dossier key declared_fixtures (the valid
    folders) exists only when .neckbeard.json does.
    Folders: find_files, skill_companions, hooks_outside_manifest and inventory_persistence walk the tree
    with os.walk, which skips a folder it cannot list (onerror: "<folder>: folder could not be listed", untested
    because it takes a folder that exists and cannot be opened, which a test may not chmod) and does not enter
    a symlinked folder ("<folder>: a symlinked folder, not followed", tested as SK8 below); both make the section partial.
    Not noted: settings_writers re-reads files the persistence walk just read, so a file it cannot
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

    moved = {}
    if kind != "rule-file" and base:
        outer = (dossier.get("marketplace") or {}).get("root") if isinstance(dossier.get("marketplace"), dict) else None
        outer = outer or base
        decl = read_declared_fixtures(outer)
        if decl is not None:
            folders, ignored = decl
            dossier["declared_fixtures"] = folders
            for e in ignored:
                add("hooks", f"{e}: not a folder under the target, ignored", cause="target-fault")
            # a note is "<path>: <reason>", its path from the walk's own root (base): it is inside a declared folder when it
            # starts with that folder's path and a separator, so a file whose name holds ": " cannot pass for one
            roots = [os.path.relpath(os.path.normpath(os.path.join(outer, f)), base) + os.sep for f in folders]
            for section in ("hooks", "persistence_candidates"):
                keep = []
                for n in notes[section]:
                    if n.from_scan and any(str(n).startswith(r) for r in roots):
                        moved.setdefault(section, []).append(str(n))
                    else:
                        keep.append(n)
                notes[section] = keep

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
        status[section] = {"state": state, "notes": [str(n) for n in ns], "causes": [n.cause for n in ns],
                           **({"declared": moved[section]} if moved.get(section) else {})}
    dossier["read_status"] = status
