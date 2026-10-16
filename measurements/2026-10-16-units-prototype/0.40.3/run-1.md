# 🔍 ch-v0403 0.40.3 · vetted against the sample reader

> ## 🟩 INSTALL · keep it as shipped
> Computed verdict: INSTALL (0 conflicts, 23 units kept as shipped, 0 new standing, 0 new skill, 0 covered, 10 dropped). Its four skills and one command are a queue and review workflow that the reader's rules and skills do not touch, and none of its text breaks a reader rule. Its hooks stay quiet in a session that is not on a queue's roster and do not reach subagents.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-15` · neckbeard 1.14.0 · ch-v0403 0.40.3

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟩 | **Cost** | Nothing injected at session start. The skills load when invoked (about 99 KB of text across four skills, their role files and one command). One hook adds one or two lines after a compaction, and only for a session on a roster |
| 🟩 | **Reach** | Main session only. The hook events (PreCompact, SessionStart on compact, SessionEnd) fire in no subagent (likely: the dossier knows of no event that fires in one) |
| 🟨 | **Leaves state** | Queue commits to a git remote or local ref when `meow` runs; a roster record for compactions; a local note of an ended session (`lib/cat_herder/ended.py`). Nothing written outside a repo or the tool's own state by the hooks |
| 🟨 | **Live surface** | `bin/meow` runs from three hooks (5 to 20 second timeouts); the queue skill fetches and pushes to the queue's git remote; pair and handoff starts use a launcher the owner names (ssh, tmux) |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 23 units: 4 skills and 1 command |

The dossier flagged all three hooks as unidentifiable because each command is `bin/meow _hook <event>`. I read `hooks/claude.json`, `hooks/claude-codex.json` and `lib/cat_herder/hooks.py` by hand: the first two events only update local state, and `sessionstart` prints a notice only after a compaction, only when the session is on a roster.

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **0** | none |
| ✅ | **kept as shipped** (own skills and command) | **23** | 🟩 ×23 |
| 🆕 | **new, standing rule** | **0** | none |
| 🆕 | **new, on-demand skill** | **0** | none |
| 🔁 | **already covered** | **0** | none |
| 🗑️ | **dropped** (persona, extras, no value) | **10** | ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ |

## ⛔ Conflicts: 0
Nothing in the target tells the model to do what a reader rule forbids. Two places look close and are not conflicts.

| looks like | reader rule | why it is not a conflict |
|---|---|---|
| `skills/herd/SKILL.md`, "Herd": a session started without `--model` runs on opus | `examples/reader/rules/engineering.md` rule 6, subagents run on the model their definition pins | That rule governs a subagent dispatch. Here a launcher starts a separate session, and the text says "never override a model they chose" |
| `skills/queue/SKILL.md`, "The queue": `accept` and `reopen` verdicts | `examples/reader/rules/safety.md` rule 2, never merge a pull request | `accept` is a verdict written to the queue, not a pull request merge. The same skill stops before any queue write on main |

## 🔁 Already covered: 0
| its rule | covered by | held in |
|---|---|---|
| none | | |

The worker's five coding rules in `skills/herd/roles/worker.md`, "When the item says rigor: build", overlap `examples/reader/rules/engineering.md` rules 1, 2 and 5. They sit inside a kept role file with other rules, so the unit is kept, not counted as covered.

## 🟩 Keep: 23
| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| 1 | `skills/capture/SKILL.md`, "Capture" | skill | 🟩 |
| 2 | `skills/capture/SKILL.md`, "An interruption, so keep it short" | skill | 🟩 |
| 3 | `skills/capture/SKILL.md`, "Asked to do work yourself: every session, not only the worker" | skill | 🟩 |
| 4 | `skills/capture/SKILL.md`, "Rescue session: everything this session was tracking" | skill | 🟩 |
| 5 | `skills/capture/SKILL.md`, "Stream-of-consciousness: the owner is riffing" | skill | 🟩 |
| 6 | `skills/herd/SKILL.md`, "Herd" | skill | 🟩 |
| 7 | `skills/herd/roles/associate.md`, "The associate" | skill | 🟩 |
| 8 | `skills/herd/roles/handoff.md`, "If you're retiring" | skill | 🟩 |
| 9 | `skills/herd/roles/handoff.md`, "If you're the one that stays" | skill | 🟩 |
| 10 | `skills/herd/roles/handoff.md`, "If you're the new session" | skill | 🟩 |
| 11 | `skills/herd/roles/handoff.md`, "In chat" | skill | 🟩 |
| 12 | `skills/herd/roles/reviewer.md`, "(top)" | skill | 🟩 |
| 13 | `skills/herd/roles/reviewer.md`, "Each review" | skill | 🟩 |
| 14 | `skills/herd/roles/reviewer.md`, "Limits" | skill | 🟩 |
| 15 | `skills/herd/roles/reviewer.md`, "Who started you, and stopping" | skill | 🟩 |
| 16 | `skills/herd/roles/reviewer.md`, "When the item says rigor: build" | skill | 🟩 |
| 17 | `skills/herd/roles/worker.md`, "The worker, in a pair" | skill | 🟩 |
| 18 | `skills/herd/roles/worker.md`, "When the item says rigor: build" | skill | 🟩 |
| 19 | `skills/queue/SKILL.md`, "The queue" | skill | 🟩 |
| 20 | `skills/queue/SKILL.md`, "Working the queue" | skill | 🟩 |
| 21 | `skills/queue/SKILL.md`, "Telling the owner what another session said" | skill | 🟩 |
| 22 | `skills/queue/SKILL.md`, "Staying reasonable" | skill | 🟩 |
| 23 | `commands/meow.md`, the /meow command | command | 🟩 |

## 🗑️ Dropped
`u8` · `u14` · `u21` · `u22` · `u23` · `u24` · `u25` · `u26` · `u27` · `u31`

The dropped units are the herder voice skill (`u21` to `u27`: cat names, "Mrrp" openers, euphemisms), an empty setup stub (`u14`), a one-line description (`u8`) and an example ledger entry (`u31`).

## 🧩 What it installs
| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| `skills/capture/SKILL.md` | when invoked, or on words like "queue that" | no | 14,273 B |
| `skills/herd/SKILL.md` and `skills/herd/roles/*.md` | when invoked (pairs, hikes, handoffs) | no | 20,779 B + 29,805 B |
| `skills/herder/SKILL.md` | when invoked (voice on or off) | no | 6,062 B |
| `skills/queue/SKILL.md` | when invoked | no | 26,817 B |
| `commands/meow.md` | when the user types /meow | no | 1,425 B |
| `PreCompact` hook (auto) | counts a compaction on the roster | no | 0 B injected |
| `SessionStart` hook (compact) | prints a notice after a compaction, only on a roster | no | a line or two |
| `SessionEnd` hook | notes the ended session in local state | no | 0 B injected |

## ✅ Do this
- ⬜ 1. Install it. Try it first for one session with `--plugin-dir`, since the skills assume `meow` and a queue, and an unconfigured repo answers exit 3 ("don't set one up unasked").
- ⬜ 2. Leave the herder skill alone unless you want the cat voice; it is off by default and changes nothing until the owner asks.
Carrying-cost case: the hooks add nothing in ordinary sessions and do not reach subagents, and many units survive, so there is no trade to weigh against copying one rule.

## 📋 Proposed rules patch
Nothing to add.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
