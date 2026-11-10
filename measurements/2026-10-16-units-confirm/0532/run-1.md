# 🔍 ch-v0532 0.53.2 · vetted against the sample reader

> ## 🟧 INSTALL WITH CHANGES · keep the workflow skills, fix the model and retry wording
> Five of its 64 sections collide with two of the reader's rules, all of them about choosing a subagent model on the dispatch call or retrying a refused action. Nine sections hold a general rule or procedure worth copying, and 42 sections are workflow skills that work as shipped. Its three hooks run `meow`, whose behaviour could not be traced, so the cost per session is unknown.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-16` · neckbeard 1.14.0 · ch-v0532 0.53.2

## ⚡ At a glance

| | | |
|:--:|---|---|
| ❓ | **Cost** | Unknown: three hooks (`SessionStart`, `PreCompact`, `SessionEnd`) run `bin/meow _hook ...` and the dossier could not trace what they inject |
| 🟩 | **Reach** | Main session only (no hooked event is known to fire in a subagent) |
| 🟨 | **Leaves state** | Many code files match write patterns (queue commits, roster and supervisor files under the repo's `.git`); none traced outside a project |
| 🟨 | **Live surface** | The `meow` command, launchers for other hosts, and a supervisor process; no MCP servers declared |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 42 skill sections, plus 9 sections with a rule or procedure to copy |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **5** | 🟥🟥🟥🟥🟥 |
| 🔁 | **already covered** | **0** | none |
| 🆕 | **new, standing rule** | **7** | 🟩🟩🟩🟩🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **2** | 🟩🟩 |
| 🗑️ | **dropped** (persona, wrappers, no value) | **22** | ▰ ×22 |

Skills kept: 42 of 64 sections. Dropped: 22 sections (u36 to u44, u48, u53 to u64). A section can be both kept as a skill and counted once above for its general rule or conflict.

## ⛔ Conflicts: 5
| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| 1 | `skills/herd/roles/orchestrator.md` · The orchestrator: "send 3 or 4 new read-only subagents on `claude-haiku-5-5`" | Subagents run on the model their definition pins; ask it to leave the model to the definition | examples/reader/rules/engineering.md | ⛔ |
| 2 | `skills/herd/roles/reviewer.md` · Each review: "send your own swarm of read-only `claude-haiku-5-5` subagents" | Subagents run on the model their definition pins; ask it to leave the model to the definition | examples/reader/rules/engineering.md | ⛔ |
| 3 | `skills/herd/roles/reviewer.md` · Limits: "try the same action, on your own judgement" | Never run anything destructive without explicit go-ahead (ask for a limit: retry only if the action is not destructive) | examples/reader/rules/safety.md | ⛔ |
| 4 | `skills/herd/roles/worker.md` · The worker, in a pair: "Send 3 or 4 subagents on `claude-haiku-5-5`" | Subagents run on the model their definition pins (and the reviewer retry of a refused action runs against the destructive-action stop) | examples/reader/rules/engineering.md, examples/reader/rules/safety.md | ⛔ |
| 5 | `skills/queue/SKILL.md` · Working the queue: "the cheapest capable model your host offers" | Subagents run on the model their definition pins; ask it to leave the model to the definition | examples/reader/rules/engineering.md | ⛔ |

## 🔁 Already covered: 0
None: no unit's general rules were already stated by the reader.

## 🆕 Rules to copy: 9
| # | unit | kind | rule or procedure | why |
|:--:|---|:--:|---|---|
| 1 | `skills/herd/roles/auditor.md` · Hard rules | standing | "never `pkill` or `killall` by pattern: you could stop another auditor's run. Stop a process by the pid yo..." | A general rule for shared machines that the reader's rules do not state. |
| 2 | `skills/herd/roles/reviewer.md` · (top) | standing | "If a git fetch or push fails on authentication, stop and report the remote and the error. Never add a key..." | The reader's rules say nothing about auth failures or adding credentials. |
| 3 | `skills/herd/roles/reviewer.md` · Each review | standing | "Silence alone is not a hang when output is buffered, so never restart an expensive suite only because it..." | A general rule about long-running commands that the reader does not state. |
| 4 | `skills/herd/roles/reviewer.md` · Limits | standing | "you may change your mind on a new argument, never on insistence." | A general rule for holding a verdict under pushback; the reader has none. |
| 5 | `skills/herd/roles/reviewer.md` · When the item says rigor: build | standing | "was a criterion, a test or a threshold changed to make it pass? Read the test diff." | Reader rule 3 covers seeing a test fail, but not checking whether the test or criterion was loosened. |
| 6 | `skills/herd/roles/worker.md` · The worker, in a pair | standing | "If a git fetch or push fails on authentication, stop and report the remote and the error. Never add a key..." | Same auth rule as the reviewer role; the reader has nothing like it. |
| 7 | `skills/herd/roles/worker.md` · When the item says rigor: build | standing | "Report what you observed, never the verdict." | A general rule on reporting evidence; the reader asks for reasoning but not this separation. |
| 8 | `skills/herd/roles/auditor.md` · Method | skill | "List every checkable claim in the area: a command and its output, a flag, a default, a number, a "never"..." | A one-shot docs-audit procedure (list claims, run each, break the code, give BACKED/UNTESTED/CONTRADICTED) that does not need the plugin's tool. |
| 9 | `skills/herd/roles/readonly.md` · The reply of a session that can't write | skill | "Reply with a section headed `## Report`, exactly in this form, one entry each, writing `none` where nothi..." | A fixed report-plus-patch reply for a session that cannot write is a small standalone procedure. |

## 🟩 Keep: 42 skill sections
| # | section | kind | |
|:--:|---|:--:|:--:|
| 1 | `skills/capture/SKILL.md` · Capture | skill | 🟩 |
| 2 | `skills/capture/SKILL.md` · An interruption, so keep it short | skill | 🟩 |
| 3 | `skills/capture/SKILL.md` · Asked to do work yourself: every session, not only the worker | skill | 🟩 |
| 4 | `skills/capture/SKILL.md` · Rescue session: everything this session was tracking | skill | 🟩 |
| 5 | `skills/capture/SKILL.md` · Stream-of-consciousness: the owner is riffing | skill | 🟩 |
| 6 | `skills/capture/SKILL.md` · Prompt me: answering the open questions with a tap | skill | 🟩 |
| 7 | `skills/capture/sections/prompt-me.md` · Prompt me: answering the open questions with a tap (the rest) | skill | 🟩 |
| 8 | `skills/herd/SKILL.md` · Herd | skill | 🟩 |
| 9 | `skills/herd/roles/associate.md` · The associate | skill | 🟩 |
| 10 | `skills/herd/roles/auditor.md` · The auditor | skill | 🟩 |
| 11 | `skills/herd/roles/auditor.md` · Method | skill | 🟩 |
| 12 | `skills/herd/roles/auditor.md` · Findings | skill | 🟩 |
| 13 | `skills/herd/roles/auditor.md` · Hard rules | skill | 🟩 |
| 14 | `skills/herd/roles/auditor.md` · Prompt hygiene | skill | 🟩 |
| 15 | `skills/herd/roles/auditor.md` · Report | skill | 🟩 |
| 16 | `skills/herd/roles/auditor.md` · The coordinator's checklist | skill | 🟩 |
| 17 | `skills/herd/roles/auditor.md` · A falsify item | skill | 🟩 |
| 18 | `skills/herd/roles/bond.md` · A bond: you and {{WORKER_NAME}} review each other | skill | 🟩 |
| 19 | `skills/herd/roles/handoff.md` · Handing off to a new session | skill | 🟩 |
| 20 | `skills/herd/roles/handoff.md` · If you're retiring | skill | 🟩 |
| 21 | `skills/herd/roles/handoff.md` · If you're the one that stays | skill | 🟩 |
| 22 | `skills/herd/roles/handoff.md` · If you're the new session | skill | 🟩 |
| 23 | `skills/herd/roles/handoff.md` · In chat | skill | 🟩 |
| 24 | `skills/herd/roles/orchestrator.md` · The orchestrator | skill | 🟩 |
| 25 | `skills/herd/roles/readonly.md` · The reply of a session that can't write | skill | 🟩 |
| 26 | `skills/herd/roles/reviewer.md` · (top) | skill | 🟩 |
| 27 | `skills/herd/roles/reviewer.md` · Setting up (once, when this pair starts) | skill | 🟩 |
| 28 | `skills/herd/roles/reviewer.md` · Each review | skill | 🟩 |
| 29 | `skills/herd/roles/reviewer.md` · Limits | skill | 🟩 |
| 30 | `skills/herd/roles/reviewer.md` · Who started you, and stopping | skill | 🟩 |
| 31 | `skills/herd/roles/reviewer.md` · When the item says rigor: build | skill | 🟩 |
| 32 | `skills/herd/roles/worker.md` · The worker, in a pair | skill | 🟩 |
| 33 | `skills/herd/roles/worker.md` · When the item says rigor: build | skill | 🟩 |
| 34 | `skills/herd/sections/launch-refused.md` · A launch is refused | skill | 🟩 |
| 35 | `skills/herd/sections/orchestrator.md` · The orchestrator at a run's end, and in cloud runs | skill | 🟩 |
| 36 | `skills/queue/SKILL.md` · The queue | skill | 🟩 |
| 37 | `skills/queue/SKILL.md` · Working the queue | skill | 🟩 |
| 38 | `skills/queue/SKILL.md` · Telling the owner what another session said | skill | 🟩 |
| 39 | `skills/queue/SKILL.md` · Staying reasonable | skill | 🟩 |
| 40 | `skills/queue/sections/asks.md` · Asking the owner to do something | skill | 🟩 |
| 41 | `skills/queue/sections/field-trip.md` · Field Trip, and reading the owner as voice | skill | 🟩 |
| 42 | `skills/queue/sections/setup.md` · Setting up a queue | skill | 🟩 |

## 🗑️ Dropped
`u36` · `u37` · `u38` · `u39` · `u40` · `u41` · `u42` · `u43` · `u44` · `u48` · `u53` · `u54` · `u55` · `u56` · `u57` · `u58` · `u59` · `u60` · `u61` · `u62` · `u63` · `u64`

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| 4 skills (`capture`, `herd`, `herder`, `queue`) | on demand | no | 76 KB |
| 12 commands | when typed | no | 4.8 KB |
| 3 hooks (`SessionStart`, `PreCompact`, `SessionEnd`) | session start, before auto-compaction, session end | no known path | unknown |
| `bin/meow` and `tools/` | when run | no | not sized |

## ✅ Do this
- ⬜ 1. Install it only if you want the queue and pair workflow, and ask the owner to change the `claude-haiku-5-5` dispatch wording and the retry-a-refused-action sentences first.
- ⬜ 2. Read the three `meow _hook` handlers by hand before enabling, since their output is unknown.
- ⬜ 3. Copy the six distinct standing rules (seven units, the authentication rule appears twice) and two procedures below whether or not you install.

Carrying-cost case: the hooks have unknown behaviour, so the cost is not measurable here; the plugin keeps many skills of its own, so it is more than a rule copy.

## 📋 Proposed rules patch
Add to `examples/reader/rules/engineering.md` (it holds how the reader builds and works; the section is short, so the rules stay inline):

```diff
+8. **Authentication failures stop work.** If a fetch or push fails on authentication, stop and report the remote and the error. Never add a key, a token, an https remote or a forwarded agent to get past it.
+9. **Quiet is not hung.** Silence alone is not a hang when output is buffered; never restart an expensive suite only because it is quiet.
+10. **Report what you observed, never the verdict.** Give the test command, its exit code and its raw output; the reviewer decides.
+11. **Check that a test or criterion was not loosened to pass.** Read the test diff.
+12. **Hold a verdict under pushback.** Change it on a new argument, never on insistence.
+13. **Stop a process by the pid you started.** Never `pkill` or `killall` by pattern.
```

Two on-demand skills, names are my proposal, location left to the reader since the dossier names none: `claim-audit` (list every checkable claim in a doc, run each, break the code it rests on, give each a BACKED, UNTESTED, CONTRADICTED or UNTESTABLE verdict) and `readonly-report` (the fixed `## Report` reply with a `git format-patch` against one named base, for a session that cannot write).

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
