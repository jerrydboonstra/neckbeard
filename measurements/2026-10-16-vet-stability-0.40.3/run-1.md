# 🔍 ch-v0403 0.40.3 · vetted against the sample reader

> ## 🟨 COPY RULES, SKIP PLUGIN · take four rules as text, install only for the queue itself
> Three quiet hooks and about 102 KB of skill text buy a git work queue, a pair-review loop and a cat-voice persona, none of which the reader asked for. Nothing collides with the reader's hard stops. Four generic rules and one small skill idea are new, and they are cheaper to copy than to carry.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-15` · neckbeard 1.14.0 · ch-v0403 0.40.3

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟨 | **Cost** | 3 hooks registered for Claude Code (PreCompact auto, SessionStart on compact, SessionEnd). Skills load on demand: capture 15.8 KB, herd 52.3 KB, queue 28.0 KB, herder 6.7 KB. Only the descriptions sit in context every session. |
| 🟩 | **Reach** | Main session only (likely): no hooked event is known to fire in a subagent. |
| 🟨 | **Leaves state** | Yes. PreCompact writes a compaction count to the session's roster record in the queue's local copy. SessionEnd writes a note to this machine's Cat Herder state folder. Both do nothing outside a roster session. |
| 🟩 | **Live surface** | No MCP servers. The `/meow` command runs only the `meow` CLI. The bundled launcher tools can start sessions over ssh, but only when asked. |
| 🟩 | **Refused reads** | none |
| 🟨 | **Worth keeping** | 5: four standing rules and one on-demand skill. |

The dossier could not trace the three hooks (❓ unidentifiable), so I read the hook module by hand. SessionStart can print one line to the model after a compaction, and only for a session on a roster. PreCompact and SessionEnd print nothing to the model.

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **0** | none |
| 🔁 | **already covered** | **9** | ⬜ ×9 |
| 🆕 | **new, standing rule** | **4** | 🟩🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **1** | 🟩 |
| 🗑️ | **dropped** (persona, extras, no value) | **8** | ⬛ ×8 |

## ⛔ Conflicts: 0
| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|

No conflicts. Nearest miss: the launcher starts a reviewer or successor "on opus" by default, while the reader says "Do not override" a pinned model on dispatch. That rule is about subagents, these are separate sessions, and the default never overrides a model the owner names and can be switched off, so I did not count it.

## 🔁 Already covered: 9
| its rule | covered by | held in |
|---|---|---|
| Source priority, no new dependency when a few lines do it (rigor build) | "Reuse before writing", rule 1, which also names the dependency step | examples/reader/rules/engineering.md |
| Bug fix finds every caller and fixes the root cause | "Fix the cause, not the symptom", rule 2 | examples/reader/rules/engineering.md |
| Debt comment naming ceiling and upgrade path, using the project's own marker | "Leave deliberate shortcuts marked", rule 5, and the target defers to `TODO(debt):` by name | examples/reader/rules/engineering.md |
| Reviewer reverts the change and watches the test fail | "seen to fail", rule 3 | examples/reader/rules/engineering.md |
| Splitting is bookkeeping, scope stays as asked, found work is captured not done inline | "The scope I asked for is the deliverable", rule 4 | examples/reader/rules/engineering.md |
| Never act on a guessed reading of an irreversible command, read it back | "explicit go-ahead", hard stop 1, chosen because it states the gate as a rule in its own right (hard stop 5 only covers ambiguity) | examples/reader/rules/safety.md |
| When an item is ambiguous or wrong, block with the question rather than guess | "ask", hard stop 5 | examples/reader/rules/safety.md |
| Never paste credentials, tokens or personal data in a done note | "Secrets never appear", hard stop 4 | examples/reader/rules/safety.md |
| Cite each accepted claim, list what you did not check | "without saying what was checked is not a review", How I like answers | examples/reader/CLAUDE.md |

## 🟩 Keep: 5
| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| 1 | Never simplify away validation at a trust boundary, error handling that prevents data loss, or a security measure (herd/roles/worker.md, rigor build) | rule | 🟩 |
| 2 | Evidence goes in raw: exact commands, exit codes and error text, not a paraphrase, and report what you observed, not "verified" (herd/roles/worker.md) | rule | 🟩 |
| 3 | Check whether a test, criterion or threshold was changed to make a result pass (herd/roles/reviewer.md) | rule | 🟩 ⭐ |
| 4 | Stop only the processes you started, by PID, never by port (both role files) | rule | 🟩 |
| 5 | Rescue the session: list unfinished work, match it against what the tracker already holds, add only what is new, ask when unsure, report counts (skills/capture/SKILL.md) | skill | 🟩 |

## 🗑️ Dropped
`skills/herder` (cat-voice persona) · `rules/cat-herder.mdc` (Cursor-only router) · `commands/meow.md` (drives the meow CLI only) · `skills/capture` levels, topics, riffing mode · `skills/queue` setup, claim, review, grooming · `skills/herd` pairs, hikes, handoffs, retrospection · launcher model default · spend and `--force` gates for meow commands

## 🧩 What it installs
| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| PreCompact hook, matcher auto | each automatic compaction | no | silent, writes a count |
| SessionStart hook, matcher compact | after a compaction | no | one line, roster sessions only (❓ exact bytes) |
| SessionEnd hook | session close | no | silent, writes a note |
| skills capture, herd, queue, herder | when invoked, descriptions always listed | no | 102,763 bytes of text |
| command /meow | when typed | no | 1,651 bytes |
| Antigravity and Cursor hooks, Cursor rule | other hosts only | no | not loaded by Claude Code |
| bin/meow, bin/repo-queue, tools | when run | no | CLI, not injected |

## ✅ Do this
- ⬜ 1. Copy rules 1 to 4 from Keep into the reader's rules file as text, and skip the plugin.
- ⬜ 2. Install it only if you want a shared git queue with paired review; then load it with `--plugin-dir` first and watch the hooks stay silent outside a roster.
- ⬜ 3. Decide whether the rescue skill is worth writing yourself; it needs a tracker to match against.

This is the "few rules, small cost" case: three hooks that stay quiet and do not reach subagents, and four rules you would likely have written yourself, so copying text beats carrying a queue system you do not use.

## 📋 Proposed rules patch
Target file: the reader's rules, in `examples/reader/rules/engineering.md`, which already holds how code gets written and is numbered 1 to 7. Append as 8 to 11, in its existing bold-lead style:

```diff
+8. **Keep validation and safeguards.** Never simplify away validation at a trust
+   boundary, error handling that prevents data loss, or a security measure.
+9. **Show raw evidence.** Report the exact commands, exit codes and error text,
+   not a paraphrase, and say what you observed, not that it is verified.
+10. **Do not move the goalposts.** If a test, criterion or threshold changed to
+    make a result pass, say so and why.
+11. **Stop only what you started.** Kill a process by its PID, never by port.
```

Proposed skill (the name is my proposal): `rescue-unfinished`, "List what this session left unfinished, compare it with the existing task list, add only what is new, ask about anything doubtful, and report counts. Never starts the work." The dossier names no folder for this reader's skills beyond `examples/reader/skills/`, which holds release-notes, so where it lives is your call.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
