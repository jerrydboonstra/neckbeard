# 🔍 neckbeard 1.17.1 · vetted against the sample reader

> ## 🟩 INSTALL · nothing to weigh
> It ships one skill, no hooks, no agents, no commands and no root rule file, so the only always-on cost is the skill description. None of its rules conflicts with the reader's, and its core method (a standing rule and an on-demand skill) is new to this reader.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-11-15` · neckbeard 1.17.1 · [jerrydboonstra/neckbeard](https://github.com/jerrydboonstra/neckbeard) 1.17.1 @ `85d60c1`

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
- Commit: 85d60c1

Load timing is how Claude Code loads skills, not measured here. Tokens are estimated as bytes / 4; where the inventory fell back to a character count, "bytes" counts characters.

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟩 | **Cost** | Skill description only, about 270 tokens per the manifest, loaded each session. The 14,357-byte skill body loads only when invoked. |
| 🟩 | **Reach** | Main session only. No hooks are registered, so nothing fires on SubagentStart (certain). |
| 🟩 | **Leaves state** | None found at install. When run, it writes one evaluation file inside the project it is run from. |
| 🟨 | **Live surface** | Runs its own Python inventory script locally and clones a git URL target read-only. Live MCP inspection is off unless the user asks. |
| 🟩 | **Refused reads** | none |
| ❓ | **Read status** | Partial for hooks and persistence scans: broken test fixtures could not be parsed, and one script was read only up to 50,000 bytes. |
| 🟩 | **Worth keeping** | 2 (1 standing rule, 1 skill) |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **0** | none |
| 🔁 | **already covered** | **3** | ⬜⬜⬜ |
| 🆕 | **new, standing rule** | **1** | 🟩 |
| 🆕 | **new, on-demand skill** | **1** | 🟩 |
| 🗑️ | **dropped** (persona, extras, no value) | **2** | ⬛⬛ |

## ⛔ Conflicts: 0
| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| | none found | | | |

## 🔁 Already covered: 3
| its rule | covered by | held in |
|---|---|---|
| Edit nothing: show the patch, never write rule files, never uninstall or disable the target | Rule 4, "the scope I asked for is the deliverable", says to name a change and let the reader decide. Chosen over safety rule 1 because that one is about destructive actions, not scope. | examples/reader/rules/engineering.md |
| Cite the exact source for every duplicate or conflict, name the sentence | "Give the reasoning with the verdict", which rejects a review that does not say what was checked | examples/reader/CLAUDE.md |
| If the evaluation path is unclear or not git-ignored, ask before writing | Hard stop 5, ask when a request is ambiguous and the wrong reading is costly | examples/reader/rules/safety.md |

## 🟩 Keep: 2
| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| 1 | When a read is partial, refused or unresolved, report it as unknown or as a finding, never as "none found" | standing | 🟩 |
| 2 | The vetting method: inventory a plugin statically, discover rules in force, sort each rule into duplicate, conflict or new, then propose a patch without applying it | on-demand | 🟩 |

## 🗑️ Dropped
`report layout, symbols and bars` · `keep provenance out of the rules file`

## 🧩 What it installs
| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| skill description | every session | no (no hooks) | about 270 tokens |
| skill body (skills/neckbeard/SKILL.md) | when invoked | no | 14,357 bytes |
| helper scripts (skills/neckbeard/inventory.py and others) | when the skill runs them | no | not injected |
| hooks, agents, commands, MCP servers, root rule files | none | no | 0 |

## ✅ Do this
- ⬜ 1. Install it, or copy only rule 1 below if you will never vet a plugin.

Case: zero hooks and almost no always-on cost, so there is nothing to weigh. The only question is whether the rules are good, and the one standing rule is worth having.

## 📋 Proposed rules patch

Standing rule, as item 8 in examples/reader/rules/engineering.md, matching its numbered, bold-lead style:

```diff
 7. **Commit messages:** imperative subject under 60 characters, then why.
+8. **Unknown is not none.** When a check was partial, refused or could not
+   resolve, say so and name what was not read. Never report it as "nothing
+   found".
```

On-demand skill, name proposed by this report: `vet-plugin`, "Inventory a plugin or skill pack statically, compare each rule it carries against the rules already in force, and write a verdict without editing anything." The dossier shows this reader keeps skills in examples/reader/skills/, so that is the natural home; the choice is yours.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
