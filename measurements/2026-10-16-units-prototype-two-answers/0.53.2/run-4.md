# 🔍 ch-v0532 0.53.2 · vetted against the sample reader

> ## 🟧 INSTALL WITH CHANGES · drop the swarm model names, copy four rules
> Cat Herder is a git-backed work queue with a worker, reviewer and orchestrator loop. Its skills work as shipped and the reader has nothing like them, but three role sections name a model on subagent dispatch, which the reader forbids. Four general rules are worth copying whether or not the plugin is installed.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-15` · neckbeard 1.14.0 · ch-v0532 0.53.2

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟨 | **Cost** | Three hooks in `hooks/claude.json`. SessionStart prints a few lines (roster role, compaction count, the repo's rules block) only in a repo that has a queue and nothing elsewhere. Byte size not measured: the dossier could not trace the three commands, so I read `lib/cat_herder/hooks.py` by hand. |
| 🟩 | **Reach** | Main session only (certain: none of the three events fires in a subagent) |
| 🟨 | **Leaves state** | PreCompact writes a compaction count to the session's roster record in the queue; SessionEnd records the close in this machine's state (`lib/cat_herder/ended.py`); the queue itself is commits in the repo |
| 🟨 | **Live surface** | No MCP servers. The `meow` CLI runs git fetch and push over ssh or https to the queue remote; hooks cap the ssh wait at 15 seconds |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 4 rules to copy, 43 skill sections |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **3** | 🟥🟥🟥 |
| 🔁 | **already covered** | **1** | ⬜ |
| 🆕 | **new, standing rule** | **3** | 🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **1** | 🟩 |
| ➖ | **nothing general** (the plugin's own mechanics) | **56** | ▰ ×56 |
| 🟩 | **skill sections kept** (a separate answer, on its own axis) | **43** | ▰ ×43 |
| 🗑️ | **units dropped** (persona, wrappers) | **21** | ▰ ×21 |

The 64 units each get one rules answer (3 + 1 + 3 + 1 + 56 = 64) and one skill answer (43 kept + 21 dropped = 64).

## ⛔ Conflicts: 3
| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| 1 | "send 3 or 4 new read-only subagents on `claude-haiku-5-5`" | Rule 6, "Do not override it on the dispatch call" | `examples/reader/rules/engineering.md` | 🟥 |
| 2 | "send your own swarm of read-only `claude-haiku-5-5` subagents" | Rule 6, "Do not override it on the dispatch call" | `examples/reader/rules/engineering.md` | 🟥 |
| 3 | "Send 3 or 4 subagents on `claude-haiku-5-5`, one lens each" | Rule 6, "Do not override it on the dispatch call" | `examples/reader/rules/engineering.md` | 🟥 |

Both sides govern a subagent dispatch. Cat Herder's `--model` default for sessions it starts (herd skill) is a session start, not a dispatch, and is not counted.

## 🔁 Already covered: 1
| its rule | covered by | held in |
|---|---|---|
| `skills/herd/roles/reviewer.md` · When the item says rigor: build: "watch the test fail" after reverting the change | Rule 3, "seen to fail" | `examples/reader/rules/engineering.md` |

## 🟩 Rules to copy: 4
| # | unit | rule, quoted | kind | |
|:--:|---|---|:--:|:--:|
| 1 | `skills/herd/roles/worker.md` · When the item says rigor: build | "Never simplify away validation at a trust boundary" | 🆕 standing | 🟩 |
| 2 | `skills/herd/roles/reviewer.md` · (top) | "Never add a key, a token, an https remote or a forwarded agent" to get past a failed git login | 🆕 standing | 🟩 |
| 3 | `skills/herd/roles/auditor.md` · Hard rules | "never `pkill` or `killall` by pattern"; stop a process by the pid you started | 🆕 standing | 🟩 |
| 4 | `skills/herd/roles/auditor.md` · Method | claim-by-claim audit with verdict words BACKED, UNTESTED, CONTRADICTED, UNTESTABLE | 🆕 skill | 🟩 |

## 🟩 Skill sections kept: 43
| # | unit | |
|:--:|---|:--:|
| 1 | u1: `skills/capture/SKILL.md` · Capture | 🟩 |
| 2 | u2: `skills/capture/SKILL.md` · An interruption, so keep it short | 🟩 |
| 3 | u3: `skills/capture/SKILL.md` · Asked to do work yourself: every session, not only the worker | 🟩 |
| 4 | u4: `skills/capture/SKILL.md` · Rescue session: everything this session was tracking | 🟩 |
| 5 | u5: `skills/capture/SKILL.md` · Stream-of-consciousness: the owner is riffing | 🟩 |
| 6 | u6: `skills/capture/SKILL.md` · Prompt me: answering the open questions with a tap | 🟩 |
| 7 | u7: `skills/capture/sections/prompt-me.md` · Prompt me: answering the open questions with a tap (the rest) | 🟩 |
| 8 | u8: `skills/herd/SKILL.md` · Herd | 🟩 |
| 9 | u9: `skills/herd/roles/associate.md` · The associate | 🟩 |
| 10 | u10: `skills/herd/roles/auditor.md` · The auditor | 🟩 |
| 11 | u11: `skills/herd/roles/auditor.md` · Method | 🟩 |
| 12 | u12: `skills/herd/roles/auditor.md` · Findings | 🟩 |
| 13 | u13: `skills/herd/roles/auditor.md` · Hard rules | 🟩 |
| 14 | u14: `skills/herd/roles/auditor.md` · Prompt hygiene | 🟩 |
| 15 | u15: `skills/herd/roles/auditor.md` · Report | 🟩 |
| 16 | u16: `skills/herd/roles/auditor.md` · The coordinator's checklist | 🟩 |
| 17 | u17: `skills/herd/roles/auditor.md` · A falsify item | 🟩 |
| 18 | u18: `skills/herd/roles/bond.md` · A bond: you and {{WORKER_NAME}} review each other | 🟩 |
| 19 | u19: `skills/herd/roles/handoff.md` · Handing off to a new session | 🟩 |
| 20 | u20: `skills/herd/roles/handoff.md` · If you're retiring | 🟩 |
| 21 | u21: `skills/herd/roles/handoff.md` · If you're the one that stays | 🟩 |
| 22 | u22: `skills/herd/roles/handoff.md` · If you're the new session | 🟩 |
| 23 | u23: `skills/herd/roles/handoff.md` · In chat | 🟩 |
| 24 | u24: `skills/herd/roles/orchestrator.md` · The orchestrator | 🟩 |
| 25 | u25: `skills/herd/roles/readonly.md` · The reply of a session that can't write | 🟩 |
| 26 | u26: `skills/herd/roles/reviewer.md` · (top) | 🟩 |
| 27 | u27: `skills/herd/roles/reviewer.md` · Setting up (once, when this pair starts) | 🟩 |
| 28 | u28: `skills/herd/roles/reviewer.md` · Each review | 🟩 |
| 29 | u29: `skills/herd/roles/reviewer.md` · Limits | 🟩 |
| 30 | u30: `skills/herd/roles/reviewer.md` · Who started you, and stopping | 🟩 |
| 31 | u31: `skills/herd/roles/reviewer.md` · When the item says rigor: build | 🟩 |
| 32 | u32: `skills/herd/roles/worker.md` · The worker, in a pair | 🟩 |
| 33 | u33: `skills/herd/roles/worker.md` · When the item says rigor: build | 🟩 |
| 34 | u34: `skills/herd/sections/launch-refused.md` · A launch is refused | 🟩 |
| 35 | u35: `skills/herd/sections/orchestrator.md` · The orchestrator at a run's end, and in cloud runs | 🟩 |
| 36 | u45: `skills/queue/SKILL.md` · The queue | 🟩 |
| 37 | u46: `skills/queue/SKILL.md` · Working the queue | 🟩 |
| 38 | u47: `skills/queue/SKILL.md` · Telling the owner what another session said | 🟩 |
| 39 | u48: `skills/queue/SKILL.md` · Questions for you | 🟩 |
| 40 | u49: `skills/queue/SKILL.md` · Staying reasonable | 🟩 |
| 41 | u50: `skills/queue/sections/asks.md` · Asking the owner to do something | 🟩 |
| 42 | u51: `skills/queue/sections/field-trip.md` · Field Trip, and reading the owner as voice | 🟩 |
| 43 | u52: `skills/queue/sections/setup.md` · Setting up a queue | 🟩 |

## 🗑️ Dropped: 21
`u36` · `u37` · `u38` · `u39` · `u40` · `u41` · `u42` · `u43` · `u44` · `u53` · `u54` · `u55` · `u56` · `u57` · `u58` · `u59` · `u60` · `u61` · `u62` · `u63` · `u64`

`u36` to `u44` are the cat-name voice (persona). `u53` to `u64` are slash commands that only wrap the skills or the `meow` CLI.

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| 4 skills (capture, herd, herder, queue) with their role and section files | on demand | no | 52 units, about 100 KB of text |
| 12 slash commands in `commands/` | when typed | no | small |
| SessionStart hook | startup, resume, compact | no | a few lines, queue repos only |
| PreCompact hook | automatic compaction | no | writes a count, prints only on failure |
| SessionEnd hook | session close | no | silent, local state |
| `rules/cat-herder.mdc` (Cursor routing) | not loaded by Claude Code | no | not judged |

## ✅ Do this
- ⬜ 1. Install it, then replace the three `claude-haiku-5-5` dispatch lines (`skills/herd/roles/orchestrator.md`, `skills/herd/roles/reviewer.md`, `skills/herd/roles/worker.md`) with an unpinned dispatch, or keep a local patch, so rule 6 holds.
- ⬜ 2. Copy the three standing rules below into the reader's rule files.
- ⬜ 3. Optionally write the claim-audit skill below.
Carrying-cost case: the plugin has hooks but they stay in the main session and print only in a repo with a queue. It carries four rules the reader would not write for itself, and 43 skill sections the reader lacks, so installing beats copying.

## 📋 Proposed rules patch
Add to `examples/reader/rules/engineering.md` after rule 7 (it numbers its rules, so these continue the list):

```diff
+8. **Never simplify away validation at a trust boundary,** error handling that prevents data loss, or a security measure.
+9. **Stop a process only by the pid you started.** Never `pkill` or `killall` by pattern.
```

Add to `examples/reader/rules/safety.md` after rule 5, since it is a hard stop:

```diff
+6. **If a git fetch or push fails on authentication, stop and report the remote and the error.** Never add a key, a token, an https remote or a forwarded agent to get past it.
```

Proposed skill (name is my proposal): `audit-claims`, "Check each claim a doc or help text makes against the code: run the example, find the test, break the code, and give each claim one verdict word (backed, untested, contradicted, untestable)." The dossier shows the reader keeps skills in `skills/<name>/SKILL.md` under its config folder, so that is where it would go.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
