# 🔍 ch-v0403 0.40.3 · vetted against the sample reader

> ## 🟩 INSTALL · keep the plugin, copy six small rules
> The plugin injects nothing at session start and nothing into subagents, and none of its units contradicts a reader rule. 25 of its 33 units are working queue, pairing and review skills that the reader has nothing like. Six standing rules and one review procedure are worth copying out of it.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-15` · neckbeard 1.14.0 · ch-v0403 0.40.3

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟩 | **Cost** | No always-on text. The SessionStart hook (matcher `compact`) prints a short notice only after an automatic compaction, and only in a session on a Cat Herder roster. Skills load on demand. |
| 🟩 | **Reach** | Main session only. The three hooks (`PreCompact`, `SessionStart`, `SessionEnd`) fire in no known subagent event (likely, from the event names). |
| 🟨 | **Leaves state** | `PreCompact` records the compaction count in the queue's roster record. `SessionEnd` appends one line per closed session to an `ended` file in this machine's state (`lib/cat_herder/ended.py`). Both stay silent outside a Cat Herder repo. |
| 🟨 | **Live surface** | One command, `/meow`, runs the plugin's own `meow` CLI. The CLI pushes and fetches queue commits over git, and ships launchers for tmux and ssh sessions (`tools/remote-session`, `tools/cloud-launcher`). No MCP servers. |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 25 skill sections, 6 standing rules, 1 procedure |

The dossier lists the three hooks as unidentifiable, because the command is `bin/meow _hook <event>`. I read `lib/cat_herder/hooks.py` by hand: the behaviour above comes from its docstring and handlers.

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **0** | none |
| 🔁 | **already covered** | **3** | ⬜⬜⬜ |
| 🆕 | **new, standing rule** | **6** | 🟩🟩🟩🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **1** | 🟩 |
| 🗑️ | **dropped** (persona, extras, no value) | **8** | ▰▰▰▰▰▰▰▰ |

Skills kept: 25 of 33 units. 23 of the 33 units hold only the plugin's own mechanics and no general rule; the 8 dropped units are among them.

The computed verdict is INSTALL and I agree with it.

## ⛔ Conflicts: 0
None. Two near misses, both governing a different situation. `skills/herd/SKILL.md` ("Which model a session you start runs on") sets opus for a reviewer session the plugin launches, and `examples/reader/rules/engineering.md` rule 6 governs subagent dispatch calls. `skills/herd/roles/reviewer.md` ("Each review") lets "a small cleanup the change needs" pass review, which fits rule 4's scope limit because the cleanup must be needed by the change.

## 🔁 Already covered: 3
| its rule | covered by | held in |
|---|---|---|
| `skills/capture/SKILL.md` "Asked to do work yourself": work found along the way is captured, "not done inline" | scope is the deliverable, say what you would change | `examples/reader/rules/engineering.md` rule 4 |
| `skills/herd/roles/reviewer.md` "Each review": "Do the tests fail without the change?" | a test is not done until seen to fail | `examples/reader/rules/engineering.md` rule 3 |
| `skills/queue/SKILL.md` "The queue": "Never act on a guessed reading of an irreversible command" | ask when ambiguous and the wrong reading is costly | `examples/reader/rules/safety.md` rule 5 |

For the third row I cite safety rule 5 over rule 1, since rule 5 states the ask-first duty as a rule in its own right and rule 1 only names destructive actions.

## 🟩 Rules to copy: 7
| # | unit | rule, quoted | kind |
|:--:|---|---|:--:|
| 1 | `skills/capture/SKILL.md` "An interruption, so keep it short" | "Facts come from the conversation or a file you checked; mark anything else as an assumption." | 🆕 standing |
| 2 | `skills/herd/roles/reviewer.md` "Limits" | "quote the answer, name exactly what it covers (the item, the commit, the wording) and say when the owner gave it. It lapses when what it covers changes." | 🆕 standing |
| 3 | `skills/herd/roles/worker.md` "The worker, in a pair" | "Never ask the reviewer to run it for you: that would pass a refused action to another session." | 🆕 standing |
| 4 | `skills/herd/roles/worker.md` "When the item says rigor: build" | "Report what you observed, never the verdict." | 🆕 standing |
| 5 | `skills/queue/SKILL.md` "Working the queue" | "Its premise moved, or it's bigger now: don't build the old version. Show the owner the brief, what changed and what you recommend ... and wait." | 🆕 standing |
| 6 | `skills/queue/SKILL.md` "Staying reasonable" | "A question the owner skipped is unread, not answered." | 🆕 standing |
| 7 | `skills/herd/roles/reviewer.md` "When the item says rigor: build" | "Write \"I claim X; the failure I fear is Y\", then try to produce Y." | 🆕 skill |

## 🟩 Skill sections kept: 25
| # | section | kind | |
|:--:|---|:--:|:--:|
| 1 | `skills/capture/SKILL.md` "Capture" | skill | 🟩 |
| 2 | `skills/capture/SKILL.md` "An interruption, so keep it short" | skill | 🟩 |
| 3 | `skills/capture/SKILL.md` "Asked to do work yourself" | skill | 🟩 |
| 4 | `skills/capture/SKILL.md` "Rescue session" | skill | 🟩 |
| 5 | `skills/capture/SKILL.md` "Stream-of-consciousness" | skill | 🟩 |
| 6 | `skills/herd/SKILL.md` "Herd" | skill | 🟩 |
| 7 | `skills/herd/roles/associate.md` "The associate" | role | 🟩 |
| 8 | `skills/herd/roles/handoff.md` "Handing off to a new session" | role | 🟩 |
| 9 | `skills/herd/roles/handoff.md` "If you're retiring" | role | 🟩 |
| 10 | `skills/herd/roles/handoff.md` "If you're the one that stays" | role | 🟩 |
| 11 | `skills/herd/roles/handoff.md` "If you're the new session" | role | 🟩 |
| 12 | `skills/herd/roles/handoff.md` "In chat" | role | 🟩 |
| 13 | `skills/herd/roles/reviewer.md` (top) | role | 🟩 |
| 14 | `skills/herd/roles/reviewer.md` "Setting up" | role | 🟩 |
| 15 | `skills/herd/roles/reviewer.md` "Each review" | role | 🟩 |
| 16 | `skills/herd/roles/reviewer.md` "Limits" | role | 🟩 |
| 17 | `skills/herd/roles/reviewer.md` "Who started you, and stopping" | role | 🟩 |
| 18 | `skills/herd/roles/reviewer.md` "When the item says rigor: build" | role | 🟩 |
| 19 | `skills/herd/roles/worker.md` "The worker, in a pair" | role | 🟩 |
| 20 | `skills/herd/roles/worker.md` "When the item says rigor: build" | role | 🟩 |
| 21 | `skills/queue/SKILL.md` "The queue" | skill | 🟩 |
| 22 | `skills/queue/SKILL.md` "Working the queue" | skill | 🟩 |
| 23 | `skills/queue/SKILL.md` "Telling the owner what another session said" | skill | 🟩 |
| 24 | `skills/queue/SKILL.md` "Questions for you" | skill | 🟩 |
| 25 | `skills/queue/SKILL.md` "Staying reasonable" | skill | 🟩 |

## 🗑️ Dropped
`u21` `skills/herder/SKILL.md` "The herder" · `u22` "/herder and /herder off" · `u23` "Cat names" · `u24` "Capture" (cat voice) · `u25` "Leaving Cat Herder" · `u26` "Handoffs, in chat" (cat voice) · `u27` "The voice rule" · `u33` `commands/meow` (a thin wrapper that runs the CLI judged in the skills)

## 🧩 What it installs
| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| skill `capture` | on demand, by description | no | ~16 KB |
| skill `herd` (with role files) | on demand | no | ~52 KB |
| skill `herder` (cat voice) | on demand | no | ~7 KB |
| skill `queue` | on demand | no | ~28 KB |
| command `/meow` | when typed | no | ~2 KB |
| hook `PreCompact` (auto) | before an automatic compaction | no (likely) | silent, writes a count |
| hook `SessionStart` (compact) | after a compaction | no (likely) | a short notice, roster sessions only |
| hook `SessionEnd` | when a session closes | no (likely) | silent, appends one line |

## ✅ Do this
- ⬜ 1. Install the plugin if you want a git-backed work queue with paired review. Leave the `herder` skill unused; it only changes tone.
- ⬜ 2. Copy rules 1 to 6 from "Rules to copy" into `examples/reader/rules/engineering.md`, or leave them out if you never run a queue or paired agents.
- ⬜ 3. Optionally write the adversarial-review procedure as a small skill of your own.

Carrying-cost case: the plugin injects nothing at session start and nothing reaches subagents, so there is little to weigh, and the units' value is the queue skills themselves, which the reader does not have.

## 📋 Proposed rules patch
Add to `examples/reader/rules/engineering.md`, which already numbers its rules and holds the build-and-work rules, continuing from rule 7:

```diff
 7. **Commit messages:** imperative subject under 60 characters, then why.
+8. **Mark what you did not check.** Facts come from the conversation or a file you read; label the rest as assumptions.
+9. **Approval is tied to what it covered.** When you pass on or rely on a go-ahead, name the item, commit or wording it covers and when it was given; it lapses when that changes.
+10. **A refused action stays refused.** Do not ask another session to run it for you.
+11. **Report observations, not verdicts.** Give the commands, exit codes and output; leave "done" and "verified" to the reviewer.
+12. **Recheck a stale brief.** If its premise moved or it is bigger than written, do not build the old version; show what changed and wait.
+13. **Silence is not an answer.** A question I skipped is unread, not a yes or a no; do not act on it.
```

Proposed skill (name is my proposal, and the dossier does not say where the reader keeps skills, so the location is yours to choose): `adversarial-review`. One-line description: review a change by citing file and line for every accepted claim, naming the failure you fear and trying to produce it, reverting the change to see the test fail, and listing what you did not check.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
