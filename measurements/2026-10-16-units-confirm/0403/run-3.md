# 🔍 ch-v0403 0.40.3 · vetted against the sample reader

> ## 🟧 INSTALL WITH CHANGES · keep the skills, copy seven rules, fix two sentences
> Three small hooks, no subagent reach, and 24 of 33 units are workflow sections that work as shipped. Two sentences let a reviewer retry a refused action on its own judgement, which fights the reader's rule against destructive actions without a go-ahead. Seven general rules are worth copying as standing rules.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-16` · neckbeard 1.14.0 · ch-v0403 0.40.3

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟨 | **Cost** | Three hooks (PreCompact, SessionStart on compact, SessionEnd) run `bin/meow _hook`. Only SessionStart prints to the model, after a compaction, to say how many compactions the session has used. The dossier could not trace the scripts (❓), so this comes from reading `lib/cat_herder/hooks.py`. Skill text loads on demand only. |
| 🟩 | **Reach** | Main session only (no hooked event fires in a subagent) |
| 🟨 | **Leaves state** | Per-session roster and an `ended` log in the machine's state, and queue commits to a git branch or ref when `meow` is used. No writes found from the hooks beyond local state |
| 🟨 | **Live surface** | `meow` CLI, git pushes to the queue remote, launcher scripts that use ssh and tmux. No MCP servers |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 24 skill sections and 7 rules to copy |

## 🧮 How its rules sorted

Units, not rules: 33 sections of the target's instruction files, each judged once. A unit can sit in more than one grid below (the two conflicting units also carry a rule to copy and are kept).

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **2** | 🟥🟥 |
| 🔁 | **already covered** | **2** | ⬜⬜ |
| 🆕 | **new, standing rule** | **7** | 🟩🟩🟩🟩🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **0** | none |
| 🗑️ | **dropped** (persona, extras, no value) | **9** | ⬛⬛⬛⬛⬛⬛⬛⬛⬛ |

Skills kept beside these: **24** of 33 units.

## ⛔ Conflicts: 2

| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| u16 | "You may try the same action, on your own judgement, and report the result, allowed or refused, as a data point." | "Never run anything destructive without my explicit go-ahead in this conversation" | examples/reader/rules/safety.md (rule 1) | ⛔ |
| u19 | "The reviewer may try an action you reported as refused, on its own judgement, and report what happened." | the same rule | examples/reader/rules/safety.md (rule 1) | ⛔ |

Both permit with no limit. Ask for one: a reviewer may retry a refused action only when it is non-destructive, and anything destructive waits for the owner's go-ahead in the conversation.

## 🔁 Already covered: 2

| its rule | covered by | held in |
|---|---|---|
| u2 `skills/capture/SKILL.md` "An interruption, so keep it short": splitting is bookkeeping and the scope asked for stays the deliverable | "The scope I asked for is the deliverable" (the rule stated in its own right) | examples/reader/rules/engineering.md (rule 4) |
| u3 `skills/capture/SKILL.md` "Asked to do work yourself": work found along the way is captured, not done inline | the same scope rule | examples/reader/rules/engineering.md (rule 4) |

## 🆕 Rules to copy: 7

| unit | rule, quoted | why the reader lacks it |
|---|---|---|
| u15 `skills/herd/roles/reviewer.md` "Each review" | "A diff that both restructures code and changes behaviour, so you can't tell which lines do which, is a finding" | Nothing keeps a refactor apart from a behaviour change |
| u16 `skills/herd/roles/reviewer.md` "Limits" | "name exactly what it covers" and "It lapses when what it covers changes." | safety.md asks for a go-ahead but never scopes it |
| u18 `skills/herd/roles/reviewer.md` "When the item says rigor: build" | "was a criterion, a test or a threshold changed to make it pass?" | No rule against relaxing a test to get a pass |
| u19 `skills/herd/roles/worker.md` "The worker, in a pair" | "attack it yourself first. A reviewer doesn't replace that." | No self-review rule |
| u20 `skills/herd/roles/worker.md` "When the item says rigor: build" | "Never simplify away validation at a trust boundary, error handling that prevents data loss, or a security measure." | engineering.md has no rule protecting validation. Its other four coding rules match engineering.md rules 1, 2 and 5 |
| u29 `skills/queue/SKILL.md` "Working the queue" | "Its premise moved, or it's bigger now: don't build the old version." | Nothing covers a brief that went stale |
| u32 `skills/queue/SKILL.md` "Staying reasonable" | "A question the owner skipped is unread, not answered." | safety.md rule 5 says to ask, not what silence means |

## 🟩 Skills kept: 24

| # | section | kind | |
|:--:|---|:--:|:--:|
| u1 | `skills/capture/SKILL.md` "Capture" | skill | 🟩 |
| u2 | `skills/capture/SKILL.md` "An interruption, so keep it short" | skill | 🟩 |
| u3 | `skills/capture/SKILL.md` "Asked to do work yourself: every session, not only the worker" | skill | 🟩 |
| u4 | `skills/capture/SKILL.md` "Rescue session: everything this session was tracking" | skill | 🟩 |
| u5 | `skills/capture/SKILL.md` "Stream-of-consciousness: the owner is riffing" | skill | 🟩 |
| u6 | `skills/herd/SKILL.md` "Herd" | skill | 🟩 |
| u7 | `skills/herd/roles/associate.md` "The associate" | skill | 🟩 |
| u8 | `skills/herd/roles/handoff.md` "Handing off to a new session" | skill | 🟩 |
| u9 | `skills/herd/roles/handoff.md` "If you're retiring" | skill | 🟩 |
| u10 | `skills/herd/roles/handoff.md` "If you're the one that stays" | skill | 🟩 |
| u11 | `skills/herd/roles/handoff.md` "If you're the new session" | skill | 🟩 |
| u12 | `skills/herd/roles/handoff.md` "In chat" | skill | 🟩 |
| u13 | `skills/herd/roles/reviewer.md` "(top)" | skill | 🟩 |
| u14 | `skills/herd/roles/reviewer.md` "Setting up (once, when this pair starts)" | skill | 🟩 |
| u15 | `skills/herd/roles/reviewer.md` "Each review" | skill | 🟩 |
| u16 | `skills/herd/roles/reviewer.md` "Limits" (⛔1) | skill | 🟧 |
| u17 | `skills/herd/roles/reviewer.md` "Who started you, and stopping" | skill | 🟩 |
| u18 | `skills/herd/roles/reviewer.md` "When the item says rigor: build" | skill | 🟩 |
| u19 | `skills/herd/roles/worker.md` "The worker, in a pair" (⛔1) | skill | 🟧 |
| u20 | `skills/herd/roles/worker.md` "When the item says rigor: build" | skill | 🟩 |
| u28 | `skills/queue/SKILL.md` "The queue" | skill | 🟩 |
| u29 | `skills/queue/SKILL.md` "Working the queue" | skill | 🟩 |
| u30 | `skills/queue/SKILL.md` "Telling the owner what another session said" | skill | 🟩 |
| u32 | `skills/queue/SKILL.md` "Staying reasonable" | skill | 🟩 |

## 🗑️ Dropped

u21 · u22 · u23 · u24 · u25 · u26 · u27 (the Cat Herder voice and persona in `skills/herder/SKILL.md`) · u31 (`skills/queue/SKILL.md` "Questions for you", only an example ledger entry) · u33 (the `meow` command, a wrapper around the CLI)

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| Hook `_hook precompact` | before an automatic compaction | no | writes a count to local state |
| Hook `_hook sessionstart` (matcher compact) | after a compaction | no | a short notice to the model |
| Hook `_hook sessionend` | session close | no | one line to a local log |
| Skills capture, herd, herder, queue | on demand | no | about 100 KB of text across 4 skills |
| Command `meow` | when typed | no | about 1.2 KB |

## ✅ Do this

- ⬜ 1. Install the plugin only if you will run a Cat Herder queue; its skills need the `meow` tool and do nothing without it.
- ⬜ 2. Before relying on the reviewer role, ask the author to limit u16 and u19 to non-destructive retries, or edit those two sentences in your copy.
- ⬜ 3. Copy the seven rules below into your own rules.

Carrying-cost case: the hooks fire only on compaction and session end and never reach subagents, so the cost is small, and the value is in the skills plus seven rules you can copy either way.

## 📋 Proposed rules patch

Proposed for `examples/reader/rules/engineering.md`, which already holds how-to-work rules, continuing its numbering (the reader's rules 1 to 7 exist; these would be 8 to 14):

```
8. **Keep a refactor apart from a behaviour change.** A change that does both, so you can't tell which lines do which, is split: the refactor first, then the change.
9. **A go-ahead covers what it named.** Quote it, say what it covers (the item, the commit, the wording) and when it was given. It lapses when what it covers changes.
10. **Never relax a criterion, a test or a threshold to make it pass.** Read the test diff for that before accepting.
11. **Attack your own work before handing it over.** A reviewer does not replace that.
12. **Never simplify away validation at a trust boundary, error handling that prevents data loss, or a security measure.**
13. **Reread an old brief before building it.** If its premise moved or the job grew, do not build the old version: say what changed and let me decide.
14. **A question I skipped is unread, not answered.** Do not act on it as a yes or a no; ask again.
```

No new on-demand skills.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
