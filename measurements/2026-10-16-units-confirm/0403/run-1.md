# 🔍 ch-v0403 0.40.3 · vetted against the sample reader

> ## 🟧 INSTALL WITH CHANGES · keep the skills, fix two permissions, copy four rules
> 25 of 33 sections are Cat Herder's own queue and herd workflow, which the reader has nothing like, so they stay. Two sentences let a model repeat a refused action on its own judgement, which the reader's destructive-action stop forbids without a go-ahead. Four general rules are worth copying as standing rules, and the cat-voice sections are persona and should go.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-16` · neckbeard 1.14.0 · ch-v0403 0.40.3

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟩 | **Cost** | Nothing at session start. One SessionStart hook (matcher `compact`) adds a line or two after a compaction, and only for a session on a Cat Herder roster. Skills load on demand (about 98 KB across four) and the `/meow` command is 1.4 KB |
| 🟩 | **Reach** | Main session only (certain: no hooked event fires in a subagent) |
| 🟨 | **Leaves state** | SessionEnd writes an "ended" record to the plugin's per-machine state folder, outside the project. `meow` itself commits and pushes the queue branch of the repo it runs in |
| 🟨 | **Live surface** | No MCP servers. `bin/meow` runs git fetch and push, and `tools/` holds launchers for other sessions (ssh, cloud, Antigravity) |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 25 skill sections and 4 rules |

The three hooks showed as unidentifiable in the dossier, so I read them by hand in `lib/cat_herder/hooks.py`. precompact counts a compaction on the roster record and is silent. sessionstart prints a notice only for a rostered session. sessionend records the close.

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **2** | 🟥🟥 |
| 🔁 | **already covered** | **2** | ⬜⬜ |
| 🆕 | **new, standing rule** | **4** | 🟩🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **0** | none |
| 🗑️ | **dropped** (persona, extras, no value) | **8** | ⬛⬛⬛⬛⬛⬛⬛⬛ |

Skills kept: 25 of 33 sections. Sections with no general rule: 27.

## ⛔ Conflicts: 2

| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| u16 | skills/herd/roles/reviewer.md, "Limits": "You may try the same action, on your own judgement, and report the result" | "Never run anything destructive without my explicit go-ahead" | examples/reader/rules/safety.md | ⛔ |
| u19 | skills/herd/roles/worker.md, "The worker, in a pair": "The reviewer may try an action you reported as refused, on its own judgement" | "Never run anything destructive without my explicit go-ahead" | examples/reader/rules/safety.md | ⛔ |

Limit to ask for on both: the retry may be made only when the action is not destructive (no `rm -rf`, no force-push, nothing the reader's rule lists), and anything destructive still needs the owner's go-ahead in the conversation.

## 🔁 Already covered: 2

| its rule | covered by | held in |
|---|---|---|
| u16 skills/herd/roles/reviewer.md, "Limits": a finding outside the item's scope is only a suggestion | "The scope I asked for is the deliverable." I chose it because it states scope as a rule of its own | examples/reader/rules/engineering.md |
| u28 skills/queue/SKILL.md, "The queue": never act on a guessed reading of an irreversible command | "If a request is ambiguous and the wrong reading is costly, ask." | examples/reader/rules/safety.md |

## 🆕 Rules to copy: 4

| # | unit | rule to copy | kind |
|:--:|---|---|:--:|
| u15 | skills/herd/roles/reviewer.md, "Each review" | A diff that "restructures code and changes behaviour" at once is a finding: "split the refactor out" | standing |
| u18 | skills/herd/roles/reviewer.md, "When the item says rigor: build" | "was a criterion, a test or a threshold changed to make it pass? Read the test diff." | standing |
| u20 | skills/herd/roles/worker.md, "When the item says rigor: build" | "Never simplify away validation at a trust boundary, error handling that prevents data loss, or a security measure." | standing |
| u29 | skills/queue/SKILL.md, "Working the queue" | "Its premise moved, or it's bigger now: don't build the old version." Show the owner what changed and wait | standing |

## 🟩 Keep: 25

| # | skill section | kind | |
|:--:|---|:--:|:--:|
| u1 | skills/capture/SKILL.md, "Capture" | skill | 🟩 |
| u2 | skills/capture/SKILL.md, "An interruption, so keep it short" | skill | 🟩 |
| u3 | skills/capture/SKILL.md, "Asked to do work yourself: every session, not only the worker" | skill | 🟩 |
| u4 | skills/capture/SKILL.md, "Rescue session: everything this session was tracking" | skill | 🟩 |
| u5 | skills/capture/SKILL.md, "Stream-of-consciousness: the owner is riffing" | skill | 🟩 |
| u6 | skills/herd/SKILL.md, "Herd" | skill | 🟩 |
| u7 | skills/herd/roles/associate.md, "The associate" | skill | 🟩 |
| u8 | skills/herd/roles/handoff.md, "Handing off to a new session" | skill | 🟩 |
| u9 | skills/herd/roles/handoff.md, "If you're retiring" | skill | 🟩 |
| u10 | skills/herd/roles/handoff.md, "If you're the one that stays" | skill | 🟩 |
| u11 | skills/herd/roles/handoff.md, "If you're the new session" | skill | 🟩 |
| u12 | skills/herd/roles/handoff.md, "In chat" | skill | 🟩 |
| u13 | skills/herd/roles/reviewer.md, "(top)" | skill | 🟩 |
| u14 | skills/herd/roles/reviewer.md, "Setting up (once, when this pair starts)" | skill | 🟩 |
| u15 | skills/herd/roles/reviewer.md, "Each review" | skill | 🟩 |
| u16 | skills/herd/roles/reviewer.md, "Limits" (after the fix in ⛔) | skill | 🟧 |
| u17 | skills/herd/roles/reviewer.md, "Who started you, and stopping" | skill | 🟩 |
| u18 | skills/herd/roles/reviewer.md, "When the item says rigor: build" | skill | 🟩 |
| u19 | skills/herd/roles/worker.md, "The worker, in a pair" (after the fix in ⛔) | skill | 🟧 |
| u20 | skills/herd/roles/worker.md, "When the item says rigor: build" | skill | 🟩 |
| u28 | skills/queue/SKILL.md, "The queue" | skill | 🟩 |
| u29 | skills/queue/SKILL.md, "Working the queue" | skill | 🟩 |
| u30 | skills/queue/SKILL.md, "Telling the owner what another session said" | skill | 🟩 |
| u32 | skills/queue/SKILL.md, "Staying reasonable" | skill | 🟩 |
| u33 | commands/meow.md, "(top)" | command | 🟩 |

## 🗑️ Dropped
`u21` · `u22` · `u23` · `u24` · `u25` · `u26` · `u27` · `u31`

u21 to u27 are the cat-voice persona in skills/herder/SKILL.md. u31 is a sample ledger line from skills/queue/SKILL.md, not an instruction.

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| 4 skills (capture, herd, herder, queue) | on demand | no | about 98 KB |
| command `/meow` | when invoked | no | 1.4 KB |
| hook SessionStart (compact) | after an automatic compaction, rostered sessions only | no | a line or two |
| hook PreCompact (auto) | before an automatic compaction, silent | no | none injected |
| hook SessionEnd | session close, writes an "ended" record | no | none injected |
| `bin/meow` and `tools/` | when run | no | not measured |

## ✅ Do this
- ⬜ 1. Ask the author to limit the two retry sentences (u16, u19) to non-destructive actions, or edit them in your copy before use.
- ⬜ 2. Copy the four standing rules below into your rules.
- ⬜ 3. Skip the herder skill (u21 to u27), which is persona only.

Case: there is no always-on cost and the hooks do not reach subagents, so the carrying-cost line does not push toward copying only. Install is reasonable if you use Cat Herder's queue, because the 25 kept sections need its `meow` tool.

## 📋 Proposed rules patch
Add to `examples/reader/rules/engineering.md`, which already holds the build rules, numbered on from 7 (my proposal):

```
8. **Keep refactors out of behaviour changes.** A diff that restructures code and changes behaviour at once gets split: the refactor first, the change after it.
9. **A passing test is only evidence if the bar stayed put.** Check whether a criterion, a test or a threshold was changed to make it pass; read the test diff.
10. **Never simplify away validation at a trust boundary, error handling that prevents data loss, or a security measure.**
11. **Recheck an old brief before building it.** If its premise moved or the work grew, do not build the old version: show what changed and wait.
```

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
