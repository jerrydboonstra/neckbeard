# 🔍 ch-v0403 0.40.3 · vetted against the sample reader

> ## 🟧 INSTALL WITH CHANGES · keep the skills, copy four rules, fence one
> Three small hooks fire only on compaction and session end, and the plugin's three skills and one command are a working queue-and-review workflow the reader has nothing like. One reviewer line collides with a hard stop, and four general rules are worth copying as standing text.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-15` · neckbeard 1.14.0 · ch-v0403 0.40.3

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟨 | **Cost** | Three hooks, none resolved by the dossier (all run `bin/meow _hook`), so I read `lib/cat_herder/hooks.py`. PreCompact counts an automatic compaction silently. SessionStart (compact only) prints one short count line to the model, and only for a session on a queue roster. SessionEnd writes a note and prints nothing. Skill bodies load on demand: about 99 KB of text across 3 skills, 4 role files and 1 command. |
| 🟩 | **Reach** | Main session only (no hook event known to fire in a subagent). |
| 🟨 | **Leaves state** | A roster record update on compaction, a session-ended note in the machine's own state folder, and queue commits pushed to a git remote or local ref when `meow` writes. |
| 🟨 | **Live surface** | The `meow` CLI, git fetch and push to the queue remote, ssh and tmux launchers under `tools/` (`tools/remote-session`, `tools/cloud-launcher`, `tools/agy-launcher`), no MCP servers. |
| 🟩 | **Refused reads** | none |
| ⭐ | **Worth keeping** | 25 skill sections, 4 rules to copy |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **1** | 🟥 |
| 🔁 | **already covered** | **4** | ⬜⬜⬜⬜ |
| 🆕 | **new, standing rule** | **4** | 🟩🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **0** | none |
| 🗑️ | **dropped** (persona, extras, no value) | **8** | ⬛⬛⬛⬛⬛⬛⬛⬛ |

Skills kept: 25 of 33 units. The other 24 units hold nothing general beyond the plugin's own mechanics.

## ⛔ Conflicts: 1

| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| u16 | skills/herd/roles/reviewer.md, "Limits": "You may try the same action, on your own judgement, and report the result, allowed or refused, as a data point." (an action the worker's permission classifier refused) | "Never run anything destructive without my explicit go-ahead in this conversation" | examples/reader/rules/safety.md, rule 1 | 🟥 |

The reviewer line sets no limit to harmless actions, so a refused delete or force-push is retryable on the reviewer's own say-so. Keep the skill, and add "never a destructive action" to that one line if you adopt it.

## 🔁 Already covered: 4

| its rule | covered by | held in |
|---|---|---|
| skills/capture/SKILL.md, "Asked to do work yourself": work found along the way "is captured the same way, not done inline" | rule 4, the scope asked for is the deliverable (the closest statement as a rule in its own right) | examples/reader/rules/engineering.md |
| skills/herd/roles/worker.md, "The worker, in a pair": deprecation markers must end as removed or a debt comment with "its ceiling and upgrade path", and off-item work becomes its own item | rule 5, shortcuts marked with what breaks first and how to fix it; rule 4 for the scope half | examples/reader/rules/engineering.md |
| skills/queue/SKILL.md, "The queue": "Never act on a guessed reading of an irreversible command", and never put the queue on `main` | safety rules 1 and 5 (destructive needs a go-ahead, ask when ambiguous); rule 2 for the `main` refusal | examples/reader/rules/safety.md |
| skills/queue/SKILL.md, "Working the queue": a ready check that finds the premise moved means "don't build the old version" and wait; never `--force` unasked | engineering rule 4 (say what you would change and let me decide); safety rule 1 | examples/reader/rules/engineering.md, examples/reader/rules/safety.md |

## 🟩 Rules to copy: 4

| # | rule, quoted | from | |
|:--:|---|---|:--:|
| 1 | "A diff that both restructures code and changes behaviour, so you can't tell which lines do which, is a finding" (split the refactor out into its own change) | skills/herd/roles/reviewer.md, "Each review" | 🆕 |
| 2 | "Stop only the processes you started, by their PID, never by port." | skills/herd/roles/reviewer.md, "When the item says rigor: build" (the same line is in worker.md, same heading) | 🆕 |
| 3 | "Never simplify away validation at a trust boundary, error handling that prevents data loss, or a security measure." | skills/herd/roles/worker.md, "When the item says rigor: build" | 🆕 |
| 4 | "A question the owner skipped is unread, not answered" (do not take silence as a yes or a no, and do not act on it) | skills/queue/SKILL.md, "Staying reasonable" | 🆕 |

No new on-demand skill came out of the units.

## 🟩 Skills kept: 25

| # | section | kind | |
|:--:|---|:--:|:--:|
| u1 | skills/capture/SKILL.md, "Capture" | skill | 🟩 |
| u2 | skills/capture/SKILL.md, "An interruption, so keep it short" | skill | 🟩 |
| u3 | skills/capture/SKILL.md, "Asked to do work yourself: every session, not only the worker" | skill | 🟩 |
| u4 | skills/capture/SKILL.md, "Rescue session: everything this session was tracking" | skill | 🟩 |
| u5 | skills/capture/SKILL.md, "Stream-of-consciousness: the owner is riffing" | skill | 🟩 |
| u6 | skills/herd/SKILL.md, "Herd" | skill | 🟩 |
| u7 | skills/herd/roles/associate.md, "The associate" | skill | 🟩 |
| u8 | skills/herd/roles/handoff.md, "Handing off to a new session" | skill | 🟩 |
| u9 | skills/herd/roles/handoff.md, "If you're retiring" | skill | 🟩 |
| u10 | skills/herd/roles/handoff.md, "If you're the one that stays" | skill | 🟩 |
| u11 | skills/herd/roles/handoff.md, "If you're the new session" | skill | 🟩 |
| u12 | skills/herd/roles/handoff.md, "In chat" | skill | 🟩 |
| u13 | skills/herd/roles/reviewer.md, "(top)" | skill | 🟩 |
| u14 | skills/herd/roles/reviewer.md, "Setting up (once, when this pair starts)" | skill | 🟩 |
| u15 | skills/herd/roles/reviewer.md, "Each review" | skill | 🟩 |
| u16 | skills/herd/roles/reviewer.md, "Limits" | skill | 🟧 keep, with the u16 change |
| u17 | skills/herd/roles/reviewer.md, "Who started you, and stopping" | skill | 🟩 |
| u18 | skills/herd/roles/reviewer.md, "When the item says rigor: build" | skill | 🟩 |
| u19 | skills/herd/roles/worker.md, "The worker, in a pair" | skill | 🟩 |
| u20 | skills/herd/roles/worker.md, "When the item says rigor: build" | skill | 🟩 |
| u28 | skills/queue/SKILL.md, "The queue" | skill | 🟩 |
| u29 | skills/queue/SKILL.md, "Working the queue" | skill | 🟩 |
| u30 | skills/queue/SKILL.md, "Telling the owner what another session said" | skill | 🟩 |
| u32 | skills/queue/SKILL.md, "Staying reasonable" | skill | 🟩 |
| u33 | commands/meow.md, "(top)" | command | 🟩 |

## 🗑️ Dropped

`u21` skills/herder/SKILL.md "The herder" · `u22` "/herder and /herder off" · `u23` "Cat names" · `u24` "Capture" · `u25` "Leaving Cat Herder" · `u26` "Handoffs, in chat" · `u27` "The voice rule" · `u31` skills/queue/SKILL.md "Questions for you"

Units u21 to u27 are the cat-voice persona and its on/off switch. Unit u31 is one example bullet that only illustrates the ledger rule judged in u32.

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| PreCompact hook, `meow _hook precompact` | an automatic compaction | no | silent |
| SessionStart hook, `meow _hook sessionstart` (matcher: compact) | after a compaction, only for a rostered session | no | one short line |
| SessionEnd hook, `meow _hook sessionend` | a session closes | no | silent |
| skills/capture, skills/herd, skills/queue, skills/herder | on demand, by trigger phrase | no | 14,273 / 20,779 / 26,817 / 6,062 bytes |
| skills/herd/roles/*.md | read when a pair, hike or handoff starts | no | 29,805 bytes |
| commands/meow.md | when the user types `/meow` | no | 1,425 bytes |

## ✅ Do this

- ⬜ 1. Copy the four rules above into your engineering rules as standing text.
- ⬜ 2. If you install, add "never a destructive action" to the reviewer's retry line in skills/herd/roles/reviewer.md ("Limits"), or tell reviewers it is subject to examples/reader/rules/safety.md rule 1.
- ⬜ 3. Skip the `herder` skill; it is voice only.

Carrying-cost case: three hooks that print nothing outside a rostered session, so the weight is the on-demand skills; the four copied rules are cheap to carry as text, but the queue and review workflow only exists in the plugin, so install it and fence the one line.

## 📋 Proposed rules patch

Add to examples/reader/rules/engineering.md as rules 8 to 11 (it already has a numbered list of build rules, so these follow its numbering and bold lead-in):

```diff
+ 8. **Keep a refactor apart from a behaviour change.** A diff that mixes them is
+    split: the refactor first, the change after it.
+ 9. **Stop only the processes you started,** by their PID, never by port.
+ 10. **Never simplify away validation at a trust boundary, error handling that
+    prevents data loss, or a security measure.**
+ 11. **A question I skipped is unread, not answered.** Do not take silence as a
+    yes or a no, and do not act on it; carry on with whatever does not depend on it.
```

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
