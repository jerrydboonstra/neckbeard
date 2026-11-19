#!/usr/bin/env python3
"""The parts of neckbeard's inventory that read a plugin's own files: marketplace and MCP manifests, skills, commands
and agents, and the CLAUDE.md files a target ships with the files they import. Moved out of inventory.py with no
change in behaviour, one step toward every shipped file being under neckbeard's own read cap. inventory.py imports
each name from here, so `inventory.<name>` still resolves. Stdlib only.
"""
import glob
import os
import re

from inventory_core import (
    _note, _walk_error, _walk_gaps, _within, find_files, measure, note_frontmatter, read_json, read_text,
    model_invocable, rule_item, split_frontmatter,
)


def marketplace_listing(path, notes=None):
    """The plugins a marketplace manifest at the target's root lists, and where each
    one's files are. A repo whose root is a marketplace and whose one plugin lives
    in plugins/<name>/ looked, read from the root, like a pack with no hooks and no
    agents. See CHANGELOG.md 1.12.6."""
    mp = os.path.join(path, ".claude-plugin", "marketplace.json")
    mp_rel = ".claude-plugin/marketplace.json"
    if not os.path.isfile(mp):
        if os.path.lexists(mp):
            _note(notes, f"{mp_rel}: not a readable file (a dangling symlink, or a folder)", "failed", cause="target-fault")
        return None
    if not _within(mp, path):
        _note(notes, f"{mp_rel}: resolves outside the target tree; not read", "failed", cause="tool-limit")
        return {"refused": "marketplace.json resolves outside the target tree; not read",
                "plugins": []}
    data = read_json(mp)
    entries = data.get("plugins") if isinstance(data, dict) else None
    if not isinstance(entries, list):
        why = "is not valid JSON" if data is None else "has no list of plugins"
        _note(notes, f"{mp_rel}: {why}; read it by hand", "failed", cause="target-fault")
        return {"parse_error": f"marketplace.json {why}; read it by hand", "plugins": []}
    plugins = []
    for e in entries:
        if not isinstance(e, dict):
            _note(notes, f"{mp_rel}: entry {str(e)[:60]!r} is not an object; skipped", cause="target-fault")
            continue
        src = e.get("source")
        entry = {"name": e.get("name"), "source": src}
        if isinstance(src, str) and not re.match(r"^[a-z+]+://", src):
            d = os.path.normpath(os.path.join(path, src))
            if not _within(d, path):
                entry["status"] = "refused: resolves outside the target tree"
            elif os.path.realpath(d) == os.path.realpath(path):
                entry["status"] = "the root itself"
            elif os.path.isdir(d):
                entry["status"], entry["dir"] = "local", d
            else:
                entry["status"] = "missing from this repository"
        else:
            entry["status"] = "external: fetched from elsewhere, not in this repository"
        if not isinstance(src, str):
            _note(notes, f"{mp_rel}: plugin {e.get('name')!r} has no source string, so it was not looked for", cause="target-fault")
        if entry["status"].startswith(("refused", "missing")):
            _note(notes, f"{mp_rel}: plugin {e.get('name')!r} ({src}): {entry['status']}", cause="tool-limit" if entry["status"].startswith("refused") else "target-fault")
        plugins.append(entry)
    return {"name": data.get("name"), "plugins": plugins}


def mcp_servers(plugin_json, plugin_root=None, notes=None):
    """MCP servers a plugin bundles. Reported because an MCP server is a live
    tool surface with network reach and real side effects, which makes it the
    single highest-consequence thing a plugin can ship.

    This tool inspects the declaration only. What the server actually exposes
    is knowable only by speaking MCP to it, which is out of scope here."""
    servers = plugin_json.get("mcpServers") or plugin_json.get("mcp_servers") or {}
    source = "plugin.json"
    ambiguity = None
    if servers and not isinstance(servers, dict):
        if isinstance(servers, str):
            _note(notes, f"plugin.json: mcpServers given as a path ({servers}), not followed", "failed", cause="tool-limit")
        else:
            _note(notes, f"plugin.json: mcpServers is a {type(servers).__name__}, expected an object", "failed", cause="target-fault")

    # A plugin may instead ship .mcp.json at its root, which Claude Code loads.
    # Reading only the inline manifest key misses this path entirely --
    # including Anthropic's own example-plugin, which ships exactly this
    # shape. See CASE-STUDIES.md, round 9.
    if not servers and plugin_root:
        dot = os.path.join(plugin_root, ".mcp.json")
        if os.path.lexists(dot) and not _within(dot, plugin_root):
            _note(notes, ".mcp.json: resolves outside the target tree; not read", "failed", cause="tool-limit")
            return {"source": ".mcp.json", "servers": None,
                    "refused": ".mcp.json resolves outside the target tree; not read"}
        raw = read_json(dot)
        if os.path.lexists(dot):
            if raw is None:
                _note(notes, ".mcp.json: not valid JSON; read it by hand", "failed", cause="target-fault")
            elif not isinstance(raw, dict):
                _note(notes, f".mcp.json: is a {type(raw).__name__}, expected an object", "failed", cause="target-fault")
            elif "mcpServers" in raw and not isinstance(raw["mcpServers"], dict):
                _note(notes, f".mcp.json: mcpServers is a {type(raw['mcpServers']).__name__}, "
                             "expected an object", "failed", cause="target-fault")
        if isinstance(raw, dict) and raw:
            source = ".mcp.json"
            if isinstance(raw.get("mcpServers"), dict):
                servers = raw["mcpServers"]
            else:
                # Anthropic's own example-plugin puts servers at the top level
                # while the docs describe the wrapped form. First-party code and
                # documentation disagree, so report both readings rather than
                # silently picking one.
                servers = raw
                ambiguity = ("servers found at the top level of .mcp.json, not under "
                             "an 'mcpServers' key. First-party examples use this shape "
                             "and the docs describe the wrapped one; treat the list as "
                             "best-effort and open the file")
                if "mcpServers" not in raw:   # a wrong-typed mcpServers is noted above, and is not a top-level shape
                    _note(notes, f".mcp.json: {ambiguity}", cause="tool-limit")
    if not isinstance(servers, dict) or not servers:
        return None
    out = []
    for name, cfg in servers.items():
        if not isinstance(cfg, dict):
            _note(notes, f"{source}: server {name!r} is not an object, so its command and url were not read", cause="target-fault")
        cfg = cfg if isinstance(cfg, dict) else {}
        out.append({
            "name": name,
            "command": cfg.get("command"),
            "args": cfg.get("args"),
            "url": cfg.get("url"),
            "transport": "remote" if cfg.get("url") else "local-process",
        })
    block = {
        "count": len(out),
        "source": source,
        "servers": out,
        "note": ("this reports the declaration, not the tool surface. A local-process "
                 "server runs on your machine; what it exposes needs a live MCP call."),
    }
    if ambiguity:
        block["ambiguity"] = ambiguity
    return block


def contained_skill(sm, root, notes=None):
    """One SKILL.md from the target, or a refusal if it resolves outside it.

    Both skill paths (a plugin's and a plain pack's) go through here, so
    containment is checked the same way for each. See CASE-STUDIES.md,
    round 14."""
    if not _within(sm, root):
        return {"source": os.path.relpath(sm, root), "path": sm,
                "name": os.path.basename(os.path.dirname(sm)),
                "description": None, "bytes": None, "text": None,
                "refused": "resolves outside the target tree; not read"}
    item = rule_item(os.path.relpath(sm, root), sm)
    if item is None:
        _note(notes, f"{os.path.relpath(sm, root)}: could not be read", "entry",
              cause="target-fault" if not os.path.isfile(sm) else "tool-limit")   # a dangling link is the plugin's, a file that will not open is ours
    if item:
        fm, _ = split_frontmatter(item["text"])
        # Claude Code treats a skill as user-invocable unless its frontmatter says false.
        item["user_invocable"] = str((fm or {}).get("user-invocable", "true")).strip().lower() != "false"
        # Claude Code leaves the description of a skill that sets disable-model-invocation: true out of every session.
        item["model_invocable"] = model_invocable(fm)
        item["companion_files"] = skill_companions(sm, root, notes)
        item = note_frontmatter(item)
    return item


COMPANION_LIMIT = 40


def skill_companions(sm, root, notes=None):
    """The other Markdown files in a skill's folder (roles/, sections/, references). A
    SKILL.md often only points at them, so a judge that sees SKILL.md alone has to open
    them by hand, and two runs then read different text. Contained and capped; a file
    past the cap is listed by name with no text, so the dossier says what it left out."""
    base = os.path.dirname(sm)
    paths = []
    # os.walk does not follow directory symlinks, so a skill folder that links to itself
    # cannot loop (a recursive glob does follow them, and ran until killed). It prunes the
    # same directories find_files does, so vendored READMEs do not crowd out the real files.
    for dirpath, dirnames, filenames in os.walk(base, onerror=_walk_error(notes, root)):
        if dirpath[len(base):].count(os.sep) >= 6:
            if dirnames:
                _note(notes, f"{os.path.relpath(dirpath, root)}: companion files below this folder not read, "
                             "deeper than 6 folders", cause="tool-limit")
            dirnames[:] = []
        dirnames[:] = sorted(d for d in dirnames if d not in (".git", "node_modules", "__pycache__", "vendor"))
        _walk_gaps(notes, dirpath, dirnames, root)
        paths += [os.path.join(dirpath, fn) for fn in sorted(filenames)
                  if fn.endswith(".md") and os.path.abspath(os.path.join(dirpath, fn)) != os.path.abspath(sm)]
    out = []
    for i, p in enumerate(paths):
        rel = os.path.relpath(p, root)
        if not _within(p, root):
            out.append({"path": rel, "text": None, "refused": "resolves outside the target tree; not read"})
        elif i >= COMPANION_LIMIT:
            out.append({"path": rel, "text": None, "skipped": f"more than {COMPANION_LIMIT} companion files"})
        else:
            text = read_text(p)
            if text is None:
                _note(notes, f"{rel}: companion file could not be read",
                      cause="target-fault" if not os.path.isfile(p) else "tool-limit")
            out.append({"path": rel, "text": text, **(measure(p, text) if text is not None else {})})
    return out


def inventory_skills(root, notes=None):
    """Broad, recursive search — for a generic pack with no canonical layout."""
    return [it for it in (contained_skill(sm, root, notes)
                          for sm in find_files(root, {"SKILL.md"}, notes=notes)) if it]


def plugin_skills(root, notes=None):
    """A Claude Code plugin's own skills are unambiguously root/skills/*/SKILL.md
    (the standard plugin paths). A non-recursive glob here,
    rather than inventory_skills' repo-wide walk, deliberately excludes bundled
    mirrors for other agent ecosystems a multi-platform plugin may ship
    (.openclaw/skills/, .opencode/command/, .cursor/rules/, etc.) — those are
    invisible to Claude Code and would otherwise double-count and inflate the
    target's apparent size."""
    return [it for it in (contained_skill(sm, root, notes)
                          for sm in sorted(glob.glob(os.path.join(glob.escape(root), "skills", "*", "SKILL.md"))))
            if it]


def inventory_commands_agents(root, notes=None):
    """Slash commands and agent definitions, read in full like skills.

    Both are instructions to a model, so the classification step needs their
    text, not just their names -- a git-URL target's temp clone is gone by the
    time anyone reads the dossier. See CASE-STUDIES.md, round 14."""
    # `notes` here is a dict of section -> list (the target's _read_notes), since the two sections
    # are read by one call: notes["commands"] and notes["agents"].
    def read(paths, source):
        out = []
        section = notes[source + "s"] if notes is not None else None
        for p in sorted(paths):
            if not os.path.isfile(p):
                _note(section, f"{os.path.relpath(p, root)}: not a readable file (a dangling symlink, or a folder)", "entry", cause="target-fault")
                continue
            if not _within(p, root):
                out.append({"source": source, "path": os.path.relpath(p, root),
                            "name": os.path.basename(p), "text": None,
                            "refused": "resolves outside the target tree; not read"})
                continue
            it = rule_item(source, p)
            if it:
                note_frontmatter(it)
                it["path"] = os.path.relpath(p, root)
                out.append(it)
            else:
                _note(section, f"{os.path.relpath(p, root)}: not a readable file (a dangling symlink, or a folder)", "entry", cause="target-fault")
        return out
    commands = read([p for pat in ("*.md", "*.toml")
                     for p in glob.glob(os.path.join(glob.escape(root), "commands", pat))], "command")
    agents = read(glob.glob(os.path.join(glob.escape(root), "agents", "*.md")), "agent")
    return commands, agents


# ------------------------------------------------------------------ CLAUDE.md imports
# Claude Code lets a CLAUDE.md pull in other files with `@path`: relative to the
# importing file, `~` allowed, up to five hops, never inside code. A global
# CLAUDE.md that is only `@~/.claude/roles/me.md` is the documented way to
# split rules, and reading only that one line compares every target against a
# near-empty corpus while reporting success. See CASE-STUDIES.md, round 14.
IMPORT_MAX_HOPS = 5
_CODE_RE = re.compile(r"```.*?```|~~~.*?~~~|`[^`\n]*`", re.S)
_IMPORT_RE = re.compile(r"(?:^|(?<=\s))@(\S+)")


def claude_md_imports(path, root=None, _hop=1, _seen=None, notes=None):
    """Files `path` imports, depth first, in the order Claude Code would read
    them. Each is (resolved_path, imported_from, refused). With `root`, an import
    that resolves outside it is refused rather than read: a target's CLAUDE.md
    is untrusted, and `@../../anything` is a read like any other."""
    seen = _seen if _seen is not None else {os.path.realpath(path)}
    text = _CODE_RE.sub(" ", read_text(path) or "")
    out = []
    for m in _IMPORT_RE.finditer(text):
        ref = m.group(1).rstrip(".,;:)]}\"'")
        cand = os.path.expanduser(ref)
        if not os.path.isabs(cand):
            cand = os.path.join(os.path.dirname(path), cand)
        cand = os.path.normpath(cand)
        if not os.path.isfile(cand):
            if os.path.lexists(cand):
                # a dangling symlink is a file that exists and cannot be read, not "@someone" in prose
                _note(notes, f"{os.path.relpath(cand, root or os.path.dirname(path))}: import is not a readable "
                             "file (a dangling symlink, or a folder)", "entry", cause="target-fault")
            continue  # "@someone" in prose, or a dead import: Claude Code skips it too
        real = os.path.realpath(cand)
        if real in seen:
            continue
        seen.add(real)
        if root is not None and not _within(cand, root):
            out.append((cand, path, True))
            continue
        out.append((cand, path, False))
        if _hop < IMPORT_MAX_HOPS:
            out.extend(claude_md_imports(cand, root, _hop + 1, seen, notes))
        elif notes is not None and claude_md_imports(cand, root, _hop + 1, set(seen)):
            _note(notes, f"{os.path.relpath(cand, root or os.path.dirname(path))}: its imports are not "
                         f"followed past {IMPORT_MAX_HOPS} hops", cause="tool-limit")
    return out


def with_imports(source, path, root=None, notes=None):
    """rule_item for a CLAUDE.md plus one item per file it imports."""
    items = []
    it = rule_item(source, path)
    if it:
        items.append(it)
    else:
        _note(notes, f"{os.path.relpath(path, root or os.path.dirname(path))}: could not be read", "entry",
              cause="target-fault" if not os.path.isfile(path) else "tool-limit")
    for p, parent, refused in claude_md_imports(path, root, notes=notes):
        if refused:
            items.append({"source": f"{source} import", "path": p, "imported_from": parent,
                          "text": None, "refused": "import resolves outside the target tree; not read"})
            continue
        imp = rule_item(f"{source} import", p)
        if imp:
            imp["imported_from"] = parent
            items.append(imp)
        else:
            _note(notes, f"{os.path.relpath(p, root or os.path.dirname(path))}: import could not be read", "entry",
                  cause="target-fault" if not os.path.isfile(p) else "tool-limit")
    return items


def target_rule_files(root, notes=None):
    """A CLAUDE.md at the target's root is a rule file the target carries.
    Without this, a CLAUDE.md-only rule pack produces an empty dossier and
    skips the reader's rules as having nothing to compare. See
    CASE-STUDIES.md, round 14."""
    p = os.path.join(root, "CLAUDE.md")
    if not os.path.isfile(p):
        if os.path.lexists(p):
            _note(notes, "CLAUDE.md: not a readable file (a dangling symlink, or a folder)", "entry", cause="target-fault")
        return []
    if not _within(p, root):
        return [{"source": "target-CLAUDE.md", "path": "CLAUDE.md", "text": None,
                 "refused": "resolves outside the target tree; not read"}]
    return with_imports("target-CLAUDE.md", p, root=root, notes=notes)
