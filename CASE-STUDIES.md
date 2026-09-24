# Case studies

Every time this tool has been pointed at something real, in order. Each entry says what was found, and where the tool itself fell short, because the second half is the part that improves it.

| # | Target | Why it was picked | What it cost the tool |
|---|---|---|---|
| 1 | `ponytail` | the plugin that prompted this one | two resolver bugs |
| 2 | `neckbeard` | itself, before publishing | a false claim in its own README |
| 3 | `obra/superpowers` | the large one, picked by measurement | nothing, it held up |
| 4 | `Koz-TV/viral-launch-pipeline` | picked at random from 183 candidates | a blind spot on dispatch-by-prose |
| 5 | `claude-security` | Anthropic's own, two hook events never seen before | dead code and a misleading field name |
| 6 | all 39 Anthropic first-party plugins | a sweep, to find where it breaks at scale | a hook blind spot it had asserted away |
| 7 | purpose-built directories | attacking the branches no real plugin exercises | three bugs, one of them the biggest omission it could make |
| 8 | the last unexercised branches | closing the list out | a crash and a lie, both in hook parsing |
| 9 | an independent audit | someone who did not build it | eleven findings, four published claims proved false |
| 10 | the skill's judgment half | the last untested surface | three instruction defects, one machine-specific |
| 11 | the judgment half, hard case | overlapping sources, hooks that reach subagents | a silence that looked like an all-clear |
| 12 | re-audit of the previous fix | the fix itself was the regression | the same bug, reintroduced narrower |
| 13 | a sealed, held-out fixture | the judgment half, graded by someone who did not build it | its last self-graded claim |
| 14 | an adversarial pass before going public | the two newest versions had no outside scrutiny | a self-check that stayed green with the bug back in, five unguarded reads |

---

## 1. `ponytail`: the one that started it

Run against the installed `ponytail@ponytail`. Found all three hooks (`SessionStart`, `SubagentStart`, `UserPromptSubmit`) and the file they inject (`skills/ponytail/SKILL.md`, 6,637 bytes). Ponytail strips the frontmatter before injecting, so the real figure is nearer 5,229 characters, and no static read can know that. Six skills and six commands, no duplicates. Run cold against `addyosmani/agent-skills` by GitHub URL to exercise the clone path: 25 skills found.

**Two bugs it exposed in the first pass**, both since fixed. The resolver missed ponytail's injection because the path is built two hops away, through a `require()` and a `path.join(__dirname, ...)` rather than a single string literal. And the skill count was doubled, because ponytail ships mirrors for other agent ecosystems under `.openclaw/` and `.opencode/` that Claude Code never loads. Counting what the host cannot see is worse than not counting.

## 2. `neckbeard`: itself, before publishing

No hooks, no agents, one skill at 7,207 bytes. The parts that went as claimed went as claimed. The run also caught a false statement in this tool's own documentation.

The docs said a directory-source install never gets a cache copy: the source directory *is* the install, so there is nothing to go stale. True for most. Not true here, because this plugin's own source directory is a git repo. Claude Code cached it anyway, keyed to `plugin.json`'s version, and that cache sat on the first commit, holding an early draft of the description, through two later commits that fixed it, because the version number never moved. Only an uninstall and reinstall picked it up. Any session reading the plugin in that window read a false claim about its own token cost.

It also flagged its own `inventory.py` as a persistence risk, for calling `os.path.expanduser` three times. All three read a caller-supplied path; none write anything. The heuristic cannot tell "resolves a path" from "writes to disk", so it says so and leaves the read to a human rather than guessing, the same posture it takes on a hook it cannot resolve statically.

**Fixed:** the version now moves with every change that touches behavior, and the cache claim now says "usually", with the exception named.

## 3. `obra/superpowers`: the large one

288,751 stars, 231 files across 67 directories, 15 skills, one hook. Picked by checking real file, hook and skill counts across four candidates via GitHub's tree API, not by reading descriptions.

```
has_hooks: true, events: [SessionStart]
hooks_reach_subagents: false
skills: 15, total 168,036 bytes
```

The resolver could not statically resolve the injection: the command is `run-hook.cmd session-start`, a wrapper with no recognizable script extension, not the shape ponytail uses. It said so rather than guessing, though only after a detour: a later fix briefly made this exact hook report nothing at all, and the correction is §12. Read by hand, `hooks/session-start` cats `skills/using-superpowers/SKILL.md` (3,192 bytes), wraps it in `<EXTREMELY_IMPORTANT>You have superpowers.`, and emits it as session context.

**Two things it does better than ponytail**, found by reading the same file it injects. Its `SessionStart` matcher is `startup|clear|compact` only, with no `SubagentStart`, so a dispatched subagent never receives it. And the skill itself opens with `<SUBAGENT-STOP>` telling a subagent to ignore it if it somehow arrives anyway. Belt and suspenders, where ponytail had neither. The cost is 3,192 bytes once against ponytail's ~6,600 on every session and every subagent.

## 4. `Koz-TV/viral-launch-pipeline`: the random one

One skill, 15,919 bytes, zero hooks, zero declared agents. Picked with an unseeded `random.choice()` from 183 candidates, filtered out of Anthropic's official (310) and community (2,282) catalogs by keyword.

The description claims a "21-agent viral product-launch pipeline." From the numbers alone that reads as an overclaim: no agent files, no hooks, one skill. **That reading was wrong.** The skill's own text *is* the orchestration protocol, instructing the main session to call the `Agent` tool 21 times in sequence, four of them in one parallel batch, writing each stage to disk before the next reads it. The 21 agents are real. They are just not files.

**The blind spot this exposes is real and still open.** A pipeline built entirely as dispatch instructions inside one skill reports `agents: []` and looks inert next to a plugin that declares its agents as files. Zero declared agents does not mean zero agent-dispatching behavior. It means the dispatching lives in prose this tool does not yet parse for `Agent(` calls.

**The 15,919-byte skill is also not the whole plugin.** Twenty-one per-stage prompt files and six reference documents sit beside it, 92,456 bytes total, loaded one at a time as each stage runs. Not counting them toward always-on cost is correct, since nothing about them is standing. But a reader judging total footprint from "one 15KB skill" would be off by a factor of six.


## 5. `claude-security`: Anthropic's own security plugin

Version 0.11.0. One skill (5,246 bytes), **8 declared agents**, no commands, two hook scripts across three events, 476KB. Picked deliberately, because two of its hook events had never appeared in any previous run: `UserPromptExpansion` and `PostToolUseFailure`.

```
hook_scripts: 2, hook_registrations: 3
events: [UserPromptExpansion, PostToolUse, PostToolUseFailure]
hooks_reach_subagents: false
persistence: []
```

**The unknown events were handled correctly.** Both were listed rather than dropped or crashed on, which is the behavior you want from a tool that will meet event types invented after it was written. No fix needed.

**Dead code, found by reading the output next to the source.** A constant named `INJECTING_EVENTS` listed five hook events and was never used anywhere. It implied the tool classified events by whether they inject context. It does not. A misleading constant is worse than no constant in a tool whose pitch is honest inspection, so it is gone.

**A field name that was correct and misleading at the same time.** The run reported `reaches_subagents: false` for a plugin with **eight declared agents**. Technically right: the field meant "a hook of this plugin fires on a subagent event", and none of these do. But no reader seeing eight agents and "reaches subagents: false" concludes the right thing. Renamed to `hooks_reach_subagents`, which says what it measures.

**The persistence heuristic produced a true negative, and that is worth recording.** It reported nothing, against a plugin with sixteen Python files and two shell scripts. Checked by hand: `hooks.py` reads files and writes only to stdout and stderr, never to disk. Taken with the false positive it produced against its own `inventory.py`, the heuristic's failure mode so far is flagging reads as writes, not missing writes. That is the right direction for it to be wrong in, and now there is evidence rather than a hope.


## 6. All 39 Anthropic first-party plugins: the sweep

Rather than pick one, run it against every plugin in `anthropics/claude-plugins-official`, then check each report against what is actually on disk. Thirty-nine targets, no crashes, no timeouts.

**Twenty-five are real plugins, and the counts were perfect.** Skills, agents and commands matched the filesystem exactly in all twenty-five. No double-counting, no misses. The kind of result that is only worth reporting because the checking was mechanical rather than eyeballed.

**Fourteen have no `plugin.json` at all.** Twelve are language-server stubs carrying nothing but a LICENSE and a README. Two, `receipts` and `session-report`, carry real skills and no manifest, and the generic-pack path handled both correctly.

**The sweep found one genuine bug, and it was hiding in an assertion.** The generic-pack branch, taken whenever no manifest is found, returned no hooks field at all, and the README stated flatly that a manifest-less pack has "no hooks, no carrying cost by construction." It had never looked. Confirmed by building a directory with a live `SubagentStart` hook and no `plugin.json`: neckbeard reported nothing about it at all, while claiming there was nothing to report.

Nothing in this catalog triggered it, which is exactly why it survived five previous case studies. A manifest-less directory that silently injects into every subagent is the single worst thing this tool could fail to mention, and it would have shipped that way.

**Fixed:** the generic-pack branch now runs the same hook and persistence inventory as the plugin branch, and the README no longer asserts what the code does not check. Re-ran all 39 afterward: no regressions, every dossier now carries a hooks field.


## 7. Purpose-built directories: attacking the unexercised branches

Case study 6 ended on a conclusion: the dangerous defects live in code paths no real plugin happens to take. So this run targets the branches directly, with directories built to provoke them rather than plugins found in the wild.

**What held up.** A `plugin.json` at the repo root instead of under `.claude-plugin/`: read correctly, version and all. A `hooks.json` in the flat shape with no top-level `hooks` wrapper: parsed, event found. A completely empty directory: handled, no crash, honest zeros. Both error paths produce a message naming the problem and what to do instead.

**Three bugs, in ascending order of how bad they were.**

*A skill with no frontmatter was named `SKILL`.* The fallback used the filename stem, and every skill file in Claude Code is called `SKILL.md`, so every frontmatter-less skill in a pack reported the same useless name. A skill's identity is its directory: `skills/<name>/SKILL.md` is named `<name>`. Fixed to read the parent directory.

*`--extra-rules` pointed at a directory silently contributed nothing.* The flag exists precisely for rules the automatic discovery would miss, and the directory branch then filtered by filename, accepting only `SKILL.md` and `CLAUDE.md`. Point it at a folder of rules named anything else and you get silence: no error, no warning, and a report that reads as though your rules were considered. Now takes every markdown file under an explicitly-given directory, warns when a path matches nothing, and warns when the path does not exist at all.

*A plugin declaring MCP servers reported nothing whatsoever.* The dossier filters the manifest down to name, version, description and license, so two declared MCP servers vanished completely. This is the worst omission the tool could make. An MCP server is a live tool surface with network reach and real side effects, which makes it the highest-consequence thing a plugin can ship, and it was the one thing a reader would never learn.

The first check of this even gave a **false pass**: the probe searched the dossier for the string "mcp" and found it, because the test plugin had been named `mcpplug`. Worth recording as its own small lesson about writing a check that can only pass for the right reason.

Now reported as a `mcp_servers` block with a count, each server's name, command and transport, and a note that this is the declaration only. What a server actually exposes is knowable only by speaking MCP to it, which this tool does not do and says so.

**Both of those sentences were wrong**, and an independent audit proved it. An earlier version of this section claimed nothing in the 39-plugin catalog declares an MCP server, and that no sweep of real plugins could have caught the omission. Anthropic's own `example-plugin`, inside those 39, ships a `.mcp.json` declaring one. The fix read the inline `plugin.json` key only, so the sweep would have found it if the fix had looked in both places. See §9.


## 8. The last unexercised branches: a crash and a lie

Three paths remained untested after round 7: the recursion limit on hook injection, a `hooks.json` that is present but broken, and a symlinked target.

**Two held.** Beyond the one-hop recursion limit, a payload buried two `require()` calls deep produced "could not statically resolve, read the hook scripts manually" rather than a confident claim of no injection. That is the limit failing in the honest direction. A symlink pointing at a real plugin resolved correctly, 8 agents and all.

**Broken hook files produced a crash and a lie.**

A `hooks.json` containing invalid JSON reported `has_hooks: true` with an empty event list. Both halves are wrong. There *are* hooks, or at least a hooks file, and reporting zero events invites the reader to conclude the plugin registers nothing. The truth was "there is a hooks file here and I could not read it", which is exactly the kind of thing this tool exists to say out loud.

A `hooks.json` containing valid JSON of the wrong shape, a list where an object belongs, **crashed with an uncaught `AttributeError`**. The parser accepts two layouts, nested under a `hooks` key or flat at the top level, and called `.get()` without ever checking it had an object at all.

Both now return `has_hooks: "unknown"` with a `parse_error` naming what went wrong and telling the reader to open the file. A three-state answer, because "yes", "no" and "there is something here I could not read" are three different facts and only the third was missing.

**This section originally claimed the class was closed. It was not.** The guard checked one nesting level, the one the fixture happened to exercise, and three deeper shapes still crashed. Found by the audit in §9.

All 39 catalog plugins re-run afterward: no crashes, and not one false "unknown".


## 9. An independent audit: the one that found the most

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


## 10. The judgment half: the first thing that passed

Every round so far tested `inventory.py`, the mechanical half. The other half is `SKILL.md`, a set of instructions a model follows to classify rules, and nothing had ever tested whether those instructions work.

Mechanical testing cannot do it, and neither can the author: writing the instructions and then following them means filling every gap with the intent you already had. So: a fixture with four planted rules whose correct buckets are unambiguous, a rules corpus built from scratch under a throwaway `HOME` so the answer is fully controlled, then a model given the instructions and the dossier and **nothing else**, with no idea what the right answers were.

| planted rule | correct bucket |
|---|---|
| prefer stdlib over a new dependency | duplicate of an existing rule |
| run destructive commands without confirming | conflict with a hard stop |
| prefix temporary files with `tmp-` | new, standing |
| on request, list unused dependencies | new, on-demand |

**Four out of four, twice.** The conflict was cited against the exact rule and the file it lives in, which is what Step 2 demands. This is the first time anything here passed on substance.

**The instructions failed three ways, and one was the same mistake as round 7.**

Step 4 told the reader to append to a section by name. That heading existed only in the author's own rules file. Any reader organised differently had to guess, and the executor said so plainly. It is the same class of defect as the hardcoded `~/proj` path caught earlier: a public tool carrying an assumption about one machine. Step 4 now hands over a method rather than a name, and requires the reader to say which section they chose.

Step 4 also demanded a "which repo" for any proposed skill, a field neither the instructions nor the dossier can supply, so the executor invented one. It now asks for a proposed name marked as a proposal, and forbids inventing a location when the dossier does not show one.

Step 2 said to weigh carrying cost and gave no criterion at all. It now gives one, and names the zero-hook case explicitly as having nothing to weigh.

**What this run did not test, in the executor's own words.** The fixture is the easy case: no hooks, no persistence, no commands, one rule source. It never exercised reconciling a target against several overlapping rule sets, which is where the real classification difficulty lives, and it never exercised the by-hand path for a hook whose injection cannot be statically resolved. The carrying-cost criterion's non-zero branch is still, in its words, "a slogan rather than a test."


## 11. The judgment half again, on the hard case

Round 10 passed, and the executor said plainly why that proved less than it looked: one rule source, no hooks, no persistence, four unambiguous buckets. An audit made the same point more sharply. A criterion no test has ever made fire is not known to work, and the carrying-cost rule had never fired, because every fixture had zero hooks.

So: three overlapping rule sources that partly restate each other, a target whose hooks reach subagents so the cost branch has to execute, and one rule whose correct bucket is genuinely arguable.

| planted rule | correct answer |
|---|---|
| prefer stdlib | duplicate, but of the **global** file, where it stands alone, not the project file that mentions it in passing |
| justify dependencies in the PR | duplicate of the **project** file, not the global one |
| skip tests on hotfixes | conflict with a project rule that says "no exceptions for hotfixes" |
| rationale comments on odd code | **deliberately arguable**: conflicts with "explain in the commit message, not a code comment", or is merely new |
| summarise changes since the last tag | duplicate of a **personal skill**, not of any rules file |

**Five of five.** It picked global over project for the first and said why, picked project for the second, found the duplicate that lived in a skill rather than a rules file, and on the arguable one gave both readings, chose the literal text, and called its own answer a coin flip rather than dressing it up. The carrying-cost branch fired for the first time and returned the right verdict: five rules in, none survived, nothing to justify a permanent injection.

**It also found a real bug, and it is the familiar shape.** The target's `PreToolUse` hook gates every Bash call and reaches subagents, and its script could not be statically resolved. The dossier said nothing at all. Not an unknown, not a note, just absence, because the warning only fired when *no* hook in the whole set resolved. One hook that did resolve silenced the warning for every hook that did not, so a gate whose behaviour is unknown looked exactly like a hook with nothing to inject.

The executor caught it unprompted and named the consequence: the procedure's own trigger to go read a script never fired, so a silent gap could pass through the judgment step undetected. Unresolved hooks are now listed individually, and the distinction is stated where it matters. A hook in neither list has nothing to inject. A hook in `unresolved_hooks` has behaviour that is unknown rather than absent. Those are different findings.

Two instruction gaps closed alongside it: which source to cite when several cover the same ground, and what to do when exactly one rule survives the carrying-cost test, which the old criterion left undefined above zero.


## 12. The fix that was the regression

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

---

## 13. The last claim resting on the builder's word

Rounds 10 and 11 tested the judgment half and both passed. Neither pass was worth what it looked like, for a reason that took an outsider to name: **the builder designed those fixtures, planted the rules, knew the correct bucket for each one, and graded the result.** Every other claim in this repo had by then been re-derived by someone with no stake in it. That one had not, and it was the only one left.

It is also the claim that mattered most. The mechanical half can be checked against a filesystem. The judgment half is a set of instructions to a model about sorting rules into duplicate, conflict and new, and there is no disk to compare it to. "Not mechanically testable" had quietly become "not tested by anyone but the author," and those are very different sentences.

The close was to hand the whole problem out. An outside auditor built its own fixture corpus, sealed the ground truth before a single evaluation ran, pre-registered the rubric it would grade against, ran six evaluations, and scored them itself. The builder specified none of it and saw none of it.

**The fixture is now sealed and lives outside this repo, and this file is not going to tell you what is in it.** That is not coyness. A held-out set is worth something for exactly one reason, that the thing being graded has not seen the answers, and a model that reads the ground truth will score well on it while the score means nothing. Nothing afterwards can distinguish that from a real pass. There is no undo and no second copy, so the only safe place to keep it is somewhere the author of the instructions does not look.

**The lesson is about the shape of the gap, not the score.** Twelve rounds of increasingly adversarial testing all pointed at the half that was easy to test, and the half that was hard to test went twelve rounds untouched while the document you are reading grew steadily more confident. Nobody decided to skip it. It simply never came up, because the available tools did not reach it and nothing forces you to notice the question your tools cannot ask.

**Re-run on 1.11.6 (2026-09-24).** A fresh session on another machine re-ran the fixture against the rewritten instructions and reported only a score. The full instructions scored 12/12 on both evaluations, matching the original. The weakened controls also scored 12/12, up from 10.5 and 10, so by the fixture's own pre-registered rule the run is inconclusive: the current model no longer needs the instructions to pass it. A held-out set wears out as models improve, and the controls are what showed it. A second fixture, aimed at what only the instructions produce, is being built.


## 14. Before going public: the tests that tested the wrong thing

1.11.3 and 1.11.4 landed the day after the last round, and only the session that wrote each fix had reviewed it. They were the newest code with the least scrutiny, in the repo about to be made public, so on 2026-09-24 they got an adversarial pass first: three reviewers, run through `falsify` (the adversarial-audit skill from the `delegation` plugin), one on the code, one on the guards, one on the claims in these documents. None of them built this tool. The method is still the author's own, so this is not independent in the sense §9 and §13 are.

**The self-check passed for the wrong reason.** `selfcheck.py` shipped with 15 cases covering the two paths that fail silently. Every one of them called a helper directly. None ran the code that decides. A reviewer inverted the line in `main()` that chooses whether to read the reader's rules, and the suite stayed at 15 of 15. It then reverted discovery to reading one settings file, the exact bug 1.11.4 fixed, and the suite stayed at 15 of 15. The commit's claim, "15 checks, all passing", would have stayed true with the bug back in. A test of the helper is not a test of the decision.

**1.11.3's skip reached further than 1.11.3 knew.** It skips the reader's rules when the target carries nothing to compare. "Nothing" meant no skill and no hook. A pack of `commands/` and `agents/` telling the model to skip the tests and log nothing counted as nothing, and so did a directory holding only a `CLAUDE.md`. A single rule file could not be a target at all: the tool exited with "not a directory", though the skill's own description says it vets one. Each is the failure 1.11.3 set out to fix, in a shape it did not consider.

**SECURITY.md said every symlink was checked. Five reads were not.** The containment guard sat on the three paths where earlier audits had found an escape: a plugin's skills, a hook's script, and the files an injection pulls in. It was missing from skills in a pack with no manifest, from the hooks file, from `.mcp.json`, from `plugin.json`, and from the README excerpt. The hooks file was the worst of them. `plugin.json` names it, and `"hooks": "../../elsewhere.json"` read a file from outside the target with no symlink needed. All of it now goes through one guard, and ten fixtures plant a marker outside the target and fail if it reaches the dossier.

**Smaller things, each a silence or a crash.** Hooks written inline in `plugin.json` as an object, a shape Claude Code accepts, crashed the run with no dossier. Managed settings, the layer an organisation uses and nothing overrides, were not read, so a plugin it had disabled still counted. A corrupt `settings.json` read exactly like "no plugins enabled", with no warning.

**These documents had drifted too.** The table at the top of this file stopped at round 12. The 1.11.4 changelog said discovery had found "one eighth" of the rules in force; 8 of 23 is about a third. The README and the close of this file both said the twelfth round came back clean, when §12 is the round that found a regression, and it was the re-audit of that round's fix that came back with nothing.

**What held.** The reviewer on the claims re-cloned ponytail, superpowers, agent-skills and claude-security and re-ran the published counts. Every byte count, skill count and hook event matched. Superpowers has grown since (261 files where §3 says 231), which is the repo moving, not the tool.

**How the fixes were checked.** Every fix was broken on purpose, one at a time, in a scratch copy, including the two mutations that had left the old suite green. One mutation first appeared to pass, and only because it had broken the script's syntax, which proves nothing; a mutation that ran showed the case does fail. Then a fourth reviewer attacked the fixes themselves and found four more gaps in them. No check would have noticed a containment test that forgot the path separator, so `/x/pack` would have accepted `/x/packEVIL`. No check covered a rule file named `notes.git`, which would have gone to `git clone`. An empty inline hooks object counted as a hook. And a refused manifest went unreported when a second one was used. All four are closed. The self-check ends at 37 cases, 21 of them through the real CLI or the real discovery path, and eighteen mutations have each turned at least one of them red.

**The instructions had drifted from the code.** 1.11.5 left `SKILL.md` alone, because the sealed fixture of §13 graded that text. It was stale in four places. Step 1 described plugin discovery as the project's settings file alone. Step 2 did not name the new `rule_files`, `commands` and `agents` fields, and commands and agents reached the dossier as filenames only, which left nothing to read once a git-URL target's temp clone was gone. Step 3 wrote evaluations into whatever project the reader sat in, with no check that anything ignored them. And Step 4 cited `list-item`, a skill that exists only on the author's machine: the same defect §10 found in a section heading. 1.11.6 fixes all four and embeds the text of commands and agents, with two more containment fixtures and one that fails if an agent's text is missing. The self-check stands at 40 cases.

That costs something real. The §13 score now describes instructions that no longer ship. The fixture is not spoiled, since nobody has read it, but its result is a statement about 1.11.5, not about this version, until it is run again.

**And one more, found by using it.** The first reports run on 1.11.6 compared targets against a global `CLAUDE.md` of 26 bytes. That file held one line, `@~/.claude/roles/...`, because Claude Code lets a rules file import others and the author had split his rules that way two days earlier. The tool read the line and not the five files it pointed at, which held every rule a target could conflict with. It is 1.11.4's failure again, one layer down: discovery ran, reported success, and compared against almost nothing. The evaluator noticed only because its dossier looked too small. 1.11.7 follows imports the way Claude Code does, and the self-check proves each rule of that (nesting, the five-hop limit, nothing inside code, no escape from a target) by breaking it. One of those checks passed with its guard removed on the first try, because the fixture could not reach the code it named. That is round 14's lesson, repeated by the round's own author the same afternoon.

**The second fixture.** An outside session built and sealed a harder one, aimed at what only the instructions produce, and 1.11.7 scored 82 of 93 (88%), with 4 points of difference between two runs on the same target. The first controls did not work: their prompt named the plugin's folder, so they read the instructions they were meant to lack. The brief allowed that, and the grader reported it rather than scoring around it. Repaired and re-run with the instructions out of reach, the controls scored 16 of 31 on the same targets where the full runs scored 30. That is the first evidence in this repo that the judgment half does work the model does not do alone. The repair found one more hole on the way: a control searched the disk and listed a path inside the sealed fixture, and was stopped before it opened anything.

---

## What the fourteen add up to

- **"Could not resolve" is honest, not a dead end.** Ponytail and superpowers both hit it. In both cases, five minutes reading the named file closed the gap. The note earns its keep by saying exactly which file to open.
- **Zero hooks and zero agents is not the same claim as "does nothing unattended."** Viral-launch-pipeline proves it: one skill's prose drove 21 real subagent dispatches, invisible to a files-only count.
- **Total size and always-on cost are different numbers.** Superpowers: 231 files, ~3.2KB injected. Viral: 34 files, 0 bytes injected, 21 dispatches once invoked. Neither number predicts the other.
- **Nearly every run has cost the tool something.** Eight of the first nine found a bug or a limit. The ninth, run by someone who did not build it, found more than the previous eight combined and proved four published claims false. The first clean result was the re-audit that closed round twelve, and it took eleven rounds to earn that. That is the argument for running it on things rather than trusting that it works.
- **The builder cannot audit the builder.** Eight self-directed rounds attacked branches the builder thought of, and never asked what the tool's own output contained. That question took an outsider about an hour.
- **Instructions are testable, and were not being tested.** Nine rounds went at the code while half the tool sat unexamined. Handing the instructions to something with no idea of the intended answer found three defects in one pass, including a heading that existed only on the author's machine.
- **A guard that has never fired is not known to work.** The carrying-cost criterion sat in the instructions for a full round before any fixture had hooks to trigger it. Writing a rule is not testing it, and the gap between those two is where this tool kept failing.
- **A real plugin with an awkward shape caught what a constructed corpus could not.** Thirty-nine catalog plugins and thirteen purpose-built fixtures were all clean while a live defect sat in the open, and one third-party plugin found it. This is the inverse of the lesson above and both are true: build the awkward case *and* keep a real, awkward, unowned target in the suite, because you cannot construct the shape you failed to imagine.
- **A fix is a change, and changes need the same suspicion as the bug.** The §11 fix reintroduced the very defect it closed, narrower and better hidden, and shipped alongside a documentation sentence that made the new silence authoritative. It passed 39 plugins and 13 fixtures, because neither could contain the case it broke.
- **The worst failures are silences.** Not wrong answers: absences that read as all-clears. A branch asserting no hooks without looking, a dossier omitting declared MCP servers, a resolver naming the wrong file with no caveat, an unresolved gate hook reported as nothing at all. Every one of them looked calm and said nothing.
- **"I could not read that" is a distinct answer from yes and no.** The last two bugs were both a broken hooks file collapsing into a confident wrong answer, once as a crash and once as a quiet falsehood. A vetting tool needs three states, and the third is the one that keeps the other two honest.
- **The claim that the heuristics fail toward false positives was false.** It rested on one false positive and one true negative, neither of which is evidence about false negatives. An audit constructed five real writes, two of them into `$HOME`, and the persistence scan missed all five. A vetting tool that cries wolf wastes five minutes; one that stays quiet wastes your trust, and this one was staying quiet. See §9.
- **The dangerous bugs live in the branches nothing exercises.** Twenty-five real plugins agreed with disk perfectly. Every genuine defect since has come from a directory built to provoke one specific path: the manifest-less pack with hooks, the frontmatter-less skill, the explicitly-passed rules folder, the bundled MCP server. Sweeping a catalog finds crashes. Only constructing the awkward case finds the assertion nobody checked.
- **Write the check so it can only pass for the right reason.** The MCP probe passed once because the test fixture's name contained the string being searched for. A green check that cannot fail is worth less than no check.
- **The half that resists testing is the half that goes untested, and nobody will notice.** Twelve rounds hammered `inventory.py`, which a filesystem can contradict. `SKILL.md` went twelve rounds on the author's own say-so, not because anyone chose to skip it but because no available tool reached it. Absence of a test leaves no trace in a test report. Ask separately which claims your method is structurally incapable of checking, because that list will not appear on its own.
- **Grading your own fixture is not a test, it is a rehearsal.** Rounds 10 and 11 planted the rules, knew the buckets, and marked the paper. They found real defects in the instructions, which is why they read as tests. What they could not do is fail in a way the author had not already imagined, which is the only thing a held-out set is for.
- **A test of the helper is not a test of the decision.** Fifteen passing cases pinned two functions and left the lines that call them free to do the opposite. Sabotage found it in minutes; reading the tests never would have, because every one of them was correct.
- **A guard added where the bug was found protects that spot, not the class.** Containment went onto each read path as an audit found it open, three times, and five paths nobody had attacked stayed open. A guard belongs where every read passes through, so the next read path is covered before anyone thinks of it.
