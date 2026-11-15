# 🔍 neckbeard 1.17.1 · vetted against the sample reader

> ## 🟩 INSTALL · the vetting skill is new to this reader and nothing in it conflicts
> It has no hooks and no agents, and its only always-on cost is a 766-byte skill description. Nothing in it collides with a rule the reader runs, and the reader has no vetting skill of its own, so the one on-demand skill is the reason to install it.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-11-15` · neckbeard 1.17.1 · [jerrydboonstra/neckbeard](https://github.com/jerrydboonstra/neckbeard) 1.17.1 @ `ba87cb2`

Baseline: the sample reader · 4 rule files · 2347 bytes · sha256 b564c945bf65

<details><summary>Rule files</summary>

- `CLAUDE.md`
- `rules/engineering.md`
- `rules/safety.md`
- `skills/release-notes/SKILL.md`

</details>

## What it adds

### Injects
- Skills:
  - neckbeard: description every session (764 chars); the file on demand (14535 bytes, ~3633 tokens)
- Rule files: none
- Hook-injected text: partly read
  - neckbeard did not read: tools/fixtures/read-status/hooks-search-dangling/data/x.json: could not be read; not searched for hooks
  - broken in the plugin: tools/fixtures/read-status/hooks-search-bad-json/data/broken.json: not valid JSON; not searched for hooks; tools/fixtures/read-status/mcp-malformed/.mcp.json: not valid JSON; not searched for hooks

### Hooks
- Hooks: partly read
  - reaches subagents: unknown
  - neckbeard did not read: tools/fixtures/read-status/hooks-search-dangling/data/x.json: could not be read; not searched for hooks
  - broken in the plugin: tools/fixtures/read-status/hooks-search-bad-json/data/broken.json: not valid JSON; not searched for hooks; tools/fixtures/read-status/mcp-malformed/.mcp.json: not valid JSON; not searched for hooks

### Subagents and commands
- Agents: none
- Commands: none

### State it may leave
- Persistence candidates: partly read
  - Makefile
  - measurements/2026-10-16-units-confirm/reconfirm.py
  - skills/neckbeard/inventory.py
  - skills/neckbeard/mcp_live.py
  - skills/neckbeard/selfcheck.py
  - tools/deploy-host.sh
  - tools/excerpts
  - tools/mutate-selfcheck
  - tools/part1
  - tools/rule-units
  - and 12 more, in: tools/ 12
  - neckbeard did not read: tools/fixtures/read-status/persist-dangling/scripts/x.sh: could not be read; not scanned; skills/neckbeard/inventory.py: read capped at 50000 bytes

### Reaches outside the session
- MCP servers: none

### Source
- Kind: plugin
- Name: neckbeard (from plugin.json)
- Version: 1.17.1 (from plugin.json)
- plugin.json:
  - name and version, shown above
- Marketplace: none
- Commit: ba87cb2

Load timing is how Claude Code loads skills, not measured here. Tokens are estimated as bytes / 4; where the inventory fell back to a character count, "bytes" counts characters.

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟩 | **Cost** | 766 bytes of skill description at every session start; the 14,535-byte skill body loads only when invoked |
| 🟩 | **Reach** | Main session only (certain: no hooks, so no SubagentStart hook) |
| 🟨 | **Leaves state** | None at install. When used, it writes an evaluation file into the project and, with `--out`, a dossier; a git-URL target is cloned to a temp dir that is removed. The scan of `skills/neckbeard/inventory.py` was capped at 50,000 of 105,514 bytes, so that file's writes are only partly checked |
| 🟩 | **Live surface** | None by default (static read). `--live-mcp` is opt-in and starts a target's local stdio server; `git clone` for URL targets |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 1 skill |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **0** | none |
| 🔁 | **already covered** | **2** | ⬜ ⬜ |
| 🆕 | **new, standing rule** | **0** | none |
| 🆕 | **new, on-demand skill** | **1** | 🟩 |
| 🗑️ | **dropped** (persona, extras, no value) | **2** | ⬛ ⬛ |

## ⛔ Conflicts: 0
None. The skill writes only an evaluation file after checking the path is git-ignored, and it asks before writing when the path is not ignored. That fits `examples/reader/rules/safety.md` rules 1 and 2 (no destructive action, no push to `main`). It spawns no subagents, so `examples/reader/rules/engineering.md` rule 6 is not touched.

## 🔁 Already covered: 2
| its rule | covered by | held in |
|---|---|---|
| Never edit a rule file or uninstall the target; show the patch and wait for a separate approval | Engineering rule 4: "say what you would change and let me decide". I chose it over safety rule 1 because it states the approval gate directly, while safety rule 1 only covers destructive actions | `examples/reader/rules/engineering.md` |
| Cite, don't gesture: name the exact rule and file for each conflict or duplicate | "Give the reasoning with the verdict", where "looks fine" without what was checked is not a review. This states the same demand as its own rule | `examples/reader/CLAUDE.md` |

## 🟩 Keep: 1
| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| 1 | The vetting procedure as one skill: static inventory with live MCP only on explicit request; a hook missing from the resolved list is not "injects nothing"; every refused read is a finding; classify each rule with exact citations; if one rule survives, say copy-as-text is the cheaper choice; check the output path is git-ignored because the dossier embeds the reader's own rules | on-demand skill | 🟩 |

## 🗑️ Dropped
`report layout rules: bars, symbols, grid shape, plain Markdown only (cosmetic, no value to this reader's rules)` · `dated incident notes inside the method text (history, not instruction)`

## 🧩 What it installs
| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| `skills/neckbeard/SKILL.md` description | every session | no | 766 B |
| `skills/neckbeard/SKILL.md` body | when invoked | no | 14,535 B |
| `skills/neckbeard/inventory.py`, `mcp_live.py`, `selfcheck.py` | run by the skill on request | no | 168,881 B |
| hooks, commands, agents, MCP servers | none | no | 0 |

## ✅ Do this
- ⬜ 1. Install the plugin and invoke it only when vetting something; no rule needs copying.

Carrying-cost case: no hooks and no subagent reach, so only the small description is always on, and the skill's value is a script plus a method that cannot be copied as a single rule.

## 📋 Proposed rules patch
Nothing to add. The one new item is an on-demand skill, and it arrives as the plugin's own `neckbeard` skill, so no skill needs writing. The dossier shows this reader keeps personal skills under `examples/reader/skills/`, but a plugin install needs no copy there.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
