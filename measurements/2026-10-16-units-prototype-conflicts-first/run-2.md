# 🔍 ch-v0403 0.40.3 · vetted against the sample reader

> ## 🟩 INSTALL · keep the plugin as shipped
> Nothing in it breaks a rule the sample reader runs. It adds no always-on text, and its three hooks stay silent unless a session is on a queue roster. 25 of its 33 sections are working skills the reader lacks, and 6 rules in them are worth copying as standing text.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-15` · neckbeard 1.14.0 · ch-v0403 0.40.3

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟩 | **Cost** | No text injected at session start. After an automatic compaction, one short notice reaches the model, and only in a session on a queue roster (`lib/cat_herder/hooks.py`) |
| 🟩 | **Reach** | Main session only (likely): no hooked event fires in a subagent |
| 🟨 | **Leaves state** | A compaction count on the roster record, and a session-end note in this machine's state (`hooks/claude-codex.json`, `hooks/claude.json`); the plugin's `meow` command also writes queue commits to the repo's git remote |
| 🟨 | **Live surface** | The `meow` command (git fetch and push to the queue remote), plus launcher scripts under `tools/` that use ssh and tmux when the owner sets one up |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 25 skill sections and 6 standing rules |

The dossier listed all three hooks as unidentifiable, since each calls `bin/meow`. I read their text in `hooks/claude-codex.json`, `hooks/claude.json` and `lib/cat_herder/hooks.py`. The PreCompact hook counts an automatic compaction and prints nothing. The SessionStart hook (compact only) tells the model how many compactions it has used. The SessionEnd hook records that the session closed, with no network call and no git.

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **0** | none |
| 🔁 | **already covered** | **3** | ⬜⬜⬜ |
| 🆕 | **new, standing rule** | **6** | 🟩🟩🟩🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **0** | none |
| 🗑️ | **dropped** (persona, extras, no value) | **8** | ⬛⬛⬛⬛⬛⬛⬛⬛ |

Skills kept: 25 of 33 sections. Units dropped: 8.

## ⛔ Conflicts: 0
None found. Every section was read sentence by sentence against `examples/reader/rules/safety.md`, `examples/reader/rules/engineering.md` and `examples/reader/CLAUDE.md`.

Three near misses are not conflicts. The plugin starts its reviewer on Opus unless told otherwise (`skills/herd/SKILL.md`), which sets a session's model and is not a subagent dispatch, so engineering rule 6 does not apply. Its debt comment defers to a marker the project names (`skills/herd/roles/worker.md`), and the reader names `TODO(debt):`. Its reviewer may retry an action a worker's classifier refused (`skills/herd/roles/reviewer.md`), which collides with the destructive-action stop only if the action is destructive, and the sentence does not say so.

## 🔁 Already covered: 3
| its rule | covered by | held in |
|---|---|---|
| u5 riffing mode: "Nothing is built, merged, dropped or released on a reply nobody read" (`skills/capture/SKILL.md`) | hard stops on destructive work and deploys | examples/reader/rules/safety.md (rules 1 and 3) |
| u28 stop before a queue write that would push to main (`skills/queue/SKILL.md`) | never push to `main` | examples/reader/rules/safety.md (rule 2) |
| u29 read a guessed irreversible command back and wait for a yes (`skills/queue/SKILL.md`) | ask when the wrong reading is costly | examples/reader/rules/safety.md (rule 5) |

## 🟩 Rules to copy: 6
| # | unit | rule | kind |
|:--:|---|---|:--:|
| 1 | u15 `skills/herd/roles/reviewer.md`, "Each review" | "A diff that both restructures code and changes behaviour, so you can't tell which lines do which, is a finding" | 🆕 standing |
| 2 | u16 `skills/herd/roles/reviewer.md`, "Limits" | "It lapses when what it covers changes." (a relayed approval names what it covers) | 🆕 standing |
| 3 | u18 `skills/herd/roles/reviewer.md`, "When the item says rigor: build" | "Write \"I claim X; the failure I fear is Y\", then try to produce Y." | 🆕 standing |
| 4 | u19 `skills/herd/roles/worker.md`, "The worker, in a pair" | "Never ask the reviewer to run it for you: that would pass a refused action to another session." | 🆕 standing |
| 5 | u20 `skills/herd/roles/worker.md`, "When the item says rigor: build" | "Never simplify away validation at a trust boundary, error handling that prevents data loss, or a security measure." | 🆕 standing |
| 6 | u32 `skills/queue/SKILL.md`, "Staying reasonable" | "A question the owner skipped is unread, not answered." | 🆕 standing |

## 🟩 Skills kept: 25
| # | section | kind | |
|:--:|---|:--:|:--:|
| u1 | `skills/capture/SKILL.md`, "Capture" | skill | 🟩 |
| u2 | `skills/capture/SKILL.md`, "An interruption, so keep it short" | skill | 🟩 |
| u3 | `skills/capture/SKILL.md`, "Asked to do work yourself" | skill | 🟩 |
| u4 | `skills/capture/SKILL.md`, "Rescue session" | skill | 🟩 |
| u5 | `skills/capture/SKILL.md`, "Stream-of-consciousness" | skill | 🟩 |
| u6 | `skills/herd/SKILL.md`, "Herd" | skill | 🟩 |
| u7 | `skills/herd/roles/associate.md`, "The associate" | skill | 🟩 |
| u8 | `skills/herd/roles/handoff.md`, "Handing off to a new session" | skill | 🟩 |
| u9 | `skills/herd/roles/handoff.md`, "If you're retiring" | skill | 🟩 |
| u10 | `skills/herd/roles/handoff.md`, "If you're the one that stays" | skill | 🟩 |
| u11 | `skills/herd/roles/handoff.md`, "If you're the new session" | skill | 🟩 |
| u12 | `skills/herd/roles/handoff.md`, "In chat" | skill | 🟩 |
| u13 | `skills/herd/roles/reviewer.md`, "(top)" | skill | 🟩 |
| u14 | `skills/herd/roles/reviewer.md`, "Setting up" | skill | 🟩 |
| u15 | `skills/herd/roles/reviewer.md`, "Each review" | skill | 🟩 |
| u16 | `skills/herd/roles/reviewer.md`, "Limits" | skill | 🟩 |
| u17 | `skills/herd/roles/reviewer.md`, "Who started you, and stopping" | skill | 🟩 |
| u18 | `skills/herd/roles/reviewer.md`, "When the item says rigor: build" | skill | 🟩 |
| u19 | `skills/herd/roles/worker.md`, "The worker, in a pair" | skill | 🟩 |
| u20 | `skills/herd/roles/worker.md`, "When the item says rigor: build" | skill | 🟩 |
| u28 | `skills/queue/SKILL.md`, "The queue" | skill | 🟩 |
| u29 | `skills/queue/SKILL.md`, "Working the queue" | skill | 🟩 |
| u30 | `skills/queue/SKILL.md`, "Telling the owner what another session said" | skill | 🟩 |
| u32 | `skills/queue/SKILL.md`, "Staying reasonable" | skill | 🟩 |
| u33 | `commands/meow.md`, "(top)" | command | 🟩 |

## 🗑️ Dropped
`u21` · `u22` · `u23` · `u24` · `u25` · `u26` · `u27` (the cat voice and persona in `skills/herder/SKILL.md`) · `u31` (one example ledger bullet in `skills/queue/SKILL.md`)

## 🧩 What it installs
| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| skills `capture`, `herd`, `herder`, `queue` | on demand, when triggered or named | no | 4 files |
| command `/meow` | when the owner types it | no | 1 file |
| hook PreCompact (auto) | before an automatic compaction | no | small, silent |
| hook SessionStart (compact) | after a compaction, only on a roster | no | one short notice |
| hook SessionEnd | when a session closes | no | silent |

## ✅ Do this
- ⬜ 1. Install the plugin if you want a git-backed work queue, and leave the `herder` skill off or unused, since it only adds voice.
- ⬜ 2. Copy the 6 standing rules in the patch below, because a rule inside an on-demand skill applies only while that skill is loaded.

Carrying-cost case: the plugin has hooks, but they are silent unless a session is on a roster, they do not reach subagents, and at least one rule survives that you would have written yourself.

## 📋 Proposed rules patch
The reader keeps its building rules in `examples/reader/rules/engineering.md`, a numbered list with a bold lead on each item. I propose appending these there as items 8 to 13, in that style:

```
8. **Split a diff that restructures and changes behaviour.** If a reviewer cannot tell which lines do which, the refactor is its own change and the behaviour change waits on it.
9. **An approval covers what it names and lapses when that changes.** When you pass one on, quote it, name the item or commit it covers, and say when it was given.
10. **Name the failure you fear.** Write "I claim X; the failure I fear is Y", then try to produce Y.
11. **A refused action stays refused.** Never hand it to another session to run for you.
12. **Never simplify away validation at a trust boundary,** error handling that prevents data loss, or a security measure.
13. **A question I skipped is unread, not answered.** Do not act on it; ask again with the next one.
```

No on-demand skill came out of this run. Provenance stays in this report, and the patch is a proposal only: nothing was written to a rules file.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
