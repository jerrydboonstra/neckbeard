#!/usr/bin/env python3
"""The README stays easy to read: a short opening, no dense prose paragraph, links that resolve, detail moved into docs/. Each rule is seen to fail on a bad sample, not only to pass on the README."""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_PARAGRAPH = 500
MAX_OPENING = 300
failures = []


def check(name, ok):
    print(("ok   " if ok else "FAIL ") + name)
    if not ok:
        failures.append(name)


LINK = re.compile(r"!?\[(?:[^\[\]]|\[[^\]]*\])*\]\(([^)\s]*)[^)]*\)")


def is_links_only(text):
    """A badge row or a list of links: nothing but links, separators and a short label is left once the links are removed."""
    rest = re.sub(r"\[!\[[^\]]*\]\([^)]*\)\]\([^)]*\)", "", text)
    rest = LINK.sub("", rest)
    rest = re.sub(r"[\s·|,]+", " ", rest).strip()
    return len(rest) <= 20


def prose_paragraphs(text):
    """The prose paragraphs, in order. A prose paragraph is not a heading, a badge row, a line of links, HTML, a blockquote, a table or a code block. A list item counts as one paragraph."""
    out, block, fenced = [], [], False

    def flush():
        if block:
            para = " ".join(s.strip() for s in block)
            if not is_links_only(para):
                out.append(para)
            block.clear()

    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            flush()
            fenced = not fenced
            continue
        if fenced:
            continue
        s = line.strip()
        if not s:
            flush()
        elif s.startswith(("#", ">", "|", "<")):
            flush()
        elif re.match(r"([-*]|\d+\.)\s", s):
            flush()
            block.append(re.sub(r"^([-*]|\d+\.)\s+", "", s))
        else:
            block.append(s)
    flush()
    return out


def dense(text):
    paras = prose_paragraphs(text)
    long_ = [p for p in paras if len(p) > MAX_PARAGRAPH]
    opening = paras[0] if paras else ""
    return long_, (opening if len(opening) > MAX_OPENING else None)


def broken_links(path):
    bad = []
    for target in LINK.findall(path.read_text()):
        if re.match(r"[a-z][a-z0-9+.-]*:", target) or target.startswith("#") or not target:
            continue
        if not (path.parent / target.split("#")[0]).exists():
            bad.append(target)
    return bad


# The checks seen to fail on bad samples
good = "# t\n\n[![CI](a)](b)\n\n> quote\n\nShort opening.\n\nSecond.\n"
check("a short opening and short paragraphs pass", dense(good) == ([], None))
check("a paragraph over 500 characters fails", len(dense(good + "\n" + "word " * 101)[0]) == 1)
check("an opening over 300 characters fails", dense("# t\n\n" + "word " * 61 + "\n")[1] is not None)
check("a badge row, a line of links, a blockquote, a table and a code block are exempt",
      dense(good + "\nRounds: " + " · ".join("[r%d](x.md#%d)" % (i, i) for i in range(60)) + "\n\n> " + "word " * 120 + "\n\n| a | b |\n|---|---|\n| " + "w " * 300 + " | x |\n\n```\n" + "w " * 300 + "\n```\n") == ([], None))
check("a long list item fails", len(dense(good + "\n- " + "word " * 101)[0]) == 1)
import tempfile
with tempfile.TemporaryDirectory() as tmp:
    t = Path(tmp)
    (t / "here.md").write_text("x")
    (t / "a.md").write_text("[ok](here.md#h) [web](https://x.org/y) [top](#h) [gone](nowhere.md)")
    check("a relative link that does not resolve is reported", broken_links(t / "a.md") == ["nowhere.md"])

# The README itself
readme = ROOT / "README.md"
long_, opening = dense(readme.read_text())
check("no README prose paragraph is over %d characters (%s)" % (MAX_PARAGRAPH, ", ".join(p[:30] for p in long_)), not long_)
check("the README opening is at most %d characters" % MAX_OPENING, opening is None)
check("every relative link in the README resolves (%s)" % ", ".join(broken_links(readme)), not broken_links(readme))
for md in sorted((ROOT / "docs").glob("*.md")):
    check("every relative link in docs/%s resolves" % md.name, not broken_links(md))

# Moved detail is one click from where it was
text = readme.read_text()
for page in ("docs/live-mcp.md", "docs/report-terms.md"):
    check("the README links %s and the file exists" % page, ("](%s" % page) in text and (ROOT / page).is_file())

if failures:
    print("\n%d failed" % len(failures))
    sys.exit(1)
print("\nall passed")
