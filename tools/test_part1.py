#!/usr/bin/env python3
"""tools/part1: "## What it adds", rendered from the dossier by code, and its placement by tools/vet (that part is in tools/test_vet.py).

Fixtures are tools/fixtures/part1/*.json, dossiers written by hand (each carries target.read_status, and in
current_rules a planted rule text, READER-MARKER-7, that no output may hold), plus one real dossier: real-plugin.json,
made by inventory.py on the small plugin tree real_tree() builds. A test runs inventory.py on that tree again and
fails when part1's output for it differs from the output for the stored dossier, so a change in the dossier's shape
shows up here. tools/vet runs against a fake `claude` that writes a fixed report."""
import json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
NB = os.path.dirname(HERE)
PART1 = os.path.join(HERE, "part1")
VET = os.path.join(HERE, "vet")
INVENTORY = os.path.join(NB, "skills", "neckbeard", "inventory.py")
FX = os.path.join(HERE, "fixtures", "part1")
HEADINGS = ["Injects", "Hooks", "Subagents and commands", "State it may leave", "Reaches outside the session", "Source"]
FOOTER = "Load timing follows Claude Code's documented skill loading; tokens are estimated as bytes / 4."
TEMPS = []
fail = checks = 0


def chk(name, ok, detail=""):
    global fail, checks
    checks += 1
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        fail += 1


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


def tmp():
    d = tempfile.mkdtemp(prefix="part1-test-")
    TEMPS.append(d)
    return d


def dossier_of(tree):
    """inventory.py on TREE with an empty config folder and project, so no reader's rules are read."""
    e = tmp()
    env = {"PATH": os.environ["PATH"], "HOME": e, "CLAUDE_CONFIG_DIR": e}
    r = subprocess.run([sys.executable, INVENTORY, tree, "--project-dir", e, "--out", os.path.join(e, "d.json")],
                       env=env, capture_output=True, text=True)
    return os.path.join(e, "d.json") if r.returncode == 0 else None


def render(path, *extra):
    r = subprocess.run([sys.executable, PART1, path, *extra], capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def lines_of(out):
    """{(card, label): rest of the line}, from `- **Card**` and its `  - Label: rest` lines."""
    got, card = {}, None
    for line in out.split("\n"):
        m = re.match(r"^- \*\*(.+)\*\*\s*$", line)
        if m:
            card = m.group(1)
            continue
        m = re.match(r"^  - ([^:]+): (.*)$", line)
        if m and card:
            got[(card, m.group(1))] = m.group(2)
    return got


def state_of(rest):
    for s in ("found", "none", "partly read", "not read", "not applicable"):
        if rest == s or rest.startswith(s + ":") or rest.startswith(s + " "):
            return s
    return rest


CARDS = {
    "Skills": "Injects", "Rule files": "Injects", "Hook-injected text": "Injects", "Hook events": "Hooks",
    "Agents": "Subagents and commands", "Commands": "Subagents and commands", "Persistence candidates": "State it may leave",
    "MCP servers": "Reaches outside the session", "plugin.json": "Source", "Marketplace": "Source",
}
STATES = {  # fixture -> label -> printed state, the five states over every card
    "plugin-found": {k: "found" for k in CARDS},
    "plugin-none": {**{k: "none" for k in CARDS}, "Marketplace": "not applicable"},
    "plugin-partial": {k: "partly read" for k in CARDS},
    "plugin-not-read": {k: "not read" for k in CARDS},
    "old-dossier": {k: "not read" for k in CARDS},
    "rule-file": {**{k: "not applicable" for k in CARDS}, "Rule files": "found"},
}

# ---------------------------------------------------------------- Done when 1: each card, each state
for name, want in STATES.items():
    rc, out, err = render(os.path.join(FX, name + ".json"))
    got = lines_of(out)
    bad = {lab: (state_of(got.get((CARDS[lab], lab), "<missing>")), st) for lab, st in want.items()
           if state_of(got.get((CARDS[lab], lab), "<missing>")) != st}
    chk(f"1. {name}: every card prints its state ({len(want)} lines)", rc == 0 and not bad, f"rc={rc} {bad} {err[-200:]}")

rc, out, _ = render(os.path.join(FX, "plugin-found.json"), "--commit", "abc1234")
got = lines_of(out)
chk("1. found: skills list each skill with its sizes, a truncated one says so",
    "alpha" in got.get(("Injects", "Skills"), "") and "description every session, 21 chars" in got.get(("Injects", "Skills"), "")
    and "the file on demand, 1200 bytes, about 300 tokens" in got.get(("Injects", "Skills"), "")
    and "beta" in got.get(("Injects", "Skills"), "") and "truncated" in got.get(("Injects", "Skills"), ""), got.get(("Injects", "Skills")))
chk("1. found: a rule file loads every session, with its bytes", "every session, 400 bytes, about 100 tokens" in got.get(("Injects", "Rule files"), ""),
    got.get(("Injects", "Rule files")))
chk("1. found: a hook-injected file with its bytes", "hooks/inject.md" in got.get(("Injects", "Hook-injected text"), "")
    and "80 bytes" in got.get(("Injects", "Hook-injected text"), ""), got.get(("Injects", "Hook-injected text")))
ev = got.get(("Hooks", "Hook events"), "")
chk("1. found: each hook event with its matcher and the script's path inside the plugin, no arguments",
    "SessionStart: hooks/run.sh" in ev and "PreToolUse (Bash): hooks/guard.sh" in ev and "--flag" not in ev, ev)
chk("1. found: hooks say whether they reach subagents, with the basis",
    "no (no event known to fire in a subagent)" in got.get(("Hooks", "Hooks reach subagents"), ""), got.get(("Hooks", "Hooks reach subagents")))
chk("1. found: agents and commands by name", "reviewer" in got.get(("Subagents and commands", "Agents"), "")
    and "ship" in got.get(("Subagents and commands", "Commands"), ""))
chk("1. found: persistence candidates sorted", "hooks/run.sh, scripts/install.sh" in got.get(("State it may leave", "Persistence candidates"), ""),
    got.get(("State it may leave", "Persistence candidates")))
mcp = got.get(("Reaches outside the session", "MCP servers"), "")
chk("1. found: each MCP server with its transport, a command's first word, a url's scheme and host only",
    "files (local-process, node)" in mcp and "web (http, https://api.example.com)" in mcp, mcp)
chk("1. found: source says the kind, plugin.json's name and version, and the commit as given",
    "plugin demo" in got.get(("Source", "Target"), "") and "demo, version 1.2.0 (from plugin.json)" in got.get(("Source", "plugin.json"), "")
    and got.get(("Source", "Commit")) == "abc1234", (got.get(("Source", "Target")), got.get(("Source", "plugin.json")), got.get(("Source", "Commit"))))
rc, out, _ = render(os.path.join(FX, "plugin-found.json"))
chk("1. no --commit: the commit line says commit not given", lines_of(out).get(("Source", "Commit")) == "commit not given")
_, out, _ = render(os.path.join(FX, "plugin-partial.json"))
chk("1. partly read: the entries found are listed, then the notes, as not read",
    "alpha" in lines_of(out).get(("Injects", "Skills"), "") and "not read: skills: one entry could not be read (dangling symlink)" in lines_of(out).get(("Injects", "Skills"), ""),
    lines_of(out).get(("Injects", "Skills")))
_, out, _ = render(os.path.join(FX, "plugin-not-read.json"))
chk("1. not read: the inventory's own note is printed", "skills: could not be read (not valid JSON)" in lines_of(out).get(("Injects", "Skills"), "")
    and lines_of(out).get(("Hooks", "Hooks reach subagents")) == "not read", lines_of(out).get(("Injects", "Skills")))
_, out, _ = render(os.path.join(FX, "old-dossier.json"))
chk("1. a dossier with no read_status prints not read, with the reason", "no read_status" in lines_of(out).get(("Injects", "Skills"), ""),
    lines_of(out).get(("Injects", "Skills")))
d = tmp()
t = json.load(open(os.path.join(FX, "plugin-found.json")))
t["target"]["hooks"]["injected_content"] = None
t["target"]["hooks"]["injected_content_note"] = "hook payloads cannot be traced"
json.dump(t, open(os.path.join(d, "x.json"), "w"))
_, out, _ = render(os.path.join(d, "x.json"))
chk("1. a read hooks section whose injected text could not be traced is not read, never none",
    state_of(lines_of(out).get(("Injects", "Hook-injected text"), "")) == "not read", lines_of(out).get(("Injects", "Hook-injected text")))

# ---------------------------------------------------------------- Done when 2: byte-identical, six headings, footer
every = sorted(f for f in os.listdir(FX) if f.endswith(".json"))
bad = []
for f in every:
    a, b = render(os.path.join(FX, f), "--commit", "abc1234"), render(os.path.join(FX, f), "--commit", "abc1234")
    if a[1] != b[1] or a[0] != 0:
        bad.append(f"{f}: not identical or exit {a[0]}")
    if not a[1].startswith("## What it adds\n") or any(f"- **{h}**" not in a[1] for h in HEADINGS) or FOOTER not in a[1]:
        bad.append(f"{f}: heading, a card or the footer missing")
chk(f"2. every fixture ({len(every)}) renders twice byte-identical, with the section heading, six cards and the footer", not bad and len(every) >= 7, "; ".join(bad[:3]))

# ---------------------------------------------------------------- Done when 4: nothing private in any output
home = os.path.expanduser("~")
banned = ["READER-MARKER-7", "/Users/", home, "secretarg", "/v1/secret", "token=abc123", "ENVVALUE-9", "/proj/demo"]
bad = []
for f in every:
    out = render(os.path.join(FX, f), "--commit", "abc1234")[1]
    bad += [f"{f}: {b}" for b in banned if b in out] + ([f"{f}: no output"] if not out.strip() else [])
chk("4. no fixture's output holds the reader's rule text, a home path, a hook's arguments, a url path or query, or an env value", not bad, "; ".join(bad[:4]))

# ---------------------------------------------------------------- the real dossier, and drift
tree = tmp(); real_tree(tree)
live = dossier_of(tree)
stored = os.path.join(FX, "real-plugin.json")
if live:
    a, b = render(live, "--commit", "abc1234"), render(stored, "--commit", "abc1234")
    chk("5. inventory.py's output today renders the same as the stored real dossier", a[0] == 0 and a[1] == b[1] and a[1] != "", f"{a[2][-200:]}\n{a[1]}\n---\n{b[1]}")
    got = lines_of(a[1])
    chk("5. the real dossier shows each card found",
        all(state_of(got.get((CARDS[l], l), "")) == "found" for l in ("Skills", "Hook events", "Hook-injected text", "Agents", "Commands", "MCP servers", "plugin.json")), got)
else:
    chk("5. inventory.py ran on the real tree", False)

for t_ in TEMPS:
    shutil.rmtree(t_, ignore_errors=True)
print(f"test_part1: {fail} failed" if fail else "test_part1: all passed")
sys.exit(1 if fail else 0)
