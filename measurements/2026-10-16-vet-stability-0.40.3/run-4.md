# 🔍 ch-v0403 0.40.3 · vetted against the sample reader

> ## 🟩 INSTALL · keep the three workflow skills and copy four rules into your engineering list
> It costs about 2.4 KB of skill and command descriptions each session, and one or two short lines after an automatic compaction in a session that sits on a queue roster. It fights none of your rules: where the queue sits on the code's branch, the queue skill now says to stop before any write, which agrees with your ban on pushing to `main`. Eleven of its rules you already run; four more are worth copying, and the queue, capture and herd skills are new on-demand capability if you want a git-backed work queue.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-15` · neckbeard 1.14.0 · ch-v0403 0.40.3

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟩 | **Cost** | no injection at session start; about 2.4 KB of descriptions (4 skills, 1 command) listed each session; after an automatic compaction, a line or two (my estimate, 100 to 300 bytes) and only in a session on a queue roster |
| 🟩 | **Reach** | main session only (likely): the hooks are PreCompact, SessionStart (matcher `compact`) and SessionEnd, and none is SubagentStart |
| 🟧 | **Leaves state** | a per-user state folder (`addresses` and `ended` records, written by `lib/cat_herder/ended.py` and `lib/cat_herder/addresses.py`), queue commits on the queue's git branch or remote, `queue.*` keys in the repo's git config, and session clones under the system temp folder |
| 🟧 | **Live surface** | its own `meow` command (Python); every queue write is a git push to the queue branch; the PreCompact hook does a git fetch and push, but only for a rostered session; `tools/herd-introspect` runs `claude -p --model sonnet`; launchers use ssh and tmux; no MCP servers |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 7: 4 standing rules and 3 skills |

The dossier could not trace the three hooks (all listed as unidentifiable), so I read `lib/cat_herder/hooks.py` and both hook files by hand. Only `sessionstart` writes to the model's context, and only after a compaction in a rostered session.

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **0** | none |
| 🔁 | **already covered** | **11** | ⬜ ×11 |
| 🆕 | **new, standing rule** | **4** | 🟩🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **3** | 🟩🟩🟩 |
| 🗑️ | **dropped** (persona, extras, no value) | **4** | ⬛⬛⬛⬛ |

## ⛔ Conflicts: 0

None found. Two near misses, checked and cleared: the queue skill stops before any queue write when the queue sits on the code's branch (it agrees with rule 2 in examples/reader/rules/safety.md), and the herd skill's default model for sessions it starts concerns launched sessions, not subagent dispatch, so rule 6 in examples/reader/rules/engineering.md does not apply.

## 🔁 Already covered: 11

| its rule | covered by | held in |
|---|---|---|
| Worker, rigor build: source priority, reuse what the repo has first | "Reuse before writing" (rule 1) | examples/reader/rules/engineering.md |
| Worker: a bug fix fixes the root cause, find every caller | "Fix the cause, not the symptom" (rule 2) | examples/reader/rules/engineering.md |
| Worker: a deliberate corner gets a debt comment, using the project's own marker when it names one | "Leave deliberate shortcuts marked" (rule 5); it states the rule in full, and the target defers to its `TODO(debt):` | examples/reader/rules/engineering.md |
| Reviewer: "Do the tests fail without the change?" | "seen to fail" (rule 3) | examples/reader/rules/engineering.md |
| Worker: blocked is a real answer, ask rather than guess on an ambiguous item | "If a request is ambiguous ... ask" (rule 5) | examples/reader/rules/safety.md |
| Worker: paste raw output, replace secrets with a redaction marker | "Secrets never appear in output" (rule 4) | examples/reader/rules/safety.md |
| Queue and herd: an owner's silence is not a yes, and a hike never takes it as a go-ahead | "explicit go-ahead in this conversation" (rule 1); chosen over rule 5 because it states the consent requirement directly | examples/reader/rules/safety.md |
| Queue: never use `--force` on your own; `meow herd clean` (removes folders outside the tree) only on the owner's go-ahead | "destructive without my explicit go-ahead" (rule 1) | examples/reader/rules/safety.md |
| Queue: if the queue sits on the code's branch, stop before any queue write | "Never push to `main`" (rule 2) | examples/reader/rules/safety.md |
| Capture: work found along the way is queued, not done inline | "The scope I asked for is the deliverable" (rule 4) | examples/reader/rules/engineering.md |
| Queue: when the ready check shows the premise moved, show the owner and wait; propose drop or merge, never do it | "say what you would change and let me decide" (rule 4) | examples/reader/rules/engineering.md |

## 🟩 Keep: 7

| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| 1 | No new dependency when a few lines do the job (herd, worker role, rigor build) | standing | 🆕 |
| 2 | Never simplify away validation at a trust boundary, error handling that prevents data loss, or a security measure (worker role) | standing | 🆕 |
| 3 | Attack your own work before handing it back, and say where you would attack it (worker role) | standing | 🆕 |
| 4 | Stop only the processes you started, by PID, never by port (worker role) | standing | 🆕 |
| 5 | `capture`: queue new work in one exchange and go back, at the detail the moment supports | skill | 🆕 |
| 6 | `queue`: set up, claim, finish, review and reorder items in a git-backed queue | skill | 🆕 |
| 7 | `herd`: pair a worker with a reviewer whose verdict binds, and take items in a row | skill | 🆕 |

## 🗑️ Dropped
`herder skill (voice and cat names)` · `/meow command (thin wrapper, ships with the skills)` · `Field Trip and dictation rules in the queue skill (phone use, not yours)` · `default model for sessions the herd starts (launcher setting; not ⛔, sessions are not subagents)`

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| skill descriptions (capture, herd, herder, queue) and the `/meow` command | listed every session | no | about 2.4 KB |
| skill bodies (capture, herd and its four role files, herder, queue) | when a skill loads | no | about 98 KB |
| PreCompact hook (`auto` only) | before an automatic compaction | no | silent; writes a roster record |
| SessionStart hook (`compact` only) | after a compaction | no | one or two lines, rostered sessions only |
| SessionEnd hook | when a session closes | no | silent; writes an `ended` record locally |

## ✅ Do this
- ⬜ 1. Add the four rules in the patch below to examples/reader/rules/engineering.md.
- ⬜ 2. Install the plugin only if you want a shared git queue. Without one, the skills sit unused at 2.4 KB of listing, and the four rules are the whole gain.
- ⬜ 3. Load it for one session first with `--plugin-dir`, and check that `meow list` in a repo with no queue ends at "no queue" and offers nothing unasked.

Carrying-cost case: the plugin has hooks but injects nothing at session start and does not reach subagents, so the cost is the description listing plus a short post-compaction line. Four rules you would write yourself survive, which clears the bar.

## 📋 Proposed rules patch

Where: the numbered list in examples/reader/rules/engineering.md, which already holds the how-to-build rules, so no new section. It is seven rules long, so no split is needed.

```diff
 7. **Commit messages:** imperative subject under 60 characters, then why.
+8. **No new dependency when a few lines do the job.**
+9. **Never simplify away** validation at a trust boundary, error handling that
+   prevents data loss, or a security measure.
+10. **Attack your own work before handing it back,** and say where you would
+    attack it.
+11. **Stop only the processes you started,** by PID, never by port.
```

On-demand skills: `capture`, `queue` and `herd` come with the plugin, so there is nothing to write. If you would rather copy than install, my proposed names are `capture-work`, `git-work-queue` and `paired-review`. The dossier does not say where you keep skills beyond examples/reader/skills/, so the location is yours to choose.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
