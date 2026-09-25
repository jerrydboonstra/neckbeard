<img src="./assets/logo.webp" alt="A bearded developer under a desk lamp, arms crossed, scowling at a terminal full of struck-out lines." width="280">

# neckbeard

[![self-check](https://github.com/jerrydboonstra/neckbeard/actions/workflows/self-check.yml/badge.svg)](https://github.com/jerrydboonstra/neckbeard/actions/workflows/self-check.yml)

> **I read the whole thing. You’re welcome.**
>
> Reads the plugin. Writes the verdict. Edits nothing.

Before you install a plugin into Claude Code, neckbeard reads it for you. Every hook, every string it injects, every session and subagent it reaches, every file it writes outside your project. Then it checks each rule against what you already run and tells you what is duplicate, what conflicts, and what is new. It changes nothing.

## Install it. It adds one skill and nothing else.

Requires Claude Code and Python 3.11 or later (standard library only), plus `git` if you point it at a git URL. Tested on macOS and, in CI, Linux.

```bash
claude plugin marketplace add jerrydboonstra/neckbeard
claude plugin install neckbeard@neckbeard
```

Or as a plain skill, with no plugin machinery at all. Everything neckbeard needs lives in one folder, so a clone and a link are the whole install, and `git pull` is the update:

```bash
git clone https://github.com/jerrydboonstra/neckbeard.git ~/src/neckbeard
mkdir -p ~/.claude/skills
ln -s ~/src/neckbeard/skills/neckbeard ~/.claude/skills/neckbeard
```

Use one or the other, not both: two copies means two skills with the same name.

One skill, zero hooks, zero agents. **About 270 tokens always-on**, the skill's description, which is all Claude Code shows its router so it knows the tool is there; **about 4.7k tokens each time you use it**. Both figures are from `claude plugin details` on 1.12.1 and are the same for either install. It injects nothing at session start and reaches none of your subagents. The plugin that prompted this one injects about 1,300 tokens into every session *and* every subagent, for as long as it is installed.

That gap is the point. A tool that catches plugins for running in the background cannot run in the background. It works when you ask, reports, and stops.

## What you get

One page per plugin, answer first. This is the top of a real report, [ponytail](https://github.com/DietrichGebert/ponytail) against a [sample reader](examples/reader/):

> ## 🟨 COPY RULES, SKIP PLUGIN · take the rule and three skills, skip the always-on injection
> Injects its main skill into every session and every subagent, about 1,300 tokens each time (its 6.6 KB skill file, frontmatter stripped), and writes mode state to files outside the project. Two of its instructions tell the model to proceed on its own where the sample reader's rules say ask first. One new safety rule and three on-demand skills are worth having, and both are cheaper to copy as text than to carry as a permanent injection.
>
> Verdict is relative to the [sample reader](examples/reader/), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](examples/README.md).

`2026-09-24` · neckbeard 1.12.0 · [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)

**⚡ At a glance**

| | | |
|:--:|---|---|
| 🟧 | **Cost** | ~1,300 tokens (its 6.6 KB skill file, frontmatter stripped) at every session start, and again at every subagent start |
| 🟧 | **Reach** | main session + subagents (certain, a `SubagentStart` hook, documented) |
| 🟧 | **Leaves state** | flag/config files outside the project: home config dir and host-specific dirs |
| 🟩 | **Live surface** | no MCP servers, no network calls in its hooks; one nudge asks the model to offer editing settings.json |
| 🟩 | **Refused reads** | none |
| 🟨 | **Worth keeping** | 1 standing rule + 3 on-demand skills |

**🧮 How its rules sorted**

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **2** | 🟥🟥 |
| 🔁 | **already covered** | **5** | ⬜⬜⬜⬜⬜ |
| 🆕 | **new, standing rule** | **1** | 🟩 |
| 🆕 | **new, on-demand skill** | **3** | 🟩🟩🟩 |
| 🗑️ | **dropped** (persona, extras, no value) | **5** | ⬛⬛⬛⬛⬛ |

The full report goes on to list every conflict with the rule it breaks, everything already covered, what is worth keeping, what the plugin installs, and a patch to copy. **[See the gallery](examples/README.md)**: seven public plugins, including this one, all against the same sample reader.

## Why

I nearly installed [ponytail](https://github.com/DietrichGebert/ponytail), the lazy-senior-dev persona plugin. It injects about 1,300 tokens into every session and every subagent, permanently. I asked an LLM to compare its rules with mine, and it told me half of them restated my own config and five contradicted hard stops I rely on (never act on something risky without my approval). I had no good way to tell whether that answer was right. So I copied the rules I wanted into my config as plain text, deleted the plugin, and wrote neckbeard to make that comparison something you can check: every call cites the rule on each side. The method is [Yanhua's](https://x.com/yanhua1010/status/2094612609932910828), who did the same audit by hand, against his own config, and published it. See [ATTRIBUTION.md](./ATTRIBUTION.md).

## Point it at the next plugin before you install it

Ask Claude to "vet this plugin" or "should I install X". From a clone, you can also run the inventory directly:

```bash
bin/neckbeard <target> [--project-dir DIR] [--extra-rules PATH] [--out FILE]
```

`<target>` is one of:

- an **installed plugin**, `name@marketplace` (e.g. `ponytail@ponytail`). It reads `installed_plugins.json` first, falling back to the marketplace manifest when that record has no working `installPath` (true for most directory-source installs, but not all: see [CASE-STUDIES, round 2](CASE-STUDIES.md#2-neckbeard-itself-before-publishing))
- a **local directory**: an already-cloned repo, a skill pack, a plugin source tree
- a **git URL**, cloned read-only, depth 1, into a temp directory that is gone when the command exits

`--project-dir` (default: cwd) is where rule discovery starts. `--extra-rules` adds a file or directory the discovery would otherwise miss.

It prints the dossier to stdout, or writes it to `--out FILE` and warns you what it contains. It writes nothing else.

**A dossier contains your rules, verbatim.** The comparison needs the text, so the dossier embeds every rule file it discovered: your global `CLAUDE.md`, your project rules, your personal skills, the skills of every plugin you have enabled. A run inside this repo produced 90,533 bytes of exactly that. It warns you on write and names the files. Do not commit one, and check your `.gitignore` first. This repo ignores every `.json` except its two manifests, for precisely this reason.

## What it reads, and what it refuses to touch

**The target.** If it carries a plugin manifest, neckbeard reads it as a plugin:

- Every `skills/*/SKILL.md`, at the standard path only. It does not walk the whole repo. A plugin built for several agents also ships copies under `.openclaw/`, `.opencode/` and `.cursor/`, and Claude Code never loads those, so counting them would double the plugin's apparent size.
- Every command and agent definition, in full, since each is an instruction to a model, and a `CLAUDE.md` at its root.
- Every hook event it registers, and whether `SubagentStart` is one of them.
- What each hook injects, where a static read can work that out. It follows one hop of local `require()` and rebuilds `path.join(__dirname, ...)` literals.
- Anything its scripts write to disk outside your project.
- Any **MCP server** the manifest declares, with its name, command and transport. The declaration only: what a server actually exposes is knowable only by speaking MCP to it, which this does not do.

No manifest means a plain pack of rules: neckbeard searches wider for skills, and still checks for hooks, because a directory can carry `hooks/hooks.json` with no manifest at all. A single file works too: point it at someone's `CLAUDE.md` and it compares that file's rules against yours.

**Your rules.** It finds these itself: your global `CLAUDE.md`, the nearest project `CLAUDE.md` above you, every file either one imports with `@path`, your project and personal skills, and the skills of every plugin that project already enables, whether enabled for you, for the project, locally or by managed settings.

It then sorts every rule the target carries into one bucket:

| bucket | means |
|---|---|
| **duplicate** | the same as something you already run. Drop it, cite the source. |
| **conflict** | contradicts a rule you have, especially a hard stop, an approval gate, or a safety rule. Drop it, name the rule. |
| **new, standing behavior** | new, and describes how to build in general. Propose it as a rule. |
| **new, on-demand behavior** | new, and describes a one-shot job. Propose it as a skill, never a rule and never a hook. |

You get an evaluation, not a patch. **It never edits a rules file, never touches `settings.json`, and never uninstalls or disables anything.** Acting on it is a separate step, and yours. A tool that judges what other plugins do to your config does not get to change your config unasked.

## What it does not do

It cannot read an **MCP connector**. Its whole pipeline assumes a target you can clone and grep, and a connector is a live service whose code runs on someone else's machine. Nothing local to read, so nothing it can honestly report. That gap is real and named rather than papered over.

It does not see a subagent dispatch **described in a skill's prose**. A plugin can instruct the main session to call the `Agent` tool twenty times and still report `agents: []`, because it declares no agent files. Zero declared agents is not zero agent behavior.

It resolves hook injection **statically, or says it could not**. A hook that builds its path at runtime from state gets flagged for a human to read, not guessed at.

## How it was tested

Fourteen rounds, each one pointed at something real. **[CASE-STUDIES.md](./CASE-STUDIES.md)** has every round, including the false claims it caught in its own docs.

- **Who reviewed it:** AI agents only. Each was a separate Claude session that had not written the code. The only outside user ran an early version and hit bugs that later rounds fixed.
- **Hardest round:** the ninth, the first by a session outside the build. Eleven problems, four published claims proved false, one of them a path that could leak 90,533 bytes of private rules into a public repo.
- **The code:** checked against the filesystem. Every self-check case has been seen to fail with the code it guards broken.
- **The judgment:** graded blind against two sealed fixtures, built by separate sessions; the author has never seen the answers. On the second, the instructions scored 30 of 31 where the same model without them scored 16.

## The name

Two kinds of hair, two kinds of developer. Ponytail ships the shortest thing that works. Neckbeard reads all 670 lines of your hook code first, and wants the smallest set of good rules and nothing else.

## License

MIT. See [LICENSE](./LICENSE) and [ATTRIBUTION.md](./ATTRIBUTION.md).

Version history, and why the number is high for a first release: [CHANGELOG.md](CHANGELOG.md).
