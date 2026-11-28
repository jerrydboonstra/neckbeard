# Changelog

**Everything before 1.12.2 was developed in private; 1.12.2 is the first public release.** Fifteen rounds of adversarial testing each found a defect and shipped a fix, which is why the version starts high (see CASE-STUDIES.md). Those numbers are kept rather than collapsed to 1.0.0, since the plugin cache is keyed to version and 1.0.0 already refers to different content.

What each round cost the tool is written up in `CASE-STUDIES.md`. This file is the short version.

## 2.0.5 (2026-11-28)

### The herd
- The persistence list no longer counts a redirect to /dev/null or another standard device, or <name>/ text in usage messages, as writing a file.
- The persistence scan now tells a file that writes from one that only names a home path, and catches writes made through a shell variable another script sets.
- The plugin's author, the marketplace's owner and the license's copyright line now read Jerry D. Boonstra.
- A named pipe or device inside a target no longer hangs the scan: only regular files are read, and the persistence note names what was left unread.
- The persistence scan now reads ${HOME:-x}/ and ${HOME:+x}/ as home paths, and counts a write to a path's dirname.

## 2.0.4 (2026-11-27)

### Security

- **Vetting a folder that came with its own `.git` no longer lets that folder's git settings run a program.** To mark a report "+ uncommitted changes", vet ran `git status` in the target, and git ran any `core.fsmonitor` command or filter driver the target's own config named. Vet now checks with a temporary git folder that carries none of the target's config. `SECURITY.md` now says that by default vet never runs the target (`--live-mcp` is the named exception), and it lists the files the skill writes.

### Plugin directory

- **neckbeard has a listing icon,** `.claude-plugin/icon.png`, made from its logo at 1024 px. The README shows the logo in Markdown image syntax, and a new section says in one place what neckbeard runs, fetches and sends.
- **Each release also publishes a slim copy of the plugin as the `plugin` branch.** It holds only what the plugin loads and runs, within the directory's limits, with README links rewritten to the release's tag. The repo's layout and install paths don't change. If that push fails, the release still completes and prints a warning, and `make slim-push` runs it again.

### Docs

- **The guide to publishing a report has an "Invite an author" section:** when to invite another plugin's author to publish their report, what a good invitation includes, and that only the person who ran the vet sends it.

## 2.0.3 (2026-11-21)

### Releasing

- **`make deploy` installs from an export, not from the working checkout.** Until now the neckbeard marketplace loaded from the checkout itself, so a branch switch or an edit there reached every running session. Deploy now keeps a clone of the released repo at `~/.claude/plugin-src/neckbeard`, makes it when it is missing, and moves it only to the released commit, by fast-forward on a clean `main`. It refuses an export that holds commits beyond the release.
- **Switch each machine once before deploying 2.0.3.** A directory marketplace that loads from anywhere but the export is refused, and deploy prints the steps: clone the export, remove the `neckbeard` marketplace, add the export in its place, and install the plugin again. A marketplace added from GitHub needs no export and deploys as before. A host in `HOSTS` with no export refuses and prints the clone step, to run with that host's own way of reaching the repo.

### Measurements

- **Five vet runs of Cat Herder 0.40.3 on neckbeard 1.14.0 are published** in `measurements/2026-10-16-vet-stability-0.40.3/`: the verdict still flipped (COPY RULES, SKIP PLUGIN in 3 of 5; INSTALL in 2 of 5), on one judgment about the target's workflow skills, and no run found a conflict.

## 2.0.2 (2026-11-19)

### Reports

- **Skills marked `disable-model-invocation: true` no longer count as every-session cost.** Claude Code leaves their descriptions out of the session until the user calls the skill by name, but the Cost row and the Injects card counted them anyway. For one plugin that put 57 of its 58 skills behind the key, the report counted 12,394 characters where 275 load. The inventory now records each skill's `model_invocable`, and the Injects card says how many skills load only when called. Reports made from older dossiers render as before.
- **Cards say "1 file" and "1 skill", not "1 files".**

### README

- **The CI and CodeQL badges show main's result.** Without a branch, a workflow badge shows the latest run on any branch, so a run elsewhere could turn it red.
- **A changelog link sits under the title.**

### Releasing

- **`make release` runs CI before public main moves.** It pushes a `release/v<version>` branch to GitHub and waits for CI there. Only a green run moves main, makes the tag and deletes the branch. A red one leaves main untouched (2.0.2's first attempt left a failing commit on main).
- **`make release` refuses a tree that names a word from a private list** (`PRIVATE_WORDS` in the git-ignored `local.mk`), before anything is pushed. A hit is reported by file and line, never by the word.
- **`make deploy` runs an optional `POST_DEPLOY` command after every host has deployed,** also set in `local.mk`. Empty by default.
## 2.0.1 (2026-11-19)

### Reports

- **"Where it takes a position" keeps one order from run to run.** Two quotes on the same line, or from the same hook, were listed in whatever order Python's hashing gave that run, so two runs on the same plugin could differ. They now sort by their text too.

### Releasing

- **`make release` waits for CI before it tags.** It pushes `main` to GitHub alone, waits for CI to pass on that exact commit, and only then creates the tag and pushes `main` and the tag to the other remotes. A failed CI leaves no tag and the mirrors untouched.

### Docs

- **`docs/slsa-provenance-research.md`: what SLSA provenance could add to an inspection, and why neckbeard does not use it yet.** The OpenSSF generator is no longer maintained, and no Claude Code installer checks an attestation today.
## 2.0.0 (2026-11-19)

**A new report layout, and a fit verdict computed by code.** A report now opens with a contents list and three layers: how the plugin affects you, what it adds, and where it takes a position. In a fit report, code computes the verdict and the counts from a fixed list of the plugin's rule units; a model answers each unit, but no model writes the colours, counts or verdict. The major version marks the new layout: anything that parses a 1.x report needs updating.

### Reports

- **tools/vet writes the 2.0 layout.** A report opens with a contents list, then three layers: "How it affects you" (the summary rows, then the fit for a fit report), "What it adds" (the facts cards) and "Where it takes a position". A published report carries no verdict.
- **The fit verdict and counts come from code.** `tools/rule-units` numbers the plugin's rule units, so every run judges the same items; the judge answers each unit, and `tools/units-verdict` computes the verdict and counts. The report shows a verdict strip and seven fit cards. The units path is now the default, and `--units` does nothing.
- **A plugin whose hooks run at session start or reach subagents gets COPY RULES, SKIP PLUGIN when the judge finds the carrying cost too high.** The answers file gains a `carrying_cost` field (`install`, `copy` or `reader-decides`), and the verdict code uses it, so the headline and the "Do this" steps agree. Answers without it are refused for such a plugin.
- **A "How it affects you" summary: five rows, each coloured by a written rule.** `tools/summary` prints Cost (what the plugin adds to every session; hook text counts twice when hooks reach subagents), Reach, Leaves state, Live surface and Read completeness. Code sets each colour (🟩🟨🟧🟥) from the dossier, and the rules print under the rows, so a reader can check them. A row whose input was not read in full is never 🟩.
- **The facts layer is six collapsible cards, each with a read marker and a gist computed by code.** "What it adds" starts with a legend (🟢 read in full, 🟡 partly read, 🔴 something unread), then one card each for Injects, Hooks, Subagents and commands, State it may leave, Reaches outside the session and Source. A card's marker says only how much neckbeard read, never whether the plugin is good. `tools/cards.py` writes every card. `tools/part1 --read-state DOSSIER` prints the overall read state, and the README badge takes its word from it, so the badge and the cards cannot disagree.
- **"Where it takes a position" is one collapsible card per topic.** `tools/positions-layer` prints each position as its quote and a `file:line` place, linked to the file at the target's commit when the report has a GitHub repo. A quote makes no Markdown link, image or code span of its own, and absolute paths show as basenames.
- **neckbeard now reports Claude Code mods.** A mod is a JavaScript or TypeScript file a plugin lists under `modules` in a hooks file; it runs inside the session with your permissions and no sandbox. The hooks dossier lists each mod, and the report adds a "Claude Code mods" card after Hooks. A path outside the plugin is refused and never opened. A listed mod makes the hooks section partly read, since neckbeard does not read its source.
- **A `node -e` hook that only requires one plugin script now names and reads that script.** The report and the inventory take `hooks/x.js` as the script of a hook such as `node -e "require(require('path').join(process.env.CLAUDE_PLUGIN_ROOT,'hooks/x.js'))"`. Any other inline code still prints as `<unparsed command>`.
- **The gallery is regenerated in the 2.0 layout.** The eight example reports, `docs/neckbeard-report.md`, and every README and case-study excerpt show the summary table and the facts cards.

### The skill

- **/neckbeard writes its report through tools/vet when tools/ sits beside the skill.** The session judges the units and writes the prose; `tools/vet --dossier --answers --prose` then computes the colours, counts and verdict with no model call. In a plain skill folder, the skill writes the 2.0 layout by hand and says the colours are its own. Step 2's sorting instructions are unchanged, word for word.
- **`tools/vet` writes a fit report from a session's own answers** (`--dossier`, `--answers`, `--prose`), with no model call.

### Fixed

- `tools/vet ... --judge own` no longer stops with "cfg[@]: unbound variable" under the bash 3.2 that ships with macOS.

### Checks

- **CodeQL now also scans the GitHub Actions workflows, and can be run on demand** (`workflow_dispatch`, from the Actions tab or `gh workflow run codeql.yml`).

### Measured

- **Five runs on Cat Herder 0.40.3** (`measurements/2026-11-18-units-default/`): the verdict was INSTALL WITH CHANGES in all five, with the same conflict each time. The card counts were not stable: one run's find passes missed one of the two conflicts, and six units' answers varied between runs. Both causes are queued for a later release.
- **The judgment half against the held-out sealed fixture** (`measurements/2026-11-18-sealed-judge-2-0/` and `-rerun/`): run under the fixture's full protocol, both runs with neckbeard's instructions scored 12 of 12 and passed its pre-registered bar. The control runs, given a set of instructions about 7% as long, scored 12 and 11, so this fixture does not tell the two apart: the judgment half is unverified by it. A new, harder fixture is planned.

## 1.17.8 (2026-11-18)

### Reports

- **Large scripts are now read in full, up to 2 MB, when listing what a plugin may leave on disk.** A plugin with one script over 50 KB no longer gets "partly read" for that cut, and a script built to slow the scan down still finishes in seconds. A script over 2,000,000 characters is still noted as capped.
- **The report badge's left label is now "neckbeard", not "neckbeard report".** The tool name sits on the left and the result on the right, as other badges do; the link still opens the report. Every repo picks it up at its next report refresh.

### Docs

- **The README badge row now reads CI, license, release, CodeQL, then the neckbeard report.** The "self-check" badge is renamed "CI" (the workflow's name is now `CI`; its file name is unchanged). New badges: MIT license, latest release, and CodeQL, which analyses the Python in `skills/neckbeard` and `tools` on each push to main, each pull request and weekly.

### Checks

- **neckbeard's skill text now has a byte budget.** `tools/skill-budget.txt` sets a line for `skills/neckbeard/SKILL.md` (bytes) and for the skill descriptions together (characters), each about 5 percent over today's size, and every description must stay under 1,024 characters. `make check` runs `tools/test_skill_budget.py` and fails when a size passes its line. To raise a line, edit the file in a reviewed commit that says what the extra text buys.

## 1.17.7 (2026-11-15)

### Reports

- **A shell hook that builds its printed text at run time is now read.** The report shows each printed line, with "…" for parts known only at run time, and each file the script writes. Scripts it cannot follow stay "partly read".

### Docs

- **The README opens with a prompt-based Install section.** Paste one prompt into Claude Code, or type one `/plugin install` line, to install neckbeard.

## 1.17.6 (2026-11-15)

### Reports

- **A report on a checkout with uncommitted changes says so.** Its header and Source line read "<commit> + uncommitted changes" when the files read differ from that commit. `tools/vet --facts` also takes `--release-tag`, so a plugin's own published report can name its release tag, as neckbeard's now does.
- **The README's report excerpt shows counts.** It lists how many skills and persistence candidates neckbeard's own report finds, in place of empty bullets.

### Docs

- **The publish guide names the current release, and a check keeps it in step.** The marketplace description, the README definition of "reader" and the score link now read plainly.
- **Each gallery row says which sections of its report are partly read, and why.**

## 1.17.5 (2026-11-15)

### Reports

- **A repo can list its test fixture folders in a `.neckbeard.json` at its root.** Unreadable files in a listed folder no longer make the hooks or persistence sections "partly read", and the report names each listed folder under "Declared fixtures, not read". The hook and persistence search still walks those folders and counts what it finds there. neckbeard lists `tools/fixtures` in its own repo.
- **neckbeard's own report now reads in full, with a green badge.** The inventory code is split into five modules under `skills/neckbeard`, each under 40,000 bytes, and `tools/test_vet.py` is split under the read cap too, so no file counts as read capped.

## 1.17.4 (2026-11-15)

### Reports

- **An explicit `--judge reader` copies your login on Linux, like the default judge.** When it cannot log in, it stops before judging, names the reason and `--judge own`, exits non-zero and writes no report. It no longer falls back to your own config. A failing judge call's last error lines reach stderr, and the report header names the judge that ran.

## 1.17.3 (2026-11-15)

### Docs

- **The README opens with its original tagline again.** The note on the yellow "partly read" badge moved down, beside neckbeard's own report.

### Plugin listing

- **The plugin description opens with its original line again.** An installer sees the same first words as the README.

## 1.17.2 (2026-11-15)

### Docs

- **The README, gallery and case studies open with facts reports.** Each shows what a plugin adds, on its current version, with no verdict on someone else's plugin; neckbeard's report on itself stays as the one verdict example. The README explains the yellow badge and shows how to run neckbeard in three lines.
- **The maintainer guide moved to `docs/publish-your-report.md`.**

### Reports

- **The judge can now run as the sample reader on Linux.** For the default sample reader, vet copies your login file into the throwaway reader folder for the run and deletes it afterwards; a `--reader` folder never gets it, and a Mac still falls back to your own config. vet refuses output that holds your login's tokens, and says why whenever it falls back.

### Plugin listing

- **The plugin and marketplace descriptions match what neckbeard does.** They list what it reads and adds, and no longer quote another plugin or old token figures.

## 1.17.1 (2026-11-14)

### Inventory

- **A repository whose marketplace lists both the root plugin and a nested one is read as the root plugin.** Such a repository (Cat Herder and its `herd-wake` mod, for one) was read as the nested plugin: the report's name, skills and hooks came from the subfolder while its header named the root. The root's manifest, skills and hooks are now the default, `--plugin NAME` still picks the nested one, and a root with no manifest no longer counts a nested plugin's skills as its own.

## 1.17.0 (2026-11-12)

### Reports

- **`tools/vet TARGET OUT --facts` writes a facts report: what the target adds, and nothing judged.** It reads no reader's rules, makes no model call and gives no verdict, so it needs only python3. Its title reads `what it adds`, and `tools/vet --check` reads it as it reads a judged report. `--judge`, `--model`, `--units` and `--note` are usage errors with `--facts`.
- **`tools/vet --reader DIR` vets against your own rules, and every judged report names its baseline.** The header gets a `Baseline:` line (the default reader's too) with the reader folder's name, its rule file count, bytes, a fingerprint that does not depend on where the folder sits, and the list of files. The title and the verdict paragraph carry the name, with no path. A reader with no rule files gets the facts report instead, with a line saying why, and exits 0.
- **Unread notes say whose limit it is.** The report separates "neckbeard did not read" (a read cap, a file it could not open, another limit of the tool) from "broken in the plugin" (a file that does not parse, a dangling link), so a gap in neckbeard's reading no longer counts against the plugin.
- **neckbeard publishes its own facts report, with a badge.** `tools/vet --facts` ends its output with a badge line: label "neckbeard report", message "<version> · <read state>" (read in full in green, partly read in yellow, something unread in red, from the report's read states alone). `docs/neckbeard-report.md` is neckbeard's facts report on itself, and the README badge links it. `make report` regenerates it, and `make release` refuses a tag whose report names another version, read from the tagged tree. `examples/neckbeard.md` is now labelled as the demo of a fit report.

### Inventory

- **`inventory.py T --live-mcp NAME` lists what a local MCP server declares, and only that.** It starts one stdio server that the target checks in, initializes it and lists its MCP tools (with input and output schemas and annotations), resources, resource templates and prompts. It never calls an MCP tool, reads a resource, gets a prompt, opens a browser or logs in, and without the flag nothing changes. The server's entry in `mcp_servers` gains a `live` key; a refusal or a failed read (a hang, a size bound, a malformed reply) keeps its status there and adds a note naming the server to `read_status.mcp_servers`. The server runs with a temporary home and only the environment its declaration names. A remote transport, a shell, eval or module command and an entrypoint outside the target are refused, and time, bytes, pages, items and depth are bounded. What the server returns is treated as untrusted data, and a declared environment value is scrubbed from it.

## 1.16.0 (2026-11-10)

### Reports

- **A report opens with what the tool adds, written by code.** `tools/part1` reads the dossier and prints "What it adds": six cards (what it injects, its hooks, its agents and commands, state it may leave, what it reaches outside the session, its source), each saying whether the inventory found something, found nothing, read part of it, could not read it, or the card does not apply. No model writes it and it quotes none of the reader's rules. `tools/vet` puts it just before At a glance and fails if that heading is missing. The state card shows ten entries and one line counting the rest by folder. Hook commands show only their script, including the `${CLAUDE_PLUGIN_ROOT:-...}` forms Cat Herder writes, and server urls only their host.
- **The dossier says what it could not read.** `target.read_status` has an entry for each of nine sections (skills, agents, commands, rule_files, hooks, mcp_servers, persistence_candidates, plugin_json, marketplace) with a state of `read`, `partial`, `failed` or `not-applicable`, and notes naming each file left unread and why. A malformed `.mcp.json`, a dangling agent symlink, a `plugin.json` that does not parse, a script over the read cap and the other places the inventory used to drop a read in silence now each leave a note. Nothing is renamed or removed.

### Fixes

- **The inventory no longer crashes or misses files in three cases.** A hook command that is not a string and a `plugin.json` that is a list no longer crash it, and a target folder whose path contains `[` or `]` now has its skills and commands found.

### Measuring verdicts (prototypes, not used by the skill yet)

- **`tools/vet --units` computes the verdict in code from per-section answers, and confirms each conflict in a call of its own.** It numbers the target's sections, has the judge answer three questions about each, pools conflict candidates from three find passes, and counts only the ones a separate call confirms. The written conflict test (`tools/vet-conflict-test.md`) says that a sentence permitting, with no limit, an action a reader rule forbids in some cases is a conflict. Five Sonnet runs each on Cat Herder 0.40.3 and 0.53.2 gave the same verdict every time. Runs and cost: `measurements/2026-10-16-units-prototype*/` and `measurements/2026-10-16-units-confirm/`.
- **`tools/vet-stability` matches conflicts by the rule they break.** It now keys on the reader's rule file and number from either report cell, so a rule written as "#6" or ", rule 6" counts as the same finding. On five real runs over Cat Herder 0.53.2 the model-override rule now reads as found in 5 of 5, not 1 of 5. Details in `measurements/2026-10-15-vet-stability/`.

## 1.15.0 (2026-10-17)

- **A hook run through `${CLAUDE_PLUGIN_ROOT:-...}` is identified.** Cat Herder runs every hook as `"${CLAUDE_PLUGIN_ROOT:-${PLUGIN_ROOT}}/bin/meow"`, so one hook file serves several hosts, and the inventory, which expanded only `${CLAUDE_PLUGIN_ROOT}` and `$CLAUDE_PLUGIN_ROOT`, listed all three of its hooks as unidentifiable; the judge then read the hook code by hand, differently each run. The shell's default forms (`:-`, `-`, `:=`, `=`, `:?`, `?`, with a word that may hold its own `${...}`) now expand to the plugin root, since Claude Code always sets the variable. `${CLAUDE_PLUGIN_ROOT:+word}` is left alone, and so is `$CLAUDE_PLUGIN_ROOTX`, a different variable that a substring replace used to expand. Cat Herder's hooks now read as found, with their payload not traced (`unresolved_hooks`), since its script builds the text it injects at run time. Five self-check cases, each through the CLI or the call site that identifies a hook's script.
- **A guide for building a plugin neckbeard will vet, and a ledger format.** `PLUGIN-GUIDE.md` lists, for each of the sample reader's rules and each card, what neckbeard reads as a conflict and the usual way to comply, plus three patterns (a pinned agent instead of a model on the call, a hook's cost weighed before a rule is promoted into it, bounds on the actions verdicts flip on). A plugin's `neckbeard-ledger.md` records one stance per rule and card (comply, exception, open or n/a) and the files each covers. neckbeard still reports a declared exception as a conflict; a plugin's own gate can count only the undeclared ones, matched on reader rule and plugin file. neckbeard does not read the ledger yet, and `SKILL.md` is unchanged. Cat Herder 0.53.2's ledger is the worked example, in `examples/ledgers/cat-herder.md`.

## 1.14.0 (2026-10-14)

- **CONTRIBUTING.md has a "Merging several branches" section, and the layout follows it.** `CHANGELOG.md` merges by union, `make check` runs every `tools/test_*.py` instead of naming each, and `.PHONY` lists one target per line. A trial merge of six open branches conflicted only in those two files.
- **The plugin has no top-level `bin/` at all.** 1.12.9 moved `excerpts` out but kept `bin/neckbeard`, so every session still got a `neckbeard` command on its PATH, and claude.ai Chat and Cowork still refused the whole plugin, because they reject any plugin with a top-level `bin/`. `bin/neckbeard`, a wrapper that only ran `skills/neckbeard/inventory.py`, is now `tools/neckbeard` (the skill itself has called `inventory.py` from its own folder since 1.12.2). Removed: a bare `neckbeard` command is no longer on your PATH. From a clone, run `tools/neckbeard <target>`. `make check` now fails if a top-level `bin/` comes back.
- **The dossier carries the text the judge needs, so two runs judge the same thing.** Run twice on Cat Herder, neckbeard named 5 conflicts, then 2, because the dossier held only each `SKILL.md` and the judge opened the role and section files by hand, differently each time. Each skill now lists its other Markdown files, with their text, as `companion_files` (capped at 40 per skill; a file past the cap or outside the target is named, never read). A plugin whose `plugin.json` gives `hooks` as a list of files (Cat Herder's does) is now read and merged instead of reported `unknown`; a missing or outside entry still makes the answer `unknown`. Each skill also carries `user_invocable`, read from its frontmatter, so no run has to work that out by hand. `SKILL.md` is unchanged. Five self-check cases; three fail against 1.13.0, and the missing-file and outside-target cases guard the new list path.
- **The dossier flags frontmatter that strict YAML cannot read.** Claude Code loads a skill whose description has an unquoted `: ` without complaint, so the author never sees the fault, while GitHub shows "Error in user YAML" and stricter agents may drop the skill. Each skill, command and agent that has such a fault now carries `frontmatter_errors` (a line and a message), and only those do. The check is a small stdlib one, not a full YAML parser: it covers an unquoted `: ` (in a plain value, a continued one or a nested one), a value starting with `@`, a backtick, `*`, `%`, `!`, `- ` or `? `, an apostrophe inside a single-quoted value, text after a closing quote or a block header, an unclosed quote or bracket, a tab in indentation and a frontmatter fence that never closes. A trailing ` # comment` is not part of the value. A `# debt:` comment in the code names what it misses. On 70 real skill, agent and command files it agreed with PyYAML on all 70, and on a list of hand-written values it disagreed once, which was fixed (an anchor is valid). The report does not mention it yet: that needs a change to `SKILL.md` and a sealed-fixture version, which is the owner's call. Twenty self-check cases.
- **`make mutate` tests the claim that every self-check case has been seen to fail.** `tools/mutate-selfcheck` makes 452 copies of `inventory.py` with one condition deleted each, runs the self-check against every copy and lists the cases that no copy made fail; `--targeted` breaks by hand the behaviours generic mutation cannot reach (a merge order, a regex). The first run found 8 of 59 cases that never failed. One was weak: "local true overrides project false" passed with every later settings layer ignored, because its final value equalled the global one (its fixture now uses a key the global layer never sets). The other seven, "no settings anywhere" among them, fail under the hand-made sabotages. It is heavy (10 jobs, several minutes), so it is not part of `make check`.
- **`tools/vet-stability` shows how far repeated reports agree.** Give it two or more reports for one unchanged target and it prints each verdict and count line, then every conflict with how many reports found it ("found in 4 of 5"), and exits 1 when the verdicts or the conflict lists differ. A conflict is matched by the rule it collides with (the rule file and number in "held in", punctuation ignored) and, when the "it says" cell names one, the file it comes from, never by wording, since the judge words one finding differently each run. Two findings from one file against one rule count as one, and the output says so. It needs only python3, so it costs no model run. `tools/vet-repeat TARGET OUTDIR N` runs `tools/vet` N times and then this (each run is a real judge session). This is the measuring half of `verdict-stability`; the measured runs and the judge changes follow.
- **A single rules file reads only itself.** Pointed at one file, neckbeard used to follow its `@path` lines and read the files they named, so a downloaded `rules.md` could pull its neighbours into the dossier. Now only a file named `CLAUDE.md` follows imports, as Claude Code does, and still only inside its own folder; any other file lists the names it gives under `imports_not_followed` and reads none of them. A binary or unreadable file is refused with an error instead of producing an empty dossier.

## 1.13.0 (2026-10-06)

- **`tools/vet` runs the whole gallery method in one command**, so a plugin can rebuild its published report, for example in a Claude Code web session on its own repo (see `examples/README.md`). It vets against a throwaway copy of the sample reader, because the judge writes its backups and synced skills into its config folder; it lets the judge edit its own report, so it can fix a count it got wrong; and it refuses a report with no verdict or with a local path in it. It writes the title line itself, since a judge was seen to write "vetted against your rules". `tools/vet --check REPORT TARGET` is the matching CI check: it needs only python3 and fails when the report vets a different version than the plugin's `plugin.json`. `tools/test_vet.py` runs both against a fake `claude`, and `make check` runs that.

## 1.12.9 (2026-10-02)

- **`make deploy`, as Cat Herder has it.** It refuses unless `main` is released on every remote, then brings this machine and each host in `HOSTS` to that commit: a directory marketplace's checkout must be clean and is fast-forwarded to exactly the release, the marketplace is updated, every install of neckbeard is updated from its own folder, and each one's version is printed and checked. `tools/test_deploy.py` runs it end to end against a fake `claude`, and `make check` runs that.
- **`excerpts` is no longer on your PATH.** A plugin's top-level `bin/` is on the PATH of every session's Bash tool, so every neckbeard user had our maintainer script as a command. It now lives in `tools/`. `bin/` kept `neckbeard`, which a later release also moved out (see Unreleased).
- **`make release` pushes to a fixed list**, `origin` plus the `MIRRORS` a git-ignored `local.mk` names, never every remote the checkout happens to have. Before, a checkout with a work-queue remote would have pushed `main` and the tag into the queue.

## 1.12.8 (2026-10-01)

- **neckbeard shows its own badge.** The README carries a neckbeard badge linked to its report on itself, rerun against the sample reader on 1.12.7: 🟩 install, no conflicts, in three separate runs. The 1.12.0 report's one conflict, its symbol key against "plain language over jargon", did not come back; the gallery says so rather than claiming a fix.
- **`make release` also publishes the GitHub Release**, with that version's changelog entry as its notes, and refuses to push anything if the entry is missing. A pushed tag alone left the repo page showing the previous version as Latest. `make release-notes` prints what the notes will say.
- **An issue form for ideas.** With blank issues off, a bug report was the only public way in. The bug form's version field now shows a generic `x.y.z` instead of a version that goes stale.

## 1.12.7 (2026-09-28)

- **The hook search reads the whole tree, and says so when it cannot.** An independent review after 1.12.6 shipped found that its new search for hook-shaped JSON stopped four directory levels down and reported `has_hooks: false` for hooks below that, which is the silence 1.12.6 set out to remove. There is no depth limit now; a budget of 20,000 JSON reads bounds the walk (the largest of 128 local repos read 5,378 in about 3 seconds, with no false alarms), and running out says where it stopped: `unknown` if nothing was found by then, and the hooks found so far with a `search_incomplete` note if something was. A `marketplace.json` that is not valid JSON, or that was refused, now says so in the dossier instead of reading as a marketplace that lists nothing. Four self-check cases: the first and last fail against 1.12.6, and the partial-result case was added after a second review round found that gap; see `CASE-STUDIES.md` §15.

## 1.12.6 (2026-09-28)

- **Hooks that no root manifest names are found.** Run on four pstack ports, the inventory called three of them hookless: two are marketplaces whose plugin lives in `plugins/pstack/`, and one merges ten hook groups from `install.json` into `~/.claude/settings.json` with an installer. A marketplace's local plugin is now what gets inventoried (`--plugin NAME` picks one of several), hook-shaped JSON anywhere in the tree is reported along with the scripts that write `settings.json`, and a marketplace or folder of plugins that was not inventoried plugin by plugin says `unknown`, never `false`. Ten self-check cases; see `CASE-STUDIES.md` §15.

## 1.12.5 (2026-09-25)

- **The case studies read in half the time.** They open with a short link list in two groups: runs against real plugins, and rounds against neckbeard itself. Each run against a gallery plugin (§1 to §5) leads with that plugin's report today, then the first run's output. Every round then lists what it showed, the version that fixed it, and the self-check that guards it, and says so where none does. Lists longer than four show three and fold the rest; §9 and §12 keep their full stories in a fold; the closing lessons are five, with twelve more folded and numbered on from them.
- **The report excerpts are copied, never typed.** `bin/excerpts` (now `tools/excerpts`) fills them from `examples/`, and `make check` fails if a case study quotes a report that has since changed.
- **The README reads in the order an evaluator asks.** What it produces, then how to install and use it, then how it was tested and what it will and will not touch, then the story behind it. A line under the intro says every round is published, and "How it was tested" links each round. It also said the gallery has seven plugins; it has eight.

## 1.12.4 (2026-09-25)

- **The README's "Why" now says what happened.** It used to say the author read ponytail himself and found half its rules duplicated and five in conflict. An LLM made that comparison, and there was no good way to check it, which is the reason neckbeard exists. The tagline changes too, and the social preview image matches it.

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
