# 🔍 ponytail 5.3.3 · what it adds

`2026-11-15` · neckbeard 1.17.1 · [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) 5.3.3 @ `7801d06`

## What it adds

### Injects
- Skills:
  - ponytail-audit: description every session (346 chars); the file on demand (5417 bytes, ~1354 tokens)
  - ponytail-debt: description every session (201 chars); the file on demand (1769 bytes, ~442 tokens)
  - ponytail-gain: description every session (160 chars); the file on demand (2164 bytes, ~541 tokens)
  - ponytail-help: description every session (141 chars); the file on demand (3188 bytes, ~797 tokens)
  - ponytail-review: description every session (370 chars); the file on demand (5143 bytes, ~1285 tokens)
  - ponytail: description every session (366 chars); the file on demand (3496 bytes, ~874 tokens)
- Rule files: none
- Hook-injected text: partly read
  - neckbeard did not read: hooks/claude-codex-hooks.json, hooks/claude-band.json: unidentifiable hooks: SessionStart: <unparsed command>; SubagentStart: <unparsed command>; UserPromptSubmit: <unparsed command>; hooks/claude-codex-hooks.json, hooks/claude-band.json: 3 hook(s) have unknown behaviour, which is not the same as none: 3 whose script could not even be identified from the command. Read them by hand.

### Hooks
- Hooks: partly read
  - SessionStart (startup|resume|clear|compact): <unparsed command>
  - SubagentStart: <unparsed command>
  - UserPromptSubmit: <unparsed command>
  - reaches subagents: true (documented: a Subagent* event, or PreToolUse/PostToolUse which the docs say fire inside subagents)
  - neckbeard did not read: hooks/claude-codex-hooks.json, hooks/claude-band.json: unidentifiable hooks: SessionStart: <unparsed command>; SubagentStart: <unparsed command>; UserPromptSubmit: <unparsed command>; hooks/claude-codex-hooks.json, hooks/claude-band.json: 3 hook(s) have unknown behaviour, which is not the same as none: 3 whose script could not even be identified from the command. Read them by hand.

### Subagents and commands
- Agents: none
- Commands:
  - ponytail
  - ponytail-audit
  - ponytail-debt
  - ponytail-gain
  - ponytail-help
  - ponytail-review

### State it may leave
- Persistence candidates:
  - .opencode/plugins/ponytail-frontmatter.cjs
  - .opencode/plugins/ponytail.mjs
  - __init__.py
  - hooks/band/board.ts
  - hooks/band/metrics.ts
  - hooks/ponytail-activate.js
  - hooks/ponytail-band-import.js
  - hooks/ponytail-config.js
  - hooks/ponytail-instructions.js
  - hooks/ponytail-map.js
  - and 8 more, in: scripts/ 5, hooks/ 3

### Reaches outside the session
- MCP servers: none

### Source
- Kind: plugin
- Name: ponytail (from plugin.json)
- Version: 5.3.3 (from plugin.json)
- plugin.json:
  - name and version, shown above
- Marketplace: none
- Commit: 7801d06

Load timing is how Claude Code loads skills, not measured here. Tokens are estimated as bytes / 4; where the inventory fell back to a character count, "bytes" counts characters.

No reader's rules were read: this report lists facts only and carries no verdict.
