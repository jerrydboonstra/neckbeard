# 🔍 calm-trader/skills @ 5a15cd2 · vetted against the sample reader

> ## 🟩 INSTALL · four on-demand skills, no hooks, one small overlap
> No plugin manifest and no hooks: nothing loads automatically and nothing reaches a subagent unless the reader follows `supervision/SKILL.md`'s own step to copy its bundled agent files into `.claude/agents/` by hand. Two of the four skills each restate a rule the sample reader already runs, almost word for word. Everything else (the audit method, the verifier protocol, and two TradingView domain skills) is new.
>
> Verdict is relative to the [sample reader](reader/), not a judgment of the pack's quality. Reproduce: see [examples/README.md](README.md).

`2026-09-24` · neckbeard 1.12.2 · [calm-trader/skills](https://github.com/calm-trader/skills) @ `5a15cd2`

The author of neckbeard contributes to this repo, a skill pack maintained with a collaborator. It is here with the maintainers' agreement, and the verdict is still only about fit with the sample reader.

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟩 | **Cost** | none: no manifest, no hooks; each skill loads only when its own trigger phrase fires |
| ⬜ | **Reach** | main session only automatically; `supervision`'s 6 bundled agent files become dispatchable subagents only if the reader runs the `cp` step its own SKILL.md gives |
| 🟨 | **Leaves state** | `tv-tab-watchdog.sh` (shipped in both TradingView skills) writes `/tmp/tv-tab-watchdog.on` and `/tmp/tv-tab-watchdog.log`, outside the project, but only while a reader explicitly runs it |
| 🟨 | **Live surface** | no MCP servers, no network calls in any script; the watchdog script drives local Chrome tabs via `osascript`, closing and activating them, only when run |
| ⬜ | **Refused reads** | none |
| 🟩 | **Worth keeping** | 4 skills (0 standing rules) |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **0** | |
| 🔁 | **already covered** | **2** | ⬜⬜ |
| 🆕 | **new, standing rule** | **0** | |
| 🆕 | **new, on-demand skill** | **4** | 🟩×4 |
| 🗑️ | **dropped** (persona, extras, no value) | **10** | ⬛×10 |

## ⛔ Conflicts: 0

None found. Nothing here touches `main`, force-pushes, deploys, or asks to override a pinned subagent model. The five safety.md hard stops and engineering.md rule 6 all hold.

## 🔁 Already covered: 2

| its rule | covered by | held in |
|---|---|---|
| "a guardrail test must be seen to fail: break the thing it guards, watch it go red, restore it" (`supervision/SKILL.md`, "The rule underneath all of it") | "A test is not done until it has been seen to fail. Break the code it guards, watch it go red, restore it." | `examples/reader/rules/engineering.md` rule 3 |
| "a guard is not a guard until it has been seen to fail": invert the condition, run the test, and "if it still passes, the test is decorative," then restore (`falsify/SKILL.md` §4, Sabotage) | same rule: a guard isn't proven until watched failing and restored | `examples/reader/rules/engineering.md` rule 3 |

## 🟩 Keep: 4

| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| 1 | falsify | skill | 🆕 |
| 2 | supervision | skill | 🆕 |
| 3 | tradingview-backtesting | skill | 🆕 |
| 4 | tradingview-chart-reading | skill | 🆕 |

## 🗑️ Dropped

`README.md` (repo overview, restates the four skill descriptions) · `falsify/LICENSE`, `supervision/LICENSE` (MIT boilerplate) · `falsify/ATTRIBUTION.md` (provenance notes, not instructions to the reader) · `falsify/MEASUREMENTS.md` (its own measurement log) · `check-falsify.sh`, `check-verifier.sh` (read-only drift checkers against an *installed copy*, not rules themselves) · `falsify/fixtures/**`, `falsify/scripts/fixtures/**`, `tradingview-backtesting/scripts/fixtures/**` (synthetic self-test targets and answer keys)

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| 4 `SKILL.md` files (`falsify`, `supervision`, `tradingview-backtesting`, `tradingview-chart-reading`) | on invocation via the Skill tool, per each one's own trigger phrases | No | 73,224 bytes combined (falsify 13,440 · supervision 7,011 · tradingview-backtesting 43,252 · tradingview-chart-reading 9,521) |
| `tv-tab-watchdog.sh` (identical copy in both TradingView skill dirs) | only if a reader runs it, per the skill's own instructions | No | drives local Chrome via `osascript`; writes 2 files under `/tmp` |
| `supervision/agents/*.md` (`supervisor-architect`, `supervisor-design`, `supervisor-evals`, `supervisor-product`, `supervisor-quant`, `verifier`) | only if the reader manually copies them into their own `.claude/agents/`, per `supervision/SKILL.md`'s install step | Yes, once copied | not auto-installed; scored separately if a reader does this |

## ✅ Do this

- ⬜ 1. Install all four skills as-is. When `supervision/SKILL.md` or `falsify/SKILL.md` restate "watch it go red, restore it," that's already `examples/reader/rules/engineering.md` rule 3. No action needed; just don't mistake it for new.
- ⬜ 2. If installing `supervision`, decide separately whether to run its `cp .../agents/*.md .claude/agents/` step. It is the one action in this pack that reaches subagents, and it's opt-in, not automatic.

This is the third carrying-cost case: no manifest, no hooks, zero always-on cost, so the only question was whether the rules were good, and four on-demand skills' worth of cited, mostly non-overlapping material clears that bar for free.

## 📋 Proposed rules patch

Nothing to add. Nothing here rose to standing, always-on behavior. All four skills are on-demand by design, gated on their own trigger phrases, and the one place the content restates a standing rule, `examples/reader/rules/engineering.md` rule 3 already covers it.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped ·
⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
