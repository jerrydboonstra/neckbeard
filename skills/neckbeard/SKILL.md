---
name: neckbeard
description: >-
  Vet a plugin, skill pack, or rule file before adopting it: inventory what it
  actually injects and when (hooks, whether it reaches subagents, any state it
  persists to disk), auto-discover the rules already in force (global and
  project CLAUDE.md, project and personal skills, other enabled plugins), then
  classify every rule the target carries as a duplicate of something already
  covered, a conflict with an existing hard-stop or safety rule, or genuinely
  new — and only then propose a patch. Never edits a rule file, never
  uninstalls or disables anything; writes an evaluation and stops. Triggers:
  "vet this plugin", "should I install X", "compare X to my rules", "neckbeard
  this", "audit this skill pack before I adopt it", "what does this plugin
  actually inject".
---

# neckbeard

Reads the whole thing before it trusts the plugin. A one-shot report, not a
persona: nothing here should ever be injected into a session or a subagent.
The point is to stop that from happening to the *target*, so the tool
practicing the opposite would be the whole method failing on itself.

## Step 1 — Run the inventory

The inventory script sits in this skill's own directory, next to this file,
so it runs the same way whether neckbeard arrived as a plugin or as a plain
skill folder. Claude Code shows the skill's base directory when the skill
loads; use it:

```bash
python3 <this skill's directory>/inventory.py <target> [--project-dir DIR] [--extra-rules PATH]
```

If the base directory was not shown, find the script rather than guess:
`find ~/.claude -path "*/neckbeard/inventory.py" 2>/dev/null`. More than one
hit means more than one copy is installed (a plugin cache and a skill folder,
or two cached versions); prefer the one whose `SKILL.md` you are reading, and
say which you used.

`<target>` is an installed plugin (`name@marketplace`, e.g. `ponytail@ponytail`
— check `enabledPlugins` in your settings for the exact key), a local
directory (an already-cloned repo or skill pack), a single rule file (a
`CLAUDE.md` or any markdown of rules), or a git URL (cloned read-only into a
temp dir, depth 1). `--project-dir` defaults to the cwd and
controls where current-rules discovery starts; pass it explicitly when vetting
a plugin for a project other than the one you're sitting in. `--extra-rules`
adds a file or directory to the current-rules corpus when the auto-discovery
below would miss something (a rules file with a name Claude Code doesn't look
for on its own).

The script prints one JSON dossier: `target` (what the thing actually does —
its manifest, every skill, command and agent it bundles with their full text,
any `CLAUDE.md` at its root under `rule_files`, every hook it registers and
what each one injects where that's staticly resolvable, whether
`SubagentStart` is among its hooked events, and any file-write patterns found
in its scripts) and
`current_rules` (every rule already in force, auto-discovered from):

- `~/.claude/CLAUDE.md`
- the nearest `CLAUDE.md` walking up from `--project-dir`
- every file either of those imports with `@path`, followed the way Claude Code
  follows it (up to five hops, never inside code). Each import is its own item,
  with `imported_from` naming the file that pulled it in
- `.claude/skills/*/SKILL.md` in that project, and `~/.claude/skills/*/SKILL.md`
- every plugin enabled for that project, each one's bundled skills.
  `enabledPlugins` is merged the way Claude Code layers settings: the user's
  `~/.claude/settings.json`, then the project's `.claude/settings.json`, then
  `.claude/settings.local.json`, then managed settings, each overriding the one
  before. A settings file that does not parse is skipped with a warning on
  stderr, and the plugins it enables are then missing from the comparison.

The script makes no judgment calls: it only reads and counts. If it reports
`injected_content_note`, read the hook scripts it names before concluding
anything about them. Every hook lands in exactly one of three places, and they
mean different things:

- **`injected_content`** — resolved. This is what it injects.
- **`unresolved_hooks`** — the script was found, its payload could not be
  traced. Behaviour unknown, not absent.
- **`unidentifiable_hooks`** — the command could not be tied to a file at all.
  A larger unknown than the one above, and the one most likely to matter.

**Never read a hook's absence from `injected_content` as "it injects
nothing."** Check the other two lists first. An earlier version of this
sentence said a hook missing from both lists genuinely had nothing to inject,
which was false for any command shape the resolver did not recognise, and a
real plugin injecting 3,192 bytes at every session start hit exactly that
(found 2026-09-19).

**An item marked `refused` resolved outside the target, usually through a
symlink or a `../` path, and was not read.** A plugin has no honest reason to
reach outside its own tree, so report every refusal in the evaluation as a
finding in its own right, never skip it as noise.

**The dossier embeds those rule files verbatim, and that makes it sensitive.**
The comparison needs the text, so `current_rules` carries the full contents of
the user's global `CLAUDE.md`, their project rules, their personal skills and
the skills of every plugin they have enabled. A run inside this plugin's own
repo produced 90,533 bytes of it. The script warns on write and names the
files. Never commit a dossier, never paste one anywhere public, and check the
`.gitignore` of wherever you are writing it before you write it.

## Step 2 — Classify every rule the target carries

For each item under `target.skills`, `target.rule_files`, `target.commands`
and `target.agents` (and, for a plugin, the text any resolved
`injected_content` file carries), compare it against every item in
`current_rules.items` and sort it into exactly one bucket. A command or an
agent is an instruction to a model like any skill; do not skip it because it
only runs when invoked.

- **duplicate** — functionally the same as something already in force. Drop
  it. Cite the exact existing source (`current_rules` item's `source` and
  `path`). **When more than one source covers the same ground, cite the one
  that states it as a rule in its own right, not the one that mentions it in
  passing inside another rule, and say why you chose it.** A rule can also
  duplicate a *skill* rather than a rules file; check both.
- **conflict** — contradicts an existing rule, especially a hard stop, an
  approval gate, a safety requirement, or a verification requirement. Drop it.
  Name the specific conflicting rule and its file — not "this could conflict
  with something," the actual sentence and where it lives.
- **new, standing behavior** — genuinely new, doesn't conflict, describes how
  to build or work in general. Propose it as a rule.
- **new, on-demand behavior** — genuinely new, describes a one-shot capability
  rather than something that should run every time. Propose it as a small
  skill, never a standing rule and never a hook.

Weigh the carrying cost from `target.hooks` against what's actually kept. A
rough line that has held up: if the target injects on every session or reaches
subagents, it needs at least one rule you would have written yourself to be
worth installing rather than copying. **If exactly one rule survives, say so
and let the reader decide**: one good rule is almost always cheaper to copy as
text than to carry as a permanent injection, and the honest output is to name
that trade rather than resolve it for them. Zero hooks and zero always-on cost means
there is nothing to weigh, and the only question is whether the rules are good.
Say which of those three cases you are in. The older wording said to weigh the
cost and gave no criterion at all: a
plugin that injects a few hundred bytes at session start for one rule you'd
keep anyway is a bad trade even if that one rule is new.

## Step 3 — Write the evaluation

Default output: `evaluations/<slug>.md` if that directory exists under the
current project (or its root), where `<slug>` is the target's plugin or repo
name in kebab-case. Otherwise ask where it should go, or accept an explicit
path from the user. **Before writing, check that the path is ignored by git**
(`git check-ignore <path>`). The evaluation quotes the user's own rules, and
the project you are sitting in is usually not this plugin's repo, so this
plugin's `.gitignore` protects nothing there. If the path is not ignored, say
so and ask before writing.

**Write it in this shape.** The reader wants the answer first and a grid they can
scan, not an essay. Rules:

- **Answer first.** The banner holds the verdict and at most three sentences.
- **Grids over prose.** One row per item; a cell is a phrase, not a paragraph.
  No section opens with a paragraph.
- **Every rule gets a symbol and lands in exactly one grid.** The counts in "How
  its rules sorted" must equal the rows in the grids below it.
- **Cite, don't gesture.** A conflict names the rule it collides with and the
  file or skill that holds it. A duplicate names what covers it.
- **Bars:** one block per item, up to 10; above 10, write `▰ ×N`.
- Plain Markdown only (tables, one blockquote, emoji), so it renders the same in
  a terminal viewer, on GitHub and in an editor. No HTML, no `[ ]` checkboxes.
- If a section would be empty, keep its heading and say so in one line.

**Verdict** (one, in the banner): 🟥 DON'T INSTALL / UNINSTALL · 🟧 INSTALL WITH
CHANGES · 🟨 COPY RULES, SKIP PLUGIN · 🟩 INSTALL. Step 2's carrying-cost line
decides between 🟨 and 🟩: a target whose only value is one or two rules is
cheaper copied as text than carried as an injection.

```
# 🔍 <target> <version> · vetted against your rules

> ## <verdict emoji> <VERDICT> · <one-phrase action>
> <Two or three sentences: what it costs, what it fights, what is worth keeping.>

`<YYYY-MM-DD>` · neckbeard <version> · <target path or URL>

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟥/🟧/🟨/🟩 | **Cost** | <bytes injected, and when> |
| .. | **Reach** | <main session only / + subagents (certain / likely)> |
| .. | **Leaves state** | <files written outside the project, or none found> |
| .. | **Live surface** | <MCP servers, network, commands it runs; or none> |
| .. | **Refused reads** | <count of `refused` items, or none>; any refusal is 🟥 |
| .. | **Worth keeping** | <N rules or skills> |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **n** | 🟥 per item |
| 🔁 | **already covered** | **n** | ⬜ per item |
| 🆕 | **new, standing rule** | **n** | 🟩 per item |
| 🆕 | **new, on-demand skill** | **n** | 🟩 per item |
| 🗑️ | **dropped** (persona, extras, no value) | **n** | ⬛ per item |

## ⛔ Conflicts: n
| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|

## 🔁 Already covered: n
| its rule | covered by | held in |
|---|---|---|

## 🟩 Keep: n
| # | rule or skill | kind | |
|:--:|---|:--:|:--:|

## 🗑️ Dropped
`<item>` · `<item> (⛔n)` · ...

## 🧩 What it installs
| surface | when | reaches subagents | size |
|---|---|:--:|--:|

## ✅ Do this
- ⬜ 1. <first action>
<One line: which of Step 2's three carrying-cost cases applies.>

## 📋 Proposed rules patch
<Step 4's patch, or "nothing to add".>

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped ·
⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
```

`examples/` in this plugin's repository holds real reports in this shape, run
against a published sample reader.

## Step 4 — Propose the rules patch

If Step 2 produced any "new, standing behavior" rules, propose them as
additions to the user's global rules file (`~/.claude/CLAUDE.md` for Claude
Code), matching whatever numbering and emphasis that file already uses.

**Do not assume a section name.** Read the file and put the rules where they
belong: an existing section about how code gets written if there is one, a new
section if there is not, and say which you are proposing. An earlier version of
this instruction named one specific heading, which existed only on its author's
machine, so any reader whose file was organised differently had to guess
(found 2026-09-19 by an evaluation of this step).

Rules live inline while the list is short. Once the section grows past roughly
40 lines, propose splitting it into its own rules file and leaving a summary
and a pointer behind, if that is a pattern the user's setup already uses.

Provenance does not go in the rules section: the evaluation document itself is
the record of where a rule came from and what was rejected alongside it. Put
dated field notes there too, not in the global file, which is read in full
every session.

If any "new, on-demand behavior" skills came out of Step 2, propose them as
skills rather than as rules. Give a proposed name and a one-line description,
and mark the name as your proposal, since the target usually does not name the
capability itself. Suggest where it should live only if the dossier tells you
where this user keeps skills; if it does not, say so and leave the choice to
them rather than inventing a path.

**Show the proposed patch as a diff or a fenced block in the evaluation
document. Do not write it into `CLAUDE.md`, a rules file, or
`settings.json` yourself, and do not uninstall or disable the target.**
Applying any of it is a separate, explicitly-approved step. This skill's whole point is to
add a rule only when it earns its keep; auto-applying its own output would
skip the one review step that makes that true.
