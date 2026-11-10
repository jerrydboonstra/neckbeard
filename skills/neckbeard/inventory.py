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
# Deliberately broad. Matches constructed writes as well as direct calls --
# shell append redirection, a copy into a home-directory cache, pathlib
# write_text, appendFileSync, createWriteStream -- because a persistence scan
# that only catches the obvious calls gives false confidence. Treat any match
# as a candidate to verify by hand, not a verdict. See CASE-STUDIES.md, round 9.
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


class _Note(str):
    """One line of a section's read_status notes, "<path relative to the target>: <reason>".
    `level` says how much of the section the line costs: "failed" (the section could not be
    read), "entry" (one entry of it was not read) or "partial" (part of it was left unread,
    a cap for one)."""
    level = "partial"


def _note(notes, text, level="partial"):
    """Record a read that did not go through, on the list a caller passed. A caller that
    passed none (the reader side's discovery among them) sees nothing change."""
    if notes is not None:
        n = _Note(text)
        n.level = level
        notes.append(n)


def _rel(path, root):
    return os.path.relpath(path, root) if os.path.isabs(path) else path


def read_text(path, limit=READ_LIMIT):
    try:
        with open(path, "r", errors="replace") as f:
            return f.read(limit)
    except Exception:
        return None


def measure(path, text):
    """Real size on disk, characters read, and whether the read was cut short.

    `bytes` is measured on disk, not derived from a decoded string's length --
    that undercounts any non-ASCII content. Also flags when the read hit the
    size limit, so a large file cannot silently report a truncated size as if
    it were the whole thing."""
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
    # Split on lines that are exactly a fence, not on the first "---" anywhere:
    # a description containing "---" would otherwise truncate the frontmatter
    # early and misparse the body.
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


# A plain (unquoted) value may not start with these in strict YAML.
_YAML_PLAIN_BAD_START = ("@", "`", "*", "%", "!", "- ", "? ")
_BLOCK_HEADER_RE = re.compile(r"^[+\-0-9]*\s*(#.*)?$")


def _quoted_end(text, q, start=1):
    """Index of the quote that closes a quoted scalar opened before `start`, or -1.
    A double-quoted scalar escapes with a backslash, a single-quoted one by doubling the quote."""
    i = start
    while i < len(text):
        c = text[i]
        if q == '"' and c == "\\":
            i += 2
            continue
        if c == q:
            if q == "'" and text[i + 1:i + 2] == "'":
                i += 2
                continue
            return i
        i += 1
    return -1


def _flow_depth(text, depth):
    """Bracket depth after `text`, ignoring quoted parts; text after depth reaches 0 is returned too."""
    i = 0
    while i < len(text):
        c = text[i]
        if c in "\"'":
            e = _quoted_end(text, c, i + 1)
            if e < 0:
                return depth, ""
            i = e
        elif c in "[{":
            depth += 1
        elif c in "]}":
            depth -= 1
            if depth <= 0:
                return 0, text[i + 1:]
        i += 1
    return depth, ""


def _after_value_ok(rest):
    rest = rest.strip()
    return not rest or rest.startswith("#")


def frontmatter_errors(text):
    """Faults a strict YAML parser rejects in a file's frontmatter, as [{"line", "message"}].

    Claude Code loads frontmatter leniently, so an unquoted ": " in a description works
    there while GitHub shows "Error in user YAML" and stricter agents may drop the skill.
    This is not a YAML parser (the standard library has none, and CONTRIBUTING.md allows no
    dependency); it checks the faults seen in real repos, and was compared with PyYAML on
    them. Line numbers count from the file's first line.
    # debt: misses a bad value inside a flow collection ([a, b: c]), anchors, aliases and
    tags used as values, duplicate keys, list items (`- key: a: b`), and a stray ' or " in the
    middle of a plain value; the upgrade path is a vendored strict parser behind this same function."""
    if not text or not text.startswith("---"):
        return []
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return []
    close = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if close is None:
        return [{"line": 1, "message": "the opening --- has no closing ---"}]
    errs = []

    def err(n, msg):
        errs.append({"line": n, "message": msg})

    mode, key_indent = None, 0   # mode: None, "block", "plain"
    i = 1
    while i < close:
        line, n = lines[i], i + 1
        indent = len(line) - len(line.lstrip())
        if "\t" in line[:indent]:
            err(n, "a tab is used for indentation; YAML allows only spaces")
            i += 1
            continue
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if mode == "block" and indent > key_indent:
            i += 1
            continue
        if mode == "plain" and indent > key_indent:
            body = re.split(r"\s#", line.strip())[0].rstrip()
            if ": " in body or body.endswith(":"):
                err(n, "a continued unquoted value holds ': '; quote the value or use a >- block")
            i += 1
            continue
        mode = None
        m = re.match(r"^\s*([A-Za-z_][\w-]*):(?:\s+(.*))?$", line)
        if not m:
            i += 1
            continue
        key_indent, val = indent, (m.group(2) or "").strip()
        if not val:
            i += 1
            continue
        c = val[0]
        if c in ">|":
            if not _BLOCK_HEADER_RE.match(val[1:]):
                err(n, f"text after the {c} block header; put it on the following lines")
            mode = "block"
        elif c in "\"'":
            end, j = _quoted_end(val, c), i
            while end < 0 and j + 1 < close:   # a quoted value may run on over several lines
                j += 1
                end = _quoted_end(lines[j], c, 0)
                last = lines[j]
            if end < 0:
                err(n, f"a {c} opened here is never closed")
            else:
                tail = (val if j == i else last)[end + 1:]
                if not _after_value_ok(tail):
                    err(j + 1, "text after the closing quote")
            i = j
        elif c in "[{":
            depth, tail, j = *_flow_depth(val, 0), i
            while depth > 0 and j + 1 < close:
                j += 1
                depth, tail = _flow_depth(lines[j], depth)
            if depth > 0:
                err(n, f"a {c} opened here is never closed")
            elif not _after_value_ok(tail):
                err(j + 1, "text after the closing bracket")
            i = j
        else:
            mode = "plain"
            body = re.split(r"\s#", val)[0].rstrip()
            if body.startswith(_YAML_PLAIN_BAD_START) or body in ("-", "?"):
                err(n, f"a plain value may not start with {body[:2].strip() or body}; quote it")
            elif ": " in body or body.endswith(":"):
                err(n, "an unquoted value holds ': ', which strict YAML reads as a nested mapping; "
                       "quote the value or use a >- block")
        i += 1
    return errs


def note_frontmatter(item):
    """Attach frontmatter_errors to a target's skill, command or agent, only when there are some."""
    errs = frontmatter_errors(item.get("text"))
    if errs:
        item["frontmatter_errors"] = errs
    return item


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
    skills/<name>/SKILL.md is named <name>, not "SKILL"."""
    base = os.path.basename(path)
    if base.upper().startswith("SKILL."):
        parent = os.path.basename(os.path.dirname(path))
        if parent:
            return parent
    return os.path.splitext(base)[0]


def _within(path, root):
    """True when path really sits under root, following symlinks. The target is
    untrusted by definition, so a skills/x/SKILL.md symlinked to /etc/passwd
    must not be read and embedded in a dossier. See CASE-STUDIES.md, round 9."""
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
def find_files(root, names, max_depth=6, notes=None):
    out = []
    root = root.rstrip("/")
    base_depth = root.count(os.sep)
    for dirpath, dirnames, filenames in os.walk(root):
        if dirpath.count(os.sep) - base_depth > max_depth:
            if dirnames or filenames:
                _note(notes, f"{os.path.relpath(dirpath, root)}: not searched, deeper than {max_depth} folders")
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
    """Ordered most-trustworthy first: a path.join(...) reconstruction is
    evidence the file is actually being built as a path, while a bare quoted
    string is not, and treating a bare literal as equally confident risks
    naming an unrelated file quoted nearby over the real payload, with no note
    telling the reader to doubt it. Handles single-literal paths
    ('../skills/x/SKILL.md') and path.join(...) calls whose arguments are all
    string literals or __dirname/__filename (ponytail's actual pattern:
    path.join(__dirname, '..', 'skills', 'ponytail', 'SKILL.md')),
    reconstructed as a plain relative path. Returns (candidate, confident)
    pairs."""
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


def resolve_injected_text(hook_file_path, plugin_root, depth=1, notes=None):
    """Best-effort: a hook script that reads a fixed SKILL.md-shaped file and
    injects it wholesale (ponytail's pattern: SessionStart hook requires a
    sibling module, which builds the path via path.join(__dirname, ..., 'SKILL.md'))
    names that file's path in its own source or one local require() away. Follows
    one hop of local requires, reconstructs literal + path.join(...) candidates,
    and resolves each against the hook's own directory and the plugin root.
    Anything genuinely dynamic (computed from runtime state) is reported as such."""
    src = read_text(hook_file_path, limit=20_000) or ""
    if len(src) >= 20_000 and os.path.getsize(hook_file_path) > 20_000:
        _note(notes, f"{os.path.relpath(hook_file_path, plugin_root)}: read capped at 20000 bytes")
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
                    found = resolve_injected_text(required, plugin_root, depth=depth - 1, notes=notes)
                    if found:
                        return found
                    break
    return fallback


def _expand_plugin_root(s, plugin_root):
    """Replace every reference to CLAUDE_PLUGIN_ROOT in a hook command with the
    plugin root: $CLAUDE_PLUGIN_ROOT, ${CLAUDE_PLUGIN_ROOT}, and the shell's
    default forms ${CLAUDE_PLUGIN_ROOT:-word}, ${...-word}, ${...:=word},
    ${...=word}, ${...:?word} and ${...?word}, whose word may itself hold ${...}. Claude Code always sets the
    variable, so each of those forms is its value and the word never runs.
    Cat Herder writes "${CLAUDE_PLUGIN_ROOT:-${PLUGIN_ROOT}}/bin/meow" so one
    hook file serves several hosts; matching only the plain forms reported all
    three of its hooks as unidentifiable. ${...:+word} (word when set) is left
    alone: its value is the word, not the root. So is $CLAUDE_PLUGIN_ROOTX, a
    different variable (1.14.0 and earlier expanded it, by a substring replace). The scan
    does not read quotes, so a quoted } inside the word ends it early and the
    hook reads as unidentifiable: an unknown, never a false all-clear."""
    head = "${CLAUDE_PLUGIN_ROOT"
    out, i = [], 0
    while True:
        j = s.find(head, i)
        if j < 0:
            break
        k = j + len(head)
        rest = s[k:]
        op = next((o for o in (":-", ":=", ":?", "-", "=", "?") if rest.startswith(o)), None)
        if not rest.startswith("}") and op is None:
            out.append(s[i:k])
            i = k
            continue
        # Find the closing brace of this ${...}, counting nested ${ ... }.
        depth, m = 1, k
        while m < len(s) and depth:
            if s.startswith("${", m):
                depth, m = depth + 1, m + 2
                continue
            if s[m] == "}":
                depth -= 1
            m += 1
        if depth:
            break
        out.append(s[i:j] + plugin_root)
        i = m
    s = "".join(out) + s[i:]
    return re.sub(r"\$CLAUDE_PLUGIN_ROOT(?![A-Za-z0-9_])", lambda _: plugin_root, s)


def _identify_hook_script(cmd, plugin_root):
    """The file a hook command actually runs, or None if it cannot be worked out.

    Deliberately not gated on an extension list or on quoting. Expands the
    plugin-root variable (with its default forms), takes every
    whitespace-separated token, strips quotes, and returns the first that
    exists as a file inside the tree. Anything else is unidentifiable, which
    is a reportable state, not silence."""
    # Expand to a token with no whitespace first, so a default word with spaces
    # still splits as the shell would, and a plugin root with spaces in its path
    # is never split; the real root goes in per token.
    mark = "\0PLUGIN_ROOT\0"
    for tok in _expand_plugin_root(cmd, mark).split():
        t = tok.strip("\"'").replace(mark, plugin_root)
        if not t or t.startswith("-"):
            continue
        cands = [t] if os.path.isabs(t) else [
            os.path.join(plugin_root, t),
            os.path.join(plugin_root, "hooks", os.path.basename(t)),
        ]
        for c in cands:
            c = os.path.normpath(c)
            if os.path.isfile(c) and _within(c, plugin_root):
                return c
    return None


def inventory_hooks(plugin_root, plugin_json, notes=None):
    hooks_ref = plugin_json.get("hooks")
    hooks_path = None
    # plugin.json may carry its hooks inline as an object rather than naming a
    # file. That shape must be handled before it reaches os.path.join, which
    # expects a path string, or the run crashes with no dossier at all. See
    # CASE-STUDIES.md, round 14.
    if isinstance(hooks_ref, dict) and hooks_ref:
        rel, hooks_json = "plugin.json (inline hooks)", hooks_ref
    elif isinstance(hooks_ref, list) and hooks_ref and all(isinstance(h, (str, dict)) for h in hooks_ref):
        # A list of hook files (or inline objects): Claude Code merges them, and so do we.
        return _merge_hook_list(plugin_root, hooks_ref, notes)
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
            if hooks_ref:
                _note(notes, f"plugin.json: hooks path {hooks_ref} in plugin.json not found", "failed")
            # Not where Claude Code would load them from, which is not the same
            # as nowhere. See hooks_outside_manifest().
            return hooks_outside_manifest(plugin_root, notes=notes)
        rel = os.path.relpath(hooks_path, plugin_root)
        # plugin.json names this path, and plugin.json is untrusted: "../../x.json"
        # or a symlinked hooks/ can read a file from anywhere, no symlink
        # privileges needed for the traversal case. See CASE-STUDIES.md, round 14.
        if not _within(hooks_path, plugin_root):
            return {"has_hooks": "unknown", "hooks_file": rel, "events": {},
                    "hook_scripts": None, "hook_registrations": None,
                    "hooks_reach_subagents": None,
                    "refused": "hooks file resolves outside the target tree; not read"}
        hooks_json = read_json(hooks_path)

    # A hooks file that exists but cannot be read is NOT "no hooks", and it is
    # not "hooks with no events" either. Say what is actually known, which is
    # that there is a hooks file and it did not parse. See CASE-STUDIES.md,
    # round 8.
    if hooks_json is None:
        return {"has_hooks": "unknown", "hooks_file": rel, "events": {},
                "hook_scripts": None, "hook_registrations": None,
                "hooks_reach_subagents": None,
                "parse_error": "hooks file exists but is not valid JSON; read it by hand"}

    # Claude Code nests events under a "hooks" key; some plugins write them at
    # the top level. Anything else (a list, a string, a number) is neither, and
    # must be handled explicitly rather than assumed. See CASE-STUDIES.md,
    # round 8.
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

    return _parse_events(events, rel, plugin_root, notes)


def _merge_hook_list(plugin_root, refs, notes=None):
    """plugin.json's "hooks" as a list: each entry is a path to a hooks file or an inline
    object of events. Every path passes the same containment and parse checks as a single
    file, and a bad entry makes the whole answer "unknown" rather than a quiet partial."""
    merged, names = {}, []
    for ref in refs:
        if isinstance(ref, dict):
            name, hooks_json = "plugin.json (inline hooks)", ref
        else:
            path = os.path.normpath(os.path.join(plugin_root, ref))
            name = os.path.relpath(path, plugin_root)
            if not _within(path, plugin_root):
                return {"has_hooks": "unknown", "hooks_file": name, "events": {},
                        "hook_scripts": None, "hook_registrations": None,
                        "hooks_reach_subagents": None,
                        "refused": "hooks file resolves outside the target tree; not read"}
            hooks_json = read_json(path) if os.path.isfile(path) else None
            if hooks_json is None:
                return {"has_hooks": "unknown", "hooks_file": name, "events": {},
                        "hook_scripts": None, "hook_registrations": None,
                        "hooks_reach_subagents": None,
                        "parse_error": "hooks file is missing or not valid JSON; read it by hand"}
        events = hooks_json.get("hooks", hooks_json) if isinstance(hooks_json, dict) else None
        if not isinstance(events, dict):
            return {"has_hooks": "unknown", "hooks_file": name, "events": {},
                    "hook_scripts": None, "hook_registrations": None,
                    "hooks_reach_subagents": None,
                    "parse_error": "hooks entry is not an object of event names; read it by hand"}
        names.append(name)
        for event, groups in events.items():
            merged.setdefault(event, [])
            if isinstance(groups, list):
                merged[event].extend(groups)
            else:
                merged[event] = groups  # malformed: _parse_events reports it
    return _parse_events(merged, ", ".join(names), plugin_root, notes)


def _parse_events(events, rel, plugin_root, notes=None):
    """Everything known about one object of hook events: what each registers, what
    it injects where that can be traced, and whether any of it reaches subagents."""
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
        # "hooks" list of dicts. Every one of those three levels needs checking
        # explicitly; each malformed shape below is reported, not assumed away.
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
                if not isinstance(cmd, str):
                    _note(notes, f"{rel}: {event}: hook command is {type(cmd).__name__}, expected a string; "
                                 "this hook was not read", "failed")
                    continue
                cmds.append({"matcher": group.get("matcher"), "command": cmd})
                base = cmd.rstrip('"').split("/")[-1].strip('"')
                if base:
                    scripts_seen.add(base)
                # Three outcomes, not two. A hook whose script cannot even be
                # IDENTIFIED is a larger unknown than one that was identified
                # and whose payload could not be traced, and ranking it below
                # "nothing to inject" by saying nothing turns an unknown into a
                # false all-clear. An extension allowlist is not enough to
                # identify a script: obra/superpowers runs its hook via
                #   "${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd" session-start
                # a wrapper with no recognizable script extension, and would
                # otherwise report silence while injecting content every
                # session. Identify first, resolve second, and never let a
                # failure to identify pass as an all-clear. See
                # CASE-STUDIES.md, round 12.
                script = _identify_hook_script(cmd, plugin_root)
                if script is None:
                    unidentifiable.add(f"{event}: {cmd.strip()[:90]}")
                else:
                    inj = resolve_injected_text(script, plugin_root, notes=notes)
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
    # more than one event. Reporting only the latter can read as drift against
    # a correct doc. See CHANGELOG.md 1.1.0.
    result["hook_registrations"] = sum(len(v) for v in result["events"].values())
    result["hook_scripts"] = len(scripts_seen)
    result["injected_content"] = [{"file": f, "bytes": b} for f, b in injected_seen.items()] or None
    result["injected_bytes_total_estimate"] = sum(injected_seen.values()) or None
    if malformed:
        result["malformed_entries"] = malformed
        result["has_hooks"] = "partial"
    # Report unresolved hooks per script, not only when the whole set failed:
    # one hook that resolves must not silence the warning for one that does
    # not, or an unresolved PreToolUse gate looks exactly like a hook with
    # nothing to inject. See CASE-STUDIES.md, round 11.
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


# Claude Code's hook event names. A JSON object keyed by at least one of these, each
# a list, is hook configuration wherever it sits in the tree.
HOOK_EVENTS = {"PreToolUse", "PostToolUse", "PostToolUseFailure", "UserPromptSubmit",
               "Notification", "Stop", "SubagentStart", "SubagentStop", "SessionStart",
               "SessionEnd", "PreCompact", "PermissionRequest"}
# Manifests and package metadata: read elsewhere or never hook configuration.
NOT_HOOK_CONFIG = {"plugin.json", "marketplace.json", "package.json", "package-lock.json",
                   "tsconfig.json"}


def _hook_events_in(obj):
    if not isinstance(obj, dict):
        return None
    events = obj["hooks"] if isinstance(obj.get("hooks"), dict) else obj
    known = {k: v for k, v in events.items() if k in HOOK_EVENTS}
    if known and all(isinstance(v, list) for v in known.values()):
        return known
    return None


def settings_writers(root):
    """Scripts that write files and name a settings.json: the likely installers."""
    return [rel for rel in inventory_persistence(root)
            if re.search(r"settings(\.local)?\.json",
                         read_text(os.path.join(root, rel), limit=50_000) or "")]


def hooks_outside_manifest(root, max_reads=20_000, notes=None):
    """Hook configuration that no manifest names, which is not the same as none.

    A plugin can ship with no manifest at all and an installer that merges the
    "hooks" block of its install.json into ~/.claude/settings.json. Checking
    only a manifest and hooks/hooks.json reported ten hook groups, SubagentStart
    among them, as none. So search the tree for JSON shaped like hook
    configuration, and when it turns up, report it as hooks with a note saying
    how they get installed. A false alarm here costs the reader a look at one
    file; a miss costs them every session. See CHANGELOG.md 1.12.6.

    No depth limit: 1.12.6 stopped four levels down and returned a bare false
    for hooks below that (1.12.7). What bounds the walk instead is how many JSON
    files it reads, and running out is said, never silent. The largest of
    128 local trees measured read 5,378 JSON files in about 3 seconds."""
    root = root.rstrip("/")
    found, events, reads, stopped_at = [], {}, 0, None
    for dirpath, dirnames, filenames in os.walk(root):
        if stopped_at:
            break
        dirnames[:] = sorted(d for d in dirnames if d not in (".git", "node_modules", "__pycache__", "vendor"))
        for fn in sorted(filenames):
            if not fn.endswith(".json") or fn in NOT_HOOK_CONFIG:
                continue
            fp = os.path.join(dirpath, fn)
            rel_fp = os.path.relpath(fp, root)
            try:
                if not _within(fp, root):
                    _note(notes, f"{rel_fp}: resolves outside the target tree; not searched for hooks")
                    continue
                if os.path.getsize(fp) > READ_LIMIT:
                    _note(notes, f"{rel_fp}: over {READ_LIMIT} bytes; not searched for hooks")
                    continue
            except OSError:
                _note(notes, f"{rel_fp}: could not be read; not searched for hooks")
                continue
            if reads >= max_reads:
                stopped_at = os.path.relpath(dirpath, root)
                break
            reads += 1
            data = read_json(fp)
            if data is None:
                _note(notes, f"{rel_fp}: not valid JSON; not searched for hooks")
            got = _hook_events_in(data)
            if got:
                found.append(os.path.relpath(fp, root))
                for event, groups in got.items():
                    events.setdefault(event, []).extend(groups)
    # A search cut short says so whatever it found: before it stopped, nothing
    # means unknown, and something means those hooks and maybe more.
    incomplete = (f"The search for hook-shaped JSON stopped after {max_reads} files, at "
                  f"{stopped_at}/, before reading the whole tree, so hooks past that "
                  "point were not looked for. Look for a hooks block by hand, or "
                  "inventory the plugin's own directory.") if stopped_at else None
    if not found and stopped_at:
        return {"has_hooks": "unknown", "events": {}, "hook_scripts": None,
                "hook_registrations": None, "hooks_reach_subagents": None,
                "search_incomplete": incomplete}
    if not found:
        return {"has_hooks": False}
    # A folder of plugins (no marketplace manifest, each plugin in its own
    # directory) turns up each plugin's own hooks/hooks.json here. Those are not
    # an installer's hooks, and merging several plugins' into one list describes
    # an install that never happens, so say unknown and name the plugins.
    nested = sorted({os.path.relpath(os.path.dirname(os.path.dirname(os.path.join(root, f))), root)
                     for f in found
                     if os.path.basename(os.path.dirname(os.path.join(root, f))) == "hooks"
                     and os.path.isfile(os.path.join(os.path.dirname(os.path.dirname(
                         os.path.join(root, f))), ".claude-plugin", "plugin.json"))})
    if nested and all(any(f.startswith(n + os.sep) for n in nested) for f in found):
        return {"has_hooks": "unknown", "events": {}, "hook_scripts": None,
                "hook_registrations": None, "hooks_reach_subagents": None,
                "nested_plugins": nested,
                "nested_note": (f"Hooks found inside {len(nested)} plugin(s) nested in this "
                                f"directory ({', '.join(nested)}). Inventory each plugin "
                                "directory on its own; this directory is not one plugin."),
                **({"search_incomplete": incomplete} if incomplete else {})}
    result = _parse_events(events, ", ".join(found), root, notes)
    result["hooks_source"] = "outside-manifest"
    if incomplete:
        result["search_incomplete"] = incomplete
    writers = settings_writers(root)
    if writers:
        result["settings_writers"] = writers
    result["hooks_note"] = (
        "No manifest names these, so Claude Code does not load them from this directory. "
        "They take effect when an installer script, or the README's instructions, merge "
        "them into a settings.json, and then they run in every session that file covers, "
        "not only this tool's. Check which file the install step uses.")
    return result


def marketplace_listing(path, notes=None):
    """The plugins a marketplace manifest at the target's root lists, and where each
    one's files are. A repo whose root is a marketplace and whose one plugin lives
    in plugins/<name>/ looked, read from the root, like a pack with no hooks and no
    agents. See CHANGELOG.md 1.12.6."""
    mp = os.path.join(path, ".claude-plugin", "marketplace.json")
    mp_rel = ".claude-plugin/marketplace.json"
    if not os.path.isfile(mp):
        if os.path.lexists(mp):
            _note(notes, f"{mp_rel}: a dangling symlink; not read", "failed")
        return None
    if not _within(mp, path):
        _note(notes, f"{mp_rel}: resolves outside the target tree; not read", "failed")
        return {"refused": "marketplace.json resolves outside the target tree; not read",
                "plugins": []}
    data = read_json(mp)
    entries = data.get("plugins") if isinstance(data, dict) else None
    if not isinstance(entries, list):
        why = "is not valid JSON" if data is None else "has no list of plugins"
        _note(notes, f"{mp_rel}: {why}; read it by hand", "failed")
        return {"parse_error": f"marketplace.json {why}; read it by hand", "plugins": []}
    plugins = []
    for e in entries:
        if not isinstance(e, dict):
            _note(notes, f"{mp_rel}: entry {str(e)[:60]!r} is not an object; skipped")
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
        if entry["status"].startswith(("refused", "missing")):
            _note(notes, f"{mp_rel}: plugin {e.get('name')!r} ({src}): {entry['status']}")
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
            _note(notes, f"plugin.json: mcpServers given as a path ({servers}), not followed", "failed")
        else:
            _note(notes, f"plugin.json: mcpServers is a {type(servers).__name__}, expected an object", "failed")

    # A plugin may instead ship .mcp.json at its root, which Claude Code loads.
    # Reading only the inline manifest key misses this path entirely --
    # including Anthropic's own example-plugin, which ships exactly this
    # shape. See CASE-STUDIES.md, round 9.
    if not servers and plugin_root:
        dot = os.path.join(plugin_root, ".mcp.json")
        if os.path.lexists(dot) and not _within(dot, plugin_root):
            _note(notes, ".mcp.json: resolves outside the target tree; not read", "failed")
            return {"source": ".mcp.json", "servers": None,
                    "refused": ".mcp.json resolves outside the target tree; not read"}
        raw = read_json(dot)
        if os.path.lexists(dot):
            if raw is None:
                _note(notes, ".mcp.json: not valid JSON; read it by hand", "failed")
            elif not isinstance(raw, dict):
                _note(notes, f".mcp.json: is a {type(raw).__name__}, expected an object", "failed")
            elif "mcpServers" in raw and not isinstance(raw["mcpServers"], dict):
                _note(notes, f".mcp.json: mcpServers is a {type(raw['mcpServers']).__name__}, "
                             "expected an object", "failed")
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
                _note(notes, f".mcp.json: {ambiguity}")
    if not isinstance(servers, dict) or not servers:
        return None
    out = []
    for name, cfg in servers.items():
        if not isinstance(cfg, dict):
            _note(notes, f"{source}: server {name!r} is not an object, so its command and url were not read")
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


def inventory_persistence(plugin_root, notes=None):
    hits = []
    for dirpath, dirnames, filenames in os.walk(plugin_root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", "__pycache__", "vendor", "benchmarks", "tests", "test")]
        for fn in filenames:
            fp = os.path.join(dirpath, fn)
            rel_fp = os.path.relpath(fp, plugin_root)
            if not _within(fp, plugin_root):
                _note(notes, f"{rel_fp}: resolves outside the target tree; not scanned")
                continue
            if not fn.endswith(SCRIPT_EXTS):
                # Keep extension-less files (hooks/session-start and friends),
                # skip obvious non-scripts and anything large.
                if "." in fn or fn.startswith("."):
                    continue
                try:
                    if os.path.getsize(fp) > 200_000:
                        _note(notes, f"{rel_fp}: over 200000 bytes; not scanned")
                        continue
                except OSError:
                    _note(notes, f"{rel_fp}: could not be read; not scanned")
                    continue
            text = read_text(fp, limit=50_000)
            if text is None:
                _note(notes, f"{rel_fp}: could not be read; not scanned")
                text = ""
            elif len(text) >= 50_000 and os.path.getsize(fp) > 50_000:
                _note(notes, f"{rel_fp}: read capped at 50000 bytes")
            for pat in PERSIST_PATTERNS:
                if pat.search(text):
                    hits.append(os.path.relpath(fp, plugin_root))
                    break
    return sorted(set(hits))


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
        _note(notes, f"{os.path.relpath(sm, root)}: could not be read", "entry")
    if item:
        fm, _ = split_frontmatter(item["text"])
        # Claude Code treats a skill as user-invocable unless its frontmatter says false.
        item["user_invocable"] = str((fm or {}).get("user-invocable", "true")).strip().lower() != "false"
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
    for dirpath, dirnames, filenames in os.walk(base):
        if dirpath[len(base):].count(os.sep) >= 6:
            if dirnames:
                _note(notes, f"{os.path.relpath(dirpath, root)}: companion files below this folder not read, "
                             "deeper than 6 folders")
            dirnames[:] = []
        dirnames[:] = sorted(d for d in dirnames if d not in (".git", "node_modules", "__pycache__", "vendor"))
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
                _note(notes, f"{rel}: companion file could not be read")
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
                          for sm in sorted(glob.glob(os.path.join(root, "skills", "*", "SKILL.md"))))
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
                _note(section, f"{os.path.relpath(p, root)}: not a readable file (a dangling symlink, or a folder)", "entry")
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
                _note(section, f"{os.path.relpath(p, root)}: not a readable file (a dangling symlink, or a folder)", "entry")
        return out
    commands = read([p for pat in ("*.md", "*.toml")
                     for p in glob.glob(os.path.join(root, "commands", pat))], "command")
    agents = read(glob.glob(os.path.join(root, "agents", "*.md")), "agent")
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
                _note(notes, f"{os.path.relpath(cand, root or os.path.dirname(path))}: import is a dangling "
                             "symlink; not read", "entry")
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
                         f"followed past {IMPORT_MAX_HOPS} hops")
    return out


def with_imports(source, path, root=None, notes=None):
    """rule_item for a CLAUDE.md plus one item per file it imports."""
    items = []
    it = rule_item(source, path)
    if it:
        items.append(it)
    else:
        _note(notes, f"{os.path.relpath(path, root or os.path.dirname(path))}: could not be read", "entry")
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
            _note(notes, f"{os.path.relpath(p, root or os.path.dirname(path))}: import could not be read", "entry")
    return items


def target_rule_files(root, notes=None):
    """A CLAUDE.md at the target's root is a rule file the target carries.
    Without this, a CLAUDE.md-only rule pack produces an empty dossier and
    skips the reader's rules as having nothing to compare. See
    CASE-STUDIES.md, round 14."""
    p = os.path.join(root, "CLAUDE.md")
    if not os.path.isfile(p):
        if os.path.lexists(p):
            _note(notes, "CLAUDE.md: a dangling symlink; not read", "entry")
        return []
    if not _within(p, root):
        return [{"source": "target-CLAUDE.md", "path": "CLAUDE.md", "text": None,
                 "refused": "resolves outside the target tree; not read"}]
    return with_imports("target-CLAUDE.md", p, root=root, notes=notes)


READ_SECTIONS = ("skills", "agents", "commands", "rule_files", "hooks", "mcp_servers",
                 "persistence_candidates", "plugin_json", "marketplace")


def inventory_target(path, plugin_name=None):
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
    market = marketplace_listing(path, notes["marketplace"])
    local = [p for p in (market or {}).get("plugins", []) if p.get("status") == "local"]
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
    plugin_json_path, manifest_refused = None, None
    for cand in (os.path.join(path, ".claude-plugin", "plugin.json"), os.path.join(path, "plugin.json")):
        if os.path.isfile(cand) and not _within(cand, path):
            manifest_refused = (f"{os.path.relpath(cand, path)} resolves outside the target "
                                "tree; not read, so this was inventoried as a plain pack")
            continue
        if os.path.isfile(cand):
            plugin_json_path = cand
            break
        if os.path.lexists(cand):
            _note(notes["plugin_json"], f"{os.path.relpath(cand, path)}: a dangling symlink; not read, "
                                        "so this was inventoried as a plain pack", "failed")
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
        _note(notes["plugin_json"], f"{os.path.relpath(plugin_json_path, path)}: {why}", "failed")
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

    Shape: {section: {"state": "read" | "partial" | "failed" | "not-applicable", "notes": [str]}} for
    skills, agents, commands, rule_files, hooks, mcp_servers, persistence_candidates, plugin_json and
    marketplace. A note reads "<path relative to the target>: <reason>". Every other key of the dossier
    is as it was; this only adds.

    Where the notes come from. Each site below records its own note on the list inventory_target passed
    down (`notes=`), kept as target["_read_notes"] until this folds it in and deletes it. Reason keys
    the dossier already carries (refused, truncated, imports_not_followed, parse_error,
    malformed_entries, injected_content_note, unresolved_hooks, unidentifiable_hooks, marketplace_note,
    nested_plugins, search_incomplete, manifest_refused) are folded in here, in the section they
    belong to. A note's level sets the state: "failed" makes the section failed; "entry" makes a list
    section failed when no entry of it was read, else partial; any other note makes it partial. A
    section with no note is read. Not-applicable: a rule-file target has every section but rule_files;
    a generic pack has no plugin_json unless a manifest was refused or dangling; marketplace is absent
    unless the target has a marketplace.json.

    Every site that turns a failed read or parse, a cap or a wrong-typed value into None, {}, [], "" or
    a skip records a note. They are, with a test each in tools/test_read_status.py:
      SK1 contained_skill -> skills: an unreadable SKILL.md is dropped (entry)
      SK2 contained_skill -> skills: a SKILL.md that resolves outside the tree is refused (key refused)
      SK3 skill_companions -> skills: an unreadable companion file has no text
      SK4 skill_companions -> skills: a companion past the 40 cap is listed without text (key skipped)
      SK5 skill_companions -> skills: folders deeper than 6 are not walked
      SK6 find_files -> skills: folders deeper than 6 are not searched (a generic pack)
      SK7 measure -> skills: a SKILL.md over the read limit is cut (key truncated)
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
      RF5 with_imports -> rule_files: an import that resolves outside the tree is refused; one
          rule_item cannot read is dropped (entry)
      RF6 inventory_target -> rule_files: a rule file other than CLAUDE.md follows no imports (key
          imports_not_followed)
      RF7 measure -> rule_files: a rule file over the read limit is cut (key truncated)
      HK1 inventory_hooks -> hooks: a hooks file that is not valid JSON, or whose events container is
          the wrong type (key parse_error)
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
      MC1 mcp_servers -> mcp_servers: .mcp.json exists and does not parse (absent is read, no entries)
      MC2 mcp_servers -> mcp_servers: .mcp.json parses to something that is not an object
      MC3 mcp_servers -> mcp_servers: mcpServers is not an object
      MC4 mcp_servers -> mcp_servers: plugin.json's mcpServers is a path, which is not followed
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
    Not noted: settings_writers re-reads files inventory_persistence just read, so a file it cannot
    read already has a persistence note; the reader's own rules (current_rules), which are
    reader-read-status's; a marketplace entry that is external, which is a choice the manifest makes.
    A site added to inventory.py without a line here, or a line without a test, sends the item back at
    review: nothing else catches it."""
    private = dossier.pop("_read_notes", None) or {}
    kind, base = dossier.get("kind"), dossier.get("path") or ""
    notes = {s: list(private.get(s) or []) for s in READ_SECTIONS}

    def add(section, text, level="partial"):
        n = _Note(text)
        n.level = level
        notes[section].append(n)

    for section in ("skills", "agents", "commands", "rule_files"):
        for entry in dossier.get(section) or []:
            if not isinstance(entry, dict):
                continue
            rel = _rel(entry.get("path") or entry.get("source") or section, base) if base else (entry.get("path") or section)
            if entry.get("refused"):
                add(section, f"{rel}: {entry['refused']}", "entry")
            if entry.get("truncated"):
                add(section, f"{rel}: read capped at {entry.get('read_limit', READ_LIMIT)} bytes")
            for comp in entry.get("companion_files") or []:
                if comp.get("refused") or comp.get("skipped"):
                    add(section, f"{comp.get('path')}: {comp.get('refused') or comp.get('skipped')}")
                elif comp.get("truncated"):
                    add(section, f"{comp.get('path')}: read capped at {comp.get('read_limit', READ_LIMIT)} bytes")
    for imp in dossier.get("imports_not_followed") or []:
        add("rule_files", f"{os.path.basename(base)}: import @{imp} not followed (only a CLAUDE.md follows its imports)")

    hooks = dossier.get("hooks")
    if isinstance(hooks, dict):
        hf = hooks.get("hooks_file") or "hooks"
        if hooks.get("parse_error"):
            add("hooks", f"{hf}: {hooks['parse_error']}", "failed")
        if hooks.get("refused"):
            add("hooks", f"{hf}: {hooks['refused']}", "failed")
        for m in hooks.get("malformed_entries") or []:
            add("hooks", f"{hf}: {m}")
        for key in ("unresolved_hooks", "unidentifiable_hooks"):
            if hooks.get(key):
                add("hooks", f"{hf}: {key.split('_')[0]} hooks: " + "; ".join(hooks[key]))
        if hooks.get("injected_content_note"):
            add("hooks", f"{hf}: {hooks['injected_content_note']}")
        if hooks.get("marketplace_note"):
            add("hooks", f".claude-plugin/marketplace.json: {hooks['marketplace_note']}", "failed")
        for n in hooks.get("nested_plugins") or []:
            add("hooks", f"{n}: hooks found in a plugin nested in this directory; inventory it on its own", "failed")
        if hooks.get("search_incomplete"):
            m = re.search(r" at (\S+)/, before", hooks["search_incomplete"])
            found = hooks.get("has_hooks") in (True, "partial")
            add("hooks", f"{m.group(1) + '/' if m else hooks.get('hooks_file') or 'hooks'}: {hooks['search_incomplete']}",
                "partial" if found else "failed")
    if dossier.get("manifest_refused"):
        add("plugin_json", dossier["manifest_refused"], "partial" if kind == "plugin" else "failed")

    na = set()
    if kind == "rule-file":
        na = set(READ_SECTIONS) - {"rule_files"}
    else:
        if kind == "generic-pack" and not notes["plugin_json"]:
            na.add("plugin_json")
        if not (dossier.get("marketplace") or notes["marketplace"]):
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
        status[section] = {"state": state, "notes": [str(n) for n in ns]}
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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target")
    ap.add_argument("--project-dir", default=os.getcwd())
    ap.add_argument("--extra-rules", action="append", default=[])
    ap.add_argument("--out")
    ap.add_argument("--plugin", help="when the target is a marketplace listing several "
                                     "plugins, the one to inventory")
    args = ap.parse_args()

    with tempfile.TemporaryDirectory(prefix="neckbeard-") as tmp:
        path, resolution = resolve_target(args.target, tmp)
        target_dossier = inventory_target(path, args.plugin)
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
