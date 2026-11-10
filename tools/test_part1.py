#!/usr/bin/env python3
"""tools/part1: "## What it adds", rendered from the dossier by code. Its place in the report, written by tools/vet,
is tested in tools/test_vet.py.

Fixtures are tools/fixtures/part1/<name>.dossier.json, dossiers written by hand: each carries target.read_status, and
in current_rules a planted rule text, READER-MARKER-7, that no output may hold. The shape check at the end builds a small
plugin in a temporary folder (a plugin-shaped tree stored in this repo would change neckbeard's own inventory, since
the marketplace ships the whole repo) and runs inventory.py on it with an empty config folder and project."""
import copy, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
NB = os.path.dirname(HERE)
PART1 = os.path.join(HERE, "part1")
INVENTORY = os.path.join(NB, "skills", "neckbeard", "inventory.py")
FX = os.path.join(HERE, "fixtures", "part1")
HEADINGS = ["Injects", "Hooks", "Subagents and commands", "State it may leave", "Reaches outside the session", "Source"]
FOOTER = ('Load timing is how Claude Code loads skills, not measured here. Tokens are estimated as bytes / 4; '
          'where the inventory fell back to a character count, "bytes" counts characters.')
TEMPS = []
fail = checks = 0


def chk(name, ok, detail=""):
    global fail, checks
    checks += 1
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        fail += 1


def tmp():
    d = tempfile.mkdtemp(prefix="part1-test-")
    TEMPS.append(d)
    return d


def fx(name):
    return os.path.join(FX, name + ".dossier.json")


def render(path, *extra):
    r = subprocess.run([sys.executable, PART1, path, *extra], capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def variant(name, edit):
    """A copy of a fixture's dossier after EDIT(dossier), written to a temp file."""
    d = json.load(open(fx(name)))
    edit(d)
    p = os.path.join(tmp(), "d.json")
    json.dump(d, open(p, "w"))
    return p


def parse(out):
    """{(card, label): (rest of the label's line, [its `  - ` lines])}"""
    got, card, cur = {}, None, None
    for line in out.split("\n"):
        m = re.match(r"^### (.+)$", line)
        if m:
            card, cur = m.group(1), None
            continue
        m = re.match(r"^- ([^:]+):(?: (.*))?$", line)
        if m and card:
            cur = (card, m.group(1))
            got[cur] = (m.group(2) or "", [])
            continue
        m = re.match(r"^  - (.*)$", line)
        if m and cur:
            got[cur][1].append(m.group(1))
    return got


def state_of(entry):
    """The state a label's line shows: entries (the label alone, then its entries), none, partly read, not read, not applicable."""
    if entry is None:
        return "missing"
    rest, _ = entry
    for s in ("none", "partly read", "not read", "not applicable"):
        if rest == s or rest.startswith(s + ":"):
            return s
    return "entries" if rest == "" else rest


def lines(got, card, label):
    return (got.get((card, label)) or ("", []))[1]


CARDS = {
    "Skills": "Injects", "Rule files": "Injects", "Hook-injected text": "Injects", "Hooks": "Hooks",
    "Agents": "Subagents and commands", "Commands": "Subagents and commands", "Persistence candidates": "State it may leave",
    "MCP servers": "Reaches outside the session", "plugin.json": "Source", "Marketplace": "Source",
}
STATES = {  # fixture -> label -> the state its line shows; across them every state appears on every card
    "plugin-found": {k: "entries" for k in CARDS},
    "plugin-none": {**{k: "none" for k in CARDS}, "Marketplace": "not applicable"},
    "plugin-partial": {k: "partly read" for k in CARDS},
    "plugin-not-read": {k: "not read" for k in CARDS},
    "rule-file": {**{k: "not applicable" for k in CARDS}, "Rule files": "entries"},
}

# ---------------------------------------------------------------- Done when 1: each card, each state, and the exact words
for name, want in STATES.items():
    rc, out, err = render(fx(name))
    got = parse(out)
    bad = {lab: (state_of(got.get((CARDS[lab], lab))), st) for lab, st in want.items() if state_of(got.get((CARDS[lab], lab))) != st}
    chk(f"1. {name}: every card prints its state ({len(want)} lines)", rc == 0 and not bad, f"rc={rc} {bad} {err[-200:]}")
seen = {s for w in STATES.values() for s in w.values()}
chk("1. across the fixtures every state appears", seen == {"entries", "none", "partly read", "not read", "not applicable"}, seen)

rc, out, _ = render(fx("plugin-found"), "--commit", "feed1234")
got = parse(out)
chk("1. a skill line: description chars, then the file's bytes and tokens (bytes // 4, with a ~); a capped one says so",
    lines(got, "Injects", "Skills") == ["alpha: description every session (21 chars); the file on demand (1200 bytes, ~300 tokens)",
                                         "beta: description every session (1 chars); the file on demand (303 bytes, ~75 tokens) (read capped)"], lines(got, "Injects", "Skills"))
chk("1. a rule file line, named by its path inside the target", lines(got, "Injects", "Rule files") == ["CLAUDE.md: every session (400 bytes, ~100 tokens)"], lines(got, "Injects", "Rule files"))
chk("1. a hook-injected file line", lines(got, "Injects", "Hook-injected text") == ["hooks/inject.md: 80 bytes, ~20 tokens"], lines(got, "Injects", "Hook-injected text"))
chk("1. each hook event with its matcher and script, then whether the hooks reach subagents, with the basis",
    lines(got, "Hooks", "Hooks") == ["PreToolUse (Bash): hooks/guard.sh", "SessionStart: hooks/run.sh", "reaches subagents: false (no event known to fire in a subagent)"], lines(got, "Hooks", "Hooks"))
chk("1. agents and commands by name", lines(got, "Subagents and commands", "Agents") == ["reviewer"] and lines(got, "Subagents and commands", "Commands") == ["ship"])
chk("1. persistence candidates", lines(got, "State it may leave", "Persistence candidates") == ["hooks/run.sh", "scripts/install.sh"], lines(got, "State it may leave", "Persistence candidates"))
chk("1. each MCP server: name, transport, a command's basename or a url's scheme and host",
    lines(got, "Reaches outside the session", "MCP servers") == ["files (local-process, node)", "web (http, https://api.example.com)"], lines(got, "Reaches outside the session", "MCP servers"))
chk("1. source: kind, name and version from plugin.json, the marketplace's name, the commit as given",
    all(l in out.split("\n") for l in ("- Kind: plugin", "- Name: demo (from plugin.json)", "- Version: 1.2.0 (from plugin.json)", "- Commit: feed1234"))
    and lines(got, "Source", "Marketplace") == ["m"], out[-400:])
chk("1. the footer is the spec's, word for word", out.rstrip("\n").endswith(FOOTER) and out.count(FOOTER) == 1)
chk("1. no --commit: the commit line says commit not given", "- Commit: commit not given" in render(fx("plugin-found"))[1].split("\n"))
p = variant("plugin-found", lambda d: (d["target"]["hooks"].update(hooks_reach_subagents=None), d["target"]["plugin_json"].update(version=None)))
out = render(p)[1]
chk("1. a null hooks_reach_subagents prints unknown; a null version prints no version",
    "  - reaches subagents: unknown" in out.split("\n") and "- Version: no version" in out.split("\n"), out)
got = parse(render(fx("plugin-partial"))[1])
chk("1. partly read: the entries found, then the notes as not read",
    (lines(got, "Injects", "Skills") or [""])[0].startswith("alpha: ") and (lines(got, "Injects", "Skills") or [""])[-1] == "not read: skills: one entry could not be read (dangling symlink)", lines(got, "Injects", "Skills"))
chk("1. a refused entry prints its name as not read, with the refused text, never None chars",
    "gamma: not read: resolves outside the target tree" in lines(got, "Injects", "Skills") and not any("None" in l for l in lines(got, "Injects", "Skills")), lines(got, "Injects", "Skills"))
chk("1. not read: the inventory's own note is printed",
    state_of(parse(render(fx("plugin-not-read"))[1]).get(("Injects", "Skills"))) == "not read"
    and "skills: could not be read (not valid JSON)" in parse(render(fx("plugin-not-read"))[1]).get(("Injects", "Skills"), ("", []))[0])
p = variant("plugin-partial", lambda d: d["target"]["read_status"]["agents"].update(notes=[]))
chk("1. a partial section with no notes prints partly read and no not read line",
    parse(render(p)[1]).get(("Subagents and commands", "Agents")) == ("partly read", ["reviewer"]))
p = variant("plugin-found", lambda d: d["target"]["hooks"].update(injected_content=None, injected_content_note="hook payloads cannot be traced"))
got = parse(render(p)[1])
chk("1. hooks read with an untraced injected text: not read, never none, and the Hooks line still follows read_status.hooks",
    state_of(got.get(("Injects", "Hook-injected text"))) == "not read" and state_of(got.get(("Hooks", "Hooks"))) == "entries", got.get(("Injects", "Hook-injected text")))

# ---------------------------------------------------------------- Done when 2: identical, six headings, sorted
every = sorted(f[: -len(".dossier.json")] for f in os.listdir(FX) if f.endswith(".dossier.json") and f != "old-dossier.dossier.json")
bad = []
for f in every:
    a, b = render(fx(f), "--commit", "feed1234"), render(fx(f), "--commit", "feed1234")
    if a[1] != b[1] or a[0] != 0:
        bad.append(f"{f}: not identical or exit {a[0]}")
    heads = re.findall(r"^### (.+)$", a[1], re.M)
    if not a[1].startswith("## What it adds\n") or heads != HEADINGS:
        bad.append(f"{f}: headings {heads}")
chk(f"2. every fixture ({len(every)}) renders twice byte-identical, with the section heading and the six cards in order", not bad and len(every) >= 8, "; ".join(bad[:3]))
got = parse(render(fx("unsorted"))[1])
chk("2. a fixture whose lists are out of order renders sorted",
    (lines(got, "Injects", "Skills") or [""])[0].startswith("alpha:") and lines(got, "Subagents and commands", "Agents") == ["beta", "zeta"]
    and lines(got, "State it may leave", "Persistence candidates") == ["a.sh", "z.sh"], got)

# ---------------------------------------------------------------- Done when 4: nothing private in any output
home = os.path.expanduser("~")
banned = ["READER-MARKER-7", "/Users/", home, "secretarg", "SECRETARG", "SECRETFLAG", "/v1/secret", "token=abc123", "ENVVALUE-9", "/proj/demo", "--flag",
          "host.example", "TOPSECRET", "SECRETCODE", "sk-live-999", "abc123", "TOK", "pw@", "8443", "~/", "$HOME", "/secret/"]
bad = []
for f in every:
    out = render(fx(f), "--commit", "feed1234")[1]
    bad += [f"{f}: {b}" for b in banned if b in out] + ([f"{f}: no output"] if not out.strip() else [])
chk("4. no fixture's output holds the reader's rule text, a home path, a hook argument, a url path or query, or an env value", not bad, "; ".join(bad[:4]))
outside = os.path.join(tmp(), "scripts")
p = variant("plugin-found", lambda d: d["target"]["hooks"]["events"].update(Stop=[{"matcher": None, "command": f"{outside}/outside.sh --token SECRETARG"}]))
out = render(p)[1]
chk("4. a hook script under an absolute temp path outside the plugin prints its basename only",
    "  - Stop: outside.sh" in out.split("\n") and outside not in out and os.path.dirname(outside) not in out and "SECRETARG" not in out, out)
out = render(fx("hooks-unidentified"))[1]
got = parse(out)
chk("4. an unidentifiable_hooks note prints as <event>: <script>, without its arguments or its absolute path",
    "not read: hooks/hooks.json: unidentifiable hooks: SessionStart: curl; Stop: thing.sh" in (lines(got, "Hooks", "Hooks") or [""])[-1] or any("unidentifiable hooks: SessionStart: curl; Stop: thing.sh" in l for l in lines(got, "Hooks", "Hooks")),
    lines(got, "Hooks", "Hooks"))

got = parse(render(fx("hooks-hostile-commands"))[1])
hl = {}
for l in lines(got, "Hooks", "Hooks"):
    m = re.match(r"^(\w+)(?: \([^)]*\))?: (.*)$", l)
    if m and not l.startswith("reaches"):
        hl[m.group(1)] = m.group(2)
UNP = "<unparsed command>"
chk("4. hook commands with an env prefix, inline code (-c, and -lc -ec -xc -Bc), a flag's value, a ~ or $HOME path print their script or <unparsed command>, never the arguments; env is looked through",
    hl == {"Notification": "homehook.sh", "PermissionRequest": UNP, "PostToolUse": "x.sh", "PostToolUseFailure": "./x.sh", "PreCompact": UNP, "PreToolUse": UNP,
           "SessionEnd": UNP, "SessionStart": "./hook.sh", "Stop": UNP, "SubagentStart": UNP, "SubagentStop": "script.py", "UserPromptSubmit": "envhome.sh",
           "Elicitation": UNP, "ElicitationResult": UNP, "Setup": "x.sh", "TaskCompleted": "./a.sh", "TeammateIdle": "http.server"}, hl)
chk("4. a url as the script (deno run, npx), a second command after ; or &&, and python -m print no url, query, argument or second command",
    all(hl.get(e) == w for e, w in (("Elicitation", UNP), ("ElicitationResult", UNP), ("Setup", "x.sh"), ("TaskCompleted", "./a.sh"), ("TeammateIdle", "http.server"))), hl)
out = render(fx("hostile"))[1]
got = parse(out)
allowed = {"## What it adds"} | {f"### {h}" for h in HEADINGS}
forged = [l for l in out.split("\n") if re.match(r"^(#|>|\|)", l) and l not in allowed]
chk("4. target strings with newlines, headings, a verdict line, a table row or the At a glance heading forge nothing: six cards, no other heading, quote or table line",
    not forged and re.findall(r"^### (.+)$", out, re.M) == HEADINGS, forged)
ml = lines(got, "Reaches outside the session", "MCP servers")
chk("4. MCP servers: a url shows scheme and host only (no userinfo, port, path or query); an env prefix, a list or a bad or non-string url print no secret and do not crash",
    render(fx("hostile"))[0] == 0 and any(l.startswith("web ") and l.endswith("(http, https://api.example.com)") for l in ml) and "envcmd (local-process, node)" in ml
    and "listcmd (local-process, command)" in ml and "badurl (http, url)" in ml and "inturl (http, url)" in ml, ml)
chk("4. an absolute or ~ path in a name, an injected file or a persistence entry prints its basename",
    "secret-tool: description every session (21 chars); the file on demand (1200 bytes, ~300 tokens)" in lines(got, "Injects", "Skills")
    and (lines(got, "Injects", "Hook-injected text") or [""])[0] == "inject.md: 12 bytes, ~3 tokens"
    and {"state.json", "p.json"} <= set(lines(got, "State it may leave", "Persistence candidates")), (lines(got, "Injects", "Skills"), lines(got, "State it may leave", "Persistence candidates")))
chk("4. an unreadable command is named as not read, with its reason", lines(got, "Subagents and commands", "Commands") == ["cmd: not read: unreadable"], lines(got, "Subagents and commands", "Commands"))
chk("4. a long target string is cut", all(len(l) < 400 for l in out.split("\n")), max(len(l) for l in out.split("\n")))
p = variant("plugin-found", lambda d: d["target"]["skills"][0].update(bytes=None))
chk("4. a skill whose bytes is None is not read, not 0 bytes", "alpha: not read" in lines(parse(render(p)[1]), "Injects", "Skills"), lines(parse(render(p)[1]), "Injects", "Skills"))
p = variant("plugin-found", lambda d: d["target"]["read_status"]["agents"].update(state="weird"))
chk("4. a section state the tool does not know prints as not read", state_of(parse(render(p)[1]).get(("Subagents and commands", "Agents"))) == "not read")
out = render(fx("generic-pack"))[1]
chk("4. a generic pack is named by its folder, with no version", "- Name: mypack" in out.split("\n") and "- Version: no version" in out.split("\n"), out)
chk("4. a rule file is named by its basename", "- Name: rules.md" in render(fx("rule-file"))[1].split("\n"))

# ---------------------------------------------------------------- Done when 6: the hook command forms
got = parse(render(fx("hooks-forms"))[1])
chk("6. ${CLAUDE_PLUGIN_ROOT}/x.sh arg, bash ${CLAUDE_PLUGIN_ROOT}/x.sh and an unbalanced quote print x.sh, x.sh and <unparsed command>",
    lines(got, "Hooks", "Hooks")[:3] == ["PreToolUse: <unparsed command>", "SessionStart: x.sh", "Stop: x.sh"], lines(got, "Hooks", "Hooks"))

# ---------------------------------------------------------------- Done when 5: the real inventory output, and no read_status
def real_tree(root):
    """A small plugin: one skill, one hook with an injected file, one MCP server, an agent and a command."""
    files = {
        ".claude-plugin/plugin.json": json.dumps({"name": "real", "version": "2.0.0"}),
        "skills/a/SKILL.md": "---\nname: a\ndescription: A real skill.\n---\nBody.\n",
        "agents/ag.md": "---\nname: ag\ndescription: d\n---\nText.\n",
        "commands/c.md": "---\nname: c\ndescription: d\n---\nText.\n",
        "hooks/hooks.json": json.dumps({"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks/run.sh"}]}]}}),
        "hooks/run.sh": "#!/bin/sh\ncat \"${CLAUDE_PLUGIN_ROOT}/hooks/inject.md\"\n",
        "hooks/inject.md": "Injected text.\n",
        ".mcp.json": json.dumps({"mcpServers": {"s": {"command": "node", "args": ["x.js"]}}}),
    }
    for rel, text in files.items():
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(text)


tree = tmp(); real_tree(tree)
e = tmp()
r = subprocess.run([sys.executable, INVENTORY, tree, "--project-dir", e, "--out", os.path.join(e, "d.json")],
                   env={"PATH": os.environ["PATH"], "HOME": e, "CLAUDE_CONFIG_DIR": e}, capture_output=True, text=True)
rc, out, err = render(os.path.join(e, "d.json"), "--commit", "feed1234") if r.returncode == 0 else (None, "", r.stderr)
got = parse(out)
chk("5. inventory.py's own output for a small plugin renders with exit 0, a state on every line of every card",
    rc == 0 and all((CARDS[l], l) in got and state_of(got[(CARDS[l], l)]) != "missing" for l in CARDS) and len(got) >= len(CARDS), f"{rc} {err[-200:]}\n{out}")
chk("5. and that plugin reads: its skill, hook, injected file, agent, command and MCP server are each listed",
    (lines(got, "Injects", "Skills") or [""])[0].startswith("a: ") and (lines(got, "Hooks", "Hooks") or [""])[0] == "SessionStart: hooks/run.sh"
    and lines(got, "Injects", "Hook-injected text") and lines(got, "Subagents and commands", "Agents") and lines(got, "Subagents and commands", "Commands")
    and lines(got, "Reaches outside the session", "MCP servers") == ["s (local-process, node)"], out)
chk("4. the real inventory's output holds no absolute temp path and no home", not any(x in "".join(out) for x in (tree, os.path.realpath(tree), e, home)) and out != "", out)
d = json.load(open(os.path.join(e, "d.json")))
del d["target"]["read_status"]
json.dump(d, open(os.path.join(e, "no-rs.json"), "w"))
rc, out, err = render(os.path.join(e, "no-rs.json"))
chk("5. a dossier with read_status removed exits 2 and says to rerun inventory.py", rc == 2 and out == "" and "dossier has no read_status; rerun inventory.py" in err, f"{rc} {err}")
rc, out, err = render(fx("old-dossier"))
chk("5. an old dossier fixture exits 2 with the same message", rc == 2 and "dossier has no read_status; rerun inventory.py" in err, f"{rc} {err}")

# ---------------------------------------------------------------- never emitted: what vet-stability and excerpts read
src = open(os.path.join(HERE, "vet-stability"), encoding="utf-8").read()
regexes = {n: re.search(rf"^{n} = re\.compile\((.*)\)$", src, re.M).group(1) for n in ("VERDICT_RE", "COUNT_RE")}
ns = {"re": re}
for n, call in regexes.items():
    exec(f"{n} = re.compile({call})", ns)
bad = []
for f in every:
    out = render(fx(f), "--commit", "feed1234")[1]
    if ns["VERDICT_RE"].search(out) or ns["COUNT_RE"].search(out) or re.search(r"^## Conflicts", out, re.M) or re.search(r"^\| \| \| \|", out, re.M):
        bad.append(f)
chk("7. no output matches vet-stability's verdict or count lines, a Conflicts heading or a | | | | row", not bad and len(regexes) == 2, bad)

for t_ in TEMPS:
    shutil.rmtree(t_, ignore_errors=True)
print(f"test_part1: {fail} failed" if fail else "test_part1: all passed")
sys.exit(1 if fail else 0)
