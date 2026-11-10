`2026-10-15` · neckbeard 1.14.0 · ch-v0532 0.53.2

# 🔍 ch-v0532 0.53.2 · vetted against the sample reader

> ## 🟧 INSTALL WITH CHANGES · keep the skills, take out the model names on subagent dispatch
> The plugin is a queue and review workflow driven by its own `meow` command. It works as shipped, and its hooks reach the main session only. Four sections tell the model to send subagents on a named model, which the reader forbids, and eight sections hold rules worth copying.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟨 | **Cost** | Three hooks run `meow _hook`: at session start a few lines (roster role, plus the repo's queue rules and recorded answers, only in a repo with a queue), and after a compaction the compaction count. Bytes not measured: the dossier could not resolve the hook command, so I read `lib/cat_herder/hooks.py` in the plugin. |
| 🟩 | **Reach** | Main session only (no hooked event fires in a subagent) |
| 🟨 | **Leaves state** | PreCompact writes the compaction count to the session's roster record in the queue, SessionEnd records the close in the machine's state folder, and queue commands commit and push to git |
| 🟨 | **Live surface** | The `meow` CLI, git fetch and push, ssh and tmux for session launchers; no MCP servers |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 43 skill sections, 8 rules |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **4** | 🟥🟥🟥🟥 |
| 🔁 | **already covered** | **2** | ⬜⬜ |
| 🆕 | **new, standing rule** | **7** | 🟩🟩🟩🟩🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **1** | 🟩 |
| 🗑️ | **dropped** (persona, wrappers) | **21** | ▰ ×21 |
| 🟩 | **skill sections kept** (a unit can also be a conflict or a rule to copy) | **43** | ▰ ×43 |

Units with no general rule at all: 50 of 64.

## ⛔ Conflicts: 4

| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| 1 | "send 3 or 4 new read-only subagents on `claude-haiku-5-5`" | examples/reader/rules/engineering.md rule 6: "Do not override it on the dispatch call." | `skills/herd/roles/orchestrator.md` · The orchestrator | 🟥 |
| 2 | "send your own swarm of read-only `claude-haiku-5-5` subagents" | examples/reader/rules/engineering.md rule 6: "Do not override it on the dispatch call." | `skills/herd/roles/reviewer.md` · Each review | 🟥 |
| 3 | "Send 3 or 4 subagents on `claude-haiku-5-5`, one lens each" | examples/reader/rules/engineering.md rule 6: "Do not override it on the dispatch call." | `skills/herd/roles/worker.md` · The worker, in a pair | 🟥 |
| 4 | "agents on the cheapest capable model your host offers" | examples/reader/rules/engineering.md rule 6: "Do not override it on the dispatch call." | `skills/queue/SKILL.md` · Working the queue | 🟥 |

Both sides govern subagent dispatch, so they collide. Sessions the plugin starts (`--model` on a pair or handoff, the Fable advisor thread in the orchestrator section) are not subagent dispatches, so they are not counted.

## 🔁 Already covered: 2

| its rule | covered by | held in |
|---|---|---|
| "the items together cover exactly what was asked, nothing added" (and ask before adding the refactor) | examples/reader/rules/engineering.md rule 4, which states the scope rule in its own right | `skills/capture/SKILL.md` · An interruption, so keep it short |
| "never act on a guessed reading of an irreversible command" | examples/reader/rules/safety.md rule 5 (ask when the wrong reading is costly), the rule that states it on its own | `skills/queue/SKILL.md` · The queue |

## 🆕 Rules to copy: 8

| # | rule or skill | kind | held in | |
|:--:|---|:--:|---|:--:|
| 1 | "the answers it returned may be the recommended ones, not what the owner picked. Read each answer back in text and ask the owner to confirm" | rule | `skills/capture/sections/prompt-me.md` · Prompt me: answering the open questions with a tap (the rest) | 🟩 |
| 2 | "List every checkable claim in the area" | skill | `skills/herd/roles/auditor.md` · Method | 🟩 |
| 3 | "never `pkill` or `killall` by pattern: you could stop another auditor's run. Stop a process by the pid you started" | rule | `skills/herd/roles/auditor.md` · Hard rules | 🟩 |
| 4 | "one command per call, no `source` followed by `cd`, no `cd` chained into a longer line" | rule | `skills/herd/roles/auditor.md` · Prompt hygiene | 🟩 |
| 5 | "If a git fetch or push fails on authentication, stop and report the remote and the error. Never add a key, a token, an https remote or a for" | rule | `skills/herd/roles/reviewer.md` · (top) | 🟩 |
| 6 | "was a criterion, a test or a threshold changed to make it pass? Read the test diff" | rule | `skills/herd/roles/reviewer.md` · When the item says rigor: build | 🟩 |
| 7 | "Report what you observed, never the verdict." | rule | `skills/herd/roles/worker.md` · When the item says rigor: build | 🟩 |
| 8 | "A question the owner skipped is unread, not answered." | rule | `skills/queue/SKILL.md` · Staying reasonable | 🟩 |

## 🟩 Skill sections kept: 43

| # | section | |
|:--:|---|:--:|
| 1 | `skills/capture/SKILL.md` · Capture | 🟩 |
| 2 | `skills/capture/SKILL.md` · An interruption, so keep it short | 🟩 |
| 3 | `skills/capture/SKILL.md` · Asked to do work yourself: every session, not only the worker | 🟩 |
| 4 | `skills/capture/SKILL.md` · Rescue session: everything this session was tracking | 🟩 |
| 5 | `skills/capture/SKILL.md` · Stream-of-consciousness: the owner is riffing | 🟩 |
| 6 | `skills/capture/SKILL.md` · Prompt me: answering the open questions with a tap | 🟩 |
| 7 | `skills/capture/sections/prompt-me.md` · Prompt me: answering the open questions with a tap (the rest) | 🟩 |
| 8 | `skills/herd/SKILL.md` · Herd | 🟩 |
| 9 | `skills/herd/roles/associate.md` · The associate | 🟩 |
| 10 | `skills/herd/roles/auditor.md` · The auditor | 🟩 |
| 11 | `skills/herd/roles/auditor.md` · Method | 🟩 |
| 12 | `skills/herd/roles/auditor.md` · Findings | 🟩 |
| 13 | `skills/herd/roles/auditor.md` · Hard rules | 🟩 |
| 14 | `skills/herd/roles/auditor.md` · Prompt hygiene | 🟩 |
| 15 | `skills/herd/roles/auditor.md` · Report | 🟩 |
| 16 | `skills/herd/roles/auditor.md` · The coordinator's checklist | 🟩 |
| 17 | `skills/herd/roles/auditor.md` · A falsify item | 🟩 |
| 18 | `skills/herd/roles/bond.md` · A bond: you and {{WORKER_NAME}} review each other | 🟩 |
| 19 | `skills/herd/roles/handoff.md` · Handing off to a new session | 🟩 |
| 20 | `skills/herd/roles/handoff.md` · If you're retiring | 🟩 |
| 21 | `skills/herd/roles/handoff.md` · If you're the one that stays | 🟩 |
| 22 | `skills/herd/roles/handoff.md` · If you're the new session | 🟩 |
| 23 | `skills/herd/roles/handoff.md` · In chat | 🟩 |
| 24 | `skills/herd/roles/orchestrator.md` · The orchestrator | 🟩 |
| 25 | `skills/herd/roles/readonly.md` · The reply of a session that can't write | 🟩 |
| 26 | `skills/herd/roles/reviewer.md` · (top) | 🟩 |
| 27 | `skills/herd/roles/reviewer.md` · Setting up (once, when this pair starts) | 🟩 |
| 28 | `skills/herd/roles/reviewer.md` · Each review | 🟩 |
| 29 | `skills/herd/roles/reviewer.md` · Limits | 🟩 |
| 30 | `skills/herd/roles/reviewer.md` · Who started you, and stopping | 🟩 |
| 31 | `skills/herd/roles/reviewer.md` · When the item says rigor: build | 🟩 |
| 32 | `skills/herd/roles/worker.md` · The worker, in a pair | 🟩 |
| 33 | `skills/herd/roles/worker.md` · When the item says rigor: build | 🟩 |
| 34 | `skills/herd/sections/launch-refused.md` · A launch is refused | 🟩 |
| 35 | `skills/herd/sections/orchestrator.md` · The orchestrator at a run's end, and in cloud runs | 🟩 |
| 36 | `skills/queue/SKILL.md` · The queue | 🟩 |
| 37 | `skills/queue/SKILL.md` · Working the queue | 🟩 |
| 38 | `skills/queue/SKILL.md` · Telling the owner what another session said | 🟩 |
| 39 | `skills/queue/SKILL.md` · Questions for you | 🟩 |
| 40 | `skills/queue/SKILL.md` · Staying reasonable | 🟩 |
| 41 | `skills/queue/sections/asks.md` · Asking the owner to do something | 🟩 |
| 42 | `skills/queue/sections/field-trip.md` · Field Trip, and reading the owner as voice | 🟩 |
| 43 | `skills/queue/sections/setup.md` · Setting up a queue | 🟩 |

## 🗑️ Dropped: 21

The herder voice (u36 to u44) is persona. The twelve commands (u53 to u64) only wrap a skill or a `meow` call kept above.

`u36` · `u37` · `u38` · `u39` · `u40` · `u41` · `u42` · `u43` · `u44` · `u53` · `u54` · `u55` · `u56` · `u57` · `u58` · `u59` · `u60` · `u61` · `u62` · `u63` · `u64`

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| 4 skills (capture, herd, herder, queue) with role and section files | on demand | no | 43 kept sections |
| 12 commands | when typed | no | small |
| 3 hooks (`meow _hook`) | session start, compaction, session end | no | not measured |
| 0 agents, 0 MCP servers | n/a | n/a | none |

## ✅ Do this

- ⬜ 1. Install the plugin if you want its queue and review workflow, and change the four conflicting sections so a subagent dispatch carries no `model:`.
- ⬜ 2. Copy the seven standing rules and the audit procedure below into your own rules, whether or not you install.
- ⬜ 3. Read the three hooks once before installing: they print into every session in a repo that has a queue.

Carrying-cost case: the hooks inject on session start but not into subagents, and far more than one rule survives, so the plugin earns its cost.

## 📋 Proposed rules patch

Add to examples/reader/rules/engineering.md as items 8 to 14, in its numbered style (its section is about how work gets done, so no new section):

```diff
+8. **Authentication failure is a stop.** If a fetch or push fails on authentication, stop and report the remote and the error. Never add a key, a token, an https remote or a forwarded agent to get past it.
+9. **Report what you observed, never the verdict.** "All 12 tests pass" is an observation; "complete" is the reviewer's call.
+10. **Check that a test was not bent to pass.** Read the test diff for a changed criterion, test or threshold.
+11. **A skipped question is unread, not answered.** Do not take silence as yes or no; ask again.
+12. **After an interrupted prompt, read the answers back.** They may be the defaults, not the choice; confirm before acting.
+13. **Stop a process by the pid you started.** Never `pkill` or `killall` by pattern.
+14. **Keep each command plain:** one command per call, no `cd` chained into a longer line, absolute paths instead.
```

Proposed skill (name is mine): `audit-claims`, "List every checkable claim in a doc or skill, run each example, break the code it depends on, and give each claim a verdict: backed, untested, contradicted or untestable." The dossier shows the reader keeps skills in a skills folder (examples/reader/skills), so it would go beside `release-notes`; the choice is yours.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
