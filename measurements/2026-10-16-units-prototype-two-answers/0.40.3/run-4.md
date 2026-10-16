# 🔍 ch-v0403 0.40.3 · vetted against the sample reader

> ## 🟧 INSTALL WITH CHANGES · keep the queue skills, copy four rules, cut one retry rule
> The plugin adds three small hooks and about 68 KB of on-demand skill text, and none of it reaches subagents. One reviewer rule lets a session retry an action another session was refused, which the reader's destructive-action stop forbids. Four general rules are worth copying whatever you decide about the plugin.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-15` · neckbeard 1.14.0 · ch-v0403 0.40.3

Computed verdict line: INSTALL WITH CHANGES; skills kept 23 of 33; rules 1 / 4 / 0 / 3 / 25 (conflict / new-standing / new-skill-text / duplicate / none). I agree with it.

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟨 | **Cost** | No always-on text found. The three hooks run `bin/meow` on compaction and session end, and their output size is unknown (see below). The four skills (about 68 KB) and the `/meow` command load only when called. |
| 🟩 | **Reach** | Main session only. The dossier finds no hooked event that fires in a subagent. |
| 🟨 | **Leaves state** | Counts compactions in a roster record and notes ended sessions in per-machine state (`hooks/claude-codex.json`, `hooks/claude.json`). The queue itself is git commits on a branch or ref you choose. |
| 🟨 | **Live surface** | No MCP servers. `bin/meow` runs git and pushes to the queue remote. `tools/` holds launchers that use ssh and tmux. `commands/meow.md` runs one quoted `meow` call in Bash. |
| 🟩 | **Refused reads** | none |
| 🟨 | **Worth keeping** | 23 skill sections, plus 4 rules to copy |

The dossier lists all three hooks as unidentifiable (the command is `bin/meow _hook ...`, not a script path), so what they inject is unknown, not absent. Their manifests say they print a compaction count after a compaction and do nothing in a session that is not on a queue's roster.

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **1** | 🟥 |
| 🔁 | **already covered** | **3** | ⬜⬜⬜ |
| 🆕 | **new, standing rule** | **4** | 🟩🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **0** | none |
| 🟩 | **skill sections kept** | **23** | ▰ ×23 |
| 🗑️ | **dropped** (persona, wrappers, examples) | **10** | ▰▰▰▰▰▰▰▰▰▰ |

## ⛔ Conflicts: 1

| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| u16 | `skills/herd/roles/reviewer.md`, "Limits": "You may try the same action, on your own judgement, and report the result" (an action the worker's session was refused) | Never run anything destructive "without my explicit go-ahead in this conversation". The unit does not limit the retry to harmless actions, and a refused action may be exactly the destructive one. | `examples/reader/rules/safety.md` rule 1 | 🟥 |

The rest of that section (binding verdict, no `--force`, no edits to the worker's code) agrees with the reader. Cut the retry bullet, or limit it to read-only actions, before adopting the reviewer role.

## 🔁 Already covered: 3

| its rule | covered by | held in |
|---|---|---|
| u2 `skills/capture/SKILL.md`, "An interruption, so keep it short": "the scope they asked for stays the deliverable" | Rule 4, the scope you asked for is the deliverable. Chosen because it states the rule on its own. | `examples/reader/rules/engineering.md` |
| u28 `skills/queue/SKILL.md`, "The queue": "Never act on a guessed reading of an irreversible command" | Rule 5, ask when a wrong reading is costly, plus rule 1 for the destructive cases. | `examples/reader/rules/safety.md` |
| u29 `skills/queue/SKILL.md`, "Working the queue": "don't build the old version" when an item's premise moved | Rule 4, say what you would change and let me decide. | `examples/reader/rules/engineering.md` |

## 🆕 Rules to copy: 4

| # | unit | rule, quoted | kind | |
|:--:|---|---|:--:|:--:|
| u15 | `skills/herd/roles/reviewer.md`, "Each review" | "A diff that both restructures code and changes behaviour, so you can't tell which lines do which, is a finding" | standing | 🟩 |
| u18 | `skills/herd/roles/reviewer.md`, "When the item says rigor: build" | "Stop only the processes you started, by their PID, never by port." | standing | 🟩 |
| u20 | `skills/herd/roles/worker.md`, "When the item says rigor: build" | "Never simplify away validation at a trust boundary, error handling that prevents data loss, or a security measure." Same unit: no new dependency when a few lines do the job. | standing | 🟩 |
| u32 | `skills/queue/SKILL.md`, "Staying reasonable" | "A question the owner skipped is unread, not answered." Do not take it as a yes or a no, and do not act on it. | standing | 🟩 |

The other coding rules in u20 (source priority, root cause, debt comment) match rules 1, 2 and 5 of `examples/reader/rules/engineering.md`, and its debt-marker rule defers to a project's own marker, so it fits the reader's `TODO(debt):`.

## 🟩 Keep: 23

| # | skill section | kind | |
|:--:|---|:--:|:--:|
| u1 | `skills/capture/SKILL.md`, "Capture" | skill | 🟩 |
| u2 | `skills/capture/SKILL.md`, "An interruption, so keep it short" | skill | 🟩 |
| u3 | `skills/capture/SKILL.md`, "Asked to do work yourself" | skill | 🟩 |
| u4 | `skills/capture/SKILL.md`, "Rescue session" | skill | 🟩 |
| u5 | `skills/capture/SKILL.md`, "Stream-of-consciousness" | skill | 🟩 |
| u6 | `skills/herd/SKILL.md`, "Herd" | skill | 🟩 |
| u7 | `skills/herd/roles/associate.md`, "The associate" | skill | 🟩 |
| u9 | `skills/herd/roles/handoff.md`, "If you're retiring" | skill | 🟩 |
| u10 | `skills/herd/roles/handoff.md`, "If you're the one that stays" | skill | 🟩 |
| u11 | `skills/herd/roles/handoff.md`, "If you're the new session" | skill | 🟩 |
| u12 | `skills/herd/roles/handoff.md`, "In chat" | skill | 🟩 |
| u13 | `skills/herd/roles/reviewer.md`, "(top)" | skill | 🟩 |
| u14 | `skills/herd/roles/reviewer.md`, "Setting up" | skill | 🟩 |
| u15 | `skills/herd/roles/reviewer.md`, "Each review" | skill | 🟩 |
| u16 | `skills/herd/roles/reviewer.md`, "Limits" (minus the retry bullet) | skill | 🟧 |
| u17 | `skills/herd/roles/reviewer.md`, "Who started you, and stopping" | skill | 🟩 |
| u18 | `skills/herd/roles/reviewer.md`, "When the item says rigor: build" | skill | 🟩 |
| u19 | `skills/herd/roles/worker.md`, "The worker, in a pair" | skill | 🟩 |
| u20 | `skills/herd/roles/worker.md`, "When the item says rigor: build" | skill | 🟩 |
| u28 | `skills/queue/SKILL.md`, "The queue" | skill | 🟩 |
| u29 | `skills/queue/SKILL.md`, "Working the queue" | skill | 🟩 |
| u30 | `skills/queue/SKILL.md`, "Telling the owner what another session said" | skill | 🟩 |
| u32 | `skills/queue/SKILL.md`, "Staying reasonable" | skill | 🟩 |

These are the plugin's own workflow skills. They need its `meow` command, which is not a reason to drop them. The herd model default (opus for reviewers a launcher starts, in u6) governs sessions the plugin starts, not a subagent dispatch, so it does not collide with rule 6 of `examples/reader/rules/engineering.md`.

## 🗑️ Dropped

`u8` (describes when a handoff happens, nothing to follow) · `u21` · `u22` · `u23` · `u24` · `u25` · `u26` · `u27` (the cat voice, persona) · `u31` (a worked ledger example) · `u33 (/meow command, a wrapper that only runs meow)`

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| `skills/capture` | on call or trigger phrase | no | 14 KB |
| `skills/herd` and its role files | on call or trigger phrase | no | 21 KB |
| `skills/herder` | on call | no | 6 KB |
| `skills/queue` | on call or trigger phrase | no | 27 KB |
| `commands/meow.md` | on `/meow` | no | 1 KB |
| hook `PreCompact` (auto) | before an automatic compaction | no | unknown |
| hook `SessionStart` (compact) | after a compaction | no | unknown |
| hook `SessionEnd` | when a session closes | no | unknown |

## ✅ Do this

- ⬜ 1. Copy the four rules in the patch below into your engineering rules.
- ⬜ 2. If you install the plugin, remove or narrow the retry bullet in `skills/herd/roles/reviewer.md` ("Limits"), since it collides with the reader's destructive-action stop.
- ⬜ 3. Read the three `bin/meow _hook ...` handlers (`lib/cat_herder/hooks.py`) before installing, since the dossier could not resolve what they inject.
- ⬜ 4. Skip the `herder` voice skill and the `/meow` wrapper.

Cost case: the hooks add a small, unmeasured injection after compaction, but the skills load only on demand and the plugin has well over one rule you would have written yourself, so the carrying cost is worth weighing and the plugin is worth installing with the change above.

## 📋 Proposed rules patch

The reader's `examples/reader/rules/engineering.md` is a numbered list under one "Engineering" heading, so the new rules go at the end of that list (my proposal, matching its numbering and bold lead-ins):

```
8. **Keep refactors and behaviour changes in separate changes.** If a diff
   restructures code and changes behaviour so you cannot tell which lines do
   which, split the refactor out.
9. **Never simplify away validation at a trust boundary,** error handling that
   prevents data loss, or a security measure. Add no dependency when a few
   lines do the job.
10. **Stop only the processes you started,** by PID, never by port.
11. **A question I skipped is unread, not answered.** Do not take silence as a
    yes or a no, and do not act on it; ask again.
```

No on-demand skills came out of Step 2.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
