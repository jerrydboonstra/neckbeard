#!/usr/bin/env python3
"""Mechanical half of neckbeard: read a target and the user's current rules,
emit one JSON dossier. Makes no judgment calls — that's the SKILL.md's job.

Usage:
  inventory.py <target> [--project-dir DIR] [--extra-rules PATH ...] [--out FILE]

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

HOME = os.path.expanduser("~")
CLAUDE_HOME = os.environ.get("CLAUDE_CONFIG_DIR", os.path.join(HOME, ".claude"))

# Where Claude Code reads file-based managed (enterprise) settings, per platform.
# A module-level list so selfcheck.py can point it at a fixture.
MANAGED_SETTINGS = {
    "darwin": ["/Library/Application Support/ClaudeCode/managed-settings.json"],
    "win32": [r"C:\Program Files\ClaudeCode\managed-settings.json"],
}.get(sys.platform, ["/etc/claude-code/managed-settings.json"])

# Events whose hooks fire on the subagent lifecycle itself.
SUBAGENT_EVENTS = {"SubagentStart", "SubagentStop"}

# Claude Code's hooks documentation states that plugin hooks "also run inside
# subagents", and names PreToolUse and PostToolUse explicitly: when a subagent
# calls a tool, those fire exactly as in the main conversation. So a plugin
# hooking them reaches every subagent, even with no Subagent* event registered.
# Reported separately from the certain set below, because the general sentence
# implies others (Stop, PermissionRequest) without documenting them one by one,
# and guessing a confident list is the failure this tool exists to prevent.
SUBAGENT_TOOL_EVENTS = {"PreToolUse", "PostToolUse"}
SUBAGENT_TOOL_EVENTS_LIKELY = {"PostToolUseFailure", "Stop", "PermissionRequest"}
# Widened 2026-09-19. The previous set matched writeFileSync and little else,
# and missed five constructed writes including two into $HOME: shell append
# redirection, cp into a home cache, pathlib write_text, appendFileSync and
# createWriteStream. The published claim that this heuristic "fails toward
# false positives" had never been tested against a write it should catch.
PERSIST_PATTERNS = [
    # node/js
    re.compile(r"\b(writeFileSync|appendFileSync|createWriteStream|copyFileSync|mkdirSync|rmSync)\b"),
    re.compile(r"fs\.(write|append|copy|rename|unlink|rm|mkdir)\w*\("),
    # python
    re.compile(r"\bopen\([^)]*['\"][wax]"),
    re.compile(r"\.(write_text|write_bytes|mkdir|touch|unlink|rename|replace)\("),
    re.compile(r"\b(shutil\.(copy|move|rmtree)|os\.(remove|rename|makedirs|mkdir))\b"),
    # shell
    re.compile(r">>?\s*[\"']?(\$HOME|~|/)"),
    re.compile(r"\b(cp|mv|rm|mkdir|touch|tee|install)\b[^\n|]*\$HOME"),
    re.compile(r"\b(cp|mv|tee)\b\s+-?\w*\s*[\"']?[^\n]*[\"']?\s+[\"']?(\$HOME|~)/"),
    # anywhere: names a home-ish destination
    re.compile(r"os\.homedir\(\)|homedir\(\)|expanduser\(|Path\.home\(\)|process\.env\.HOME"),
    re.compile(r"[\"'/]\.(config|cache|local|claude)[\"'/]"),
]

# Extensions alone missed superpowers' own hook, which is the extension-less
# file `hooks/session-start`. Scan anything small and text-shaped instead.
SCRIPT_EXTS = (".js", ".py", ".sh", ".mjs", ".cjs", ".ts", ".bash", ".zsh", ".rb", ".pl")


# ------------------------------------------------------------------ helpers
def read_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


READ_LIMIT = 200_000


def read_text(path, limit=READ_LIMIT):
    try:
        with open(path, "r", errors="replace") as f:
            return f.read(limit)
    except Exception:
        return None


def measure(path, text):
    """Real size on disk, characters read, and whether the read was cut short.

    `bytes` used to be len() of a decoded string, which is a character count
    wearing the wrong unit: 10,000 em dashes reported 10,000 against 30,000 on
    disk. It was also silently capped at the read limit, so a one-megabyte
    skill reported exactly 200,000 with nothing saying so. A plugin that wants
    to look small only has to be large. Both found 2026-09-19."""
    try:
        size = os.path.getsize(path)
    except OSError:
        size = None
    chars = len(text or "")
    out = {"bytes": size, "chars": chars}
    if size is not None and chars >= READ_LIMIT and size > READ_LIMIT:
        out["truncated"] = True
        out["read_limit"] = READ_LIMIT
    return out


def split_frontmatter(text):
    """Return (frontmatter_dict_or_None, body_text) for a '---\\n...\\n---' header.
    Minimal YAML: only flat 'key: value' and 'key: >-' folded blocks are parsed;
    good enough for name/description, which is all current_items needs."""
    if not text or not text.startswith("---"):
        return None, text or ""
    # Split on lines that are exactly a fence, not on the first "---" anywhere.
    # "description: uses a --- separator" used to truncate the description at
    # "uses a" and misparse the body with it (found 2026-09-19).
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return None, text
    close = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if close is None:
        return None, text
    fm_raw, body = "".join(lines[1:close]), "".join(lines[close + 1:])
    fm = {}
    key, buf = None, []
    for line in fm_raw.splitlines():
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m and (not line.startswith(" ")):
            if key:
                fm[key] = " ".join(buf).strip()
            key, val = m.group(1), m.group(2).strip()
            if val in (">-", ">", "|", "|-", ""):
                buf = []
            else:
                fm[key] = val.strip('"').strip("'")
                key = None
        elif key:
            buf.append(line.strip())
    if key:
        fm[key] = " ".join(buf).strip()
    return fm, body.strip()


def find_up(start, filename):
    """Walk up from start looking for filename; stop at $HOME or filesystem root."""
    d = os.path.abspath(start)
    while True:
        cand = os.path.join(d, filename)
        if os.path.isfile(cand):
            return cand
        if d in (HOME, os.path.dirname(d)):
            break
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return None


def find_project_root(start):
    """Nearest ancestor with a .git dir; falls back to start itself."""
    d = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(d, ".git")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return os.path.abspath(start)
        d = parent


def _name_from_path(path):
    """A skill with no frontmatter still has an identity: its directory.
    skills/<name>/SKILL.md is named <name>, not "SKILL". Found 2026-09-19,
    where every frontmatter-less skill reported the same useless name."""
    base = os.path.basename(path)
    if base.upper().startswith("SKILL."):
        parent = os.path.basename(os.path.dirname(path))
        if parent:
            return parent
    return os.path.splitext(base)[0]


def _within(path, root):
    """True when path really sits under root, following symlinks. The target is
    untrusted by definition, so a skills/x/SKILL.md symlinked to /etc/passwd
    must not be read and embedded in a dossier. This guard existed on the
    injection resolver only until 2026-09-19."""
    try:
        rp = os.path.realpath(path)
        rr = os.path.realpath(root)
        return rp == rr or rp.startswith(rr + os.sep)
    except Exception:
        return False


def rule_item(source, path):
    text = read_text(path)
    if text is None:
        return None
    fm, body = split_frontmatter(text)
    item = {
        "source": source,
        "path": path,
        "name": (fm or {}).get("name") or _name_from_path(path),
        "description": (fm or {}).get("description"),
        "text": text,
    }
    item.update(measure(path, text))
    return item


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
    # and the cache can go stale silently (confirmed on this plugin itself,
    # 2026-09-19 — a fixed description sat uncorrected in the cache until an
    # uninstall/reinstall, because the version number never changed). Verify
    # a found installPath actually has the manifest before trusting it, and
    # fall back to the marketplace's own listing when it does not.
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
    # Testing the .git suffix first sent ./repo.git to git clone and crashed
    # with an uncaught CalledProcessError (found 2026-09-19).
    if os.path.isdir(os.path.expanduser(target)):
        path = os.path.realpath(os.path.expanduser(target))
        return path, "local-path"
    # A single rule file (someone's CLAUDE.md, a pasted rules.md). The skill has
    # always said it vets one; until 2026-09-24 this exited "not a directory".
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
def find_files(root, names, max_depth=6):
    out = []
    root = root.rstrip("/")
    base_depth = root.count(os.sep)
    for dirpath, dirnames, filenames in os.walk(root):
        if dirpath.count(os.sep) - base_depth > max_depth:
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", "__pycache__", "vendor")]
        for fn in filenames:
            if fn in names:
                out.append(os.path.join(dirpath, fn))
    return out


JS_REQUIRE_RE = re.compile(r"""require\(\s*['"](\.[^'"]+)['"]\s*\)""")
PATH_JOIN_RE = re.compile(r"""path\.join\(\s*([^)]+?)\s*\)""")


def _literal_path_candidates(src):
    """Ordered most-trustworthy first. A path.join(...) reconstruction is
    evidence the file is actually being built as a path; a bare quoted string
    is not. Returning bare literals first, then taking the first that exists on
    disk, made the resolver confidently name an unrelated CHANGELOG.md quoted
    two lines above the real payload, with no note telling the reader to doubt
    it (found 2026-09-19). Returns (candidate, confident) pairs."""
    """Single-literal paths ('../skills/x/SKILL.md') and path.join(...) calls
    whose arguments are all string literals or __dirname/__filename (ponytail's
    actual pattern: path.join(__dirname, '..', 'skills', 'ponytail', 'SKILL.md')),
    reconstructed as a plain relative path."""
    joined, bare = [], list(re.findall(r"""['"]([\w./-]+\.(?:md|txt))['"]""", src))
    out = []
    for args_raw in PATH_JOIN_RE.findall(src):
        parts, ok = [], True
        for arg in [a.strip() for a in args_raw.split(",")]:
            if arg in ("__dirname", "__filename"):
                continue  # treated as "start here", handled by the caller's base dirs
            m = re.match(r"""^['"]([^'"]*)['"]$""", arg)
            if m:
                parts.append(m.group(1))
            else:
                ok = False
                break
        if ok and parts:
            joined.append("/".join(parts))
    # confident: reconstructed from a real path expression.
    out = [(c, True) for c in joined]
    # not confident: a bare quoted filename, which may be anything.
    out += [(c, False) for c in bare if c not in joined]
    return out


def resolve_injected_text(hook_file_path, plugin_root, depth=1):
    """Best-effort: a hook script that reads a fixed SKILL.md-shaped file and
    injects it wholesale (ponytail's pattern: SessionStart hook requires a
    sibling module, which builds the path via path.join(__dirname, ..., 'SKILL.md'))
    names that file's path in its own source or one local require() away. Follows
    one hop of local requires, reconstructs literal + path.join(...) candidates,
    and resolves each against the hook's own directory and the plugin root.
    Anything genuinely dynamic (computed from runtime state) is reported as such."""
    src = read_text(hook_file_path, limit=20_000) or ""
    candidates = _literal_path_candidates(src)
    fallback = None
    for c, confident in candidates:
        for base in (os.path.dirname(hook_file_path), plugin_root):
            p = os.path.normpath(os.path.join(base, c))
            if os.path.isfile(p) and _within(p, plugin_root):
                text = read_text(p)
                if not text:
                    continue
                hit = {"resolved_file": os.path.relpath(p, plugin_root)}
                hit.update(measure(p, text))
                if confident:
                    return hit
                # A bare literal is a guess. Hold it, keep looking for a
                # reconstructed path, and label it if nothing better turns up.
                if fallback is None:
                    hit["confidence"] = "low"
                    hit["why"] = ("matched a bare quoted filename in the hook source, not a "
                                  "reconstructed path expression; verify by reading the hook")
                    fallback = hit
    if depth > 0:
        for rel in JS_REQUIRE_RE.findall(src):
            for cand in (rel, rel + ".js", rel + ".mjs", rel + ".cjs"):
                required = os.path.normpath(os.path.join(os.path.dirname(hook_file_path), cand))
                if os.path.isfile(required):
                    found = resolve_injected_text(required, plugin_root, depth=depth - 1)
                    if found:
                        return found
                    break
    return fallback


def _identify_hook_script(cmd, plugin_root):
    """The file a hook command actually runs, or None if it cannot be worked out.

    Deliberately not gated on an extension list or on quoting. Takes every
    whitespace-separated token, strips quotes, expands the plugin-root
    variable, and returns the first that exists as a file inside the tree.
    Anything else is unidentifiable, which is a reportable state, not silence."""
    for tok in cmd.split():
        t = tok.strip("\"'")
        if not t or t.startswith("-"):
            continue
        for var in ("${CLAUDE_PLUGIN_ROOT}", "$CLAUDE_PLUGIN_ROOT"):
            t = t.replace(var, plugin_root)
        cands = [t] if os.path.isabs(t) else [
            os.path.join(plugin_root, t),
            os.path.join(plugin_root, "hooks", os.path.basename(t)),
        ]
        for c in cands:
            c = os.path.normpath(c)
            if os.path.isfile(c) and _within(c, plugin_root):
                return c
    return None


def inventory_hooks(plugin_root, plugin_json):
    hooks_ref = plugin_json.get("hooks")
    hooks_path = None
    # plugin.json may carry its hooks inline as an object rather than naming a
    # file. That shape went straight into os.path.join and killed the run with a
    # TypeError and no dossier at all (found 2026-09-24 by a falsify pass).
    if isinstance(hooks_ref, dict) and hooks_ref:
        rel, hooks_json = "plugin.json (inline hooks)", hooks_ref
    elif hooks_ref and not isinstance(hooks_ref, (str, dict)):
        return {"has_hooks": "unknown", "hooks_file": "plugin.json", "events": {},
                "hook_scripts": None, "hook_registrations": None,
                "hooks_reach_subagents": None,
                "parse_error": f"plugin.json's \"hooks\" is a {type(hooks_ref).__name__}, "
                               "neither a path nor an object of events; read it by hand"}
    else:
        if hooks_ref:
            hooks_path = os.path.normpath(os.path.join(plugin_root, hooks_ref))
        else:
            default = os.path.join(plugin_root, "hooks", "hooks.json")
            if os.path.isfile(default):
                hooks_path = default
        if not hooks_path or not os.path.isfile(hooks_path):
            return {"has_hooks": False}
        rel = os.path.relpath(hooks_path, plugin_root)
        # plugin.json names this path and plugin.json is untrusted: "../../x.json"
        # or a symlinked hooks/ read a file from anywhere, no symlink privileges
        # needed for the first. Unguarded until 2026-09-24.
        if not _within(hooks_path, plugin_root):
            return {"has_hooks": "unknown", "hooks_file": rel, "events": {},
                    "hook_scripts": None, "hook_registrations": None,
                    "hooks_reach_subagents": None,
                    "refused": "hooks file resolves outside the target tree; not read"}
        hooks_json = read_json(hooks_path)

    # A hooks file that exists but cannot be read is NOT "no hooks", and it is
    # not "hooks with no events" either. Both readings are false and the second
    # is the one this used to report: has_hooks true, events empty. Say what is
    # actually known, which is that there is a hooks file and it did not parse.
    # Found 2026-09-19 with a deliberately corrupt hooks.json.
    if hooks_json is None:
        return {"has_hooks": "unknown", "hooks_file": rel, "events": {},
                "hook_scripts": None, "hook_registrations": None,
                "hooks_reach_subagents": None,
                "parse_error": "hooks file exists but is not valid JSON; read it by hand"}

    # Claude Code nests events under a "hooks" key; some plugins write them at
    # the top level. Anything else (a list, a string, a number) is neither, and
    # crashed on .get() until 2026-09-19.
    events = hooks_json.get("hooks", hooks_json) if isinstance(hooks_json, dict) else None
    if not isinstance(events, dict):
        # Name the value that is actually wrong. Reporting type(hooks_json)
        # produced "parsed as dict, not an object of events" for {"hooks": []},
        # which contradicts itself.
        inner = hooks_json.get("hooks") if isinstance(hooks_json, dict) else hooks_json
        return {"has_hooks": "unknown", "hooks_file": rel, "events": {},
                "hook_scripts": None, "hook_registrations": None,
                "hooks_reach_subagents": None,
                "parse_error": f"events container is {type(inner).__name__}, "
                               "expected an object of event names; read it by hand"}

    result = {"has_hooks": True, "hooks_file": rel, "events": {}}
    reaches_subagents = False
    reaches_subagents_likely = False
    injected_seen = {}
    scripts_seen = set()
    resolved_scripts = set()
    unresolved_scripts = set()
    unidentifiable = set()
    malformed = []
    for event, entries in (events.items() if isinstance(events, dict) else []):
        cmds = []
        # An event's value should be a list of groups, each a dict with a
        # "hooks" list of dicts. Every one of those three levels was assumed
        # rather than checked, and each shape below crashed until 2026-09-19.
        if not isinstance(entries, list):
            malformed.append(f"{event}: value is {type(entries).__name__}, expected a list")
            result["events"][event] = []
            continue
        for group in entries:
            if not isinstance(group, dict):
                malformed.append(f"{event}: group is {type(group).__name__}, expected an object")
                continue
            inner = group.get("hooks", [])
            if not isinstance(inner, list):
                malformed.append(f"{event}: inner hooks is {type(inner).__name__}, expected a list")
                continue
            for h in inner:
                if not isinstance(h, dict):
                    malformed.append(f"{event}: hook entry is {type(h).__name__}, expected an object")
                    continue
                cmd = h.get("command", "")
                cmds.append({"matcher": group.get("matcher"), "command": cmd})
                base = cmd.rstrip('"').split("/")[-1].strip('"')
                if base:
                    scripts_seen.add(base)
                # Three outcomes, not two. A hook whose script cannot even be
                # IDENTIFIED is a larger unknown than one that was identified
                # and whose payload could not be traced, and the previous
                # version ranked it below "nothing to inject" by saying
                # nothing at all.
                #
                # That regression shipped in 1.10.0 and was caught against
                # obra/superpowers, whose command is
                #   "${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd" session-start
                # A five-extension allowlist never matched .cmd, so a hook
                # injecting 3,192 bytes every session reported silence, while
                # the instructions told the reader that silence meant nothing
                # was injected. Identify first, resolve second, and never let a
                # failure to identify pass as an all-clear.
                script = _identify_hook_script(cmd, plugin_root)
                if script is None:
                    unidentifiable.add(f"{event}: {cmd.strip()[:90]}")
                else:
                    inj = resolve_injected_text(script, plugin_root)
                    if inj:
                        injected_seen[inj["resolved_file"]] = inj.get("bytes") or inj.get("chars") or 0
                        resolved_scripts.add(os.path.basename(script))
                    else:
                        unresolved_scripts.add(
                            f"{event}: {os.path.relpath(script, plugin_root)}")
        if event in SUBAGENT_EVENTS or event in SUBAGENT_TOOL_EVENTS:
            reaches_subagents = True
        if event in SUBAGENT_TOOL_EVENTS_LIKELY:
            reaches_subagents_likely = True
        result["events"][event] = cmds
    result["hooks_reach_subagents"] = reaches_subagents
    result["hooks_reach_subagents_basis"] = (
        "documented: a Subagent* event, or PreToolUse/PostToolUse which the docs "
        "say fire inside subagents" if reaches_subagents
        else "likely but not individually documented; read the events list"
        if reaches_subagents_likely else "no event known to fire in a subagent")
    # Report both counts. A plugin's own docs usually count distinct scripts,
    # while the registration count is higher whenever one script is wired to
    # more than one event. Reporting only the latter reads as drift against a
    # correct doc (found 2026-09-19 against a plugin with 8 scripts and 9
    # registrations, because one script was wired to two different events).
    result["hook_registrations"] = sum(len(v) for v in result["events"].values())
    result["hook_scripts"] = len(scripts_seen)
    result["injected_content"] = [{"file": f, "bytes": b} for f, b in injected_seen.items()] or None
    result["injected_bytes_total_estimate"] = sum(injected_seen.values()) or None
    if malformed:
        result["malformed_entries"] = malformed
        result["has_hooks"] = "partial"
    # Report unresolved hooks per script, not only when the whole set failed.
    # The old condition fired only if NOTHING resolved, so one hook that did
    # resolve silenced the warning for every hook that did not: an unresolved
    # PreToolUse gate looked exactly like a hook with nothing to inject. Found
    # 2026-09-19 by an evaluation of the judgment half, which flagged the
    # silence as indistinguishable from an all-clear.
    if unresolved_scripts:
        result["unresolved_hooks"] = sorted(unresolved_scripts)
    if unidentifiable:
        result["unidentifiable_hooks"] = sorted(unidentifiable)
    unknown = len(unresolved_scripts) + len(unidentifiable)
    if unknown:
        parts = []
        if unresolved_scripts:
            parts.append(f"{len(unresolved_scripts)} whose script was found but whose "
                         "payload could not be traced")
        if unidentifiable:
            parts.append(f"{len(unidentifiable)} whose script could not even be identified "
                         "from the command")
        result["injected_content_note"] = (
            f"{unknown} hook(s) have unknown behaviour, which is not the same as none: "
            + "; ".join(parts) + ". Read them by hand.")
    return result


def mcp_servers(plugin_json, plugin_root=None):
    """MCP servers a plugin bundles. Reported because an MCP server is a live
    tool surface with network reach and real side effects, which makes it the
    single highest-consequence thing a plugin can ship. Invisible until
    2026-09-19, when a target declaring two of them reported nothing at all.

    This tool inspects the declaration only. What the server actually exposes
    is knowable only by speaking MCP to it, which is out of scope here."""
    servers = plugin_json.get("mcpServers") or plugin_json.get("mcp_servers") or {}
    source = "plugin.json"
    ambiguity = None

    # A plugin may instead ship .mcp.json at its root, which Claude Code loads.
    # Reading only the inline manifest key missed it entirely, including in
    # Anthropic's own example-plugin, which sits inside the 39-plugin catalog
    # this tool swept and declared free of MCP servers (found 2026-09-19).
    if not servers and plugin_root:
        dot = os.path.join(plugin_root, ".mcp.json")
        if os.path.lexists(dot) and not _within(dot, plugin_root):
            return {"source": ".mcp.json", "servers": None,
                    "refused": ".mcp.json resolves outside the target tree; not read"}
        raw = read_json(dot)
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
    if not isinstance(servers, dict) or not servers:
        return None
    out = []
    for name, cfg in servers.items():
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


def inventory_persistence(plugin_root):
    hits = []
    for dirpath, dirnames, filenames in os.walk(plugin_root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", "__pycache__", "vendor", "benchmarks", "tests", "test")]
        for fn in filenames:
            fp = os.path.join(dirpath, fn)
            if not _within(fp, plugin_root):
                continue
            if not fn.endswith(SCRIPT_EXTS):
                # Keep extension-less files (hooks/session-start and friends),
                # skip obvious non-scripts and anything large.
                if "." in fn or fn.startswith("."):
                    continue
                try:
                    if os.path.getsize(fp) > 200_000:
                        continue
                except OSError:
                    continue
            text = read_text(fp, limit=50_000) or ""
            for pat in PERSIST_PATTERNS:
                if pat.search(text):
                    hits.append(os.path.relpath(fp, plugin_root))
                    break
    return sorted(set(hits))


def contained_skill(sm, root):
    """One SKILL.md from the target, or a refusal if it resolves outside it.

    Both skill paths go through here. Until 2026-09-24 only the plugin path
    checked containment, so a pack with no manifest (the "plain pack of rules"
    case) read skills/x/SKILL.md straight through a symlink to anywhere."""
    if not _within(sm, root):
        return {"source": os.path.relpath(sm, root), "path": sm,
                "name": os.path.basename(os.path.dirname(sm)),
                "description": None, "bytes": None, "text": None,
                "refused": "resolves outside the target tree; not read"}
    return rule_item(os.path.relpath(sm, root), sm)


def inventory_skills(root):
    """Broad, recursive search — for a generic pack with no canonical layout."""
    return [it for it in (contained_skill(sm, root) for sm in find_files(root, {"SKILL.md"})) if it]


def plugin_skills(root):
    """A Claude Code plugin's own skills are unambiguously root/skills/*/SKILL.md
    (the standard plugin paths). A non-recursive glob here,
    rather than inventory_skills' repo-wide walk, deliberately excludes bundled
    mirrors for other agent ecosystems a multi-platform plugin may ship
    (.openclaw/skills/, .opencode/command/, .cursor/rules/, etc.) — those are
    invisible to Claude Code and would otherwise double-count and inflate the
    target's apparent size."""
    return [it for it in (contained_skill(sm, root)
                          for sm in sorted(glob.glob(os.path.join(root, "skills", "*", "SKILL.md"))))
            if it]


def inventory_commands_agents(root):
    """Slash commands and agent definitions, read in full like skills.

    Both are instructions to a model, so the classification step needs their
    text. They used to be listed by filename only, which left nothing to read
    for a git-URL target once its temp clone was gone (found 2026-09-24)."""
    def read(paths, source):
        out = []
        for p in sorted(paths):
            if not os.path.isfile(p):
                continue
            if not _within(p, root):
                out.append({"source": source, "path": os.path.relpath(p, root),
                            "name": os.path.basename(p), "text": None,
                            "refused": "resolves outside the target tree; not read"})
                continue
            it = rule_item(source, p)
            if it:
                it["path"] = os.path.relpath(p, root)
                out.append(it)
        return out
    commands = read([p for pat in ("*.md", "*.toml")
                     for p in glob.glob(os.path.join(root, "commands", pat))], "command")
    agents = read(glob.glob(os.path.join(root, "agents", "*.md")), "agent")
    return commands, agents


# ------------------------------------------------------------------ CLAUDE.md imports
# Claude Code lets a CLAUDE.md pull in other files with `@path`: relative to the
# importing file, `~` allowed, up to five hops, never inside code. A global
# CLAUDE.md that is only `@~/.claude/roles/me.md` is the documented way to split
# rules, and until 2026-09-24 this tool read exactly that one line and compared
# every target against it. Found by an evaluation that noticed its dossier held
# 26 bytes of global rules.
IMPORT_MAX_HOPS = 5
_CODE_RE = re.compile(r"```.*?```|~~~.*?~~~|`[^`\n]*`", re.S)
_IMPORT_RE = re.compile(r"(?:^|(?<=\s))@(\S+)")


def claude_md_imports(path, root=None, _hop=1, _seen=None):
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
            out.extend(claude_md_imports(cand, root, _hop + 1, seen))
    return out


def with_imports(source, path, root=None):
    """rule_item for a CLAUDE.md plus one item per file it imports."""
    items = []
    it = rule_item(source, path)
    if it:
        items.append(it)
    for p, parent, refused in claude_md_imports(path, root):
        if refused:
            items.append({"source": f"{source} import", "path": p, "imported_from": parent,
                          "text": None, "refused": "import resolves outside the target tree; not read"})
            continue
        imp = rule_item(f"{source} import", p)
        if imp:
            imp["imported_from"] = parent
            items.append(imp)
    return items


def target_rule_files(root):
    """A CLAUDE.md at the target's root is a rule file the target carries, and
    was read by nothing until 2026-09-24: a CLAUDE.md-only rule pack produced an
    empty dossier and skipped the reader's rules as having nothing to compare."""
    p = os.path.join(root, "CLAUDE.md")
    if not os.path.isfile(p):
        return []
    if not _within(p, root):
        return [{"source": "target-CLAUDE.md", "path": "CLAUDE.md", "text": None,
                 "refused": "resolves outside the target tree; not read"}]
    return with_imports("target-CLAUDE.md", p, root=root)


def inventory_target(path):
    if os.path.isfile(path):
        rule_files = with_imports("rule-file", path, root=os.path.dirname(path))
        return {
            "kind": "rule-file",
            "path": path,
            "is_plugin": False,
            "skills": [],
            "rule_files": rule_files,
            "hooks": {"has_hooks": False},
        }
    plugin_json_path, manifest_refused = None, None
    for cand in (os.path.join(path, ".claude-plugin", "plugin.json"), os.path.join(path, "plugin.json")):
        if os.path.isfile(cand) and not _within(cand, path):
            manifest_refused = (f"{os.path.relpath(cand, path)} resolves outside the target "
                                "tree; not read, so this was inventoried as a plain pack")
            continue
        if os.path.isfile(cand):
            plugin_json_path = cand
            break
    if not plugin_json_path:
        # Generic pack: no plugin manifest, so no canonical layout. Search
        # broadly for skills.
        #
        # STILL CHECK FOR HOOKS. A directory can carry hooks/hooks.json with no
        # manifest at all, and an earlier version of this branch asserted "no
        # hooks, no carrying cost by construction" without ever looking. Found
        # 2026-09-19: a test directory with a live SubagentStart hook reported
        # no hooks field whatsoever. Silently under-reporting a hook that
        # reaches subagents is the worst direction for this tool to be wrong in.
        skills = inventory_skills(path)
        readme = None
        for r in ("README.md", "readme.md"):
            if os.path.isfile(os.path.join(path, r)) and _within(os.path.join(path, r), path):
                readme = read_text(os.path.join(path, r), limit=4000)
                break
        return {
            "kind": "generic-pack",
            "path": path,
            "is_plugin": False,
            "skills": skills,
            "hooks": inventory_hooks(path, {}),
            "mcp_servers": mcp_servers({}, path),
            "persistence_candidates": inventory_persistence(path),
            "rule_files": target_rule_files(path),
            **dict(zip(("commands", "agents"), inventory_commands_agents(path))),
            "readme_excerpt": readme,
            **({"manifest_refused": manifest_refused} if manifest_refused else {}),
        }
    skills = plugin_skills(path)
    plugin_json = read_json(plugin_json_path) or {}
    return {
        "kind": "plugin",
        "path": path,
        "is_plugin": True,
        "plugin_json": {k: plugin_json.get(k) for k in ("name", "version", "description", "license")},
        "declares_hooks_in_manifest": "hooks" in plugin_json,
        "declares_agents_in_manifest": "agents" in plugin_json,
        "mcp_servers": mcp_servers(plugin_json, path),
        "skills": skills,
        "hooks": inventory_hooks(path, plugin_json),
        "persistence_candidates": inventory_persistence(path),
        "rule_files": target_rule_files(path),
        **dict(zip(("commands", "agents"), inventory_commands_agents(path))),
        **({"manifest_refused": manifest_refused} if manifest_refused else {}),
    }


# ------------------------------------------------------------------ settings layering
def merge_enabled_plugins(project_root):
    """Which plugins are enabled, merged the way Claude Code layers its settings.

    WHICH PLUGINS ARE ENABLED IS NOT ONE FILE. Claude Code reads the user's
    ~/.claude/settings.json, then the project's .claude/settings.json, then
    .claude/settings.local.json, each overriding the one before. Reading only the
    project file, which this tool did until 2026-09-20, misses every plugin enabled
    globally -- which is the normal way to enable one.

    Measured the day it was found: vetting a target from ~/proj/neckbeard, a repo with
    no .claude/ directory at all, discovered **8** rule sources where the corrected path
    discovers **23**. The 15 it missed were the installed skills of all six enabled
    plugins, `delegation` and `delegation-lab` among them, which were exactly the rules
    that target conflicted with. The evaluation would have reported NO CONFLICTS because
    the conflicting rules were invisible.

    A first attempt to size this said 59, obtained by passing `--extra-rules` over a
    whole worktree. That path recursively counts every markdown file it meets, so 40 of
    those 51 "missing rules" were agent definitions, READMEs, docs and two briefs
    written the same afternoon. **The measurement used to size a bug about under-broad
    rule discovery was itself produced by an over-broad one, and it was not re-derived
    once the correct path existed.** Worth keeping: a number can read correctly, survive
    review and be wrong, which is the same shape as the defect it was describing.

    That is this tool's whole purpose failing quietly: "compare the target against the
    rules already in force" had been comparing against about a third of them and
    saying nothing. Personal SKILLS were already read from CLAUDE_HOME, which is why
    this reads as an oversight rather than a decision.

    Later layers override earlier ones, including overriding true with false, so a
    project may legitimately disable a globally-enabled plugin and that is honoured
    rather than unioned away.
    """
    merged = {}
    for settings_path in (
        os.path.join(CLAUDE_HOME, "settings.json"),
        os.path.join(project_root, ".claude", "settings.json"),
        os.path.join(project_root, ".claude", "settings.local.json"),
        # Managed settings sit above every other layer and nothing overrides
        # them, so an organisation that force-disables a plugin there must win.
        # Missing until 2026-09-24. MDM- and console-delivered policy is not
        # readable from disk and stays out of reach; see MANAGED_SETTINGS.
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
            # rather than only the two canonical names. Filtering an explicit
            # path by filename made `--extra-rules <dir>` silently contribute
            # nothing unless the files happened to be SKILL.md or CLAUDE.md,
            # which defeats the flag's entire purpose (found 2026-09-19).
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
    `git add` away from publishing it.

    Found 2026-09-19 by an independent audit of this tool: a run from inside
    this plugin's own repo produced 90,533 bytes of private rules including a
    Tailscale hostname, a NAS host and two private marketplace names, in a repo
    with no gitignore rule that would have caught it.

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
    skills. Measured 2026-09-20: a 102,899-byte dossier for a target with zero
    classifiable items, of which about 100KB was the reader's own rules, read off
    disk and embedded to be compared against nothing.

    Counts skills, and ANY hook at all -- not only the ones whose payload
    resolved.

    The first version of this counted `injected_content` and nothing else, which
    walked straight into the rule this tool exists to enforce: *never read a
    hook's absence from `injected_content` as "it injects nothing."* A fixture
    with one SessionStart hook injecting two rules, whose shell payload the
    resolver could not trace, landed in `unresolved_hooks` -- and this function
    scored it zero and skipped the reader's rules, for a target that injects at
    every session start. Caught 2026-09-20 by the fixture written to check the
    other direction. An unresolved hook is the case where the reader most needs
    their own rules in hand, because they are about to go read that script.

    Deliberately fails toward INCLUDING the rules. Skipping them when there IS
    something to classify breaks the tool; carrying them when there is not only
    wastes bytes. So this returns a count and the caller skips on a hard zero,
    rather than judging whether the items found are worth comparing."""
    # Commands, agents and rule files carry instructions too. Counting only
    # skills and hooks skipped the reader's rules for a pack of nothing but
    # commands/ and agents/, which is the failure this function exists to avoid
    # (found 2026-09-24 by a falsify pass).
    n = sum(len(target_dossier.get(k) or [])
            for k in ("skills", "rule_files", "commands", "agents"))
    hooks = target_dossier.get("hooks") or {}
    if isinstance(hooks, dict) and hooks.get("has_hooks"):
        n += max(1, len(hooks.get("injected_content") or []))
    return n


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target")
    ap.add_argument("--project-dir", default=os.getcwd())
    ap.add_argument("--extra-rules", action="append", default=[])
    ap.add_argument("--out")
    args = ap.parse_args()

    with tempfile.TemporaryDirectory(prefix="neckbeard-") as tmp:
        path, resolution = resolve_target(args.target, tmp)
        target_dossier = inventory_target(path)
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
