# 🔍 obra/superpowers 6.4.1 · vetted against the sample reader

> ## 🟧 INSTALL WITH CHANGES · install it, skip the two model overrides
> Fifteen skills and one hook, 3,192 bytes injected once at session start and never reaching a subagent. Two skills tell you to override a dispatched subagent's pinned model, which collides with a rule the sample reader already runs; two more just restate a rule it already has. The other ten, one of them condensed into a new rule, are worth keeping.
>
> Verdict is relative to the [sample reader](reader/), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](README.md).

`2026-09-24` · neckbeard 1.12.0 · obra/superpowers (https://github.com/obra/superpowers)

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟧 | **Cost** | 3,192 bytes injected at `SessionStart` (`startup\|clear\|compact`), once per session |
| ⬜ | **Reach** | main session only: the matcher excludes every subagent-firing event, and the injected skill itself carries a guard telling a dispatched subagent to ignore it |
| ⬜ | **Leaves state** | plans, specs and review ledgers under the consuming project's own `docs/superpowers/` and `.superpowers/`; nothing found outside the project |
| ⬜ | **Live surface** | no MCP servers, no network calls; skills shell out to `git`, test runners and `gh` |
| ⬜ | **Refused reads** | none |
| 🟩 | **Worth keeping** | 10 (1 rule, 9 skills) |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **2** | 🟥🟥 |
| 🔁 | **already covered** | **2** | ⬜⬜ |
| 🆕 | **new, standing rule** | **1** | 🟩 |
| 🆕 | **new, on-demand skill** | **9** | 🟩×9 |
| 🗑️ | **dropped** (persona, extras, no value) | **2** | ⬛⬛ |

## ⛔ Conflicts: 2

| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| 1 | "Always specify the model explicitly when dispatching a subagent" (`skills/subagent-driven-development/SKILL.md`) | "Subagents run on the model their definition pins. Do not override it on the dispatch call." | `examples/reader/rules/engineering.md` rule 6 | 🟥 |
| 2 | "an omitted model inherits the session's, which may not be the most capable" (`skills/executing-plans/SKILL.md`) | same rule: don't override a subagent's pinned model on dispatch | `examples/reader/rules/engineering.md` rule 6 | 🟥 |

## 🔁 Already covered: 2

| its rule | covered by | held in |
|---|---|---|
| "NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST" (`skills/systematic-debugging/SKILL.md`) | "Fix the cause, not the symptom. Before changing a function, find every caller." | `examples/reader/rules/engineering.md` rule 2 |
| "NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST" (`skills/test-driven-development/SKILL.md`) | "A test is not done until it has been seen to fail. Break the code it guards, watch it go red, restore it." | `examples/reader/rules/engineering.md` rule 3 |

## 🟩 Keep: 10

| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| 1 | verification-before-completion, condensed | rule | ⭐ |
| 2 | brainstorming | skill | 🆕 |
| 3 | diagnosing-superpowers | skill | 🆕 |
| 4 | dispatching-parallel-agents | skill | 🆕 |
| 5 | finishing-a-development-branch | skill | 🆕 |
| 6 | receiving-code-review | skill | 🆕 |
| 7 | requesting-code-review | skill | 🆕 |
| 8 | using-git-worktrees | skill | 🆕 |
| 9 | writing-plans | skill | 🆕 |
| 10 | writing-skills | skill | 🆕 |

## 🗑️ Dropped

`skills/using-superpowers/SKILL.md` (the `SessionStart` payload; "you ABSOLUTELY MUST invoke the skill" is a bootstrap mandate, not an engineering rule, and its own text already tells a subagent to ignore it) · `CLAUDE.md` (target root; points contributors at `AGENTS.md`, but a plugin install never loads a target's own root `CLAUDE.md` into the installing session, so it carries no weight here)

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| `hooks/session-start` (`SessionStart` hook) | every session start matching `startup\|clear\|compact` | No | 3,192 bytes |
| 15 skills under `skills/` | on invocation via the Skill tool | No | 168,882 bytes |
| `CLAUDE.md` (target root) | only inside a checkout of this repo itself | No | 123 bytes |

## ✅ Do this

- ⬜ 1. Install the plugin as-is; when `skills/subagent-driven-development/SKILL.md` or `skills/executing-plans/SKILL.md` says to specify a model on dispatch, follow `examples/reader/rules/engineering.md` rule 6 instead and leave the model alone.
- ⬜ 2. Add the proposed rule below to `examples/reader/rules/engineering.md`.

This is the first carrying-cost case: the hook injects at every session, and what survives (one new rule plus nine skills) is well above the one-rule bar that would make copying the text cheaper than installing the plugin.

## 📋 Proposed rules patch

```diff
--- a/examples/reader/rules/engineering.md
+++ b/examples/reader/rules/engineering.md
@@
 7. **Commit messages:** imperative subject under 60 characters, then why.
+8. **No completion claims without fresh evidence.** Before saying a fix, a
+   build, or a test run passed, run the command in this message and read
+   its output. "Should pass" is not evidence.
```

Condensed from `skills/verification-before-completion/SKILL.md`.

The other nine keeps (brainstorming, diagnosing-superpowers, dispatching-parallel-agents, finishing-a-development-branch, receiving-code-review, requesting-code-review, using-git-worktrees, writing-plans, writing-skills) already ship as named, on-demand skills inside the plugin. Installing it is how the sample reader gets them, so none need a new name or a separate file.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped ·
⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
