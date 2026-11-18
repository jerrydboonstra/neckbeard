#!/usr/bin/env python3
"""Claude Code mods in a plugin's hooks files, for the hooks reader in inventory_hooks.py. A mod is a JavaScript or TypeScript file
a plugin lists under "modules" in a hooks file; it runs inside the session with the user's permissions, unsandboxed. This module only
lists them (never reads their source) and keeps "modules" from being taken for an event name. Stdlib only."""
import os

from inventory_core import _note, _within


def events_of(hooks_json):
    """The object of events in a parsed hooks file, or None when it is not one. Claude Code nests events under "hooks"; some
    plugins write them at the top level, where a "modules" key lists mods (see read_mods) and is never an event name."""
    if not isinstance(hooks_json, dict):
        return None
    if "hooks" in hooks_json:
        return hooks_json["hooks"]
    return {k: v for k, v in hooks_json.items() if k != "modules"}


def read_mods(hooks_json, base_dir, plugin_root, label, notes):
    """The Claude Code mods a hooks file lists under "modules", or None when it has no such key. A mod is a JavaScript or
    TypeScript file that runs inside the session with the user's permissions, unsandboxed; its source is not read here, so every
    mod that exists makes the hooks section partly read. Each path is relative to the hooks file's own folder (BASE_DIR; the
    plugin root for an inline object in plugin.json), as the mods reference says. One entry per mod:
    {"path": <relative to the plugin root>, "exists": bool, "refused": bool}. A path outside the tree is refused and never opened;
    a "modules" value that is not a list of strings records no mods from it."""
    if not isinstance(hooks_json, dict) or "modules" not in hooks_json:
        return None
    listed = hooks_json["modules"]
    if not isinstance(listed, list) or not all(isinstance(m, str) for m in listed):
        _note(notes, f"{label}: \"modules\" is not a list of strings; no mods recorded from it", cause="target-fault")
        return []
    mods = []
    for m in listed:
        path = os.path.normpath(os.path.join(base_dir, m))   # an absolute m drops the base, and _within then refuses it
        rel = os.path.relpath(path, plugin_root)
        if not _within(path, plugin_root):
            mods.append({"path": rel, "exists": False, "refused": True})
            _note(notes, f"{rel}: mod path resolves outside the target tree; not opened", cause="tool-limit")
        elif not os.path.isfile(path):
            mods.append({"path": rel, "exists": False, "refused": False})
            _note(notes, f"{rel}: mod file not found", cause="target-fault")
        else:
            mods.append({"path": rel, "exists": True, "refused": False})
            _note(notes, f"{rel}: a Claude Code mod; it runs unsandboxed in the session and its source is not read", cause="tool-limit")
    return mods
