#!/usr/bin/env python3
"""The byte budget for neckbeard's skill text (tools/skill-budget.txt). Reads the budget, measures each listed file in bytes and every skill description in characters. The guard is seen to bite on an oversize copy."""
import re, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DESC_MAX = 1024
failures = []


def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        failures.append(name)


def description(text):
    """The parsed value of the frontmatter's description: plain, or a folded/literal block (>-, >, |)."""
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    lines = m.group(1).split("\n")
    for i, ln in enumerate(lines):
        if ln.startswith("description:"):
            rest = ln[len("description:"):].strip()
            if rest[:1] in (">", "|"):
                block = []
                for nxt in lines[i + 1:]:
                    if nxt and not nxt.startswith((" ", "\t")):
                        break
                    block.append(nxt.strip())
                return (" " if rest[0] == ">" else "\n").join(b for b in block if b)
            return rest.strip("\"'")
    return None


def problems(root):
    """What passes its line under ROOT, each as 'file: size over line N' (empty when all is within budget)."""
    out = []
    budget = {}
    for raw in (root / "tools" / "skill-budget.txt").read_text().splitlines():
        if raw.strip() and not raw.startswith("#"):
            name, _, n = raw.rpartition(":")
            budget[name.strip()] = int(n)
    for name, line in budget.items():
        if name == "descriptions":
            continue
        size = (root / name).stat().st_size
        if size > line:
            out.append(f"{name}: {size} bytes, over its line of {line}")
    total = 0
    for skill in sorted((root / "skills").glob("*/SKILL.md")):
        d = description(skill.read_text())
        if d is None:
            out.append(f"{skill.relative_to(root)}: no description found")
            continue
        total += len(d)
        if len(d) > DESC_MAX:
            out.append(f"{skill.relative_to(root)}: description {len(d)} characters, over {DESC_MAX}")
    if "descriptions" in budget and total > budget["descriptions"]:
        out.append(f"descriptions: {total} characters, over its line of {budget['descriptions']}")
    unlisted = [str(s.relative_to(root)) for s in (root / "skills").glob("*/SKILL.md") if str(s.relative_to(root)) not in budget]
    out += [f"{u}: a skill with no line in tools/skill-budget.txt" for u in unlisted]
    return out


def tree(skill_text, budget_text):
    d = Path(tempfile.mkdtemp())
    (d / "skills" / "neckbeard").mkdir(parents=True)
    (d / "tools").mkdir()
    (d / "skills" / "neckbeard" / "SKILL.md").write_text(skill_text)
    (d / "tools" / "skill-budget.txt").write_text(budget_text)
    return d


real = problems(ROOT)
check("the repo's skill text is within its budget", not real, "; ".join(real))

# The guard bites: each case is a temp tree, and must name the file, its size and its line.
skill = (ROOT / "skills" / "neckbeard" / "SKILL.md").read_text()
size = len(skill.encode())
desc = description(skill)
check("the parsed description is the folded text, in characters", desc is not None and "\n" not in desc and 0 < len(desc) < DESC_MAX)

ok_budget = f"descriptions: {len(desc)}\nskills/neckbeard/SKILL.md: {size}\n"
check("a tree exactly at its lines passes", not problems(tree(skill, ok_budget)))

over = problems(tree(skill + "x", ok_budget))
check("a SKILL.md one byte over its line fails, naming file, size and line",
      len(over) == 1 and f"skills/neckbeard/SKILL.md: {size + 1} bytes, over its line of {size}" in over[0], repr(over))

fat = re.sub(r"(description: >-\n)", r"\1  " + "word " * 3 + "\n", skill, count=1)
over = problems(tree(fat, ok_budget))
check("a description over its line fails, naming its size and line",
      any(o.startswith("descriptions: ") and f"over its line of {len(desc)}" in o for o in over), repr(over))

long_desc = skill.replace("description: >-\n", "description: >-\n  " + "y" * DESC_MAX + "\n", 1)
over = problems(tree(long_desc, f"descriptions: 99999\nskills/neckbeard/SKILL.md: {len(long_desc.encode())}\n"))
check("a description over 1024 characters fails even under a generous line", any("over 1024" in o for o in over), repr(over))

check("a skill with no line in the budget fails", any("no line" in o for o in problems(tree(skill, f"descriptions: {len(desc)}\n"))))

print("FAILED" if failures else "test_skill_budget: all passed")
sys.exit(1 if failures else 0)
