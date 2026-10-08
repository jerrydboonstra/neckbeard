## What it adds

### Injects
- Skills: none
- Rule files: none
- Hook-injected text: none

### Hooks
- Hooks: none

### Subagents and commands
- Agents: none
- Commands: none

### State it may leave
- Persistence candidates: partly read
  - not read: .claude-plugin/marketplace.json: resolves outside the target tree; not scanned

### Reaches outside the session
- MCP servers: none

### Source
- Kind: plugin
- Name: <ROOT> (from plugin.json)
- Version: 1.0.0 (from plugin.json)
- plugin.json:
  - name and version, shown above
- Marketplace: not read: .claude-plugin/marketplace.json: resolves outside the target tree; not read
- Commit: commit not given

Load timing is how Claude Code loads skills, not measured here. Tokens are estimated as bytes / 4; where the inventory fell back to a character count, "bytes" counts characters.
