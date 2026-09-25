# 🔍 github/spec-kit 1.0.12.dev0 · vetted against the sample reader

> ## 🟨 COPY RULES, SKIP PLUGIN · take two review lines, leave the rest
> Nothing about this target costs anything to carry: no hooks, no subagents, two skills that only load inside a checkout of the repo itself. One line inside them conflicts with a hard engineering rule, one duplicates a safety rule already in force, and two are worth copying as text. The templates this project hands to a user's own project at install time sit outside what this scan inventories, so this verdict covers only what ships in the repo.
>
> Verdict is relative to the [sample reader](reader/), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](README.md).

`2026-09-24` · neckbeard 1.12.0 · [github/spec-kit](https://github.com/github/spec-kit)

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟩 | **Cost** | 0 bytes on session start; ~7,532 bytes across 2 skills, loaded only on demand |
| 🟩 | **Reach** | main session only, and only inside a checkout of this repo (no hooks declared) |
| 🟩 | **Leaves state** | none in the skills themselves; the CLI's own job is scaffolding whatever project you point it at |
| 🟨 | **Live surface** | no MCP servers; one skill directs a `git push` and a pull-request open via the assistant itself |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | ▰▰ 2 rules |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **1** | 🟥 per item |
| 🔁 | **already covered** | **1** | ⬜ per item |
| 🆕 | **new, standing rule** | **2** | 🟩 per item |
| 🆕 | **new, on-demand skill** | **0** | n/a |
| 🗑️ | **dropped** (persona, extras, no value) | **0** | n/a |

## ⛔ Conflicts: 1

| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| 1 | a bug-fix regression test may be skipped for "available evidence" when the reviewer "cannot run the comparison" (`.github/skills/code-review/SKILL.md`) | "A test is not done until it has been seen to fail. Break the code it guards, watch it go red, restore it." | `examples/reader/rules/engineering.md` rule 3 | 🟥 |

## 🔁 Already covered: 1

| its rule | covered by | held in |
|---|---|---|
| `.github/skills/add-community-extension/SKILL.md`'s closing step: push a feature branch and open a pull request against `upstream`'s `main`, never push `main` or merge it | "Never push to `main` or merge a pull request. Open the PR and stop." | `examples/reader/rules/safety.md` rule 2 |

## 🟩 Keep: 2

| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| 1 | Reviews must check for both positive and negative test coverage on every code change (`.github/skills/code-review/SKILL.md`) | new, standing rule | 🟩 |
| 2 | Reviews must flag wording changes that drift from terms already used elsewhere in the codebase (`.github/skills/code-review/SKILL.md`) | new, standing rule | 🟩 |

## 🗑️ Dropped

None. Every item this scan found sorted into one of the grids above.

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| `.github/skills/code-review/SKILL.md` | on demand, reviewing a diff or PR, only inside a checkout of this repo | no (no hooks declared) | 854 bytes |
| `.github/skills/add-community-extension/SKILL.md` | on demand, processing a catalog-submission issue, only inside a checkout of this repo | no (no hooks declared) | 6,678 bytes |

No `rule_files`, `commands`, `agents`, hooks, or MCP servers were found at the repo root. The repo's actual end-user surface, the set of slash-style skills its own CLI writes into whatever project runs its installer, is generated from template files at install time and does not exist in this shape in the source tree, so it is not part of this comparison.

## ✅ Do this

- ⬜ 1. Copy the two kept lines above into `examples/reader/rules/engineering.md` (or its equivalent) as new numbered rules.
- ⬜ 2. Do not adopt the regression-evidence exception; it weakens `engineering.md` rule 3.
- ⬜ 3. Do not add the repo itself as an ongoing rules source: its only claude-facing content is two contributor skills scoped to its own repo.

Zero hooks, zero always-on cost: nothing to weigh, so the only question was whether the two surviving rules were worth copying. They were.

## 📋 Proposed rules patch

```diff
--- a/examples/reader/rules/engineering.md
+++ b/examples/reader/rules/engineering.md
@@
 7. **Commit messages:** imperative subject under 60 characters, then why.
+8. **Reviews check both directions.** Before approving a change, confirm it
+   has test cases for what it should do and test cases for what it should
+   prevent.
+9. **Wording changes match the codebase's own terms.** Flag a rename or a
+   rewritten comment that drifts from terminology already used elsewhere in
+   the repo.
```

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped ·
⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
