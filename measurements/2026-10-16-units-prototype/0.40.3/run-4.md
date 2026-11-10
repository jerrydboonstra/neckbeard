# 🔍 ch-v0403 0.40.3 · vetted against the sample reader

> ## 🟩 INSTALL · keep the plugin as shipped
> Cat Herder's three workflow skills (capture, herd, queue) and its `/meow` command work as shipped and cover ground the sample reader has nothing for. Its three hooks fire only on compaction and session end, nothing is injected at session start, and none reach subagents. The cat voice (8 units) is persona and gets dropped.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-15` · neckbeard 1.14.0 · ch-v0403 0.40.3

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟩 | **Cost** | No session-start injection. The `SessionStart` hook matches compaction only and prints a short retire notice, and only in a session on a roster. The skills load when invoked: about 95,500 characters across 33 units in all, 49,600 of them in herd |
| 🟩 | **Reach** | Main session only (certain: the dossier finds no event that fires in a subagent) |
| 🟨 | **Leaves state** | Counts a compaction on the session's roster record and notes a closed session in this machine's Cat Herder state (`lib/cat_herder/hooks.py`); the queue itself is git commits. Where the machine state sits was not traced |
| 🟨 | **Live surface** | Three hooks run `bin/meow _hook ...`; `tools/` holds ssh, tmux and cloud launchers that run only when invoked; no MCP servers |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 25 units: 24 skill and role sections plus the `/meow` command |

The dossier lists the three hooks as unidentifiable (the command is a `${CLAUDE_PLUGIN_ROOT}` path). I read `hooks/claude.json` and the module header in `lib/cat_herder/hooks.py` by hand: precompact and sessionend are silent, sessionstart speaks only after a compaction.

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **0** | none |
| ✅ | **kept as shipped** (the plugin's own skills, commands and roles) | **25** | 🟩 ×25 |
| 🆕 | **new, standing rule** | **0** | none |
| 🆕 | **new, on-demand skill** | **0** | none |
| 🔁 | **already covered** | **0** | none |
| 🗑️ | **dropped** (persona, extras, no value) | **8** | ⬛ ×8 |

## ⛔ Conflicts: 0
No unit tells the model to do what a reader rule forbids. Two near misses, each a different situation. `skills/herd/SKILL.md` starts a reviewer "on opus" by default, but that is a session the plugin launches, not a subagent dispatch, so examples/reader/rules/engineering.md rule 6 does not apply. The queue and herd skills ask the owner before setup, a pair, a clean or a force, which fits examples/reader/rules/safety.md rules 1, 3 and 5.

## 🔁 Already covered: 0
No unit was sorted here. Overlaps with examples/reader/rules/engineering.md rules 1, 2, 3 and 5 sit inside role files that are kept whole (`skills/herd/roles/worker.md` and `skills/herd/roles/reviewer.md`, rigor: build sections).

## 🟩 Keep: 25
| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| u1 | `skills/capture/SKILL.md` · Capture | skill | 🟩 |
| u2 | `skills/capture/SKILL.md` · An interruption, so keep it short | skill | 🟩 |
| u3 | `skills/capture/SKILL.md` · Asked to do work yourself | skill | 🟩 |
| u4 | `skills/capture/SKILL.md` · Rescue session | skill | 🟩 |
| u5 | `skills/capture/SKILL.md` · Stream-of-consciousness | skill | 🟩 |
| u6 | `skills/herd/SKILL.md` · Herd | skill | 🟩 |
| u7 | `skills/herd/roles/associate.md` · The associate | role | 🟩 |
| u8 | `skills/herd/roles/handoff.md` · Handing off to a new session | role | 🟩 |
| u9 | `skills/herd/roles/handoff.md` · If you're retiring | role | 🟩 |
| u10 | `skills/herd/roles/handoff.md` · If you're the one that stays | role | 🟩 |
| u11 | `skills/herd/roles/handoff.md` · If you're the new session | role | 🟩 |
| u12 | `skills/herd/roles/handoff.md` · In chat | role | 🟩 |
| u13 | `skills/herd/roles/reviewer.md` · (top) | role | 🟩 |
| u14 | `skills/herd/roles/reviewer.md` · Setting up | role | 🟩 |
| u15 | `skills/herd/roles/reviewer.md` · Each review | role | 🟩 |
| u16 | `skills/herd/roles/reviewer.md` · Limits | role | 🟩 |
| u17 | `skills/herd/roles/reviewer.md` · Who started you, and stopping | role | 🟩 |
| u18 | `skills/herd/roles/reviewer.md` · When the item says rigor: build | role | 🟩 |
| u19 | `skills/herd/roles/worker.md` · The worker, in a pair | role | 🟩 |
| u20 | `skills/herd/roles/worker.md` · When the item says rigor: build | role | 🟩 |
| u28 | `skills/queue/SKILL.md` · The queue | skill | 🟩 |
| u29 | `skills/queue/SKILL.md` · Working the queue | skill | 🟩 |
| u30 | `skills/queue/SKILL.md` · Telling the owner what another session said | skill | 🟩 |
| u32 | `skills/queue/SKILL.md` · Staying reasonable | skill | 🟩 |
| u33 | `commands/meow.md` · (top) | command | 🟩 |

## 🗑️ Dropped
`u21` · `u22` · `u23` · `u24` · `u25` · `u26` · `u27` · `u31`

Seven are the cat voice in `skills/herder/SKILL.md` (persona, off by default). One, `u31`, is a sample ledger line in `skills/queue/SKILL.md` that only illustrates what the other queue units describe.

## 🧩 What it installs
| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| skill `capture` | when invoked | no | 13,016 chars |
| skill `herd` (with associate, handoff, reviewer, worker roles) | when invoked | no | 49,601 chars |
| skill `herder` (cat voice, dropped) | when invoked | no | 5,637 chars |
| skill `queue` | when invoked | no | 26,060 chars |
| command `/meow` | when invoked | no | 1,233 chars |
| hook `SessionStart` (compact only) | after an automatic compaction | no | short notice, size not measured |
| hooks `PreCompact` (auto) and `SessionEnd` | compaction, session close | no | silent |

## ✅ Do this
- ⬜ 1. Install the plugin; skip or never invoke the `herder` skill so the cat voice stays off.
- ⬜ 2. Note that the pair and hike features start more sessions and cost money while a reviewer runs; the skills ask the owner first.

Case: three hooks exist but none inject at session start or reach subagents, and 25 units earn their place, so this is not the one-rule trade and the plugin is worth carrying whole.

## 📋 Proposed rules patch
nothing to add.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
