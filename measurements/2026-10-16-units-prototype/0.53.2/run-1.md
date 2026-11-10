# 🔍 ch-v0532 0.53.2 · vetted against the sample reader

> ## 🟧 INSTALL WITH CHANGES · keep the three workflow skills, and rewrite the four lines that pick a subagent model
> Its hooks cost almost nothing outside a repo with a queue and never reach subagents, and 38 of its 64 sections are workflow rules the reader lacks. Four sections tell the model to send Haiku subagents or to pick the cheapest model on the dispatch call, which breaks the reader's subagent rule. The voice skill and the thin commands are dropped.
> 
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-15` · neckbeard 1.14.0 · ch-v0532 0.53.2

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟨 | **Cost** | 3 hooks, none resolved by the script, so I read `lib/cat_herder/hooks.py`: SessionStart prints nothing in a repo with no queue (the reader's project has none), and in a repo with a queue it prints the rules block plus role lines (size varies with the queue). Skill text is on demand: 76 KB across 4 skills, 5 KB across 12 commands |
| 🟩 | **Reach** | Main session only (certain: no SubagentStart or other subagent event is hooked) |
| 🟨 | **Leaves state** | SessionEnd appends a line to an `ended` file in the machine's state directory; `meow` commits and pushes queue state to a git remote or local ref, and `meow herd orient` installs a supervisor in the clone (skills/herd/roles/orchestrator.md) |
| 🟨 | **Live surface** | No MCP servers. The `bin/meow` command, git fetch and push, ssh, tmux and a launcher it can start sessions through |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 38 sections of its own skills and commands |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **4** | 🟥🟥🟥🟥 |
| 🟩 | **kept as shipped** (its own skills and commands) | **38** | 🟩 ×38 |
| 🆕 | **new, standing rule** | **0** | none |
| 🆕 | **new, on-demand skill** | **0** | none |
| 🔁 | **already covered** | **0** | none |
| 🗑️ | **dropped** (persona, extras, no value) | **22** | ⬛ ×22 |

## ⛔ Conflicts: 4
| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| 1 | "send 3 or 4 new read-only subagents on `claude-haiku-5-5`" (judging a `rigor: run` item), in `skills/herd/roles/orchestrator.md` | rule 6, "Do not override it on the dispatch call" | `examples/reader/rules/engineering.md` | 🟥 |
| 2 | "send your own swarm of read-only `claude-haiku-5-5` subagents", in `skills/herd/roles/reviewer.md` (Each review) | rule 6, "Do not override it on the dispatch call" | `examples/reader/rules/engineering.md` | 🟥 |
| 3 | "Send 3 or 4 subagents on `claude-haiku-5-5`" and "three subagents on `claude-haiku-5-5`", in `skills/herd/roles/worker.md` | rule 6, "Do not override it on the dispatch call" | `examples/reader/rules/engineering.md` | 🟥 |
| 4 | "agents on the cheapest capable model your host offers" (grooming step 3), in `skills/queue/SKILL.md` | rule 6, "Do not override it on the dispatch call" | `examples/reader/rules/engineering.md` | 🟥 |

Each of these dispatches a subagent and names its model in the same call, which is what rule 6 forbids. The model defaults the herd skill sets for sessions it starts (`meow herd pair start` starts a reviewer on opus) launch a whole session, not a subagent, so they are a different situation and not a conflict. One side note on `skills/herd/roles/worker.md`: its commit-subject example ("pairs.md: the nested-thread sentence reworded") is not the imperative form that `examples/reader/rules/engineering.md` rule 7 asks for.

## 🔁 Already covered: 0
Nothing in the target restates a reader rule closely enough to drop it; the five coding rules inside the worker's rigor-build section overlap `examples/reader/rules/engineering.md` rules 1, 2 and 5, but that section is kept whole as part of the herd skill.

## 🟩 Keep: 38
| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| 1 | `skills/capture/SKILL.md`: Capture | skill | 🟩 |
| 2 | `skills/capture/SKILL.md`: An interruption, so keep it short | skill | 🟩 |
| 3 | `skills/capture/SKILL.md`: Asked to do work yourself: every session, not only the worker | skill | 🟩 |
| 4 | `skills/capture/SKILL.md`: Rescue session: everything this session was tracking | skill | 🟩 |
| 5 | `skills/capture/SKILL.md`: Stream-of-consciousness: the owner is riffing | skill | 🟩 |
| 6 | `skills/capture/SKILL.md`: Prompt me: answering the open questions with a tap | skill | 🟩 |
| 7 | `skills/capture/sections/prompt-me.md`: Prompt me: answering the open questions with a tap (the rest) | skill | 🟩 |
| 8 | `skills/herd/SKILL.md`: Herd | skill | 🟩 |
| 9 | `skills/herd/roles/associate.md`: The associate | skill | 🟩 |
| 10 | `skills/herd/roles/auditor.md`: The auditor | skill | 🟩 |
| 11 | `skills/herd/roles/auditor.md`: Method | skill | 🟩 |
| 12 | `skills/herd/roles/auditor.md`: Findings | skill | 🟩 |
| 13 | `skills/herd/roles/auditor.md`: Hard rules | skill | 🟩 |
| 14 | `skills/herd/roles/auditor.md`: Prompt hygiene | skill | 🟩 |
| 15 | `skills/herd/roles/auditor.md`: Report | skill | 🟩 |
| 16 | `skills/herd/roles/auditor.md`: The coordinator's checklist | skill | 🟩 |
| 17 | `skills/herd/roles/auditor.md`: A falsify item | skill | 🟩 |
| 18 | `skills/herd/roles/bond.md`: A bond: you and {{WORKER_NAME}} review each other | skill | 🟩 |
| 19 | `skills/herd/roles/handoff.md`: Handing off to a new session | skill | 🟩 |
| 20 | `skills/herd/roles/handoff.md`: If you're retiring | skill | 🟩 |
| 21 | `skills/herd/roles/handoff.md`: If you're the one that stays | skill | 🟩 |
| 22 | `skills/herd/roles/handoff.md`: If you're the new session | skill | 🟩 |
| 23 | `skills/herd/roles/handoff.md`: In chat | skill | 🟩 |
| 24 | `skills/herd/roles/readonly.md`: The reply of a session that can't write | skill | 🟩 |
| 25 | `skills/herd/roles/reviewer.md`: (top) | skill | 🟩 |
| 26 | `skills/herd/roles/reviewer.md`: Limits | skill | 🟩 |
| 27 | `skills/herd/roles/reviewer.md`: Who started you, and stopping | skill | 🟩 |
| 28 | `skills/herd/roles/reviewer.md`: When the item says rigor: build | skill | 🟩 |
| 29 | `skills/herd/roles/worker.md`: When the item says rigor: build | skill | 🟩 |
| 30 | `skills/herd/sections/launch-refused.md`: A launch is refused | skill | 🟩 |
| 31 | `skills/herd/sections/orchestrator.md`: The orchestrator at a run's end, and in cloud runs | skill | 🟩 |
| 32 | `skills/queue/SKILL.md`: The queue | skill | 🟩 |
| 33 | `skills/queue/SKILL.md`: Telling the owner what another session said | skill | 🟩 |
| 34 | `skills/queue/SKILL.md`: Staying reasonable | skill | 🟩 |
| 35 | `skills/queue/sections/asks.md`: Asking the owner to do something | skill | 🟩 |
| 36 | `skills/queue/sections/field-trip.md`: Field Trip, and reading the owner as voice | skill | 🟩 |
| 37 | `skills/queue/sections/setup.md`: Setting up a queue | skill | 🟩 |
| 38 | command `(top)` | command | 🟩 |

## 🗑️ Dropped
`u27` · `u36` · `u37` · `u38` · `u39` · `u40` · `u41` · `u42` · `u43` · `u44` · `u48` · `u53` · `u54` · `u55` · `u56` · `u58` · `u59` · `u60` · `u61` · `u62` · `u63` · `u64`

The dropped units are the herder voice skill (u36 to u44), one placeholder (u27), one sample ledger line (u48) and eleven thin commands that only point at a skill judged elsewhere.

## 🧩 What it installs
| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| skill `capture` (+ one section file) | on demand | no | 17.9 KB |
| skill `herd` (+ role and section files) | on demand | no | 25.6 KB |
| skill `herder` (voice) | on demand | no | 7.5 KB |
| skill `queue` (+ section files) | on demand | no | 25.0 KB |
| 12 commands | when typed | no | 5.1 KB |
| hook SessionStart (`startup\|resume\|compact`) | every session start | no | not fixed |
| hook PreCompact (`auto`) | automatic compaction | no | no output, one queue write |
| hook SessionEnd | session close | no | no output |
| `bin/meow` and `tools/` scripts | when a skill runs them | no | n/a |

## ✅ Do this
- ⬜ 1. Install, then keep the four spots above out of the model's hands: edit those lines in your copy so the subagent runs on the model its definition pins, or add a stated exception to rule 6 if you want Haiku swarms.
- ⬜ 2. Skip the `herder` skill unless you want the cat voice, and note that every skill assumes the `meow` command from this plugin is on the path.
Carrying-cost case: the hooks fire at every session start but print nothing outside a repo with a queue and never reach subagents, and many sections survive, so the cost is worth carrying.

## 📋 Proposed rules patch
Nothing to add.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
