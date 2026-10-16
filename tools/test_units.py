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

# units-verdict: the verdict rule
def answers(name, buckets):
    return J(name, {"answers": [{"id": f"u{i + 1}", "bucket": b, "why": "x"} for i, b in enumerate(buckets)]})
cases = [
    (["install-skill", "dropped", "dropped", "duplicate", "dropped"], "INSTALL"),
    (["install-skill", "conflict", "dropped", "dropped", "dropped"], "INSTALL WITH CHANGES"),
    (["new-standing", "conflict", "dropped", "dropped", "dropped"], "COPY RULES, SKIP PLUGIN"),
    (["new-skill-text", "dropped", "dropped", "dropped", "dropped"], "COPY RULES, SKIP PLUGIN"),
    (["conflict", "duplicate", "dropped", "dropped", "dropped"], "DON'T INSTALL"),
    (["duplicate", "duplicate", "dropped", "dropped", "dropped"], "DON'T INSTALL"),
]
for i, (b, want) in enumerate(cases):
    code, out = run("units-verdict", U, answers(f"a{i}.json", b))
    chk(f"units-verdict: {'/'.join(sorted(set(b)))} gives {want}", code == 0 and f": {want};" in out, out)

# refusals
code, out = run("units-verdict", U, answers("short.json", ["dropped"] * 4))
chk("a unit with no answer is refused, exit 2", code == 2 and "u5: no answer" in out, out)
code, out = run("units-verdict", U, J("twice.json", {"answers": [{"id": "u1", "bucket": "dropped"}] * 2 + [{"id": f"u{i}", "bucket": "dropped"} for i in range(2, 6)]}))
chk("a unit answered twice is refused", code == 2 and "u1: answered twice" in out, out)
code, out = run("units-verdict", U, answers("bad.json", ["keep"] + ["dropped"] * 4))
chk("a bucket outside the list is refused", code == 2 and "u1: bucket 'keep'" in out, out)
code, out = run("units-verdict", U, J("extra.json", {"answers": [{"id": f"u{i}", "bucket": "dropped"} for i in range(1, 7)]}))
chk("an answer for a unit that doesn't exist is refused", code == 2 and "u6: no such unit" in out, out)
code, out = run("units-verdict", U, os.path.join(d, "nope.json"))
chk("a missing answers file is refused", code == 2 and "can't read" in out, out)

# several runs: agreement per unit
a = answers("r1.json", ["install-skill", "dropped", "dropped", "duplicate", "dropped"])
b = answers("r2.json", ["install-skill", "dropped", "dropped", "duplicate", "dropped"])
c = answers("r3.json", ["new-standing", "dropped", "dropped", "duplicate", "dropped"])
code, out = run("units-verdict", U, a, b)
chk("two identical runs are stable, exit 0", code == 0 and "5 of 5" in out and out.rstrip().endswith("stable"), out)
code, out = run("units-verdict", U, a, b, c)
chk("a unit judged differently is named with its split, and the set is not stable (exit 1)",
    code == 1 and "INSTALL in 2 of 3" in out and "u1 skills/s/SKILL.md > (top): install-skill 2, new-standing 1" in out, out)
sys.exit(1 if fails else 0)
