# 🔍 ch-v0532 0.53.2 · vetted against the sample reader

> ## 🟧 INSTALL WITH CHANGES · keep the skills, drop four model pins, copy eight rules
> It adds three lifecycle hooks that say nothing outside a repo with a queue, and 43 skill sections that work as shipped but need its own `meow` tool. Four sections name the model for a subagent, which the reader's rules forbid. Eight general rules and one procedure are worth copying even if the plugin is not kept.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-15` · neckbeard 1.14.0 · ch-v0532 0.53.2

## ⚡ At a glance

| | | |
|:--:|---|---|
| ❓ | **Cost** | Three hooks (SessionStart on startup, resume and compact; PreCompact on auto; SessionEnd). The dossier could not identify any of the three commands, so I read `lib/cat_herder/hooks.py`: SessionStart prints a roster role, a compaction count and the repo's rules and recorded answers, only where a queue exists, and nothing elsewhere. Bytes not measured. |
| 🟩 | **Reach** | Main session only (likely): no event it hooks is known to fire in a subagent. |
| 🟨 | **Leaves state** | SessionEnd appends to an `ended` record in a per-machine state directory (`lib/cat_herder/ended.py`); `meow` keeps roster and queue state, and many library files are flagged as write candidates. |
| 🟨 | **Live surface** | No MCP servers. `bin/meow` runs git, and the launchers it documents use ssh, tmux and cloud sessions. |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 8 standing rules, 1 skill, and 43 skill sections |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **4** | 🟥🟥🟥🟥 |
| 🔁 | **already covered** | **2** | ⬜⬜ |
| 🆕 | **new, standing rule** | **8** | 🟩🟩🟩🟩🟩🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **1** | 🟩 |
| 🟩 | **skill sections kept** | **43** | 🟩 ×43 |
| 🗑️ | **dropped** (persona, wrappers, no value) | **21** | ⬛ ×21 |

The other 49 of 64 units hold no general rule, only the plugin's own mechanics. They sit in the kept and dropped grids below.

## ⛔ Conflicts: 4
| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| u24 | `skills/herd/roles/orchestrator.md` "The orchestrator": "send 3 or 4 new read-only subagents on `claude-haiku-5-5`" | Rule 6: do not override a subagent's pinned model on the dispatch call. The unit names the model on the dispatch. | examples/reader/rules/engineering.md | ⛔ |
| u28 | `skills/herd/roles/reviewer.md` "Each review": "send your own swarm of read-only `claude-haiku-5-5` subagents" | Same rule 6, same situation: a subagent dispatch with a model named. | examples/reader/rules/engineering.md | ⛔ |
| u32 | `skills/herd/roles/worker.md` "The worker, in a pair": "Send 3 or 4 subagents on `claude-haiku-5-5`" | Same rule 6, same situation. | examples/reader/rules/engineering.md | ⛔ |
| u46 | `skills/queue/SKILL.md` "Working the queue": "agents on the cheapest capable model your host offers" | Same rule 6: it picks the model when dispatching groom scans. | examples/reader/rules/engineering.md | ⛔ |

The same unit u24 also tells the orchestrator to pass `claude-fable-5-1` when starting an advisor thread. A thread is a session the plugin starts, not a subagent dispatch, so I count it as no conflict. Likewise u8's default of opus for a reviewer it starts governs a session start, not a dispatch.

## 🔁 Already covered: 2
| its rule | covered by | held in |
|---|---|---|
| u3 `skills/capture/SKILL.md` "Asked to do work yourself": work found along the way is queued, "not done inline" | Rule 4, the scope asked for is the deliverable. I chose it because it states the scope limit as a rule in its own right. | examples/reader/rules/engineering.md |
| u31 `skills/herd/roles/reviewer.md` "When the item says rigor: build": revert the change and "watch the test fail" | Rule 3, a test is not done until seen to fail. Its pid rule is counted at u13. | examples/reader/rules/engineering.md |

## 🟩 Keep: 9 rules to copy, 43 skill sections

Rules to copy (9), whatever the verdict:

| # | unit | rule | kind |
|:--:|---|---|:--:|
| u7 | `skills/capture/sections/prompt-me.md` "Prompt me: answering the open questions with a tap (the rest)" | "Read each answer back in text and ask the owner to confirm" after an interrupted prompt, since the answers "may be the recommended ones" | 🆕 standing |
| u13 | `skills/herd/roles/auditor.md` "Hard rules" | "never `pkill` or `killall` by pattern ... Stop a process by the pid you started" | 🆕 standing |
| u26 | `skills/herd/roles/reviewer.md` "(top)" | on an authentication failure, "stop and report", and "Never add a key, a token, an https remote or a forwarded agent to get past it" | 🆕 standing |
| u29 | `skills/herd/roles/reviewer.md` "Limits" | a relayed approval must "name exactly what it covers" and "lapses when what it covers changes" | 🆕 standing |
| u33 | `skills/herd/roles/worker.md` "When the item says rigor: build" | "Never simplify away validation at a trust boundary, error handling that prevents data loss, or a security measure" | 🆕 standing |
| u49 | `skills/queue/SKILL.md` "Staying reasonable" | a skipped question is "unread, not answered": "don't take it as a yes or a no, and don't act on it" | 🆕 standing |
| u50 | `skills/queue/sections/asks.md` "Asking the owner to do something" | what to run "sits alone in a code block ... with no placeholder left for the owner to fill" | 🆕 standing |
| u51 | `skills/queue/sections/field-trip.md` "Field Trip, and reading the owner as voice" | "Never act on a guessed reading of an irreversible command": read it back and "wait for a yes" | 🆕 standing |
| u11 | `skills/herd/roles/auditor.md` "Method" | list each checkable claim in a doc, run its example, break the code behind it, and give one verdict word: BACKED, UNTESTED, CONTRADICTED or UNTESTABLE | 🆕 skill |

Skill sections kept (43), each part of one of the plugin's skills and working as shipped with `meow`:

| # | unit | kind |
|:--:|---|:--:|
| u1 | `skills/capture/SKILL.md` "Capture" | skill |
| u2 | `skills/capture/SKILL.md` "An interruption, so keep it short" | skill |
| u3 | `skills/capture/SKILL.md` "Asked to do work yourself: every session, not only the worker" | skill |
| u4 | `skills/capture/SKILL.md` "Rescue session: everything this session was tracking" | skill |
| u5 | `skills/capture/SKILL.md` "Stream-of-consciousness: the owner is riffing" | skill |
| u6 | `skills/capture/SKILL.md` "Prompt me: answering the open questions with a tap" | skill |
| u7 | `skills/capture/sections/prompt-me.md` "Prompt me: answering the open questions with a tap (the rest)" | skill |
| u8 | `skills/herd/SKILL.md` "Herd" | skill |
| u9 | `skills/herd/roles/associate.md` "The associate" | skill |
| u10 | `skills/herd/roles/auditor.md` "The auditor" | skill |
| u11 | `skills/herd/roles/auditor.md` "Method" | skill |
| u12 | `skills/herd/roles/auditor.md` "Findings" | skill |
| u13 | `skills/herd/roles/auditor.md` "Hard rules" | skill |
| u14 | `skills/herd/roles/auditor.md` "Prompt hygiene" | skill |
| u15 | `skills/herd/roles/auditor.md` "Report" | skill |
| u16 | `skills/herd/roles/auditor.md` "The coordinator's checklist" | skill |
| u17 | `skills/herd/roles/auditor.md` "A falsify item" | skill |
| u18 | `skills/herd/roles/bond.md` "A bond: you and {{WORKER_NAME}} review each other" | skill |
| u19 | `skills/herd/roles/handoff.md` "Handing off to a new session" | skill |
| u20 | `skills/herd/roles/handoff.md` "If you're retiring" | skill |
| u21 | `skills/herd/roles/handoff.md` "If you're the one that stays" | skill |
| u22 | `skills/herd/roles/handoff.md` "If you're the new session" | skill |
| u23 | `skills/herd/roles/handoff.md` "In chat" | skill |
| u24 | `skills/herd/roles/orchestrator.md` "The orchestrator" (⛔ with its model pin) | skill |
| u25 | `skills/herd/roles/readonly.md` "The reply of a session that can't write" | skill |
| u26 | `skills/herd/roles/reviewer.md` "(top)" | skill |
| u27 | `skills/herd/roles/reviewer.md` "Setting up (once, when this pair starts)" | skill |
| u28 | `skills/herd/roles/reviewer.md` "Each review" (⛔ with its model pin) | skill |
| u29 | `skills/herd/roles/reviewer.md` "Limits" | skill |
| u30 | `skills/herd/roles/reviewer.md` "Who started you, and stopping" | skill |
| u31 | `skills/herd/roles/reviewer.md` "When the item says rigor: build" | skill |
| u32 | `skills/herd/roles/worker.md` "The worker, in a pair" (⛔ with its model pin) | skill |
| u33 | `skills/herd/roles/worker.md` "When the item says rigor: build" | skill |
| u34 | `skills/herd/sections/launch-refused.md` "A launch is refused" | skill |
| u35 | `skills/herd/sections/orchestrator.md` "The orchestrator at a run's end, and in cloud runs" | skill |
| u45 | `skills/queue/SKILL.md` "The queue" | skill |
| u46 | `skills/queue/SKILL.md` "Working the queue" (⛔ with its model pin) | skill |
| u47 | `skills/queue/SKILL.md` "Telling the owner what another session said" | skill |
| u49 | `skills/queue/SKILL.md` "Staying reasonable" | skill |
| u50 | `skills/queue/sections/asks.md` "Asking the owner to do something" | skill |
| u51 | `skills/queue/sections/field-trip.md` "Field Trip, and reading the owner as voice" | skill |
| u52 | `skills/queue/sections/setup.md` "Setting up a queue" | skill |
| u57 | `commands/meow.md` "(top)", the `/meow` command | skill |

## 🗑️ Dropped
`u36` · `u37` · `u38` · `u39` · `u40` · `u41` · `u42` · `u43` · `u44` (the cat voice, persona) · `u48` (one example bullet) · `u53` · `u54` · `u55` · `u56` · `u58` · `u59` · `u60` · `u61` · `u62` · `u63` · `u64` (commands that only call a skill or one `meow` command judged elsewhere)

## 🧩 What it installs
| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| `skills/herd` (SKILL.md, roles, sections) | on demand, when the skill loads | no | 103,344 chars judged |
| `skills/queue` | on demand | no | 35,953 chars judged |
| `skills/capture` | on demand, and by trigger words | no | 19,968 chars judged |
| `skills/herder` (cat voice) | on demand | no | 7,075 chars judged |
| 12 commands in `commands/` | when typed | no | 3,366 chars judged for 12 |
| SessionStart hook | startup, resume, compact | no (likely) | not measured; silent without a queue |
| PreCompact hook (auto) | before an automatic compaction | no (likely) | counts the compaction; silent, exit 0 |
| SessionEnd hook | session close | no (likely) | writes one line to the machine's `ended` record |
| `rules/cat-herder.mdc`, `hooks/antigravity.json`, `hooks/cursor.json` | other hosts, not Claude Code | n/a | not judged: no unit |

## ✅ Do this
- ⬜ 1. Copy the eight standing rules in the patch below, and the one skill, into your own files.
- ⬜ 2. If you install the plugin, treat the four model pins (u24, u28, u32, u46) as void: your engineering rule 6 wins, and the plugin's workers, reviewers and orchestrator would otherwise break it every round.
- ⬜ 3. Install only for a repo where you will run a `meow` queue; the skills do nothing useful without it.
- ⬜ 4. Run it once with `--plugin-dir` and watch SessionStart in a repo with a queue, since its output was read from source, not measured.

Carrying-cost case: the plugin has hooks, but they inject only inside a repo with a queue, and nine rules survive, so this is not the one-rule trade. The cost is small and conditional, and the real price is the four conflicts and the dependence on `meow`.

## 📋 Proposed rules patch

I disagree with nothing in the computed verdict.

Put the first five in `examples/reader/rules/safety.md`, which already numbers hard stops (rules 1 to 5); the sixth and seventh in `examples/reader/rules/engineering.md` after rule 7; the last one in `examples/reader/CLAUDE.md` under "How I like answers". Wording is mine, not the plugin's.

```diff
 # examples/reader/rules/safety.md
+6. **If a git fetch or push fails on authentication, stop and report the
+   remote and the error.** Never add a key, a token, an https remote or a
+   forwarded agent to get past it.
+7. **A command you only heard, not read, is not a go-ahead.** If any part of a
+   destructive or irreversible instruction was matched by sound or by guess,
+   read the exact command back and wait for a yes.
+8. **An approval covers what it named.** When you pass on my answer, say what it
+   covers and when I gave it. It lapses when that changes.
+9. **A question I skipped is unanswered.** Do not take silence as a yes or a no,
+   and do not act on it; ask again.
+10. **If a prompt was interrupted, or came back without my visibly choosing,
+    read the answers back and confirm before acting on them.** They may be
+    defaults.
```

```diff
 # examples/reader/rules/engineering.md
+8. **Never simplify away** validation at a trust boundary, error handling that
+   prevents data loss, or a security measure.
+9. **Stop only the processes you started**, by pid. Never `pkill` or `killall`
+   by pattern, and never stop one by port.
```

```diff
 # examples/reader/CLAUDE.md  (How I like answers)
+- When I must run something, put it alone in a code block, exactly as I should
+  paste it, with no placeholder left for me to fill.
```

Proposed skill (the name is my proposal, the plugin does not name it): `audit-doc-claims`, "Check a doc or help page claim by claim: run each example, break the code it depends on, and give each claim one verdict, BACKED, UNTESTED, CONTRADICTED or UNTESTABLE." The dossier shows the reader keeps skills in `examples/reader/skills/`, beside `release-notes`.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
