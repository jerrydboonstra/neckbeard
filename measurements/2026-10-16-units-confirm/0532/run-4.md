# 🔍 ch-v0532 0.53.2 · vetted against the sample reader

> ## 🟧 INSTALL WITH CHANGES · keep the skills, but fix the subagent-model and retry-limit lines first
> Its hooks are small and run only in a repo that has a queue, and 43 of its 64 sections work as shipped and add something the reader lacks. 8 lines in 5 sections collide with the reader's rules: they name `claude-haiku-5-5` on the dispatch call, or let a session retry a refused action on its own judgement. 10 general rules outside the plugin's own tool are worth copying whether or not you install.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-16` · neckbeard 1.14.0 · ch-v0532 0.53.2

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟨 | **Cost** | Three hooks (SessionStart, PreCompact, SessionEnd) all run `bin/meow _hook`, so the dossier could not trace them. Read by hand: SessionStart prints a few role lines and the queue's recorded rules and answers, and only in a repo with a queue copy; nothing otherwise. Size per start: ❓ |
| 🟩 | **Reach** | Main session only (no event fires in a subagent) |
| 🟨 | **Leaves state** | SessionEnd writes an ended-session record and PreCompact counts a compaction in this machine's state; `meow` commits to the git queue and pushes it. The dossier flags 97 scripts with file-write patterns and I did not trace them all, so the full list of paths is ❓ |
| 🟨 | **Live surface** | No MCP servers. `meow` runs git fetch and push against the queue remote (ssh or https) and can start sessions through a launcher |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 43 skill sections and 10 general rules (8 standing, 2 small skills) |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **8** | 🟥🟥🟥🟥🟥🟥🟥🟥 |
| 🔁 | **already covered** | **2** | ⬜⬜ |
| 🆕 | **new, standing rule** | **8** | 🟩🟩🟩🟩🟩🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **2** | 🟩🟩 |
| 🗑️ | **dropped** (persona, wrappers, no value) | **21** | ⬛ ×21 |
| 🟩 | **skill sections kept** | **43** of 64 | 🟩 ×43 |

The 8 conflicts sit in 5 sections, and a section can also hold a rule to copy, so the grids below count conflicts, rules and kept sections separately. Of the 64 sections, 52 hold only the plugin's own mechanics as far as general rules go.

## ⛔ Conflicts: 8

| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| 1 | "send 3 or 4 new read-only subagents on claude-haiku-5-5" | examples/reader/rules/engineering.md rule 6 ("Do not override it on the dispatch call") | `skills/herd/roles/orchestrator.md` · The orchestrator (u24) | 🟥 |
| 2 | "send your own swarm of read-only claude-haiku-5-5 subagents" | examples/reader/rules/engineering.md rule 6 ("Do not override it on the dispatch call") | `skills/herd/roles/reviewer.md` · Each review (u28) | 🟥 |
| 3 | "try the same action, on your own judgement" | examples/reader/rules/safety.md rule 1 ("explicit go-ahead") | `skills/herd/roles/reviewer.md` · Limits (u29) | 🟥 |
| 4 | "try an action you reported as refused, on its own judgement" | examples/reader/rules/safety.md rule 1 ("explicit go-ahead") | `skills/herd/roles/worker.md` · The worker, in a pair (u32) | 🟥 |
| 5 | "Send 3 or 4 subagents on claude-haiku-5-5" | examples/reader/rules/engineering.md rule 6 ("Do not override it on the dispatch call") | `skills/herd/roles/worker.md` · The worker, in a pair (u32) | 🟥 |
| 6 | "send three subagents on claude-haiku-5-5" | examples/reader/rules/engineering.md rule 6 ("Do not override it on the dispatch call") | `skills/herd/roles/worker.md` · The worker, in a pair (u32) | 🟥 |
| 7 | "one more read-only Haiku checks each docs or CHANGELOG line" | examples/reader/rules/engineering.md rule 6 ("Do not override it on the dispatch call") | `skills/herd/roles/worker.md` · The worker, in a pair (u32) | 🟥 |
| 8 | "the cheapest capable model your host offers" | examples/reader/rules/engineering.md rule 6 ("Do not override it on the dispatch call") | `skills/queue/SKILL.md` · Working the queue (u46) | 🟥 |

For the model-pin conflicts, ask for the pinned model to stand, with a note that the Haiku pick is only a default. For the retry conflicts, ask that a refused action is retried only when it is not destructive and the owner has said go.

## 🔁 Already covered: 2

| its rule | covered by | held in |
|---|---|---|
| cite what was checked, revert the change and watch the test fail | examples/reader/rules/engineering.md rule 3, and "saying what was checked" in examples/reader/CLAUDE.md | `skills/herd/roles/reviewer.md` · When the item says rigor: build (u31) |
| reread a stale brief; if its premise moved, do not build the old version, show the owner and wait | examples/reader/rules/engineering.md rule 4 (say what you would change and let the owner decide) | `skills/queue/SKILL.md` · Working the queue (u46) |

## 🆕 Rules to copy: 10

| unit | kind | rule, as a phrase |
|---|:--:|---|
| `skills/herd/roles/auditor.md` · Hard rules (u13) | standing | never pkill or killall by pattern; stop a process by the pid you started |
| `skills/herd/roles/auditor.md` · Prompt hygiene (u14) | standing | one command per call, absolute paths instead of cd |
| `skills/herd/roles/reviewer.md` · (top) (u26) | standing | on an auth failure, stop and report; never add a key, token, https remote or forwarded agent |
| `skills/herd/roles/reviewer.md` · Each review (u28) | standing | a diff that restructures and changes behaviour in one is a finding: split the refactor out |
| `skills/herd/roles/reviewer.md` · Limits (u29) | standing | an owner answer names what it covers and lapses when that changes |
| `skills/herd/roles/worker.md` · The worker, in a pair (u32) | standing | never ask another session to run an action you were refused |
| `skills/herd/roles/worker.md` · When the item says rigor: build (u33) | standing | never simplify away validation at a trust boundary, data-loss error handling or a security measure |
| `skills/queue/sections/asks.md` · Asking the owner to do something (u50) | standing | what the owner must paste sits alone in a code block, no placeholders |
| `skills/herd/roles/auditor.md` · Method (u11) | skill | list every checkable claim in a doc, run each example, break the code, give each a verdict |
| `skills/herd/roles/readonly.md` · The reply of a session that can't write (u25) | skill | a fixed report form for a session that cannot write: outcome, base sha, patch, commands run |

## 🟩 Keep: 43

| # | skill section | kind | |
|:--:|---|:--:|:--:|
| 1 | `skills/capture/SKILL.md` · Capture (u1) | skill | 🟩 |
| 2 | `skills/capture/SKILL.md` · An interruption, so keep it short (u2) | skill | 🟩 |
| 3 | `skills/capture/SKILL.md` · Asked to do work yourself: every session, not only the worker (u3) | skill | 🟩 |
| 4 | `skills/capture/SKILL.md` · Rescue session: everything this session was tracking (u4) | skill | 🟩 |
| 5 | `skills/capture/SKILL.md` · Stream-of-consciousness: the owner is riffing (u5) | skill | 🟩 |
| 6 | `skills/capture/SKILL.md` · Prompt me: answering the open questions with a tap (u6) | skill | 🟩 |
| 7 | `skills/capture/sections/prompt-me.md` · Prompt me: answering the open questions with a tap (the rest) (u7) | section | 🟩 |
| 8 | `skills/herd/SKILL.md` · Herd (u8) | skill | 🟩 |
| 9 | `skills/herd/roles/associate.md` · The associate (u9) | role | 🟩 |
| 10 | `skills/herd/roles/auditor.md` · The auditor (u10) | role | 🟩 |
| 11 | `skills/herd/roles/auditor.md` · Method (u11) | role | 🟩 |
| 12 | `skills/herd/roles/auditor.md` · Findings (u12) | role | 🟩 |
| 13 | `skills/herd/roles/auditor.md` · Hard rules (u13) | role | 🟩 |
| 14 | `skills/herd/roles/auditor.md` · Prompt hygiene (u14) | role | 🟩 |
| 15 | `skills/herd/roles/auditor.md` · Report (u15) | role | 🟩 |
| 16 | `skills/herd/roles/auditor.md` · The coordinator's checklist (u16) | role | 🟩 |
| 17 | `skills/herd/roles/auditor.md` · A falsify item (u17) | role | 🟩 |
| 18 | `skills/herd/roles/bond.md` · A bond: you and {{WORKER_NAME}} review each other (u18) | role | 🟩 |
| 19 | `skills/herd/roles/handoff.md` · Handing off to a new session (u19) | role | 🟩 |
| 20 | `skills/herd/roles/handoff.md` · If you're retiring (u20) | role | 🟩 |
| 21 | `skills/herd/roles/handoff.md` · If you're the one that stays (u21) | role | 🟩 |
| 22 | `skills/herd/roles/handoff.md` · If you're the new session (u22) | role | 🟩 |
| 23 | `skills/herd/roles/handoff.md` · In chat (u23) | role | 🟩 |
| 24 | `skills/herd/roles/orchestrator.md` · The orchestrator (u24) | role | 🟩 |
| 25 | `skills/herd/roles/readonly.md` · The reply of a session that can't write (u25) | role | 🟩 |
| 26 | `skills/herd/roles/reviewer.md` · (top) (u26) | role | 🟩 |
| 27 | `skills/herd/roles/reviewer.md` · Setting up (once, when this pair starts) (u27) | role | 🟩 |
| 28 | `skills/herd/roles/reviewer.md` · Each review (u28) | role | 🟩 |
| 29 | `skills/herd/roles/reviewer.md` · Limits (u29) | role | 🟩 |
| 30 | `skills/herd/roles/reviewer.md` · Who started you, and stopping (u30) | role | 🟩 |
| 31 | `skills/herd/roles/reviewer.md` · When the item says rigor: build (u31) | role | 🟩 |
| 32 | `skills/herd/roles/worker.md` · The worker, in a pair (u32) | role | 🟩 |
| 33 | `skills/herd/roles/worker.md` · When the item says rigor: build (u33) | role | 🟩 |
| 34 | `skills/herd/sections/launch-refused.md` · A launch is refused (u34) | section | 🟩 |
| 35 | `skills/herd/sections/orchestrator.md` · The orchestrator at a run's end, and in cloud runs (u35) | section | 🟩 |
| 36 | `skills/queue/SKILL.md` · The queue (u45) | skill | 🟩 |
| 37 | `skills/queue/SKILL.md` · Working the queue (u46) | skill | 🟩 |
| 38 | `skills/queue/SKILL.md` · Telling the owner what another session said (u47) | skill | 🟩 |
| 39 | `skills/queue/SKILL.md` · Questions for you (u48) | skill | 🟩 |
| 40 | `skills/queue/SKILL.md` · Staying reasonable (u49) | skill | 🟩 |
| 41 | `skills/queue/sections/asks.md` · Asking the owner to do something (u50) | section | 🟩 |
| 42 | `skills/queue/sections/field-trip.md` · Field Trip, and reading the owner as voice (u51) | section | 🟩 |
| 43 | `skills/queue/sections/setup.md` · Setting up a queue (u52) | section | 🟩 |

## 🗑️ Dropped

Skills: herder voice (u36 to u44). Commands, thin wrappers over skills or `meow` (u53 to u64).

`u36` · `u37` · `u38` · `u39` · `u40` · `u41` · `u42` · `u43` · `u44` · `u53` · `u54` · `u55` · `u56` · `u57` · `u58` · `u59` · `u60` · `u61` · `u62` · `u63` · `u64`

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| 4 skills: capture, herd, herder, queue | on demand, when invoked or matched | no | about 176 KB of text |
| 12 commands (`/meow`, `/board`, `/hike` and others) | when typed | no | about 8 KB |
| 0 agents | n/a | n/a | 0 |
| SessionStart hook | session start, resume, compact; prints only in a repo with a queue | no | ❓ |
| PreCompact and SessionEnd hooks | automatic compaction; session close | no | no output |
| `bin/meow` and `lib/cat_herder` | when run | no | the plugin's own tool |

## ✅ Do this

- ⬜ 1. Before installing, ask the author to keep each subagent's own pinned model (drop `claude-haiku-5-5` from the worker, reviewer and orchestrator roles and the queue skill's groom step), and to limit the retry-a-refused-action lines to non-destructive actions with the owner's go-ahead.
- ⬜ 2. Copy the 8 standing rules below into the reader's rules.
- ⬜ 3. Write the 2 small skills below if you want them.
- ⬜ 4. Treat the herder skill and the 12 commands as skipped.

Carrying-cost case: it hooks session start, but only prints in a repo with a queue and never reaches subagents, and more than one rule survives, so carrying it is defensible once the conflicts are fixed.

## 📋 Proposed rules patch

Placed in the reader's existing files, matching their numbering. Wording is mine, not the plugin's.

```diff
+ # examples/reader/rules/engineering.md
+ 8. **Keep refactors and behaviour changes apart.** A change that does both at once goes back to be split.
+ 9. **Do not simplify away safeguards.** Keep validation at trust boundaries, error handling that prevents data loss, and security measures.
+ 10. **Kill only what you started,** by pid. Never `pkill` or `killall` by pattern.
+ 11. **Keep shell commands plain:** one command per call, absolute paths instead of `cd`.
+
+ # examples/reader/rules/safety.md
+ 6. **A failed git login is a stop.** Report the remote and the error. Never add a key, a token, an https remote or a forwarded agent to get past it.
+ 7. **A go-ahead covers only what it named,** and lapses when that changes.
+ 8. **A refused action stays refused.** Do not hand it to another session to run.
+
+ # examples/reader/CLAUDE.md, under "How I like answers"
+ - When I must paste or run something, put it alone in a code block, exactly as typed, with no placeholder left for me to fill.
```

Proposed skills (names are my proposal; the dossier shows the reader keeps skills as `skills/<name>/SKILL.md`, as in `skills/release-notes`):

- `falsify-docs`: check a doc's claims by running each example, finding its test and breaking the code, and give each claim BACKED, UNTESTED, CONTRADICTED or UNTESTABLE.
- `readonly-report`: the fixed `## Report` form (outcome, base sha, patch, commands run, blocked by) for a session that cannot write.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
