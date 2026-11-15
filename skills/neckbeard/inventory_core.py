#!/usr/bin/env python3
"""The helpers every part of neckbeard's inventory uses: reading files, the read-status notes, frontmatter,
the containment guard (_within lives only here among the inventory*.py modules; mcp_live.py keeps its own), and the file search. Moved out of inventory.py with no change
in behaviour, so no shipped file is over neckbeard's own read cap. inventory.py imports each name from here, so
`inventory.<name>` still resolves. Stdlib only; reads nothing outside the paths it is given.
"""
import json
import os
import re


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
    a cap for one). A note can carry text from the target, so it is one line of at most 400
    characters whatever the target wrote."""
    level = "partial"
    cause = None   # "tool-limit" (neckbeard's limit) or "target-fault" (the plugin's), set by _note and add

    def __new__(cls, text):
        return super().__new__(cls, " ".join(str(text).split())[:400])


def _note(notes, text, level="partial", *, cause):
    """Record a read that did not go through, on the list a caller passed. A caller that
    passed none (the reader side's discovery among them) sees nothing change. `cause` is required:
    "tool-limit" when the gap is neckbeard's (a cap, a depth limit, a refused path, a file it could not
    open, a thing it does not follow or trace), "target-fault" when the plugin is at fault (a file that
    does not parse, the wrong type, a dangling link, a path the manifest names that is not there)."""
    if notes is not None:
        n = _Note(text)
        n.level = level
        n.cause = cause
        notes.append(n)


def _rel(path, root):
    return os.path.relpath(path, root) if os.path.isabs(path) else path


def _walk_error(notes, root):
    """os.walk's onerror: a folder it cannot list is skipped, so say so."""
    def note(error):
        _note(notes, f"{os.path.relpath(error.filename, root) if error.filename else '.'}: folder could not be listed", cause="tool-limit")
    return note


def _walk_gaps(notes, dirpath, dirnames, root):
    """os.walk does not enter a symlinked folder (containment, and no loops), so what is inside one is not read: say so."""
    if notes is not None:
        for d in dirnames:
            if os.path.islink(os.path.join(dirpath, d)):
                _note(notes, f"{os.path.relpath(os.path.join(dirpath, d), root)}: a symlinked folder, not followed", cause="tool-limit")


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


def find_up(start, filename, home=None):
    """Walk up from start looking for filename; stop at `home` (inventory.py passes $HOME) or filesystem root."""
    d = os.path.abspath(start)
    while True:
        cand = os.path.join(d, filename)
        if os.path.isfile(cand):
            return cand
        if d in (home, os.path.dirname(d)):
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


# debt: a module-level set, not an argument, because the generic-pack search reaches find_files and
# hooks_outside_manifest through several callers. Only inventory_target sets it, and only while it
# reads a root that a marketplace lists beside nested local plugins; upgrade path: thread a skip
# argument through inventory_skills, inventory_hooks and the two walkers.
_SKIP_DIRS = set()


def _prune_skipped(dirpath, dirnames):
    """Drop the folders of other plugins from a walk: the root's own pack must not sweep in
    the skills and hooks a nested plugin ships, which installing the root never loads."""
    if _SKIP_DIRS:
        dirnames[:] = [d for d in dirnames if os.path.realpath(os.path.join(dirpath, d)) not in _SKIP_DIRS]


def find_files(root, names, max_depth=6, notes=None):
    out = []
    root = root.rstrip("/")
    base_depth = root.count(os.sep)
    for dirpath, dirnames, filenames in os.walk(root, onerror=_walk_error(notes, root)):
        if dirpath.count(os.sep) - base_depth > max_depth:
            if dirnames or filenames:
                _note(notes, f"{os.path.relpath(dirpath, root)}: not searched, deeper than {max_depth} folders", cause="tool-limit")
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", "__pycache__", "vendor")]
        _prune_skipped(dirpath, dirnames)
        _walk_gaps(notes, dirpath, dirnames, root)
        for fn in filenames:
            if fn in names:
                out.append(os.path.join(dirpath, fn))
    return out
