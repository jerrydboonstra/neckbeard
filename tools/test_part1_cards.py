#!/usr/bin/env python3
"""tools/part1's collapsible cards (part1-colour-rules): the legend, each card's read marker and gist, escaping in tools/cards.py,
`part1 --read-state`, and that card markup is written only by tools/cards.py. Split from tools/test_part1.py to stay under the
test-module size cap; it uses the same fixtures (tools/fixtures/part1/<name>.dossier.json)."""
import json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
NB = os.path.dirname(HERE)
PART1 = os.path.join(HERE, "part1")
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
    d = tempfile.mkdtemp(prefix="part1-cards-test-")
    TEMPS.append(d)
    return d


def fx(name):
    return os.path.join(FX, name + ".dossier.json")


def render(path, *extra):
    r = subprocess.run([sys.executable, PART1, path, *extra], capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def variant(name, edit):
    d = json.load(open(fx(name)))
    edit(d)
    p = os.path.join(tmp(), "d.json")
    json.dump(d, open(p, "w"))
    return p


def parse(out):
    """{(card, label): (rest of the label's line, [its `  - ` lines])}, `&lt;` read back as `<`."""
    got, card, cur = {}, None, None
    for line in out.split("\n"):
        line = line.replace("&lt;", "<")
        m = re.match(r"^<details><summary>(?:\U0001F7E2|\U0001F7E1|\U0001F534) <b>(.*?)</b>", line)
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
    if entry is None:
        return "missing"
    rest, _ = entry
    for s in ("none", "partly read", "not read", "not applicable"):
        if rest == s or rest.startswith(s + ":"):
            return s
    if rest.startswith(("neckbeard did not read: ", "broken in the plugin: ")):
        return "not read"
    return "entries" if rest == "" else rest


every = sorted(f[: -len(".dossier.json")] for f in os.listdir(FX) if f.endswith(".dossier.json") and f != "old-dossier.dossier.json")

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
    len(cards(out)) == 6 and ["- Skills:", "  - alpha: description every session (21 chars); the file on demand (1200 bytes, ~300 tokens)"] == [l for l in cards(out)[0][3] if l][:2]
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
runs_ = [subprocess.run([sys.executable, PART1, *a], capture_output=True, text=True)
         for a in (["--read-state", fx("plugin-found"), fx("plugin-found")], ["--read-state", fx("plugin-found"), "--commit", "abc"], ["--read-state"])]
chk("CR5. --read-state with a second argument, or with --commit, or with no dossier, exits 2, prints the usage and no word",
    all(r.returncode == 2 and r.stdout == "" and "usage: part1" in r.stderr and "--read-state" in r.stderr for r in runs_), [(r.returncode, r.stderr[:60]) for r in runs_])
emp = variant("plugin-found", lambda d: d["target"].update(read_status={}))
r = subprocess.run([sys.executable, PART1, "--read-state", emp], capture_output=True, text=True)
chk("CR5. --read-state on an empty read_status exits 2 as vet did before (no read_status)", (r.returncode, r.stdout, "has no read_status" in r.stderr), (2, "", True))
# a partly read section with nothing found makes no count claim; a read one with nothing found does
for sec_, label_ in (("agents", "Subagents and commands"), ("mcp_servers", "Reaches outside the session"), ("hooks", "Hooks")):
    def edit(d, s=sec_):
        d["target"]["read_status"][s].update(state="partial", notes=["x: y"])
        d["target"][{"agents": "agents", "mcp_servers": "mcp_servers", "hooks": "hooks"}[s]] = [] if s == "agents" else ({"servers": []} if s == "mcp_servers" else {"events": {}, "injected_content": [], "hooks_reach_subagents": None})
    g_ = card_gist(render(variant("plugin-found", edit))[1], label_) or ""
    chk(f"CR1. {sec_} partly read with nothing found: the gist claims no zero ('no agents', 'no MCP servers', '0 hooks')", not re.search(r"\bno agents\b|\bno MCP servers\b|\b0 hooks\b", g_), g_)
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
            if f_.startswith("test_") or rel in (os.path.join("tools", "cards.py"), os.path.join("tools", "vet-stability")):   # vet-stability reads cards, it writes none
                continue
            try:
                txt = open(fp_, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            if "<details><summary>" in txt:
                found.append(rel)
chk("CR7. `<details><summary>` is written nowhere in tools/ or skills/ outside tools/cards.py, tests, fixtures, tools/vet-stability (a reader) and tools/vet's Rule files block",
    os.path.exists(os.path.join(HERE, "cards.py")) and found == ["tools/vet"], found)
vet_txt = open(os.path.join(HERE, "vet"), encoding="utf-8").read()
chk("CR7. in tools/vet the only `<details><summary>` is the Rule files block", re.findall(r"<details><summary>([^<]*)</summary>", vet_txt) == ["Rule files"], "")

# card() with an empty marker (summary-cards): the summary line drops the marker and its space
sys.path.insert(0, HERE)
import cards as cards_mod
chk("CR8. card() with an empty marker writes `<details><summary><b>name</b>` with no marker and no space",
    cards_mod.card("", "At a glance in full", "", ["x"])[0] == "<details><summary><b>At a glance in full</b></summary>", cards_mod.card("", "At a glance in full", "", ["x"])[0])
chk("CR8. an empty marker with a gist keeps the gist", cards_mod.card("", "N", "g", [])[0] == "<details><summary><b>N</b> \u00b7 g</summary>", cards_mod.card("", "N", "g", [])[0])
chk("CR8. a marker still prints marker, space, name as before", cards_mod.card("\U0001F7E2", "N", "", [])[0] == "<details><summary>\U0001F7E2 <b>N</b></summary>", cards_mod.card("\U0001F7E2", "N", "", [])[0])

for t_ in TEMPS:
    shutil.rmtree(t_, ignore_errors=True)
print(f"test_part1_cards: {fail} failed" if fail else "test_part1_cards: all passed")
sys.exit(1 if fail else 0)
