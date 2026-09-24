<img src="./assets/logo.svg" alt="" width="360">

# neckbeard

> **Ponytail ships it. Neckbeard reads it first.**
>
> Reads the plugin. Writes the verdict. Edits nothing.

Before you install a plugin into Claude Code, neckbeard reads it for you. Every
hook, every string it injects, every session and subagent it reaches, every file
it writes outside your project. Then it checks each rule against what you already
run and tells you what is duplicate, what conflicts, and what is new. It changes
nothing.

A tool that asks you to trust its measurements should show its own. Fourteen
rounds of adversarial testing, what each one cost this tool, and the published
claims that turned out false: **[CASE-STUDIES.md](./CASE-STUDIES.md)**.

## Why

I nearly installed [ponytail](https://github.com/DietrichGebert/ponytail), the
lazy-senior-dev persona plugin, then read it instead: 1,300 tokens injected into
every session and every subagent, permanently, with half its rules restating my
own config, five contradicting hard stops I rely on (never act on something risky
without my approval), and five worth keeping. I copied those into my config as
plain text, deleted the plugin, and wrote neckbeard so the next read
takes minutes instead of an afternoon. The method is
[Yanhua's](https://x.com/yanhua1010/status/2094612609932910828), who did the same
audit by hand and published it. See [ATTRIBUTION.md](./ATTRIBUTION.md).

## Install it. It registers nothing.

```bash
claude plugin marketplace add jerrydboonstra/neckbeard
claude plugin install neckbeard@neckbeard
```

One skill, zero hooks, zero agents, and **~266 tokens always-on**: its manifest
description plus the skill's frontmatter, the two strings Claude Code shows its
router so it knows the tool is there. It injects nothing at
session start and reaches none of your subagents. The plugin that prompted this
one injects about 1,300 tokens into every session *and* every subagent, forever.

That gap is the point. A tool that catches plugins for running in the background
cannot run in the background. It works when you ask, reports, and stops.

## Point it at the next plugin before you install it

Ask Claude to "vet this plugin" or "should I install X", or run the inventory
directly:

```bash
bin/neckbeard <target> [--project-dir DIR] [--extra-rules PATH]
```

`<target>` is one of:

- an **installed plugin**, `name@marketplace` (e.g. `ponytail@ponytail`). It
  reads `installed_plugins.json` first, falling back to the marketplace
  manifest when that record has no working `installPath` (true for most
  directory-source installs, but not all: see "Ran on itself" below)
- a **local directory**: an already-cloned repo, a skill pack, a plugin source tree
- a **git URL**, cloned read-only, depth 1, into a temp directory that is gone
  when the command exits

`--project-dir` (default: cwd) is where rule discovery starts. `--extra-rules`
adds a file or directory the discovery would otherwise miss.

The command prints one JSON dossier and writes nothing outside `--out`.

**A dossier contains your rules, verbatim.** The comparison needs the text, so
the dossier embeds every rule file it discovered: your global `CLAUDE.md`, your
project rules, your personal skills, the skills of every plugin you have
enabled. A run inside this repo produced 90,533 bytes of exactly that. It warns
you on write and names the files. Do not commit one, and check your
`.gitignore` first. This repo ignores every `.json` except its two manifests,
for precisely this reason.

## What it reads, and what it refuses to touch

**The target.** If it carries a plugin manifest, neckbeard reads it as a plugin:

- Every `skills/*/SKILL.md`, at the standard path only. It does not walk the
  whole repo. A plugin built for several agents also ships copies under
  `.openclaw/`, `.opencode/` and `.cursor/`, and Claude Code never loads those,
  so counting them would double the plugin's apparent size.
- Every command and agent definition, in full, since each is an instruction to
  a model, and a `CLAUDE.md` at its root.
- Every hook event it registers, and whether `SubagentStart` is one of them.
- What each hook injects, where a static read can work that out. It follows one
  hop of local `require()` and rebuilds `path.join(__dirname, ...)` literals.
- Anything its scripts write to disk outside your project.
- Any **MCP server** the manifest declares, with its name, command and
  transport. The declaration only: what a server actually exposes is knowable
  only by speaking MCP to it, which this does not do.

No manifest means a plain pack of rules: neckbeard searches wider for skills,
and still checks for hooks, because a directory can carry `hooks/hooks.json`
with no manifest at all. A single file works too: point it at someone's
`CLAUDE.md` and it compares that file's rules against yours.

**Your rules.** It finds these itself: your global `CLAUDE.md`, the nearest
project `CLAUDE.md` above you, every file either one imports with `@path`, your project and personal skills, and the skills
of every plugin that project already enables, whether enabled for you, for the
project, locally or by managed settings.

It then sorts every rule the target carries into one bucket:

| bucket | means |
|---|---|
| **duplicate** | the same as something you already run. Drop it, cite the source. |
| **conflict** | contradicts a rule you have, especially a hard stop, an approval gate, or a safety rule. Drop it, name the rule. |
| **new, standing behavior** | new, and describes how to build in general. Propose it as a rule. |
| **new, on-demand behavior** | new, and describes a one-shot job. Propose it as a skill, never a rule and never a hook. |

You get an evaluation, not a patch. **It never edits a rules file, never touches
`settings.json`, and never uninstalls or disables anything.** Acting on it is a
separate step, and yours. A tool that judges what other plugins do to your config
does not get to change your config unasked.

## What it does not do

It cannot read an **MCP connector**. Its whole pipeline assumes a target you
can clone and grep, and a connector is a live service whose code runs on
someone else's machine. Nothing local to read, so nothing it can honestly
report. That gap is real and named rather than papered over.

It does not see a subagent dispatch **described in a skill's prose**. A plugin
can instruct the main session to call the `Agent` tool twenty times and still
report `agents: []`, because it declares no agent files. Zero declared agents
is not zero agent behavior.

It resolves hook injection **statically, or says it could not**. A hook that
builds its path at runtime from state gets flagged for a human to read, not
guessed at.

## Where it has run, and what each run cost it

Fourteen rounds so far. The ninth was an independent audit by a reviewer who
did not build this, and it found eleven problems and proved four published
claims false, including one where an evaluation could have leaked 90,533 bytes
of private rules into a public repo. Eight of the first nine rounds cost this
tool a bug or a named limit. The first clean result was the re-audit that closed
round twelve.

The mechanical half is checked against the filesystem. The judgment half, which
no filesystem can contradict, is checked against a held-out fixture built by
that same outside reviewer, whose answers the author has never seen.

Full write-ups, including the false claim it caught in its own README:
**[CASE-STUDIES.md](./CASE-STUDIES.md)**.

## The name

Two kinds of hair, two kinds of developer. Ponytail ships the shortest thing that
works. Neckbeard reads all 670 lines of your hook code first, and wants the
smallest set of good rules and nothing else.

## License

MIT. See [LICENSE](./LICENSE) and [ATTRIBUTION.md](./ATTRIBUTION.md).

Version history, and why the number is high for a first release:
[CHANGELOG.md](CHANGELOG.md).
