## What it adds

### Injects
- Skills: none
- Rule files: none
- Hook-injected text: partly read
  - not read: hooks/hooks.json: unresolved hooks: SessionStart: hooks/run.sh; hooks/hooks.json: 1 hook(s) have unknown behaviour, which is not the same as none: 1 whose script was found but whose payload could not be traced. Read them by hand.

### Hooks
- Hooks: partly read
  - SessionStart: hooks/run.sh
  - reaches subagents: false (no event known to fire in a subagent)
  - not read: hooks/hooks.json: unresolved hooks: SessionStart: hooks/run.sh; hooks/hooks.json: 1 hook(s) have unknown behaviour, which is not the same as none: 1 whose script was found but whose payload could not be traced. Read them by hand.

### Subagents and commands
- Agents: none
- Commands: none

### State it may leave
- Persistence candidates: none

### Reaches outside the session
- MCP servers: none

### Source
- Kind: plugin
- Name: <ROOT> (from plugin.json)
- Version: 1.0.0 (from plugin.json)
- plugin.json:
  - name and version, shown above
- Marketplace: not applicable
- Commit: commit not given

Load timing is how Claude Code loads skills, not measured here. Tokens are estimated as bytes / 4; where the inventory fell back to a character count, "bytes" counts characters.
