# 🔍 ch-v0403 0.40.3 · vetted against the sample reader

> ## 🟩 INSTALL · adopt the queue as a tool, add three small rules
> Nothing in it collides with the reader's rules, ten of its rules repeat ones the reader already runs, and the always-on cost is about 2.4 KB of skill descriptions. The hooks stay out of subagents and say something only after a compaction, inside a session that is on a queue. Three general rules are new and worth copying (validation, dependencies, spending), and three skills give a shared git work queue the reader does not have.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-15` · neckbeard 1.14.0 · ch-v0403 0.40.3

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟩 | **Cost** | About 2.4 KB of skill descriptions (capture 978 B, herd 566 B, queue 581 B, herder 240 B) each session. The hooks add one or two lines (under 300 B) after an automatic compaction, and only in a session on a queue's roster. |
| 🟩 | **Reach** | Main session only (certain for hooks: none of PreCompact, SessionStart or SessionEnd fires in a subagent). |
| 🟨 | **Leaves state** | SessionEnd records ended sessions in a per-user state directory (`lib/cat_herder/ended.py`). PreCompact writes a compaction count to the queue's git remote, roster sessions only. |
| 🟨 | **Live surface** | `bin/meow` runs git fetch and push against the queue remote, and starts reviewer sessions through a launcher the owner names. No MCP servers. |
| 🟩 | **Refused reads** | None. |
| 🟩 | **Worth keeping** | 6: three rules and three skills. |

The dossier listed all three hooks as unidentifiable, because each calls `bin/meow _hook <event>`. I read `lib/cat_herder/hooks.py` by hand: every hook exits 0 on any error, and PreCompact and SessionStart do nothing outside a roster session.

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **0** | none |
| 🔁 | **already covered** | **10** | ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ |
| 🆕 | **new, standing rule** | **3** | 🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **3** | 🟩🟩🟩 |
| 🗑️ | **dropped** (persona, extras, no value) | **8** | ⬛⬛⬛⬛⬛⬛⬛⬛ |

## ⛔ Conflicts: 0

None found. Two came close and were checked. The queue skill's riffing mode keeps replies to a line and defers questions to a ledger, but it builds, merges and drops nothing on a reply the owner has not read, so it keeps examples/reader/rules/safety.md rule 5 ("ask"). The default model for sessions it starts is a launch preference the owner overrides, not a subagent dispatch, so it does not touch examples/reader/rules/engineering.md rule 6.

## 🔁 Already covered: 10

| its rule | covered by | held in |
|---|---|---|
| Source priority: reuse the repo, standard library, platform, installed dependency first (`skills/herd/roles/worker.md`, rigor build) | rule 1, "Reuse before writing" | examples/reader/rules/engineering.md |
| Bug fix fixes the root cause, find every caller (`skills/herd/roles/worker.md`) | rule 2, "Fix the cause, not the symptom" | examples/reader/rules/engineering.md |
| Deliberate corner gets a debt comment naming ceiling and upgrade path, using the project's own marker (`skills/herd/roles/worker.md`) | rule 5, `TODO(debt):` plus what breaks first and how to fix it. I chose it because it states the rule on its own, and the target defers to it when a project names a marker. | examples/reader/rules/engineering.md |
| A test must be seen to fail: revert the change and watch it go red (`skills/herd/roles/reviewer.md`) | rule 3, "seen to fail" | examples/reader/rules/engineering.md |
| Work found along the way is captured, not done inline; a split adds no scope, and out-of-scope findings are suggestions only (`skills/capture/SKILL.md`, `skills/herd/roles/reviewer.md`) | rule 4, "The scope I asked for is the deliverable" | examples/reader/rules/engineering.md |
| Never paste credentials, tokens or personal data into a done note (`skills/herd/roles/worker.md`) | rule 4, "Secrets never appear" | examples/reader/rules/safety.md |
| Never run `meow herd clean` on your own, since it deletes folders outside the working tree (`skills/herd/roles/worker.md`) | rule 1, "Never run anything destructive" | examples/reader/rules/safety.md |
| Never put the queue on the branch the code is on, so no queue write is a push to main (`skills/queue/SKILL.md`) | rule 2, "Never push to `main`" | examples/reader/rules/safety.md |
| An unsure item goes on the ledger as a question, and a guessed reading of an irreversible command waits for a yes (`skills/capture/SKILL.md`, `skills/queue/SKILL.md`) | rule 5, "If a request is ambiguous ... ask" | examples/reader/rules/safety.md |
| A reviewer cites every accepted claim with `file:line` and a quoted span (`skills/herd/roles/reviewer.md`) | "A review that says 'looks fine' ... is not a review" | examples/reader/CLAUDE.md |

## 🟩 Keep: 6

| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| 1 | Never simplify away validation at a trust boundary, error handling that prevents data loss, or a security measure (`skills/herd/roles/worker.md`) | rule | 🟩 |
| 2 | No new dependency when a few lines do the job (`skills/herd/roles/worker.md`) | rule | 🟩 |
| 3 | Starting anything that costs money while it runs, or publishes, needs the owner's yes (`skills/herd/SKILL.md`, `skills/queue/SKILL.md`). The reader's rule 3 covers deploys only. | rule | 🟩 |
| 4 | `capture`: park new work in one exchange and return to the task, plus rescue session | skill | 🟩 |
| 5 | `queue`: set up, list, claim, finish, review and reorder items in a git-backed queue | skill | 🟩 |
| 6 | `herd`: pair a worker with a reviewer whose verdict binds, take items in a row, hand off | skill | 🟩 |

## 🗑️ Dropped

`herder` skill (cat voice, off by default) · `commands/meow.md` (a thin wrapper, the skills already run `meow`) · default model for sessions it starts (a preference, no collision with engineering rule 6) · Overheard block format · "Questions for you" ledger footer · Field Trip phone rules · handling of untrusted `.repoq` config (internal to the tool) · introspection and retrospection pass

These come along inside the skills if you install. The ledger footer and the Overheard block change reply shape, but only in a repo that has a queue.

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| 4 skills (`capture`, `herd`, `herder`, `queue`) | descriptions each session, bodies on trigger | no (likely) | 2.4 KB descriptions, about 87 KB of bodies |
| `/meow` command (`commands/meow.md`) | only when you type it | no | 1.4 KB |
| PreCompact hook, matcher auto (`hooks/claude-codex.json`) | automatic compaction, roster sessions only | no | writes a count, injects nothing |
| SessionStart hook, matcher compact (`hooks/claude-codex.json`) | after a compaction, roster sessions only | no | under 300 B |
| SessionEnd hook (`hooks/claude.json`) | a session closes | no | writes one local record, injects nothing |

`AGENTS.md` and `rules/cat-herder.mdc` instruct the plugin's own developers and Cursor, and Claude Code does not load them into the reader's sessions.

## ✅ Do this

- ⬜ 1. Install it if you want a shared work queue across agent sessions. Keep the queue on its own branch or remote: `init` refuses `main`, which fits your rule 2.
- ⬜ 2. Add the three rules below to examples/reader/rules/engineering.md, or to the safety file for the spending gate.
- ⬜ 3. Leave the voice and Field Trip settings off, as they ship.

Carrying-cost case: it injects at every session start, through skill descriptions, but three rules survive that you would keep, and the queue itself is the larger value, so installing beats copying.

## 📋 Proposed rules patch

I would put the first two in examples/reader/rules/engineering.md, continuing its numbering, and the third in examples/reader/rules/safety.md. Both files are short, so they stay inline.

```diff
 # Engineering (examples/reader/rules/engineering.md)
 7. **Commit messages:** imperative subject under 60 characters, then why.
+8. **Never simplify away safeguards.** Keep validation at trust boundaries, error handling that prevents data loss, and security measures, whatever else gets trimmed.
+9. **No new dependency when a few lines do the job.**

 # Safety: hard stops (examples/reader/rules/safety.md)
 5. **If a request is ambiguous and the wrong reading is costly, ask.** Do not
    pick the cheaper reading and carry on.
+6. **Ask before spending or publishing.** Starting a paid or long-running session, a paid API call, or anything that publishes needs my yes in this conversation.
```

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
