## What it adds

### Injects
- Skills: none
- Rule files: none
- Hook-injected text:
  - hooks/session-start.sh (SessionStart, built at run time, at least 66 bytes): imagegen doctor: … missing; run skills/imagegen/doctor.sh for fixes
  writes: mkdir -p …; : > …
  - built at run time: read from the script's own text, not run; commands it runs are not followed and may print or write files

### Hooks
- Hooks:
  - SessionStart: hooks/session-start.sh
  - reaches subagents: false (no event known to fire in a subagent)

### Subagents and commands
- Agents: none
- Commands: none

### State it may leave
- Persistence candidates:
  - hooks/session-start.sh

### Reaches outside the session
- MCP servers: none

### Source
- Kind: generic-pack
- Name: <ROOT>
- Version: no version
- plugin.json: not applicable
- Marketplace: not applicable
- Commit: commit not given

Load timing is how Claude Code loads skills, not measured here. Tokens are estimated as bytes / 4; where the inventory fell back to a character count, "bytes" counts characters.
