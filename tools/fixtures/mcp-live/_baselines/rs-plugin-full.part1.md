## What it adds

### Injects
- Skills:
  - a: description every session (16 chars); the file on demand (52 bytes, ~13 tokens)
- Rule files:
  - CLAUDE.md: every session (6 bytes, ~1 tokens)
- Hook-injected text:
  - hooks/inject.md: 15 bytes, ~3 tokens

### Hooks
- Hooks:
  - SessionStart: hooks/run.sh
  - reaches subagents: false (no event known to fire in a subagent)

### Subagents and commands
- Agents:
  - x
- Commands:
  - x

### State it may leave
- Persistence candidates:
  - hooks/install.sh

### Reaches outside the session
- MCP servers:
  - s (local-process, node)

### Source
- Kind: plugin
- Name: <ROOT> (from plugin.json)
- Version: 1.0.0 (from plugin.json)
- plugin.json:
  - name and version, shown above
- Marketplace: not applicable
- Commit: commit not given

Load timing is how Claude Code loads skills, not measured here. Tokens are estimated as bytes / 4; where the inventory fell back to a character count, "bytes" counts characters.
