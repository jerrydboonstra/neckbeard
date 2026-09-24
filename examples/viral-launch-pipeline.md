# 🔍 viral-launch-pipeline 1.0.0 · vetted against the sample reader

> ## 🟩 INSTALL · adopt as-is, then copy four of its rules into your own
> No hooks, no declared agents, no MCP servers: the only always-on cost is one skill description in the session listing. Its 21 subagents are real, they just live in prose rather than agent files, and the loop dispatches them straight into your `Agent` tool. Four of its internal rules are worth keeping on their own; two duplicate a rule you already run, and none of them conflict with it.
>
> Verdict is relative to the [sample reader](reader/), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](README.md).

`2026-09-24` · neckbeard 1.12.0 · Koz-TV/viral-launch-pipeline (https://github.com/Koz-TV/viral-launch-pipeline)

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟩 | **Cost** | 571 B skill description, every session; the 15,919 B `SKILL.md` and ~92 KB of prompt/reference files load only when the skill fires |
| 🟩 | **Reach** | main session + subagents (certain): dispatches roughly 21 `Agent` calls per launch, one per pipeline stage |
| 🟩 | **Leaves state** | none outside the project; writes a full paper trail under `./launches/<slug>/` inside the working directory |
| 🟨 | **Live surface** | `WebSearch` / `WebFetch` in its research and technical-review stages; no MCP servers, no external API keys |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 4 rules |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **0** | none found |
| 🔁 | **already covered** | **2** | ⬜ per item |
| 🆕 | **new, standing rule** | **4** | 🟩 per item |
| 🆕 | **new, on-demand skill** | **0** | none found |
| 🗑️ | **dropped** (persona, extras, no value) | **4** | ⬛ per item |

## ⛔ Conflicts: 0
None found. Nothing in `skills/viral-launch/SKILL.md` touches a hard stop, an approval gate, or a deploy/push/secrets rule the sample reader runs.

## 🔁 Already covered: 2
| its rule | covered by | held in |
|---|---|---|
| Hard rule 7: a failed Call Supervisor check "always" surfaces to the user, never auto-resolved | "If a request is ambiguous and the wrong reading is costly, ask. Do not pick the cheaper reading and carry on." (rule 5) | `examples/reader/rules/safety.md` |
| Hard rule 9: an ambiguous subagent return gets re-dispatched or surfaced, never advanced on | same rule, same file | `examples/reader/rules/safety.md` |

## 🟩 Keep: 4
| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| 1 | Bound every critique loop with a hard cap; on exhausting it, surface the best attempts instead of looping forever or picking one silently (target's Hard rule 2) | standing | 🆕 |
| 2 | Batch independent subagent dispatches into one message so they run in parallel, not sequentially (target's Hard rule 5) | standing | 🆕 |
| 3 | Verify a delegated stage actually wrote its expected file before marking it done; a summary is not proof (target's Hard rule 8) | standing | 🆕 |
| 4 | Never soften a grading or critique result to force a pass, even against an iteration budget (target's Hard rule 10) | standing | 🆕 |

## 🗑️ Dropped
`Hard rule 1 (write nothing yourself, delegate everything)` · `Hard rule 3 (Mom Test budget, restates rule 2)` · `Hard rule 4 (meta.json bookkeeping)` · `Hard rule 6 (specialist chain re-run)`

Each is specific to running this one pipeline rather than a portable working principle, or restates a rule already counted above.

## 🧩 What it installs
| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| skill: `viral-launch` | trigger phrases like "viral launch for X" or "resume the launch for X" | yes, certain | `SKILL.md` 15,919 B; 21 stage prompts + 6 reference docs, ~92,456 B, read one at a time as stages run |
| hooks | never registers | no | none declared |
| commands | none shipped | n/a | none |
| agents (as files) | none declared | n/a | none, the pipeline's ~21 subagents are dispatched from prose via `Agent(subagent_type="general-purpose", ...)` calls, not declared as agent files |
| MCP servers | none declared | n/a | none |

## ✅ Do this
- ⬜ 1. Install it. Nothing in it conflicts with your rules, and the pipeline itself is a real capability, not just rules worth copying.
- ⬜ 2. Fold the four kept rules into `examples/reader/rules/engineering.md`, near its existing subagent rule (rule 6).
- ⬜ 3. Before your first run, confirm the channel scope it defaults to (X-thread + LinkedIn + ProductHunt) and budget for the roughly 30-60 minute, 21-dispatch run its own docs describe.

The pipeline reaches subagents on every run, so per the carrying-cost test it needed at least one rule you'd have written yourself to be worth installing rather than just copying: it cleared that bar with four.

## 📋 Proposed rules patch

```diff
--- a/examples/reader/rules/engineering.md
+++ b/examples/reader/rules/engineering.md
@@
 7. **Commit messages:** imperative subject under 60 characters, then why.
+8. **Bound every critique or refinement loop.** Cap the iterations, and on
+   exhausting the cap, surface the best attempts to me instead of looping
+   forever or picking one silently.
+9. **Batch independent subagent dispatches into one message.** Sequential
+   dispatch of work that could run in parallel wastes wall time.
+10. **Verify a delegated stage's artifact exists before marking it done.**
+    A subagent's summary is not proof; check the file it was supposed to
+    write.
+11. **Never soften a grading or critique result to force a pass.** Report
+    the honest score even against an iteration budget.
```

## Key
🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
