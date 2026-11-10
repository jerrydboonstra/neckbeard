# 🔍 ch-v0403 0.40.3 · vetted against the sample reader

> ## 🟩 INSTALL · keep as shipped, nothing to add to the reader's rules
> The 33 sections judged sort to 0 conflicts, 24 plugin workflow sections worth keeping and 9 dropped (the cat voice and wrappers). The three hooks do nothing in a session that is not on a queue's roster, and none reaches subagents.
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-15` · neckbeard 1.14.0 · ch-v0403 0.40.3

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟨 | **Cost** | Four skill descriptions (about 2.5 KB) in the session listing; the hooks inject text only after an automatic compaction in a rostered session (two short lines at most) |
| 🟩 | **Reach** | Main session only (no hooked event fires in a subagent) |
| 🟨 | **Leaves state** | SessionEnd appends a line to a file in the machine's state folder (`lib/cat_herder/ended.py`); PreCompact commits to the queue branch, only for rostered sessions |
| 🟨 | **Live surface** | PreCompact runs `git fetch` and a push to the queue remote (15 s deadline) in rostered sessions; skills run the `meow` command; `/meow` runs one quoted `meow` call |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 24 sections: 4 skills and 1 command |

The hook commands could not be traced by the script (all three show as unidentifiable), so I read them by hand in `lib/cat_herder/hooks.py`: each exits 0 on any failure and does nothing outside a git repo with a queue.

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **0** | none |
| 🛠️ | **kept as shipped** (own skills and command) | **24** | 🟩 ×24 |
| 🆕 | **new, standing rule** | **0** | none |
| 🆕 | **new, on-demand skill** | **0** | none |
| 🔁 | **already covered** | **0** | none |
| 🗑️ | **dropped** (persona, extras, no value) | **9** | ⬛⬛⬛⬛⬛⬛⬛⬛⬛ |

## ⛔ Conflicts: 0
None found. Two near misses, each a different situation from the reader rule it resembles: `skills/herd/SKILL.md` starts reviewers on a default model, which governs a session it launches, while `examples/reader/rules/engineering.md` rule 6 governs a subagent dispatch call; and `skills/herd/roles/worker.md` defers to the project's own debt marker, which fits `examples/reader/rules/engineering.md` rule 5 (`TODO(debt):`).

## 🔁 Already covered: 0
None. Parts of `skills/herd/roles/worker.md` ("Five coding rules") and `skills/herd/roles/reviewer.md` (the test must fail without the change) restate `examples/reader/rules/engineering.md` rules 1, 2, 3 and 5, but each sits in a section that also holds tool-specific procedure, so the section is kept.

## 🟩 Keep: 24
| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| u1 | `skills/capture/SKILL.md` · Capture | skill | 🟩 |
| u2 | `skills/capture/SKILL.md` · An interruption, so keep it short | skill | 🟩 |
| u3 | `skills/capture/SKILL.md` · Asked to do work yourself: every session, not only the worker | skill | 🟩 |
| u4 | `skills/capture/SKILL.md` · Rescue session: everything this session was tracking | skill | 🟩 |
| u5 | `skills/capture/SKILL.md` · Stream-of-consciousness: the owner is riffing | skill | 🟩 |
| u6 | `skills/herd/SKILL.md` · Herd | skill | 🟩 |
| u7 | `skills/herd/roles/associate.md` · The associate | skill | 🟩 |
| u9 | `skills/herd/roles/handoff.md` · If you're retiring | skill | 🟩 |
| u10 | `skills/herd/roles/handoff.md` · If you're the one that stays | skill | 🟩 |
| u11 | `skills/herd/roles/handoff.md` · If you're the new session | skill | 🟩 |
| u12 | `skills/herd/roles/handoff.md` · In chat | skill | 🟩 |
| u13 | `skills/herd/roles/reviewer.md` · (top) | skill | 🟩 |
| u14 | `skills/herd/roles/reviewer.md` · Setting up (once, when this pair starts) | skill | 🟩 |
| u15 | `skills/herd/roles/reviewer.md` · Each review | skill | 🟩 |
| u16 | `skills/herd/roles/reviewer.md` · Limits | skill | 🟩 |
| u17 | `skills/herd/roles/reviewer.md` · Who started you, and stopping | skill | 🟩 |
| u18 | `skills/herd/roles/reviewer.md` · When the item says rigor: build | skill | 🟩 |
| u19 | `skills/herd/roles/worker.md` · The worker, in a pair | skill | 🟩 |
| u20 | `skills/herd/roles/worker.md` · When the item says rigor: build | skill | 🟩 |
| u28 | `skills/queue/SKILL.md` · The queue | skill | 🟩 |
| u29 | `skills/queue/SKILL.md` · Working the queue | skill | 🟩 |
| u30 | `skills/queue/SKILL.md` · Telling the owner what another session said | skill | 🟩 |
| u32 | `skills/queue/SKILL.md` · Staying reasonable | skill | 🟩 |
| u33 | `commands/meow.md` · (top) | command | 🟩 |

## 🗑️ Dropped
`u8` · `u21` · `u22` · `u23` · `u24` · `u25` · `u26` · `u27` · `u31`

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| skill `capture` | on invoke; description always listed | no | 14.3 KB |
| skill `herd` (with `roles/`) | on invoke; description always listed | no | 20.8 KB |
| skill `herder` | on invoke; description always listed | no | 6.1 KB |
| skill `queue` | on invoke; description always listed | no | 26.8 KB |
| command `/meow` | on invoke | no | 1.4 KB |
| hook PreCompact (auto) | automatic compaction, rostered sessions write | no | script |
| hook SessionStart (compact) | after a compaction, prints counts and the parent session | no | script |
| hook SessionEnd | session close, one local state line | no | script |

## ✅ Do this
- ⬜ 1. Install the plugin; the cat voice (`herder`) stays off unless the owner asks for it.
- ⬜ 2. Test it in one session with `--plugin-dir` before a global install, and run `/reload-plugins` in running sessions afterward.

Case: hooks present, main session only, and many sections worth keeping, so the carrying cost is worth paying.

## 📋 Proposed rules patch
Nothing to add.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
