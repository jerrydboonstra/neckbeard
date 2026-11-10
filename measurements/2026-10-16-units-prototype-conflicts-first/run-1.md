# 🔍 ch-v0403 0.40.3 · vetted against the sample reader

> ## 🟧 INSTALL WITH CHANGES · keep the workflow skills, leave Field Trip off
> Three hooks fire only on compaction or session end, and only a rostered session hears or writes anything. 25 of the 33 sections are workflow skills that need the plugin's own `meow` tool, and one sentence in `skills/queue/SKILL.md` (Field Trip phone rules) cuts against the reader's "complete is required". Eight general rules are worth copying whether or not you install.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-15` · neckbeard 1.14.0 · ch-v0403 0.40.3

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟩 | **Cost** | Skill descriptions at session start; bodies (99 KB across 4 skills, 4 role files and 1 command) load on demand. Hooks print at most two lines, and only after an automatic compaction in a session on a roster (`lib/cat_herder/hooks.py`) |
| 🟩 | **Reach** | Main session only (no hooked event is known to fire in a subagent) |
| 🟨 | **Leaves state** | Session-end hook writes an `ended` record and the plugin keeps an `addresses` record, both in its machine state directory under the XDG state home (`lib/cat_herder/ended.py`, `lib/cat_herder/addresses.py`); the compaction hook also commits to the queue remote for a rostered session |
| 🟨 | **Live surface** | git fetch and push to a queue remote, ssh and tmux launchers (`tools/remote-session`, `tools/cloud-launcher`, `tools/agy-launcher`), no MCP servers |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 25 skill sections and 8 rules to copy |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **1** | 🟥 |
| 🔁 | **already covered** | **2** | ⬜⬜ |
| 🆕 | **new, standing rule** | **8** | 🟩🟩🟩🟩🟩🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **0** | none |
| 🗑️ | **dropped** (persona, extras, no value) | **8** | ▰▰▰▰▰▰▰▰ |
| 🟩 | **skills kept** (of 33 sections) | **25** | ▰ ×25 |

## ⛔ Conflicts: 1

| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| u28 | "Short. The answer first, in a few sentences. Details only when asked." (Field Trip phone rules) | "Short is good; complete is required", and give "the reasoning with the verdict" | `examples/reader/CLAUDE.md`, from `skills/queue/SKILL.md` > The queue | 🟨 |

## 🆕 Rules to copy: 8

| # | unit | rule | |
|:--:|---|---|:--:|
| u2 | `skills/capture/SKILL.md` > An interruption, so keep it short | "Facts come from the conversation or a file you checked; mark anything else as an assumption." | 🆕 |
| u15 | `skills/herd/roles/reviewer.md` > Each review | "A diff that both restructures code and changes behaviour, so you can't tell which lines do which, is a finding" | 🆕 |
| u16 | `skills/herd/roles/reviewer.md` > Limits | An owner's answer relayed to another session names what it covers and when it was given: "It lapses when what it covers changes." | 🆕 |
| u18 | `skills/herd/roles/reviewer.md` > When the item says rigor: build | "Name the failure you fear": write "I claim X; the failure I fear is Y", then try to produce Y | 🆕 |
| u19 | `skills/herd/roles/worker.md` > The worker, in a pair | A refused action stays refused: "Never ask the reviewer to run it for you: that would pass a refused action to another session." | 🆕 |
| u20 | `skills/herd/roles/worker.md` > When the item says rigor: build | "Never simplify away validation at a trust boundary, error handling that prevents data loss, or a security measure." | 🆕 |
| u29 | `skills/queue/SKILL.md` > Working the queue | "Its premise moved, or it's bigger now: don't build the old version." Show what changed and wait | 🆕 |
| u32 | `skills/queue/SKILL.md` > Staying reasonable | "A question the owner skipped is unread, not answered": don't take it as a yes or a no, and don't act on it | 🆕 |

## 🔁 Already covered: 2

| its rule | covered by | held in |
|---|---|---|
| u3 `skills/capture/SKILL.md` > Asked to do work yourself: work found along the way is captured, not done inline | Rule 4, the scope asked for is the deliverable (the queue-then-claim steps are meow's own) | `examples/reader/rules/engineering.md` |
| u28 `skills/queue/SKILL.md` > The queue: never act on a guessed reading of an irreversible command; do not `init` over a config unasked | Rule 5, ask when the wrong reading is costly, stated as a rule in its own right (rule 1 only mentions destructive acts) | `examples/reader/rules/safety.md` |

## 🟩 Keep: 25

| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| u1 | `skills/capture/SKILL.md` > Capture | skill | 🟩 |
| u2 | `skills/capture/SKILL.md` > An interruption, so keep it short | skill | ⭐ |
| u3 | `skills/capture/SKILL.md` > Asked to do work yourself | skill | 🟩 |
| u4 | `skills/capture/SKILL.md` > Rescue session | skill | 🟩 |
| u5 | `skills/capture/SKILL.md` > Stream-of-consciousness | skill | 🟩 |
| u6 | `skills/herd/SKILL.md` > Herd | skill | 🟩 |
| u7 | `skills/herd/roles/associate.md` > The associate | role | 🟩 |
| u8 | `skills/herd/roles/handoff.md` > Handing off to a new session | role | 🟩 |
| u9 | `skills/herd/roles/handoff.md` > If you're retiring | role | 🟩 |
| u10 | `skills/herd/roles/handoff.md` > If you're the one that stays | role | 🟩 |
| u11 | `skills/herd/roles/handoff.md` > If you're the new session | role | 🟩 |
| u12 | `skills/herd/roles/handoff.md` > In chat | role | 🟩 |
| u13 | `skills/herd/roles/reviewer.md` > (top) | role | 🟩 |
| u14 | `skills/herd/roles/reviewer.md` > Setting up | role | 🟩 |
| u15 | `skills/herd/roles/reviewer.md` > Each review | role | ⭐ |
| u16 | `skills/herd/roles/reviewer.md` > Limits | role | ⭐ |
| u17 | `skills/herd/roles/reviewer.md` > Who started you, and stopping | role | 🟩 |
| u18 | `skills/herd/roles/reviewer.md` > When the item says rigor: build | role | ⭐ |
| u19 | `skills/herd/roles/worker.md` > The worker, in a pair | role | ⭐ |
| u20 | `skills/herd/roles/worker.md` > When the item says rigor: build | role | ⭐ |
| u28 | `skills/queue/SKILL.md` > The queue | skill | 🟨 |
| u29 | `skills/queue/SKILL.md` > Working the queue | skill | ⭐ |
| u30 | `skills/queue/SKILL.md` > Telling the owner what another session said | skill | 🟩 |
| u32 | `skills/queue/SKILL.md` > Staying reasonable | skill | ⭐ |
| u33 | `commands/meow.md` > (top) | command | 🟩 |

## 🗑️ Dropped

`u21` · `u22` · `u23` · `u24` · `u25` · `u26` · `u27` (all in `skills/herder/SKILL.md`: cat voice, persona and wording) · `u31` (`skills/queue/SKILL.md` > Questions for you: one sample ledger line)

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| 4 skills: capture, herd, herder, queue | descriptions each session, bodies on demand | no | 14,262 + 20,779 + 6,058 + 26,814 B |
| 4 role files under `skills/herd/roles/` | read by the herd skill on demand | no | 29,805 B |
| `commands/meow.md` | when `/meow` is typed | no | 1,425 B |
| PreCompact hook (auto) | an automatic compaction, rostered sessions only | no | writes one queue commit |
| SessionStart hook (compact) | after a compaction, rostered sessions only | no | up to 2 lines on stdout |
| SessionEnd hook | a session closes | no | one small state file |
| `rules/cat-herder.mdc` | Cursor only (`alwaysApply`); Claude Code does not load it | no | 932 B |
| `hooks.json` | Antigravity only; Claude Code does not load it | no | one PreToolUse entry |

## ✅ Do this

- ⬜ 1. Copy the 8 rules in the patch below into `examples/reader/rules/engineering.md`.
- ⬜ 2. If you adopt the queue workflow, load the plugin for one session first and leave Field Trip off: its phone rules are inactive until the owner turns them on.
- ⬜ 3. The 8 dropped sections (cat voice and one sample line) need nothing from you.

Carrying-cost case: hooks exist but act rarely and stay in the main session, and more than one rule survives, so the plugin's value is in its tool-bound workflow skills and the rules can be copied either way.

## 📋 Proposed rules patch

Add after rule 7 in `examples/reader/rules/engineering.md`, which is a numbered list of short rules, so the new ones continue the numbering:

```
8. **Mark unchecked facts as assumptions.** A fact comes from the conversation or a file you read.
9. **A change that mixes a refactor with a behaviour change is a finding.** Split the refactor out.
10. **An approval covers only what it names.** It lapses when what it covers changes.
11. **Name the failure you fear.** Write "I claim X; the failure I fear is Y", then try to produce Y.
12. **A refused action stays refused.** Do not hand it to another session to run.
13. **Never simplify away validation at a trust boundary,** error handling that prevents data loss, or a security measure.
14. **Re-check a stale brief before starting.** If its premise moved, show what changed and wait.
15. **A skipped question is unread, not answered.** Do not read it as a yes or a no, and do not act on it.
```

No new on-demand skills came out of the pass.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
