# 🔍 ch-v0403 0.40.3 · vetted against the sample reader

> ## 🟧 INSTALL WITH CHANGES · keep the queue skills, copy six rules, fix one reviewer line
> It injects nothing at session start and its hooks do not reach subagents. One unit collides with a reader rule, and eight are persona or sample text. The rest is queue mechanics, with six general rules worth copying as standing text.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-15` · neckbeard 1.14.0 · ch-v0403 0.40.3

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟩 | **Cost** | No injection at session start. After an automatic compaction, in a session on a queue's roster only, `SessionStart` prints one or two lines (compactions used, who started it). The dossier could not trace the three hook commands, so I read `lib/cat_herder/hooks.py` by hand. Skills load on demand: about 99 KB of text across four skills, five role files and one command. |
| 🟩 | **Reach** | Main session only (likely): no event it hooks is known to fire in a subagent. |
| 🟨 | **Leaves state** | `SessionEnd` writes an `ended` file in the plugin's machine state directory (`lib/cat_herder/ended.py`). `PreCompact` on a rostered session fetches the queue and pushes one commit to it. The queue itself is the product, so its commits and pushes are by design. |
| 🟨 | **Live surface** | No MCP servers. Git fetch and push to the queue remote from `PreCompact`, and `meow` plus launchers (ssh, tmux, `claude`) when the skills start sessions. `hooks.json` adds an Antigravity-only `PreToolUse` hook that allows everything elsewhere. |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 25 skill sections, and 6 general rules to copy |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **1** | 🟥 |
| 🔁 | **already covered** | **3** | ⬜⬜⬜ |
| 🆕 | **new, standing rule** | **6** | 🟩🟩🟩🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **0** | none |
| 🟩 | **skill sections kept** | **25** | ▰ ×25 |
| 🗑️ | **dropped** (persona, extras, no value) | **8** | ⬛⬛⬛⬛⬛⬛⬛⬛ |

The 33 units are judged on three separate questions (skill, conflicts, rules), so one unit can sit in more than one grid below. Skill sections kept (25) plus dropped (8) is the 33 units.

## ⛔ Conflicts: 1
| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| 1 | `skills/herd/roles/reviewer.md`, "Each review" (u15): "`meow accept <id> {{REVIEWER}}` when it's right" ends a default review with a bare accept and asks for no stated checks | "Give the reasoning with the verdict" and "a review that says 'looks fine' without saying what was checked is not a review" | examples/reader/CLAUDE.md | 🟥 |

The `rigor: build` section of the same file does ask for a cited, itemised verdict. The default path does not.

## 🔁 Already covered: 3
| its rule | covered by | held in |
|---|---|---|
| `skills/capture/SKILL.md`, "An interruption, so keep it short" (u2): a split is bookkeeping and "the scope they asked for stays the deliverable" | "The scope I asked for is the deliverable" (engineering rule 4). Chosen over the safety rules because it states the point as a rule of its own. | examples/reader/rules/engineering.md |
| `skills/queue/SKILL.md`, "The queue" (u28): read an irreversible command back when any part was matched by sound, and wait for a yes | "If a request is ambiguous and the wrong reading is costly, ask" (safety rule 5) | examples/reader/rules/safety.md |
| `skills/queue/SKILL.md`, "Working the queue" (u29): when a brief's premise has moved, show the owner and wait; never `--force` on your own | "say what you would change and let me decide" (engineering rule 4), with the hard stops in safety rule 1 for the `--force` half | examples/reader/rules/engineering.md |

## 🟩 Rules to copy: 6
| # | unit | rule to copy | kind |
|:--:|---|---|:--:|
| 1 | `skills/herd/roles/reviewer.md`, "Each review" | "A diff that both restructures code and changes behaviour, so you can't tell which lines do which, is a finding" | 🆕 standing |
| 2 | `skills/herd/roles/reviewer.md`, "Limits" | An approval you pass on names what it covers and when it was given: "It lapses when what it covers changes." | 🆕 standing |
| 3 | `skills/herd/roles/reviewer.md`, "When the item says rigor: build" | "was a criterion, a test or a threshold changed to make it pass? Read the test diff." | 🆕 standing |
| 4 | `skills/herd/roles/worker.md`, "The worker, in a pair" | "Never ask the reviewer to run it for you: that would pass a refused action to another session." | 🆕 standing |
| 5 | `skills/herd/roles/worker.md`, "When the item says rigor: build" | "Never simplify away validation at a trust boundary, error handling that prevents data loss, or a security measure." The other four coding rules there repeat engineering rules 1, 2 and 5. | 🆕 standing |
| 6 | `skills/queue/SKILL.md`, "Staying reasonable" | "When a reply skips something you asked, don't take it as a yes or a no, and don't act on it." | 🆕 standing |

## 🟩 Skill sections kept: 25
| # | section | kind |
|:--:|---|:--:|
| 1 | `skills/capture/SKILL.md`, "Capture" | skill |
| 2 | `skills/capture/SKILL.md`, "An interruption, so keep it short" | skill |
| 3 | `skills/capture/SKILL.md`, "Asked to do work yourself: every session, not only the worker" | skill |
| 4 | `skills/capture/SKILL.md`, "Rescue session: everything this session was tracking" | skill |
| 5 | `skills/capture/SKILL.md`, "Stream-of-consciousness: the owner is riffing" | skill |
| 6 | `skills/herd/SKILL.md`, "Herd" | skill |
| 7 | `skills/herd/roles/associate.md`, "The associate" | skill |
| 8 | `skills/herd/roles/handoff.md`, "Handing off to a new session" | skill |
| 9 | `skills/herd/roles/handoff.md`, "If you're retiring" | skill |
| 10 | `skills/herd/roles/handoff.md`, "If you're the one that stays" | skill |
| 11 | `skills/herd/roles/handoff.md`, "If you're the new session" | skill |
| 12 | `skills/herd/roles/handoff.md`, "In chat" | skill |
| 13 | `skills/herd/roles/reviewer.md`, top section | skill |
| 14 | `skills/herd/roles/reviewer.md`, "Setting up (once, when this pair starts)" | skill |
| 15 | `skills/herd/roles/reviewer.md`, "Each review" (⛔1) | skill |
| 16 | `skills/herd/roles/reviewer.md`, "Limits" | skill |
| 17 | `skills/herd/roles/reviewer.md`, "Who started you, and stopping" | skill |
| 18 | `skills/herd/roles/reviewer.md`, "When the item says rigor: build" | skill |
| 19 | `skills/herd/roles/worker.md`, "The worker, in a pair" | skill |
| 20 | `skills/herd/roles/worker.md`, "When the item says rigor: build" | skill |
| 21 | `skills/queue/SKILL.md`, "The queue" | skill |
| 22 | `skills/queue/SKILL.md`, "Working the queue" | skill |
| 23 | `skills/queue/SKILL.md`, "Telling the owner what another session said" | skill |
| 24 | `skills/queue/SKILL.md`, "Staying reasonable" | skill |
| 25 | `commands/meow.md`, top section | command |

## 🗑️ Dropped
`u21` · `u22` · `u23` · `u24` · `u25` · `u26` · `u27` · `u31`

Seven are the cat voice in `skills/herder/SKILL.md` (intro, switch, names, capture lines, leaving, handoff lines, euphemism rule), a persona with no value for the reader. `u31` is a one-row sample ledger inside `skills/queue/SKILL.md`, an illustration of a section already kept.

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| `SessionEnd` hook, `meow _hook sessionend` | a session closes (not clear or resume) | no | no output; one small state file |
| `PreCompact` hook (auto), `meow _hook precompact` | before an automatic compaction, rostered sessions only | no | no output; one fetch and one queue commit |
| `SessionStart` hook (compact), `meow _hook sessionstart` | after a compaction, rostered sessions only | no | one or two lines to the model |
| `PreToolUse` hook in `hooks.json` | Antigravity only; allows everything on other hosts | no | negligible |
| skills `capture`, `herd`, `herder`, `queue` | on demand | no | about 14 KB, 21 KB, 6 KB, 27 KB |
| herd role files (`associate`, `handoff`, `reviewer`, `worker`) | read when a session takes that role | no | about 2 KB, 5 KB, 9 KB, 13 KB |
| command `/meow` | when invoked | no | 1.4 KB |

## ✅ Do this
- ⬜ 1. Add the six rules above to the reader's rules if you do not adopt the plugin.
- ⬜ 2. If you do install it, change the default review path so an accept carries what was checked (conflict 1), and leave the `herder` voice off.
- ⬜ 3. Decide whether you want a git-backed work queue at all: the kept sections all drive the `meow` command, so they are no use without it.

Carrying-cost case: the plugin has hooks, but none runs at every session start and none reaches subagents, so it is neither the always-injecting case nor the zero-hooks case. Six rules survive, which makes copying them cheap, while the queue skills are a real capability the reader lacks.

## 📋 Proposed rules patch

Add to the reader's existing numbered list in `examples/reader/rules/engineering.md` (numbering and bold lead-ins match the file; the section is short, so they stay inline). Not applied.

```diff
+8. **Keep a refactor and a behaviour change in separate commits.** A diff that restructures code and changes behaviour at once cannot be reviewed.
+9. **An approval covers what it named.** Quote it, say when it was given, and treat it as lapsed when what it covers changes.
+10. **Check that a test was not bent to pass.** Read the test diff for a changed criterion, test or threshold.
+11. **A refused action stays refused.** Do not hand it to another session to run.
+12. **Never simplify away validation at a trust boundary,** error handling that prevents data loss, or a security measure.
+13. **A question I skip is unanswered, not a yes.** Do not act on it; ask again with the next one.
```

No on-demand skills to propose.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
