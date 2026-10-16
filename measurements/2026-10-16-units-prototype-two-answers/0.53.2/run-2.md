# 🔍 ch-v0532 0.53.2 · vetted against the sample reader

> ## 🟧 INSTALL WITH CHANGES · keep the workflow skills, drop four lines that pick a model for subagents
> Cat Herder is a git-backed work queue with its own `meow` command, and 42 of its 64 instruction sections work as shipped and do things the reader's rules do not. Four sections tell the model to dispatch subagents on a named model, which the reader's rule 6 forbids. Three general rules and one audit procedure are worth copying as text whatever you decide about the plugin.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-15` · neckbeard 1.14.0 · ch-v0532 0.53.2

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟨 | **Cost** | Three hooks, no bytes measured by the inventory (all three were unidentifiable, so I read `lib/cat_herder/hooks.py`). SessionStart prints a few lines of role, compaction count and the repo's queue rules, only in a repo that has a queue; nothing in a repo without one. SessionEnd and PreCompact print nothing. |
| 🟩 | **Reach** | Main session only. No hook event fires inside a subagent (certain for the three registered events). |
| 🟨 | **Leaves state** | SessionEnd writes an `ended` file in the machine's state directory. PreCompact commits a compaction count to the queue's roster, and only for a session already on that roster. |
| 🟨 | **Live surface** | PreCompact runs `git fetch` and `git push` against the queue remote (ssh, git or https, 15 second deadline). It ships a `meow` command, 12 slash commands and tools under `tools/`. No MCP servers. |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 42 skill sections, 3 standing rules, 1 on-demand procedure |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **4** | 🟥🟥🟥🟥 |
| 🔁 | **already covered** | **1** | ⬜ |
| 🆕 | **new, standing rule** | **3** | 🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **1** | 🟩 |
| 🟩 | **skill sections kept** | **42** | 🟩 ×42 |
| 🗑️ | **dropped** (persona, wrappers, no value) | **22** | ⬛ ×22 |

The 64 units are 64 sections of 4 skills, their role and section files, and 12 commands. Each has a skill answer (kept 42, dropped 22) and a rules answer (4 conflict, 3 new standing, 1 new skill, 1 covered, 55 nothing general). The grids below list a unit once in its rules grid, and every kept unit again under Keep.

## ⛔ Conflicts: 4
| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| 1 | `skills/herd/roles/orchestrator.md` · The orchestrator: "send 3 or 4 new read-only subagents on `claude-haiku-5-5`, one lens each" | "Do not override it on the dispatch call" (rule 6): subagents run on the model their definition pins | `examples/reader/rules/engineering.md` | 🟥 |
| 2 | `skills/herd/roles/reviewer.md` · Each review: "you may send your own swarm of read-only `claude-haiku-5-5` subagents at it" | "Do not override it on the dispatch call" (rule 6): subagents run on the model their definition pins | `examples/reader/rules/engineering.md` | 🟥 |
| 3 | `skills/herd/roles/worker.md` · The worker, in a pair: "Send 3 or 4 subagents on `claude-haiku-5-5`, one lens each (and again for the pre-check and the wording swarm)" | "Do not override it on the dispatch call" (rule 6): subagents run on the model their definition pins | `examples/reader/rules/engineering.md` | 🟥 |
| 4 | `skills/queue/SKILL.md` · Working the queue: "Hand the rest out in batches of about 8 to agents on the cheapest capable model your host offers" | "Do not override it on the dispatch call" (rule 6): subagents run on the model their definition pins | `examples/reader/rules/engineering.md` | 🟥 |

The reader's rule governs a subagent dispatch call. The sections above dispatch subagents too, so both apply. Sessions the plugin starts (`meow herd pair start` starting a reviewer on opus, `claude-fable-5-1` for an advisor thread) are separate sessions, not dispatch calls, and I did not count them.

## 🔁 Already covered: 1
| its rule | covered by | held in |
|---|---|---|
| `skills/herd/roles/reviewer.md` · When the item says rigor: build: revert the change and watch the test fail; cite a `file:line` for every accepted claim | rule 3, "A test is not done until it has been seen to fail"; chosen over the answers rule in `examples/reader/CLAUDE.md` because rule 3 states the revert check as a rule in its own right | `examples/reader/rules/engineering.md` |

## 🟩 Rules to copy: 4
| # | unit | rule or skill | kind | |
|:--:|---|---|:--:|:--:|
| 1 | `skills/herd/roles/auditor.md` · Hard rules | "never `pkill` or `killall` by pattern: you could stop another auditor's run. Stop a process by the pid you started." | standing | 🟩 |
| 2 | `skills/herd/roles/reviewer.md` · (top) | "If a git fetch or push fails on authentication, stop and report the remote and the error. Never add a key, a token, an https remote or a forwarded agent to get past it." | standing | 🟩 |
| 3 | `skills/herd/roles/worker.md` · When the item says rigor: build | "Never paraphrase evidence" (paste each command, its exit code and bounded raw output), and "Stop only the processes you started, by their PID, never by port." | standing | 🟩 |
| 4 | `skills/herd/roles/auditor.md` · Method | List every checkable claim in a doc, run each example in a scratch repo, break the code the claim depends on, and give each claim one of BACKED, UNTESTED, CONTRADICTED or UNTESTABLE | on-demand skill | 🟩 |

## 🟩 Keep: 42
Skill sections that work as shipped and do something the reader's rules and skill (`examples/reader/skills/release-notes/SKILL.md`) do not. All need the plugin's own `meow` command, which is not a reason to drop them.

| # | skill section | kind | |
|:--:|---|:--:|:--:|
| 1 | `skills/capture/SKILL.md` · Capture | skill | 🟩 |
| 2 | `skills/capture/SKILL.md` · An interruption, so keep it short | skill | 🟩 |
| 3 | `skills/capture/SKILL.md` · Asked to do work yourself: every session, not only the worker | skill | 🟩 |
| 4 | `skills/capture/SKILL.md` · Rescue session: everything this session was tracking | skill | 🟩 |
| 5 | `skills/capture/SKILL.md` · Stream-of-consciousness: the owner is riffing | skill | 🟩 |
| 6 | `skills/capture/SKILL.md` · Prompt me: answering the open questions with a tap | skill | 🟩 |
| 7 | `skills/capture/sections/prompt-me.md` · Prompt me: answering the open questions with a tap (the rest) | section | 🟩 |
| 8 | `skills/herd/SKILL.md` · Herd | skill | 🟩 |
| 9 | `skills/herd/roles/associate.md` · The associate | role | 🟩 |
| 10 | `skills/herd/roles/auditor.md` · The auditor | role | 🟩 |
| 11 | `skills/herd/roles/auditor.md` · Method | role | 🟩 |
| 12 | `skills/herd/roles/auditor.md` · Findings | role | 🟩 |
| 13 | `skills/herd/roles/auditor.md` · Hard rules | role | 🟩 |
| 14 | `skills/herd/roles/auditor.md` · Prompt hygiene | role | 🟩 |
| 15 | `skills/herd/roles/auditor.md` · Report | role | 🟩 |
| 16 | `skills/herd/roles/auditor.md` · The coordinator's checklist | role | 🟩 |
| 17 | `skills/herd/roles/auditor.md` · A falsify item | role | 🟩 |
| 18 | `skills/herd/roles/bond.md` · A bond: you and {{WORKER_NAME}} review each other | role | 🟩 |
| 19 | `skills/herd/roles/handoff.md` · Handing off to a new session | role | 🟩 |
| 20 | `skills/herd/roles/handoff.md` · If you're retiring | role | 🟩 |
| 21 | `skills/herd/roles/handoff.md` · If you're the one that stays | role | 🟩 |
| 22 | `skills/herd/roles/handoff.md` · If you're the new session | role | 🟩 |
| 23 | `skills/herd/roles/handoff.md` · In chat | role | 🟩 |
| 24 | `skills/herd/roles/orchestrator.md` · The orchestrator | role | 🟩 |
| 25 | `skills/herd/roles/readonly.md` · The reply of a session that can't write | role | 🟩 |
| 26 | `skills/herd/roles/reviewer.md` · (top) | role | 🟩 |
| 27 | `skills/herd/roles/reviewer.md` · Setting up (once, when this pair starts) | role | 🟩 |
| 28 | `skills/herd/roles/reviewer.md` · Each review | role | 🟩 |
| 29 | `skills/herd/roles/reviewer.md` · Limits | role | 🟩 |
| 30 | `skills/herd/roles/reviewer.md` · Who started you, and stopping | role | 🟩 |
| 31 | `skills/herd/roles/reviewer.md` · When the item says rigor: build | role | 🟩 |
| 32 | `skills/herd/roles/worker.md` · The worker, in a pair | role | 🟩 |
| 33 | `skills/herd/roles/worker.md` · When the item says rigor: build | role | 🟩 |
| 34 | `skills/herd/sections/launch-refused.md` · A launch is refused | section | 🟩 |
| 35 | `skills/herd/sections/orchestrator.md` · The orchestrator at a run's end, and in cloud runs | section | 🟩 |
| 36 | `skills/queue/SKILL.md` · The queue | skill | 🟩 |
| 37 | `skills/queue/SKILL.md` · Working the queue | skill | 🟩 |
| 38 | `skills/queue/SKILL.md` · Telling the owner what another session said | skill | 🟩 |
| 39 | `skills/queue/SKILL.md` · Staying reasonable | skill | 🟩 |
| 40 | `skills/queue/sections/asks.md` · Asking the owner to do something | section | 🟩 |
| 41 | `skills/queue/sections/field-trip.md` · Field Trip, and reading the owner as voice | section | 🟩 |
| 42 | `skills/queue/sections/setup.md` · Setting up a queue | section | 🟩 |

## 🗑️ Dropped
Cat voice and persona text, one example line, and 12 slash commands that only wrap a skill or a `meow` call judged above.

`u36` · `u37` · `u38` · `u39` · `u40` · `u41` · `u42` · `u43` · `u44` · `u48` · `u53` · `u54` · `u55` · `u56` · `u57` · `u58` · `u59` · `u60` · `u61` · `u62` · `u63` · `u64`

`u36` to `u44` are `skills/herder/SKILL.md`. `u48` is an example ledger line in `skills/queue/SKILL.md`. `u53` to `u64` are the files under `commands/`.

## 🧩 What it installs
| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| SessionStart hook (`hooks/claude-codex.json`) | startup, resume, compact; prints text only in a repo with a queue | no | not measured, a few lines |
| PreCompact hook (`hooks/claude-codex.json`) | automatic compaction; one queue commit for a rostered session | no | no output |
| SessionEnd hook (`hooks/claude.json`) | session close; writes a local `ended` file | no | no output |
| 4 skills (capture, herd, herder, queue) | on demand, by trigger words | no | 76,054 characters |
| 12 commands | when typed | no | 5,051 characters |

`hooks/cursor.json` and `hooks/antigravity.json` serve other hosts and do not load in Claude Code.

## ✅ Do this
- ⬜ 1. Install it only for repos that run a Cat Herder queue; the hooks say nothing elsewhere.
- ⬜ 2. Before relying on the swarm steps, strip the model names from the four conflicting sections, or change the reader's rule 6 on purpose. Both choices are yours; I changed neither.
- ⬜ 3. Copy the three standing rules below into the reader's engineering rules.
- ⬜ 4. Decide whether the audit method is worth a small skill of its own.

First carrying-cost case: the hooks run at session start and compaction, but only in the main session and only where a queue exists. The kept sections are the plugin's own workflow skills, which the owner's rule keeps whenever they work as shipped, so the cost is the price of the queue itself.

## 📋 Proposed rules patch
Add to `examples/reader/rules/engineering.md`, after rule 7, in its numbered style:

```diff
+8. **Stop only what you started.** Kill a process by the pid you launched, never by
+   name pattern or port.
+9. **Evidence is pasted, not paraphrased.** Report each check as the command, its
+   exit code and bounded raw output.
```

Add to `examples/reader/rules/safety.md`, after rule 5:

```diff
+6. **If a git fetch or push fails on authentication, stop and report.** Never add a key,
+   token, https remote or forwarded agent to get past it.
```

Proposed on-demand skill (the name is my proposal, and the reader's skill folder is `examples/reader/skills/`): `audit-doc-claims`, "Check a document claim by claim: run each example, break the code behind it, and mark each claim BACKED, UNTESTED, CONTRADICTED or UNTESTABLE."

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
