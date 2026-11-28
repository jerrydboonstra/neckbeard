#!/usr/bin/env python3
"""The persistence scan of neckbeard's inventory: which files under a target may write something that persists. Every rule
about what counts as a write, and what a file merely names, lives here. Moved out of inventory_hooks.py, which was at the
size cap; inventory_hooks imports each name back, so `inventory.<name>` still resolves. Stdlib only.
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


PERSIST_PATTERNS = [
    # node/js
    re.compile(r"\b(writeFileSync|appendFileSync|createWriteStream|copyFileSync|mkdirSync|rmSync)\b"),
    re.compile(r"fs\.(write|append|copy|rename|unlink|rm|mkdir)\w*\("),
    # python
    re.compile(r"\bopen\([^)]{0,%d}['\"][wax]" % _SPAN),
    re.compile(r"\.(write_text|write_bytes|mkdir|touch|unlink|rename|replace)\("),
    re.compile(r"\b(shutil\.(copy|move|rmtree)|os\.(remove|rename|makedirs|mkdir))\b"),
    # shell
    _SHELL_REDIRECT,
    # anywhere: names a home-ish destination
    re.compile(r"os\.homedir\(\)|homedir\(\)|expanduser\(|Path\.home\(\)|process\.env\.HOME"),
    re.compile(r"[\"'/]\.(config|cache|local|claude)[\"'/]"),
]

# Extensions alone missed superpowers' own hook, which is the extension-less
# file `hooks/session-start`. Scan anything small and text-shaped instead.
SCRIPT_EXTS = (".js", ".py", ".sh", ".mjs", ".cjs", ".ts", ".bash", ".zsh", ".rb", ".pl")


def inventory_persistence(plugin_root, notes=None):
    first_note = len(notes) if notes is not None else 0
    try:
        return _persistence_walk(plugin_root, notes)
    finally:
        _mark_scan(notes, first_note)


def _persistence_walk(plugin_root, notes):
    hits = []
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
            for pat in PERSIST_PATTERNS:
                if pat.search(text):
                    hits.append(os.path.relpath(fp, plugin_root))
                    break
            else:
                if _shell_home_write(text):
                    hits.append(os.path.relpath(fp, plugin_root))
    return sorted(set(hits))
