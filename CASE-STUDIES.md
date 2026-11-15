# Case studies

Every time this tool has been pointed at something real, in order, with what it found and where the tool itself fell short.

**Pointed at real plugins**

1. [`ponytail`](#1-ponytail-the-one-that-started-it): the one that started it
2. [`neckbeard`](#2-neckbeard-itself-before-publishing): itself, before publishing
3. [`obra/superpowers`](#3-obrasuperpowers-the-large-one): the large one
4. [`Koz-TV/viral-launch-pipeline`](#4-koz-tvviral-launch-pipeline-the-random-one): the random one
5. [`claude-security`](#5-claude-security-anthropics-own-security-plugin): Anthropic's own security plugin
6. [All 39 Anthropic first-party plugins](#6-all-39-anthropic-first-party-plugins-the-sweep): the sweep

**Pointed at neckbeard itself**

7. [Purpose-built directories](#7-purpose-built-directories-attacking-the-unexercised-branches): attacking the unexercised branches
8. [The last unexercised branches](#8-the-last-unexercised-branches-a-crash-and-a-lie): a crash and a lie
9. [An independent audit](#9-an-independent-audit-the-one-that-found-the-most): the one that found the most
10. [The judgment half](#10-the-judgment-half-the-first-thing-that-passed): the first thing that passed
11. [The judgment half again, on the hard case](#11-the-judgment-half-again-on-the-hard-case)
12. [The fix that was the regression](#12-the-fix-that-was-the-regression)
13. [The last claim resting on the builder's word](#13-the-last-claim-resting-on-the-builders-word)
14. [Before going public](#14-before-going-public-the-tests-that-tested-the-wrong-thing): the tests that tested the wrong thing

**Pointed at real plugins, later**

15. [Four `pstack` ports](#15-four-pstack-ports-hooks-where-the-manifest-did-not-say): hooks where the manifest did not say

[What the fifteen add up to](#what-the-fifteen-add-up-to) · [Who did the reviewing](#who-did-the-reviewing)

---

## 1. `ponytail`: the one that started it

The plugin that prompted this one. Run against the installed `ponytail@ponytail`, then cold against `addyosmani/agent-skills` by GitHub URL to exercise the clone path (25 skills found).

**The report today** · ponytail 5.3.3 @ `7801d06`, a facts report by neckbeard 1.17.1 (no reader, no verdict) · [full report](examples/ponytail.md)

<!-- report:ponytail -->
> # 🔍 ponytail 5.3.3 · what it adds
>
> `2026-11-15` · neckbeard 1.17.1 · [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) 5.3.3 @ `7801d06`
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
> - Commands:
>
> ### State it may leave
> - Persistence candidates:
>
> ### Reaches outside the session
> - MCP servers: none
>
> ### Source
> - Kind: plugin
> - Name: ponytail (from plugin.json)
> - Version: 5.3.3 (from plugin.json)
> - plugin.json:
> - Marketplace: none
> - Commit: 7801d06
<!-- /report -->

**The first run** · before 1.0.0, against the author's own rules

- three hooks (`SessionStart`, `SubagentStart`, `UserPromptSubmit`) injecting `skills/ponytail/SKILL.md`, 6,637 bytes; about 5,229 characters once ponytail strips the frontmatter, which no static read can know\
  ↳ about the plugin
- the resolver missed the injection, because the path is built two hops away through a `require()` and `path.join(__dirname, ...)` rather than one string literal\
  ↳ 1.0.0 · guard: no `selfcheck.py` case yet
- the skill count was doubled by mirrors for other agents under `.openclaw/` and `.opencode/`, which Claude Code never loads\
  ↳ 1.0.0 · guard: no `selfcheck.py` case yet

Counting what the host cannot see is worse than not counting.

**The rerun** · 2026-11-15, ponytail 5.3.3 (the first run read it before 1.0.0), neckbeard 1.17.1, facts only

- the plugin grew to six skills and six commands, 21,177 bytes of skill files in all; the hooks still inject at session start and at every subagent start, and neckbeard reaches the same answer ("reaches subagents: true", from the `SubagentStart` hook)\
  ↳ about the plugin
- neckbeard cannot say what the three hooks inject. Each runs an inline `node -e` command that requires one script by a path built from `CLAUDE_PLUGIN_ROOT`, and the report prints `<unparsed command>` and "partly read", where 1.0.0 had learned to follow exactly this shape through a script file\
  ↳ **open**: `hook-inline-require`
- `plugin.json` also lists `hooks/claude-band.json`, which holds no hooks but a `modules` entry: a Claude Code mod, JavaScript that runs inside the session with your permissions. The inventory reads only the `hooks` key, so the mod does not appear in the report at all\
  ↳ **open**: `mod-inventory`
- the old first-run bullet about doubled skill counts (mirrors for other agents) did not come back: six skills are six folders under `skills/`\
  ↳ guard from 1.0.0 held

A fit verdict on the rerun would need your own rules, so there is none here. The facts show what changed since the first run, and where today's tool reads less than it should.

## 2. `neckbeard`: itself, before publishing

No hooks, no agents, one skill, at 7,207 bytes when first read. Its own report marked it down at 1.12.0 for a report format that needs a symbol key; three runs on 1.12.7 and one on 1.17.1 found no conflict (see the rerun below).

**The report today** · neckbeard 1.17.1 against the [sample reader](examples/reader/) · [full fit report, kept as the labelled demo of a fit report](examples/neckbeard.md)

<!-- report:neckbeard -->
> 🟩 INSTALL · nothing to weigh
> It ships one skill, no hooks, no agents, no commands and no root rule file, so the only always-on cost is the skill description. None of its rules conflicts with the reader's, and its core method (a standing rule and an on-demand skill) is new to this reader.

| | | |
|:--:|---|---|
| 🟩 | **Cost** | Skill description only, about 270 tokens per the manifest, loaded each session. The 14,357-byte skill body loads only when invoked. |
| 🟩 | **Reach** | Main session only. No hooks are registered, so nothing fires on SubagentStart (certain). |
| 🟩 | **Leaves state** | None found at install. When run, it writes one evaluation file inside the project it is run from. |
| 🟨 | **Live surface** | Runs its own Python inventory script locally and clones a git URL target read-only. Live MCP inspection is off unless the user asks. |
| 🟩 | **Refused reads** | none |
| ❓ | **Read status** | Partial for hooks and persistence scans: broken test fixtures could not be parsed, and one script was read only up to 50,000 bytes. |
| 🟩 | **Worth keeping** | 2 (1 standing rule, 1 skill) |
<!-- /report -->

**The first run** · before 1.1.0, against the author's own rules

- the docs said a directory-source install never gets a cache copy; this plugin's source is a git repo, so Claude Code cached it anyway, keyed to the version, and served an early false description through two commits that fixed it\
  ↳ about the tool's docs · 1.1.0: the version moves with every behavior change, and the claim says "usually", with the exception named
- its own `inventory.py` flagged as a persistence risk for three `os.path.expanduser` calls, all reads of a caller-supplied path; the heuristic cannot tell resolving a path from writing to disk, so it says so\
  ↳ worked as designed: flagged for a human, not guessed

**The rerun** · 2026-11-15, neckbeard 1.17.1 vetting itself, judged on the Mac in a separate session, the judge, which is the model session that does the comparing. The run printed judge mode `own`: the judge could not log in with the sample reader as its config folder, so it started with the machine's own config and was told to ignore it

- verdict INSTALL again, with 0 conflicts. This run counts 3 rules as already covered (duplicates of rules the reader runs), 1 new standing rule, 1 new on-demand skill and 2 dropped; the three runs on 1.12.7 counted 2 covered, 1 new skill and 2 dropped. The extra standing rule is "unknown is not none", which the judge now keeps as a rule for the reader's own config\
  ↳ about the tool: the verdict held, the sort moved a little between versions
- the report has a "Read status" row that the 1.12.7 reports did not: hooks and persistence are "partial", because broken test fixtures could not be parsed and one script was read only up to 50,000 bytes\
  ↳ worked as designed: the gaps are named, not hidden
- the same report still says "main session only (certain)" in its Reach row, while the facts report on this tree says "reaches subagents: unknown", because the same fixtures stop the hooks search. The judge states more than the inventory knew\
  ↳ **open**: raised with the maintainers, not yet queued; the report order planned for 2.0 (facts first, fit after) is meant to stop a verdict from outrunning its facts
- the judge wrote 14,357 bytes for the skill body, where the inventory counts 14,535, and "about 270 tokens per the manifest" for the description, which the facts report counts at 764 characters\
  ↳ about the tool: figures in a fit report come from a model's reading and can differ from the inventory's; the facts report is the one to quote

## 3. `obra/superpowers`: the large one

Picked by measurement: real file, hook and skill counts across four candidates from GitHub's tree API, not their descriptions. 231 files across 67 directories as of 2026-09-19 (its size today is in the rerun below).

**The report today** · superpowers 7.0.2 @ `22f0b46`, a facts report by neckbeard 1.17.1 (no reader, no verdict) · [full report](examples/superpowers.md)

<!-- report:superpowers -->
> # 🔍 superpowers 7.0.2 · what it adds
>
> `2026-11-15` · neckbeard 1.17.1 · [obra/superpowers](https://github.com/obra/superpowers) 7.0.2 @ `22f0b46`
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
> - Persistence candidates:
>
> ### Reaches outside the session
> - MCP servers: none
>
> ### Source
> - Kind: plugin
> - Name: superpowers (from plugin.json)
> - Version: 7.0.2 (from plugin.json)
> - plugin.json:
> - Marketplace: none
> - Commit: 22f0b46
<!-- /report -->

**The first run** · 2026-09-19, against the author's own rules

```
has_hooks: true, events: [SessionStart]
hooks_reach_subagents: false
skills: 15, total 168,036 bytes
```

- the hook command `run-hook.cmd session-start` has no script extension, so it could not be resolved statically; reported as unresolved, not guessed\
  ↳ worked as designed · guard: `selfcheck.py`: "no skills, UNRESOLVED hook" (an unresolved hook still triggers the comparison)
- a later fix narrowed resolution to an extension allowlist and made this same hook report nothing at all ([§12](#12-the-fix-that-was-the-regression))\
  ↳ 1.11.0: resolved, unresolved and absent reported separately · guard: no `selfcheck.py` case yet
- the hook's matcher is `startup|clear|compact` with no `SubagentStart`, and the injected skill opens with `<SUBAGENT-STOP>`: it never reaches a subagent\
  ↳ about the plugin

Read by hand, `hooks/session-start` cats `skills/using-superpowers/SKILL.md` (3,192 bytes) into session context, once, against ponytail's ~6,600 on every session and every subagent.

**The rerun** · 2026-11-15, superpowers 7.0.2 (first read at 6.4.1), neckbeard 1.17.1, facts only

- still fifteen skills, now 143,103 bytes (it was 168,036), and still one `SessionStart` hook with the matcher `startup|clear|compact`; neckbeard still reports that it reaches no subagent\
  ↳ about the plugin
- the hook command is still `run-hook.cmd`, and the report still says "partly read": the script was found, its payload could not be traced, and the report says unknown, not none. This is the 1.11.0 behaviour of [§12](#12-the-fix-that-was-the-regression) working on the same hook it once got wrong\
  ↳ worked as designed · guard: `selfcheck.py` "no skills, UNRESOLVED hook"

## 4. `Koz-TV/viral-launch-pipeline`: the random one

Picked with an unseeded `random.choice()` from 183 candidates, filtered by keyword out of Anthropic's official (310) and community (2,282) catalogs. One skill, 15,919 bytes, no hooks, no declared agents.

**The report today** · viral-launch-pipeline 1.0.0 @ `475705f`, a facts report by neckbeard 1.17.1 (no reader, no verdict) · [full report](examples/viral-launch-pipeline.md)

<!-- report:viral-launch-pipeline -->
> # 🔍 viral-launch-pipeline 1.0.0 · what it adds
>
> `2026-11-15` · neckbeard 1.17.1 · [Koz-TV/viral-launch-pipeline](https://github.com/Koz-TV/viral-launch-pipeline) 1.0.0 @ `475705f`
>
> ### Injects
> - Skills:
> - Rule files: none
> - Hook-injected text: none
>
> ### Hooks
> - Hooks: none
>
> ### Subagents and commands
> - Agents: none
> - Commands: none
>
> ### State it may leave
> - Persistence candidates: none
>
> ### Reaches outside the session
> - MCP servers: none
>
> ### Source
> - Kind: plugin
> - Name: viral-launch-pipeline (from plugin.json)
> - Version: 1.0.0 (from plugin.json)
> - plugin.json:
> - Marketplace: none
> - Commit: 475705f
<!-- /report -->

**The first run** · 2026-09-19, against the author's own rules

- "21-agent pipeline" sat next to zero agent files; the skill's text *is* the orchestration, calling the `Agent` tool 21 times, four in one parallel batch\
  ↳ about the plugin
- a pipeline built as dispatch instructions inside one skill reports `agents: []` and looks inert; zero declared agents does not mean zero agent dispatch\
  ↳ **still open**: prose is not parsed for `Agent(` calls
- the 15,919-byte skill is not the whole footprint: 21 stage prompts and 6 references, 92,456 bytes, load one at a time as stages run\
  ↳ about the tool's framing · not a bug: nothing about them is standing cost, but "one 15KB skill" understates the total by six times

**The rerun** · 2026-11-15, viral-launch-pipeline 1.0.0 @ `475705f` (unchanged since the first read), neckbeard 1.17.1, facts only

- one skill, 15,919 bytes, no hooks and no declared agents: the same facts as the first run, now all read in full ("read in full" is the colour of its badge)\
  ↳ about the plugin
- the report still says `Agents: none`, and the skill still dispatches 21 agents in prose\
  ↳ **still open**: prose is not parsed for `Agent(` calls
- the old report counted the 92 KB of stage prompts as footprint; the facts report lists the skill file and its description only, since the prompts load one at a time\
  ↳ about the tool's framing, as before

## 5. `claude-security`: Anthropic's own security plugin

Version 0.11.0. Picked deliberately, because two of its hook events had never appeared in any earlier run: `UserPromptExpansion` and `PostToolUseFailure`. One skill (5,246 bytes), **8 declared agents**, two hook scripts across three events, 476KB.

**The report today** · claude-security 0.12.0 @ `b5b01ac` (the head of the marketplace repo, which has no tags), a facts report by neckbeard 1.17.1 (no reader, no verdict) · [full report](examples/claude-security.md)

<!-- report:claude-security -->
> # 🔍 claude-plugins-official 0.12.0 · what it adds
>
> `2026-11-15` · neckbeard 1.17.1 · [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) 0.12.0 @ `b5b01ac`
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
> - Agents:
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
> - Name: claude-security (from plugin.json)
> - Version: 0.12.0 (from plugin.json)
> - plugin.json:
> - Marketplace: not applicable
> - Commit: b5b01ac
<!-- /report -->

**The first run** · 2026-09-19, against the author's own rules

```
hook_scripts: 2, hook_registrations: 3
events: [UserPromptExpansion, PostToolUse, PostToolUseFailure]
hooks_reach_subagents: false
persistence: []
```

- both never-seen hook events were listed, not dropped or crashed on\
  ↳ worked as designed
- a constant, `INJECTING_EVENTS`, listed five events and was used nowhere, implying a classification the tool does not do\
  ↳ 1.2.0: removed
- `reaches_subagents: false` beside **eight declared agents**: correct (no hook fires on a subagent event) and misleading\
  ↳ 1.2.0: renamed `hooks_reach_subagents`
- the persistence scan found nothing across 16 Python files and 2 shell scripts; `hooks.py` writes only to stdout and stderr. Read at the time as evidence the heuristic errs toward false positives\
  ↳ that reading was wrong: [§9](#9-an-independent-audit-the-one-that-found-the-most) built five writes it missed; widened in 1.7.0

**The rerun** · 2026-11-15, claude-security 0.12.0 @ `b5b01ac` (first read at 0.11.0), neckbeard 1.17.1, facts only

- one skill (5,569 bytes) and now nine agents, with `scan-redactor` added; the hooks file now registers `PermissionRequest` beside `UserPromptExpansion`, `PostToolUse` and `PostToolUseFailure`, all running one `hooks/hooks.sh`\
  ↳ about the plugin
- the report now says "reaches subagents: true", on the documented rule that `PostToolUse` fires inside subagents; the first run said false, since no `Subagent*` event was registered. The matcher is `Bash`, so the reach is narrower than the word suggests, and a facts report does not say so\
  ↳ about the tool's framing · 1.2.0 named the field for exactly this reason
- the hooks read "partly read": the script `hooks/hooks.sh` was found but what it injects could not be traced, so the report says unknown\
  ↳ worked as designed
- two persistence candidates (`workflows/scan.js`, `scripts/patch_artifacts.py`) are over the 50,000-byte read cap, and the report says so rather than listing them as clean\
  ↳ worked as designed: the read cap is named, not hidden

## 6. All 39 Anthropic first-party plugins: the sweep

Rather than pick one, run it against every plugin in `anthropics/claude-plugins-official`, then check each report against what is actually on disk. Thirty-nine targets, no crashes, no timeouts.

**Twenty-five are real plugins, and the counts were perfect.** Skills, agents and commands matched the filesystem exactly in all twenty-five. No double-counting, no misses. The kind of result that is only worth reporting because the checking was mechanical rather than eyeballed.

**Fourteen have no `plugin.json` at all.** Twelve are language-server stubs carrying nothing but a LICENSE and a README. Two, `receipts` and `session-report`, carry real skills and no manifest, and the generic-pack path handled both correctly.

**The sweep found one genuine bug, and it was hiding in an assertion.** The generic-pack branch, taken whenever no manifest is found, returned no hooks field at all, and the README stated flatly that a manifest-less pack has "no hooks, no carrying cost by construction." It had never looked. Confirmed by building a directory with a live `SubagentStart` hook and no `plugin.json`: neckbeard reported nothing about it at all, while claiming there was nothing to report.

Nothing in this catalog triggered it, which is exactly why it survived five previous case studies. A manifest-less directory that silently injects into every subagent is the single worst thing this tool could fail to mention, and it would have shipped that way.

**Fixed:** the generic-pack branch now runs the same hook and persistence inventory as the plugin branch, and the README no longer asserts what the code does not check. Re-ran all 39 afterward: no regressions, every dossier now carries a hooks field.


## 7. Purpose-built directories: attacking the unexercised branches

§6 ended on a conclusion: the dangerous defects live in code paths no real plugin takes. So this round built directories to provoke those paths. A root-level `plugin.json`, a flat `hooks.json` and an empty directory all held.

- a skill with no frontmatter was named `SKILL`, the filename, so every such skill in a pack had the same name\
  ↳ 1.4.0: named by its directory · guard: no `selfcheck.py` case
- `--extra-rules` pointed at a folder silently took nothing unless the files were named `SKILL.md` or `CLAUDE.md`\
  ↳ 1.4.0: every markdown file, and a warning when a path matches nothing · guard: no `selfcheck.py` case
- a plugin declaring two MCP servers reported nothing about them: the worst omission it could make\
  ↳ 1.4.0: an `mcp_servers` block; `.mcp.json` added in 1.7.0 after [§9](#9-an-independent-audit-the-one-that-found-the-most) · guard: no `selfcheck.py` case

<details>
<summary>2 more findings</summary>

- the first check of that fix passed only because the test plugin was named `mcpplug`\
  ↳ rewritten to pass for the right reason
- this section claimed no catalog plugin declares an MCP server; Anthropic's own `example-plugin` does\
  ↳ corrected after §9

</details>

**Write the check so it can only pass for the right reason.**

## 8. The last unexercised branches: a crash and a lie

The three paths left after round 7: the hook-injection recursion limit, a `hooks.json` that is present but broken, and a symlinked target. The recursion limit failed honestly ("could not statically resolve") and the symlinked target resolved correctly.

- a `hooks.json` of invalid JSON reported `has_hooks: true` with no events, which reads as "registers nothing"\
  ↳ 1.5.0: `has_hooks: "unknown"` with a `parse_error` · guard: `selfcheck.py`: "hooks file that did not parse"
- a `hooks.json` holding a list where an object belongs crashed with an `AttributeError`\
  ↳ 1.5.0 · guard: no `selfcheck.py` case
- this section claimed the class was closed; three deeper shapes still crashed\
  ↳ 1.7.0, after §9 · guard: no `selfcheck.py` case

All 39 catalog plugins re-ran with no crashes and no false "unknown".

**"I could not read that" is a third answer, distinct from yes and no.**

## 9. An independent audit: the one that found the most

Eight rounds of self-testing, then a separate session with no stake in the code, briefed to treat every claim as a hypothesis. Eleven findings, all missed by the builder; the main ones:

- a run embedded 90,533 bytes of the user's private rules in a file no `.gitignore` covered, one `git add` from a public repo\
  ↳ 1.6.0: ignore rules, and a warning on every write · guard: no `selfcheck.py` case
- a symlinked skill file could make it read and embed `/etc/passwd`\
  ↳ 1.7.0: refused, and reported as refused · guard: `selfcheck.py`: the 12 containment cases
- "nothing in the 39-plugin catalog declares an MCP server": Anthropic's `example-plugin` does, in `.mcp.json`\
  ↳ 1.7.0: both locations read · guard: no `selfcheck.py` case

<details>
<summary>3 more findings</summary>

- "the heuristics fail toward false positives": five constructed writes, two into `$HOME`, all missed\
  ↳ 1.7.0: all six fixtures caught · guard: no `selfcheck.py` case
- the injection resolver confidently named an unrelated `CHANGELOG.md`\
  ↳ 1.7.0: a bare match is labelled low confidence · guard: no `selfcheck.py` case
- `bytes` was a character count, and silently capped at 200,000\
  ↳ 1.8.0: `bytes` and `chars` both reported; three published figures corrected · guard: no `selfcheck.py` case

</details>

**Widen the claim to match the fix, or narrow the claim to match the fixture.**

<details>
<summary>Read the full story</summary>

Eight rounds of self-testing, then a fresh reviewer with no stake in the code and a brief that listed every claim as a hypothesis rather than a finding. It returned eleven findings. The builder had missed all of them.

**The worst was not in the code at all. It was in the output.** A dossier embeds the full text of every rule file it discovers, because the comparison needs the text. Those files are the user's global rules, their project rules, their personal skills. A run from inside this repo produced 90,533 bytes of private configuration, including a hostname and two private marketplace names, in a repo one `git add` from being published, with no ignore rule that would have caught it. Eight rounds of checking what the tool *read* never once asked what it *wrote*.

**Four published claims turned out to be false.** Each had the same shape: a round found a bug, built one fixture, fixed what that fixture exercised, and then wrote the general sentence into the docs.

| claim | reality |
|---|---|
| "Nothing in the 39-plugin catalog declares an MCP server" | Anthropic's own `example-plugin` does, via `.mcp.json`, which the fix never read |
| "no sweep of real plugins would ever have caught it" | a sweep that looked in both places would have |
| a crash and a lie in hook parsing, "both closed" | the guard covered one nesting level; three deeper shapes still crashed |
| "the heuristics fail toward false positives, not false negatives" | five constructed writes, two into `$HOME`, all missed |

That last one is the sharpest. The evidence offered for it was one false positive and one true negative. **Neither is evidence about false negatives.** The claim had never been tested by constructing a write the scan should catch, and when someone did, it caught none of them.

**Other findings worth naming.** The injection resolver named an unrelated `CHANGELOG.md` quoted two lines above the real payload, with full confidence and no note, directly contradicting the promise that it says so when it cannot tell. A hostile target could make it read and embed `/etc/passwd` through a symlinked skill file, because the containment check existed on one code path and not the other two. Passing the same directory as `./rel` or with a trailing slash silently disabled injection reporting, and the failure wore the costume of the tool's own documented honest fallback, so nobody would investigate it. Reported `bytes` was a character count, which undercounts any non-ASCII file: 10,000 em dashes reported 10,000 against 30,000 on disk. It was also silently capped at the 200,000-character read limit, so a one-megabyte skill reported exactly 200,000 with nothing saying so. Both fixed, and `bytes` now means bytes with `chars` reported alongside. **Three figures published in these case studies were character counts wearing the wrong unit and have been corrected**: ponytail 6,616 to 6,637, viral-launch 15,775 to 15,919, claude-security 5,222 to 5,246. Superpowers' 3,192 was already correct, having been measured with `wc -c` rather than through the tool.

**What actually held.** Re-measured from scratch: the ~266 token figure, ponytail's numbers, superpowers' injection size, the 39/25/14 split, the 25-of-25 filesystem match, and the claim that it never writes outside `--out`, verified by watching mtimes rather than reading the code.

**The lesson, in the auditor's words:** widen the claim to match the fix, or narrow the claim to match the fixture. Do not ship the general sentence off a single constructed case. Every fixture from this round is kept as a permanent regression case, because no real plugin exercises any of them.

</details>

## 10. The judgment half: the first thing that passed

Every earlier round tested `inventory.py`. This one tested `SKILL.md`, the instructions a model follows to sort rules: four planted rules with unambiguous answers, a throwaway `HOME`, and a model given only the instructions and the dossier. **Four of four, twice.**

- Step 4 named a section heading that existed only in the author's own rules file\
  ↳ 1.9.0: a method instead of a name · guard: sealed fixture ([§13](#13-the-last-claim-resting-on-the-builders-word))
- Step 4 demanded a repo for any proposed skill, which nothing could supply, so the model invented one\
  ↳ 1.9.0: a proposed name, marked as a proposal · guard: sealed fixture
- Step 2 said to weigh carrying cost and gave no criterion\
  ↳ 1.9.0: a criterion, with the zero-hook case named · guard: sealed fixture

**Instructions are testable, and were not being tested.**

## 11. The judgment half again, on the hard case

Three overlapping rule sources, hooks that reach subagents so the carrying-cost rule finally has to fire, and one rule whose right answer is arguable. **Five of five**, including picking the right source among overlapping ones and calling the arguable one a coin flip rather than dressing it up.

- one hook that resolved silenced the warning for every hook that did not, so a `PreToolUse` gate of unknown behavior looked like a hook with nothing to inject\
  ↳ 1.10.0: unresolved hooks listed one by one · guard: `selfcheck.py`: "no skills, UNRESOLVED hook"
- no rule for which source to cite when several cover the same ground\
  ↳ 1.10.0 · guard: sealed fixture
- no rule for exactly one rule surviving the carrying-cost test\
  ↳ 1.10.0 · guard: sealed fixture

**A guard that has never fired is not known to work.**

## 12. The fix that was the regression

An audit of the §11 fix found it had made a different hook invisible. `obra/superpowers` injects 3,192 bytes through `run-hook.cmd`, and `.cmd` was not on the fix's new extension allowlist:

```
1.9.0   injected_content_note: "could not statically resolve ..."
1.10.0  injected_content_note: NONE
```

- the fix only examined a quoted path with one of five extensions, and dropped every other shape silently\
  ↳ 1.11.0: three buckets, resolved, unresolved and unidentifiable; every token in the command tried · guard: no `selfcheck.py` case; superpowers kept as a regression target
- §11 had told the reading model that a hook in neither list "genuinely has nothing resolvable to inject"\
  ↳ 1.11.0: the sentence removed
- 39 catalog plugins and 13 fixtures stayed clean throughout, because none had the wrapper shape

Re-audited afterwards, with all eleven earlier findings re-checked: the first round to come back with nothing.

**A fix is a change, and changes need the same suspicion as the bug.**

<details>
<summary>Read the full story</summary>

The §11 fix made unresolved hooks visible. An audit of that fix found it had made a different hook invisible, and the new version was worse.

The old warning was crude: say something if *nothing* in the whole hook set resolved. The replacement only recorded a hook when the command carried a **quoted** path with one of five extensions that **existed on disk**. Every other shape was dropped in silence.

The proof is a real plugin, not a fixture. `obra/superpowers` runs `"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd" session-start` and injects 3,192 bytes at every session start.

```
1.9.0   injected_content_note: "could not statically resolve ..."
1.10.0  injected_content_note: NONE
```

`.cmd` was not on the allowlist, so the hook was never even examined. And §11 had added a sentence to the instructions telling the reading model that a hook in neither list **"genuinely has nothing resolvable to inject."** The fix turned an ambiguous silence into a documented false conclusion, with "genuinely" doing the confident work. This same file, in §3, still claimed of this exact target that "it said so rather than guessing." It had stopped saying so.

**Why the regression check missed it.** The commit reported 39 catalog plugins and 13 fixtures clean, and both were true. No plugin in that catalog uses the wrapper-script shape, and the fixtures had been built around the shape being fixed. Sweeping a corpus cannot find a class the corpus does not contain, and a fixture written to confirm a fix confirms that fix. **The check passed for the wrong reason**, which is this repo's own recurring lesson landing squarely on the fix written to address it.

**The fix is three buckets, not two.** A hook whose script cannot be *identified* is a larger unknown than one whose script was found but whose payload could not be traced, and the old code ranked it below "nothing to inject" by saying nothing. Identification no longer depends on an extension list or on quoting: every token in the command is tried, the plugin-root variable is expanded, and the first that exists inside the tree wins. All five command shapes from the audit now report, none silently.

`obra/superpowers` is now a permanent regression target. It is the only real-world plugin in reach that exercises this path, and it has caught the same class of defect twice: once as the plugin whose wrapper shape the resolver could not handle, and once as the only target able to detect the silence that replaced it.

Re-audited afterwards and confirmed closed, with all eleven earlier findings re-checked because `inventory.py` had moved 81 lines. First round to come back with nothing.

</details>

## 13. The last claim resting on the builder's word

Rounds 10 and 11 passed, but the builder had planted the rules, known the answers and graded the result. So a separate session built its own fixture, sealed the ground truth, pre-registered a rubric, ran six evaluations and scored them. The builder has seen none of it, and this file does not describe it: a held-out set is only worth anything while the graded instructions have not seen the answers.

- twelve rounds tested the half that was easy to test; the judgment half went untested by anyone but its author\
  ↳ 1.11.2: graded blind against the sealed fixture · guard: sealed fixture 1
- re-run on 1.11.6: 12 of 12 with the instructions, and 12 of 12 without them, so by its own rule inconclusive\
  ↳ a second, harder fixture ([§14](#14-before-going-public-the-tests-that-tested-the-wrong-thing)) · guard: sealed fixture 2

**Grading your own fixture is not a test, it is a rehearsal.**

## 14. Before going public: the tests that tested the wrong thing

1.11.3 and 1.11.4 had only been reviewed by the sessions that wrote them, in a repo about to go public. Three adversarial reviewers took the code, the guards and the claims, and a fourth then attacked their fixes.

- the self-check's 15 cases called helpers directly; inverting the decision in `main()`, or putting 1.11.4's bug back, left it at 15 of 15\
  ↳ 1.11.5: cases through the real CLI and discovery path · guard: `selfcheck.py`: "the wiring" cases
- 1.11.3's skip treated a pack of commands and agents, a lone `CLAUDE.md`, or a single rule file as nothing to compare\
  ↳ 1.11.5 · guard: `selfcheck.py`: "commands only", "agents only", "CLAUDE.md only", "a single rule file is a valid target"
- `SECURITY.md` said every read was contained; five were not, and `"hooks": "../../elsewhere.json"` escaped with no symlink needed\
  ↳ 1.11.5: one guard every read passes through · guard: `selfcheck.py`: the 12 containment cases

<details>
<summary>5 more findings</summary>

- inline hooks crashed the run; managed settings were not read; a corrupt `settings.json` looked like "no plugins"\
  ↳ 1.11.5 · guard: `selfcheck.py`: "hooks inline in plugin.json are read, not a crash", "managed settings disabling it win over the user's enable"
- the fixes had four gaps of their own: `/x/pack` accepted `/x/packEVIL`, `notes.git` went to `git clone`, an empty inline hooks object counted as a hook, a refused manifest went unreported\
  ↳ 1.11.5 · guard: `selfcheck.py`: a case for each
- `SKILL.md` had drifted from the code in four places, one citing a skill on the author's machine\
  ↳ 1.11.6 · guard: `selfcheck.py`: "an agent's text is in the dossier"
- a global `CLAUDE.md` of one `@` import line: the rules it pointed at were never read\
  ↳ 1.11.7: imports followed the way Claude Code follows them · guard: `selfcheck.py`: the five `@`-import cases
- second sealed fixture: 82 of 93 with the instructions; controls, once kept away from them, 16 of 31 where the full runs scored 30\
  ↳ guard: sealed fixture 2

</details>

Eighteen mutations have each turned at least one self-check case red. Every published count re-cloned and re-run: all matched.

**A test of the helper is not a test of the decision.**

## 15. Four `pstack` ports: hooks where the manifest did not say

Lauren Tan's pstack, a Cursor skill stack, has several Claude Code ports. On 2026-09-28 neckbeard 1.12.5 was run on four of them, each by a separate Sonnet session: [michael-denyer/pstack-claude](https://github.com/michael-denyer/pstack-claude), [backnotprop/pstack](https://github.com/backnotprop/pstack), [ericlitman/open-pstack](https://github.com/ericlitman/open-pstack) and [EvanBatten/pstack-for-cc](https://github.com/EvanBatten/pstack-for-cc). Each port packages the same idea its own way, and two of those ways were new to the tool.

- two ports are marketplaces whose one plugin lives in `plugins/pstack/`; read from the repo root, the inventory reported no hooks and no agents where there were a `SessionStart` hook and 2 and 12 agents\
  ↳ 1.12.6: a marketplace's local plugin is inventoried, `--plugin NAME` picks one of several, several unpicked report hooks as unknown · guard: `selfcheck.py`: "a marketplace's only plugin, in plugins/<name>/, is the one inventoried", "several plugins and none chosen: hooks are unknown, never false"
- another has no manifest; its installer merges ten hook groups on eight events, `SubagentStart` among them, from `install.json` into `~/.claude/settings.json`, and the dossier said `has_hooks: false`\
  ↳ 1.12.6: hook-shaped JSON anywhere in the tree is reported, with the scripts that write `settings.json` · guard: `selfcheck.py`: "hooks in an installer's JSON are reported, with their reach"
- re-running the old and new inventory over local plugins found a third shape, a folder of plugins with no marketplace manifest, also reported as hookless\
  ↳ 1.12.6: hooks unknown, the nested plugins named · guard: `selfcheck.py`: "a folder of plugins: hooks unknown, and the plugins named"
- an independent review after 1.12.6 shipped found the new search stopped four levels down and said `false` for hooks below that, the same silence in a new place, and that a `marketplace.json` which failed to parse read as one listing nothing\
  ↳ 1.12.7: no depth limit, a budget of JSON reads that says so when it runs out, and parse errors carried into the dossier · guard: `selfcheck.py`: "hooks six levels down are found", "a search that runs out of reads says unknown, never false", "a search that found hooks and then ran out says it is incomplete", "a marketplace.json that is not JSON says so"

The evaluating sessions noticed all three and read the hooks by hand, so the reports were right; the tool was not. On its own, the inventory would have missed the hooks in three of the four. The gap was neckbeard's, not the ports'. Thanks to their authors for layouts that made the tool better.

**Where a manifest does not name hooks is not where there are none.**

## Who did the reviewing

Every reviewer here was an AI agent: a Claude session, run on the author's machine. "Independent" in these case studies means a separate session that had not written the code it was reviewing and had no stake in the result; it does not mean a human auditor. Both sealed fixtures were built and graded by such sessions, and the author has never seen their answers. The only outside human user so far ran an early version once and hit bugs that later rounds fixed.

## What the fifteen add up to

1. **The worst failures are silences.** Not wrong answers: absences that read as all-clears.
2. **The builder cannot audit the builder.** One session outside the build found more in an hour than eight rounds of self-testing.
3. **Nearly every run cost the tool something.** That is the argument for running it on things rather than trusting that it works.
4. **Bugs live where nothing goes.** Build the awkward case, and keep a real, awkward, unowned plugin in the suite, because you cannot construct the shape you failed to imagine.
5. **The half that resists testing goes untested, and nobody notices.** Ask separately which claims your method cannot check.

<details>
<summary>12 more</summary>

6. **"Could not resolve" is honest, not a dead end.** Ponytail and superpowers both hit it. In both cases, five minutes reading the named file closed the gap. The note earns its keep by saying exactly which file to open.
7. **Zero hooks and zero agents is not the same claim as "does nothing unattended."** Viral-launch-pipeline proves it: one skill's prose drove 21 real subagent dispatches, invisible to a files-only count.
8. **Total size and always-on cost are different numbers.** Superpowers: 231 files when measured, ~3.2KB injected. Viral: 34 files, 0 bytes injected, 21 dispatches once invoked. Neither number predicts the other.
9. **Instructions are testable, and were not being tested.** Nine rounds went at the code while half the tool sat unexamined. Handing the instructions to something with no idea of the intended answer found three defects in one pass, including a heading that existed only on the author's machine.
10. **A guard that has never fired is not known to work.** The carrying-cost criterion sat in the instructions for a full round before any fixture had hooks to trigger it. Writing a rule is not testing it, and the gap between those two is where this tool kept failing.
11. **A fix is a change, and changes need the same suspicion as the bug.** The §11 fix reintroduced the very defect it closed, narrower and better hidden, and shipped alongside a documentation sentence that made the new silence authoritative. It passed 39 plugins and 13 fixtures, because neither could contain the case it broke.
12. **"I could not read that" is a distinct answer from yes and no.** The last two bugs were both a broken hooks file collapsing into a confident wrong answer, once as a crash and once as a quiet falsehood. A vetting tool needs three states, and the third is the one that keeps the other two honest.
13. **The claim that the heuristics fail toward false positives was false.** It rested on one false positive and one true negative, neither of which is evidence about false negatives. An audit constructed five real writes, two of them into `$HOME`, and the persistence scan missed all five. A vetting tool that cries wolf wastes five minutes; one that stays quiet wastes your trust, and this one was staying quiet. See §9.
14. **Write the check so it can only pass for the right reason.** The MCP probe passed once because the test fixture's name contained the string being searched for. A green check that cannot fail is worth less than no check.
15. **Grading your own fixture is not a test, it is a rehearsal.** Rounds 10 and 11 planted the rules, knew the buckets, and marked the paper. They found real defects in the instructions, which is why they read as tests. What they could not do is fail in a way the author had not already imagined, which is the only thing a held-out set is for.
16. **A test of the helper is not a test of the decision.** Fifteen passing cases pinned two functions and left the lines that call them free to do the opposite. Sabotage found it in minutes; reading the tests never would have, because every one of them was correct.
17. **A guard added where the bug was found protects that spot, not the class.** Containment went onto each read path as an audit found it open, three times, and five paths nobody had attacked stayed open. A guard belongs where every read passes through, so the next read path is covered before anyone thinks of it.

</details>
