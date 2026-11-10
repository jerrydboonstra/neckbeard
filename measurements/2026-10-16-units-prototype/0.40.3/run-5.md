# 🔍 ch-v0403 0.40.3 · vetted against the sample reader

> ## 🟩 INSTALL · keep it, it earns its place
> Nothing in it fights the reader's rules, and it adds a queue, review and handoff workflow the reader has no skills for. It injects nothing on every session: the three hooks speak only after a compaction and only in a session on a queue's roster. The cat voice skill is dropped as persona, and it is off by default.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-15` · neckbeard 1.14.0 · ch-v0403 0.40.3

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟩 | **Cost** | No always-on injection. SessionStart (compact only) prints at most two short sentences after a compaction, and only in a session on a queue's roster. Skill text loads when a skill is used. |
| 🟩 | **Reach** | Main session only: no hooked event is known to fire in a subagent. |
| 🟨 | **Leaves state** | PreCompact adds a compaction count to the queue's roster record. SessionEnd records the ended session in this machine's state. Queue commands commit to a git queue (its own branch or ref, never the code's branch). |
| 🟨 | **Live surface** | The `meow` command, `git fetch` and `git push` to the queue remote over ssh, and optional launchers under `tools/` that the skills run only on the owner's say-so. No MCP servers. |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 24 units from four skills and one command |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **0** | none |
| ✅ | **kept as shipped** (the plugin's own skills and command) | **24** | 🟩 ▰ ×24 |
| 🆕 | **new, standing rule** | **0** | none |
| 🆕 | **new, on-demand skill** | **0** | none |
| 🔁 | **already covered** | **0** | none |
| 🗑️ | **dropped** (persona, extras, no value) | **9** | ⬛ ▰ ×9 |

## ⛔ Conflicts: 0
No unit tells the model to do what a reader rule forbids. Two near misses govern a different situation. The herd skill starts a reviewer session on opus when the owner names no model, which is not a subagent dispatch (examples/reader/rules/engineering.md, rule 6). Its queue and worker text pushes item branches only and never merges, in line with examples/reader/rules/safety.md.

## 🔁 Already covered: 0
No unit was judged a pure duplicate. The five coding rules in the worker's rigor section overlap examples/reader/rules/engineering.md (reuse, root cause, debt marker) but sit inside a shipped role, so they sorted as kept.

## 🟩 Keep: 24
| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| u1 | `skills/capture/SKILL.md · Capture` | skill | 🟩 |
| u2 | `skills/capture/SKILL.md · An interruption, so keep it short` | skill | 🟩 |
| u3 | `skills/capture/SKILL.md · Asked to do work yourself: every session, not only the worker` | skill | 🟩 |
| u4 | `skills/capture/SKILL.md · Rescue session: everything this session was tracking` | skill | 🟩 |
| u5 | `skills/capture/SKILL.md · Stream-of-consciousness: the owner is riffing` | skill | 🟩 |
| u6 | `skills/herd/SKILL.md · Herd` | skill | 🟩 |
| u7 | `skills/herd/roles/associate.md · The associate` | skill | 🟩 |
| u9 | `skills/herd/roles/handoff.md · If you're retiring` | skill | 🟩 |
| u10 | `skills/herd/roles/handoff.md · If you're the one that stays` | skill | 🟩 |
| u11 | `skills/herd/roles/handoff.md · If you're the new session` | skill | 🟩 |
| u12 | `skills/herd/roles/handoff.md · In chat` | skill | 🟩 |
| u13 | `skills/herd/roles/reviewer.md · (top)` | skill | 🟩 |
| u14 | `skills/herd/roles/reviewer.md · Setting up (once, when this pair starts)` | skill | 🟩 |
| u15 | `skills/herd/roles/reviewer.md · Each review` | skill | 🟩 |
| u16 | `skills/herd/roles/reviewer.md · Limits` | skill | 🟩 |
| u17 | `skills/herd/roles/reviewer.md · Who started you, and stopping` | skill | 🟩 |
| u18 | `skills/herd/roles/reviewer.md · When the item says rigor: build` | skill | 🟩 |
| u19 | `skills/herd/roles/worker.md · The worker, in a pair` | skill | 🟩 |
| u20 | `skills/herd/roles/worker.md · When the item says rigor: build` | skill | 🟩 |
| u28 | `skills/queue/SKILL.md · The queue` | skill | 🟩 |
| u29 | `skills/queue/SKILL.md · Working the queue` | skill | 🟩 |
| u30 | `skills/queue/SKILL.md · Telling the owner what another session said` | skill | 🟩 |
| u32 | `skills/queue/SKILL.md · Staying reasonable` | skill | 🟩 |
| u33 | `commands/meow.md · (top)` | command | 🟩 |

## 🗑️ Dropped
`u8` · `u21` · `u22` · `u23` · `u24` · `u25` · `u26` · `u27` · `u31`

## 🧩 What it installs
| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| skill `capture` | when the owner raises new work | no | 14,273 B |
| skill `herd` (with four role files) | pairs, hikes, handoffs | no | 20,779 B + 29,805 B |
| skill `queue` | any queue work | no | 26,817 B |
| skill `herder` (cat voice) | only when the owner turns the voice on | no | 6,062 B |
| command `meow` | when typed | no | 1,425 B |
| hook PreCompact (auto) | each automatic compaction | no | script only |
| hook SessionStart (compact) | after a compaction | no | script only |
| hook SessionEnd | a session closes | no | script only |

## ✅ Do this
- ⬜ 1. Install the plugin if you want a git-based work queue with review. Its skills only matter once a queue exists in a repo.
- ⬜ 2. Do not turn on the cat voice: it fights nothing, but it is persona and the reader prefers plain language.
Carrying-cost case: zero always-on injection and no hook that reaches subagents, so there is little to weigh and the question is only whether the skills are good.

## 📋 Proposed rules patch
Nothing to add. No unit sorted as a new standing rule or a new on-demand skill, because every general rule sits inside one of the plugin's own skills.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
