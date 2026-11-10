# 🔍 ch-v0403 0.40.3 · vetted against the sample reader

> ## 🟧 INSTALL WITH CHANGES · keep the queue skills, fix two retry sentences, copy four rules
> It costs nothing at session start: its three hooks fire only on compaction or session end, and its skills load on demand. Two sentences let a reviewer or worker retry a refused action on its own judgement, which collides with the reader's destructive-action stop. Four general rules are worth copying as standing text, and 24 of its 33 sections work as shipped and add something the reader lacks.

Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-16` · neckbeard 1.14.0 · ch-v0403 0.40.3

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟩 | **Cost** | No injection at session start. SessionStart fires only after a compaction and says one short notice, and only in a session on a queue roster. Skills load when called. |
| 🟩 | **Reach** | Main session only (certain): no hooked event is known to fire in a subagent. |
| 🟨 | **Leaves state** | SessionEnd records the ended session in this machine's state (`lib/cat_herder/ended.py`). PreCompact writes a compaction count to the queue's roster and may fetch or push, but only in a repo with a queue. Nothing outside those. |
| 🟨 | **Live surface** | `bin/meow` runs from every hook and from the skills. It talks to git remotes for the queue. Launchers in `tools/` start other sessions over ssh when the owner sets one. No MCP servers. |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 24 skill sections and 4 rules to copy |

## 🧮 How its rules sorted

Counts are units (one section of one instruction file). The 33 units split two ways: 24 skill sections kept and 9 dropped.

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **2** | 🟥🟥 |
| 🔁 | **already covered** | **2** | ⬜⬜ |
| 🆕 | **new, standing rule** | **4** | 🟩🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **0** | none |
| 🗑️ | **dropped** (persona, extras, no value) | **9** | ⬛⬛⬛⬛⬛⬛⬛⬛⬛ |

Skills kept: 24 of 33 units. Separately, 27 units hold no general rule beyond the plugin's own mechanics.

## ⛔ Conflicts: 2
| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| u16 | skills/herd/roles/reviewer.md, "Limits": "You may try the same action, on your own judgement, and report the result, allowed or refused, as a data point." | "Never run anything destructive without my explicit go-ahead in this conversation" | examples/reader/rules/safety.md (rule 1) | ⛔ |
| u19 | skills/herd/roles/worker.md, "The worker, in a pair": "The reviewer may try an action you reported as refused, on its own judgement, and report what happened." | the same destructive-action stop | examples/reader/rules/safety.md (rule 1) | ⛔ |

Both permit a retry with no limit. Ask the plugin for one: retry only if the action is not destructive, and never one the owner has not approved.

## 🔁 Already covered: 2
| its rule | covered by | held in |
|---|---|---|
| skills/queue/SKILL.md, "The queue": read a guessed reading of an irreversible command back and wait for a yes | "If a request is ambiguous and the wrong reading is costly, ask." Chosen because it states the ask-first rule on its own, where rule 1 only lists destructive acts. | examples/reader/rules/safety.md (rule 5) |
| skills/queue/SKILL.md, "Working the queue": reread a stale item against what changed, and if its premise moved, show the owner and wait | "say what you would change and let me decide." Chosen because it covers narrowing or widening a brief, which is what the ready check does. | examples/reader/rules/engineering.md (rule 4) |

## 🆕 Rules to copy: 4
| # | unit | rule to copy | kind |
|:--:|---|---|:--:|
| u15 | skills/herd/roles/reviewer.md, "Each review" | "A diff that both restructures code and changes behaviour, so you can't tell which lines do which, is a finding" | standing |
| u18 | skills/herd/roles/reviewer.md, "When the item says rigor: build" | "Was a criterion, a test or a threshold changed to make it pass? Read the test diff." | standing |
| u20 | skills/herd/roles/worker.md, "When the item says rigor: build" | "Never simplify away validation at a trust boundary, error handling that prevents data loss, or a security measure." | standing |
| u32 | skills/queue/SKILL.md, "Staying reasonable" | "When a reply skips something you asked, don't take it as a yes or a no, and don't act on it." | standing |

No on-demand skill came out of this pass.

## 🟩 Keep: 24
The plugin's own workflow skills, kept because they work as shipped and the reader has nothing like them (its only skill drafts release notes). u16 and u19 are kept except for the one sentence each in the conflicts grid.

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
| u16 | skills/herd/roles/reviewer.md, "Limits" | skill | 🟩 |
| u17 | skills/herd/roles/reviewer.md, "Who started you, and stopping" | skill | 🟩 |
| u18 | skills/herd/roles/reviewer.md, "When the item says rigor: build" | skill | 🟩 |
| u19 | skills/herd/roles/worker.md, "The worker, in a pair" | skill | 🟩 |
| u20 | skills/herd/roles/worker.md, "When the item says rigor: build" | skill | 🟩 |
| u28 | skills/queue/SKILL.md, "The queue" | skill | 🟩 |
| u29 | skills/queue/SKILL.md, "Working the queue" | skill | 🟩 |
| u30 | skills/queue/SKILL.md, "Telling the owner what another session said" | skill | 🟩 |
| u32 | skills/queue/SKILL.md, "Staying reasonable" | skill | 🟩 |

## 🗑️ Dropped
`u21` · `u22` · `u23` · `u24` · `u25` · `u26` · `u27` (the herder skill: cat voice and persona) · `u31` (a sample ledger line) · `u33` (the `meow` command wrapper)

## 🧩 What it installs
| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| SessionStart hook (`meow _hook sessionstart`) | after a compaction, in a session on a roster | no | one short notice |
| PreCompact hook (`meow _hook precompact`) | automatic compaction | no | writes a count, no output |
| SessionEnd hook (`meow _hook sessionend`) | session close | no | local state write |
| skill `capture` | on demand | no | about 13 KB of text |
| skill `herd` and its roles | on demand | no | about 49 KB of text |
| skill `queue` | on demand | no | about 26 KB of text |
| skill `herder` | on demand | no | about 6 KB of text |
| command `meow` | on demand | no | about 1 KB of text |

## ✅ Do this
- ⬜ 1. Ask the plugin for a limit on the two retry sentences (u16, u19), or edit them locally, before the pair roles run with a reviewer.
- ⬜ 2. Copy the four rules below into `examples/reader/rules/engineering.md`.
- ⬜ 3. Install only if you will run the `meow` queue; skip the `herder` skill and the `/meow` command, which add voice and a wrapper.

Carrying-cost case: the hooks inject nothing standing and never reach subagents, so there is no always-on cost to weigh, and the only question is whether the rules are good. The four standing rules are worth copying even if you skip the plugin.

## 📋 Proposed rules patch
Add to `examples/reader/rules/engineering.md`, continuing its numbered list (the file holds how to build and work, and has seven items):

```
8. **Keep a refactor apart from a behaviour change.** A diff that does both, so you can't tell which lines do which, gets split.
9. **When a test passes, ask what changed to make it pass.** Read the test diff for a loosened criterion, test or threshold.
10. **Never simplify away validation at a trust boundary,** error handling that prevents data loss, or a security measure.
11. **A question I skip is unread, not answered.** Don't take silence as a yes or a no, and don't act on it.
```

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
