# 🔍 ch-v0532 0.53.2 · vetted against the sample reader

> ## 🟧 INSTALL WITH CHANGES · keep the queue skills, cut the four steps that name a subagent model
> Cat Herder's four skills, twelve commands and role files carry 39 units of workflow the sample reader lacks, and its hooks inject nothing in a repo with no queue. Four units tell the model to run subagents on a named model, which the reader's engineering rules forbid. 21 units are cat voice or thin command wrappers.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-15` · neckbeard 1.14.0 · ch-v0532 0.53.2

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟨 | **Cost** | Three hooks (SessionStart, PreCompact, SessionEnd) run `bin/meow _hook`. Their output size is not fixed. In a repo with no queue the start hook prints nothing; in a repo with a queue it prints the repo's rules and answers, and for a rostered session its role and house-rules lines. |
| 🟩 | **Reach** | Main session only (likely): no hook event known to fire in a subagent. |
| 🟨 | **Leaves state** | SessionEnd writes a session-ended note in this machine's Cat Herder state. PreCompact writes a compaction count to the queue roster, only for a session already on a roster. The skills write the queue and push branches when used. |
| 🟨 | **Live surface** | No MCP servers. The `meow` command (git, and pushes to the queue's remote), plus launchers that start other sessions over ssh, tmux or the cloud, only when invoked. |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 39 skill, role, section and command units |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **4** | 🟥🟥🟥🟥 |
| 🔁 | **already covered** | **0** | none |
| 🟩 | **kept as shipped** (the plugin's own skills, commands and roles) | **39** | 🟩 ×39 |
| 🆕 | **new, standing rule** | **0** | none |
| 🆕 | **new, on-demand skill** | **0** | none |
| 🗑️ | **dropped** (persona, extras, no value) | **21** | ⬛ ×21 |

## ⛔ Conflicts: 4

| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| 1 | `skills/herd/roles/orchestrator.md` · The orchestrator (u24): send 3 or 4 new read-only subagents on `claude-haiku-5-5` | rule 6: "Do not override it on the dispatch call" | `examples/reader/rules/engineering.md` | ⛔ |
| 2 | `skills/herd/roles/reviewer.md` · Each review (u28): may send your own swarm of read-only `claude-haiku-5-5` subagents | rule 6: "Do not override it on the dispatch call" | `examples/reader/rules/engineering.md` | ⛔ |
| 3 | `skills/herd/roles/worker.md` · The worker, in a pair (u32): Send 3 or 4 subagents on `claude-haiku-5-5`, and three more for wording | rule 6: "Do not override it on the dispatch call" | `examples/reader/rules/engineering.md` | ⛔ |
| 4 | `skills/queue/SKILL.md` · Working the queue (u46): agents on the cheapest capable model your host offers | rule 6: "Do not override it on the dispatch call" | `examples/reader/rules/engineering.md` | ⛔ |

Both sides govern a subagent dispatch. The plugin's lines that pick a model for a session it starts (a reviewer or a successor on Opus, in `skills/herd/SKILL.md`) are a different situation and are not counted.

## 🔁 Already covered: 0

Nothing was judged a plain duplicate. `skills/herd/roles/worker.md` · When the item says rigor: build repeats reader rules 1, 2 and 5 in its coding list, but the unit also holds new done-note rules, so it stays under Keep.

## 🟩 Keep: 39

| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| 1 | `skills/capture/SKILL.md` · Capture (u1) | skill | 🟩 |
| 2 | `skills/capture/SKILL.md` · An interruption, so keep it short (u2) | skill | 🟩 |
| 3 | `skills/capture/SKILL.md` · Asked to do work yourself: every session, not only the worker (u3) | skill | 🟩 |
| 4 | `skills/capture/SKILL.md` · Rescue session: everything this session was tracking (u4) | skill | 🟩 |
| 5 | `skills/capture/SKILL.md` · Stream-of-consciousness: the owner is riffing (u5) | skill | 🟩 |
| 6 | `skills/capture/SKILL.md` · Prompt me: answering the open questions with a tap (u6) | skill | 🟩 |
| 7 | `skills/capture/sections/prompt-me.md` · Prompt me: answering the open questions with a tap (the rest) (u7) | section | 🟩 |
| 8 | `skills/herd/SKILL.md` · Herd (u8) | skill | 🟩 |
| 9 | `skills/herd/roles/associate.md` · The associate (u9) | role | 🟩 |
| 10 | `skills/herd/roles/auditor.md` · The auditor (u10) | role | 🟩 |
| 11 | `skills/herd/roles/auditor.md` · Method (u11) | role | 🟩 |
| 12 | `skills/herd/roles/auditor.md` · Findings (u12) | role | 🟩 |
| 13 | `skills/herd/roles/auditor.md` · Hard rules (u13) | role | 🟩 |
| 14 | `skills/herd/roles/auditor.md` · Prompt hygiene (u14) | role | 🟩 |
| 15 | `skills/herd/roles/auditor.md` · Report (u15) | role | 🟩 |
| 16 | `skills/herd/roles/auditor.md` · The coordinator's checklist (u16) | role | 🟩 |
| 17 | `skills/herd/roles/auditor.md` · A falsify item (u17) | role | 🟩 |
| 18 | `skills/herd/roles/bond.md` · A bond: you and {{WORKER_NAME}} review each other (u18) | role | 🟩 |
| 19 | `skills/herd/roles/handoff.md` · Handing off to a new session (u19) | role | 🟩 |
| 20 | `skills/herd/roles/handoff.md` · If you're retiring (u20) | role | 🟩 |
| 21 | `skills/herd/roles/handoff.md` · If you're the one that stays (u21) | role | 🟩 |
| 22 | `skills/herd/roles/handoff.md` · If you're the new session (u22) | role | 🟩 |
| 23 | `skills/herd/roles/handoff.md` · In chat (u23) | role | 🟩 |
| 24 | `skills/herd/roles/readonly.md` · The reply of a session that can't write (u25) | role | 🟩 |
| 25 | `skills/herd/roles/reviewer.md` · (top) (u26) | role | 🟩 |
| 26 | `skills/herd/roles/reviewer.md` · Setting up (once, when this pair starts) (u27) | role | 🟩 |
| 27 | `skills/herd/roles/reviewer.md` · Limits (u29) | role | 🟩 |
| 28 | `skills/herd/roles/reviewer.md` · Who started you, and stopping (u30) | role | 🟩 |
| 29 | `skills/herd/roles/reviewer.md` · When the item says rigor: build (u31) | role | 🟩 |
| 30 | `skills/herd/roles/worker.md` · When the item says rigor: build (u33) | role | 🟩 |
| 31 | `skills/herd/sections/launch-refused.md` · A launch is refused (u34) | section | 🟩 |
| 32 | `skills/herd/sections/orchestrator.md` · The orchestrator at a run's end, and in cloud runs (u35) | section | 🟩 |
| 33 | `skills/queue/SKILL.md` · The queue (u45) | skill | 🟩 |
| 34 | `skills/queue/SKILL.md` · Telling the owner what another session said (u47) | skill | 🟩 |
| 35 | `skills/queue/SKILL.md` · Staying reasonable (u49) | skill | 🟩 |
| 36 | `skills/queue/sections/asks.md` · Asking the owner to do something (u50) | section | 🟩 |
| 37 | `skills/queue/sections/field-trip.md` · Field Trip, and reading the owner as voice (u51) | section | 🟩 |
| 38 | `skills/queue/sections/setup.md` · Setting up a queue (u52) | section | 🟩 |
| 39 | command · (top) (u57) | command | 🟩 |

## 🗑️ Dropped

Cat voice and persona: `u36` · `u37` · `u38` · `u39` · `u40` · `u41` · `u42` · `u43` · `u44`

Sample ledger line: `u48`

Thin command wrappers: `u53` · `u54` · `u55` · `u56` · `u58` · `u59` · `u60` · `u61` · `u62` · `u63` · `u64`

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| hook SessionStart (`startup\|resume\|compact`) | session start | no | not fixed; empty with no queue |
| hook PreCompact (`auto`) | before an automatic compaction | no | writes only |
| hook SessionEnd | session close | no | writes only |
| skill `capture` with its roles and sections | on demand | no | 19,968 bytes judged |
| skill `herd` with its roles and sections | on demand | no | 103,344 bytes judged |
| skill `herder` with its roles and sections | on demand | no | 7,075 bytes judged |
| skill `queue` with its roles and sections | on demand | no | 35,953 bytes judged |
| 12 commands (`/asks`, `/board`, `/groom`, `/hike`, `/meow`, `/next`, `/park`, `/prompt-me`, `/rescue`, `/show`, `/status`, `/timeline`) | when typed | no | 3,366 bytes judged |

## ✅ Do this

- ⬜ 1. Decide how to handle the four units that name `claude-haiku-5-5` or "the cheapest capable model": ask the author to leave the model out of the dispatch, or accept that the plugin's swarm steps break `examples/reader/rules/engineering.md` rule 6.
- ⬜ 2. Install it only in repos where you want a Cat Herder queue; its hooks do nothing for a repo without one.
- ⬜ 3. Skip `skills/herder/SKILL.md` if you do not want the cat voice; it is off by default.

Carrying cost: three hooks that reach the main session only and print nothing without a queue, against 39 kept units, so there is more to weigh than one rule copied as text.

## 📋 Proposed rules patch

Nothing to add. No unit passed as a new standing rule or a new on-demand skill; the 39 kept units are the plugin's own workflow skills and stay inside the plugin.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
