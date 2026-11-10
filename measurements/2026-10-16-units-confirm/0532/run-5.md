# 🔍 ch-v0532 0.53.2 · vetted against the sample reader

> ## 🟧 INSTALL WITH CHANGES · keep the workflow skills, remove the model pins and the open-ended retries
> Five of its 64 instruction sections collide with the reader: four tell the model to name `claude-haiku-5-5` or "the cheapest capable model" on a dispatch call, and two let a session retry a refused action on its own judgement. The other sections are a large queue-and-review workflow that works as shipped (42 kept) plus 11 general rules the reader lacks, led by "stop at an auth failure" and "validation at a trust boundary". Its hooks add text only in a repo that has a Cat Herder queue and do not reach subagents.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-16` · neckbeard 1.14.0 · ch-v0532 0.53.2

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟨 | **Cost** | Four skills load on demand (76 KB of SKILL.md text) and 12 commands (about 5 KB). Three hooks run in Claude Code: SessionStart prints a short rules block in a repo that has a queue and nothing elsewhere; its size was not measured (`lib/cat_herder/hooks.py`) |
| 🟩 | **Reach** | Main session only (likely): no hook event is known to fire in a subagent |
| 🟧 | **Leaves state** | SessionEnd records the ended session in this machine's state (`lib/cat_herder/ended.py`); PreCompact writes a compaction count to the queue for sessions on a roster; the queue itself is git commits on a branch or ref |
| 🟧 | **Live surface** | Git fetch and push to queue remotes (ssh or http), launchers, tmux, ssh test hosts, cloud sessions; no MCP servers |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 42 skill sections and 11 general rules (9 standing, 2 skills) |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **5** | 🟥🟥🟥🟥🟥 |
| 🔁 | **already covered** | **5** | ⬜⬜⬜⬜⬜ |
| 🆕 | **new, standing rule** | **9** | 🟩🟩🟩🟩🟩🟩🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **2** | 🟩🟩 |
| 🗑️ | **dropped** (persona, wrappers, no value) | **22** | ⬛ ×22 |
| 🟩 | **skill sections kept** (of 64 units) | **42** | 🟩 ×42 |

## ⛔ Conflicts: 5

| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| u24 | `skills/herd/roles/orchestrator.md` "The orchestrator": "send 3 or 4 new read-only subagents on `claude-haiku-5-5`" | rule 6, "Do not override it on the dispatch call" | examples/reader/rules/engineering.md | ⛔ |
| u28 | `skills/herd/roles/reviewer.md` "Each review": "you may send your own swarm of read-only `claude-haiku-5-5` subagents". Names a model, with no limit. Ask for: only for agents whose definition pins no model | rule 6, same sentence | examples/reader/rules/engineering.md | ⛔ |
| u29 | `skills/herd/roles/reviewer.md` "Limits": "You may try the same action, on your own judgement". No limit. Ask for: only non-destructive actions, or with a go-ahead in this conversation | rule 1, "explicit go-ahead in this conversation" | examples/reader/rules/safety.md | ⛔ |
| u32 | `skills/herd/roles/worker.md` "The worker, in a pair": four sentences. Three dispatch subagents on `claude-haiku-5-5` ("Send 3 or 4 subagents", the wording swarm of three, "one more read-only Haiku" for docs lines). The fourth, "The reviewer may try an action you reported as refused, on its own judgement", has no limit. Ask for: only non-destructive actions, or with a go-ahead | rule 6 for the model sentences; rule 1 for the retry | examples/reader/rules/engineering.md; examples/reader/rules/safety.md | ⛔ |
| u46 | `skills/queue/SKILL.md` "Working the queue": "the cheapest capable model your host offers" | rule 6, "Do not override it on the dispatch call" | examples/reader/rules/engineering.md | ⛔ |

## 🔁 Already covered: 5

| its rule | covered by | held in |
|---|---|---|
| u3 `skills/capture/SKILL.md` "Asked to do work yourself": work found along the way is queued, not done inline | rule 4, the scope asked is the deliverable | examples/reader/rules/engineering.md |
| u28 `skills/herd/roles/reviewer.md` "Each review": review the commits and watch the test fail without the change | rule 3, a test is done once seen to fail | examples/reader/rules/engineering.md |
| u31 `skills/herd/roles/reviewer.md` "When the item says rigor: build": revert the change and watch the test fail | rule 3 | examples/reader/rules/engineering.md |
| u46 `skills/queue/SKILL.md` "Working the queue": reread a stale brief, and do not build the old version | rule 4, say what you would change and let me decide | examples/reader/rules/engineering.md |
| u51 `skills/queue/sections/field-trip.md` "Field Trip, and reading the owner as voice": read a guessed irreversible command back and wait | rule 5, ask when the wrong reading is costly | examples/reader/rules/safety.md |

Units u28 and u46 also appear in the conflicts grid, since a unit's conflict and its general rules are judged separately.

## 🟩 Keep: 42

### Rules to copy (11, whatever the verdict)

| # | unit | rule to copy | kind |
|:--:|---|---|:--:|
| u13 | `skills/herd/roles/auditor.md` "Hard rules" | "never `pkill` or `killall` by pattern" and "Stop a process by the pid you started" | 🆕 standing |
| u22 | `skills/herd/roles/handoff.md` "If you're the new session" | push the branch "early and often, because a worktree or clone can be removed"; never write in the checkout you were started from | 🆕 standing |
| u24 | `skills/herd/roles/orchestrator.md` "The orchestrator" | "Start any command that can run past about 30 seconds" in the background and read its output file | 🆕 standing |
| u26 | `skills/herd/roles/reviewer.md` "(top)" | "stop and report the remote and the error" on an auth failure; "Never add a key, a token, an https remote or a forwarded agent" | 🆕 standing |
| u29 | `skills/herd/roles/reviewer.md` "Limits" | "If you need something your permission mode doesn't allow, stop and say what." | 🆕 standing |
| u32 | `skills/herd/roles/worker.md` "The worker, in a pair" | "Never ask the reviewer to run it for you" (a refused action must not pass to another session) | 🆕 standing |
| u33 | `skills/herd/roles/worker.md` "When the item says rigor: build" | "Never simplify away validation at a trust boundary" or error handling that prevents data loss, or a security measure | 🆕 standing |
| u49 | `skills/queue/SKILL.md` "Staying reasonable" | "A question the owner skipped is unread, not answered." | 🆕 standing |
| u50 | `skills/queue/sections/asks.md` "Asking the owner to do something" | what the owner must run sits alone in a code block, "exactly as it should be pasted", with no placeholder | 🆕 standing |
| u11 | `skills/herd/roles/auditor.md` "Method" | list every checkable claim, run each example, break the code once per claim, give a verdict word | 🆕 skill |
| u25 | `skills/herd/roles/readonly.md` "The reply of a session that can't write" | a fixed `## Report` form with a patch against a named base | 🆕 skill |

### Skill sections kept (all 42; they need the plugin's own `meow` command)

| # | unit | |
|:--:|---|:--:|
| u1 | `skills/capture/SKILL.md` "Capture" | 🟩 |
| u2 | `skills/capture/SKILL.md` "An interruption, so keep it short" | 🟩 |
| u3 | `skills/capture/SKILL.md` "Asked to do work yourself: every session, not only the worker" | 🟩 |
| u4 | `skills/capture/SKILL.md` "Rescue session: everything this session was tracking" | 🟩 |
| u5 | `skills/capture/SKILL.md` "Stream-of-consciousness: the owner is riffing" | 🟩 |
| u6 | `skills/capture/SKILL.md` "Prompt me: answering the open questions with a tap" | 🟩 |
| u7 | `skills/capture/sections/prompt-me.md` "Prompt me: answering the open questions with a tap (the rest)" | 🟩 |
| u8 | `skills/herd/SKILL.md` "Herd" | 🟩 |
| u9 | `skills/herd/roles/associate.md` "The associate" | 🟩 |
| u10 | `skills/herd/roles/auditor.md` "The auditor" | 🟩 |
| u11 | `skills/herd/roles/auditor.md` "Method" | ⭐ |
| u12 | `skills/herd/roles/auditor.md` "Findings" | 🟩 |
| u13 | `skills/herd/roles/auditor.md` "Hard rules" | 🟩 |
| u14 | `skills/herd/roles/auditor.md` "Prompt hygiene" | 🟩 |
| u15 | `skills/herd/roles/auditor.md` "Report" | 🟩 |
| u16 | `skills/herd/roles/auditor.md` "The coordinator's checklist" | 🟩 |
| u17 | `skills/herd/roles/auditor.md` "A falsify item" | 🟩 |
| u18 | `skills/herd/roles/bond.md` "A bond: you and {{WORKER_NAME}} review each other" | 🟩 |
| u19 | `skills/herd/roles/handoff.md` "Handing off to a new session" | 🟩 |
| u20 | `skills/herd/roles/handoff.md` "If you're retiring" | 🟩 |
| u21 | `skills/herd/roles/handoff.md` "If you're the one that stays" | 🟩 |
| u22 | `skills/herd/roles/handoff.md` "If you're the new session" | 🟩 |
| u23 | `skills/herd/roles/handoff.md` "In chat" | 🟩 |
| u24 | `skills/herd/roles/orchestrator.md` "The orchestrator" | 🟧 |
| u25 | `skills/herd/roles/readonly.md` "The reply of a session that can't write" | 🟩 |
| u26 | `skills/herd/roles/reviewer.md` "(top)" | 🟩 |
| u27 | `skills/herd/roles/reviewer.md` "Setting up (once, when this pair starts)" | 🟩 |
| u28 | `skills/herd/roles/reviewer.md` "Each review" | 🟧 |
| u29 | `skills/herd/roles/reviewer.md` "Limits" | 🟧 |
| u30 | `skills/herd/roles/reviewer.md` "Who started you, and stopping" | 🟩 |
| u31 | `skills/herd/roles/reviewer.md` "When the item says rigor: build" | 🟩 |
| u32 | `skills/herd/roles/worker.md` "The worker, in a pair" | 🟧 |
| u33 | `skills/herd/roles/worker.md` "When the item says rigor: build" | 🟩 |
| u34 | `skills/herd/sections/launch-refused.md` "A launch is refused" | 🟩 |
| u35 | `skills/herd/sections/orchestrator.md` "The orchestrator at a run's end, and in cloud runs" | 🟩 |
| u45 | `skills/queue/SKILL.md` "The queue" | 🟩 |
| u46 | `skills/queue/SKILL.md` "Working the queue" | 🟧 |
| u47 | `skills/queue/SKILL.md` "Telling the owner what another session said" | 🟩 |
| u49 | `skills/queue/SKILL.md` "Staying reasonable" | 🟩 |
| u50 | `skills/queue/sections/asks.md` "Asking the owner to do something" | 🟩 |
| u51 | `skills/queue/sections/field-trip.md` "Field Trip, and reading the owner as voice" | 🟩 |
| u52 | `skills/queue/sections/setup.md` "Setting up a queue" | 🟩 |

## 🗑️ Dropped

Persona and voice: `u36` · `u37` · `u38` · `u39` · `u40` · `u41` · `u42` · `u43` · `u44` (the `herder` skill, cat names and cat-voice lines)

Example text, not an instruction: `u48` (a sample ledger entry)

Wrappers that only call a skill section or one `meow` command: `u53` · `u54` · `u55` · `u56` · `u57` · `u58` · `u59` · `u60` · `u61` · `u62` · `u63` · `u64` (the 12 files in `commands/`)

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| skills `capture`, `herd`, `herder`, `queue` | on demand, when triggered | no | 76 KB |
| 12 commands (`commands/`) | when the user types one | no | about 5 KB |
| SessionStart hook (`hooks/claude-codex.json`) | startup, resume, compact | no (likely) | ❓ short rules block, only in a repo with a queue |
| PreCompact hook | automatic compaction | no (likely) | none printed; writes a count to the queue for a roster session |
| SessionEnd hook (`hooks/claude.json`) | a session closes | no (likely) | none printed; writes machine state |
| Antigravity PreToolUse hook (`hooks.json`) | each shell command, in Antigravity only | not in Claude Code | allows at once when `ANTIGRAVITY_PLUGIN_ROOT` is unset |

## ✅ Do this
- ⬜ 1. Before installing, ask for the five conflicts to be fixed: drop the model names in the swarm sentences (u24, u28, u32, u46) and limit the two retry sentences (u29, u32) to non-destructive actions or an explicit go-ahead.
- ⬜ 2. Install it only if you will use its queue and review workflow; its skills do nothing without the `meow` command and a queue in a git repo.
- ⬜ 3. Copy the 9 standing rules and 2 skills below into your own files, since they hold outside the plugin's skills.

Case: hooks exist but add text only in a repo with a queue and skip subagents, and more than one rule survives, so the plugin is worth carrying once the conflicts are fixed.

## 📋 Proposed rules patch

Where: your `examples/reader/rules/safety.md` takes the stop rules, `examples/reader/rules/engineering.md` the working rules, and `examples/reader/CLAUDE.md` ("How I like answers") the two reply rules.

```diff
--- examples/reader/rules/safety.md
+++ examples/reader/rules/safety.md
+6. **If a git fetch or push fails on authentication, stop and report the remote and the error.** Never add a key, a token, an https remote or a forwarded agent to get past it.
+7. **If you need something your permission mode doesn't allow, stop and say what.** Do not route a refused action through another session.
--- examples/reader/rules/engineering.md
+8. **Never simplify away validation at a trust boundary,** error handling that prevents data loss, or a security measure.
+9. **Stop only processes you started,** by pid. Never `pkill` or `killall` by pattern.
+10. **Run anything that may take over 30 seconds in the background** and read its output file.
+11. **Push a work branch early and often,** and never write in the checkout you were started from.
--- examples/reader/CLAUDE.md
+- A question I skipped is unread, not answered. Do not take silence as yes or no.
+- Anything I must run goes alone in a code block, exactly as I should paste it, with no placeholder.
```

Proposed skills (the names are my proposals; the dossier names no skills folder beyond `examples/reader/skills/`, so the location is yours to choose):

- `falsify-docs`: list every checkable claim in a doc or help text, run each example as written, break the code once per claim, and give each a verdict (backed, untested, contradicted, untestable). From u11.
- `readonly-report`: the reply form for a session that cannot write or push: a `## Report` with outcome, base sha, patch and commands run. From u25.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
