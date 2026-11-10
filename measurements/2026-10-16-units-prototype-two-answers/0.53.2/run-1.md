# 🔍 ch-v0532 0.53.2 · vetted against the sample reader

> ## 🟧 INSTALL WITH CHANGES · keep the queue, herd and capture workflow, skip the subagent model names
> Three hooks that stay silent outside a git repo with a queue, main session only, and 43 of 64 instruction sections that work as shipped and do things the reader's rules and skills do not. Five sections collide with the reader: four name a model on a subagent call, and one lets a reviewer retry an action another session was refused. Eight more are worth copying as the reader's own: seven standing rules and one audit procedure.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-15` · neckbeard 1.14.0 · ch-v0532 0.53.2

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟩 | **Cost** | Nothing outside a git repo with a queue. In one, SessionStart prints the repo's rules and recorded answers, and for a rostered session its role and compaction count (lib/cat_herder/hooks.py). The four skill descriptions and 12 command names sit in context always; the 76,072 bytes of SKILL.md load on demand. |
| 🟩 | **Reach** | Main session only (no hooked event fires in a subagent) |
| 🟨 | **Leaves state** | PreCompact writes a compaction count to the queue as a commit and pushes it, only for a session on the roster. SessionEnd records the close in this machine's state (lib/cat_herder/ended.py). Skills create and push queue commits, item branches and worktrees when used. |
| 🟨 | **Live surface** | No MCP server. A compaction in a rostered session runs git fetch and push against the queue remote (15 second deadline). The tools/*-launcher scripts start other sessions over ssh, tmux or the cloud when asked. |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 43 sections of 3 skills and 1 command, 7 standing rules, 1 skill to write |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **5** | 🟥🟥🟥🟥🟥 |
| 🔁 | **already covered** | **6** | ⬜⬜⬜⬜⬜⬜ |
| 🆕 | **new, standing rule** | **7** | 🟩🟩🟩🟩🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **1** | 🟩 |
| ✅ | **skills kept** (sections that work as shipped) | **43** | ▰ ×43 |
| 🗑️ | **dropped** (persona, wrappers, no value) | **21** | ▰ ×21 |

Of the 64 sections, 45 hold only the plugin's own mechanics for the rules question, and 24 of those are kept as skill text. A section can be kept and also appear under conflicts or rules to copy.

## ⛔ Conflicts: 5
| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| 1 | u24 skills/herd/roles/orchestrator.md › The orchestrator: "send 3 or 4 new read-only subagents on `claude-haiku-5-5`" (the kitten swarm for a run item) | "Do not override it on the dispatch call" (rule 6) | examples/reader/rules/engineering.md | 🟥 |
| 2 | u28 skills/herd/roles/reviewer.md › Each review: "send your own swarm of read-only `claude-haiku-5-5` subagents" | "Do not override it on the dispatch call" (rule 6) | examples/reader/rules/engineering.md | 🟥 |
| 3 | u29 skills/herd/roles/reviewer.md › Limits: "You may try the same action, on your own judgement" for an action the worker's session was refused | "Never run anything destructive without my explicit go-ahead" (hard stop 1), when the refused action is destructive | examples/reader/rules/safety.md | 🟥 |
| 4 | u32 skills/herd/roles/worker.md › The worker, in a pair: "Send 3 or 4 subagents on `claude-haiku-5-5`, one lens each", also for the wording swarm | "Do not override it on the dispatch call" (rule 6) | examples/reader/rules/engineering.md | 🟥 |
| 5 | u46 skills/queue/SKILL.md › Working the queue: grooming hands items to "agents on the cheapest capable model your host offers" | "Do not override it on the dispatch call" (rule 6) | examples/reader/rules/engineering.md | 🟥 |

Situations: the swarm and grooming rows govern subagent dispatch, which is what rule 6 governs. The model defaults for sessions the plugin starts (skills/herd/SKILL.md, "Which model a session you start runs on") start a separate session, not a subagent, so they are not counted.

## 🔁 Already covered: 6
| its rule | covered by | held in |
|---|---|---|
| u2 Splitting adds nothing; ask before widening (skills/capture/SKILL.md › An interruption, so keep it short) | rule 4, "say what you would change and let me decide"; chosen because it is stated as a rule of its own | examples/reader/rules/engineering.md |
| u3 Work found along the way is captured, not done inline (skills/capture/SKILL.md › Asked to do work yourself) | rule 4, scope as asked | examples/reader/rules/engineering.md |
| u20 Run `meow herd clean` only on the owner's go-ahead (skills/herd/roles/handoff.md › If you're retiring) | hard stop 1, deleting files outside the working tree needs a go-ahead | examples/reader/rules/safety.md |
| u45 Read back an irreversible command heard by sound (skills/queue/SKILL.md › The queue) | hard stops 1 and 5, ask when ambiguous and costly | examples/reader/rules/safety.md |
| u51 Two matches: ask which; irreversible commands wait for a yes (skills/queue/sections/field-trip.md) | hard stop 5, and the short-but-complete line in CLAUDE.md for phone replies | examples/reader/rules/safety.md, examples/reader/CLAUDE.md |
| u52 Never push the code yourself without the owner's word (skills/queue/sections/setup.md) | hard stop 2, no push to main without being asked | examples/reader/rules/safety.md |

## 🟩 Keep: 51

Rules to copy: 8 (listed first, whatever the verdict). Skill sections kept: 43.

### Rules to copy
| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| 1 | u11 Skill to write (name is my proposal: audit-claims): "Run each example as written, in a scratch repo, with a fake for anything that leaves the host", find the test, break the code, give each claim one of BACKED, UNTESTED, CONTRADICTED, UNTESTABLE (skills/herd/roles/auditor.md › Method) | skill | 🟩 |
| 2 | u13 "never `pkill` or `killall` by pattern"; "Stop a process by the pid you started" (skills/herd/roles/auditor.md › Hard rules) | rule | 🟩 |
| 3 | u22 "Push your branch ... early and often, because a worktree or clone can be removed at any time"; leave a dirty checkout alone (skills/herd/roles/handoff.md › If you're the new session) | rule | 🟩 |
| 4 | u26 "Never add a key, a token, an https remote or a forwarded agent to get past it" when git fails on authentication (skills/herd/roles/reviewer.md › (top)) | rule | 🟩 |
| 5 | u31 "Stop only the processes you started, by their PID, never by port" (skills/herd/roles/reviewer.md › When the item says rigor: build); same rule as u13 and u33 | rule | 🟩 |
| 6 | u33 "Never simplify away validation at a trust boundary, error handling that prevents data loss, or a security measure" (skills/herd/roles/worker.md › When the item says rigor: build) | rule | 🟩 |
| 7 | u49 "When a reply skips something you asked, don't take it as a yes or a no, and don't act on it" (skills/queue/SKILL.md › Staying reasonable) | rule | 🟩 |
| 8 | u50 "What to type or paste sits alone in a code block, exactly as it should be pasted", no placeholder left to fill (skills/queue/sections/asks.md) | rule | 🟩 |

### Skill sections kept (work as shipped; they need the plugin's own `meow` tool)
| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| 1 | u1 skills/capture/SKILL.md › Capture | skill | 🟩 |
| 2 | u2 skills/capture/SKILL.md › An interruption, so keep it short | skill | 🟩 |
| 3 | u3 skills/capture/SKILL.md › Asked to do work yourself: every session, not only the worker | skill | 🟩 |
| 4 | u4 skills/capture/SKILL.md › Rescue session: everything this session was tracking | skill | 🟩 |
| 5 | u5 skills/capture/SKILL.md › Stream-of-consciousness: the owner is riffing | skill | 🟩 |
| 6 | u6 skills/capture/SKILL.md › Prompt me: answering the open questions with a tap | skill | 🟩 |
| 7 | u7 skills/capture/sections/prompt-me.md › Prompt me: answering the open questions with a tap (the rest) | skill | 🟩 |
| 8 | u8 skills/herd/SKILL.md › Herd | skill | 🟩 |
| 9 | u9 skills/herd/roles/associate.md › The associate | skill | 🟩 |
| 10 | u10 skills/herd/roles/auditor.md › The auditor | skill | 🟩 |
| 11 | u11 skills/herd/roles/auditor.md › Method | skill | 🟩 |
| 12 | u12 skills/herd/roles/auditor.md › Findings | skill | 🟩 |
| 13 | u13 skills/herd/roles/auditor.md › Hard rules | skill | 🟩 |
| 14 | u14 skills/herd/roles/auditor.md › Prompt hygiene | skill | 🟩 |
| 15 | u15 skills/herd/roles/auditor.md › Report | skill | 🟩 |
| 16 | u16 skills/herd/roles/auditor.md › The coordinator's checklist | skill | 🟩 |
| 17 | u17 skills/herd/roles/auditor.md › A falsify item | skill | 🟩 |
| 18 | u18 skills/herd/roles/bond.md › A bond: you and {{WORKER_NAME}} review each other | skill | 🟩 |
| 19 | u19 skills/herd/roles/handoff.md › Handing off to a new session | skill | 🟩 |
| 20 | u20 skills/herd/roles/handoff.md › If you're retiring | skill | 🟩 |
| 21 | u21 skills/herd/roles/handoff.md › If you're the one that stays | skill | 🟩 |
| 22 | u22 skills/herd/roles/handoff.md › If you're the new session | skill | 🟩 |
| 23 | u23 skills/herd/roles/handoff.md › In chat | skill | 🟩 |
| 24 | u24 skills/herd/roles/orchestrator.md › The orchestrator | skill | 🟩 |
| 25 | u25 skills/herd/roles/readonly.md › The reply of a session that can't write | skill | 🟩 |
| 26 | u26 skills/herd/roles/reviewer.md › (top) | skill | 🟩 |
| 27 | u27 skills/herd/roles/reviewer.md › Setting up (once, when this pair starts) | skill | 🟩 |
| 28 | u28 skills/herd/roles/reviewer.md › Each review | skill | 🟩 |
| 29 | u29 skills/herd/roles/reviewer.md › Limits | skill | 🟩 |
| 30 | u30 skills/herd/roles/reviewer.md › Who started you, and stopping | skill | 🟩 |
| 31 | u31 skills/herd/roles/reviewer.md › When the item says rigor: build | skill | 🟩 |
| 32 | u32 skills/herd/roles/worker.md › The worker, in a pair | skill | 🟩 |
| 33 | u33 skills/herd/roles/worker.md › When the item says rigor: build | skill | 🟩 |
| 34 | u34 skills/herd/sections/launch-refused.md › A launch is refused | skill | 🟩 |
| 35 | u35 skills/herd/sections/orchestrator.md › The orchestrator at a run's end, and in cloud runs | skill | 🟩 |
| 36 | u45 skills/queue/SKILL.md › The queue | skill | 🟩 |
| 37 | u46 skills/queue/SKILL.md › Working the queue | skill | 🟩 |
| 38 | u47 skills/queue/SKILL.md › Telling the owner what another session said | skill | 🟩 |
| 39 | u49 skills/queue/SKILL.md › Staying reasonable | skill | 🟩 |
| 40 | u50 skills/queue/sections/asks.md › Asking the owner to do something | skill | 🟩 |
| 41 | u51 skills/queue/sections/field-trip.md › Field Trip, and reading the owner as voice | skill | 🟩 |
| 42 | u52 skills/queue/sections/setup.md › Setting up a queue | skill | 🟩 |
| 43 | u57 commands/meow.md | command | 🟩 |

## 🗑️ Dropped
`u36` · `u37` · `u38` · `u39` · `u40` · `u41` · `u42` · `u43` · `u44` · `u48` · `u53` · `u54` · `u55` · `u56` · `u58` · `u59` · `u60` · `u61` · `u62` · `u63` · `u64`

u36 to u44 are the herder skill (cat voice and names), u48 is an example ledger bullet, and the other ten are commands that only call a skill or print one `meow` output.

## 🧩 What it installs
| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| SessionStart hook (`meow _hook sessionstart`) | startup, resume, compact | no | a few lines in a repo with a queue, none elsewhere |
| PreCompact hook (`meow _hook precompact`) | automatic compaction | no | silent, one queue commit for a rostered session |
| SessionEnd hook (`meow _hook sessionend`) | session close | no | silent, one state record |
| 4 skills: capture, herd, herder, queue | on demand; descriptions always | no | 76,072 bytes of SKILL.md, plus roles and sections |
| 12 commands | when typed | no | 109 to 1,233 characters each |
| agents, MCP servers | none | n/a | 0 |

## ✅ Do this
- ⬜ 1. Install it if you will run a work queue with a reviewer. Before you do, decide the four model-naming collisions: either accept the haiku swarm as a named exception to rule 6, or tell the sessions to run the swarm steps without a `model` argument. The plugin file stays unedited.
- ⬜ 2. Decide whether a reviewer may retry an action a worker's session was refused (skills/herd/roles/reviewer.md › Limits). Hard stop 1 says not when it is destructive.
- ⬜ 3. Copy the six standing rules in the patch below, and write the audit-claims skill.
Carrying-cost case: the hooks inject at session start but only inside a repo with a queue, and many sections survive, so this is neither the single-rule case nor the zero-hook case. The cost is real but small and the kept workflow is the reason to install.

## 📋 Proposed rules patch
Add to the reader's `rules/engineering.md`, which is a numbered list of one-line bold rules that `CLAUDE.md` imports. Items 8 to 13 follow rule 7. The three process-stopping rows (u13, u31, u33) collapse into one rule, so seven standing rows become six rules.

```diff
+8. **Stop only the processes you started.** Use the PID, never a name pattern or a port.
+9. **Never simplify away validation at a trust boundary,** error handling that prevents data loss, or a security measure.
+10. **Push work in progress early and often,** and leave a dirty or unrelated checkout alone: a worktree can vanish with unpushed work in it.
+11. **If git fails on authentication, stop and report the remote and the error.** Do not add a key, token, https remote or forwarded agent to get past it.
+12. **A question I skip is unread, not answered.** Do not read it as a yes or a no, and do not act on it.
+13. **When you give me a command, put it alone in a code block,** exactly as I would paste it, with no placeholder left to fill.
```

Proposed skill (name is my proposal): `audit-claims`, "Audit a document's claims: run every example as written, find the test that covers each claim, break the code and see whether a test fails, then label each claim BACKED, UNTESTED, CONTRADICTED or UNTESTABLE." The dossier shows the reader keeps a skill next to `release-notes`, so put it beside that one; I did not see a path, so the choice is yours.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
