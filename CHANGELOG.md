# Changelog

**Everything before 1.12.2 was developed in private; 1.12.2 is the first public release.** The version number is high for a first release because the tool was rewritten fifteen times in thirty-one hours, each time because something found a defect in it. Those numbers are kept rather than collapsed to 1.0.0, since the plugin cache is keyed to version and 1.0.0 already refers to different content.

What each round cost the tool is written up in `CASE-STUDIES.md`. This file is the short version.

## 1.12.3 (2026-09-25)

- **An eighth gallery report: `calm-trader/skills`**, a skill pack with no plugin manifest, vetted against the sample reader. It is a pack the author contributes to, which the report and the gallery say plainly. The report failed the gallery's own count check as first written and was corrected by hand; the gallery lists each correction.

## 1.12.2 (2026-09-24)

First public release. Polish from an independent release review: a separate Claude session, given only a fresh clone and the GitHub settings, and none of the history.

- **Who reviewed this tool, stated plainly.** Every reviewer in `CASE-STUDIES.md` was an AI agent, a separate Claude session that had not written the code. The README and the case studies used to say "an independent audit" and "an outside reviewer" without saying so.
- **The README leads with install**, then requirements (Python 3.11+, standard library only), then what it costs: about 270 tokens always-on and about 4.7k per use, measured with `claude plugin details`.
- **The code's comments explain the code.** Dated accounts of how each bug was found now live only here and in `CASE-STUDIES.md`.
- **Consistent gallery pages**, a `--out` flag that the usage line now shows, no references to tools that are not published, and placeholder names in the self-check's fixtures.
- **Contributor files:** `CONTRIBUTING.md`, a bug-report form that warns against pasting a dossier, and Dependabot for the CI's actions.

## 1.12.1 (2026-09-24)

Works as a plain skill as well as a plugin. Step 1 used to search three possible plugin locations for `bin/neckbeard`; it now runs `inventory.py` from the skill's own directory, which is the same place whichever way neckbeard was installed. The README gives the second install path: clone the repo and link `skills/neckbeard` into `~/.claude/skills/`. Both paths were tested before release, the plugin through `--plugin-dir` and the skill through a symlink, each running Step 1 against ponytail.

## 1.12.0 (2026-09-24)

The report is visual. Step 3 of `SKILL.md` now writes an answer-first page: a verdict banner, an at-a-glance grid, a count of how the target's rules sorted, one grid per verdict with one line per item, and a colour key. The counts must match the grids. The old shape was prose sections, and a reader had to get through several screens to learn whether to install.

`examples/` holds real reports in the new shape for seven public plugins, including this one, all run against a published sample reader in `examples/reader/` so anyone can reproduce them. Verdicts there are relative to that reader, not judgments of the plugins.

## 1.11.7 (2026-09-24)

Follows `@path` imports in `CLAUDE.md`. A global rules file that only says `@~/.claude/roles/me.md` is Claude Code's documented way to split rules, and discovery read that one line and none of the files it imported. On the author's own setup that was 26 bytes of global rules instead of about 16 KB. Imports are followed as Claude Code follows them: relative to the importing file, `~` allowed, up to five hops, never inside code. Each becomes its own item with `imported_from`. On the target side an import that leaves the target is refused, like any other read. Self-check: 45 cases, each new one seen to fail under sabotage.

## 1.11.6 (2026-09-24)

`SKILL.md` brought into line with the code. 1.11.5 had left it alone because the sealed fixture graded that text; the cost of that is recorded in round 14.

- Step 1 names every `enabledPlugins` layer, single rule files as targets, and the `refused` marker, which the evaluation must report rather than skip.
- Step 2 classifies `rule_files`, `commands` and `agents` as well as skills.
- Step 3 checks that the evaluation path is ignored by git before writing it.
- Step 4 no longer cites `list-item`, a skill that exists only on the author's machine.
- Commands and agents are read into the dossier in full, behind the containment guard, instead of listed by filename. Self-check: 40 cases.
- README: the "Why" paragraph said "one worth keeping" and then "copied five"; it was five.

## 1.11.5 (2026-09-24)

An adversarial pass before the repo was made public. Written up as round 14 in `CASE-STUDIES.md`.

- **The self-check tested helpers, not decisions.** All 15 cases called `classifiable_items()` or `merge_enabled_plugins()` directly. Inverting the skip in `main()`, or reverting discovery to the single-file read 1.11.4 fixed, left it at 15/15. It now has 37 cases, 21 of them through the real CLI or the real discovery path, and every fix below has been broken on purpose and seen to turn a case red.
- **Containment covers every read from the target.** Skills in a pack with no manifest, the hooks file (including a `../` path named in `plugin.json`), `.mcp.json`, `plugin.json` and the README excerpt were read without the check that `SECURITY.md` said applied to everything.
- **More of what a target carries counts as something to compare.** Commands, agents and a root `CLAUDE.md` now count, so a pack of only those no longer skips the reader's rules. A root `CLAUDE.md` is read into `rule_files`.
- **A single rule file is a valid target**, as the skill has always said. It used to exit "not a directory".
- **Hooks inline in `plugin.json`** are read. They crashed the run before.
- **Managed settings are read** as the top layer of `enabledPlugins`, so a plugin an organisation disables there no longer counts as in force.
- **A corrupt settings file says so** on stderr instead of reading as "no plugins enabled".

Correction to 1.11.4 below: it said discovery found "one eighth" of the rules in force. 8 of 23 is about a third.

## 1.11.4 (2026-09-20)

Discovered the rules that were actually in force, instead of about a third of them.

`enabledPlugins` was read from the project's `.claude/settings.json` alone. Claude Code layers user, project and project-local settings, and enabling a plugin globally is the normal way to do it, so a project with no `.claude/` directory saw none of them. Personal *skills* were already read from `CLAUDE_HOME`, which is why this reads as an oversight rather than a decision.

Found by pointing the tool at `github/spec-kit` from a repo with no `.claude/` directory. It discovered **8** rule sources where the corrected path discovers **23**. The **15** it missed were the installed skills of all six enabled plugins, and those were exactly the rules that target conflicted with. The evaluation would have reported **no conflicts**, because the conflicting rules were invisible.

The first attempt to size this said 59, and that number was wrong in a way worth keeping. It came from passing `--extra-rules` over a whole worktree as a workaround, and that path recursively counts every markdown file it meets: 40 of those 51 "missing rules" were agent definitions, READMEs, docs and two briefs written the same afternoon. **The measurement used to size a bug about under-broad rule discovery was itself produced by an over-broad one, and nobody re-derived it once the correct path existed.** A number can read correctly, survive review and be wrong, which is the same shape as the defect it was describing. Caught by the session that reviewed the fix, not by its author.

That is the failure this tool exists to catch, in its own discovery half: the comparison ran, reported success, and had nothing like the corpus it claimed. The merge now honours precedence as well as presence, so a project that deliberately disables a globally-enabled plugin is not silently re-enabled.

`skills/neckbeard/selfcheck.py` covers both paths that fail silently now, not one.

## 1.11.3 (2026-09-20)

Stopped reading the reader's private rule files for a target that cannot be compared against them.

A dossier embeds the verbatim text of the global `CLAUDE.md`, the project rules, every personal skill and every enabled plugin's skills. That is load-bearing for the classification step and a hazard everywhere else, which 1.11.2 already said in a warning. What it did not do was ask whether the comparison was possible at all: pointed at a repository carrying no skill and no hook, it read and embedded 102,899 bytes, about 100KB of it the reader's own rules, to compare against nothing. The same run now writes 4,983 bytes and says why it read nothing.

The first fix counted only hooks whose payload resolved, which walked into this tool's own hardest rule -- *never read a hook's absence from `injected_content` as "it injects nothing"* -- and skipped the rules for a fixture that injects at every session start through a shell payload the resolver cannot trace. Any hook at all now counts, resolved or not. `skills/neckbeard/selfcheck.py` holds both directions, including that one.

## 1.11.2 (2026-09-19)

First tagged release.

Recorded how the last claim resting on the author's own account was closed. The judgment half, the instructions that sort a plugin's rules into duplicate, conflict and new, has no filesystem to check it against. An outside auditor built a held-out fixture, sealed the ground truth before running anything, pre-registered a rubric, and graded its own six evaluations. The author has never seen it.

## 1.11.1 (2026-09-19)

Recorded the lesson from the first re-audit that came back clean: a real third-party plugin with an awkward hook wrapper caught a defect that 39 catalog plugins and 13 purpose-built fixtures all missed.

## 1.11.0 (2026-09-19)

**Fixed a regression introduced by the previous fix.** The 1.9.0 change narrowed hook-command resolution to a short extension allowlist, which silenced a real plugin entirely instead of reporting that it could not resolve the command. Worse, it shipped alongside a sentence claiming silence meant nothing to inject. Hook commands now report in three buckets: resolved, unresolved, and absent.

## 1.10.0 (2026-09-19)

Tested the judgment half against a hard fixture with several overlapping rule sources, and fixed a silence it exposed.

## 1.9.0 (2026-09-19)

First test of the judgment half at all. Fixed three defects in the instructions, including a step that named a rules-file section heading that only existed on the author's own machine.

## 1.8.0 (2026-09-19)

Closed the remaining audit findings and corrected three published numbers that did not reproduce.

## 1.7.0 (2026-09-19)

Fixed five blocking findings from an independent audit, including a symlinked skill file that escaped the plugin directory and was read and embedded.

## 1.6.0 (2026-09-19)

**Security.** Evaluations embedded the user's own rules verbatim, including host names and private identifiers, into a file that a deny-by-default `.gitignore` did not cover. Added the ignore rules and a runtime warning on every write. Verified nothing had ever been committed.

## 1.5.0 (2026-09-19)

Closed the last unexercised branches in hook parsing: one crash, and one confident wrong answer on a hooks file that does not parse. `has_hooks` became three-state so "could not read that" stopped collapsing into "no".

## 1.4.0 (2026-09-19)

Attacked branches no real plugin exercises, using purpose-built directories. Three bugs, including declared MCP servers reported nowhere at all.

## 1.3.0 (2026-09-19)

Swept all 39 of Anthropic's first-party plugins and fixed the bug that found.

## 1.2.0 (2026-09-19)

Fifth case study, against Anthropic's `claude-security`, and the two fixes it forced.

## 1.1.0 (2026-09-19)

Corrected a claim about plugin caching that the tool disproved when run against itself. Separated hook scripts from hook registrations, which are different counts.

## 1.0.0 (2026-09-18)

Initial build. Replaced an unmeasured "zero cost" claim with the measured token count.
