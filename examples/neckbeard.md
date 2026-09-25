# 🔍 neckbeard 1.12.0 · vetted against the sample reader

> ## 🟧 INSTALL WITH CHANGES · keep the skill, fix the report's own jargon
> Costs about 270 tokens a session and nothing more: no hooks, no agents, so it never runs uninvited. Two of its habits already match the sample reader's rules, and one collides with them. The one-shot vetting skill itself is worth keeping.
>
> Verdict is relative to the [sample reader](reader/), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](README.md).

`2026-09-24` · neckbeard 1.12.0 · [jerrydboonstra/neckbeard](https://github.com/jerrydboonstra/neckbeard)

This target is neckbeard vetting itself, against the sample reader, not the setup that built it.

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟩 | **Cost** | ~270 tokens (the skill's description), every session; the full skill body loads only when invoked |
| 🟩 | **Reach** | none automatic. Zero hooks, so nothing fires until a person asks for it |
| 🟩 | **Leaves state** | the JSON dossier, only when `--out` is passed, only at that path (embeds the reader's rule files verbatim; never commit it) |
| 🟩 | **Live surface** | `git clone --depth 1`, only when the target is a git URL, into a temp dir removed after; no MCP servers |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 1 skill |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **1** | 🟥 per item |
| 🔁 | **already covered** | **2** | ⬜ per item |
| 🆕 | **new, standing rule** | **0** | 🟩 per item |
| 🆕 | **new, on-demand skill** | **1** | 🟩 per item |
| 🗑️ | **dropped** (persona, extras, no value) | **1** | ⬛ per item |

## ⛔ Conflicts: 1

| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| 1 | its report leans on a nine-symbol emoji key ("grids over prose; a cell is a phrase, not a paragraph") | "Plain language over jargon." | `examples/reader/CLAUDE.md` | 🟥 |

## 🔁 Already covered: 2

| its rule | covered by | held in |
|---|---|---|
| when exactly one rule survives a vet, "say so and let the reader decide" | "If a request is ambiguous and the wrong reading is costly, ask." (rule 5) | `examples/reader/rules/safety.md` |
| a proposed patch stays a diff; applying it is "a separate, explicitly-approved step" | "Say what you would change and let me decide." (rule 4) | `examples/reader/rules/engineering.md` |

## 🟩 Keep: 1

| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| 1 | `neckbeard`: vet a plugin, skill pack, or rule file before adopting it, then classify every rule it carries as duplicate, conflict, or new | skill | 🆕 |

## 🗑️ Dropped

`persona framing ("reads the whole thing before it trusts the plugin")`

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| skill: `skills/neckbeard/SKILL.md` | on demand, invoked by name | no (no hooks) | ~14 KB body · ~270 tokens description, always-on |

## ✅ Do this

- ⬜ 1. Install the skill. Its only always-on cost is its own description, and it never runs unless asked.
- ⬜ 2. Before trusting a report from it against your own setup, check whether its default grid-and-emoji format suits how you like answers, since that format is the one thing here that pulls against a rule you already run.

Carrying-cost case: zero hooks and zero always-on cost beyond the description, so nothing to weigh; the only question was whether the rule and the skill were good, and one of the two habits checked was not.

## 📋 Proposed rules patch

Nothing to add as a standing rule. The one genuinely new item is the skill itself (see Keep), and the one conflict is a report-formatting habit inside that skill, not a rule to add to a global rules file.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
