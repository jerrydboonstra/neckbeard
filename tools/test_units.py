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
code, out = run("units-verdict", U, J("notdict.json", {"answers": ["u1"]}))
chk("an answer that isn't an object is refused, exit 2", code == 2 and "not an object" in out, out)
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

# units-confirm: pool candidates from find passes, then count only the confirmed ones
U2 = J("units2.json", {"units": [{"id": "u1", "file": "a.md", "heading": "A", "text": "You may try the same action,\n  on your own judgement. Stop at once."},
                                 {"id": "u2", "file": "b.md", "heading": "B", "text": "Never push."}]})
DOS = J("dossier.json", {"current_rules": {"items": [{"path": "/home/x/rules/safety.md", "text": "# Safety\n\n1. **Never push without my go-ahead in this conversation:** not to main,\n   not to a branch.\n2. **Never delete files outside the working tree.** Ask first.\n"}]}})
R1 = "rules/safety.md: 1. **Never push without my go-ahead in this conversation:** not to main, not to a branch."
f1 = J("f1.json", {"conflicts": [{"id": "u1", "quote": "You may try the same action, on your own judgement.", "reader_rule": 'safety.md: "Never push without my go-ahead in this conversation" (the permission is unlimited, so it covers pushes)'},
                                 {"id": "u9", "quote": "x", "reader_rule": "Never push without my go-ahead"}, {"id": "u2", "quote": "Always push.", "reader_rule": "Never push without my go-ahead"}]})
f2 = J("f2.json", {"conflicts": [{"id": "u1", "quote": "try the same action, on your own judgement", "reader_rule": "rules/safety.md rule 1: Never push without my go-ahead in this conversation"}, {"id": "u2", "quote": "never push.", "reader_rule": "safety.md 2. Never delete files outside the working tree"},
                                 {"id": "u2", "quote": "Never push.", "reader_rule": "safety.md rule 1: Never push without my go-ahead in this conversation"},
                                 {"id": "u2", "quote": "Never push.", "reader_rule": "rule X, which I made up"}]})
f3 = J("f3.json", {"conflicts": []})
C2 = os.path.join(d, "cands.json")
code, out = run("units-confirm", "pool", U2, DOS, C2, f1, f2, f3)
cands = json.load(open(C2))
chk("pool: the same sentence in two passes (spacing, case and a longer quote ignored) is one candidate found in 2", code == 0 and [(c["id"], c["found_in"]) for c in cands["candidates"]] == [("u1", 2), ("u2", 1), ("u2", 1)], cands)
chk("pool: the longer quote is kept", cands["candidates"][0]["quote"] == "You may try the same action, on your own judgement.", cands)
chk("pool: a quote not in the unit and a unit that doesn't exist are dropped, and listed", sorted(x["why"] for x in cands["dropped"] if "quote" in x["why"]) == ["quote is not in the unit's text"] * 2, cands["dropped"])
chk("pool: the reader rule is the reader's own text, whatever the finder wrote around it", cands["candidates"][0]["reader_rule"] == R1, cands["candidates"][0])
chk("pool: no argument of the finder's reaches the reader rule", all("unlimited" not in c["reader_rule"] and "covers" not in c["reader_rule"] for c in cands["candidates"]), cands)
chk("pool: one sentence against two reader rules stays two candidates", [c["reader_rule"][17:32] for c in cands["candidates"] if c["id"] == "u2"] == ["2. **Never dele", "1. **Never push"], cands)
chk("pool: a reader_rule that matches no reader rule drops the candidate", [x["candidate"]["reader_rule"] for x in cands["dropped"] if "no reader rule" in x["why"]] == ["rule X, which I made up"], cands["dropped"])
code, out = run("units-confirm", "pool", U2, DOS, C2, os.path.join(d, "nope.json"))
chk("pool: an unreadable find pass is skipped, not fatal", code == 0 and "0 candidates" in out, out)
code, out = run("units-confirm", "pool", U2, DOS, C2, f1, f2, f3)
cc = lambda name, rows: J(name, {"confirmations": [{"cid": cid, "conflict": v, "why": "w"} for cid, v in rows]})
ans = lambda: answers("m.json", [("keep", "none"), D])
code, out = run("units-confirm", "merge", C2, cc("c1.json", [("c1", True), ("c2", False), ("c3", False)]), ans())
code2, out2 = run("units-verdict", U2, os.path.join(d, "m.json"))
chk("merge: a confirmed candidate becomes the unit's conflict, a rejected one does not", code == 0 and "1 of 3 candidates confirmed" in out and "INSTALL WITH CHANGES" in out2 and "units with a conflict 1" in out2, out + out2)
got = json.load(open(os.path.join(d, "m.json")))["answers"]
chk("merge: it carries the confirmed sentence and rule", got[0]["conflicts"] == [{"quote": "You may try the same action, on your own judgement.", "reader_rule": R1}] and got[1]["conflicts"] == [], got)
code, out = run("units-confirm", "merge", C2, cc("c2.json", [("c1", False), ("c2", False), ("c3", False)]), answers("m2.json", [("keep", "conflict"), D]))
code2, out2 = run("units-verdict", U2, os.path.join(d, "m2.json"))
chk("merge: a conflict the judge wrote itself is replaced, so none confirmed means INSTALL", code == 0 and ": INSTALL;" in out2 and "units with a conflict 0" in out2, out + out2)
code, out = run("units-confirm", "merge", C2, cc("c3.json", [("c1", True)]), ans())
chk("merge: a candidate with no confirmation is refused, exit 2", code == 2 and "c2" in out, out)
code, out = run("units-confirm", "merge", C2, J("c4.json", {"confirmations": [{"cid": "c1", "conflict": "yes"}, {"cid": "c2", "conflict": True}, {"cid": "c3", "conflict": True}]}), ans())
chk("merge: a confirmation that is not true or false is refused", code == 2 and "c1" in out, out)
code, out = run("units-confirm")
chk("units-confirm with no arguments prints usage, exit 2", code == 2, out)
sys.exit(1 if fails else 0)
