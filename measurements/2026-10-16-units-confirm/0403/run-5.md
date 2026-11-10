# 🔍 ch-v0403 0.40.3 · vetted against the sample reader

> ## 🟧 INSTALL WITH CHANGES · skip the voice skill, fix two retry sentences
> Cat Herder adds a git-based work queue, pairing and review loop that the sample reader has nothing like, so 24 of its 33 sections are worth keeping as shipped. Two sentences let a model retry a refused action on its own judgement, which fights the reader's destructive-action stop. Two general rules are worth copying as standing text.

Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-16` · neckbeard 1.14.0 · ch-v0403 0.40.3

## ⚡ At a glance

| | | |
|:--:|---|---|
| ❓ | **Cost** | Three hooks (PreCompact, SessionStart on compact, SessionEnd) run `bin/meow _hook ...`; what they inject could not be traced, so the size is unknown. Skills total about 67 KB of text, loaded on demand |
| 🟩 | **Reach** | Main session only (no hooked event is known to fire in a subagent) |
| 🟧 | **Leaves state** | Writes queue commits to a git branch, ref or remote; its scripts also carry 36 file-write patterns (lib, tools) |
| 🟧 | **Live surface** | The `meow` CLI, git remotes, optional launchers for starting other sessions (ssh, tmux); no MCP servers |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 24 skill sections, 2 rules to copy |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **2** | 🟥🟥 |
| 🔁 | **already covered** | **1** | ⬜ |
| 🆕 | **new, standing rule** | **2** | 🟩🟩 |
| 🆕 | **new, on-demand skill** | **0** | none |
| 🗑️ | **dropped** (persona, extras, no value) | **9** | ▰▰▰▰▰▰▰▰▰ |

Skills kept: 24 of 33 units (the two conflicting units stay in that count, with the fix below). Units dropped: 9. Units with nothing general to copy: 30.

## ⛔ Conflicts: 2
| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| u16 | skills/herd/roles/reviewer.md, "Limits": "You may try the same action, on your own judgement, and report the result" | "Never run anything destructive without my explicit go-ahead" | examples/reader/rules/safety.md | ⛔ |
| u19 | skills/herd/roles/worker.md, "The worker, in a pair": "The reviewer may try an action you reported as refused, on its own judgement" | "Never run anything destructive without my explicit go-ahead" | examples/reader/rules/safety.md | ⛔ |

Both permit a retry with no limit. Ask for one: the retry applies only to actions that are not destructive, and anything destructive still waits for the owner's go-ahead in the conversation.

## 🔁 Already covered: 1
| its rule | covered by | held in |
|---|---|---|
| u18 skills/herd/roles/reviewer.md, "When the item says rigor: build" (revert the change and watch the test fail; say what you did not check) | the rule that a test must be seen to fail, stated in its own right; the answers rule covers saying what was checked | examples/reader/rules/engineering.md (rule 3), examples/reader/CLAUDE.md |

## 🆕 Rules to copy: 2
| unit | quoted rule | kind |
|---|---|:--:|
| u15 skills/herd/roles/reviewer.md, "Each review" | "A diff that both restructures code and changes behaviour, so you can't tell which lines do which, is a finding" | 🆕 standing |
| u20 skills/herd/roles/worker.md, "When the item says rigor: build" | "Never simplify away validation at a trust boundary, error handling that prevents data loss, or a security measure." | 🆕 standing |

## 🟩 Keep: 24
| # | rule or skill | kind | |
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
| u13 | skills/herd/roles/reviewer.md, top | skill | 🟩 |
| u14 | skills/herd/roles/reviewer.md, "Setting up (once, when this pair starts)" | skill | 🟩 |
| u15 | skills/herd/roles/reviewer.md, "Each review" | skill | 🟩 |
| u16 | skills/herd/roles/reviewer.md, "Limits" (⛔ fix the retry sentence) | skill | 🟧 |
| u17 | skills/herd/roles/reviewer.md, "Who started you, and stopping" | skill | 🟩 |
| u18 | skills/herd/roles/reviewer.md, "When the item says rigor: build" | skill | 🟩 |
| u19 | skills/herd/roles/worker.md, "The worker, in a pair" (⛔ fix the retry sentence) | skill | 🟧 |
| u20 | skills/herd/roles/worker.md, "When the item says rigor: build" | skill | 🟩 |
| u28 | skills/queue/SKILL.md, "The queue" | skill | 🟩 |
| u29 | skills/queue/SKILL.md, "Working the queue" | skill | 🟩 |
| u30 | skills/queue/SKILL.md, "Telling the owner what another session said" | skill | 🟩 |
| u32 | skills/queue/SKILL.md, "Staying reasonable" | skill | 🟩 |
| u33 | commands/meow.md, top | command | 🟩 |

## 🗑️ Dropped
`u12` · `u21` · `u22` · `u23` · `u24` · `u25` · `u26` · `u27` · `u31`

Units u21 to u27 are the herder voice skill (persona and cat-speak). u12 is the scripted handoff chat lines, u31 is a sample ledger entry.

## 🧩 What it installs
| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| skills/capture, herd, queue (and role files under herd) | on demand, when a queue task or a pair comes up | no | about 62 KB |
| skills/herder | on demand, on the voice command | no | about 6 KB |
| commands/meow.md | when the owner types `/meow` | no | about 1.4 KB |
| hooks: PreCompact, SessionStart (compact), SessionEnd | at those events | no | unknown (3 hooks untraced) |

## ✅ Do this
- ⬜ 1. Copy the two standing rules in the patch below into the reader's engineering rules.
- ⬜ 2. If you install, edit the retry sentences in u16 and u19 to say a retry applies only to non-destructive actions, or accept that the reader's destructive-action stop still wins.
- ⬜ 3. Read the three hook commands (`bin/meow _hook precompact`, `sessionstart`, `sessionend`) before enabling; the dossier could not trace what they inject.
Carrying-cost case: the hooks have unknown cost and none reaches subagents, and the kept value is whole workflow skills rather than one or two rules, so there is something to weigh and the plugin is worth carrying once the hooks are read.

## 📋 Proposed rules patch
Add to examples/reader/rules/engineering.md, after rule 7 (the file is a numbered list of working rules; matching its numbering and bold lead-in):

```
8. **Never simplify away validation at a trust boundary, error handling that
   prevents data loss, or a security measure.** A shorter version that drops one
   is not a simplification.
9. **Keep a refactor out of a behaviour change.** A diff that restructures code
   and changes behaviour together, so the two can't be told apart, is split:
   the refactor first, the change after.
```

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
