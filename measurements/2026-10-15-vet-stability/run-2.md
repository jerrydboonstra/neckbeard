# 🔍 ch-v0532 0.53.2 · vetted against the sample reader

> ## 🟨 COPY RULES, SKIP PLUGIN · take four general rules and one skill, leave the queue system
> The plugin costs almost nothing in a repo without a Cat Herder queue, but its value is the `meow` queue and review loop, which the reader does not run. Three of its instructions collide with the reader's rules, and four standing rules plus one on-demand skill are new and stand without `meow`.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-15` · neckbeard 1.14.0 · ch-v0532 0.53.2

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟨 | **Cost** | Estimated, not measured: the dossier could not trace the three hooks, so I read `lib/cat_herder/hooks.py` and `lib/cat_herder/rules.py`. SessionStart injects about 0.8 KB (five rules and framing) only in a repo with a queue, plus about 0.5 KB more after a compaction. Elsewhere it injects nothing. The four skill descriptions add about 1.8 KB to every session |
| 🟩 | **Reach** | Main session only (likely): no hooked event is known to fire in a subagent |
| 🟨 | **Leaves state** | SessionEnd writes an "ended" record to a machine state directory outside the project. PreCompact commits and pushes a compaction count to the queue branch, for sessions on a roster. `meow` also creates scratch clones and test receipts under the git directory |
| 🟨 | **Live surface** | No MCP servers. `bin/meow` runs git against queue and code remotes, `gh run list`, and a launcher that can start sessions over tmux or ssh |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 5: four standing rules and one on-demand skill |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **3** | 🟥🟥🟥 |
| 🔁 | **already covered** | **7** | ⬜⬜⬜⬜⬜⬜⬜ |
| 🆕 | **new, standing rule** | **4** | 🟩🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **1** | 🟩 |
| 🗑️ | **dropped** (persona, extras, no value) | **19** | ▰ ×19 |

## ⛔ Conflicts: 3

| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| 1 | After a deploy, run `meow herd respawn` "unasked", which parks and replaces every live session (`skills/herd/SKILL.md`) | Rule 4: "say what you would change and let me decide" | examples/reader/rules/engineering.md | 🟥 |
| 2 | The orchestrator section ends "Act first, report after" (`skills/herd/SKILL.md`) | Rule 5: "ask" when the wrong reading is costly, not "carry on" | examples/reader/rules/safety.md | 🟥 |
| 3 | Groom hands scans to "the cheapest capable model" chosen on the dispatch call (`skills/queue/SKILL.md`) | Rule 6: "Do not override it on the dispatch call" | examples/reader/rules/engineering.md | 🟨 |

Row 3 is the weakest: a generic scan agent has no pinned definition, so it only collides in spirit.

## 🔁 Already covered: 7

| its rule | covered by | held in |
|---|---|---|
| Never use `--force` on your own; relay the refusal and wait (`skills/queue/SKILL.md`) | Rule 1, "explicit go-ahead". Chosen over the intro line because rule 1 is the one that names overriding a safeguard | examples/reader/rules/safety.md |
| `integrate cleanup` deletes remote branches only after a dry run and the owner's go-ahead (`skills/herd/SKILL.md`) | Rule 1, which names force-pushing and deleting | examples/reader/rules/safety.md |
| Ask the owner before adding a refactor as its own item, since it "widens what was asked" (`skills/capture/SKILL.md`) | Rule 4, scope is the deliverable | examples/reader/rules/engineering.md |
| Work found along the way is queued, not done inline (`skills/capture/SKILL.md`) | Rule 4, do not widen unasked | examples/reader/rules/engineering.md |
| Do not set up a queue, run `admin upgrade` or lower `min_writer` unasked (`skills/queue/SKILL.md`) | Rule 4, say it and let the owner decide | examples/reader/rules/engineering.md |
| Injected rule `block-dont-guess`: do the clear parts, then block with the question rather than guess | Rule 5, ask instead of picking the cheaper reading | examples/reader/rules/safety.md |
| Injected rule `test-before-done`, and a done note that says how it was checked (`skills/queue/SKILL.md`) | "saying what was checked", chosen because it states the reporting duty; rule 3 only covers how a test is proved | examples/reader/CLAUDE.md |

## 🟩 Keep: 5

| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| 1 | **Reread a stale brief before starting.** If it was written long ago, or items and files it names have changed, check what moved. If its premise moved, show the owner and wait; if it is already done, propose dropping it. Source: the "ready check" in `skills/queue/SKILL.md` | standing | 🟩 |
| 2 | **Branch from the task's stated base, not from whatever is checked out.** Name the base commit in the hand-in note. Source: "Work an item" in `skills/queue/SKILL.md` | standing | 🟩 |
| 3 | **A question the owner skipped is unread, not a yes.** Keep it open and ask again; carry on only with work that does not depend on it. Source: "Staying reasonable" in `skills/queue/SKILL.md` and `skills/herd/SKILL.md` | standing | ⭐ |
| 4 | **Ask once before starting another agent session (it costs money), and give each its own worktree or clone, never your directory.** Source: "Before starting a second agent" in `skills/herd/SKILL.md` | standing | 🟩 |
| 5 | **Post-compaction check** (my proposed name): after a compaction, restate your standing rules from memory, compare with the canonical rules text, report every difference, reread it. Source: "After an automatic compaction" in `skills/herd/SKILL.md` and the SessionStart notice in `lib/cat_herder/hooks.py` | on-demand | 🟩 |

## 🗑️ Dropped

`herder` skill (voice and cat names) · `capture` levels, size, rigor, topics and kind · `capture` riffing mode · `capture` rescue session · `capture` prompt me and ask blocks · `queue` field trip phone rules · `queue` swap, peer transfer, queue move and batch · `queue` dependencies and readiness · overheard block (`queue` and `herd` both carry it) · `herd` status card and Say line · `herd` pairs, associates, bond, roles and scale · `herd` hikes · `herd` handoff, join, retire and leave · `herd` release scope, integrate, cloud usage and supervisor · 12 slash commands in `commands/` · `rules/cat-herder.mdc` (a Cursor rule file, not loaded by Claude Code) · injected rule `say-how-long` · injected rule `push-early` · injected rule `review-pushed-commits`

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| `skills/capture`, `herd`, `herder`, `queue` (descriptions) | every session | no (likely) | about 1.8 KB |
| the same four skill bodies | when triggered | no (likely) | 17.9, 25.6, 7.6, 25.0 KB |
| SessionStart hook, `meow _hook sessionstart` | start, resume, compact; only in a repo with a queue | no | about 0.8 KB, plus about 0.5 KB after a compaction |
| PreCompact hook (auto) | before an automatic compaction; writes to the queue for roster sessions only | no | writes, no injection found |
| SessionEnd hook | session close | no | writes a local record |
| 12 commands in `commands/` | only when the owner types them | no | 8.7 KB in all |

## ✅ Do this
- ⬜ 1. Do not install the plugin.
- ⬜ 2. Review the patch below and apply the four rules by hand.
- ⬜ 3. Decide whether to write the post-compaction skill.

Carrying-cost case: it injects at session start and reaches no subagents, and more than one rule survives (four plus a skill), so the call rests on those rules; since they stand without `meow`, the rules are cheaper copied as text than carried as an injection.

## 📋 Proposed rules patch

Section: examples/reader/rules/engineering.md already holds how work gets done, with bold numbered rules. Add these as 8 to 11 there, matching its style. Provenance stays out of the file.

```diff
 7. **Commit messages:** imperative subject under 60 characters, then why.
+8. **Check a stale brief before starting.** If a task was written long ago, or
+   something it names has changed, find out what moved. If its premise moved,
+   show me and wait.
+9. **Branch from the task's stated base,** not the branch that happens to be
+   checked out, and name the base commit in your hand-in note.
+10. **A question I skip is unanswered, not a yes.** Keep it open and ask again.
+    Carry on only with work that does not depend on it.
+11. **Ask before starting another agent session,** since it costs money. Give
+    each its own worktree or clone, never the directory you are in.
```

On-demand skill, a proposal: `post-compaction-check`, with the one-line description "After a context compaction, restate your standing rules from memory, compare them with the rules files, and report every difference before going on." The dossier shows the reader keeps personal skills at examples/reader/skills/, so it could live at examples/reader/skills/post-compaction-check/SKILL.md; the choice is yours.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
