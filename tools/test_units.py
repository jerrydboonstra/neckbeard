#!/usr/bin/env python3
"""tools/rule-units and tools/units-verdict, the units prototype (verdict-prototype-units).

    python3 tools/test_units.py
"""
import json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
fails = 0


def chk(name, ok, detail=""):
    global fails
    fails += not ok
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + ("" if ok else f": {detail}"))


def run(tool, *args):
    r = subprocess.run([sys.executable, os.path.join(HERE, tool), *args], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


d = tempfile.mkdtemp()
J = lambda name, obj: (json.dump(obj, open(os.path.join(d, name), "w")), os.path.join(d, name))[1]

# rule-units
skill = "---\nname: s\ndescription: d\n---\n\nIntro text.\n\n## One\n\nRule one.\n\n```\n# not a heading\n```\n\n## Empty\n\n### Two\n\nRule two.\n"
dossier = J("dossier.json", {"target": {"skills": [{"source": "skills/s/SKILL.md", "text": skill,
                                                  "companion_files": [{"path": "skills/s/roles/w.md", "text": "# W\n\nRole text.\n"}]}],
                                       "commands": [{"source": "commands/c.md", "text": "Run it.\n"}], "agents": [], "rule_files": []}})
code, out = run("rule-units", dossier, os.path.join(d, "units.json"))
units = json.load(open(os.path.join(d, "units.json")))["units"]
chk("rule-units: exit 0", code == 0, out)
chk("rule-units: sections split at headings, frontmatter and empty sections left out, a # in a code fence kept",
    [(u["file"], u["heading"]) for u in units] == [("skills/s/SKILL.md", "(top)"), ("skills/s/SKILL.md", "One"), ("skills/s/SKILL.md", "Two"),
                                                   ("skills/s/roles/w.md", "W"), ("commands/c.md", "(top)")]
    and "# not a heading" in units[1]["text"], [(u["file"], u["heading"]) for u in units])
chk("rule-units: ids are u1.. in order", [u["id"] for u in units] == ["u1", "u2", "u3", "u4", "u5"], units)
U = os.path.join(d, "units.json")

# units-verdict: the verdict rule, from two answers per unit
C = [{"quote": "q", "reader_rule": "r"}]
def answers(name, pairs):
    return J(name, {"answers": [{"id": f"u{i + 1}", "skill": k, "rules": "none" if r == "conflict" else r,
                                 "conflicts": C if r == "conflict" else [], "why": "x"} for i, (k, r) in enumerate(pairs)]})
D = ("drop", "none")
cases = [
    ([("keep", "none"), D, D, ("drop", "duplicate"), D], "INSTALL"),
    ([("keep", "new-standing"), D, D, D, D], "INSTALL"),
    ([("keep", "none"), ("drop", "conflict"), D, D, D], "INSTALL WITH CHANGES"),
    ([("drop", "new-standing"), ("drop", "conflict"), D, D, D], "COPY RULES, SKIP PLUGIN"),
    ([("drop", "new-skill-text"), D, D, D, D], "COPY RULES, SKIP PLUGIN"),
    ([("drop", "conflict"), ("drop", "duplicate"), D, D, D], "DON'T INSTALL"),
    ([("drop", "duplicate"), D, D, D, D], "DON'T INSTALL"),
]
for i, (p, want) in enumerate(cases):
    code, out = run("units-verdict", U, answers(f"a{i}.json", p))
    chk(f"units-verdict: {sorted(set(p))} gives {want}", code == 0 and f": {want};" in out, out)
code, out = run("units-verdict", U, answers("keepcopy.json", [("keep", "new-standing"), ("keep", "new-standing"), D, D, D]))
chk("a kept skill's general rules are still counted as rules to copy", "units with a conflict 0; rules 2 / 0 / 0 / 3" in out and "skills kept 2 of 5" in out, out)

# refusals
code, out = run("units-verdict", U, answers("short.json", [D] * 4))
chk("a unit with no answer is refused, exit 2", code == 2 and "u5: no answer" in out, out)
code, out = run("units-verdict", U, J("twice.json", {"answers": [{"id": "u1", "skill": "drop", "rules": "none", "conflicts": []}] * 2 + [{"id": f"u{i}", "skill": "drop", "rules": "none", "conflicts": []} for i in range(2, 6)]}))
chk("a unit answered twice is refused", code == 2 and "u1: answered twice" in out, out)
code, out = run("units-verdict", U, answers("bad.json", [("maybe", "none")] + [D] * 4))
chk("a skill answer outside keep/drop is refused", code == 2 and "u1: skill 'maybe'" in out, out)
code, out = run("units-verdict", U, answers("bad2.json", [("drop", "install-skill")] + [D] * 4))
chk("a rules answer outside the list is refused", code == 2 and "u1: rules 'install-skill'" in out, out)
code, out = run("units-verdict", U, J("extra.json", {"answers": [{"id": f"u{i}", "skill": "drop", "rules": "none", "conflicts": []} for i in range(1, 7)]}))
chk("an answer for a unit that doesn't exist is refused", code == 2 and "u6: no such unit" in out, out)
code, out = run("units-verdict", U, J("noc.json", {"answers": [{"id": f"u{i}", "skill": "drop", "rules": "none"} for i in range(1, 6)]}))
chk("an answer with no conflicts list is refused", code == 2 and "u1: conflicts must be a list" in out, out)
code, out = run("units-verdict", U, answers("conf.json", [("keep", "conflict"), D, D, D, D]))
chk("a section with a conflict counts as one, whatever its rules answer", "INSTALL WITH CHANGES" in out and "units with a conflict 1" in out, out)
code, out = run("units-verdict", U, os.path.join(d, "nope.json"))
chk("a missing answers file is refused", code == 2 and "can't read" in out, out)

# several runs: agreement per unit, on each answer
a = answers("r1.json", [("keep", "new-standing"), D, D, ("drop", "duplicate"), D])
b = answers("r2.json", [("keep", "new-standing"), D, D, ("drop", "duplicate"), D])
c = answers("r3.json", [("keep", "none"), D, D, ("drop", "duplicate"), ("keep", "none")])
code, out = run("units-verdict", U, a, b)
chk("two identical runs are stable, exit 0", code == 0 and "skill: units answered the same in all 2 runs: 5 of 5" in out and out.rstrip().endswith("stable"), out)
code, out = run("units-verdict", U, a, b, c)
chk("a unit answered differently is named on its axis, and the set is not stable (exit 1)",
    code == 1 and "rules: units answered the same in all 3 runs: 4 of 5" in out and "conflict: units answered the same in all 3 runs: 5 of 5" in out and "u1 skills/s/SKILL.md > (top): new-standing 2, none 1" in out
    and "u5 commands/c.md > (top): drop 2, keep 1" in out, out)
sys.exit(1 if fails else 0)
