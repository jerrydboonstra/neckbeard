## What it adds

### Injects
- Skills: none
- Rule files: none
- Hook-injected text: none

### Hooks
- Hooks:
  - Notification: hooks/e.sh
  - PostCompact: hooks/d.sh
  - PostToolUse: <unparsed command>
  - PreCompact: hooks/c.sh
  - PreToolUse: hooks/f.sh
  - SessionEnd: bin/meow
  - SessionStart: hooks/a.sh
  - Stop: hooks/b.sh
  - SubagentStop: hooks/h.sh
  - UserPromptSubmit: <unparsed command>
  - reaches subagents: unknown

### Subagents and commands
- Agents: none
- Commands: none

### State it may leave
- Persistence candidates: none

### Reaches outside the session
- MCP servers: none

### Source
- Kind: plugin
- Name: demo
- Version: no version
- plugin.json: none
- Marketplace: none
- Commit: commit not given

Load timing is how Claude Code loads skills, not measured here. Tokens are estimated as bytes / 4; where the inventory fell back to a character count, "bytes" counts characters.
