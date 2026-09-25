# 🔍 ponytail 4.10.0 · vetted against the sample reader

> ## 🟨 COPY RULES, SKIP PLUGIN · take the rule and three skills, skip the always-on injection
> Injects its main skill into every session and every subagent, about 1,300 tokens each time (its 6.6 KB skill file, frontmatter stripped), and writes mode state to files outside the project. Two of its instructions tell the model to proceed on its own where the sample reader's rules say ask first. One new safety rule and three on-demand skills are worth having, and both are cheaper to copy as text than to carry as a permanent injection.
>
> Verdict is relative to the [sample reader](reader/), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](README.md).

`2026-09-24` · neckbeard 1.12.0 · [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟧 | **Cost** | ~1,300 tokens (its 6.6 KB skill file, frontmatter stripped) at every session start, and again at every subagent start |
| 🟧 | **Reach** | main session + subagents (certain, a `SubagentStart` hook, documented) |
| 🟧 | **Leaves state** | flag/config files outside the project: home config dir and host-specific dirs |
| 🟩 | **Live surface** | no MCP servers, no network calls in its hooks; one nudge asks the model to offer editing settings.json |
| 🟩 | **Refused reads** | none |
| 🟨 | **Worth keeping** | 1 standing rule + 3 on-demand skills |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **2** | 🟥🟥 |
| 🔁 | **already covered** | **5** | ⬜⬜⬜⬜⬜ |
| 🆕 | **new, standing rule** | **1** | 🟩 |
| 🆕 | **new, on-demand skill** | **3** | 🟩🟩🟩 |
| 🗑️ | **dropped** (persona, extras, no value) | **5** | ⬛⬛⬛⬛⬛ |

## ⛔ Conflicts: 2

| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| 1 | "skip it, say so in one line" (speculative work) | "say what you would change and let me decide" | `examples/reader/rules/engineering.md` rule 4 | 🟥 |
| 2 | "Never stall on an answer you can default" | "Do not pick the cheaper reading and carry on" | `examples/reader/rules/safety.md` rule 5 | 🟥 |

## 🔁 Already covered: 5

| its rule | covered by | held in |
|---|---|---|
| reuse codebase → stdlib → native → dependency before writing | "Reuse before writing" | `examples/reader/rules/engineering.md` rule 1 |
| "grep every caller" before fixing a shared function | "find every caller" | `examples/reader/rules/engineering.md` rule 2 |
| mark shortcuts with a `ponytail:` comment "naming the ceiling and upgrade path" | `TODO(debt):` marker convention | `examples/reader/rules/engineering.md` rule 5 |
| "leaves ONE runnable check behind" for non-trivial logic | "seen to fail" test rule (stricter: must go red first) | `examples/reader/rules/engineering.md` rule 3 |
| "Code first" plus at most three short lines of explanation | "Short is good; complete is required" | `examples/reader/CLAUDE.md`, "How I like answers" |

## 🟩 Keep: 4

| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| 1 | Never simplify away input validation, error handling for data loss, security, or accessibility | standing rule | 🆕 |
| 2 | Review a diff for reinvented stdlib, needless deps, and speculative abstractions; one line per finding | on-demand skill | 🆕 |
| 3 | Same review, whole-repo, ranked by biggest cut | on-demand skill | 🆕 |
| 4 | Harvest a debt-marker comment convention into one ledger, flagging entries with no upgrade path | on-demand skill | 🆕 |

## 🗑️ Dropped

`ponytail-gain` (benchmark scoreboard, self-promotional, no portable rule) · `ponytail-help` (reference card and update instructions, self-referential) · intensity-level table and lite/full/ultra persona framing (config scaffolding, not a rule) · "Boundaries" meta text ("governs what you build, not how you talk") · statusline auto-nudge text bundled into the injected ruleset (unrelated to coding rules, adds injected bytes for a plugin feature)

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| `SessionStart` hook | every session start | no (parent thread only) | ~6.6 KB ruleset + first-run setup nudge |
| `SubagentStart` hook | every subagent spawn | yes | ~6.6 KB ruleset (same file) |
| `UserPromptSubmit` hook | every prompt | no | few bytes; full ruleset again on a mode switch |
| main skill | auto-injected (above) | yes | 6,637 bytes |
| 5 further skills | on demand / slash command only | no | 200–456 byte descriptions |
| 6 slash commands | user-typed trigger | no | thin wrapper prompts |
| state files | on activation / mode switch | n/a | small flag + JSON files, home config dirs |

## ✅ Do this

- ⬜ 1. Add the one new standing rule to `examples/reader/rules/engineering.md` (patch below).
- ⬜ 2. Write the three kept skills yourself, dropping the two conflicting instructions from their source text; do not install the plugin to get them.
- ⬜ 3. If reusing the debt-ledger idea, grep for the reader's own `TODO(debt):` marker, not `ponytail:`: the two conventions use different strings and won't find each other's comments.

Carrying-cost case: the always-on injection reaches subagents, so it needed at least one rule worth writing yourself to earn that cost. It produced exactly one, and one rule is cheaper to copy as text than to carry as a permanent injection. Skip the plugin, keep the rule and the three on-demand skills.

## 📋 Proposed rules patch

```diff
--- a/examples/reader/rules/engineering.md
+++ b/examples/reader/rules/engineering.md
@@
 7. **Commit messages:** imperative subject under 60 characters, then why.
+8. **Never simplify away safety-critical work.** Input validation at trust
+   boundaries, error handling that prevents data loss, security measures, and
+   accessibility basics stay in however small the change; simplicity never
+   overrides them or anything I explicitly asked to keep.
```

Proposed skills (name and location are this evaluation's suggestion, not the target's own; place them alongside the existing `examples/reader/skills/release-notes/SKILL.md`):

- **`over-engineering-review`**: review a diff for reinvented standard library, needless dependencies, and speculative abstractions; one line per finding: location, what to cut, what replaces it.
- **`over-engineering-audit`**: the same review run over a whole repository instead of a diff, ranked biggest cut first.
- **`debt-ledger`**: grep the repo for the reader's own `TODO(debt):` marker and collect the hits into one ledger, flagging any entry that names no upgrade trigger.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped ·
⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
