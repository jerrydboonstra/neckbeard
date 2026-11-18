#!/usr/bin/env python3
"""tools/summary: "## How it affects you", the five summary rows (Cost, Reach, Leaves state, Live surface, Read completeness),
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
for sec, row in [("persistence_candidates", "Leaves state"), ("mcp_servers", "Live surface"), ("hooks", "Reach"), ("skills", "Cost"),
                 ("agents", "Cost"), ("rule_files", "Cost")]:
    for state in ("partial", "failed"):
        got = colours(edit("green", lambda t: t["read_status"].__setitem__(sec, {"state": state, "notes": ["x"]})))
        chk(f"2 {sec} {state}: {row} is not {G}", got[row] not in (G, None), str(got))
chk("2 a not-applicable section counts as read in full", colours(edit("green", lambda t: t["read_status"].__setitem__("agents", {"state": "not-applicable", "notes": []})))["Cost"] == G)

# 2a. mod only, local-process MCP only, ssh hook only
chk("2a mod only: Live surface orange", colours(load("mod-only"))["Live surface"] == O)
chk("2a local-process MCP only: Live surface orange", colours(load("mcp-local"))["Live surface"] == O)
chk("2a ssh hook: Live surface red", colours(load("hook-ssh-subagents"))["Live surface"] == R)


def hook_cmd(cmd):
    return edit("hook-local", lambda t: t["hooks"]["events"]["SessionStart"][0].__setitem__("command", cmd))


for cmd, want in [("grep ssh log", Y), ("FOO=1 ssh h", R), ("echo hi && ssh h", R), ("a & ssh h", R), ("/usr/bin/mosh h", R),
                  ("wget x", O), ("run.sh https://example.com/x", O), ("run.sh | nc h 1", O), ("bash -c 'ssh h'", Y), ("run.sh", Y)]:
    chk(f"2a hook command {cmd!r}", colours(hook_cmd(cmd))["Live surface"] == want, colours(hook_cmd(cmd))["Live surface"])
chk("2a MCP server running ssh: red", colours(edit("mcp-local", lambda t: t["mcp_servers"]["servers"][0].update(command="ssh")))["Live surface"] == R)
chk("2a MCP server with an ssh arg: red", colours(edit("mcp-local", lambda t: t["mcp_servers"]["servers"][0].update(args=["/usr/bin/ssh", "h"])))["Live surface"] == R)

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
    chk("3 and the printed footer", "2,000" in before and "3,000" not in before and "3,000" in after and "2,000" not in after)
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

# 6, and the shape of the output
for name, _ in CASES:
    code, out, err = run(fx(name))
    chk(f"6 {name}: no read marker, five rows, a rules footer, the full card", code == 0 and not re.search("[\U0001F7E2\U0001F7E1\U0001F534]", out) and list(rows(out)) == ROWS
        and "<summary>" in out and "At a glance in full" in out and "2,000" in out, f"{code} {err[:200]}")
    chk(f"  {name}: two runs are byte-identical", run(fx(name))[1] == out)
d = load("green")
del d["target"]["read_status"]
chk("a dossier with no read_status exits 2", run(write(d))[0] == 2)
chk("a missing file exits 2", run("/nonexistent/x.json")[0] == 2)

for f in TEMPS:
    os.unlink(f)
print(f"{checks - fail}/{checks} checks passed")
sys.exit(1 if fail else 0)
