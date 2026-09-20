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

```bash
find "${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins}" "$HOME/.claude/plugins/cache" \
     -path "*/neckbeard/bin/neckbeard" 2>/dev/null | head -1
```

Two paths because a **directory** marketplace usually resolves in place with
no cache copy, while a **GitHub** install lives only in the cache. "Usually":
if the directory is itself a git repo, Claude Code may cache it anyway, keyed
to `plugin.json`'s version, and that cache does not refresh on its own when
the version number does not change (see "Ran on itself" in the README).
`CLAUDE_PLUGIN_ROOT` covers the in-place case when it is set. If neither
lookup finds it, the plugin is checked out somewhere else entirely, and
`find <that directory> -path "*/bin/neckbeard"` gets you there. Then:

```bash
<path-to>/bin/neckbeard <target> [--project-dir DIR] [--extra-rules PATH]
```

`<target>` is an installed plugin (`name@marketplace`, e.g. `ponytail@ponytail`
— check `.claude/settings.json`'s `enabledPlugins` for the exact key), a local
directory (an already-cloned repo or skill pack), or a git URL (cloned
read-only into a temp dir, depth 1). `--project-dir` defaults to the cwd and
controls where current-rules discovery starts; pass it explicitly when vetting
a plugin for a project other than the one you're sitting in. `--extra-rules`
adds a file or directory to the current-rules corpus when the auto-discovery
below would miss something (a rules file with a name Claude Code doesn't look
for on its own).

The script prints one JSON dossier: `target` (what the thing actually does —
its manifest, every skill it bundles, every hook it registers and what each
one injects where that's staticly resolvable, whether `SubagentStart` is among
its hooked events, and any file-write patterns found in its scripts) and
`current_rules` (every rule already in force, auto-discovered from):

- `~/.claude/CLAUDE.md`
- the nearest `CLAUDE.md` walking up from `--project-dir`
- `.claude/skills/*/SKILL.md` in that project, and `~/.claude/skills/*/SKILL.md`
- every plugin enabled for that project (`.claude/settings.json`'s
  `enabledPlugins`), each one's bundled skills

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

**The dossier embeds those rule files verbatim, and that makes it sensitive.**
The comparison needs the text, so `current_rules` carries the full contents of
the user's global `CLAUDE.md`, their project rules, their personal skills and
the skills of every plugin they have enabled. A run inside this plugin's own
repo produced 90,533 bytes of it. The script warns on write and names the
files. Never commit a dossier, never paste one anywhere public, and check the
`.gitignore` of wherever you are writing it before you write it.

## Step 2 — Classify every rule the target carries

For each item under `target.skills` (and, for a plugin, the text any resolved
`injected_content` file carries), compare it against every item in
`current_rules.items` and sort it into exactly one bucket:

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
path from the user. Follow this exact section shape (it is what
proved out by hand on ponytail — see that file for a worked example if one
exists in the corpus you can reach):

```
# Evaluation: <target> against <user>'s rules

Date, method (this skill), link/source of the target.

## What is installed / what the target is
Where it lives, what enables it, what it bundles.

## What it says
One-paragraph summary of its actual behavior, in its own terms.

## Overlap with what is already in force
Table or list: target rule -> what already covers it.

## Conflicts
Numbered. Each one names the exact contradicting rule and its file.

## Keep
The rules and skills that are genuinely new. For each: rule text, or
skill name + one-line description. Say which are standing rules
vs. on-demand skills.

## Drop
Everything else, briefly, with the one-line reason.

## Recommendation
Keep as installed / adopt rules only and uninstall / adopt nothing.
```

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
Applying any of it is a separate, explicitly-approved step — the same posture
`list-item` takes before publishing a listing. This skill's whole point is to
add a rule only when it earns its keep; auto-applying its own output would
skip the one review step that makes that true.
