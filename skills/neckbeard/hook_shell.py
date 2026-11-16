#!/usr/bin/env python3
"""Reads a shell hook script's own text and says what an ordinary script of that shape prints to stdout, for hooks that
build their line at run time (imagegen's `echo "imagegen doctor: $failed missing; ..."`). It reads; it never runs the script
and never follows what the script calls. Rule of the design: when in doubt, stop the trace, so a stopped trace is the old
"unresolved", never a false all-clear. What it cannot see (code inside $(...) and backticks, the programs the script runs)
is a named limit in SECURITY.md and on the report line. Stdlib only.

trace_shell_hook(text) -> {"template": [lines], "writes": [items], "at_least": bool, "bytes": literal template bytes} when every statement passes, or
{"stop": (line, why)} on the first that does not. A "…" in a template line stands for text known only at run time.
"""
import re

BLANK = "…"
KEEP_WORDS = {"if", "then", "elif", "else", "while", "until", "do", "!"}
OPEN_WORDS = {"if", "while", "until", "{", "("}
CLOSE_WORDS = {"fi", "done", "}", ")"}
STOP_COMMANDS = {"export", "readonly", "set", "shift", "unset", "eval", "source", ".", "exec", "for", "case", "esac", "function", "in", "select"}
# Commands whose path operand is a file read; a file's text is not a run-time blank.
PROGRAM_CMDS = {"sed", "awk", "grep", "jq"}
FILE_CMDS = {"cat", "head", "tail", "cut", "sort", "uniq", "base64", "od", "xxd", "nl", "tac", "paste"} | PROGRAM_CMDS
# Flags whose argument belongs to the flag; for sed and grep and jq and awk. -e and -f stand in for the program word.
ARG_FLAGS = {"sed": ("ef", "ef"), "grep": ("ef", "ef"), "awk": ("fvF", "f"), "jq": ("f", "f")}
JQ_LONG_ARGS = {"--arg": 2, "--argjson": 2, "--slurpfile": 2, "--rawfile": 2, "--args": 0}
ASSIGN_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)(\[[^\]]*\])?\+?=")
REDIR_RE = re.compile(r"^(\d*|&)(>>|>&|>|<<<|<<|<&|<)(.*)$", re.S)
VAR_REF_RE = re.compile(r"\$\{?([A-Za-z_][A-Za-z0-9_]*)")


class Stop(Exception):
    def __init__(self, line, why):
        super().__init__(why)
        self.line, self.why = line, why


# ---------------------------------------------------------------- reading the text into words

def _skip_balanced(s, i, open_c, close_c, line):
    """s[i] is just after an opening bracket; the index after its match, honouring quotes. Returns (index, lines crossed)."""
    depth, n = 1, 0
    while i < len(s):
        c = s[i]
        if c == "\n":
            n += 1
        elif c == "\\":
            i += 1
            if i < len(s) and s[i] == "\n":
                n += 1
        elif c == "'":
            j = s.find("'", i + 1)
            if j < 0:
                raise Stop(line + n, "an unbalanced quote")
            n += s.count("\n", i, j)
            i = j
        elif c == '"':
            j, k = _skip_dq(s, i + 1, line + n)
            n += k
            i = j - 1
        elif c == "`":
            j = s.find("`", i + 1)
            if j < 0:
                raise Stop(line + n, "an unbalanced quote")
            n += s.count("\n", i, j)
            i = j
        elif c == open_c:
            depth += 1
        elif c == close_c:
            depth -= 1
            if depth == 0:
                return i + 1, n
        i += 1
    raise Stop(line, "an unbalanced quote or bracket")


def _skip_dq(s, i, line):
    """s[i] is just after an opening double quote; the index after the closing one, with the lines crossed."""
    n = 0
    while i < len(s):
        c = s[i]
        if c == "\n":
            n += 1
        elif c == "\\":
            i += 1
        elif c == '"':
            return i + 1, n
        elif c == "`":
            j = s.find("`", i + 1)
            if j < 0:
                break
            n += s.count("\n", i, j)
            i = j
        elif c == "$" and i + 1 < len(s) and s[i + 1] in "({":
            close = ")" if s[i + 1] == "(" else "}"
            j, k = _skip_balanced(s, i + 2, s[i + 1], close, line + n)
            n += k
            i = j - 1
        i += 1
    raise Stop(line, "an unbalanced quote")


def tokens(s):
    """[(kind, text, line)]: kind is word, ; (a statement break: newline, ;, && or ||), |, &, ;;, ( or ). Comments and
    backslash-newlines are gone. A quote, $(...), ${...} or backtick left open raises Stop."""
    out, i, line, n = [], 0, 1, len(s)
    while i < n:
        c = s[i]
        if c == "\n":
            out.append((";", "\n", line))
            line += 1
            i += 1
        elif c in " \t\r":
            i += 1
        elif c == "\\" and s[i + 1:i + 2] == "\n":
            i += 2
            line += 1
        elif c == "#":
            while i < n and s[i] != "\n":
                i += 1
        elif c == ";":
            if s[i + 1:i + 2] == ";":
                out.append((";;", ";;", line))
                i += 2
            else:
                out.append((";", ";", line))
                i += 1
        elif c == "&":
            if s[i + 1:i + 2] == "&":
                out.append((";", "&&", line))
                i += 2
            elif s[i + 1:i + 2] == ">":
                i, w, k = _word(s, i, line)
                out.append(("word", w, line))
                line += k
            else:
                out.append(("&", "&", line))
                i += 1
        elif c == "|":
            if s[i + 1:i + 2] == "|":
                out.append((";", "||", line))
                i += 2
            else:
                out.append(("|", "|", line))
                i += 1
        elif c == "(":
            out.append(("(", "(", line))
            i += 1
        elif c == ")":
            out.append((")", ")", line))
            i += 1
        else:
            start = line
            i, w, k = _word(s, i, line)
            out.append(("word", w, start))
            line += k
    return out


def _word(s, i, line):
    """The word starting at s[i]: (index after, raw text, lines crossed). Raw text keeps its quotes."""
    start, n = i, 0
    while i < len(s):
        c = s[i]
        if c in " \t\r\n;|&()":
            if c == "(" and i > start and ASSIGN_RE.match(s[start:i] + "(") is None and s[i - 1] == "=":
                pass
            if c == "(" and i > start and s[start:i].endswith("=") and ASSIGN_RE.match(s[start:i]):
                j, k = _skip_balanced(s, i + 1, "(", ")", line + n)
                n += k
                i = j
                continue
            if c == "&" and s[i - 1:i] in (">", "<") and i > start:
                i += 1
                continue
            if c == "(" and i > start and s[i - 1] in "<>":
                raise Stop(line + n, "uses process substitution")
            if c == "(" and i > start:
                raise Stop(line + n, "defines a function")
            break
        if c == "\\":
            if s[i + 1:i + 2] == "\n":
                n += 1
                i += 2
                continue
            i += 2
            continue
        if c == "'":
            j = s.find("'", i + 1)
            if j < 0:
                raise Stop(line + n, "an unbalanced quote")
            n += s.count("\n", i, j)
            i = j + 1
            continue
        if c == '"':
            j, k = _skip_dq(s, i + 1, line + n)
            n += k
            i = j
            continue
        if c == "`":
            j = s.find("`", i + 1)
            if j < 0:
                raise Stop(line + n, "an unbalanced quote")
            n += s.count("\n", i, j)
            i = j + 1
            continue
        if c == "$" and i + 1 < len(s) and s[i + 1] in "({":
            close = ")" if s[i + 1] == "(" else "}"
            j, k = _skip_balanced(s, i + 2, s[i + 1], close, line + n)
            n += k
            i = j
            continue
        i += 1
    if i == start:
        i += 1   # a character no rule takes: never loop
    return i, s[start:i], n


# ---------------------------------------------------------------- what a word prints

def expand(word, glob=True):
    """The template text of one word: literal text stays, anything known only at run time becomes BLANK, outer quotes go."""
    out, i, n = [], 0, len(word)
    globbed = False

    def put(x):
        if x == BLANK and out and out[-1] == BLANK:
            return
        out.append(x)
    if glob and word.startswith("~"):
        globbed = True
    while i < n:
        c = word[i]
        if c == "'":
            j = word.find("'", i + 1)
            put(word[i + 1:j if j >= 0 else n])
            i = (j if j >= 0 else n) + 1
        elif c == '"':
            i += 1
            while i < n and word[i] != '"':
                if word[i] == "\\" and i + 1 < n:
                    put(word[i + 1] if word[i + 1] in '"\\$`' else word[i:i + 2])
                    i += 2
                elif word[i] == "$" or word[i] == "`":
                    i = _expansion(word, i, put)
                else:
                    put(word[i])
                    i += 1
            i += 1
        elif c == "\\" and i + 1 < n:
            put(word[i + 1])
            i += 2
        elif c in "$`":
            i = _expansion(word, i, put)
        elif glob and c in "*?[":
            globbed = True   # the shell replaces the whole word with whatever matches
            put(c)
            i += 1
        elif glob and c == "{" and re.search(r"\{[^{}]*(,|\.\.)[^{}]*\}", word[i:]):
            globbed = True
            i = word.find("}", i) + 1
        else:
            put(c)
            i += 1
    return BLANK if globbed else "".join(out)


def _expansion(w, i, put):
    """w[i] is $ or a backtick: skip the whole expansion, put a blank; the index after."""
    if w[i] == "`":
        j = w.find("`", i + 1)
        put(BLANK)
        return (j if j >= 0 else len(w)) + 1
    nxt = w[i + 1:i + 2]
    if nxt in ("(", "{"):
        j, _ = _skip_balanced(w, i + 2, nxt, ")" if nxt == "(" else "}", 0)
        put(BLANK)
        return j
    m = re.match(r"\$([A-Za-z_][A-Za-z0-9_]*|[0-9@*#?$!-])", w[i:])
    if m:
        put(BLANK)
        return i + m.end()
    put("$")
    return i + 1


def _printf_lines(fmt_word, nargs):
    """printf's template lines from its format word, and whether extra arguments repeat the format."""
    raw = expand(fmt_word)
    conv = 0
    out, i = [], 0
    while i < len(raw):
        c = raw[i]
        if c == "%" and i + 1 < len(raw):
            if raw[i + 1] == "%":
                out.append("%")
                i += 2
                continue
            m = re.match(r"%[-+ #0]*[0-9*]*(\.[0-9*]+)?[a-zA-Z]", raw[i:])
            if m:
                conv += 1
                out.append(BLANK)
                i += m.end()
                continue
        if c == "\\" and i + 1 < len(raw):
            e = raw[i + 1]
            out.append({"n": "\n", "t": "\t", "\\": "\\", '"': '"'}.get(e, "\\" + e))
            i += 2
            continue
        out.append(c)
        i += 1
    text = re.sub(BLANK + "+", BLANK, "".join(out))
    return text, bool(conv and nargs > conv)


def _lines(text):
    """A printed text as template lines: each \\n ends a line; a text with no newline is one line."""
    parts = text.split("\n")
    if parts and parts[-1] == "":
        parts.pop()
    return parts


# ---------------------------------------------------------------- file-read check (5b)

def _segments(value):
    """The bodies of every $(...) and backtick expression in a raw word, outermost only."""
    out, i = [], 0
    while i < len(value):
        c = value[i]
        if c == "'":
            j = value.find("'", i + 1)
            i = (j if j >= 0 else len(value)) + 1
        elif c == "\\":
            i += 2
        elif c == "$" and value[i + 1:i + 2] == "(":
            try:
                j, _ = _skip_balanced(value, i + 2, "(", ")", 0)
            except Stop:
                j = len(value)
            out.append(value[i + 2:j - 1])
            i = j
        elif c == "`":
            j = value.find("`", i + 1)
            j = len(value) if j < 0 else j
            out.append(value[i + 1:j])
            i = j + 1
        else:
            i += 1
    return out


def _reads_file(seg):
    """True when the command text of one $(...) or backtick reads a file: a file command given a path operand, or a < redirect."""
    if re.match(r"\s*<", seg):
        return True
    try:
        toks = tokens(seg)
    except Stop:
        return True   # cannot read it: assume it does
    cmds, cur = [], []
    for kind, text, _ in toks:
        if kind == "word":
            cur.append(text)
        else:
            cmds.append(cur)
            cur = []
    cmds.append(cur)
    for words in cmds:
        if any(_reads_file(s) for w in words for s in _segments(w)):   # an assignment's own $(...) counts too
            return True
        while words and ASSIGN_RE.match(words[0]):
            words = words[1:]
        if not words:
            continue
        if any(re.match(r"^\d*<[^<]", w) or w == "<" for w in words[1:]):
            return True
        cmd = words[0].rsplit("/", 1)[-1]
        if cmd in FILE_CMDS and _has_path(cmd, words[1:]):
            return True
        if any(_reads_file(s) for w in words for s in _segments(w)):
            return True
    return False


def _has_path(cmd, args):
    if cmd not in PROGRAM_CMDS:
        return any(a != "-" and not a.startswith("-") for a in args)
    short, prog_flags = ARG_FLAGS[cmd]
    has_prog_flag, nonflag, i = False, [], 0
    while i < len(args):
        a = args[i]
        if cmd == "jq" and a in JQ_LONG_ARGS:
            i += 1 + JQ_LONG_ARGS[a]
            continue
        if a.startswith("--") or a == "-":
            if a != "-":
                i += 1
                continue
        if a.startswith("-") and a != "-":
            for k, ch in enumerate(a[1:], 1):
                if ch in short:
                    if ch in prog_flags:
                        has_prog_flag = True
                    if k == len(a) - 1:
                        i += 1   # its argument is the next word
                    break
            i += 1
            continue
        nonflag.append(a)
        i += 1
    return bool(nonflag) if has_prog_flag else len(nonflag) > 1


# ---------------------------------------------------------------- the trace

def trace_shell_hook(text):
    try:
        return _trace(text)
    except Stop as s:
        return {"stop": (s.line, s.why)}
    except Exception:   # deep nesting (RecursionError) or anything else the reader cannot take apart: an unknown, never a trace
        return {"stop": (1, "could not be read by the trace")}


def _statements(toks):
    """[(line, [token, ...])] split at statement breaks; a ( or ) is its own token. A pipe, & or ;; stops the trace."""
    out, cur = [], []
    for kind, text, line in toks:
        if kind == ";":
            if cur:
                out.append(cur)
            cur = []
        else:
            cur.append((kind, text, line))
    if cur:
        out.append(cur)
    return out


def _trace(text):
    template, writes, at_least = [], [], False
    file_vars = set()
    frames = []          # open groups: (word, len(template) at open, line)
    last = None          # (line, ok) of the latest statement that is not a bare keyword
    for stmt in _statements(tokens(text)):
        line = stmt[0][2]
        kinds = {k for k, _, _ in stmt}
        if "|" in kinds:
            raise Stop(line, "uses a pipe, whose output may reach Claude")
        if "&" in kinds:
            raise Stop(line, "runs a command in the background")
        if ";;" in kinds:
            raise Stop(line, "uses case")
        words = []
        for k, w, ln in stmt:
            words.append(w if k == "word" else k)
        # leading keywords, opening the frames they open
        while words and words[0] in KEEP_WORDS | {"{", "("}:
            if words[0] in OPEN_WORDS:
                frames.append((words[0], len(template), line))
            words = words[1:]
        for w in words:
            if "$((" in w or re.search(r"\$\{[^}]*\?|\$\{!", w) or re.search(r"(^|[^\\])[<>]\(", w):
                raise Stop(line, "uses an expansion that can exit 2 or print through another process")
        words, redirs = _split_redirects(words, line)
        if not words:
            _close(frames, words, redirs, template, line)
            continue
        head = words[0]
        if head in CLOSE_WORDS and len(words) == 1:
            _close_frame(head, frames, redirs, template, writes, line)
            continue
        ok_exit = False
        silent = True
        stmt_template = None
        stmt_lines = []
        if ASSIGN_RE.match(head) or head == "local":
            names = words[1:] if head == "local" else words
            if head == "local" and not names:
                pass
            for w in names:
                m = ASSIGN_RE.match(w)
                if not m:
                    raise Stop(line, f"runs `{_cmd_name(w)}`, whose output may reach Claude" if names is words else "uses local with something other than assignments")
                if re.search(r"[A-Z]", m.group(1)):
                    raise Stop(line, f"assigns {m.group(1)}, which can change how later commands run")
                value = w[m.end():]
                refs = set(VAR_REF_RE.findall(value))
                if (refs & file_vars) or any(_reads_file(s) for s in _segments(value)):
                    file_vars.add(m.group(1))
        elif head in ("[", "[[", "test", ":", "true", "false"):
            pass
        elif head in ("exit", "return"):
            if not (len(words) == 2 and words[1] in ("0", "1")):
                raise Stop(line, f"uses `{head}` with something other than a literal 0 or 1, which can exit 2")
            ok_exit = head == "exit"
        elif head == "cd":
            if len(words) != 2 or words[1].startswith("-"):
                raise Stop(line, "uses cd with a flag or no single directory")
        elif head in ("mkdir", "touch", "rm"):
            allowed = {"mkdir": ("-p",), "touch": (), "rm": ("-f", "-r", "-rf", "-fr")}[head]
            for w in words[1:]:
                if w.startswith("-") and w not in allowed:
                    raise Stop(line, f"runs `{head} {w}`, a flag the trace does not allow")
            stmt_template = " ".join(expand(w) for w in words)
        elif head in ("echo", "printf"):
            stmt_lines, extra = _print_template(head, words, file_vars, line)
            silent = False
            at_least = at_least or extra
        elif head in STOP_COMMANDS or head == "function":
            raise Stop(line, _stop_reason(head))
        else:
            raise Stop(line, f"runs `{_cmd_name(head)}`, whose output may reach Claude")
        # redirects of this statement
        to_stderr = False
        for fd, op, target in redirs:
            if op in (">&", "1>&") and target == "2" and fd in ("", "1"):
                to_stderr = True
            elif fd == "2" and op in (">", ">>"):
                if target != "/dev/null":
                    writes.append(f"{stmt_template or ' '.join(expand(w) for w in words)} 2> {BLANK}")
            elif fd in ("", "1") and op in (">", ">>"):
                if not silent:
                    raise Stop(line, f"uses `{head}` to write to a file, which could put text in a project file")
                if target != "/dev/null":
                    base = stmt_template or " ".join(expand(w) for w in words)
                    writes.append(f"{base} {op} {BLANK}")
            else:
                raise Stop(line, f"uses the redirect `{fd}{op}{target}`, which can send output to Claude")
        if stmt_lines and not to_stderr:
            template.extend(stmt_lines)
        if stmt_template and head in ("mkdir", "touch", "rm"):
            writes.append(stmt_template)
        if words and head not in CLOSE_WORDS:
            last = (line, ok_exit and not frames)
    if frames:
        raise Stop(frames[-1][2], "opens a group or loop that is never closed")
    if last is None or not last[1]:
        raise Stop(last[0] if last else 1, "does not end with a top-level `exit 0` or `exit 1`, so its exit status is not known")
    lit = sum(len(re.sub(BLANK, "", t).encode("utf-8")) for t in template)
    return {"template": template, "writes": writes, "at_least": at_least, "bytes": lit}


def _cmd_name(w):
    return re.sub(r"\s.*", "", expand(w, glob=False))[:40] or "?"


def _stop_reason(head):
    return {
        "export": "uses export, which can change how later commands run", "readonly": "uses readonly",
        "set": "uses set, which can change how the script runs", "shift": "uses shift", "unset": "uses unset",
        "eval": "uses eval", "source": "sources another file", ".": "sources another file", "exec": "uses exec",
        "for": "uses a for loop", "case": "uses case", "esac": "uses case", "function": "defines a function",
    }.get(head, f"uses `{head}`")


def _split_redirects(words, line):
    """(words without redirects, [(fd, op, target)]). A redirect word is taken whole or with the next word as its target."""
    kept, redirs, i = [], [], 0
    while i < len(words):
        w = words[i]
        m = REDIR_RE.match(w) if not w[:1] in "'\"" else None
        if m and (w[0] in "<>&" or w[0].isdigit()):
            fd, op, rest = m.groups()
            if fd == "&" or op in ("<<", "<<<", "<", "<&"):
                raise Stop(line, "uses a redirect or heredoc the trace does not follow")
            if op == ">&":
                redirs.append((fd, op, rest))   # the redirect loop in _trace keeps only >&2 and 1>&2 and stops on any other
            else:
                if fd not in ("", "1", "2"):
                    raise Stop(line, f"uses the redirect on file descriptor {fd}, which the trace does not follow")
                if not rest:
                    i += 1
                    if i >= len(words):
                        raise Stop(line, "has a redirect with no target")
                    rest = words[i]
                redirs.append((fd, op, rest if rest.startswith("/dev/null") else expand(rest, glob=False) and rest))
            i += 1
            continue
        kept.append(w)
        i += 1
    return kept, redirs


def _print_template(head, words, file_vars, line):
    args = words[1:]
    for w in args:
        if (set(VAR_REF_RE.findall(w)) & file_vars) or any(_reads_file(s) for s in _segments(w)):
            raise Stop(line, f"prints text read from a file with `{head}`, which resolve_injected_text should name")
    if any("$'" in a or re.search(r"\\[xuU0-7]", a) for a in args):
        raise Stop(line, f"prints with an escape (\\x, \\u, octal or $'...') the trace does not decode")
    if head == "echo":
        flags = []
        while args and re.fullmatch(r"-[neE]+", args[0]):
            flags.append(args.pop(0))
        text = " ".join(expand(a) for a in args)
        text = re.sub(BLANK + "+", BLANK, text)
        if "\\" in text and not any("e" in f for f in flags):
            raise Stop(line, "prints a backslash with echo, which different shells print differently")
        if any("e" in f for f in flags):
            text = text.replace("\\n", "\n")
        return _lines(text), False
    if not args:
        return [], False
    if args[0].startswith("-"):
        raise Stop(line, "uses a printf flag")
    text, extra = _printf_lines(args[0], len(args) - 1)
    return _lines(text), extra


def _close_frame(word, frames, redirs, template, writes, line):
    if not frames:
        raise Stop(line, f"has a stray `{word}`")
    opener, start, _ = frames.pop()
    want = {"fi": "if", "done": ("while", "until"), "}": "{", ")": "("}[word]
    if opener not in (want if isinstance(want, tuple) else (want,)):
        raise Stop(line, f"closes a `{opener}` with `{word}`")
    drop = False
    for fd, op, target in redirs:
        if op == ">&" and target == "2" and fd in ("", "1"):
            drop = True
        elif fd == "2" and op in (">", ">>"):
            pass
        elif fd in ("", "1") and op in (">", ">>"):
            # a group's output to a file stops the trace whether or not it prints: it writes
            raise Stop(line, "redirects a group's output to a file, which could put text in a project file")
        else:
            raise Stop(line, f"uses the redirect `{fd}{op}{target}` on a group, which can send output to Claude")
    if drop:
        del template[start:]


def _close(frames, words, redirs, template, line):
    if redirs:
        raise Stop(line, "has a redirect with no command")
