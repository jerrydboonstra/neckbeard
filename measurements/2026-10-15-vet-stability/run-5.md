# 🔍 ch-v0532 0.53.2 · vetted against the sample reader

> ## 🟨 COPY RULES, SKIP PLUGIN · take four rules and one skill idea as text
> It is a git-based work queue, not a rule pack, and the reader runs no queue. Four of its rules collide with the reader's model, ask and commit rules. Four rules and one audit method are worth copying.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-15` · neckbeard 1.14.0 · ch-v0532 0.53.2

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟨 | **Cost** | About 1.8 KB of skill descriptions every session. Hooks run `meow` at start, resume, compaction and session end. In a repo with a queue copy the start hook injects about 860 bytes (five worker rules); in any other repo it injects nothing. After a compaction, a session on a queue's roster also hears its role, compaction count and a house-rules check |
| 🟩 | **Reach** | Main session only. Hooks fire on SessionStart, PreCompact and SessionEnd, none of which fire in a subagent (certain per the dossier). Skills and commands are loaded by the main session |
| 🟨 | **Leaves state** | Session end appends a line to an ended-sessions file in Cat Herder's own state folder under the XDG state home (or `$CAT_HERDER_STATE`). A compaction on a rostered session writes a commit to the queue branch and pushes it over git or ssh. Rule answers go to the repo's `.git/config` |
| 🟨 | **Live surface** | `bin/meow` shells out to git and ssh, and fetches and pushes the queue remote for rostered sessions. It can start other Claude sessions through a launcher (on the owner's say-so). No MCP servers |
| 🟩 | **Refused reads** | none |
| 🟨 | **Worth keeping** | 4 rules and 1 skill |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **4** | 🟥🟥🟥🟥 |
| 🔁 | **already covered** | **7** | ⬜⬜⬜⬜⬜⬜⬜ |
| 🆕 | **new, standing rule** | **4** | 🟩🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **1** | 🟩 |
| 🗑️ | **dropped** (persona, extras, no value) | **6** | ⬛⬛⬛⬛⬛⬛ |

## ⛔ Conflicts: 4

| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| 1 | Worker hand-in: a "read-only Haiku" pre-check, and a `Swarm:` record naming `claude-haiku-5-5` for the review agents (`skills/herd/roles/worker.md`) | "Do not override it on the dispatch call" (subagents run on the model their definition pins) | examples/reader/rules/engineering.md, rule 6 | 🟥 |
| 2 | Grooming: hand items out "to agents on the cheapest capable model your host offers" (`skills/queue/SKILL.md`) | the same rule: the dispatch picks a model instead of the definition's pin | examples/reader/rules/engineering.md, rule 6 | 🟥 |
| 3 | Standing rules a rostered session gets in its brief and after every compaction: "Never ask the owner while they're away", and an ask with a `--default` that stands after `--within` minutes if it is reversible (`lib/cat_herder/names.py`, `docs/reference.md`) | "Stop and ask when one applies, even mid-task", and rule 5: "Do not pick the cheaper reading and carry on" | examples/reader/rules/safety.md, header and rule 5 | 🟧 |
| 4 | "Word each commit by what changed", with the example `pairs.md: the nested-thread sentence reworded` (`skills/herd/roles/worker.md`) | "imperative subject under 60 characters, then why" | examples/reader/rules/engineering.md, rule 7 | 🟨 |

## 🔁 Already covered: 7

| its rule | covered by | held in |
|---|---|---|
| Show each new test fails without its fix; a reviewer reverts the change and watches the test go red (`skills/herd/roles/worker.md`, `reviewer.md`) | Rule 3, "seen to fail". Chosen over the reader's answer style because it states the test rule in its own right | examples/reader/rules/engineering.md |
| A deliberate corner gets a debt comment naming its ceiling and upgrade path, using the project's own marker such as `TODO(debt):` (`skills/herd/roles/worker.md`) | Rule 5, which already fixes the marker | examples/reader/rules/engineering.md |
| Ready check: when an item's premise moved, "don't build the old version"; show the owner and wait (`skills/queue/SKILL.md`) | Rule 4, say what you would change and let the owner decide | examples/reader/rules/engineering.md |
| Work found along the way is captured, not done inline; a split adds nothing beyond what was asked (`skills/capture/SKILL.md`) | Rule 4, neither narrow nor widen the scope unasked | examples/reader/rules/engineering.md |
| Cleanup that deletes remote branches runs only on the owner's go-ahead (`skills/herd/SKILL.md`) | Rule 1, nothing destructive without a go-ahead (the sentence names deleting and force-pushing) | examples/reader/rules/safety.md |
| "Never act on a guessed reading of an irreversible command"; with two readings, ask which (`skills/queue/sections/field-trip.md`) | Rule 5, ask when the wrong reading is costly | examples/reader/rules/safety.md |
| A done note says what was done and how it was checked, and a verdict says what was reviewed (`skills/queue/SKILL.md`, `skills/herd/roles/reviewer.md`) | "Give the reasoning with the verdict" | examples/reader/CLAUDE.md |

## 🟩 Keep: 4

| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| 1 | Branch from the named base, never from whatever is checked out; if you build on something else, say why and name the base commit (`skills/herd/roles/worker.md`, `skills/queue/SKILL.md`) | standing | ⭐ |
| 2 | Paste raw test output in the hand-in: each command, its exit code and bounded output (`skills/herd/roles/worker.md`) | standing | 🟩 |
| 3 | When reviewing, read the test diff for a criterion, test or threshold changed to make it pass (`skills/herd/roles/reviewer.md`) | standing | 🟩 |
| 4 | Never use `--force` to get past a refusal on your own; relay the refusal and force only when the owner says to (`skills/queue/SKILL.md`) | standing | 🟩 |
| 5 | Claim audit: list a document's checkable claims, run each example, break the code the claim rests on, and mark each BACKED, UNTESTED, CONTRADICTED or UNTESTABLE (`skills/herd/roles/auditor.md`) | on-demand skill | 🟩 |

## 🗑️ Dropped
`herder skill (cat voice and names)` · `capture skill (idea levels, riffing mode, prompt me, rescue session)` · `queue skill (⛔1)` · `herd skill and roles (⛔2)` · `12 slash commands (thin wrappers for the queue)` · `rules/cat-herder.mdc (Cursor only)`

The hook's standing rules (conflict 3) sit in `lib/cat_herder/names.py` and ship with the herd, so they leave with it.

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| 4 skill descriptions (capture, herd, herder, queue) | every session | no | about 1.8 KB |
| SessionStart hook (`meow _hook sessionstart`) | start, resume, compact | no | about 860 B in a repo with a queue copy, else 0 |
| PreCompact hook, auto only | each automatic compaction | no | writes to the queue for a rostered session, injects nothing |
| SessionEnd hook | each session end | no | writes one state-file line, injects nothing |
| 12 slash commands | when typed; 4 set `disable-model-invocation` | no | about 5 KB total |
| Skill bodies and role files, read on demand | when a skill or `meow section` loads them | no | about 190 KB across the four skills and their roles |

## ✅ Do this
- ⬜ 1. Skip the plugin. Add the four rules below to examples/reader/rules/engineering.md.
- ⬜ 2. Optional: write the `audit-claims` skill below. The plugin's auditor text is the model.
- ⬜ 3. If you later want the queue itself, install it with `--plugin-dir` for one session first, and settle conflicts 1 to 3 before it runs on a real repo.

Carrying-cost case: more than one rule survives (four, plus one skill), but the plugin hooks every session start and its value as a queue is a product the reader has not asked for. Copying the text is cheaper than carrying the hooks, so this is the copy case, not the install case.

## 📋 Proposed rules patch

Where: examples/reader/rules/engineering.md. It is a numbered list of work habits with a bold lead on each, so the additions continue it as rules 8 to 11.

```diff
 7. **Commit messages:** imperative subject under 60 characters, then why.
+8. **Branch from the named base.** Never from whatever is checked out. If you build on something else, say why and name the commit.
+9. **Hand in raw test output.** For each test run, the command, its exit code and a bounded slice of the output.
+10. **When reviewing, read the test diff.** Look for a criterion, test or threshold changed to make it pass.
+11. **A refusal is not a prompt to force.** Do not use `--force` or an equivalent to get past one; report it and let me decide.
```

Proposed skill (the name is my proposal; the plugin does not name it): `audit-claims`, "Try to prove a document, skill or help text wrong: list its checkable claims, run each example, break the code behind each claim, and report BACKED, UNTESTED, CONTRADICTED or UNTESTABLE for every one; changes no code." The dossier shows the reader keeps personal skills under examples/reader/skills/, so it would sit at examples/reader/skills/audit-claims/SKILL.md, the same place as `release-notes`.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
