<img src="./assets/logo.webp" alt="A bearded developer under a desk lamp, arms crossed, scowling at a terminal full of struck-out lines." width="280">

# neckbeard

[![self-check](https://github.com/jerrydboonstra/neckbeard/actions/workflows/self-check.yml/badge.svg)](https://github.com/jerrydboonstra/neckbeard/actions/workflows/self-check.yml) [![neckbeard report: 1.17.1 · partly read](https://img.shields.io/badge/neckbeard%20report-1.17.1%20%C2%B7%20partly%20read-yellow?logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI%2BPG1hc2sgaWQ9Im0iPjxyZWN0IHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgZmlsbD0iI2ZmZiIvPjxwYXRoIGQ9Ik02LjYgOC4yIDEwLjkgOS42IDEwLjYgMTAuNiA2LjMgOS4yWiBNMTcuNCA4LjIgMTMuMSA5LjYgMTMuNCAxMC42IDE3LjcgOS4yWiIgZmlsbD0iIzAwMCIvPjxyZWN0IHg9IjgiIHk9IjExLjEiIHdpZHRoPSIyLjIiIGhlaWdodD0iMS4xIiBmaWxsPSIjMDAwIi8%2BPHJlY3QgeD0iMTMuOCIgeT0iMTEuMSIgd2lkdGg9IjIuMiIgaGVpZ2h0PSIxLjEiIGZpbGw9IiMwMDAiLz48cGF0aCBkPSJNOS44IDE2LjIgQzExIDE1LjQgMTMgMTUuNCAxNC4yIDE2LjIgTDEzLjkgMTYuOSBDMTIuOCAxNi4zIDExLjIgMTYuMyAxMC4xIDE2LjlaIiBmaWxsPSIjMDAwIi8%2BPC9tYXNrPjxnIG1hc2s9InVybCgjbSkiIGZpbGw9IiNmZmYiPjxjaXJjbGUgY3g9IjciIGN5PSI3LjIiIHI9IjMuNCIvPjxjaXJjbGUgY3g9IjEwLjMiIGN5PSI0LjYiIHI9IjMuNCIvPjxjaXJjbGUgY3g9IjEzLjciIGN5PSI0LjYiIHI9IjMuNCIvPjxjaXJjbGUgY3g9IjE3IiBjeT0iNy4yIiByPSIzLjQiLz48ZWxsaXBzZSBjeD0iMTIiIGN5PSIxMC41IiByeD0iNi44IiByeT0iNi44Ii8%2BPHBhdGggZD0iTTQuNiAxMS41IEM0LjIgMTYgNS44IDE5LjYgOC4yIDIxLjQgTDkuNiAyMyAxMSAyMiAxMiAyMy42IDEzIDIyIDE0LjQgMjMgMTUuOCAyMS40IEMxOC4yIDE5LjYgMTkuOCAxNiAxOS40IDExLjUgWiIvPjwvZz48L3N2Zz4%3D)](docs/neckbeard-report.md)

The yellow badge means "partly read". neckbeard's own report names each gap, and two are on purpose: test files under `tools/fixtures` that are broken on purpose, and one source file, `inventory.py`, that is bigger than the most neckbeard reads of one file (50,000 bytes).

> **I read what I could. I tell you what I couldn’t.**
>
> Reads the plugin. Lists what it adds. Edits nothing.

Before you install a plugin into Claude Code, neckbeard reads it for you and lists what it would add to every session. A **hook** is a script Claude Code runs on its own at an event, such as the start of a session. A **subagent** is a helper session that Claude starts for one job. neckbeard lists the hooks, the text a plugin injects, the sessions and subagents it reaches, and the files it may write outside your project, and says which parts it could not read. That list is the **facts report**. Optionally, it then compares each rule the plugin carries with the rules you already run and tells you which of its rules duplicate one of yours, which contradict one, and which are new. That is the **fit report**, and it needs your own rules. It changes nothing.

**Tested by trying to break it, fifteen times, and every round is published.** Each [case study](CASE-STUDIES.md) shows what the tool printed and what that round cost it: the bug, the version that fixed it, and the check that guards it now.

## Try it: three lines, then the report

```bash
git clone https://github.com/jerrydboonstra/neckbeard && cd neckbeard
tools/vet . report.md --facts
cat report.md
```

The `.` is the plugin's folder, so this reads neckbeard itself; give another plugin's folder to read that one. It needs Python 3.11 or later and no login. The report opens with a title, a header line (date, neckbeard version, the plugin's version and commit) and one section per kind of thing the plugin adds. This is neckbeard's own, cut down to its headings and top-level bullets ([the full report](docs/neckbeard-report.md) lists every skill and file):

<!-- report:docs/neckbeard-report -->
> # 🔍 neckbeard 1.17.1 · what it adds
>
> `2026-11-14` · neckbeard 1.17.1 · [jerrydboonstra/neckbeard](https://github.com/jerrydboonstra/neckbeard) 1.17.1 @ `aa64129`
>
> ### Injects
> - Skills:
> - Rule files: none
> - Hook-injected text: partly read
>
> ### Hooks
> - Hooks: partly read
>
> ### Subagents and commands
> - Agents: none
> - Commands: none
>
> ### State it may leave
> - Persistence candidates: partly read
>
> ### Reaches outside the session
> - MCP servers: none
>
> ### Source
> - Kind: plugin
> - Name: neckbeard (from plugin.json)
> - Version: 1.17.1 (from plugin.json)
> - plugin.json:
> - Marketplace: none
> - Commit: aa64129
<!-- /report -->

**Injects** is the text a plugin adds to the model's context, **Hook-injected text** is what its hooks add, **Persistence candidates** are scripts that might write files outside your project, and **MCP servers** are defined below. A fit verdict needs the rules you already run, so a facts report gives none. To get one, point neckbeard at your own rules with `--reader DIR`, or ask Claude to "vet this plugin" with the skill installed (see below). The [gallery](examples/README.md) has seven public plugins and skill packs as facts reports, and neckbeard's fit report on itself, as a labelled demo of what a fit report looks like.

Building a plugin of your own? **[PLUGIN-GUIDE.md](PLUGIN-GUIDE.md)** lists what neckbeard looks for under each of the sample reader's rules and on each card, and gives a ledger format for recording, rule by rule, how far your plugin means to comply.

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

One skill. Its plugin manifest registers no hooks and no agents. By the [published report](docs/neckbeard-report.md) (tokens estimated as bytes / 4): the skill's description is 764 characters, about 190 tokens, in every session, since that is all Claude Code shows its router so it knows the tool is there; the skill file is 14,535 bytes, about 3,600 tokens, loaded each time you use it. Both figures are the same for either install.

The same report says "Hooks: partly read" and "reaches subagents: unknown", and that is the report being honest, not a hidden hook. The deliberately broken fixtures under `tools/fixtures` stop the hooks search from finishing, so neckbeard can only say what it did read. The plugin that prompted this one injected about 1,300 tokens into every session *and* every subagent when I first read it.

That gap is the point. A tool that catches plugins for running in the background cannot run in the background. It works when you ask, reports, and stops.

## Point it at the next plugin before you install it

Ask Claude to "vet this plugin" or "should I install X". The skill runs the inventory, which writes a **dossier** (a JSON record of everything it read), then judges the fit. From a clone, you can also run the inventory directly. `tools/vet` (above) writes the finished report; `tools/neckbeard` prints the raw dossier that report is built from:

```bash
tools/neckbeard <target> [--project-dir DIR] [--extra-rules PATH] [--out FILE]
tools/neckbeard <target> --live-mcp NAME [--out FILE]
```

`<target>` is one of:

- an **installed plugin**, `name@marketplace` (e.g. `ponytail@ponytail`). It reads `installed_plugins.json` first, falling back to the marketplace manifest when that record has no working `installPath` (true for most directory-source installs, but not all: see [CASE-STUDIES, round 2](CASE-STUDIES.md#2-neckbeard-itself-before-publishing))
- a **local directory**: an already-cloned repo, a skill pack, a plugin source tree
- a **marketplace** repo (local or a git URL): its plugin is inventoried, not the repo root. When it lists several, `--plugin NAME` picks one; without it, hooks are reported as unknown rather than absent
- a **git URL**, cloned read-only, depth 1, into a temp directory that is gone when the command exits

`--project-dir` (default: cwd) is where rule discovery starts. `--extra-rules` adds a file or directory the discovery would otherwise miss.

`--live-mcp NAME` is a separate, explicit trust decision. An **MCP server** is a program a plugin can start to give Claude extra tools; a **stdio** server talks to Claude over standard input and output. For one local stdio server declared by the target, Neckbeard starts its target-owned entrypoint, initializes MCP, and lists the advertised tools, resources, resource templates, and prompts. It records metadata and schemas only: it never calls a tool, reads a resource, expands a prompt, opens a browser, or performs a login. Remote servers, shell snippets, package runners, missing or outside-tree entrypoints, unbounded output, and hung servers fail closed. Declared environment values are passed only to that isolated process and are redacted from the dossier, even if the server echoes one back (a value of four characters or more wherever it appears, a shorter one only where a whole string equals it).

It prints the dossier to stdout, or writes it to `--out FILE` and warns you what it contains. The static default writes nothing else. Live inventory executes target code under your user account; the temporary home reduces accidental access but is not a sandbox, so read the static report first.

**A dossier contains your rules, verbatim.** The comparison needs the text, so the dossier embeds every rule file it discovered: your global `CLAUDE.md`, your project rules, your personal skills, the skills of every plugin you have enabled. A run inside this repo produced 90,533 bytes of exactly that. It warns you on write and names the files. Do not commit one, and check your `.gitignore` first. This repo's `.gitignore` ignores JSON files by default, so a dossier does not get committed by accident.

## How it was tested

Fifteen rounds, each one pointed at something real. **[CASE-STUDIES.md](./CASE-STUDIES.md)** has every round, including the false claims it caught in its own docs.

Rounds: [ponytail](CASE-STUDIES.md#1-ponytail-the-one-that-started-it) · [itself](CASE-STUDIES.md#2-neckbeard-itself-before-publishing) · [superpowers](CASE-STUDIES.md#3-obrasuperpowers-the-large-one) · [a random pick](CASE-STUDIES.md#4-koz-tvviral-launch-pipeline-the-random-one) · [claude-security](CASE-STUDIES.md#5-claude-security-anthropics-own-security-plugin) · [all 39 Anthropic plugins](CASE-STUDIES.md#6-all-39-anthropic-first-party-plugins-the-sweep) · [built to break](CASE-STUDIES.md#7-purpose-built-directories-attacking-the-unexercised-branches) · [a crash and a lie](CASE-STUDIES.md#8-the-last-unexercised-branches-a-crash-and-a-lie) · [independent audit](CASE-STUDIES.md#9-an-independent-audit-the-one-that-found-the-most) · [judgment](CASE-STUDIES.md#10-the-judgment-half-the-first-thing-that-passed) · [judgment, hard case](CASE-STUDIES.md#11-the-judgment-half-again-on-the-hard-case) · [the fix that regressed](CASE-STUDIES.md#12-the-fix-that-was-the-regression) · [sealed fixture](CASE-STUDIES.md#13-the-last-claim-resting-on-the-builders-word) · [before going public](CASE-STUDIES.md#14-before-going-public-the-tests-that-tested-the-wrong-thing) · [four pstack ports](CASE-STUDIES.md#15-four-pstack-ports-hooks-where-the-manifest-did-not-say)

- **Who reviewed it:** AI agents only. Each was a separate Claude session that had not written the code. The only outside user ran an early version and hit bugs that later rounds fixed.
- **Hardest round:** the ninth, the first by a session outside the build. Eleven problems, four published claims proved false, one of them a path that could leak 90,533 bytes of private rules into a public repo.
- **The code:** checked against the filesystem. Every self-check case has been seen to fail with the code it guards broken.
- **The judgment:** graded blind against two sealed fixtures (test sets with known answers, built by separate sessions; the author has never seen the answers). On the 31 items of the second that both arms were graded on, the instructions scored 30 where the same model without them scored 16.

## What it reads, and what it refuses to touch

**The target.** If it carries a plugin manifest, neckbeard reads it as a plugin:

- Every `skills/*/SKILL.md`, at the standard path only. It does not walk the whole repo. A plugin built for several agents also ships copies under `.openclaw/`, `.opencode/` and `.cursor/`, and Claude Code never loads those, so counting them would double the plugin's apparent size.
- Every command and agent definition, in full, since each is an instruction to a model, and a `CLAUDE.md` at its root.
- Every hook event it registers, and whether `SubagentStart` (the event that fires when a subagent starts, so a hook on it reaches every helper session) is one of them.
- What each hook injects, where a static read can work that out. It follows one hop of local `require()` and rebuilds `path.join(__dirname, ...)` literals.
- Anything its scripts write to disk outside your project.
- Any **MCP server** the manifest declares, with its name, command and transport. This remains declaration-only by default. With the explicit `--live-mcp NAME` option, one contained local stdio server can also be initialized and asked only for its advertised metadata.

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

## Why

I nearly installed [ponytail](https://github.com/DietrichGebert/ponytail), the lazy-senior-dev persona plugin, which at the time injected about 1,300 tokens into every session and every subagent, permanently. I asked an LLM to compare its rules with mine, and the answer was a list of overlaps and clashes with rules I rely on (never act on something risky without my approval). I had no good way to tell whether that answer was right. So I copied the rules I wanted into my config as plain text, deleted the plugin, and wrote neckbeard to make that comparison something you can check: every call cites the rule on each side. The method is [Yanhua's](https://x.com/yanhua1010/status/2094612609932910828), who did the same audit by hand, against his own config, and published it. See [ATTRIBUTION.md](./ATTRIBUTION.md).

## The name

The name is the developer who reads all of your hook code first, and wants the smallest set of good rules and nothing else.

## License

MIT. See [LICENSE](./LICENSE) and [ATTRIBUTION.md](./ATTRIBUTION.md).

Version history, and why the number is high for a first release: [CHANGELOG.md](CHANGELOG.md).
