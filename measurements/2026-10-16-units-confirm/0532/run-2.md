# 🔍 ch-v0532 0.53.2 · vetted against the sample reader

> ## 🟧 INSTALL WITH CHANGES · keep the workflow skills, fix five sections and copy the new rules
> Cat Herder is a queue-and-review workflow driven by its own `meow` command, and 43 of its 64 sections work as shipped and add something the reader lacks. Five sections tell the model to name a subagent model or to retry a refused action, which collides with two of the reader's rules. Its three hooks inject nothing in a repo with no queue, and it reaches no subagents.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-16` · neckbeard 1.14.0 · ch-v0532 0.53.2

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟨 | **Cost** | 3 hooks, no static payload. SessionStart says the roster role and the repo's queue rules, only in a repo that has a queue; nothing in one without. Size varies with the queue. Skills load on demand (about 76 KB of skill text across 4 skills, 12 commands). |
| 🟩 | **Reach** | Main session only (no hooked event is known to fire in a subagent, likely). |
| 🟨 | **Leaves state** | SessionEnd notes the closed session in this machine's state (`lib/cat_herder/ended.py`). PreCompact counts compactions in the queue's roster, a git write. |
| 🟨 | **Live surface** | `bin/meow`, git fetch and push to the queue remote, ssh to other hosts, launchers in `tools/`. No MCP servers. |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 43 skill sections, 12 standing rules and 1 skill to copy |

The dossier lists all three hooks as unidentifiable, so I read `lib/cat_herder/hooks.py` by hand: SessionStart reads only the local copy of the queue and prints role and rule lines; PreCompact and SessionEnd print nothing to the model.

## 🧮 How its rules sorted

Each of the 64 sections gets a skill answer and a rules answer, so a section can appear in more than one row.

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **5** sections (6 sentences) | 🟥🟥🟥🟥🟥 |
| 🔁 | **already covered** | **4** | ⬜⬜⬜⬜ |
| 🆕 | **new, standing rule** | **12** | ▰ ×12 |
| 🆕 | **new, on-demand skill** | **1** | 🟩 |
| 🟩 | **skill sections kept** | **43** of 64 | ▰ ×43 |
| 🗑️ | **dropped** (persona, wrappers, no value) | **21** | ▰ ×21 |

## ⛔ Conflicts: 5
| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| 1 | u24: skills/herd/roles/orchestrator.md · The orchestrator says "send 3 or 4 new read-only subagents on `claude-haiku-5-5`" | examples/reader/rules/engineering.md rule 6 (no override on dispatch). Name no model on the dispatch; let each agent definition pin it. | examples/reader/rules/engineering.md | ⛔ |
| 2 | u28: skills/herd/roles/reviewer.md · Each review says "send your own swarm of read-only `claude-haiku-5-5` subagents" | examples/reader/rules/engineering.md rule 6. Same: no model id on the call. Permits it with no limit. | examples/reader/rules/engineering.md | ⛔ |
| 3 | u29: skills/herd/roles/reviewer.md · Limits says "You may try the same action, on your own judgement" | examples/reader/rules/safety.md rule 1 (destructive needs go-ahead). Permits a retry with no limit. Ask for: only non-destructive actions, and ask first for anything destructive. | examples/reader/rules/safety.md | ⛔ |
| 4 | u32: skills/herd/roles/worker.md · The worker, in a pair says "Send 3 or 4 subagents on `claude-haiku-5-5`" and, in the same section, "send three subagents on `claude-haiku-5-5`" | examples/reader/rules/engineering.md rule 6. Two sentences. Drop the model id from both. | examples/reader/rules/engineering.md | ⛔ |
| 5 | u46: skills/queue/SKILL.md · Working the queue says "agents on the cheapest capable model your host offers" | examples/reader/rules/engineering.md rule 6. Picks a model on the call. Drop it, or use the definition's pin. | examples/reader/rules/engineering.md | ⛔ |

## 🔁 Already covered: 4
| its rule | covered by | held in |
|---|---|---|
| skills/capture/SKILL.md · An interruption, so keep it short (u2) | examples/reader/rules/engineering.md rule 4 (scope is the deliverable) | examples/reader/rules/engineering.md |
| skills/queue/SKILL.md · The queue (u45) | examples/reader/rules/safety.md rule 5 (ask when ambiguous and costly) | examples/reader/rules/safety.md |
| skills/queue/SKILL.md · Working the queue (u46) | examples/reader/rules/engineering.md rule 4 (say what changes, let me decide) | examples/reader/rules/engineering.md |
| skills/queue/sections/field-trip.md · Field Trip, and reading the owner as voice (u51) | examples/reader/rules/safety.md rule 5 (ask when ambiguous and costly) | examples/reader/rules/safety.md |

## 🆕 Rules to copy: 13
| # | section | kind | rule (short phrase) | |
|:--:|---|:--:|---|:--:|
| 1 | skills/herd/roles/auditor.md · Hard rules (u13) | standing | "never `pkill` or `killall` by pattern" | 🆕 |
| 2 | skills/herd/roles/handoff.md · If you're the new session (u22) | standing | "never from whatever is checked out" | 🆕 |
| 3 | skills/herd/roles/orchestrator.md · The orchestrator (u24) | standing | "in the background, and read its output file" | 🆕 |
| 4 | skills/herd/roles/reviewer.md · (top) (u26) | standing | "Never add a key, a token, an https remote" | 🆕 |
| 5 | skills/herd/roles/reviewer.md · Each review (u28) | standing | "unchanged at the base is baseline" | 🆕 |
| 6 | skills/herd/roles/reviewer.md · Limits (u29) | standing | "It lapses when what it covers changes" | 🆕 |
| 7 | skills/herd/roles/reviewer.md · When the item says rigor: build (u31) | standing | "changed to make it pass" | 🆕 |
| 8 | skills/herd/roles/worker.md · The worker, in a pair (u32) | standing | "Never add a key, a token, an https remote" | 🆕 |
| 9 | skills/herd/roles/worker.md · When the item says rigor: build (u33) | standing | "Never simplify away validation at a trust boundary" | 🆕 |
| 10 | skills/herd/sections/launch-refused.md · A launch is refused (u34) | standing | "get around the refusal no other way" | 🆕 |
| 11 | skills/queue/SKILL.md · Staying reasonable (u49) | standing | "don't act on it" | 🆕 |
| 12 | skills/queue/sections/asks.md · Asking the owner to do something (u50) | standing | "no placeholder left for the owner to fill" | 🆕 |
| 13 | skills/herd/roles/auditor.md · Method (u11) | skill | "List every checkable claim in the area" | 🆕 |

## 🟩 Keep: 43
| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| 1 | skills/capture/SKILL.md · Capture (u1) | skill | 🟩 |
| 2 | skills/capture/SKILL.md · An interruption, so keep it short (u2) | skill | 🟩 |
| 3 | skills/capture/SKILL.md · Asked to do work yourself: every session, not only the worker (u3) | skill | 🟩 |
| 4 | skills/capture/SKILL.md · Rescue session: everything this session was tracking (u4) | skill | 🟩 |
| 5 | skills/capture/SKILL.md · Stream-of-consciousness: the owner is riffing (u5) | skill | 🟩 |
| 6 | skills/capture/SKILL.md · Prompt me: answering the open questions with a tap (u6) | skill | 🟩 |
| 7 | skills/capture/sections/prompt-me.md · Prompt me: answering the open questions with a tap (the rest) (u7) | section | 🟩 |
| 8 | skills/herd/SKILL.md · Herd (u8) | skill | 🟩 |
| 9 | skills/herd/roles/associate.md · The associate (u9) | role | 🟩 |
| 10 | skills/herd/roles/auditor.md · The auditor (u10) | role | 🟩 |
| 11 | skills/herd/roles/auditor.md · Method (u11) | role | 🟩 |
| 12 | skills/herd/roles/auditor.md · Findings (u12) | role | 🟩 |
| 13 | skills/herd/roles/auditor.md · Hard rules (u13) | role | 🟩 |
| 14 | skills/herd/roles/auditor.md · Prompt hygiene (u14) | role | 🟩 |
| 15 | skills/herd/roles/auditor.md · Report (u15) | role | 🟩 |
| 16 | skills/herd/roles/auditor.md · The coordinator's checklist (u16) | role | 🟩 |
| 17 | skills/herd/roles/auditor.md · A falsify item (u17) | role | 🟩 |
| 18 | skills/herd/roles/bond.md · A bond: you and {{WORKER_NAME}} review each other (u18) | role | 🟩 |
| 19 | skills/herd/roles/handoff.md · Handing off to a new session (u19) | role | 🟩 |
| 20 | skills/herd/roles/handoff.md · If you're retiring (u20) | role | 🟩 |
| 21 | skills/herd/roles/handoff.md · If you're the one that stays (u21) | role | 🟩 |
| 22 | skills/herd/roles/handoff.md · If you're the new session (u22) | role | 🟩 |
| 23 | skills/herd/roles/handoff.md · In chat (u23) | role | 🟩 |
| 24 | skills/herd/roles/orchestrator.md · The orchestrator (u24) | role | 🟩 |
| 25 | skills/herd/roles/readonly.md · The reply of a session that can't write (u25) | role | 🟩 |
| 26 | skills/herd/roles/reviewer.md · (top) (u26) | role | 🟩 |
| 27 | skills/herd/roles/reviewer.md · Setting up (once, when this pair starts) (u27) | role | 🟩 |
| 28 | skills/herd/roles/reviewer.md · Each review (u28) | role | 🟩 |
| 29 | skills/herd/roles/reviewer.md · Limits (u29) | role | 🟩 |
| 30 | skills/herd/roles/reviewer.md · Who started you, and stopping (u30) | role | 🟩 |
| 31 | skills/herd/roles/reviewer.md · When the item says rigor: build (u31) | role | 🟩 |
| 32 | skills/herd/roles/worker.md · The worker, in a pair (u32) | role | 🟩 |
| 33 | skills/herd/roles/worker.md · When the item says rigor: build (u33) | role | 🟩 |
| 34 | skills/herd/sections/launch-refused.md · A launch is refused (u34) | section | 🟩 |
| 35 | skills/herd/sections/orchestrator.md · The orchestrator at a run's end, and in cloud runs (u35) | section | 🟩 |
| 36 | skills/queue/SKILL.md · The queue (u45) | skill | 🟩 |
| 37 | skills/queue/SKILL.md · Working the queue (u46) | skill | 🟩 |
| 38 | skills/queue/SKILL.md · Telling the owner what another session said (u47) | skill | 🟩 |
| 39 | skills/queue/SKILL.md · Staying reasonable (u49) | skill | 🟩 |
| 40 | skills/queue/sections/asks.md · Asking the owner to do something (u50) | section | 🟩 |
| 41 | skills/queue/sections/field-trip.md · Field Trip, and reading the owner as voice (u51) | section | 🟩 |
| 42 | skills/queue/sections/setup.md · Setting up a queue (u52) | section | 🟩 |
| 43 | commands/meow.md (whole command) (u57) | command | 🟩 |

## 🗑️ Dropped
`u36` · `u37` · `u38` · `u39` · `u40` · `u41` · `u42` · `u43` · `u44` · `u48` · `u53` · `u54` · `u55` · `u56` · `u58` · `u59` · `u60` · `u61` · `u62` · `u63` · `u64`

That is the whole `skills/herder/SKILL.md` voice (u36 to u44), one sample question (u48) and ten commands that only point at a skill or a `meow` call (u53 to u56, u58 to u64). None of the dropped sections has a conflict.

## 🧩 What it installs
| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| SessionStart hook (`meow _hook sessionstart`) | startup, resume, compact | no (likely) | varies, 0 without a queue |
| PreCompact hook | automatic compaction | no (likely) | none to the model |
| SessionEnd hook | session close | no (likely) | none to the model |
| 4 skills: capture, herd, herder, queue | on demand | no | about 76 KB of text |
| 12 commands | when typed | no | about 5 KB |
| `bin/meow` and `lib/`, `tools/` | when a skill calls them | no | CLI, launchers, supervisor |

## ✅ Do this
- ⬜ 1. Add the rules patch below to `examples/reader/rules/engineering.md` and `examples/reader/rules/safety.md`.
- ⬜ 2. Ask the maintainer to drop the `claude-haiku-5-5` and "cheapest capable model" wording from u24, u28, u32 and u46, and to limit u29 to non-destructive retries. Until then, `examples/reader/rules/engineering.md` rule 6 and `examples/reader/rules/safety.md` rule 1 win over those sentences.
- ⬜ 3. Skip the `herder` skill. It is voice only.

Carrying-cost case: the hooks fire at every session start but inject nothing outside a queue repo, and the plugin holds several rules you would write yourself, so installing is reasonable once the five sections are fixed.

## 📋 Proposed rules patch

The reader's `examples/reader/rules/engineering.md` is a numbered list about how code gets written, so the build rules go after rule 7 there. The two about refusals and approvals go in `examples/reader/rules/safety.md` after rule 5. Wording is mine; the quoted phrases come from the sections named.

```diff
+ examples/reader/rules/engineering.md
+ 8. **Start a new task from its base**, never from whatever is checked out; leave a dirty checkout alone.   (u22)
+ 9. **Run anything past about 30 seconds in the background** and read its output file.   (u24)
+ 10. **A failure that also shows at the review base is baseline**, not a reason to reject.   (u28)
+ 11. **When a test now passes, read the test diff:** was a criterion, test or threshold changed to make it pass?   (u31)
+ 12. **Never simplify away validation at a trust boundary,** error handling that prevents data loss, or a security measure.   (u33)
+ 13. **Stop only the processes you started, by pid.** Never `pkill` or `killall` by pattern.   (u13)
+ 14. **Ask the owner to run something in a block of its own,** the command alone, with no placeholder left to fill.   (u50)
+ examples/reader/rules/safety.md
+ 6. **If a git fetch or push fails on authentication, stop and report** the remote and the error. Never add a key, a token, an https remote or a forwarded agent.   (u26, u32)
+ 7. **If an action is refused, get around it no other way** (another tool, a background command, a permission change).   (u34)
+ 8. **An approval covers only what it named** and lapses when that changes.   (u29)
+ 9. **A question the owner skipped is unread, not a yes or a no.** Do not act on it.   (u49)
```

That is 11 rules covering the 12 sections in the table (u26 and u32 carry the same rule).

Proposed skill (name is mine): `audit-doc-claims`, "List every checkable claim in a doc, run each example, find the test that covers it, break the code once, and give each claim a verdict: backed, untested, contradicted or untestable." It comes from `skills/herd/roles/auditor.md` Method (u11). The dossier does not say where this reader keeps skills, so the choice is theirs.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
