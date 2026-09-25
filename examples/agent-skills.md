# 🔍 agent-skills 0.6.10 · vetted against the sample reader

> ## 🟩 INSTALL · install as published, nothing to strip first
> No hooks are wired in the manifest, so nothing runs until a skill, command, or agent is explicitly invoked; the only standing cost is the native skill router seeing each item's description every session. Nothing in the 39 bundled skills, commands, agents, and rule files collides with the sample reader's hard stops on destructive operations, pushing to `main`, deploys, or secrets. 37 of those 39 add coverage the sample reader has none of; only one repeats a rule it already runs, and one doesn't apply outside the target's own repo.
>
> Verdict is relative to the [sample reader](reader/), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](README.md).

`2026-09-24` · neckbeard 1.12.0 · [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟩 | **Cost** | 0 bytes injected by hooks (none wired in the manifest); ~9.1 KB of skill/agent descriptions surfaced to the native skill router every session, the same mechanism any skill pack uses |
| 🟩 | **Reach** | Main session only, plus 3 personas the `/ship` command explicitly dispatches as subagents. No hook reaches a subagent silently |
| 🟩 | **Leaves state** | None by default. Two opt-in hook pairs (unwired, and written assuming they're copied into the *user's own* project rather than run from the plugin's install path) would write to `.claude/sdd-cache/` inside the project if manually wired |
| 🟨 | **Live surface** | `WebFetch` to official documentation sites (`source-driven-development`, on invocation); an optional user-supplied `chrome-devtools` MCP server for two items, never bundled or auto-configured. No MCP servers declared by the plugin itself |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 37 of 39: 36 skills/commands/agents plus 1 standing rule |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **0** | 🟥 per item |
| 🔁 | **already covered** | **1** | ⬜ per item |
| 🆕 | **new, standing rule** | **1** | 🟩 per item |
| 🆕 | **new, on-demand skill** | **36** | 🟩 per item |
| 🗑️ | **dropped** (persona, extras, no value) | **1** | ⬛ per item |

## ⛔ Conflicts: 0
| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|

None found. Nothing in the target instructs autonomous pushes to `main`, unapproved deploys, unapproved destructive operations, or secret exposure. `security-and-hardening` and `constraint-driven-development`'s "Floor" both reinforce the sample reader's secrets rule rather than fight it.

## 🔁 Already covered: 1
| its rule | covered by | held in |
|---|---|---|
| `skills/using-agent-skills/SKILL.md`: "Manage Confusion Actively" ("STOP. Do not proceed with a guess.") and "Maintain Scope Discipline" ("Touch only what you're asked to touch.") | safety.md rule 5 ("If a request is ambiguous ... ask") and engineering.md rule 4 ("The scope I asked for is the deliverable") | `examples/reader/rules/safety.md`; `examples/reader/rules/engineering.md` |

## 🟩 Keep: 37

| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| 1 | `git-workflow-and-versioning` | standing rule | ⭐ |
| 2 | `api-and-interface-design` | skill | 🆕 |
| 3 | `browser-testing-with-devtools` | skill | 🆕 |
| 4 | `ci-cd-and-automation` | skill | 🆕 |
| 5 | `code-review-and-quality` | skill | 🆕 |
| 6 | `code-simplification` | skill | 🆕 |
| 7 | `constraint-driven-development` | skill | 🆕 |
| 8 | `context-engineering` | skill | 🆕 |
| 9 | `debugging-and-error-recovery` | skill | 🆕 |
| 10 | `deprecation-and-migration` | skill | 🆕 |
| 11 | `documentation-and-adrs` | skill | 🆕 |
| 12 | `doubt-driven-development` | skill | 🆕 |
| 13 | `frontend-ui-engineering` | skill | 🆕 |
| 14 | `idea-refine` | skill | 🆕 |
| 15 | `incremental-implementation` | skill | 🆕 |
| 16 | `interview-me` | skill | 🆕 |
| 17 | `observability-and-instrumentation` | skill | 🆕 |
| 18 | `performance-optimization` | skill | 🆕 |
| 19 | `planning-and-task-breakdown` | skill | 🆕 |
| 20 | `security-and-hardening` | skill | 🆕 |
| 21 | `shipping-and-launch` | skill | 🆕 |
| 22 | `source-driven-development` | skill | 🆕 |
| 23 | `spec-driven-development` | skill | 🆕 |
| 24 | `test-driven-development` | skill | 🆕 |
| 25 | `/build` | command | 🆕 |
| 26 | `/code-simplify` | command | 🆕 |
| 27 | `/constraints` | command | 🆕 |
| 28 | `/planning` | command | 🆕 |
| 29 | `/review` | command | 🆕 |
| 30 | `/ship` | command | 🆕 |
| 31 | `/spec` | command | 🆕 |
| 32 | `/test` | command | 🆕 |
| 33 | `/webperf` | command | 🆕 |
| 34 | `code-reviewer` | agent | 🆕 |
| 35 | `security-auditor` | agent | 🆕 |
| 36 | `test-engineer` | agent | 🆕 |
| 37 | `web-performance-auditor` | agent | 🆕 |

Notes on three of the above, since "new" doesn't mean "untouched by the sample reader's rules":

- `code-review-and-quality`'s "Dependency Discipline" section ("Prefer standard library and existing utilities over new dependencies") echoes engineering.md rule 1, inside a much larger five-axis review skill that is otherwise new.
- `debugging-and-error-recovery`'s "Fix the Root Cause" step echoes engineering.md rule 2, inside a larger reproduce/localize/reduce/guard triage process.
- `test-driven-development`'s Prove-It Pattern (write a failing reproduction test, watch it fail, then fix) echoes engineering.md rule 3, inside a much larger skill covering the full red-green-refactor cycle, the test pyramid, and mocking policy.

None of these three duplications are large enough to sink the whole item; each skill's new content dominates its file.

## 🗑️ Dropped
`CLAUDE.md`

The target's own root `CLAUDE.md` says outright: "This file configures agents working on the `addyosmani/agent-skills` repository itself, not other projects. Don't copy it into another project." It documents that repo's own directory layout, contribution process, and PR etiquette. Nothing in it is a portable rule, by its own declaration.

## 🧩 What it installs
| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| 25 skills | on demand, per each skill's own trigger description | no (loads into whichever session or subagent invokes it) | ~332 KB |
| 9 commands | on demand, via slash invocation (`/ship`, `/build`, ...) | no directly; `/ship` fans out to 3 agents | ~17 KB |
| 4 agents | on demand, dispatched as subagent tools (explicit, e.g. by `/ship`) | yes, by design | ~24 KB |
| 1 rule file (`CLAUDE.md`) | always visible to an agent working inside the target's own checkout | no | ~4 KB, self-scoped |
| 6 hook scripts (3 pairs) | never automatically: no `hooks` key in the manifest | no | small; opt-in only |

## ✅ Do this
- ⬜ 1. Install the plugin as published: zero wired hooks means zero always-on cost to weigh against the skills.
- ⬜ 2. Skip copying `using-agent-skills`'s "Manage Confusion Actively" and "Maintain Scope Discipline" text into a rules file. safety.md rule 5 and engineering.md rule 4 already say it; keeping both copies is redundant, not harmful.
- ⬜ 3. Leave the target's `CLAUDE.md` behind; it only applies inside the target's own repository.

Carrying-cost case: zero hooks, zero always-on cost, so the only question was whether the rules and skills are good, and 37 of 39 add something the sample reader didn't already have.

## 📋 Proposed rules patch

One "new, standing behavior" item surfaced: `git-workflow-and-versioning` declares itself in scope for "Always. Every code change flows through git," which puts its atomic-commit and branch-lifetime guidance in the same category as the sample reader's existing engineering rules, not a one-shot skill. The other 36 new items are already packaged as skills, commands, and agents in the plugin, and installing the plugin is the proposal for those; nothing further needs authoring.

```diff
--- a/rules/engineering.md
+++ b/rules/engineering.md
@@
 7. **Commit messages:** imperative subject under 60 characters, then why.
+8. **Keep commits atomic and small.** One logical change per commit, target
+   about 100 changed lines, split anything heading toward 1000. Prefer
+   short-lived branches that merge back within 1-3 days over long-lived
+   ones. (Source: agent-skills' `git-workflow-and-versioning` skill.)
```

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped ·
⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
