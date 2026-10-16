# 🔍 ch-v0403 0.40.3 · vetted against the sample reader

> ## 🟧 INSTALL WITH CHANGES · skip the voice skill, fix one sentence, copy eight rules
> Its hooks inject only after a compaction in a session on a queue's roster, and its 25 workflow sections work as shipped. One sentence in the reviewer role lets a reviewer retry a refused action unasked, which the reader's hard stops forbid, and the herder skill is all persona. Eight of its rules are worth copying as standing rules whatever you decide about the plugin.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-15` · neckbeard 1.14.0 · ch-v0403 0.40.3

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟩 | **Cost** | No always-on injection found. Three hooks (PreCompact `auto`, SessionStart `compact`, SessionEnd) run `bin/meow _hook`. Per `lib/cat_herder/hooks.py`, only SessionStart writes to the model, and only after a compaction in a rostered session. Bytes not measured (the inventory could not resolve the three hook commands). |
| 🟩 | **Reach** | Main session only (likely): no hooked event is known to fire in a subagent. |
| 🟨 | **Leaves state** | Counts compactions in the queue's roster record and notes ended sessions in per-machine state (`lib/cat_herder/ended.py`). The queue itself is git commits on its own branch or ref. 36 files in `lib/` and `tools/` match write patterns. |
| 🟨 | **Live surface** | `bin/meow` pushes and fetches queue branches over git remotes. `tools/` launchers use ssh, tmux and cloud sessions. No MCP servers. |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 8 rules to copy, 25 skill sections |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **1** | 🟥 |
| 🔁 | **already covered** | **2** | ⬜⬜ |
| 🆕 | **new, standing rule** | **8** | 🟩🟩🟩🟩🟩🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **0** | none |
| 🟩 | **skill sections kept** (33 units judged; a unit can also sit in a rules row) | **25** | 🟩 ×25 |
| 🗑️ | **dropped** (persona, illustration) | **8** | ⬛⬛⬛⬛⬛⬛⬛⬛ |

## ⛔ Conflicts: 1

| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| 1 | "You may try the same action, on your own judgement, and report the result, allowed or refused, as a data point." (about an action the worker's permission classifier refused) | "Never run anything destructive without my explicit go-ahead in this conversation" and "Stop and ask when one applies, even mid-task" | `skills/herd/roles/reviewer.md`, Limits, against `examples/reader/rules/safety.md` | ⛔ |

## 🔁 Already covered: 2

| its rule | covered by | held in |
|---|---|---|
| Work found along the way is queued, not done inline (`skills/capture/SKILL.md`, "Asked to do work yourself") | "do not narrow it quietly or widen it unasked" (rule 4) | `examples/reader/rules/engineering.md` |
| Never queue writes on the branch the code is on; ask before acting on a guessed reading of an irreversible command (`skills/queue/SKILL.md`, "The queue") | "Never push to `main`" (rule 2) and "If a request is ambiguous and the wrong reading is costly, ask" (rule 5). Rule 5 is cited because it states the ask as a rule in its own right | `examples/reader/rules/safety.md` |

## 🟩 Keep: 8 rules to copy, 25 skill sections

Rules to copy (new, standing), 8:

| # | rule, quoted | from | |
|:--:|---|---|:--:|
| 1 | "Facts come from the conversation or a file you checked; mark anything else as an assumption." | `skills/capture/SKILL.md`, "An interruption, so keep it short" | 🆕 |
| 2 | "A diff that both restructures code and changes behaviour, so you can't tell which lines do which, is a finding" | `skills/herd/roles/reviewer.md`, "Each review" | 🆕 |
| 3 | "name exactly what it covers (the item, the commit, the wording) and say when the owner gave it. It lapses when what it covers changes." | `skills/herd/roles/reviewer.md`, "Limits" | 🆕 |
| 4 | "was a criterion, a test or a threshold changed to make it pass? Read the test diff." | `skills/herd/roles/reviewer.md`, "When the item says rigor: build" | 🆕 |
| 5 | "attack it yourself first. A reviewer doesn't replace that." | `skills/herd/roles/worker.md`, "The worker, in a pair" | 🆕 |
| 6 | "Never simplify away validation at a trust boundary, error handling that prevents data loss, or a security measure." | `skills/herd/roles/worker.md`, "When the item says rigor: build" | 🆕 |
| 7 | "Its premise moved, or it's bigger now: don't build the old version." Show the owner the brief and what changed, then wait | `skills/queue/SKILL.md`, "Working the queue" | 🆕 |
| 8 | "A question the owner skipped is unread, not answered." Do not act on it | `skills/queue/SKILL.md`, "Staying reasonable" | 🆕 |

New on-demand skills: none.

Skill sections kept, 25:

| # | file and heading | |
|:--:|---|:--:|
| 1 | `skills/capture/SKILL.md`, "Capture" | 🟩 |
| 2 | `skills/capture/SKILL.md`, "An interruption, so keep it short" | 🟩 |
| 3 | `skills/capture/SKILL.md`, "Asked to do work yourself: every session, not only the worker" | 🟩 |
| 4 | `skills/capture/SKILL.md`, "Rescue session: everything this session was tracking" | 🟩 |
| 5 | `skills/capture/SKILL.md`, "Stream-of-consciousness: the owner is riffing" | 🟩 |
| 6 | `skills/herd/SKILL.md`, "Herd" | 🟩 |
| 7 | `skills/herd/roles/associate.md`, "The associate" | 🟩 |
| 8 | `skills/herd/roles/handoff.md`, "Handing off to a new session" | 🟩 |
| 9 | `skills/herd/roles/handoff.md`, "If you're retiring" | 🟩 |
| 10 | `skills/herd/roles/handoff.md`, "If you're the one that stays" | 🟩 |
| 11 | `skills/herd/roles/handoff.md`, "If you're the new session" | 🟩 |
| 12 | `skills/herd/roles/handoff.md`, "In chat" | 🟩 |
| 13 | `skills/herd/roles/reviewer.md`, top section | 🟩 |
| 14 | `skills/herd/roles/reviewer.md`, "Setting up (once, when this pair starts)" | 🟩 |
| 15 | `skills/herd/roles/reviewer.md`, "Each review" | 🟩 |
| 16 | `skills/herd/roles/reviewer.md`, "Limits" (after the fix in Do this) | 🟩 |
| 17 | `skills/herd/roles/reviewer.md`, "Who started you, and stopping" | 🟩 |
| 18 | `skills/herd/roles/reviewer.md`, "When the item says rigor: build" | 🟩 |
| 19 | `skills/herd/roles/worker.md`, "The worker, in a pair" | 🟩 |
| 20 | `skills/herd/roles/worker.md`, "When the item says rigor: build" | 🟩 |
| 21 | `skills/queue/SKILL.md`, "The queue" | 🟩 |
| 22 | `skills/queue/SKILL.md`, "Working the queue" | 🟩 |
| 23 | `skills/queue/SKILL.md`, "Telling the owner what another session said" | 🟩 |
| 24 | `skills/queue/SKILL.md`, "Staying reasonable" | 🟩 |
| 25 | `commands/meow.md`, top section | 🟩 |

## 🗑️ Dropped

`u21` · `u22` · `u23` · `u24` · `u25` · `u26` · `u27` (all of `skills/herder/SKILL.md`, the cat voice) · `u31` (one example ledger line in `skills/queue/SKILL.md`)

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| Hook: PreCompact `auto` (`bin/meow _hook precompact`) | before an automatic compaction | no | 817 B config shared with SessionStart |
| Hook: SessionStart `compact` (`bin/meow _hook sessionstart`) | after a compaction, rostered sessions only | no | unmeasured |
| Hook: SessionEnd (`bin/meow _hook sessionend`) | when a session closes | no | 505 B config |
| 4 skills: capture, herd, herder, queue | on demand | no | 14,262 / 20,779 / 6,058 / 26,814 B |
| Command `/meow` | on demand | no | 1,233 B text |
| Role files `skills/herd/roles/*.md` | read when a pair, handoff or associate role starts | no | about 30 KB (sum of the units) |

## ✅ Do this

- ⬜ 1. Before installing, strike or reword the reviewer sentence that lets a reviewer retry a refused action on its own judgement, so a reviewer asks you first. The hooks and skills are otherwise safe to run under your hard stops.
- ⬜ 2. Leave out the herder skill (`skills/herder/SKILL.md`) or never run `/herder`. It is persona only, and the plugin's plain wording is the default.
- ⬜ 3. Copy the eight rules below into your files.

This is none of Step 2's three cases exactly: the hooks inject only after a compaction in a rostered session, never every session and never in subagents, and 25 skill sections plus eight standing rules are worth more than that cost, so there is no copy-only trade to make.

## 📋 Proposed rules patch

The reader's `examples/reader/rules/engineering.md` is a numbered list of working rules, so rules 1, 2, 4, 5, 6 and 7 below go there as items 8 to 13. The reader's `examples/reader/rules/safety.md` holds hard stops about asking and approvals, so rules 3 and 8 go there as items 6 and 7.

```
engineering.md
8.  **Facts come from the conversation or a file I checked.** Mark anything else as an assumption.
9.  **Keep refactors apart from behaviour changes.** A diff that does both, so the lines can't be told apart, gets split before review.
10. **A passing test is suspect if a test, criterion or threshold was changed to make it pass.** Read the test diff.
11. **Attack your own work before handing it over.** A reviewer does not replace that.
12. **Never simplify away validation at a trust boundary, error handling that prevents data loss, or a security measure.**
13. **A brief that has aged gets reread against what changed.** If its premise moved or it grew, do not build the old version: show me what changed and wait.

safety.md
6. **An approval covers only what it named** (the item, the commit, the wording) and lapses when that changes. Say when it was given.
7. **A question I skipped is unread, not answered.** Do not act on it; ask it again.
```

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
