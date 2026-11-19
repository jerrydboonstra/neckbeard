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


def outside_fences(text):
    """The lines of a Markdown file that are not inside a fenced code block."""
    out, fenced = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
        elif not fenced:
            out.append(line)
    return out


def slugs(path):
    """The anchors GitHub makes for a file's headings: lowercase, punctuation dropped except - and _, spaces to -, a -1, -2 suffix for repeats."""
    seen, out = {}, set()
    for line in outside_fences(path.read_text()):
        m = re.match(r"#{1,6}\s+(.*?)\s*#*\s*$", line)
        if not m:
            continue
        title = LINK.sub(lambda k: re.match(r"!?\[(.*)\]", k.group(0)).group(1), m.group(1))
        slug = re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")
        n = seen.get(slug, 0)
        seen[slug] = n + 1
        out.add(slug if n == 0 else "%s-%d" % (slug, n))
    return out


def broken_links(path):
    """The relative links in a file (outside code blocks) whose file is missing or whose #fragment matches no heading in it."""
    bad = []
    for target in LINK.findall("\n".join(outside_fences(path.read_text()))):
        if re.match(r"[a-z][a-z0-9+.-]*:", target) or not target:
            continue
        name, _, frag = target.partition("#")
        dest = path if not name else path.parent / name
        if not dest.exists() or (frag and (dest.suffix != ".md" or frag not in slugs(dest))):
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
    (t / "a.md").write_text("[ok](here.md) [web](https://x.org/y) [gone](nowhere.md)")
    check("a relative link that does not resolve is reported", broken_links(t / "a.md") == ["nowhere.md"])
    (t / "h.md").write_text("# Top\n\n## Try it: three lines, then the `report`\n\n## Again\n\n## Again\n\n```\n# not a heading\n```\n\n[self](#again-1) [bad](#nope) [other](a.md#x)\n")
    (t / "b.md").write_text("[ok](h.md#try-it-three-lines-then-the-report) [rep](h.md#again-1) [gone](h.md#renamed) [nofile](zz.md#top) [code](h.md#not-a-heading)\n```\n[skip](nowhere.md)\n```\n")
    check("a fragment that matches no heading in an existing file is reported (and slugs, repeats and code fences are read as GitHub does)",
          broken_links(t / "b.md") == ["h.md#renamed", "zz.md#top", "h.md#not-a-heading"])
    check("a bare #fragment is checked against the file's own headings", broken_links(t / "h.md") == ["#nope", "a.md#x"])

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
