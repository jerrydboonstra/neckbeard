# 🔍 ch-v0403 0.40.3 · vetted against the sample reader

> ## 🟧 INSTALL WITH CHANGES · drop one reviewer sentence, copy seven rules
> It costs a few lines after a compaction and 99 KB of on-demand skill text, and its hooks stay out of subagents. One sentence in the reviewer role collides with the reader's destructive-action stop. Seven of its rules are general and new to the reader, and 25 of its 33 sections are workflow skills that work as shipped.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-15` · neckbeard 1.14.0 · ch-v0403 0.40.3

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟩 | **Cost** | Hooks: a SessionStart hook (matcher `compact`) prints up to two short lines, about 100 to 300 bytes, after an automatic compaction, and only in a session on a queue's roster. PreCompact and SessionEnd print nothing. Skills and the command load on demand: about 99,000 bytes of text in all |
| 🟩 | **Reach** | Main session only (likely): no hooked event is known to fire in a subagent |
| 🟨 | **Leaves state** | PreCompact commits a roster record to the queue (a git write, after a fetch). SessionEnd appends a line to an `ended` file in the machine's state directory (`lib/cat_herder/ended.py`), pruned after 30 days |
| 🟨 | **Live surface** | Git fetch and push to the queue's remote over ssh or http; `bin/meow`; launchers that start other sessions (`tools/remote-session`, `tools/cloud-launcher`, ssh, tmux). No MCP servers |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 25 skill sections and 7 rules to copy |

The dossier listed all three hooks as unidentifiable, because each command is `bin/meow _hook <event>`. I read `lib/cat_herder/hooks.py` by hand to resolve them. `hooks.json` at the plugin root targets Antigravity, not Claude Code.

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **1** | 🟥 |
| 🔁 | **already covered** | **3** | ⬜⬜⬜ |
| 🆕 | **new, standing rule** | **7** | 🟩🟩🟩🟩🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **0** | none |
| 🗑️ | **dropped** (persona, extras, no value) | **8** | ⬛⬛⬛⬛⬛⬛⬛⬛ |

Skills kept: 25 of 33 units. A unit can sit in more than one grid: `skills/herd/roles/reviewer.md` "Limits" holds the conflict and also a rule to copy. The other 15 kept units appear only under Keep.

## ⛔ Conflicts: 1

| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| 1 | "A done note may report an action the worker's session was refused by its permission classifier. You may try the same action, on your own judgement, and report the result" | "Never run anything destructive without my explicit go-ahead in this conversation" | `skills/herd/roles/reviewer.md` "Limits" (u16), against `examples/reader/rules/safety.md` rule 1 | 🟥 |

The refused action is unnamed, so it may be the destructive kind the reader requires a go-ahead for. The reviewer is told to try it on its own judgement.

## 🆕 Rules to copy: 7

| # | unit | rule to copy | kind | |
|:--:|---|---|:--:|:--:|
| 1 | `skills/capture/SKILL.md` "An interruption, so keep it short" (u2) | "Facts come from the conversation or a file you checked; mark anything else as an assumption." | standing | 🟩 |
| 2 | `skills/herd/roles/reviewer.md` "Each review" (u15) | "A diff that both restructures code and changes behaviour, so you can't tell which lines do which, is a finding" | standing | 🟩 |
| 3 | `skills/herd/roles/reviewer.md` "Limits" (u16) | "It lapses when what it covers changes." (an owner's answer, once relayed, covers only the item, commit or wording it named) | standing | 🟩 |
| 4 | `skills/herd/roles/reviewer.md` "When the item says rigor: build" (u18) | "was a criterion, a test or a threshold changed to make it pass? Read the test diff." | standing | 🟩 |
| 5 | `skills/herd/roles/worker.md` "The worker, in a pair" (u19) | "Do the work, and attack it yourself first. A reviewer doesn't replace that." | standing | 🟩 |
| 6 | `skills/herd/roles/worker.md` "When the item says rigor: build" (u20) | "Never simplify away validation at a trust boundary, error handling that prevents data loss, or a security measure." | standing | 🟩 |
| 7 | `skills/queue/SKILL.md` "Staying reasonable" (u32) | "When a reply skips something you asked, don't take it as a yes or a no, and don't act on it." | standing | 🟩 |

## 🔁 Already covered: 3

| its rule | covered by | held in |
|---|---|---|
| Work found along the way is captured, not done inline (`skills/capture/SKILL.md` "Asked to do work yourself", u3) | "The scope I asked for is the deliverable." States scope as a rule in its own right | `examples/reader/rules/engineering.md` rule 4 |
| Read back an irreversible command that was matched by sound, and wait for a yes (`skills/queue/SKILL.md` "The queue", u28) | "If a request is ambiguous and the wrong reading is costly, ask." | `examples/reader/rules/safety.md` rule 5 |
| When a ready check says the premise moved, show the owner and wait (`skills/queue/SKILL.md` "Working the queue", u29) | "say what you would change and let me decide" | `examples/reader/rules/engineering.md` rule 4 |

Other overlap sits inside units judged new above. In `skills/herd/roles/worker.md` "When the item says rigor: build" (u20), four of the five coding rules repeat reader rules 1, 2 and 5. The debt marker there yields to the project's own (`TODO(debt):` in the reader), so it does not collide.

## 🟩 Keep: 25

| # | skill section | kind | |
|:--:|---|:--:|:--:|
| u1 | `skills/capture/SKILL.md` "Capture" | skill | 🟩 |
| u2 | `skills/capture/SKILL.md` "An interruption, so keep it short" | skill | 🟩 |
| u3 | `skills/capture/SKILL.md` "Asked to do work yourself: every session, not only the worker" | skill | 🟩 |
| u4 | `skills/capture/SKILL.md` "Rescue session: everything this session was tracking" | skill | 🟩 |
| u5 | `skills/capture/SKILL.md` "Stream-of-consciousness: the owner is riffing" | skill | 🟩 |
| u6 | `skills/herd/SKILL.md` "Herd" | skill | 🟩 |
| u7 | `skills/herd/roles/associate.md` "The associate" | role | 🟩 |
| u8 | `skills/herd/roles/handoff.md` "Handing off to a new session" | role | 🟩 |
| u9 | `skills/herd/roles/handoff.md` "If you're retiring" | role | 🟩 |
| u10 | `skills/herd/roles/handoff.md` "If you're the one that stays" | role | 🟩 |
| u11 | `skills/herd/roles/handoff.md` "If you're the new session" | role | 🟩 |
| u12 | `skills/herd/roles/handoff.md` "In chat" | role | 🟩 |
| u13 | `skills/herd/roles/reviewer.md` (top) | role | 🟩 |
| u14 | `skills/herd/roles/reviewer.md` "Setting up (once, when this pair starts)" | role | 🟩 |
| u15 | `skills/herd/roles/reviewer.md` "Each review" | role | 🟩 |
| u16 | `skills/herd/roles/reviewer.md` "Limits" | role | 🟨 |
| u17 | `skills/herd/roles/reviewer.md` "Who started you, and stopping" | role | 🟩 |
| u18 | `skills/herd/roles/reviewer.md` "When the item says rigor: build" | role | 🟩 |
| u19 | `skills/herd/roles/worker.md` "The worker, in a pair" | role | 🟩 |
| u20 | `skills/herd/roles/worker.md` "When the item says rigor: build" | role | 🟩 |
| u28 | `skills/queue/SKILL.md` "The queue" | skill | 🟩 |
| u29 | `skills/queue/SKILL.md` "Working the queue" | skill | 🟩 |
| u30 | `skills/queue/SKILL.md` "Telling the owner what another session said" | skill | 🟩 |
| u32 | `skills/queue/SKILL.md` "Staying reasonable" | skill | 🟩 |
| u33 | `commands/meow.md` (top) | command | 🟩 |

The role files are not skills of their own. They load when the `herd` skill points a session at them. u16 is 🟨 because it is kept with its one sentence removed.

## 🗑️ Dropped

`u21` The herder · `u22` /herder and /herder off · `u23` Cat names · `u24` Capture (voice lines) · `u25` Leaving Cat Herder · `u26` Handoffs, in chat (voice lines) · `u27` The voice rule · `u31` Questions for you (a sample ledger line)

All of `skills/herder/SKILL.md` is persona and voice, off by default. u31 only illustrates a format that u30 and u32 already describe.

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| Hook: SessionStart, matcher `compact` (`hooks/claude-codex.json`) | after an automatic compaction | no (likely) | about 100 to 300 B, roster sessions only |
| Hook: PreCompact, matcher `auto` (`hooks/claude-codex.json`) | before an automatic compaction | no (likely) | none printed; writes a roster record |
| Hook: SessionEnd (`hooks/claude.json`) | when a session closes | no (likely) | none printed; appends to `ended` |
| Skill `queue` | on demand | no | 26,817 B |
| Skill `herd`, plus 4 role files | on demand | no | 20,779 B, roles 29,805 B |
| Skill `capture` | on demand | no | 14,273 B |
| Skill `herder` | on demand | no | 6,062 B |
| Command `/meow` | on invocation | no | 1,425 B |

## ✅ Do this

- ⬜ 1. If you install, delete the sentence in `skills/herd/roles/reviewer.md` "Limits" that lets a reviewer retry a refused action on its own judgement. Without that edit the plugin collides with `examples/reader/rules/safety.md` rule 1.
- ⬜ 2. Copy the seven rules below into your own files, whether or not you install. Most are stated inside `rigor: build` or queue sections that load only while that skill is in use.
- ⬜ 3. Leave `skills/herder/SKILL.md` alone. Its voice stays off unless the owner turns it on.

Carrying-cost case: there are hooks, but they print only after a compaction in a roster session and do not reach subagents, so the standing cost is small. Seven rules clear the bar, so the question is whether you want the queue workflow itself, not whether the rules justify the hooks.

## 📋 Proposed rules patch

Add to `examples/reader/rules/engineering.md`, numbered on from rule 7 and bold-led like the others (an existing section about how code gets written):

```
8. **Attack your own work first.** A reviewer does not replace that.
9. **Keep restructuring and behaviour changes apart.** A diff that mixes them, so no one can tell which lines do which, gets split.
10. **Never simplify away validation at a trust boundary,** error handling that prevents data loss, or a security measure.
11. **Mark what you did not check.** Facts come from the conversation or a file you read; anything else is labelled an assumption.
12. **Read the test diff.** If a test, criterion or threshold changed to make a result pass, say so and why.
```

Add to `examples/reader/rules/safety.md`, after rule 5 (it has the stop-and-ask list):

```
6. **An approval covers only what it named.** An answer relayed from me quotes what it covers and lapses when that changes.
7. **A question I skip is unread, not a yes or a no.** Do not act on it. Ask again with the next reply.
```

No on-demand skills came out of Step 2.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
