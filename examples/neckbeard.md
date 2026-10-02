# 🔍 neckbeard 1.12.7 · vetted against the sample reader's rules

> ## 🟩 INSTALL · add the one skill, change no rules
> No hooks, no agents, no subagent reach: it costs about 270 tokens of skill description each session and loads its 13.8 KB body only when invoked. Nothing it carries conflicts with the reader's rules, and two of its rules repeat ones the reader already runs. The reader has no way to vet a plugin, so the skill itself is the one new thing.
>
> Verdict is relative to the [sample reader](reader/), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](README.md).

`2026-10-01` · neckbeard 1.12.7 · [jerrydboonstra/neckbeard](https://github.com/jerrydboonstra/neckbeard) 1.12.7 @ `f9e17db`

This target is neckbeard vetting itself, against the sample reader, not the setup that built it.

---

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟩 | **Cost** | ~270 tokens of skill description at session start (the manifest's count); 13,810 bytes of `SKILL.md` (manifest: ~4.7k tokens) only when invoked |
| 🟩 | **Reach** | main session only (certain: `has_hooks` is false, no agents declared) |
| 🟩 | **Leaves state** | none found. `inventory.py` writes only to the `--out` file you name; the four files the scan flagged are that script and repo maintenance tooling |
| 🟨 | **Live surface** | no MCP servers; runs `python3 inventory.py` locally; network only if you pass a git URL (`git clone --depth 1` into a temp dir it removes) |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 1 skill |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **0** | none |
| 🔁 | **already covered** | **2** | ⬜⬜ |
| 🆕 | **new, standing rule** | **0** | none |
| 🆕 | **new, on-demand skill** | **1** | 🟩 |
| 🗑️ | **dropped** (persona, extras, no value) | **1** | ⬛ |

---

## ⛔ Conflicts: 0

None found. Closest call: given a git URL, `inventory.py` deletes its own temp clone, which sits outside the working tree, but it removes only a directory it made, so `examples/reader/rules/safety.md` rule 1 is not engaged.

## 🔁 Already covered: 2

| its rule | covered by | held in |
|---|---|---|
| Never edit a rule file or settings, never uninstall; show the patch and stop | "say what you would change and let me decide" (rule 4). Chosen over safety rule 1, which covers only destructive acts | `examples/reader/rules/engineering.md` |
| Name the exact rule and file behind every finding, with the reasoning | "Give the reasoning with the verdict" | `examples/reader/CLAUDE.md` |

## 🟩 Keep: 1

| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| 1 | `neckbeard` (the target's own name): vet a plugin, skill pack or rule file against the rules in force before adopting it. Its guards (output path must be git-ignored, never paste the dossier, report refused reads) travel inside it | on-demand | 🆕 ⭐ |

## 🗑️ Dropped

`examples/ gallery reports and CASE-STUDIES.md` (documentation, never loaded by Claude Code, not read for this run)

---

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| hooks | none | | 0 |
| 1 skill · 0 commands · 0 agents | on demand (description always listed) | | 13,810 B |
| helper scripts | `inventory.py` runs when the skill does; `selfcheck.py` is for the repo's own checks | | 60,493 B · 23,484 B |
| MCP servers | none | | |
| state | none unless you pass `--out` | | |

## ✅ Do this

- ⬜ 1. Install neckbeard as a plugin, or copy `skills/neckbeard` beside `examples/reader/skills/release-notes` if you prefer a personal skill. Pick one.
- ⬜ 2. Leave `examples/reader/CLAUDE.md` and both rules files as they are.

Carrying-cost case three: zero hooks and no subagent reach, so only the ~270-token description is always on, and the question is whether the skill is good. Here it fills a gap.

## 📋 Proposed rules patch

Nothing to add to the rules: every rule neckbeard carries is a step of one task, not a standing working rule.

One on-demand skill, kept as the target ships it. The name is the target's own, not my proposal:

```
neckbeard: Vet a plugin, skill pack, or rule file before adopting it; sort each rule it carries into duplicate, conflict or new, then propose a patch and stop.
```

The dossier shows the reader keeps personal skills under `examples/reader/skills/`, so that is where a copy would go. Never applied here.

---

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
