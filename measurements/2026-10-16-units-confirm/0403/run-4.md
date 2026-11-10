# 🔍 ch-v0403 0.40.3 · vetted against the sample reader

> ## 🟧 INSTALL WITH CHANGES · keep the skills, add the limit the two conflicts lack
> Hooks run only at compaction and session end, so the standing cost is small; the skills load on demand. Two sentences in the reviewer and worker roles let a refused action be retried on the session's own judgement, which fights the reader's destructive-action stop. Six general rules are worth copying whatever you decide.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-16` · neckbeard 1.14.0 · ch-v0403 0.40.3

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟨 | **Cost** | Three hooks (PreCompact on auto, SessionStart on compact, SessionEnd); the dossier could not trace their payload, and the hook descriptions say a compaction count and an ended-session note, so injected size is unknown but small |
| 🟩 | **Reach** | Main session only (no hooked event is known to fire in a subagent) |
| 🟨 | **Leaves state** | Per-machine session state and the roster written by `bin/meow`; the queue is commits on a git branch or ref (36 writer files flagged) |
| 🟨 | **Live surface** | The `bin/meow` command, git fetch and push to the queue's remote, and one `/meow` slash command; no MCP servers |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 24 skill sections and 6 general rules |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **2** | ▰▰ |
| 🔁 | **already covered** | **0** | none |
| 🆕 | **new, standing rule** | **6** | ▰▰▰▰▰▰ |
| 🆕 | **new, on-demand skill** | **0** | none |
| 🟩 | **skill sections kept** | **24** of 33 | ▰ ×24 |
| 🗑️ | **dropped** (persona, extras, no value) | **9** | ▰▰▰▰▰▰▰▰▰ |

## ⛔ Conflicts: 2

| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| u16 | "You may try the same action, on your own judgement" (skills/herd/roles/reviewer.md, Limits). Ask for a limit: only when the action is not destructive, otherwise stop and ask the owner | "Never run anything destructive without my explicit go-ahead" | examples/reader/rules/safety.md | ⛔ |
| u19 | "The reviewer may try an action you reported as refused, on its own judgement" (skills/herd/roles/worker.md, The worker, in a pair). Ask for the same limit | "Never run anything destructive without my explicit go-ahead" | examples/reader/rules/safety.md | ⛔ |

## 🔁 Already covered: 0
None. The overlaps are partial (see the Keep notes), and each unit that overlaps also carries a rule the reader lacks.

## 🆕 Rules to copy: 6

| unit | file and heading | rule to copy | |
|:--:|---|---|:--:|
| u15 | skills/herd/roles/reviewer.md, Each review | "A diff that both restructures code and changes behaviour, so you can't tell which lines do which, is a finding" | 🆕 |
| u16 | skills/herd/roles/reviewer.md, Limits | "It lapses when what it covers changes." (a relayed owner go-ahead ends when its subject changes) | 🆕 |
| u18 | skills/herd/roles/reviewer.md, When the item says rigor: build | "Cite every claim you accept with a `file:line` and a quoted span." | 🆕 |
| u19 | skills/herd/roles/worker.md, The worker, in a pair | "Never ask the reviewer to run it for you: that would pass a refused action to another session." | 🆕 |
| u20 | skills/herd/roles/worker.md, When the item says rigor: build | "Never simplify away validation at a trust boundary, error handling that prevents data loss, or a security measure." | 🆕 |
| u32 | skills/queue/SKILL.md, Staying reasonable | "A question the owner skipped is unread, not answered." | 🆕 |

Units u16 and u19 appear twice on purpose: the sentence that conflicts is not the one worth copying.

## 🟩 Keep: 24 skill sections

| unit | file and heading | kind | |
|:--:|---|:--:|:--:|
| u1 | skills/capture/SKILL.md, Capture | skill | 🟩 |
| u2 | skills/capture/SKILL.md, An interruption, so keep it short | skill | 🟩 |
| u3 | skills/capture/SKILL.md, Asked to do work yourself | skill | 🟩 |
| u4 | skills/capture/SKILL.md, Rescue session | skill | 🟩 |
| u5 | skills/capture/SKILL.md, Stream-of-consciousness | skill | 🟩 |
| u6 | skills/herd/SKILL.md, Herd | skill | 🟩 |
| u7 | skills/herd/roles/associate.md, The associate | skill | 🟩 |
| u9 | skills/herd/roles/handoff.md, If you're retiring | skill | 🟩 |
| u10 | skills/herd/roles/handoff.md, If you're the one that stays | skill | 🟩 |
| u11 | skills/herd/roles/handoff.md, If you're the new session | skill | 🟩 |
| u12 | skills/herd/roles/handoff.md, In chat | skill | 🟩 |
| u13 | skills/herd/roles/reviewer.md, (top) | skill | 🟩 |
| u14 | skills/herd/roles/reviewer.md, Setting up | skill | 🟩 |
| u15 | skills/herd/roles/reviewer.md, Each review | skill | 🟩 |
| u16 | skills/herd/roles/reviewer.md, Limits | skill | 🟩 ⛔ |
| u17 | skills/herd/roles/reviewer.md, Who started you, and stopping | skill | 🟩 |
| u18 | skills/herd/roles/reviewer.md, When the item says rigor: build | skill | 🟩 |
| u19 | skills/herd/roles/worker.md, The worker, in a pair | skill | 🟩 ⛔ |
| u20 | skills/herd/roles/worker.md, When the item says rigor: build | skill | 🟩 |
| u28 | skills/queue/SKILL.md, The queue | skill | 🟩 |
| u29 | skills/queue/SKILL.md, Working the queue | skill | 🟩 |
| u30 | skills/queue/SKILL.md, Telling the owner what another session said | skill | 🟩 |
| u32 | skills/queue/SKILL.md, Staying reasonable | skill | 🟩 |
| u33 | commands/meow.md, (top) | command | 🟩 |

Each is the plugin's own workflow, works as shipped, and the reader has no queue, pair or review-loop skill; the reader's only skill is examples/reader/skills/release-notes/SKILL.md. The rigor: build sections overlap examples/reader/rules/engineering.md (reuse, root cause, a test seen to fail, `TODO(debt):`), but add the rules above.

## 🗑️ Dropped
`u8` · `u21` · `u22` · `u23` · `u24` · `u25` · `u26` · `u27` · `u31`

Seven are the herder skill's cat voice (persona); u8 only describes when a handoff happens; u31 is a sample ledger bullet.

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| hooks/claude-codex.json: PreCompact (auto), SessionStart (compact) | automatic compaction | no | unknown |
| hooks/claude.json: SessionEnd | session close | no | unknown |
| skills/capture | on demand | no | about 13.0k chars |
| skills/herd (with roles) | on demand | no | about 49.6k chars |
| skills/herder | on demand | no | about 5.6k chars |
| skills/queue | on demand | no | about 26.1k chars |
| commands/meow.md | when invoked | no | about 1.2k chars |

## ✅ Do this
- ⬜ 1. Before installing, ask the author to add a limit to the two retry sentences in u16 and u19 (only when the action is not destructive), or edit them after install.
- ⬜ 2. Add the six rules below to the reader's engineering rules whether or not you install.
- ⬜ 3. Skip the herder skill; it is only a cat voice.

Case: it has hooks, but they fire only at compaction and session end, and the payload is unknown rather than absent. Skill sections cost nothing until loaded, and 24 of them are kept, so installing beats copying the text.

## 📋 Proposed rules patch
Target: examples/reader/rules/engineering.md, which is a numbered list of how to build and work, so these continue the numbering after rule 7.
```
8. **Mixed diffs are a finding.** A change that both restructures code and
   changes behaviour, so you can't tell which lines do which, goes back to be split.
9. **A go-ahead lapses when what it covers changes.** Name what it covers
   (the item, the commit, the wording) and when it was given.
10. **Cite every claim you accept** with a file:line and a quoted span.
11. **A refused action stays refused.** Do not hand it to another session to run.
12. **Never simplify away validation at a trust boundary,** error handling that
    prevents data loss, or a security measure.
13. **A question that went unanswered is unread, not answered.** Do not act on
    silence as a yes or a no.
```

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
