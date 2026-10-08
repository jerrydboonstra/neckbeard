## What it adds

### Injects
- Skills:
  - alpha: description every session (21 chars); the file on demand (1200 bytes, ~300 tokens)
  - beta: description every session (1 chars); the file on demand (303 bytes, ~75 tokens) (read capped)
- Rule files:
  - CLAUDE.md: every session (400 bytes, ~100 tokens)
- Hook-injected text:
  - hooks/inject.md: 80 bytes, ~20 tokens

### Hooks
- Hooks:
  - PreToolUse (Bash): hooks/guard.sh
  - SessionStart: hooks/run.sh
  - reaches subagents: false (no event known to fire in a subagent)

### Subagents and commands
- Agents:
  - reviewer
- Commands:
  - ship

### State it may leave
- Persistence candidates:
  - hooks/run.sh
  - scripts/install.sh

### Reaches outside the session
- MCP servers:
  - files (local-process, node)
  - web (http, https://api.example.com)

### Source
- Kind: plugin
- Name: demo (from plugin.json)
- Version: 1.2.0 (from plugin.json)
- plugin.json:
  - name and version, shown above
- Marketplace:
  - m
- Commit: commit not given

Load timing is how Claude Code loads skills, not measured here. Tokens are estimated as bytes / 4; where the inventory fell back to a character count, "bytes" counts characters.
