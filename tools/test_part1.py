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
INVENTORY_HOOKS = os.path.join(NB, "skills", "neckbeard", "inventory_hooks.py")
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
        m = re.match(r"^### (.+)$", line) or re.match(r"^<details><summary>(?:\U0001F7E2|\U0001F7E1|\U0001F534) <b>(.*?)</b>", line)
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
    if rest.startswith(("neckbeard did not read: ", "broken in the plugin: ")):   # a failed section names its cause in place of `not read:`
        return "not read"
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

# ---------------------------------------------------------------- declared-fixtures: the Declared fixtures line
p = variant("plugin-found", lambda d: d["target"].update(declared_fixtures=["tools/fixtures", "x\ny"]))
got = parse(render(p)[1])
chk("D. a dossier with declared_fixtures prints one Declared fixtures line in the Source card, names through safe()",
    (got.get(("Source", "Declared fixtures")) or ("",))[0].startswith("tools/fixtures, x y"), got.get(("Source", "Declared fixtures")))
chk("D. a dossier without the key, or with an empty list, prints no such line",
    ("Source", "Declared fixtures") not in parse(render(fx("plugin-found"))[1])
    and ("Source", "Declared fixtures") not in parse(render(variant("plugin-found", lambda d: d["target"].update(declared_fixtures=[])))[1]))

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
          "host.example", "SECRET9", "TOPSECRET", "SECRETCODE", "sk-live-999", "abc123", "TOK", "pw@", "8443", "~/", "$HOME", "/secret/"]
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
           "Elicitation": UNP, "ElicitationResult": UNP, "Setup": "x.sh", "TaskCompleted": "./a.sh", "TeammateIdle": "http.server", "PostCompact": UNP}, hl)
chk("4. a url as the script (deno run, npx), a second command after ; or &&, and python -m print no url, query, argument or second command (an interpreter with no script of its own in the first command never takes a later command's)",
    all(hl.get(e) == w for e, w in (("Elicitation", UNP), ("ElicitationResult", UNP), ("Setup", "x.sh"), ("TaskCompleted", "./a.sh"), ("TeammateIdle", "http.server"), ("PostCompact", UNP))), hl)
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

# ---------------------------------------------------------------- hook default forms: ${CLAUDE_PLUGIN_ROOT:-word} and the rest
got = parse(render(fx("hooks-default-forms"))[1])
hl = {}
for l in lines(got, "Hooks", "Hooks"):
    m = re.match(r"^(\w+)(?: \([^)]*\))?: (.*)$", l)
    if m and not l.startswith("reaches"):
        hl[m.group(1)] = m.group(2)
chk("8. Cat Herder's hook form, \"${CLAUDE_PLUGIN_ROOT:-${PLUGIN_ROOT}}/bin/meow\" _hook sessionend, prints bin/meow, not <unparsed command>", hl.get("SessionEnd") == "bin/meow", hl)
chk("8. each default form inventory_hooks.py expands (:- - := = :? ?) prints its script; :+ and $CLAUDE_PLUGIN_ROOTX stay <unparsed command>; a quoted form after an interpreter prints its script",
    hl == {"SessionEnd": "bin/meow", "SessionStart": "hooks/a.sh", "Stop": "hooks/b.sh", "PreCompact": "hooks/c.sh", "PostCompact": "hooks/d.sh", "Notification": "hooks/e.sh",
           "PreToolUse": "hooks/f.sh", "PostToolUse": "<unparsed command>", "SubagentStop": "hooks/h.sh", "UserPromptSubmit": "<unparsed command>"}, hl)


p = variant("plugin-found", lambda d: d["target"]["read_status"]["hooks"].update(state="partial", notes=[
    "hooks/hooks.json: unidentifiable hooks: _hook: ${CLAUDE_PLUGIN_ROOT}/x.sh --token SECRET9; 9lives: curl https://h.example/p?SECRET9"]))
out = render(p)[1]
chk("8. an unidentifiable_hooks item whose event name is not a plain capitalised word still prints no argument or url",
    "SECRET9" not in out and "--token" not in out and "h.example" not in out, [l for l in out.split("\n") if "unidentifiable" in l])
p = variant("plugin-found", lambda d: d["target"]["read_status"]["hooks"].update(state="partial", notes=["hooks/hooks.json: unidentifiable hooks: ${CLAUDE_PLUGIN_ROOT}/x.sh --token SECRET9"]))
out = render(p)[1]
chk("8. an unidentifiable_hooks item with no event name at all prints <unparsed command>, never the command",
    "SECRET9" not in out and "--token" not in out and "unidentifiable hooks: <unparsed command>" in out, [l for l in out.split("\n") if "unidentifiable" in l])
p = variant("plugin-found", lambda d: d["target"]["hooks"]["events"].update(Stop=[{"matcher": None, "command": '"hooks/a.sh\n"'}]))
got = parse(render(p)[1])
chk("8. a quoted newline in a hook command cannot split the printed line", "  - Stop: <unparsed command>" in "\n".join("  - " + l for l in lines(got, "Hooks", "Hooks")), lines(got, "Hooks", "Hooks"))
import time
slow = "${CLAUDE_PLUGIN_ROOTX" * 100000   # 2 MB, 100,000 look-alike references that are not expanded: slicing the rest of the string for each is quadratic
p = variant("plugin-found", lambda d: d["target"]["hooks"]["events"].update(Stop=[{"matcher": None, "command": slow}]))
t0 = time.time(); rc = render(p)[0]; took = time.time() - t0
chk("8. a 2 MB hook command with 100,000 plugin-root look-alikes renders in under 3 seconds (a long command is refused before shlex reads it)", rc == 0 and took < 3, f"rc={rc} {took:.1f}s")


def load_expander(path, name):
    """A function from a script, loaded by path (tools/part1 has no .py name)."""
    import importlib.machinery, importlib.util
    modname = "loaded_" + re.sub(r"\W", "_", os.path.basename(path))
    loader = importlib.machinery.SourceFileLoader(modname, path)
    mod = importlib.util.module_from_spec(importlib.util.spec_from_loader(modname, loader))
    loader.exec_module(mod)
    return getattr(mod, name)


FORMS = ["${CLAUDE_PLUGIN_ROOT}/x.sh", "$CLAUDE_PLUGIN_ROOT/x.sh", "${CLAUDE_PLUGIN_ROOT:-${PLUGIN_ROOT}}/bin/meow _hook a", "${CLAUDE_PLUGIN_ROOT:-/opt/x y}/z.sh",
         "${CLAUDE_PLUGIN_ROOT-w}/a", "${CLAUDE_PLUGIN_ROOT:=w}/a", "${CLAUDE_PLUGIN_ROOT=w}/a", "${CLAUDE_PLUGIN_ROOT:?w}/a", "${CLAUDE_PLUGIN_ROOT?w}/a",
         "${CLAUDE_PLUGIN_ROOT:+w}/a", "$CLAUDE_PLUGIN_ROOTX/a", "$CLAUDE_PLUGIN_ROOT_x/a", "${CLAUDE_PLUGIN_ROOTX}/a", "${CLAUDE_PLUGIN_ROOT:-${A:-${B}}}/a", "${CLAUDE_PLUGIN_ROOT:-unclosed/a",
         "a ${CLAUDE_PLUGIN_ROOT}/b $CLAUDE_PLUGIN_ROOT/c", "no variable here", "${CLAUDE_PLUGIN_ROOT:-w}${CLAUDE_PLUGIN_ROOT-v}/a"]
try:
    t0 = time.time(); load_expander(PART1, "expand_plugin_root")("${CLAUDE_PLUGIN_ROOTX" * 100000, "ROOT"); took = time.time() - t0
    chk("8. tools/part1's plugin-root expansion scans a 2 MB command with 100,000 look-alike references in under 2 seconds (no quadratic slicing)", took < 2, f"{took:.1f}s")
except Exception as e:
    chk("8. tools/part1's plugin-root expansion is fast on a long command", False, f"{type(e).__name__}: {e}")
try:
    sys.path.insert(0, os.path.dirname(INVENTORY_HOOKS))   # inventory_hooks imports its sibling inventory_core
    inv = load_expander(INVENTORY_HOOKS, "_expand_plugin_root")
    mine = load_expander(PART1, "expand_plugin_root")
    bad = [f for f in FORMS if inv(f, "ROOT") != mine(f, "ROOT")]
    chk(f"8. tools/part1's copy of the plugin-root expansion agrees with inventory_hooks.py's on {len(FORMS)} forms, :+ and ROOTX included", not bad, bad)
except Exception as e:
    chk("8. tools/part1's copy of the plugin-root expansion agrees with inventory_hooks.py's", False, f"{type(e).__name__}: {e}")

# ---------------------------------------------------------------- the State it may leave card summarises a long list
def card_lines(out, heading):
    """The lines of one card, from its ### heading to the line before the next, blank lines left out."""
    keep, on = [], False
    for l in out.split("\n"):
        if l.startswith("### "):
            on = l == f"### {heading}"
            if on:
                keep.append(l)
        elif on and l.strip():
            keep.append(l)
    return keep


out = render(fx("persist-many"))[1]
pl = lines(parse(out), "State it may leave", "Persistence candidates")
more = [l for l in pl if l.startswith("and ")]
folders = re.match(r"^and (\d+) more, in: (.*)$", more[0]) if more else None
counts = [(m.group(1), int(m.group(2))) for m in re.finditer(r"(\S+/) (\d+)", folders.group(2))] if folders else []
chk("9. 150 persistence candidates print 10 entries (the first 10 by path) and one 'and 140 more, in: ...' line whose folder counts sum to 140",
    pl[:10] == [f"lib/f{i:03d}.py" for i in range(10)] and len(pl) == 11 and folders is not None and folders.group(1) == "140" and sum(n for _, n in counts) == 140, pl)
chk("9. the folders are every folder of the rest, the highest count first, then by name; a root file counts under ./",
    more == ["and 140 more, in: lib/ 105, tools/ 25, ./ 10"], more)
chk("9. the card is at most 13 lines (heading, label, 10 entries, the more line)", len(card_lines(out, "State it may leave")) <= 13, card_lines(out, "State it may leave"))
out = render(fx("persist-folders"))[1]
pl = lines(parse(out), "State it may leave", "Persistence candidates")
more = [l for l in pl if l.startswith("and ")]
m = re.match(r"^and (\d+) more, in: (.*), and (\d+) other folders \((\d+) files\)$", more[0]) if more else None
listed = [(a, int(b)) for a, b in re.findall(r"(\S+/) (\d+)", m.group(2))] if m else []
chk("9. 42 candidates in 42 folders: the folder list stops at 15 folders and the rest are 'and 17 other folders (17 files)'; the counts still sum to 32 and the line stays short",
    m is not None and len(listed) == 15 and sum(n for _, n in listed) + int(m.group(4)) == int(m.group(1)) == 32
    and (m.group(3), m.group(4)) == ("17", "17") and len(more[0]) < 200, more)
chk("9. a folder name that holds ', ' and digits cannot forge a count (it is counted under (other)/), and ./dot/z.py counts under dot/ not ./",
    m is not None and "lib 999" not in out and "(other)/ 1" in more[0], more)
def setp(entries):
    def edit(d):
        d["target"]["persistence_candidates"] = entries
    return edit
two = [f"e{i:02d}/{n}" for i in range(22) for n in "ab"]
out = render(variant("persist-ten", setp(two)))[1]
chk("9. 22 folders of 2 files: 'and 34 more, in: ...' lists 15 folders with 2 each, then 'and 2 other folders (4 files)'",
    "and 34 more, in: " in out and out.count("/ 2") == 15 and ", and 2 other folders (4 files)" in out, out)
out = render(variant("persist-ten", setp([f"./dot/f{i:02d}" for i in range(12)])))[1]
chk("9. files under ./dot/ count under dot/, not ./", "and 2 more, in: dot/ 2\n" in out, out)
out = render(fx("persist-ten"))[1]
pl = lines(parse(out), "State it may leave", "Persistence candidates")
chk("9. 10 candidates print all ten and no more line", len(pl) == 10 and not any("more" in l for l in pl), pl)
p = variant("persist-ten", lambda d: d["target"]["persistence_candidates"].append("scripts/s9z.sh"))
pl = lines(parse(render(p)[1]), "State it may leave", "Persistence candidates")
chk("9. 11 candidates print ten and 'and 1 more, in: scripts/ 1'", len(pl) == 11 and pl[-1] == "and 1 more, in: scripts/ 1", pl)
out = render(fx("persist-capped"))[1]
pl = lines(parse(out), "State it may leave", "Persistence candidates")
nr = [l for l in pl if l.startswith("not read: ")]
chk("9. 18 capped files: the not read line names 5 and ends 'and 13 more'",
    len(nr) == 1 and nr[0].count("read capped") == 5 and nr[0].endswith("; and 13 more") and "c00.sh" in nr[0] and "c04.sh" in nr[0] and "c05.sh" not in nr[0], nr)
chk("9. a partly read persistence card with its more line is at most 14 lines", len(card_lines(out, "State it may leave")) <= 14, card_lines(out, "State it may leave"))
def trim(n):
    def edit(d):
        d["target"]["read_status"]["persistence_candidates"]["notes"] = d["target"]["read_status"]["persistence_candidates"]["notes"][:n]
    return edit
for n, want in ((5, None), (6, "and 1 more")):
    pl = lines(parse(render(variant("persist-capped", trim(n)))[1]), "State it may leave", "Persistence candidates")
    nr = [l for l in pl if l.startswith("not read: ")]
    chk(f"9. {n} capped notes: all named" + (", no 'more'" if want is None else ", then 'and 1 more'"),
        len(nr) == 1 and nr[0].count("read capped") == 5 and (("more" not in nr[0]) if want is None else nr[0].endswith("; " + want)), nr)
def many_skills(d):
    d["target"]["skills"] = [{"name": f"s{i:02d}", "description": "x", "path": f"skills/s{i:02d}/SKILL.md"} for i in range(12)]
pl = lines(parse(render(variant("plugin-partial", many_skills))[1]), "Injects", "Skills")
chk("9. 12 skills: the Skills list prints all 12 (a cap inside block() would cut it)", sum(1 for l in pl if re.match(r"s\d\d: ", l)) == 12, pl)
out = render(fx("plugin-partial"))[1]
chk("9. a card that is not persistence still prints every entry (the cap is at the persistence call site only)",
    lines(parse(out), "Injects", "Skills")[0].startswith("alpha: "), lines(parse(out), "Injects", "Skills"))

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

# ---------------------------------------------------------------- note-cause: the report says whose limit each note is
def with_notes(section, notes, causes, state="partial"):
    def edit(d):
        d["target"]["read_status"][section] = {"state": state, "notes": notes, "causes": causes}
    return edit


both = variant("plugin-partial", with_notes("agents", ["agents/a.md: read capped at 200000 bytes", "agents/b.md: not valid JSON"], ["tool-limit", "target-fault"]))
al = lines(parse(render(both)[1]), "Subagents and commands", "Agents")
chk("C4. one tool-limit and one target-fault note: 'neckbeard did not read:' line, then 'broken in the plugin:' line, each its own line",
    al[-2:] == ["neckbeard did not read: agents/a.md: read capped at 200000 bytes", "broken in the plugin: agents/b.md: not valid JSON"], al)
only = variant("plugin-partial", with_notes("agents", ["agents/a.md: read capped at 200000 bytes"], ["tool-limit"]))
al = lines(parse(render(only)[1]), "Subagents and commands", "Agents")
chk("C4. only tool-limit notes: no 'broken' line", al[-1] == "neckbeard did not read: agents/a.md: read capped at 200000 bytes" and not any(l.startswith("broken in the plugin") for l in al), al)
fl = variant("plugin-partial", with_notes("agents", ["agents/a.md: could not be read", "agents/b.md: not valid JSON"], ["tool-limit", "target-fault"], "failed"))
chk("C4. a failed section prints both on the label's line, in place of 'not read: <notes>'",
    parse(render(fl)[1]).get(("Subagents and commands", "Agents"), ("", []))[0] ==
    "neckbeard did not read: agents/a.md: could not be read; broken in the plugin: agents/b.md: not valid JSON",
    parse(render(fl)[1]).get(("Subagents and commands", "Agents")))

old = variant("plugin-partial", lambda d: d["target"]["read_status"]["agents"].update(notes=["agents/a.md: x", "agents/b.md: y"]))
al = lines(parse(render(old)[1]), "Subagents and commands", "Agents")
chk("C4. a section with no causes list (an old dossier) prints today's single 'not read:' line", al[-1] == "not read: agents/a.md: x; agents/b.md: y", al)
bad = variant("plugin-partial", with_notes("agents", ["agents/a.md: x"], ["bogus"]))
al = lines(parse(render(bad)[1]), "Subagents and commands", "Agents")
chk("C4. an unknown cause value falls back to the plain 'not read:' line, never a wrong attribution", al[-1] == "not read: agents/a.md: x", al)
many = variant("persist-capped", lambda d: d["target"]["read_status"]["persistence_candidates"].update(causes=["tool-limit"] * len(d["target"]["read_status"]["persistence_candidates"]["notes"])))
pl = lines(parse(render(many)[1]), "State it may leave", "Persistence candidates")
nr = [l for l in pl if l.startswith("neckbeard did not read: ")]
chk("C4. 18 tool-limit notes on the persistence card: one 'neckbeard did not read:' line, 5 named, ending 'and 13 more'",
    len(nr) == 1 and nr[0].count("read capped") == 5 and nr[0].endswith("; and 13 more"), pl)

# end to end: inventory.py's own causes reach the card (the cases above feed causes in by hand)
tree = tmp(); real_tree(tree)
open(os.path.join(tree, ".mcp.json"), "w").write("{not json")
open(os.path.join(tree, "agents", "big.md"), "w").write("---\nname: big\ndescription: d\n---\n" + "x" * 250_000)
e = tmp()
r = subprocess.run([sys.executable, INVENTORY, tree, "--project-dir", e, "--out", os.path.join(e, "d.json")],
                   env={"PATH": os.environ["PATH"], "HOME": e, "CLAUDE_CONFIG_DIR": e}, capture_output=True, text=True)
got = parse(render(os.path.join(e, "d.json"))[1]) if r.returncode == 0 else {}
chk("C4. real inventory output: a malformed .mcp.json prints 'broken in the plugin:' on the MCP line, a capped agent 'neckbeard did not read:'",
    "broken in the plugin: .mcp.json" in (got.get(("Reaches outside the session", "MCP servers")) or ("", []))[0]
    and any(l.startswith("neckbeard did not read: agents/big.md") for l in lines(got, "Subagents and commands", "Agents")), (r.stderr[-200:], got))

# ---------------------------------------------------------------- hook-echo-traced: text a shell hook builds at run time
def built(events, template, writes, nbytes=66):
    return {"file": "hooks/run.sh", "bytes": nbytes, "events": events, "built_at_run_time": True, "template": template, "writes": writes}


def with_injected(entries):
    return variant("plugin-found", lambda d: d["target"]["hooks"].update(injected_content=entries))


CAVEAT = "built at run time: read from the script's own text, not run; commands it runs are not followed and may print or write files"
rc, out, _ = render(with_injected([built(["SessionStart"], ["imagegen doctor: \u2026 missing", "second \u2026"], ["mkdir -p \u2026", ": > \u2026"])]))
chk("HE5. a built-at-run-time entry prints one `<file> (<events>, built at run time, at least N bytes): <line>` line per template line",
    "  - hooks/run.sh (SessionStart, built at run time, at least 66 bytes): imagegen doctor: \u2026 missing\n"
    "  - hooks/run.sh (SessionStart, built at run time, at least 66 bytes): second \u2026\n" in out, out[:900])
chk("HE5. ... then a `  writes: <items joined by '; '>` line under the entry", "\n  writes: mkdir -p \u2026; : > \u2026\n" in out, out[:900])
rc, out, _ = render(with_injected([built(["SessionStart", "Stop"], [], ["touch \u2026"], 0)]))
chk("HE5. a writes-only entry prints `<file> (<events>, built at run time): prints nothing; writes: <items>`",
    "  - hooks/run.sh (SessionStart, Stop, built at run time): prints nothing; writes: touch \u2026\n" in out, out[:900])
rc, out, _ = render(with_injected([built(["SessionStart"], ["a"], []), {**built(["Stop"], ["b"], []), "file": "hooks/two.sh"}]))
chk("HE5. the caveat line appears once per report, however many entries", out.count(CAVEAT) == 1, out.count(CAVEAT))
rc, out, _ = render(fx("plugin-found"))
chk("HE5. a report with no built entry has no caveat line", CAVEAT not in out)

# ---------------------------------------------------------------- part1-colour-rules: collapsible cards with a read marker and a gist
LEGEND = "\U0001F7E2 read in full \u00b7 \U0001F7E1 partly read \u00b7 \U0001F534 something unread"
G, Y, R = "\U0001F7E2", "\U0001F7E1", "\U0001F534"
SUMMARY = re.compile(r"^<details><summary>(" + G + "|" + Y + "|" + R + r") <b>(.*?)</b>(?: \u00b7 (.*))?</summary>$")


def cards(out):
    """[(marker, name, gist, [body lines])] for each `<details>` card, in order."""
    got, cur = [], None
    for line in out.split("\n"):
        m = SUMMARY.match(line)
        if m:
            cur = (m.group(1), m.group(2), m.group(3), [])
            got.append(cur)
        elif line == "</details>":
            cur = None
        elif cur is not None:
            cur[3].append(line)
    return got


def markers(out):
    return [c[0] for c in cards(out)]


def card_gist(out, name):
    return next((c[2] for c in cards(out) if c[1] == name), None)


rc, out, err = render(fx("plugin-found"), "--commit", "feed1234")
chk("CR1. a fully read fixture prints the legend line, then six `<details><summary>\U0001F7E2 <b>...` cards in order",
    rc == 0 and out.startswith("## What it adds\n\n" + LEGEND + "\n\n<details><summary>" + G + " <b>Injects</b>")
    and [c[1] for c in cards(out)] == HEADINGS and markers(out) == [G] * 6 and "\n### " not in out, (rc, out[:300], err[-200:]))
chk("CR1. each card is `<details><summary>`, a blank line, its lines, a blank line, `</details>`",
    "</summary>\n\n- Skills:\n" in out and "\n\n</details>\n\n<details><summary>" in out and out.count("</details>\n") == 6, out[:400])
want = {
    "Injects": "2 skills \u00b7 ~375 tokens on demand \u00b7 ~22 chars of skill descriptions every session \u00b7 hook text read in full",
    "Hooks": "2 hooks \u00b7 stay in the main session \u00b7 read in full",
    "Subagents and commands": "1 agents \u00b7 1 commands",
    "State it may leave": "2 files that may write state",
    "Reaches outside the session": "2 MCP servers",
    "Source": "plugin \u00b7 demo 1.2.0 from plugin.json \u00b7 commit feed123",
}
chk("CR1. each card's gist is computed from the dossier: counts, tokens (bytes / 4), reach, short sha", {c[1]: c[2] for c in cards(out)} == want, {c[1]: c[2] for c in cards(out)})
chk("CR1. a card's lines are unchanged: the Skills, Hooks and Source lines are the ones the old cards printed",
    len(cards(out)) == 6 and ["- Skills:", "  - alpha: description every session (21 chars); the file on demand (1200 bytes, ~300 tokens)"] == cards(out)[0][3][:2]
    and "  - PreToolUse (Bash): hooks/guard.sh" in cards(out)[1][3] and "- Commit: feed1234" in cards(out)[5][3], len(cards(out)))
chk("CR1. the footer still ends the section", out.rstrip("\n").endswith(FOOTER))
hk = card_gist(render(fx("plugin-none"))[1], "Hooks")
chk("CR1. a gist with the hooks' reach unknown leaves the reach phrase out", hk is not None and "subagents" not in hk and "main session" not in hk and hk.endswith("read in full"), hk)
none_out = render(fx("plugin-none"))[1]
chk("CR1. no agents, no MCP servers and no marketplace read as words in the gist",
    (card_gist(none_out, "Subagents and commands") or "").startswith("no agents") and card_gist(none_out, "Reaches outside the session") == "no MCP servers"
    and (card_gist(none_out, "Source") or "").endswith("\u00b7 no marketplace"), [card_gist(none_out, n) for n in HEADINGS])
cap_out = render(fx("persist-capped"))[1]
chk("CR1. a long persistence list adds `\u00b7 <k> named` (the paths the card lists), and leaves it out when it lists them all",
    card_gist(cap_out, "State it may leave") == "18 files that may write state \u00b7 10 named"
    and "named" not in (card_gist(render(fx("plugin-found"))[1], "State it may leave") or "named"), card_gist(cap_out, "State it may leave"))

# Done when 2: each card's marker is the read state of its own line states, per card
MARK = {  # fixture -> markers in card order (Injects, Hooks, Subagents and commands, State it may leave, Reaches, Source)
    "plugin-found": [G, G, G, G, G, G],
    "plugin-none": [G, G, G, G, G, G],
    "rule-file": [G, G, G, G, G, G],
    "persist-capped": [G, G, G, Y, G, G],        # only State it may leave
    "hooks-unidentified": [Y, Y, G, G, G, G],    # the hooks section feeds Injects and Hooks
    "plugin-partial": [Y, Y, Y, Y, Y, Y],        # Source is partly read
    "plugin-not-read": [R, R, R, R, R, R],       # Source is not read
    "hooks-note": [R, G, G, G, G, G],            # hooks read, injected text untraced: Injects red, the Hooks line keeps its own state
}
for name, want_m in MARK.items():
    chk(f"CR2. {name}: markers {''.join(want_m)}", markers(render(fx(name))[1]) == want_m, markers(render(fx(name))[1]))
for sec_, state_, card_i, mark_ in (("agents", "failed", 2, R), ("mcp_servers", "partial", 4, Y), ("commands", "partial", 2, Y), ("rule_files", "failed", 0, R)):
    p = variant("plugin-found", lambda d, s=sec_, st=state_: d["target"]["read_status"][s].update(state=st, notes=["x: y"]))
    chk(f"CR2. plugin-found with {sec_} {state_}: only card {HEADINGS[card_i]} changes, to {mark_}",
        markers(render(p)[1]) == [mark_ if i == card_i else G for i in range(6)], markers(render(p)[1]))
chk("CR2. a card whose every section failed has the gist `not read`; one with a read section keeps its computed gist",
    {c[1]: c[2] for c in cards(render(fx("plugin-not-read"))[1])} == {h: "not read" for h in HEADINGS}
    and (card_gist(render(fx("hooks-note"))[1], "Injects") or "").endswith("hook text something unread"), card_gist(render(fx("hooks-note"))[1], "Injects"))
got = parse(render(fx("hooks-note"))[1])
chk("CR2. a hooks section read with an untraced injected text: Injects' line is not read, Hooks' line follows read_status.hooks",
    state_of(got.get(("Injects", "Hook-injected text"))) == "not read" and state_of(got.get(("Hooks", "Hooks"))) == "entries", got.get(("Injects", "Hook-injected text")))

# Done when 3: an unknown state word makes its card yellow, keeps its line, and reads as partly read
p = variant("plugin-found", lambda d: d["target"]["read_status"]["agents"].update(state="weird"))
out = render(p)[1]
rs_ = subprocess.run([sys.executable, PART1, "--read-state", p], capture_output=True, text=True)
chk("CR3. an unknown section state: its card is yellow, its line reads `not read: unknown state weird`, --read-state says partly read",
    markers(out) == [G, G, Y, G, G, G] and "- Agents: not read: unknown state weird" in out and (rs_.returncode, rs_.stdout) == (0, "partly read\n"), (markers(out), rs_.stdout, rs_.stderr))

# Done when 4: a card cannot be ended early, and text is escaped once
rc, out, err = render(fx("hostile-card"))
inner = out.replace("</summary>\n", "").replace("</details>\n", "")
chk("CR4. a hostile dossier (</summary>, </details>, & and a newline in a skill name, a hook note, a persistence path and the plugin name): six cards, each closed once, no tag ends one early",
    rc == 0 and out.count("</details>") == 6 and out.count("</summary>") == 6 and out.count("<details>") == 6 and "</summary>" not in inner and "</details>" not in inner
    and len(cards(out)) == 6, (rc, out.count("</details>"), out.count("</summary>"), err[-200:]))
src_summary = next((l for l in out.split("\n") if l.startswith("<details><summary>") and "<b>Source</b>" in l), "")
chk("CR4. the Source summary shows a hostile plugin name escaped once, never twice",
    "&lt;/summary&gt;&amp;&lt;x" in src_summary and "&amp;lt;" not in out and "&amp;amp;" not in out, src_summary)
chk("CR4. a body line escapes `<` as `&lt;` and keeps `&` and `>` as they were", "  - a&lt;/summary>&lt;/details>& b: description every session" in out, [l for l in out.split("\n") if "summary" in l and "<details>" not in l][:3])

# Done when 5: --read-state
bad = []
for f in every:
    r = subprocess.run([sys.executable, PART1, "--read-state", fx(f)], capture_output=True, text=True)
    word = r.stdout.rstrip("\n")
    mk = markers(render(fx(f))[1])
    want_word = "something unread" if R in mk else "partly read" if Y in mk else "read in full"
    if r.returncode != 0 or r.stdout.count("\n") != 1 or word != want_word:
        bad.append(f"{f}: rc={r.returncode} {r.stdout!r} want {want_word}")
chk(f"CR5. --read-state prints one line, the overall read state, and exits 0 on every fixture with read_status ({len(every)}), agreeing with the worst card marker", not bad, "; ".join(bad[:3]))
r = subprocess.run([sys.executable, PART1, "--read-state", fx("old-dossier")], capture_output=True, text=True)
chk("CR5. --read-state on old-dossier (no read_status) exits 2", (r.returncode, r.stdout), (2, ""))
chk("CR5. --read-state with a second argument, or with --commit, or with no dossier, exits 2 and prints the usage",
    all(subprocess.run([sys.executable, PART1, *a], capture_output=True, text=True).returncode == 2
        for a in (["--read-state", fx("plugin-found"), fx("plugin-found")], ["--read-state", fx("plugin-found"), "--commit", "abc"], ["--read-state"])), "")
p = variant("plugin-found", lambda d: d["target"]["read_status"].update(extra_section={"state": "failed", "notes": ["x"]}))
chk("CR5. a read_status section no card uses counts in the overall state but changes no card",
    subprocess.run([sys.executable, PART1, "--read-state", p], capture_output=True, text=True).stdout == "something unread\n" and markers(render(p)[1]) == [G] * 6, "")
p = variant("plugin-found", lambda d: d["target"]["read_status"].pop("agents"))
chk("CR5. a section a card uses that is missing from read_status gives something unread, and its card is red",
    subprocess.run([sys.executable, PART1, "--read-state", p], capture_output=True, text=True).stdout == "something unread\n" and markers(render(p)[1])[2] == R, markers(render(p)[1]))
chk("CR5. hooks-note: Injects is red, Hooks green, and the overall word is something unread",
    subprocess.run([sys.executable, PART1, "--read-state", fx("hooks-note")], capture_output=True, text=True).stdout == "something unread\n", "")

# reviewer's extra cases: Source on its own, a non-dict section, the other refusals
for sec_, state_, want_m in (("plugin_json", "partial", [G, G, G, G, G, Y]), ("marketplace", "failed", [G, G, G, G, G, R]), ("skills", "partial", [Y, G, G, G, G, G])):
    p = variant("plugin-found", lambda d, s=sec_, st=state_: d["target"]["read_status"][s].update(state=st, notes=["x: y"]))
    chk(f"CR2. plugin-found with only {sec_} {state_}: markers {''.join(want_m)}", markers(render(p)[1]) == want_m, markers(render(p)[1]))
p = variant("plugin-found", lambda d: d["target"]["read_status"].update(agents="read"))
chk("CR2. a read_status section that is a string, not a dict, is failed: Subagents and commands is red, --read-state says something unread",
    markers(render(p)[1]) == [G, G, R, G, G, G] and subprocess.run([sys.executable, PART1, "--read-state", p], capture_output=True, text=True).stdout == "something unread\n", markers(render(p)[1]))
junk = os.path.join(tmp(), "junk.json"); open(junk, "w").write("not json")
listrs = variant("plugin-found", lambda d: d["target"].update(read_status=[]))
for what, arg, msg in (("a missing path", os.path.join(tmp(), "nope.json"), "cannot read a dossier from"), ("a file that is not JSON", junk, "cannot read a dossier from"), ("read_status as a list", listrs, "has no read_status")):
    r = subprocess.run([sys.executable, PART1, "--read-state", arg], capture_output=True, text=True)
    chk(f"CR5. --read-state on {what} exits 2 with part1's own message ({msg!r}), printing no word", (r.returncode, r.stdout, msg in r.stderr), (2, "", True))

# Done when 7: card() is the only place card markup is written, and no judgement square sits in a facts card
chk("CR7. a facts report's cards hold no \U0001F7E9\U0001F7E8\U0001F7E7\U0001F7E5 square", not any(sq in render(fx(f))[1] for f in every if f != "hostile" for sq in "\U0001F7E9\U0001F7E8\U0001F7E7\U0001F7E5"), "")   # hostile plants a square on purpose
found = []
for top in ("tools", "skills"):
    for dp, dn, fn in os.walk(os.path.join(NB, top)):
        dn[:] = [x for x in dn if x not in ("fixtures", "__pycache__")]
        for f_ in fn:
            fp_ = os.path.join(dp, f_)
            rel = os.path.relpath(fp_, NB)
            if f_.startswith("test_") or rel == os.path.join("tools", "cards.py"):
                continue
            try:
                txt = open(fp_, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            if "<details><summary>" in txt:
                found.append(rel)
chk("CR7. `<details><summary>` is written nowhere in tools/ or skills/ outside tools/cards.py, tests, fixtures and tools/vet's Rule files block",
    os.path.exists(os.path.join(HERE, "cards.py")) and found == ["tools/vet"], found)
vet_txt = open(os.path.join(HERE, "vet"), encoding="utf-8").read()
chk("CR7. in tools/vet the only `<details><summary>` is the Rule files block", re.findall(r"<details><summary>([^<]*)</summary>", vet_txt) == ["Rule files"], "")

for t_ in TEMPS:
    shutil.rmtree(t_, ignore_errors=True)
print(f"test_part1: {fail} failed" if fail else "test_part1: all passed")
sys.exit(1 if fail else 0)
