# 🔍 ch-v0403 0.40.3 · vetted against the sample reader

> ## 🟨 COPY RULES, SKIP PLUGIN · take four build rules as text
> It costs little (about 2.5 KB of skill and command descriptions in every session, and hooks that stay silent unless a session is on a queue roster), and it fights none of the reader's rules. But nearly all of it is a git work queue driven by its own `meow` command, which the reader does not run, and what is left over is four generic build rules and one handoff idea that are cheaper to copy as text.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-15` · neckbeard 1.14.0 · ch-v0403 0.40.3

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟨 | **Cost** | About 2,460 bytes of skill and command names and descriptions, loaded every session. The four skills hold 67,931 bytes of text, read only when one triggers. No hook injects at session start. |
| 🟩 | **Reach** | Main session only (certain): no registered hook event fires in a subagent. |
| 🟨 | **Leaves state** | One line per closed session appended to an `ended` file in a per-user state folder, 30-day trim (`lib/cat_herder/ended.py`). Queue commits go to a git branch or remote when a queue is set up. |
| 🟨 | **Live surface** | No MCP servers. In a session on a queue roster, the PreCompact hook runs git fetch and a compare-and-swap push to the queue's remote (up to 15 s). The bundled launchers (`tools/remote-session`, `tools/cloud-launcher`) use ssh, tmux and cloud sessions when asked. |
| 🟩 | **Refused reads** | none |
| 🟨 | **Worth keeping** | 5 (4 rules, 1 skill) |

The dossier lists all three hooks as unidentifiable (each calls `bin/meow _hook ...`), so I read the handler, `lib/cat_herder/hooks.py`. PreCompact (auto only) counts a compaction on the roster and exits silently for any session not on it. SessionStart (compact only) prints one or two lines for a rostered session and nothing otherwise. SessionEnd (`hooks/claude.json`) only appends to the local `ended` file.

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **0** | none |
| 🔁 | **already covered** | **10** | ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ |
| 🆕 | **new, standing rule** | **4** | 🟩🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **1** | 🟩 |
| 🗑️ | **dropped** (persona, extras, no value) | **8** | ⬛⬛⬛⬛⬛⬛⬛⬛ |

## ⛔ Conflicts: 0

None. Nearest miss: a plain `meow accept` carries no stated check (`skills/herd/roles/reviewer.md`), but the same file makes a non-bare note mandatory for `rigor: build`, so it does not contradict `examples/reader/CLAUDE.md`.

## 🔁 Already covered: 10

| its rule | covered by | held in |
|---|---|---|
| Source priority, no new dependency if a few lines do it (`skills/herd/roles/worker.md`) | "Reuse before writing", rule 1 | `examples/reader/rules/engineering.md` |
| Bug fix fixes the root cause, find every caller (`worker.md`) | "Fix the cause, not the symptom", rule 2 | `examples/reader/rules/engineering.md` |
| Debt comment naming ceiling and upgrade path, using the project's own marker (`worker.md`) | "Leave deliberate shortcuts marked", rule 5; it even defers to `TODO(debt):` | `examples/reader/rules/engineering.md` |
| Verifier reverts the change and watches the test fail (`reviewer.md`) | "seen to fail", rule 3 | `examples/reader/rules/engineering.md` |
| Split work by dependency without growing it, capture side work instead of doing it inline, reread a stale brief and stop before building (`skills/capture/SKILL.md`, `skills/queue/SKILL.md`) | "The scope I asked for is the deliverable", rule 4 (it states the rule on its own; the plugin's wording is queue procedure) | `examples/reader/rules/engineering.md` |
| Replace secrets and tokens with a placeholder in done notes (`worker.md`) | "Secrets never appear in output", rule 4 | `examples/reader/rules/safety.md` |
| Remove finished clones only on the owner's go-ahead (`worker.md`, `handoff.md`) | "Never run anything destructive", rule 1 (deleting outside the working tree) | `examples/reader/rules/safety.md` |
| A relayed answer never stands in for the owner's word on a deploy or release (`worker.md`) | "Deploys happen only after", rule 3 | `examples/reader/rules/safety.md` |
| If the queue sits on the code's branch, stop before any write (`skills/queue/SKILL.md`) | "Never push to `main`", rule 2 | `examples/reader/rules/safety.md` |
| Blocked is a real answer: ask rather than guess; read an irreversible, guessed command back and wait for a yes (`worker.md`, `skills/queue/SKILL.md`) | "If a request is ambiguous", rule 5 | `examples/reader/rules/safety.md` |

Where two sources cover the same ground I cited the numbered rule, not `examples/reader/CLAUDE.md`, which only imports them.

## 🟩 Keep: 5

| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| 1 | Never simplify away validation at trust boundaries, error handling that prevents data loss, or a security measure (`worker.md`, rigor: build) | rule | 🆕 |
| 2 | Done notes paste the exact commands, exit codes and error text, and report what was observed, never the verdict (`worker.md`) | rule | 🆕 |
| 3 | A diff that mixes a refactor with a behaviour change gets split, refactor first (`reviewer.md`, `skills/capture/SKILL.md`) | rule | 🆕 |
| 4 | Stop only the processes you started, by PID, never by port (`worker.md`, `reviewer.md`) | rule | 🆕 |
| 5 | Write a handoff brief of what the record doesn't hold: working decisions, promises made, background tasks, what may have changed (`skills/herd/roles/handoff.md`) | skill | 🆕 |

## 🗑️ Dropped

`skills/herder/SKILL.md` (cat-name voice, persona) · `skills/capture/SKILL.md` apart from the rules above (levels, topics, riffing mode, rescue session; all need `meow`) · `skills/queue/SKILL.md` apart from the rules above (claims, ledger, overheard block, Field Trip, voice dictation; all need `meow`) · `skills/herd/SKILL.md` (pairs, hikes, supervisor inbox, introspection; all need `meow`) · `skills/herd/roles/*.md` apart from the rules above (pair and hike procedure) · `skills/herd/roles/associate.md` (domain routing between sessions) · `commands/meow.md` (runs `meow`) · `rules/cat-herder.mdc` (Cursor-only, always-on rule that does not load in Claude Code)

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| 4 skills (`capture`, `herd`, `herder`, `queue`) | descriptions every session; body when triggered | no | 67,931 B text |
| `/meow` command | on invoke only (`disable-model-invocation`) | no | 1,425 B |
| Hook PreCompact (auto) | each automatic compaction; silent unless rostered | no | no injection |
| Hook SessionStart (compact) | after a compaction; 0 to 2 lines, rostered sessions only | no | under 300 B |
| Hook SessionEnd | session close; local file append | no | no injection |
| `bin/meow`, `bin/repo-queue`, `bin/repoq` and `tools/` | when the skills run them | no | n/a |

## ✅ Do this

- ⬜ 1. Skip the plugin. Add the four rules in the patch below to `examples/reader/rules/engineering.md`.
- ⬜ 2. Decide whether to keep the handoff brief as a skill (proposal below).
- ⬜ 3. Revisit only if the reader wants a shared git work queue across several agent sessions; that is what the plugin is for, and the reader has none.

Carrying-cost case: the plugin has always-on cost (skill descriptions) but no session-start injection and no subagent reach, and several rules survive, none of which needs the plugin to work, so copy as text.

## 📋 Proposed rules patch

Rules go in `examples/reader/rules/engineering.md`, the existing file about how code gets built, continuing its numbered bold style.

```diff
 7. **Commit messages:** imperative subject under 60 characters, then why.
+8. **Never simplify away safety.** Keep validation at trust boundaries, error
+   handling that prevents data loss, and security measures, whatever else is
+   cut.
+9. **Done notes report what was seen.** Paste the exact commands, exit codes and
+   error text. Say "12 tests pass", not "verified".
+10. **Refactors travel alone.** If one change both restructures code and changes
+    behaviour, split the refactor out and land it first.
+11. **Stop only the processes you started,** by PID, never by port.
```

Proposed skill (the name is mine; the plugin names no such capability): `session-handoff-brief` · "Write the brief a successor session needs: the working decisions, promises made, background tasks, and what may have changed since they were written." The dossier shows the reader keeps skills in `examples/reader/skills/`, so `examples/reader/skills/session-handoff-brief/SKILL.md` fits; the choice is the reader's.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
