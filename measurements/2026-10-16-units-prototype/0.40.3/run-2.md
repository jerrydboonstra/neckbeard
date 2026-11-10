# 🔍 ch-v0403 0.40.3 · vetted against the sample reader

> ## 🟩 INSTALL · keep the workflow skills as shipped
> Computed from the unit answers: 25 units are the plugin's own working skills and command, none conflicts with a reader rule, and 8 are cat-voice persona text that is dropped. The one cost to settle is three hooks (compaction and session end) whose scripts could not be read from the dossier.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-15` · neckbeard 1.14.0 · ch-v0403 0.40.3

## ⚡ At a glance

| | | |
|:--:|---|---|
| ❓ | **Cost** | Skills load on demand: capture 14,273 bytes, herd 20,779, queue 26,817, herder 6,062, plus the /meow command at 1,425. Three hooks run `bin/meow _hook ...` on auto-compaction (PreCompact), after a compaction (SessionStart, matcher `compact`) and at SessionEnd; none resolved, so what they inject is unknown |
| 🟩 | **Reach** | Main session only: no SubagentStart hook, and no event known to fire in a subagent |
| ❓ | **Leaves state** | The queue itself is commits on a git branch or ref (and a roster of sessions); 36 scripts match file-write patterns and were not read one by one |
| 🟨 | **Live surface** | No MCP servers. It runs its own `meow` command, pushes queue and work branches to the project's git remotes, and bundles launchers that use ssh and tmux (`tools/remote-session`) |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 25 units (the capture, herd, queue skills, their role files and the /meow command) |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **0** | none |
| 🟩 | **kept as shipped** (the plugin's own skills and command) | **25** | ▰ ×25 |
| 🆕 | **new, standing rule** | **0** | none |
| 🆕 | **new, on-demand skill** | **0** | none |
| 🔁 | **already covered** | **0** | none |
| 🗑️ | **dropped** (persona, extras, no value) | **8** | ▰▰▰▰▰▰▰▰ |

## ⛔ Conflicts: 0

No unit tells the model to do what a reader rule forbids, or the reverse, in a situation where both apply. Near misses, and why each is not a conflict:

| it says | reader rule | why not |
|---|---|---|
| `skills/herd/SKILL.md` (Herd): "start the reviewer, or the new session, on opus" unless the owner names a model | `examples/reader/rules/engineering.md`, "Subagents run on the model their definition pins" | Rule 6 governs a dispatch call to a subagent. This starts a separate session through a launcher, and it is a default the owner overrides |
| `skills/herd/roles/worker.md` (The worker, in a pair): "Start the pair once (the owner's go-ahead covers it)" | `examples/reader/rules/safety.md`, ask before a costly or ambiguous step | The sentence itself says the owner's go-ahead is needed, and `skills/queue/SKILL.md` repeats "never without the yes" |
| `skills/herd/roles/worker.md` (When the item says rigor: build): split work that needs "more than four checks" | `examples/reader/rules/engineering.md`, "The scope I asked for is the deliverable" | The split is into queue items that together cover the same work, which `skills/capture/SKILL.md` calls "bookkeeping, not new scope" |

## 🔁 Already covered: 0

| its rule | covered by | held in |
|---|---|---|
| none | | |

## 🟩 Keep: 25

New standing rules: 0. New on-demand skills of the reader's own: 0. Kept as shipped, because each is part of one of the plugin's own skills or its command, works as shipped, and does something no reader rule or skill does:

| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| u1 | `skills/capture/SKILL.md`, Capture | skill | 🟩 |
| u2 | `skills/capture/SKILL.md`, An interruption, so keep it short | skill | ⭐ |
| u3 | `skills/capture/SKILL.md`, Asked to do work yourself | skill | 🟩 |
| u4 | `skills/capture/SKILL.md`, Rescue session | skill | 🟩 |
| u5 | `skills/capture/SKILL.md`, Stream-of-consciousness | skill | 🟩 |
| u6 | `skills/herd/SKILL.md`, Herd | skill | 🟩 |
| u7 | `skills/herd/roles/associate.md`, The associate | skill | 🟩 |
| u8 | `skills/herd/roles/handoff.md`, Handing off to a new session | skill | 🟩 |
| u9 | `skills/herd/roles/handoff.md`, If you're retiring | skill | 🟩 |
| u10 | `skills/herd/roles/handoff.md`, If you're the one that stays | skill | 🟩 |
| u11 | `skills/herd/roles/handoff.md`, If you're the new session | skill | 🟩 |
| u12 | `skills/herd/roles/handoff.md`, In chat | skill | 🟩 |
| u13 | `skills/herd/roles/reviewer.md`, (top) | skill | 🟩 |
| u14 | `skills/herd/roles/reviewer.md`, Setting up | skill | 🟩 |
| u15 | `skills/herd/roles/reviewer.md`, Each review | skill | ⭐ |
| u16 | `skills/herd/roles/reviewer.md`, Limits | skill | 🟩 |
| u17 | `skills/herd/roles/reviewer.md`, Who started you, and stopping | skill | 🟩 |
| u18 | `skills/herd/roles/reviewer.md`, When the item says rigor: build | skill | 🟩 |
| u19 | `skills/herd/roles/worker.md`, The worker, in a pair | skill | 🟩 |
| u20 | `skills/herd/roles/worker.md`, When the item says rigor: build | skill | 🟩 |
| u28 | `skills/queue/SKILL.md`, The queue | skill | 🟩 |
| u29 | `skills/queue/SKILL.md`, Working the queue | skill | ⭐ |
| u30 | `skills/queue/SKILL.md`, Telling the owner what another session said | skill | 🟩 |
| u32 | `skills/queue/SKILL.md`, Staying reasonable | skill | 🟩 |
| u33 | the /meow command | command | 🟩 |

## 🗑️ Dropped

`u21` · `u22` · `u23` · `u24` · `u25` · `u26` · `u27` · `u31`

All but u31 are the `skills/herder/SKILL.md` cat voice: persona and wording, no working procedure. u31 is a sample ledger entry in `skills/queue/SKILL.md` that serves as an example.

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| `skills/capture/SKILL.md` | when invoked or triggered by "queue that" and similar | no | 14,273 B |
| `skills/herd/SKILL.md` (+ role files read on demand) | when invoked: pairs, hikes, handoffs | no | 20,779 B |
| `skills/queue/SKILL.md` | when invoked: queue setup and work | no | 26,817 B |
| `skills/herder/SKILL.md` | when the owner asks for the voice | no | 6,062 B |
| `/meow` command | when typed | no | 1,425 B |
| hooks: PreCompact (auto), SessionStart (compact), SessionEnd | at those events | no | unknown |
| `bin/meow` and `lib/`, `tools/` | when the skills call them | no | not measured |

## ✅ Do this

- ⬜ 1. Read what `bin/meow _hook precompact`, `sessionstart` and `sessionend` print or write before enabling the hooks; the dossier could not trace them.
- ⬜ 2. Install the plugin for the capture, herd and queue skills and the /meow command. Skip or ignore the herder voice skill if you do not want the cat persona.
- ⬜ 3. Test it in a throwaway repo first: setting up a queue creates a branch on a remote, and pair starts cost money while a reviewer runs.

Carrying-cost case: hooks exist but run only on compaction and session end, and do not reach subagents. Their content is unknown, so the cost is unmeasured, not zero. The skills load on demand, and the value is in the skills themselves, not in rules to copy out.

## 📋 Proposed rules patch

Nothing to add: no unit was a new standing rule. One optional line lives inside a kept unit (u20), "Never simplify away validation at a trust boundary, error handling that prevents data loss, or a security measure", which the reader's rules do not state. The reader could copy it into `examples/reader/rules/engineering.md` as a new numbered rule if wanted, but it is not required for the verdict.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
