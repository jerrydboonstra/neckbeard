## What it adds

### Injects
- Skills: partly read
  - alpha: description every session (21 chars); the file on demand (1200 bytes, ~300 tokens)
  - gamma: not read: resolves outside the target tree
  - not read: skills: one entry could not be read (dangling symlink)
- Rule files: partly read
  - CLAUDE.md: every session (400 bytes, ~100 tokens)
  - not read: rule_files: one entry could not be read (dangling symlink)
- Hook-injected text: partly read
  - hooks/inject.md: 80 bytes, ~20 tokens
  - not read: hooks: one entry could not be read (dangling symlink)

### Hooks
- Hooks: partly read
  - PreToolUse (Bash): hooks/guard.sh
  - SessionStart: hooks/run.sh
  - reaches subagents: false (no event known to fire in a subagent)
  - not read: hooks: one entry could not be read (dangling symlink)

### Subagents and commands
- Agents: partly read
  - reviewer
  - not read: agents: one entry could not be read (dangling symlink)
- Commands: partly read
  - ship
  - not read: commands: one entry could not be read (dangling symlink)

### State it may leave
- Persistence candidates: partly read
  - scripts/install.sh
  - not read: persistence_candidates: one entry could not be read (dangling symlink)

### Reaches outside the session
- MCP servers: partly read
  - files (local-process, node)
  - web (http, https://api.example.com)
  - not read: mcp_servers: one entry could not be read (dangling symlink)

### Source
- Kind: plugin
- Name: demo (from plugin.json)
- Version: 1.2.0 (from plugin.json)
- plugin.json: partly read
  - name and version, shown above
  - not read: plugin_json: one entry could not be read (dangling symlink)
- Marketplace: partly read
  - m
  - not read: marketplace: one entry could not be read (dangling symlink)
- Commit: commit not given

Load timing is how Claude Code loads skills, not measured here. Tokens are estimated as bytes / 4; where the inventory fell back to a character count, "bytes" counts characters.
