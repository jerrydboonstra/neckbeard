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
  - bad (local-process)
  - good (local-process, x)
  - not read: .mcp.json: server 'bad' is not an object, so its command and url were not read

### Source
- Kind: plugin
- Name: <ROOT> (from plugin.json)
- Version: 1.0.0 (from plugin.json)
- plugin.json:
  - name and version, shown above
- Marketplace: not applicable
- Commit: commit not given

Load timing is how Claude Code loads skills, not measured here. Tokens are estimated as bytes / 4; where the inventory fell back to a character count, "bytes" counts characters.
