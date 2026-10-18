# Building a plugin neckbeard will vet

For people who build a Claude Code plugin and want its neckbeard report to come out the way they intend. It lists what neckbeard looks for under each rule of the [sample reader](examples/reader/) and on each card of the report's "At a glance" grid, and the usual way to comply. It also defines a **ledger**: a file in the plugin's repo that records, rule by rule, how far the plugin means to comply.

Nothing here is required. neckbeard vets any plugin the same way, ledger or not. A plugin's own workflow can load this guide when it works on a repo that keeps a ledger, and leave it out everywhere else.

## How a vet reads your plugin

neckbeard's inventory lists everything the plugin carries: skills, commands, agents, rule files, hooks and what each hook injects. The judge then sorts every rule the plugin carries against the reader's rules, as a duplicate, a conflict, or new. Two things follow:

- **Your text is read as instructions.** An example in a skill (a sample commit message, a sample command) is read the way a model would read it, as something to copy. An example can break a rule too.
- **The judge varies from run to run.** The same text can be read as a conflict in one run and not the next. Text that states its bounds ("ask before X", "only on the owner's word") gives the judge fewer ways to read it than text that only states an action ("act first", "do it either way").

## The ledger

A file named `neckbeard-ledger.md`, at the repo root or in `docs/`. Its header names the reader it was written against and the plugin version. Then one table, with one row for every reader rule and every card.

```markdown
# neckbeard ledger

reader: neckbeard v1.14.0, examples/reader
target: my-plugin 2.3.0

| rule | stance | files | where it shows, or why | agreed |
|---|---|---|---|---|
| engineering 6 | comply | `agents/reviewer.md` | pins `model: haiku`; skills send it by name | |
| safety 2 | exception | `Makefile` | `make release` pushes main after its checks pass; the release is the point | owner, 2026-10-15 |
| cost | open | `hooks/hooks.json` | SessionStart now fires on every start; narrowing it is queued (item hook-narrow) | owner, 2026-10-15 |
| release-notes | n/a | | the plugin writes no release notes | |
```

**Rule names.** Each name stands for a reader file and, where it has one, a rule number, which is how a report's conflicts table names them in its "held in" cell:

| ledger name | reader file | rule |
|---|---|---|
| `engineering 1` to `engineering 7` | [`examples/reader/rules/engineering.md`](examples/reader/rules/engineering.md) | 1 to 7 |
| `safety 1` to `safety 5` | [`examples/reader/rules/safety.md`](examples/reader/rules/safety.md) | 1 to 5 |
| `answers` | [`examples/reader/CLAUDE.md`](examples/reader/CLAUDE.md), "How I like answers" | none |
| `release-notes` | [`examples/reader/skills/release-notes/SKILL.md`](examples/reader/skills/release-notes/SKILL.md) | none |

The cards are `cost`, `reach`, `leaves state`, `live surface` and `refused reads`. "Worth keeping" is not a compliance matter and has no row.

**Stances.**

- **comply**: the plugin keeps the rule. Say where that shows, so a reviewer can check it.
- **exception**: the plugin breaks the rule on purpose. Name the files it breaks it in, give the reason, and in `agreed` write who agreed and the date (`owner, 2026-10-15`).
- **open**: a fix is planned, because the plugin breaks the rule today or reads close enough that a run may count a conflict. Name the files and the fix.
- **n/a**: the rule has nothing to act on in this plugin.

**Cells.** Keep `|` out of a cell, even inside backticks, so a script can split a row on it. Write a hook matcher such as `startup|resume|compact` as "startup, resume and compact".

**What counts.** neckbeard still reports a declared exception as a conflict, since the reader's rule is broken either way. A plugin's own gate (a release check, a minimum verdict) can count only the undeclared ones. Read the whole row of the report's conflicts table, not one cell: neckbeard words the row differently from run to run. "held in" usually names only the reader file, the rule number may sit in "collides with" ("rule 6", "#6"), and the plugin's file sits in "it says", when the row names one at all. A reported conflict is declared when its row names the reader file of a row marked `exception` and, where that file numbers its rules, the rule number; names at least one plugin file; and every plugin file it names is in that row's `files`. A conflict that names no plugin file, or no rule number for a numbered rule, is not declared. That errs toward counting: an exception can't cover a passage nobody agreed to, at the price of some declared conflicts counting anyway until neckbeard gives the report a fixed place for each. Every other conflict counts, `open` rows included. A gate should also fail on a missing row and on a stance that isn't one of the four words, since a missing row means undecided, not fine. A card row records the stance only. Cards don't yet have written colour rules, so a gate can't hold a card to its row.

**Today, neckbeard does not read the ledger.** Matching the report's conflicts to the ledger is the plugin's gate's job. A later neckbeard may read the ledger and mark declared conflicts in the report itself.

**When to change it.** Change a row in a reviewed commit, as you would change a rule. When the reader or neckbeard version moves, update the header and check each row again.

## The rules

What neckbeard looks for under each rule, and how plugins usually comply.

| rule | what reads as a conflict | the usual way to comply |
|---|---|---|
| engineering 1, reuse first | an instruction to write new code or add a dependency without checking what exists | rarely conflicts; a plugin that says "reuse the repo, then the standard library" is a duplicate, not a conflict |
| engineering 2, fix the cause | "patch the failing path", with no step to find every caller | ask for the callers before the change |
| engineering 3, tests seen to fail | test-writing steps that end at "tests pass" | require breaking the guarded code once and watching the test go red |
| engineering 4, scope is the deliverable | "act first, report after", "do it either way", "fix anything else you notice" | state the bounds: what it may do unasked, and what it proposes and waits on |
| engineering 5, mark debt | an instruction to leave shortcuts unmarked, or to use only its own marker | a marker of its own is fine when it defers to the project's (`TODO(debt):` here) |
| engineering 6, pinned models | a model named when sending a subagent: `model:` on the Agent call, or "send three agents on haiku" | ship `agents/<name>.md` with `model:` in its frontmatter and send it by name; see the patterns below |
| engineering 7, commit messages | a sample subject that is not imperative, runs over 60 characters, or has no why | make every sample a good commit: "Reword the nested-thread sentence", then a line on why |
| safety 1, destructive steps | `rm -rf`, force-push, branch or file cleanup with no go-ahead step | a dry run first, then the action only on an explicit yes in the conversation |
| safety 2, never push to main | tooling or steps that push to `main` or merge a pull request | keep work on branches and stop at the pull request; a release step that must push `main` is an exception to declare |
| safety 3, deploy on "ship it" | a deploy that runs on its own once checks pass | prepare the deploy and stop; run it only on the user's word |
| safety 4, no secrets in output | steps that print, log or commit tokens, or fixtures holding real credentials | redact by default and say so; fake values in fixtures |
| safety 5, ask when it's costly | "when unclear, pick the likelier reading and carry on" | a reversible default is fine; anything irreversible waits for an answer |
| answers | verdicts with no account of what was checked | every review says what it checked and what it didn't |
| release-notes | almost never conflicts; a release-notes skill of the plugin's own may duplicate it | n/a for most plugins |

## The cards

| card | what it measures | the usual way to pass it |
|---|---|---|
| cost | bytes in every session: skill and command descriptions, and what each SessionStart hook injects | short descriptions; a SessionStart matcher as narrow as the job (compact alone, rather than startup, resume and compact); load long text on demand |
| reach | whether the plugin's hooks fire inside subagents: certainly for SubagentStart, SubagentStop, PreToolUse and PostToolUse, likely for PostToolUseFailure, Stop and PermissionRequest | hook those events only when the job needs it inside subagents |
| leaves state | files written outside the project | write inside the project, or name each file and what removes it |
| live surface | MCP servers, network access, and commands its hooks and skills run | name each; keep hook commands local and bounded by a timeout |
| refused reads | any path that leaves the plugin's tree, through a symlink or `../` | none; any refusal fails the card |

**Write hook commands the inventory can follow.** Use `${CLAUDE_PLUGIN_ROOT}/path/to/script`. neckbeard 1.14.0 and earlier don't follow the shell's default forms, such as `${CLAUDE_PLUGIN_ROOT:-${PLUGIN_ROOT}}`; the next release does. A command the inventory can't tie to a file lands in `unidentifiable_hooks`, and the judge then has to read your scripts itself. A script whose output is built at run time lands in `unresolved_hooks`: found, but what it injects is not traced.

## Patterns

- **A pinned agent instead of a model on the call.** Engineering 6 is about where the model is chosen. Ship the agent definition with its model, tools and instructions, and have the skill send it by name. The same file is a good home for a fixed review rubric: two reviewers that share one definition share one rubric, rather than retyping it into each brief. Agent files load in Claude Code only, so a plugin that also runs on other hosts still names a model there; its row says which hosts comply.
- **Weigh a hook's cost before you promote a rule into one.** A rule agents keep missing is tempting to enforce with a hook. A hook raises cost, and a hook that fires inside subagents raises reach. Make that a ledger decision, with the card it moves in mind.
- **Bound the actions the judge varies on.** The passages that flip from run to run are usually bare imperatives to act. Saying what the action may touch, and when it waits for a yes, is the first edit to try.

## A worked example

[`examples/ledgers/cat-herder.md`](examples/ledgers/cat-herder.md) is Cat Herder's first ledger, written against Cat Herder 0.53.2.
