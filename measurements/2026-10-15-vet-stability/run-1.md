# 🔍 ch-v0532 0.53.2 · vetted against the sample reader

> ## 🟨 COPY RULES, SKIP PLUGIN · take 8 items as text
> The plugin is a git-backed work queue driven by its own `meow` command, and the reader has no queue, so nearly all of its 170 KB of skill and role text is machinery the reader would never run. It carries 3 conflicts with the reader's subagent-model rule, and its hooks add about 860 bytes at session start in any repo that has a queue. Eight things are worth keeping, and all of them copy as plain text.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-15` · neckbeard 1.14.0 · ch-v0532 0.53.2

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟧 | **Cost** | About 1.8 KB of skill descriptions in every session. About 860 bytes from the SessionStart hook on each start, resume or compaction in a repo that has a queue copy, plus a few role lines when the session is on a roster. Skill bodies (76 KB) load only when a skill triggers |
| 🟩 | **Reach** | Main session only (likely). The dossier finds no hook event that fires in a subagent |
| 🟧 | **Leaves state** | A `cat-herder` folder under the XDG state directory (`ended` and `addresses` files), written at session end. A session on a roster also commits and pushes to its repo's queue branch |
| 🟧 | **Live surface** | Skills and hooks run the bundled `bin/meow` (Python), which runs `git fetch` and `git push`, `ssh` and `tmux`. No MCP servers |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 8 (7 rules, 1 skill) |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **3** | 🟥🟥🟥 |
| 🔁 | **already covered** | **9** | ⬜⬜⬜⬜⬜⬜⬜⬜⬜ |
| 🆕 | **new, standing rule** | **7** | 🟩🟩🟩🟩🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **1** | 🟩 |
| 🗑️ | **dropped** (persona, extras, no value) | **12** | ⬛ ×12 |

## ⛔ Conflicts: 3

| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| 1 | Kitten swarms: send "3 or 4 subagents on `claude-haiku-5-5`" (the worker and reviewer roles, and the orchestrator's `rigor: run` judging) | "Do not override it on the dispatch call" (rule 6) | examples/reader/rules/engineering.md | 🟥 |
| 2 | Escalated item: start an advisor thread "passing the model `claude-fable-5-1`" (orchestrator role) | The same rule 6: the model comes from the definition, not the dispatch call | examples/reader/rules/engineering.md | 🟥 |
| 3 | Grooming: hand items to agents "on the cheapest capable model your host offers" (queue skill) | The same rule 6 | examples/reader/rules/engineering.md | 🟥 |

## 🔁 Already covered: 9

| its rule | covered by | held in |
|---|---|---|
| Source priority: reuse the repo, then the standard library, the platform, an installed dependency (worker role, `rigor: build`) | "Reuse before writing" (rule 1). It states the order as a rule of its own | examples/reader/rules/engineering.md |
| A bug fix fixes the root cause: "find every caller" | "Fix the cause, not the symptom" (rule 2) | examples/reader/rules/engineering.md |
| A deliberate corner gets a debt comment with ceiling and upgrade path; it defers to a project marker such as `TODO(debt):` | "Leave deliberate shortcuts marked" (rule 5), which names that very marker | examples/reader/rules/engineering.md |
| New tests must fail without the fix; a reviewer reverts the fix and watches them go red | "A test is not done until it has been seen to fail" (rule 3) | examples/reader/rules/engineering.md |
| Ambiguous item: do the parts that are clear, then block with the question "rather than guess" | "If a request is ambiguous and the wrong reading is costly, ask" (rule 5). I chose it over the capture skill's "ask only what's missing", which is about interview length | examples/reader/rules/safety.md |
| Deleting remote branches or worktree folders (`integrate cleanup`, `herd clean`) only on the owner's go-ahead | "Never run anything destructive without my explicit go-ahead" (rule 1) | examples/reader/rules/safety.md |
| Done notes redact secrets; "never paste credentials, tokens or personal data" | "Secrets never appear in output, logs, commits or test fixtures" (rule 4) | examples/reader/rules/safety.md |
| A reviewer cites each accepted claim with a file and line, and lists what it did not check | "A review that says 'looks fine' without saying what was checked is not a review" | examples/reader/CLAUDE.md |
| Work found along the way is queued, not done inline; a split adds no scope; a finding outside scope is a suggestion | "The scope I asked for is the deliverable" (rule 4) | examples/reader/rules/engineering.md |

## 🟩 Keep: 8

| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| 1 | On a failed git fetch or push for auth, stop and report the remote and the error. Never add a key, token, https remote or forwarded agent to get past it (worker and reviewer roles) | standing | ⭐ |
| 2 | A question the owner skipped is unread, not a yes or a no. Do not act on it; carry on only with what does not depend on the answer (queue and herd skills) | standing | 🟩 |
| 3 | Stop only the processes you started, by PID, never by port or name pattern (worker and auditor roles) | standing | 🟩 |
| 4 | Add no dependency when a few lines do the job (worker role) | standing | 🟩 |
| 5 | Never simplify away validation at a trust boundary, error handling that prevents data loss, or a security measure (worker role) | standing | 🟩 |
| 6 | Commit subjects say what changed and name no agent, session or roster id (worker and reviewer roles) | standing | 🟩 |
| 7 | Before starting a task written earlier, check what changed since; if its premise moved, show the owner and wait rather than build the old version (the queue skill's ready check) | standing | 🟩 |
| 8 | Falsify a document: list its checkable claims, run each example in a scratch repo, find the test that covers it, break the code, and give each claim BACKED, UNTESTED, CONTRADICTED or UNTESTABLE (`skills/herd/roles/auditor.md`) | on-demand skill | 🟩 |

## 🗑️ Dropped

`herder skill: cat names and "Mrrp" openers` · `capture: mid-task queueing, riffing mode, rescue session` · `queue: claim, reorder, merge, swap, peer transfer, queue move` · `herd: pairs, hikes, launchers, roster, retire, join` · `worker and reviewer mechanics: --expect, pair wait, test run, done-note format` · `orchestrator, handoff, associate, bond, readonly roles and the supervisor sections` · `Overheard block, status footer and the ledger on every reply` · `Field Trip phone rules` · `12 slash commands (thin wrappers over meow)` · `rules/cat-herder.mdc (a Cursor rule)` · `compaction counting and the house-rules recital hook` · `--force only on the owner's word (meow-specific)`

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| 4 skill descriptions (capture, herd, herder, queue) | every session | no (likely) | 1.8 KB |
| 4 skill bodies | when a skill triggers | no (likely) | 76 KB |
| Role and section files (worker, reviewer, orchestrator, and others) | read on request through `meow herd role` and `meow section` | no (likely) | 94 KB |
| SessionStart hook (startup, resume, compact) | each start in a repo with a queue copy | no | about 860 B injected, more for a rostered session |
| PreCompact hook (auto) | each automatic compaction | no | injects nothing; for a rostered session it runs `git fetch` and `git push` (20 s limit) |
| SessionEnd hook | each session close | no | injects nothing; appends one line to a state file |
| 12 slash commands | only when typed (model invocation is off) | no | 5 KB |
| `bin/meow` and `lib/` | run by skills and hooks | no | Python CLI that uses git, ssh and tmux |

The dossier lists all three Claude Code hooks as unidentifiable, so I read what they run in `lib/cat_herder/hooks.py`. The Antigravity and Cursor hook files do not apply to Claude Code.

## ✅ Do this

- ⬜ 1. Do not install the plugin. Nothing it does well works without the `meow` queue, and the reader has none.
- ⬜ 2. Copy the 7 standing rules into the reader's files as proposed below.
- ⬜ 3. If you want the audit method, write the `falsify-docs` skill below.

Carrying-cost case: hooks and always-on text are present, and the rules worth keeping are short enough to copy as text, so the cost buys nothing.

## 📋 Proposed rules patch

Where they go: `examples/reader/rules/safety.md` holds the stop-and-ask rules, so items 1 to 3 belong there. `examples/reader/rules/engineering.md` already covers how code gets written, so items 4 to 7 go there. Both files are short, so no split is needed.

```diff
--- examples/reader/rules/safety.md
+++ examples/reader/rules/safety.md
@@
 5. **If a request is ambiguous and the wrong reading is costly, ask.** Do not
    pick the cheaper reading and carry on.
+6. **If a git fetch or push fails on authentication, stop and report the
+   remote and the error.** Never add a key, a token, an https remote or a
+   forwarded agent to get past it.
+7. **A question I did not answer is unanswered, not a yes.** Carry on only with
+   work that does not depend on it, and ask again.
+8. **Stop only the processes you started,** by PID, never by port or name
+   pattern.
```

```diff
--- examples/reader/rules/engineering.md
+++ examples/reader/rules/engineering.md
@@
-7. **Commit messages:** imperative subject under 60 characters, then why.
+7. **Commit messages:** imperative subject under 60 characters, then why. Say
+   what changed; never name an agent or a session.
+8. **No new dependency when a few lines do the job.**
+9. **Never simplify away validation at a trust boundary, error handling that
+   prevents data loss, or a security measure.**
+10. **A task written earlier gets rechecked before you start it.** Look at what
+    changed since; if its premise moved, show me and wait. Do not build the old
+    version.
```

On-demand skill (the name is my proposal; the target does not name it as a skill). The reader keeps personal skills under `examples/reader/skills/<name>/SKILL.md`, so that is the place:

- `falsify-docs`: Audit a doc, skill or command help by running each checkable claim in a scratch repo and breaking the code behind it. Gives BACKED, UNTESTED, CONTRADICTED or UNTESTABLE per claim, then reports findings. Edits nothing.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
