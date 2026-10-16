# 🔍 ch-v0532 0.53.2 · vetted against the sample reader

> ## 🟨 COPY RULES, SKIP PLUGIN · take five rules and one skill as text
> The plugin is a large queue-and-review system (about 175 KB of skills, roles and sections) that the sample reader has no use for, and its role text tells sessions to dispatch subagents on a named model, which breaks one of the reader's rules four times. The hooks cost nothing in a repo with no queue, and about 860 bytes per session start in one that has a queue, so the cost is small; the trouble is what the skills ask for. What is worth keeping is a handful of coding and review habits and a claim-auditing method, all cheaper to copy than to carry.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-15` · neckbeard 1.14.0 · ch-v0532 0.53.2

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟩 | **Cost** | About 860 bytes at session start, resume and compaction, only in a repo that has a queue; a few hundred bytes more after a compaction for a session on the roster; nothing in a repo with no queue |
| 🟩 | **Reach** | Main session only for hooks (certain: no subagent event is hooked); skill text arrives only when a skill triggers |
| 🟨 | **Leaves state** | A small per-user state folder (`lib/cat_herder/ended.py`, `addresses.py`), `.git/config` rule answers, and, for a rostered session at compaction, a commit pushed to the queue remote (`lib/cat_herder/hooks.py`) |
| 🟧 | **Live surface** | No MCP server. `meow` fetches and pushes git remotes over ssh or http, and launches and stops other sessions; `/meow` runs `Bash(meow:*)` |
| 🟩 | **Refused reads** | none |
| 🟨 | **Worth keeping** | 6 (5 rules, 1 skill) |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **4** | 🟥🟥🟥🟥 |
| 🔁 | **already covered** | **11** | ▰ ×11 |
| 🆕 | **new, standing rule** | **5** | 🟩🟩🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **1** | 🟩 |
| 🗑️ | **dropped** (persona, extras, no value) | **30** | ▰ ×30 |

## ⛔ Conflicts: 4

| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| 1 | Worker sends 3 or 4 subagents "on `claude-haiku-5-5`" at its own diff before `done`, plus a docs pre-check on Haiku (`skills/herd/roles/worker.md`) | "Do not override it on the dispatch call" (rule 6) | `examples/reader/rules/engineering.md` | 🟥 |
| 2 | Worker sends three wording subagents on `claude-haiku-5-5` (`skills/herd/roles/worker.md`) | Same rule 6: the dispatch names a model | `examples/reader/rules/engineering.md` | 🟥 |
| 3 | Orchestrator judges a `rigor: run` item with 3 or 4 subagents on `claude-haiku-5-5` (`skills/herd/roles/orchestrator.md`) | Same rule 6 | `examples/reader/rules/engineering.md` | 🟥 |
| 4 | Groom hands items to agents "on the cheapest capable model your host offers" (`skills/queue/SKILL.md`) | Same rule 6: the model is chosen at dispatch, not by the agent's definition | `examples/reader/rules/engineering.md` | 🟥 |

## 🔁 Already covered: 11

| its rule | covered by | held in |
|---|---|---|
| Source priority: reuse, standard library, platform, installed dependency, then new code (`worker.md`, five coding rules) | Rule 1, "Reuse before writing" | `examples/reader/rules/engineering.md` |
| No new dependency when a few lines do the job (`worker.md`) | Same rule 1 ("an existing dependency, before adding code") | `examples/reader/rules/engineering.md` |
| A bug fix fixes the root cause: find every caller (`worker.md`) | Rule 2, "Fix the cause, not the symptom" | `examples/reader/rules/engineering.md` |
| A deliberate corner gets a debt comment, using the project's own marker such as `TODO(debt):` (`worker.md`) | Rule 5, which names that exact marker | `examples/reader/rules/engineering.md` |
| Prove each new test fails without its fix: break the fix, see red, restore (`worker.md`, "Prove a batch's tests") | Rule 3, "seen to fail" | `examples/reader/rules/engineering.md` |
| Work found along the way is captured, not done inline; a refactor is added only after asking the owner (`capture/SKILL.md`) | Rule 4, "do not narrow it quietly or widen it unasked" | `examples/reader/rules/engineering.md` |
| Never use `--force` on your own; read an unsure irreversible command back and wait for a yes (`queue/SKILL.md`) | Hard stop 1, destructive actions need an explicit go-ahead | `examples/reader/rules/safety.md` |
| Put go-aheads for publishing, spending or a deploy in the item; stop and ask before doing them (`queue/SKILL.md`, `worker.md`) | Hard stop 3 ("Preparing one is fine") | `examples/reader/rules/safety.md` |
| Refuse every queue write on the branch the code is on, since each would push to main (`queue/SKILL.md`) | Hard stop 2, never push to `main` | `examples/reader/rules/safety.md` |
| Replace a secret in pasted output with `<redacted>`; never paste credentials (`worker.md`) | Hard stop 4, secrets never appear in output | `examples/reader/rules/safety.md` |
| A skipped question is unread, not a yes or no; ask on the ledger and do not act (`queue/SKILL.md`) | Hard stop 5, ask when the wrong reading is costly. I chose it over the "Plain language" lines of `CLAUDE.md` because it states the same gate as a rule in its own right | `examples/reader/rules/safety.md` |

## 🟩 Keep: 6

| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| 1 | Never simplify away validation at a trust boundary, error handling that prevents data loss, or a security measure (`worker.md`) | standing | ⭐ |
| 2 | Evidence is raw output: the command, its exit code and bounded output, never a paraphrase (`worker.md`) | standing | 🆕 |
| 3 | When reviewing, write "I claim X; the failure I fear is Y", then try to produce Y; one real gap is a reopen (`reviewer.md`) | standing | 🆕 |
| 4 | Stop only the processes you started, by PID, never by port or `pkill` pattern (`worker.md`, `reviewer.md`, `auditor.md`) | standing | 🆕 |
| 5 | Start new work from a freshly fetched base, never from whatever is checked out; leave a dirty checkout alone (`worker.md`) | standing | 🆕 |
| 6 | Claim audit: list every checkable claim in a doc, run each example, break the code it depends on, label it BACKED, UNTESTED, CONTRADICTED or UNTESTABLE (`auditor.md`, Method) | skill | 🆕 |

## 🗑️ Dropped

`capture` skill, remainder · `herder` skill · `herd` skill, remainder · `queue` skill, remainder (⛔1) · `worker` role, remainder (⛔2) · `reviewer` role, remainder · `orchestrator` role, remainder (⛔1) · `associate` role · `handoff` role · `readonly` role · `bond` role · `rules/cat-herder.mdc` · section `asks` · section `field-trip` · section `prompt-me` · section `setup` · section `launch-refused` · section `orchestrator` · command `asks` · command `board` · command `groom` · command `hike` · command `meow` · command `next` · command `park` · command `prompt-me` · command `rescue` · command `show` · command `status` · command `timeline`

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| SessionStart hook (`meow _hook sessionstart`) | start, resume, compact | no | about 860 B in a repo with a queue, 0 B otherwise |
| PreCompact hook, auto only | automatic compaction | no | injects nothing; writes a queue commit for a rostered session |
| SessionEnd hook | session close | no | injects nothing; writes a small local state file |
| 4 skills: `capture` (not user-invocable), `herd`, `herder`, `queue` | when triggered | ❓ | 17,879 + 25,636 + 7,552 + 25,005 B |
| 8 role files and 3 sections, read through `meow` | when a session is started in a role | ❓ | about 75 KB of roles |
| 12 slash commands | when typed | no | 5,051 B |
| `rules/cat-herder.mdc`, `hooks/cursor.py`, `hooks/antigravity.py` | other hosts only | no | 932 B for the rule |

## ✅ Do this

- ⬜ 1. Do not install the plugin. Copy the five rules in the patch below into `examples/reader/rules/engineering.md`.
- ⬜ 2. Decide whether you want the claim-audit skill, and if so create it from the sketch below.
- ⬜ 3. If you ever adopt the plugin anyway, remove or edit the four model-naming dispatches first, since they cannot coexist with rule 6.

Carrying-cost case: the hooks inject on every session start in a queue repo, so the plugin would need at least one rule you would not write yourself; five survive, and each is a sentence, so copying beats carrying.

## 📋 Proposed rules patch

Proposed section: the existing numbered list in `examples/reader/rules/engineering.md`, which is where the reader keeps how code gets written. The numbering and bold lead-ins match it.

```diff
 7. **Commit messages:** imperative subject under 60 characters, then why.
+8. **Never simplify away safety.** Keep validation at trust boundaries, error
+   handling that prevents data loss, and security measures, even when removing
+   them would shorten the code.
+9. **Evidence is raw output.** Report the command, its exit code and bounded
+   output, never a paraphrase of it.
+10. **Review by trying to break the claim.** Write "I claim X; the failure I
+    fear is Y", then try to produce Y. One real gap is a reopen.
+11. **Stop only processes you started,** by PID, never by port or name pattern.
+12. **Start from a fresh base.** Branch from a freshly fetched base, not from
+    whatever is checked out, and leave a dirty checkout alone.
```

Proposed skill (the name is my proposal; the plugin does not name this capability). The reader keeps personal skills beside `examples/reader/skills/release-notes`, so that is the natural place, but the choice is yours.

```
name: claim-audit
description: Audit a doc, skill or command help by checking every claim against the code: run each example, break the code it depends on, and label the claim BACKED, UNTESTED, CONTRADICTED or UNTESTABLE. Reports findings and edits nothing.
```

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
