#!/usr/bin/env python3
"""The persistence scan of neckbeard's inventory: which files under a target may write something that persists. Every rule
about what counts as a write, and what a file merely names, lives here. Each file it lists has a tier: "writes" when a write
is found in its text (evidence, not proof that it runs), "mentions" when it only names a home path. Moved out of
inventory_hooks.py, which was at the size cap; inventory_hooks imports each name back, so `inventory.<name>` still resolves. Stdlib only.
"""
import os
import re

from inventory_core import _mark_scan, _note, _walk_error, _walk_gaps, _within, read_text


# Deliberately broad. Matches constructed writes as well as direct calls --
# shell append redirection, a copy into a home-directory cache, pathlib
# write_text, appendFileSync, createWriteStream -- because a persistence scan
# that only catches the obvious calls gives false confidence. Treat any match
# as a candidate to verify by hand, not a verdict. See CASE-STUDIES.md, round 9.
# A script is read in full up to this many characters; the patterns have unbounded
# spans, so reading in windows could split a match.
PERSIST_READ_CEILING = 2_000_000

# debt: spans are bounded to _SPAN characters (a shell write whose command word and $HOME sit
# more than _SPAN apart on one line is missed) so a hostile 2 MB one-line file cannot backtrack
# quadratically; upgrade path: scan per line in bounded pieces.
_SPAN = 400
_SHELL_WORD = re.compile(r"\b(cp|mv|rm|mkdir|touch|tee|install)\b")
_HOME_NEXT_LINE = re.compile(r"\s+[\"']?(\$HOME|~)/")
_HOME_ARG = re.compile(r"\s[\"']?(\$HOME|~)/")


def _shell_home_write(text):
    """cp/mv/rm/mkdir/touch/tee/install with $HOME after it on the line (up to a pipe), or
    cp/mv/tee followed by an argument starting $HOME/ or ~/. Linear: each word looks at _SPAN characters."""
    if "$HOME" not in text and "~/" not in text:
        return False
    for m in _SHELL_WORD.finditer(text):
        full = text[m.end():m.end() + _SPAN]
        win, _, rest = full.partition("\n")
        if "$HOME" in win.split("|", 1)[0]:
            return True
        if m.group(1) in ("cp", "mv", "tee") and (
                _HOME_ARG.search(win) or (rest and _HOME_NEXT_LINE.match("\n" + rest))):
            return True   # the second test is a backslash continuation: the argument starts the next line
    return False


# The devices a redirect can name without leaving anything behind, each whole: `/dev/nullx`, `/dev/null/x`,
# `/dev/null,log` and `/dev/../x` are other files. The name ends where a shell word ends. A quote, a backtick or a
# backslash-newline does not end a word, so each counts only when such an end follows it: `"/dev/null"` is the device,
# `/dev/null"x"` is not.
# debt: matching text cannot tell a closing quote from an opening one, so `/dev/null" x"` and `"/dev/null x"` are taken
# for the device; and a device inside a quoted string that a comma or bracket follows (`run('x >/dev/null', 1)`) is
# still counted, which over-states. Upgrade path: tokenise shell lines instead of matching text.
DEVICE_PATTERN = r"/dev/(?:null|stdout|stderr|tty|fd/[0-9]+)(?=(?:[\"'`]|\\\r?\n)*(?:$|[\s;&|()<>]))"

# A shell redirect to a file that persists: $HOME, ~, or an absolute path that is not a device. The second branch
# takes a `/` straight after the `>`, except where that `>` ends `<word>` (letters, digits, `_`, `-`): the
# `<name>/` placeholder in usage text.
# debt: the pattern cannot tell that placeholder from a real redirect written with no spaces, so `cmd <in>/tmp/x`
# (read `in`, write /tmp/x) is not counted; upgrade path: tokenise shell lines instead of matching text.
_SHELL_REDIRECT = re.compile(
    r">>?(?!/)\s*[\"']?(?:\$HOME|~|(?!%(device)s)/)"
    r"|(?:(?<![\w<-])[\w-]*|(?<=<))>>?(?!%(device)s)/" % {"device": DEVICE_PATTERN})


# The two patterns that only name a home location: alone, off a comment line, they make a file a "mention".
_HOME_PATTERNS = [
    re.compile(r"os\.homedir\(\)|homedir\(\)|expanduser\(|Path\.home\(\)|process\.env\.HOME"),
    re.compile(r"[\"'/]\.(config|cache|local|claude)[\"'/]"),
]
_COMMENT_LINE = re.compile(r"(?m)^[ \t]*(?:#(?!!)|//).*$")
# `.replace(` is a write only in a file that uses pathlib; elsewhere it is nearly always a string's replace.
_PATHLIB = re.compile(r"Path\(|pathlib")

PERSIST_PATTERNS = [
    # node/js
    re.compile(r"\b(writeFileSync|appendFileSync|createWriteStream|copyFileSync|mkdirSync|rmSync)\b"),
    re.compile(r"fs\.(write|append|copy|rename|unlink|rm|mkdir)\w*\("),
    # python
    re.compile(r"\bopen\([^)]{0,%d}['\"][wax]" % _SPAN),
    re.compile(r"\.(write_text|write_bytes|mkdir|touch|unlink|rename)\("),
    re.compile(r"\b(shutil\.(copy|move|rmtree)|os\.(remove|rename|makedirs|mkdir))\b"),
    # shell
    _SHELL_REDIRECT,
    # anywhere: names a home-ish destination
    *_HOME_PATTERNS,
    # python, whatever else the file imports
    re.compile(r"\bos\.replace\("),
]
_WRITE_PATTERNS = [p for p in PERSIST_PATTERNS if p not in _HOME_PATTERNS]

# Extensions alone missed superpowers' own hook, which is the extension-less
# file `hooks/session-start`. Scan anything small and text-shaped instead.
SCRIPT_EXTS = (".js", ".py", ".sh", ".mjs", ".cjs", ".ts", ".bash", ".zsh", ".rb", ".pl")


# ------------------------------------------------------------ writes through a shell variable
# A script sets a variable to a path under a home folder, and the same script or one that sources it writes through it.
# A name assigned in any shell file counts in every one: a collision can over-state, never hide. Comment lines are read too.
_HOME_LITERAL = re.compile(r"\$HOME/|\$\{HOME\}/|~/|\$\{?XDG_[A-Za-z0-9_]*_HOME|/(?:home|Users)/[^/\s<>\"'$:}]+/")
_ASSIGN = re.compile(r"(?<![^\s;&|({`])([A-Za-z_][A-Za-z0-9_]*)=")
_VALUE = re.compile(r"""(?:"[^"]*"?|'[^']*'?|\$\{[^}]*\}?|\$\([^)]*\)?|[^\s;&|()<>"'$]+|\$)*""")
_VAR = r"\"?\$(?:\{([A-Za-z_][A-Za-z0-9_]*)\}|([A-Za-z_][A-Za-z0-9_]*))"
_VAR_ARG = re.compile(_VAR)
_VAR_REDIRECT = re.compile(r">[>|&]?[ \t]*" + _VAR)
# A command is cut here, quotes not tracked: that can cut a quoted argument, which over-states rather than hides.
_PIECE = re.compile(r"\n|;|\|\||&&|(?<![<>])&(?!>)|(?<!>)\|")
_TARGET_CMD = re.compile(r"\b(mkdir|touch|tee|rm|cp|mv)\b")
_ARG = re.compile(r"""(?:"[^"]*"|'[^']*'|[^\s"'])+|["']""")
_REDIR_WORD = re.compile(r"[0-9]*(?:&?>>?[|&]?|<<?<?)")
_SHELL_SHEBANG = re.compile(r"#!.*\b(?:ba|z)?sh\b")


def _is_shell(name, text):
    return name.endswith((".sh", ".bash", ".zsh")) or ("." not in name and bool(_SHELL_SHEBANG.match(text)))


def _home_variables(text):
    """The names this shell text assigns a value holding a home path literal (not one inside a :// URL)."""
    names = set()
    if not _HOME_LITERAL.search(text):
        return names
    for m in _ASSIGN.finditer(text):
        if m.group(1) in names:
            continue
        # debt: a value is read for _SPAN characters on its line; a literal further in is missed.
        value = _VALUE.match(text[m.end():m.end() + _SPAN].partition("\n")[0]).group()
        for lit in _HOME_LITERAL.finditer(value):
            if "://" not in value[:lit.start()].split(" ")[-1]:
                names.add(m.group(1))
                break
    return names


def _variables_written_through(text):
    """The names of the variables this shell text writes through: a redirect's target, every argument of mkdir,
    touch, tee and rm, and the last argument of cp and mv, where it begins $NAME or ${NAME}. Linear in the text."""
    if "$" not in text:
        return set()
    names = {m.group(1) or m.group(2) for m in _VAR_REDIRECT.finditer(text)}
    for piece in _PIECE.split(text.replace("\\\n", " ")):
        cmd = "$" in piece and _TARGET_CMD.search(piece)
        if not cmd:
            continue
        args, skip = [], False
        for token in _ARG.finditer(piece, cmd.end()):
            word = token.group()
            if word.startswith("#"):
                break
            redirect = _REDIR_WORD.match(word)
            if redirect:
                skip = redirect.end() == len(word)   # `2> file`: the next word is the redirect's, not the command's
            elif skip:
                skip = False
            elif not word.startswith("-"):
                args.append(word)
        for word in args[-1:] if cmd.group(1) in ("cp", "mv") else args:
            m = _VAR_ARG.match(word)
            if m:
                names.add(m.group(1) or m.group(2))
    return names


# ------------------------------------------------------------ the walk
def _tier(text):
    """"writes", "mentions" or None, from this file's text alone."""
    if (any(p.search(text) for p in _WRITE_PATTERNS) or _shell_home_write(text)
            or (".replace(" in text and _PATHLIB.search(text))):
        return "writes"
    if any(p.search(text) for p in _HOME_PATTERNS):
        code = _COMMENT_LINE.sub("", text)
        if any(p.search(code) for p in _HOME_PATTERNS):
            return "mentions"
    return None


def persistence_keys(plugin_root, notes=None):
    """The dossier's two keys from one walk: every listed path, and the same paths with their tiers."""
    detail = inventory_persistence_detail(plugin_root, notes)
    return {"persistence_candidates": [e["path"] for e in detail], "persistence_detail": detail}


def inventory_persistence(plugin_root, notes=None):
    return [e["path"] for e in inventory_persistence_detail(plugin_root, notes)]


def inventory_persistence_detail(plugin_root, notes=None):
    first_note = len(notes) if notes is not None else 0
    try:
        return _persistence_walk(plugin_root, notes)
    finally:
        _mark_scan(notes, first_note)


def _persistence_walk(plugin_root, notes):
    tiers, assigned, through = {}, set(), {}
    for dirpath, dirnames, filenames in os.walk(plugin_root, onerror=_walk_error(notes, plugin_root)):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", "__pycache__", "vendor", "benchmarks", "tests", "test")]
        _walk_gaps(notes, dirpath, dirnames, plugin_root)
        for fn in filenames:
            fp = os.path.join(dirpath, fn)
            rel_fp = os.path.relpath(fp, plugin_root)
            if not _within(fp, plugin_root):
                _note(notes, f"{rel_fp}: resolves outside the target tree; not scanned", cause="tool-limit")
                continue
            if not fn.endswith(SCRIPT_EXTS):
                # Keep extension-less files (hooks/session-start and friends),
                # skip obvious non-scripts and anything large.
                if "." in fn or fn.startswith("."):
                    continue
                try:
                    if os.path.getsize(fp) > 200_000:
                        _note(notes, f"{rel_fp}: over 200000 bytes; not scanned", cause="tool-limit")
                        continue
                except OSError:
                    _note(notes, f"{rel_fp}: could not be read; not scanned", cause="tool-limit")
                    continue
            text = read_text(fp, limit=PERSIST_READ_CEILING)
            if text is None:
                _note(notes, f"{rel_fp}: could not be read; not scanned", cause="tool-limit")
                text = ""
            elif len(text) >= PERSIST_READ_CEILING and os.path.getsize(fp) > PERSIST_READ_CEILING:
                _note(notes, f"{rel_fp}: read capped at {PERSIST_READ_CEILING} characters", cause="tool-limit")
            tier = _tier(text)
            if tier:
                tiers[rel_fp] = tier
            if _is_shell(fn, text):
                assigned |= _home_variables(text)
                if tier != "writes":
                    through[rel_fp] = _variables_written_through(text)
    for rel, names in through.items():
        if names & assigned:
            tiers[rel] = "writes"
    return [{"path": p, "tier": tiers[p]} for p in sorted(tiers)]
