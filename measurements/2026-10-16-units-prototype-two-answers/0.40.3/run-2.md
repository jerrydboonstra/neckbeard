# 🔍 ch-v0403 0.40.3 · vetted against the sample reader

> ## 🟩 INSTALL · skills work as shipped, copy three rules into your own file
> No conflicts with the sample reader's rules. The hooks run only at automatic compaction and session end, and do nothing in a session that is not on a queue's roster. Three general rules are worth copying as standing text, because they stop applying once a skill is unloaded.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-15` · neckbeard 1.14.0 · ch-v0403 0.40.3

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟩 | **Cost** | No text injected at session start. After an automatic compaction, one line telling the session how many compactions it has used (roster sessions only). Skill text loads on demand. |
| 🟩 | **Reach** | Main session only (certain: no hooked event fires in a subagent) |
| 🟨 | **Leaves state** | Compaction counts in the queue roster; a session-ended note in the machine's own state; queue commits on a queue branch. Its lib code also writes under the repo for queue, pair and hike records. |
| 🟨 | **Live surface** | The `meow` command, git pushes of queue branches, launcher scripts under `tools/` (ssh, tmux, cloud sessions). No MCP servers. |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 25 skill sections, 3 rules |

Hook notes: all three hooks call `bin/meow _hook ...`, which the inventory could not trace, so I read `hooks/claude.json`, `hooks/claude-codex.json` and `lib/cat_herder/hooks.py` by hand. PreCompact (auto only) records a compaction, SessionStart (compact only) prints one line, SessionEnd notes the ended session. Timeouts are 20, 10 and 5 seconds.

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **0** | none |
| 🔁 | **already covered** | **4** | ⬜⬜⬜⬜ |
| 🆕 | **new, standing rule** | **3** | 🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **0** | none |
| 🗑️ | **dropped** (persona, extras, no value) | **8** | ⬛⬛⬛⬛⬛⬛⬛⬛ |

Skills kept: 25 of 33 units. Computed verdict: INSTALL; I agree with it.

## ⛔ Conflicts: 0
| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| | none found | | | |

One near miss, judged not a conflict. `skills/herd/SKILL.md` ("Herd") starts a reviewer on opus by default and passes `--model` on the plugin's own session start. `examples/reader/rules/engineering.md` rule 6 governs the dispatch call for a subagent. A reviewer session the plugin launches is a different situation, and the plugin yields to a model the owner names.

## 🔁 Already covered: 4
| its rule | covered by | held in |
|---|---|---|
| `skills/capture/SKILL.md` "An interruption, so keep it short": split into pieces that "cover exactly what was asked, nothing added" | rule 4, "The scope I asked for is the deliverable." Chosen because it states the scope rule on its own. | examples/reader/rules/engineering.md |
| `skills/herd/roles/reviewer.md` "When the item says rigor: build": revert the change and watch the test fail | rule 3, "A test is not done until it has been seen to fail." | examples/reader/rules/engineering.md |
| `skills/queue/SKILL.md` "The queue": never queue-write to the code branch, and read back guessed irreversible commands | safety rules 2 and 5, "Never push to `main`" and "If a request is ambiguous and the wrong reading is costly, ask." | examples/reader/rules/safety.md |
| `skills/queue/SKILL.md` "Working the queue": "Never use `--force` on your own"; read back guessed irreversible commands | safety rules 1 and 5, the destructive-action go-ahead and the ask-when-ambiguous rule | examples/reader/rules/safety.md |

## 📥 Rules to copy: 3
| # | unit | the rule | kind |
|:--:|---|---|:--:|
| 1 | `skills/herd/roles/worker.md` "When the item says rigor: build" | "Never simplify away validation at a trust boundary, error handling that prevents data loss, or a security measure." The same section also says to stop only the processes you started, by PID, never by port. | 🆕 standing |
| 2 | `skills/queue/SKILL.md` "Staying reasonable" | "When a reply skips something you asked, don't take it as a yes or a no, and don't act on it." | 🆕 standing |
| 3 | `skills/herd/roles/reviewer.md` "Each review" | "A diff that both restructures code and changes behaviour, so you can't tell which lines do which, is a finding" | 🆕 standing |

## 🟩 Keep: 25
| # | skill section | kind | |
|:--:|---|:--:|:--:|
| 1 | `skills/capture/SKILL.md` Capture | skill | 🟩 |
| 2 | `skills/capture/SKILL.md` An interruption, so keep it short | skill | 🟩 |
| 3 | `skills/capture/SKILL.md` Asked to do work yourself | skill | 🟩 |
| 4 | `skills/capture/SKILL.md` Rescue session | skill | 🟩 |
| 5 | `skills/capture/SKILL.md` Stream-of-consciousness | skill | 🟩 |
| 6 | `skills/herd/SKILL.md` Herd | skill | 🟩 |
| 7 | `skills/herd/roles/associate.md` The associate | skill | 🟩 |
| 8 | `skills/herd/roles/handoff.md` Handing off to a new session | skill | 🟩 |
| 9 | `skills/herd/roles/handoff.md` If you're retiring | skill | 🟩 |
| 10 | `skills/herd/roles/handoff.md` If you're the one that stays | skill | 🟩 |
| 11 | `skills/herd/roles/handoff.md` If you're the new session | skill | 🟩 |
| 12 | `skills/herd/roles/handoff.md` In chat | skill | 🟩 |
| 13 | `skills/herd/roles/reviewer.md` (top) | skill | 🟩 |
| 14 | `skills/herd/roles/reviewer.md` Setting up | skill | 🟩 |
| 15 | `skills/herd/roles/reviewer.md` Each review | skill | 🟩 |
| 16 | `skills/herd/roles/reviewer.md` Limits | skill | 🟩 |
| 17 | `skills/herd/roles/reviewer.md` Who started you, and stopping | skill | 🟩 |
| 18 | `skills/herd/roles/reviewer.md` When the item says rigor: build | skill | 🟩 |
| 19 | `skills/herd/roles/worker.md` The worker, in a pair | skill | 🟩 |
| 20 | `skills/herd/roles/worker.md` When the item says rigor: build | skill | 🟩 |
| 21 | `skills/queue/SKILL.md` The queue | skill | 🟩 |
| 22 | `skills/queue/SKILL.md` Working the queue | skill | 🟩 |
| 23 | `skills/queue/SKILL.md` Telling the owner what another session said | skill | 🟩 |
| 24 | `skills/queue/SKILL.md` Staying reasonable | skill | 🟩 |
| 25 | `commands/meow` (top) | command | 🟩 |

These need the plugin's own `meow` tool. That is not a reason to drop them. None duplicates a skill in the sample reader, whose only skill is `examples/reader/skills/release-notes/SKILL.md`.

## 🗑️ Dropped
`u21` · `u22` · `u23` · `u24` · `u25` · `u26` · `u27` · `u31`

The first seven are `skills/herder/SKILL.md`, the cat voice persona. `u31` is a single example ledger bullet in `skills/queue/SKILL.md`.

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| PreCompact hook, `meow _hook precompact` | automatic compaction | no | 20 s timeout |
| SessionStart hook, `meow _hook sessionstart` | after a compaction, prints one line | no | 10 s timeout |
| SessionEnd hook, `meow _hook sessionend` | session close (Claude Code only) | no | 5 s timeout |
| `capture` skill | on demand | no | about 13,000 chars |
| `herd` skill and role files | on demand | no | about 49,600 chars |
| `herder` skill | on demand | no | about 5,600 chars |
| `queue` skill | on demand | no | about 26,000 chars |
| `/meow` command | when typed | no | about 1,200 chars |

## ✅ Do this
- ⬜ 1. Install the plugin if you want the queue, pairs and hikes, and leave `herder` unused.
- ⬜ 2. Copy the three rules below into your own rules file, so they hold when no skill is loaded.
- ⬜ 3. Check that your host's `bin/meow` path in the hooks resolves before relying on compaction counts.

Case: the hooks inject almost nothing and never reach subagents, so the carrying cost is low and the plugin is worth installing as shipped.

## 📋 Proposed rules patch
Add to `examples/reader/rules/engineering.md`, which already holds the build rules, as items 8 to 10. The file numbers its rules, so keep that.

```
8. **Never simplify away safeguards.** Keep validation at trust boundaries, error handling that prevents data loss, and security measures. Stop only the processes you started, by PID, never by port.
9. **Silence is not consent.** When a reply skips something I asked, do not take it as a yes or a no, and do not act on it. Ask again, and carry on with what does not depend on the answer.
10. **Keep refactors apart from behaviour changes.** A diff that does both, so you cannot tell which lines do which, goes back to be split.
```

No skill proposals.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
