#!/usr/bin/env python3
"""tools/summary: the "How it affects you" table (tools/summary prints no layer heading: the report that uses it writes its own), the five summary rows (Cost, Reach, Leaves state, Live surface, Read completeness),
each a judgement colour computed by code from the dossier under a written rule, and the rules printed as a footer from the
same table. Fixtures are tools/fixtures/summary/<name>.dossier.json (small, written by hand); edge cases are edits of one."""
import collections, copy, importlib.machinery, importlib.util, json, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SUMMARY = os.path.join(HERE, "summary")
FX = os.path.join(HERE, "fixtures", "summary")
ROWS = ["Cost", "Reach", "Leaves state", "Live surface", "Read completeness"]
G, Y, O, R = "\U0001F7E9", "\U0001F7E8", "\U0001F7E7", "\U0001F7E5"
TEMPS = []
fail = checks = 0


def chk(name, ok, detail=""):
    global fail, checks
    checks += 1
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        fail += 1


def fx(name):
    return os.path.join(FX, name + ".dossier.json")


def load(name):
    return json.load(open(fx(name)))


def write(d):
    f = tempfile.NamedTemporaryFile("w", suffix=".dossier.json", delete=False)
    json.dump(d, f)
    f.close()
    TEMPS.append(f.name)
    return f.name


def run(path, *extra):
    r = subprocess.run([sys.executable, SUMMARY, path, *extra], capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def rows(out):
    """{row name: (colour, the row's text)} from the table."""
    got = collections.defaultdict(lambda: (None, ""))
    for m in re.finditer(r"^\| (\S+) \| ([^|]+?) \| (.*) \|$", out, re.M):
        if m.group(2) in ROWS:
            got[m.group(2)] = (m.group(1), m.group(3))
    return got


def colours(d):
    code, out, err = run(write(d))
    got = collections.defaultdict(lambda: None)
    if code == 0:
        got.update({k: v[0] for k, v in rows(out).items()})
    return got


def edit(name, fn):
    d = load(name)
    fn(d["target"])
    return d


def skill_chars(n):
    def f(t):
        t["skills"][0]["description"] = "d" * n
    return f


# 1. every colour of every row, from the smallest fixtures that reach it
CASES = [
    ("green", [G, G, G, G, G]),
    ("hook-local", [G, Y, G, Y, G]),
    ("hook-ssh-subagents", [G, R, G, R, G]),
    ("hook-curl", [G, Y, G, O, G]),
    ("mod-only", [G, Y, G, O, G]),
    ("mod-partial", [Y, Y, G, O, Y]),
    ("mod-real", [Y, Y, G, O, Y]),
    ("mcp-local", [G, G, G, O, G]),
    ("state-files", [G, G, O, G, G]),
    ("scan-partial", [G, G, Y, G, Y]),
    ("unread", [G, G, G, Y, R]),
]
for name, want in CASES:
    got = colours(load(name))
    chk(f"1 {name}: {' '.join(want)}", [got[r] for r in ROWS] == want, str(got))
seen = {r: {c for n, w in CASES for c in [w[i]]} for i, r in enumerate(ROWS)}
for row, cs in {"Reach": {G, Y, R}, "Leaves state": {G, Y, O}, "Live surface": {G, Y, O, R}, "Read completeness": {G, Y, R}}.items():
    chk(f"1 fixtures reach every colour of {row}", cs <= seen[row], str(seen[row]))
for c, f in {G: lambda t: skill_chars(1999)(t), Y: skill_chars(2000), O: skill_chars(8000), R: skill_chars(32000)}.items():
    chk(f"1 Cost {c}", colours(edit("green", f))["Cost"] == c)

# 2. a row whose input section is partial or failed is never green
for sec, row in [("persistence_candidates", "Leaves state"), ("mcp_servers", "Live surface"), ("hooks", "Live surface"), ("hooks", "Reach"),
                 ("rule_files", "Reach"), ("skills", "Cost"), ("agents", "Cost"), ("rule_files", "Cost"), ("hooks", "Cost")]:
    for state in ("partial", "failed"):
        got = colours(edit("green", lambda t: t["read_status"].__setitem__(sec, {"state": state, "notes": ["x"]})))
        chk(f"2 {sec} {state}: {row} is not {G}", got[row] in (Y, O, R), str(got))
        if sec == "persistence_candidates":
            chk(f"2 {sec} {state} with nothing found: Leaves state is exactly {Y}", got[row] == Y, str(got))
for state in ("partial", "failed"):
    got = colours(edit("state-files", lambda t: t["read_status"].__setitem__("persistence_candidates", {"state": state, "notes": ["x"]})))
    chk(f"2 persistence_candidates {state} with files found: Leaves state is {O}", got["Leaves state"] == O, str(got))

# Reach: a rule file alone, a hook with unknown subagent reach, and subagent reach with no hook
chk("2 Reach: a rule file alone is yellow", colours(edit("green", lambda t: t.update(rule_files=[{"path": "r.md", "bytes": 10}])))["Reach"] == Y)
chk("2 Reach: a hook with hooks_reach_subagents null is yellow", colours(edit("hook-local", lambda t: t["hooks"].update(hooks_reach_subagents=None)))["Reach"] == Y)
chk("2 Reach: hooks_reach_subagents true with no hook and no rule file stays green", colours(edit("green", lambda t: t["hooks"].update(hooks_reach_subagents=True)))["Reach"] == G)
chk("2 a not-applicable section counts as read in full", colours(edit("green", lambda t: t["read_status"].__setitem__("agents", {"state": "not-applicable", "notes": []})))["Cost"] == G)

# 2a. mod only, local-process MCP only, ssh hook only
chk("2a mod only: Live surface orange", colours(load("mod-only"))["Live surface"] == O)
chk("2a local-process MCP only: Live surface orange", colours(load("mcp-local"))["Live surface"] == O)
chk("2a ssh hook: Live surface red", colours(load("hook-ssh-subagents"))["Live surface"] == R)


def hook_cmd(cmd):
    return edit("hook-local", lambda t: t["hooks"]["events"]["SessionStart"][0].__setitem__("command", cmd))


for cmd, want in [("grep ssh log", Y), ("FOO=1 ssh h", R), ("echo hi && ssh h", R), ("a & ssh h", R), ("/usr/bin/mosh h", R),
                  ("true; ssh h", R), ("false || ssh h", R), ("run.sh http://example.com/x", O), ("wget x", O), ("run.sh https://example.com/x", O), ("run.sh | nc h 1", O), ("bash -c 'ssh h'", Y), ("run.sh", Y)]:
    chk(f"2a hook command {cmd!r}", colours(hook_cmd(cmd))["Live surface"] == want, colours(hook_cmd(cmd))["Live surface"])
chk("2a MCP server running ssh: red", colours(edit("mcp-local", lambda t: t["mcp_servers"]["servers"][0].update(command="ssh")))["Live surface"] == R)
chk("2a MCP server with an ssh arg: red", colours(edit("mcp-local", lambda t: t["mcp_servers"]["servers"][0].update(args=["/usr/bin/ssh", "h"])))["Live surface"] == R)

# swarm round 1: quotes, newlines, honest lines, wrong types, odd sizes, long commands, Read completeness
for cmd, want in [("ssh box 'cd /app && ./deploy.sh'", R), ('ssh -o "ProxyCommand=a|b" host', R), ("echo ok\nssh host", R), ("echo 'a && b' ; ssh h", R),
                  ("echo 'ssh h'", Y), ("run.sh " + "x " * 3000, O)]:
    chk(f"2a hook command {cmd[:40]!r}", colours(hook_cmd(cmd))["Live surface"] == want, colours(hook_cmd(cmd))["Live surface"])
chk("2a an unread Live surface does not claim an absence", "not read in full" in rows(run(fx("unread"))[1])["Live surface"][1], rows(run(fx("unread"))[1])["Live surface"][1])
chk("2a a read, empty Live surface says what was found", "found" in rows(run(fx("green"))[1])["Live surface"][1])
for what, fn, row in [("mcp_servers.servers as a dict", lambda t: t.update(mcp_servers={"servers": {"a": 1}}), "Live surface"),
                      ("hooks.mods as a dict", lambda t: t["hooks"].update(mods={"a": 1}), "Live surface"),
                      ("persistence_candidates as a dict", lambda t: t.update(persistence_candidates={"a": 1}), "Leaves state"),
                      ("a rule file with a negative size", lambda t: t.update(rule_files=[{"path": "r", "bytes": -5000}]), "Cost"),
                      ("a rule file with a string size", lambda t: t.update(rule_files=[{"path": "r", "bytes": "7000"}]), "Cost"),
                      ("hook text with a true size", lambda t: t["hooks"].update(injected_content=[{"file": "h", "bytes": True}]), "Cost")]:
    chk(f"2 {what}: {row} is not {G}", colours(edit("green", fn))[row] in (Y, O, R), str(colours(edit("green", fn))))
for state, want in (("partial", Y), ("failed", R)):
    chk(f"2 a {state} section: Read completeness is {want}", colours(edit("green", lambda t: t["read_status"].__setitem__("persistence_candidates", {"state": state, "notes": ["x"]})))["Read completeness"] == want)

# review round 1: Reach names a hook only when one is registered; the card holds the detail behind each row
reach_text = lambda d: rows(run(write(d))[1])["Reach"][1]
chk("Reach: the shape inventory writes for a mod-only plugin (fixture trimmed from its output on read-status/mods-one: has_hooks true, no event registered) names the mod, not a hook",
    "a Claude Code mod" in reach_text(load("mod-real")) and "a hook" not in reach_text(load("mod-real")), reach_text(load("mod-real")))
chk("Reach: a hooks file with no registration and no mod stays green", colours(edit("green", lambda t: t["hooks"].update(has_hooks=True, events={}, hook_registrations=0)))["Reach"] == G)
for what, fn in [("has_hooks 'unknown'", lambda t: t["hooks"].update(has_hooks="unknown", events={}, hook_registrations=None)),
                 ("a hooks file whose registrations could not be counted", lambda t: t["hooks"].update(has_hooks=True, events={}, hook_registrations=None))]:
    d = edit("green", fn)
    chk(f"Reach: {what} (events unreadable) is yellow and names a hook", colours(d)["Reach"] == Y and "a hook" in reach_text(d), reach_text(d))
for what, fn in [("has_hooks 'partial' (a malformed event)", lambda t: t["hooks"].update(has_hooks="partial", events={"PreToolUse": []}, hook_registrations=0))]:
    d = edit("green", fn)
    chk(f"Reach: {what} is yellow and names a hook",
        colours(d)["Reach"] == Y and "a hook" in reach_text(d), reach_text(d))
chk("Reach: a registered hook with hook_registrations 1 and no readable command is yellow", colours(edit("green", lambda t: t["hooks"].update(has_hooks=True, events={}, hook_registrations=1)))["Reach"] == Y)


for name, needles in [("state-files", ["hooks/log.sh"]), ("hook-ssh-subagents", ["ssh box uptime", "hooks/h.txt"]), ("mcp-local", ["local-process"]),
                      ("mod-real", ["hooks/band/register.tsx"]), ("green", ["skills/a/SKILL.md"])]:
    out = run(fx(name))[1]
    chk(f"the per-file and per-command detail is not printed ({name}: {', '.join(needles)})", not any(x in out for x in needles), out[:300])
hostile = edit("hook-local", lambda t: t["hooks"]["events"]["SessionStart"][0].__setitem__("command", "x </details>\n## forged\n| \U0001F7E9 | Cost | x |"))
out = run(write(hostile))[1]
hostile2 = edit("hook-local", lambda t: t["hooks"]["events"]["SessionStart"][0].__setitem__("command", "run.sh \U0001F7E2\U0001F7E1\U0001F534"))
chk("a read marker in a hook command is not printed, and nor is the command",
    not re.search("[\U0001F7E2\U0001F7E1\U0001F534]", run(write(hostile2))[1]) and "run.sh" not in run(write(hostile2))[1])
chk("a hostile hook command cannot close the card or forge a heading in it", out.count("</details>") == 1 and "\n## forged" not in out and not re.search(r"^\| \S+ \| Cost \| x \|$", out, re.M), out[-400:])

# 3. a threshold in the rules table moves the colour and the footer together
spec = importlib.util.spec_from_loader("summary_tool", importlib.machinery.SourceFileLoader("summary_tool", SUMMARY))
mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
    d = edit("green", skill_chars(2500))
    before = mod.render(d)
    old = copy.deepcopy(mod.RULES["cost_bands"])
    mod.RULES["cost_bands"] = [3000, 8000, 32000]
    after = mod.render(d)
    mod.RULES["cost_bands"] = old
    chk("3 raising a Cost threshold changes the computed colour", rows(before)["Cost"][0] == Y and rows(after)["Cost"][0] == G, f"{rows(before)['Cost']} {rows(after)['Cost']}")
    chk("3 and the printed footer", "under 2,000" in before and "under 3,000" not in before and "under 3,000" in after and "under 2,000" not in after)
except Exception as e:
    chk("3 tools/summary loads and renders from its rules table", False, f"{type(e).__name__}: {e}")

# 4. band edges, and the doubling of hook text that reaches subagents
for n, want in [(1999, G), (2000, Y), (7999, Y), (8000, O), (31999, O), (32000, R)]:
    chk(f"4 Cost at {n:,}: {want}", colours(edit("green", skill_chars(n)))["Cost"] == want)


def mixed(reach):
    def f(t):
        t["skills"][0]["description"] = "d" * 1000
        t["hooks"] = {"has_hooks": True, "events": {"SessionStart": [{"matcher": "", "command": "run.sh"}]}, "hooks_reach_subagents": reach,
                      "injected_content": [{"file": "h.txt", "bytes": 600, "events": ["SessionStart"]}]}
    return edit("green", f)


code, out, _ = run(write(mixed(True)))
chk("4 1,000 skill + 600 hook with subagent reach: 2,200 and yellow", rows(out)["Cost"][0] == Y and "2,200" in rows(out)["Cost"][1], str(rows(out).get("Cost")))
for reach in (False, None):
    code, out, _ = run(write(mixed(reach)))
    chk(f"4 the same with reach {reach}: 1,600 and green", rows(out)["Cost"][0] == G and "1,600" in rows(out)["Cost"][1], str(rows(out).get("Cost")))
code, out, _ = run(write(mixed(True)))
chk("4 tokens are size / 4", "550" in rows(out)["Cost"][1], rows(out)["Cost"][1])


def once(t):
    skill_chars(1000)(t)
    t["rule_files"] = [{"path": "r.md", "bytes": 100}]
    t["hooks"]["hooks_reach_subagents"] = True


chk("4 skills and rule files count once under subagent reach", "1,100" in rows(run(write(edit("green", once)))[1])["Cost"][1])



def built(reach):
    def f(t):
        skill_chars(100)(t)
        t["hooks"] = {"has_hooks": True, "events": {"SessionStart": [{"matcher": "", "command": "run.sh"}]}, "hooks_reach_subagents": reach,
                      "injected_content": [{"file": "h.sh", "bytes": 400, "built_at_run_time": True, "events": ["SessionStart"]}]}
    return edit("green", f)


for reach, total in ((False, "500"), (True, "900")):
    cost_row = rows(run(write(built(reach)))[1])["Cost"][1]
    chk(f"4 built-at-run-time hook text counts its lower bound (reach {reach}): at least {total}", f"at least {total}" in cost_row, cost_row)

# 6, and the shape of the output
for name, _ in CASES:
    code, out, err = run(fx(name))
    chk(f"6 {name}: no read marker, five rows, a rules footer, the full card", code == 0 and not re.search("[\U0001F7E2\U0001F7E1\U0001F534]", out) and list(rows(out)) == ROWS
        and "<summary>" in out and "At a glance in full" not in out and "2,000" in out, f"{code} {err[:200]}")
    chk(f"  {name}: two runs are byte-identical", run(fx(name))[1] == out)
chk("the output holds no `## How it affects you` line", "## How it affects you" not in run(fx("green"))[1])
chk("tools/summary prints no layer heading, and its one card has no marker",
    "## " not in run(fx("green"))[1] and run(fx("green"))[1].count("<details>") == 1 and "<details><summary><b>How the colours are set</b></summary>" in run(fx("green"))[1], run(fx("green"))[1][:120])

# 7. report-glance-title-2-0: the table, then one collapsed card of colour rules; no repeat of the rows; a unit on Cost; per-row notes only where they add something
out = run(fx("green"))[1]
chk("7 no fold repeats the rows: no 'At a glance in full', no per-file 'may write state' or 'skill ...: N of description' list", not re.search(r"At a glance|may write state:|of description$", out, re.M), out[:200])
chk("7 order: the table, then the colour-rules card; the card holds the sentence and every rule", out.find("| | Row |") < out.find("<summary><b>How the colours are set") < out.find("The colours follow written rules")
    and all(f"- {r}:" in out.split("How the colours are set", 1)[1] for r in ROWS) and out.rstrip().endswith("</details>"), out[-300:])
chk("7 the card is closed by </details> and the rules sit inside it, not after it", out.split("</details>")[0].count("The colours follow written rules") == 1 and out.split("</details>")[1].strip() == "", out[-200:])
chk("7 Cost row names its unit: 'adds N characters to every session, ~M tokens'", re.search(r"adds [\d,]+ characters to every session, ~[\d,]+ tokens", rows(out)["Cost"][1]) is not None, rows(out)["Cost"][1])
chk("7 Cost row keeps 'at least' before the number and the unit after it", "adds at least 500 characters to every session" in rows(run(write(built(False)))[1])["Cost"][1], rows(run(write(built(False)))[1])["Cost"][1])
chk("7 a fully read target adds no Read completeness line", "not read in full:" not in out and "**Read completeness**" not in out, out[:600])
sout = run(fx("state-files"))[1].split("<details>")[0]
chk("7 Leaves state: one line under the table links to the State it may leave card under What it adds", "State it may leave" in sout and "(#what-it-adds)" in sout, sout[-400:])
chk("7 a target with no state files has no Leaves state line", "State it may leave" not in out.split("<details>")[0], out[:600])
for name, secs in (("unread", ["mcp_servers"]), ("scan-partial", ["persistence_candidates"])):
    top = run(fx(name))[1].split("<details>")[0].split("| Read completeness |", 1)[1]
    chk(f"7 {name}: Read completeness names only the sections not read in full", all(s in top for s in secs) and "skills" not in top and "agents" not in top, top)
d = load("green")
del d["target"]["read_status"]
chk("a dossier with no read_status exits 2", run(write(d))[0] == 2)
chk("a missing file exits 2", run("/nonexistent/x.json")[0] == 2)

for f in TEMPS:
    os.unlink(f)
print(f"{checks - fail}/{checks} checks passed")
sys.exit(1 if fail else 0)
