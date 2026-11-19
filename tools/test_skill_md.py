#!/usr/bin/env python3
"""skills/neckbeard/SKILL.md against the tools its report depends on (skill-md-2-0): Step 2 is the owner's text and stays
byte for byte; Step 3 follows the 2.0 order and calls tools/vet in session mode; the verdict list and the plain template's Key
carry the marks the tools themselves use. The tools' constants are imported, never parsed out of their printed reports.

    python3 tools/test_skill_md.py
"""
import hashlib, importlib.machinery, importlib.util, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SKILL = open(os.path.join(ROOT, "skills", "neckbeard", "SKILL.md"), encoding="utf-8").read()
failures = []


def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        failures.append(name)


def load(name):   # the tools have no .py suffix
    path = os.path.join(HERE, name)
    spec = importlib.util.spec_from_loader(name, importlib.machinery.SourceFileLoader(name, path))
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, HERE)
    spec.loader.exec_module(mod)
    return mod


def source(name):
    return open(os.path.join(HERE, name), encoding="utf-8").read()


def section(text, start, end):
    a = text.index(start)
    return text[a:text.index(end, a + 1)] if end else text[a:]


# 1. Step 2 stays as the owner wrote it ("12a"): from its "## Step 2" line through the blank line before "## Step 3".
# The expected hash is that of the text at 0ed058b9c33a. A guard: green before the rewrite and after it.
STEP2_SHA256 = "6f9675b47335449c12401c22cf066f46b67f8b398efdac8eb99ef181236e5bc5"
step2 = section(SKILL, "## Step 2", "## Step 3")
check("Step 2's text is byte for byte the text at 0ed058b9c33a", hashlib.sha256(step2.encode("utf-8")).hexdigest() == STEP2_SHA256,
      hashlib.sha256(step2.encode("utf-8")).hexdigest())
guard = SKILL.replace("sort it into exactly one bucket", "sort it into one bucket")
check("the Step 2 guard bites: one word changed inside Step 2 changes the hash",
      hashlib.sha256(section(guard, "## Step 2", "## Step 3").encode("utf-8")).hexdigest() != STEP2_SHA256)

# 2. Step 3 follows the 2.0 order and calls tools/vet in session mode
step3 = section(SKILL, "## Step 3", "## Step 4")
heads = ["How it affects you", "What it adds", "Where it takes a position"]
at = [step3.find(h) for h in heads]
check("Step 3 names the three 2.0 layer headings, in order", all(i >= 0 for i in at) and at == sorted(at), repr(at))
call = [l for l in step3.split("\n") if "tools/vet" in l and "--dossier" in l and "--answers" in l and "--prose" in l]
check("Step 3 gives the `tools/vet ... --dossier ... --answers ... --prose ...` call", bool(call))
check('no line of SKILL.md is exactly "## ⚡ At a glance"', "## ⚡ At a glance" not in SKILL.split("\n"))
check("path A runs tools/vet itself, as the bash script it is, not through python3", "python3 <base>/../../tools/vet" not in step3 and "`<base>/../../tools/vet <target>" in step3)
check("Step 1 writes the dossier to a file beside the report (inventory's --out, <stem>.dossier.json)",
      "--out" in section(SKILL, "## Step 1", "## Step 2") and ".dossier.json" in section(SKILL, "## Step 1", "## Step 2"))
check("Step 3 points at tools/rule-units and tools/vet-units.md for the units and the answer fields",
      "tools/rule-units" in step3 and "vet-units.md" in step3)
check("Step 3 gives a conflict in units-confirm's form (quote, reader_rule, held_in, hard_stop)",
      all(w in step3 for w in ("quote", "reader_rule", "held_in", "hard_stop")))
check("Step 3 names the plain path for a skill folder with no tools/ beside it, and says the colours are the model's",
      "plain skill folder" in step3 and "model's" in step3)

# 3. the verdict list equals tools/fit's table; the plain template's Key lists exactly the marks the tools use
fit = load("fit")
para = next((p for p in re.split(r"\n\s*\n", step3) if p.startswith("**Verdict**")), "")
flat = " ".join(para.split())
listed = flat.split("):", 1)[-1].split(". ", 1)[0] if "):" in flat else flat.split(":", 1)[-1].split(". ", 1)[0]
pairs = {tuple(item.strip().split(" ", 1)) for item in listed.split(" · ") if item.strip()}
want = {(mark, name) for name, mark in fit.VERDICT_MARK.items()}
check("the verdict list equals tools/fit's verdict table (mark and name)", pairs == want, f"got {sorted(pairs)}, want {sorted(want)}")
after = flat.split(". ", 1)[-1]
check("the sentence after the verdict list names the two verdicts the carrying cost decides between, not colours",
      "\U0001F7E8 COPY RULES, SKIP PLUGIN" in after and "\U0001F7E9 INSTALL" in after, after)

CARD_MARKS = "⛔\U0001F501\U0001F195\U0001F5D1"   # the "How its rules sorted" table's marks: conflicts, covered, new, dropped
fit_src = source("fit")
check("the card marks the Key explains are still the ones tools/fit prints",
      all(ch in fit_src or "\\U%08X" % ord(ch) in fit_src or "\\u%04X" % ord(ch) in fit_src.upper() for ch in CARD_MARKS))
summary = load("summary")
summary_marks = {summary.G, summary.Y, summary.O, summary.R}   # tools/summary's colours, imported
check("tools/summary's four colours are the four judgement colours", summary_marks == set("\U0001F7E9\U0001F7E8\U0001F7E7\U0001F7E5"), repr(summary_marks))
part1 = load("part1")
union = set(fit.VERDICT_MARK.values()) | {fit.RED, fit.ORANGE, fit.GREEN, fit.WHITE, fit.BLACK, fit.STAR} | set(CARD_MARKS) | summary_marks | set(part1.MARKER.values())
key = next((p for p in re.split(r"\n\s*\n", step3) if p.startswith("**Key:**")), "")
if not key:   # the Key sits inside the template's code fence, after a blank line
    m = re.search(r"\*\*Key:\*\*.*?(?=\n```|\n\n)", step3, re.S)
    key = m.group(0) if m else ""
marks = {c for c in key if unicodedata.category(c) == "So" and c != "️"}
check("the plain template's Key lists exactly the union of the marks tools/fit, tools/summary and the read markers use",
      marks == union, f"missing {sorted(union - marks)}, extra {sorted(marks - union)}")

# 4. the plain template: sections, never cards, and nothing that says it was written by code
template = step3[step3.find("```"):]
check("guard (green before the rewrite and after): the plain template holds no <details> card", "<details" not in template)
check("guard (green before the rewrite and after): no layer label in the plain template says 'written by code'",
      not re.search(r"\*\*[123] · .*written by code", template))

if failures:
    print(f"test_skill_md: {len(failures)} failed")
    sys.exit(1)
print("test_skill_md: all passed")
