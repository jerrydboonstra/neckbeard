#!/usr/bin/env python3
"""The carrying cost in the verdict code (carrying-cost-verdict): tools/rule-units copies the dossier's always-on hook facts into the units
file, the answers carry "carrying_cost", and tools/units-verdict decides INSTALL against COPY RULES, SKIP PLUGIN from both, as Step 2 says.

    python3 tools/test_carrying_cost.py
"""
import json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
VET = os.path.join(HERE, "vet")
FIX = os.path.join(HERE, "fixtures", "vet-session")
fails = 0


def chk(name, ok, detail=""):
    global fails
    fails += not ok
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + ("" if ok else f": {detail}"))


def run(tool, *args, env=None):
    r = subprocess.run([sys.executable, os.path.join(HERE, tool), *args], capture_output=True, text=True, env=env)
    return r.returncode, r.stdout + r.stderr


d = tempfile.mkdtemp()
J = lambda name, obj: (json.dump(obj, open(os.path.join(d, name), "w")), os.path.join(d, name))[1]
SKILL = "---\nname: s\ndescription: d\n---\n\nAlways run the tests.\n\n## Two\n\nKeep commits small.\n"


def dossier(name, hooks):
    return J(name, {"target": {"skills": [{"source": "skills/s/SKILL.md", "text": SKILL}], "commands": [], "agents": [], "rule_files": [], "hooks": hooks}})


def units_of(name, hooks):
    path = os.path.join(d, name + ".units.json")
    code, out = run("rule-units", dossier(name + ".dossier.json", hooks), path)
    return code, out, path


NOHOOKS = {"has_hooks": False, "events": {}, "hooks_reach_subagents": False}
SS = {"has_hooks": True, "events": {"SessionStart": [{"matcher": "", "command": "run.sh"}]}, "hooks_reach_subagents": False}
SUB = {"has_hooks": True, "events": {"Stop": [{"matcher": "", "command": "run.sh"}]}, "hooks_reach_subagents": True}
QUIET = {"has_hooks": True, "events": {"Stop": [{"matcher": "", "command": "run.sh"}]}, "hooks_reach_subagents": False}
UNKNOWN = {"has_hooks": True, "events": {"Stop": [{"matcher": "", "command": "run.sh"}]}, "hooks_reach_subagents": None}


def answers(name, cost=None, skill="keep", rules="none", n=2):
    body = {"answers": [{"id": f"u{i + 1}", "skill": skill, "rules": rules, "conflicts": [], "why": "x"} for i in range(n)]}
    if cost is not None:
        body["carrying_cost"] = cost
    return J(name, body)


# 1. rule-units copies the always-on facts into the units file
for label, hooks, want in (("no hooks", NOHOOKS, {"session_start": False, "subagents": False}), ("a SessionStart hook", SS, {"session_start": True, "subagents": False}),
                           ("hooks that reach subagents", SUB, {"session_start": False, "subagents": True}), ("a hook that stays in the main session", QUIET, {"session_start": False, "subagents": False}),
                           ("hooks_reach_subagents unknown", UNKNOWN, {"session_start": False, "subagents": True})):
    code, out, path = units_of("ao", hooks)
    got = json.load(open(path)).get("always_on")
    chk(f"rule-units: {label} gives always_on {want}", code == 0 and got == want, (code, got, out))
PARTIAL_SS = {"has_hooks": "partial", "events": {"SessionStart": [{"matcher": "", "command": "run.sh"}]}, "hooks_reach_subagents": False}
PARTIAL_Q = {"has_hooks": "partial", "events": {"Stop": [{"matcher": "", "command": "run.sh"}]}, "hooks_reach_subagents": False}
for label, hooks, want in (("with a SessionStart event", PARTIAL_SS, {"session_start": True, "subagents": False}), ("with only a Stop event", PARTIAL_Q, {"session_start": False, "subagents": False})):
    code, out, path = units_of("ao", hooks)
    chk(f"rule-units: has_hooks partial {label} is read from its events, no unknown note: {want}", json.load(open(path)).get("always_on") == want and "unknown" not in out, (json.load(open(path)).get("always_on"), out))
code, out, path = units_of("ao", UNKNOWN)
chk("rule-units: an unread hook counts as always-on and says so on stderr", "unknown" in out.lower() and "always" in out.lower(), out)
UNKNOWN_HAS = {"has_hooks": "unknown", "events": {}, "hooks_reach_subagents": None}
code, out, path = units_of("ao", UNKNOWN_HAS)
chk("rule-units: the inventory's has_hooks \"unknown\" (events unread) gives both flags true and a stderr note naming it",
    json.load(open(path)).get("always_on") == {"session_start": True, "subagents": True} and "has_hooks" in out, out)
doc = json.load(open(dossier("nohooks.dossier.json", {})))
del doc["target"]["hooks"]
code, out = run("rule-units", J("nohooks.dossier.json", doc), os.path.join(d, "nohooks.units.json"))
chk("rule-units: a dossier with no hooks key at all gives both flags true", json.load(open(os.path.join(d, "nohooks.units.json"))).get("always_on") == {"session_start": True, "subagents": True}, out)
code, out, path = units_of("ao", {})
chk("rule-units: a dossier with no hooks section counts as always-on (unread), and says so", json.load(open(path)).get("always_on") == {"session_start": True, "subagents": True} and "unknown" in out.lower(), out)

# 2. units-verdict: the verdict rule with carrying_cost
_, _, U_ON = units_of("on", SS)
_, _, U_OFF = units_of("off", NOHOOKS)
COPY = "COPY RULES, SKIP PLUGIN"
for cost, want in (("install", "INSTALL"), ("copy", COPY), ("reader-decides", COPY)):
    code, out = run("units-verdict", U_ON, answers(f"on-{cost}.json", cost))
    chk(f"units-verdict: always-on cost, a kept skill, carrying_cost {cost} gives {want}", code == 0 and f": {want};" in out, out)
for cost in (None, "install", "copy", "reader-decides"):
    code, out = run("units-verdict", U_OFF, answers(f"off-{cost}.json", cost))
    chk(f"units-verdict: no always-on cost, carrying_cost {cost} is ignored: INSTALL", code == 0 and ": INSTALL;" in out, out)
code, out = run("units-verdict", U_ON, answers("conf.json", "copy"))
body = json.load(open(os.path.join(d, "conf.json")))
C = [{"quote": "q", "reader_rule": "r", "held_in": "rules/x.md", "hard_stop": False}]
body["answers"][0]["conflicts"] = C
code, out = run("units-verdict", U_ON, J("conf2.json", body))
chk("units-verdict: a conflict is still counted when the verdict is COPY RULES", code == 0 and f": {COPY};" in out and "units with a conflict 1" in out, out)
code, out = run("units-verdict", U_ON, answers("dropall.json", "copy", skill="drop", n=2))
chk("units-verdict: nothing kept and nothing to copy stays DON'T INSTALL whatever carrying_cost says", ": DON'T INSTALL;" in out, out)
code, out = run("units-verdict", U_ON, answers("dropnew.json", "install", skill="drop", rules="new-standing", n=2))
chk("units-verdict: carrying_cost install with only rules kept keeps today's COPY RULES", f": {COPY};" in out, out)
code, out = run("units-verdict", U_ON, answers("rd.json", "reader-decides"))
_, copy_out = run("units-verdict", U_ON, answers("rd-copy.json", "copy"))
chk("units-verdict: reader-decides adds exactly one line to the same answers marked copy, and it names the trade",
    code == 0 and len(out.splitlines()) - len(copy_out.splitlines()) == 1 and "reader-decides" in out and "cheaper to copy" in out, (out, copy_out))
code, out = run("units-verdict", U_ON, answers("rd2.json", "copy"))
chk("units-verdict: copy needs no trade line", "reader-decides" not in out, out)
code, out = run("units-verdict", U_ON, answers("rd3.json", "reader-decides"), "--json")
chk("units-verdict --json carries the carrying_cost and the verdict", json.loads(out)["verdict"] == COPY and json.loads(out).get("carrying_cost") == "reader-decides", out)

# the multi-run path: each ANSWERS file's own carrying_cost applies
code, out = run("units-verdict", U_ON, answers("m1.json", "copy"), answers("m2.json", "install"))
chk("units-verdict: two answers files, one copy and one install on an always-on units file, give both verdicts and are not stable",
    code == 1 and f"{COPY} in 1 of 2" in out and "INSTALL in 1 of 2" in out and "NOT stable" in out, (code, out))
code, out = run("units-verdict", U_ON, answers("m3.json", "copy"), answers("m4.json", "copy"))
chk("units-verdict: two answers files marked copy agree and are stable", code == 0 and out.rstrip().endswith("stable") and "NOT" not in out, (code, out))
code, out = run("units-verdict", U_ON, answers("m5.json", "copy"), answers("m6.json"))
chk("units-verdict: with several files, one missing its carrying_cost is refused, exit 2", code == 2 and "carrying_cost" in out, (code, out))

# 3. refusals
for label, units in (("a SessionStart hook", U_ON), ("a hook reaching subagents", units_of("sub", SUB)[2]), ("an unread hook", units_of("unk", UNKNOWN)[2])):
    code, out = run("units-verdict", units, answers("none.json"))
    chk(f"units-verdict: {label} and no carrying_cost is refused, named, exit 2", code == 2 and "carrying_cost" in out and "refused" in out, (code, out))
_, _, U_QUIET = units_of("quiet", QUIET)
code, out = run("units-verdict", U_QUIET, answers("none2.json"))
chk("units-verdict: a hook that is neither at session start nor reaching subagents needs no carrying_cost", code == 0 and ": INSTALL;" in out, out)
code, out = run("units-verdict", U_ON, answers("bad.json", "maybe"))
chk("units-verdict: a carrying_cost outside install/copy/reader-decides is refused, named", code == 2 and "carrying_cost" in out and "maybe" in out, out)
code, out = run("units-verdict", U_OFF, answers("bad2.json", "maybe"))
chk("units-verdict: a bad carrying_cost is refused even with no always-on cost", code == 2 and "carrying_cost" in out, out)
old = J("old.units.json", {"units": json.load(open(U_ON))["units"]})
code, out = run("units-verdict", old, answers("old.json"))
chk("units-verdict: a units file with no always_on key gets today's rule and one stderr note", code == 0 and ": INSTALL;" in out and out.lower().count("carrying-cost rule was not applied") == 1, (code, out))

# a units file with no always_on key ignores carrying_cost, "copy" included
code, out = run("units-verdict", old, answers("oldcopy.json", "copy"))
chk("units-verdict: a units file with no always_on key and carrying_cost copy still gives INSTALL, with the one stderr note",
    code == 0 and ": INSTALL;" in out and out.lower().count("carrying-cost rule was not applied") == 1, (code, out))

# the field is asked for where the answers are written (Done when 4)
vu = open(os.path.join(HERE, "vet-units.md"), encoding="utf-8").read()
skill = open(os.path.join(HERE, "..", "skills", "neckbeard", "SKILL.md"), encoding="utf-8").read()
path_a = skill.split("**Path A:")[1].split("**Path B:")[0]
answers_bullet = [l for l in path_a.split("\n") if l.startswith("- **Answers.**")]
chk("tools/vet-units.md asks for carrying_cost and its three values", '"carrying_cost": "install", "copy" or "reader-decides"' in vu, vu[-400:])
chk("SKILL.md's path A Answers bullet names carrying_cost and points at Step 2", len(answers_bullet) == 1 and "carrying_cost" in answers_bullet[0] and "Step 2" in answers_bullet[0], answers_bullet)

# 4. end to end through tools/vet's session mode, on a plugin with a session-start hook and a subagent hook
def build(name, hooked):
    tmp = os.path.join(d, name)
    home, proj, other = (os.path.join(tmp, x) for x in ("home", "proj", "other"))
    for p in (os.path.join(home, ".claude"), proj, other):
        os.makedirs(p)
    shutil.copy(os.path.join(FIX, "home", ".claude", "CLAUDE.md"), os.path.join(home, ".claude", "CLAUDE.md"))
    shutil.copy(os.path.join(FIX, "project", "CLAUDE.md"), os.path.join(proj, "CLAUDE.md"))
    shutil.copy(os.path.join(FIX, "other", "outside-rules.md"), os.path.join(other, "outside-rules.md"))
    target = os.path.join(tmp, "demo")
    os.makedirs(os.path.join(target, ".claude-plugin")); os.makedirs(os.path.join(target, "skills", "demo"))
    json.dump({"name": "demo", "version": "1.0.0"}, open(os.path.join(target, ".claude-plugin", "plugin.json"), "w"))
    open(os.path.join(target, "skills", "demo", "SKILL.md"), "w").write("---\nname: demo\ndescription: A demo skill.\n---\n\nAlways run the tests before you commit.\n")
    if hooked:
        os.makedirs(os.path.join(target, "hooks"))
        json.dump({"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": "echo hi"}]}],
                             "SubagentStart": [{"hooks": [{"type": "command", "command": "echo hi"}]}]}}, open(os.path.join(target, "hooks", "hooks.json"), "w"))
    dos = os.path.join(tmp, "dossier.json")
    env = {**os.environ, "HOME": home, "CLAUDE_CONFIG_DIR": os.path.join(home, ".claude")}
    subprocess.run([sys.executable, os.path.join(HERE, "..", "skills", "neckbeard", "inventory.py"), target, "--project-dir", proj, "--out", dos,
                    "--extra-rules", os.path.join(other, "outside-rules.md")], env=env, check=True, capture_output=True)
    return tmp, home, target, dos


def vet(tmp, home, target, dos, cost):
    units = os.path.join(tmp, "u.json")
    subprocess.run([sys.executable, os.path.join(HERE, "rule-units"), dos, units], check=True, capture_output=True)
    ids = [u["id"] for u in json.load(open(units))["units"]]
    body = {"answers": [{"id": i, "skill": "keep", "rules": "none", "quote": "", "why": "x", "conflicts": [], "star": n == 0} for n, i in enumerate(ids)]}
    if cost:
        body["carrying_cost"] = cost
    ans = os.path.join(tmp, "answers.json")
    json.dump(body, open(ans, "w"))
    bindir = os.path.join(tmp, "bin"); os.makedirs(bindir, exist_ok=True)
    open(os.path.join(bindir, "claude"), "w").write("#!/bin/sh\nexit 1\n"); os.chmod(os.path.join(bindir, "claude"), 0o755)
    env = {**{k: v for k, v in os.environ.items() if k != "CLAUDE_CONFIG_DIR"}, "HOME": home, "PATH": bindir + os.pathsep + os.environ["PATH"]}
    out = os.path.join(tmp, "out", "report.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    p = subprocess.run([VET, target, out, "--dossier", dos, "--answers", ans, "--prose", os.path.join(FIX, "prose.json")], env=env, capture_output=True, text=True, cwd=tmp)
    return p.returncode, p.stdout + p.stderr, open(out, encoding="utf-8").read() if os.path.exists(out) else ""


hooked = build("hooked", True)
hu = os.path.join(hooked[0], "u.json")
subprocess.run([sys.executable, os.path.join(HERE, "rule-units"), hooked[3], hu], check=True, capture_output=True)
chk("end to end: the real inventory's dossier of that plugin gives always_on session_start and subagents both true", json.load(open(hu)).get("always_on") == {"session_start": True, "subagents": True}, json.load(open(hu)).get("always_on"))
code, out, text = vet(*hooked, "copy")
chk("end to end: a session-start hook and a subagent hook, one kept skill, answered copy: COPY RULES, SKIP PLUGIN in the strip", code == 0 and COPY in text and "🟩 INSTALL" not in text, (code, out[-400:]))
code, out, text = vet(*hooked, None)
chk("end to end: the same with no carrying_cost: vet exits 1 naming it, no report", code == 1 and "carrying_cost" in out and not text, (code, out[-400:]))
code, out, text = vet(*hooked, "reader-decides")
chk("end to end: the hooked plugin answered reader-decides gives COPY RULES and the report carries the trade line under the strip",
    code == 0 and COPY in text and text.count("Reader decides: exactly one rule survives") == 1, (code, out[-300:]))
code, out, text = vet(*hooked, "copy")
chk("end to end: answered copy, the report has no trade line", code == 0 and "Reader decides" not in text, (code, out[-300:]))
plain = build("plain", False)
code, out, text = vet(*plain, "copy")
chk("end to end: the same answers (copy) on a copy with no hooks give INSTALL", code == 0 and "🟩 INSTALL" in text and COPY not in text, (code, out[-400:]))

shutil.rmtree(d)
print(f"test_carrying_cost: {'FAILED ' + str(fails) if fails else 'ok'}")
sys.exit(1 if fails else 0)
