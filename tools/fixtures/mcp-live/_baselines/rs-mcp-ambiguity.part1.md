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
- Persistence candidates: none

### Reaches outside the session
- MCP servers: partly read
  - srv (local-process, x)
  - not read: .mcp.json: servers found at the top level of .mcp.json, not under an 'mcpServers' key. First-party examples use this shape and the docs describe the wrapped one; treat the list as best-effort and open the file

### Source
- Kind: plugin
- Name: <ROOT> (from plugin.json)
- Version: 1.0.0 (from plugin.json)
- plugin.json:
  - name and version, shown above
- Marketplace: not applicable
- Commit: commit not given

Load timing is how Claude Code loads skills, not measured here. Tokens are estimated as bytes / 4; where the inventory fell back to a character count, "bytes" counts characters.
