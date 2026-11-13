## What it adds

### Injects
- Skills: none
- Rule files: none
- Hook-injected text: none

### Hooks
- Hooks:
  - Elicitation: <unparsed command>
  - ElicitationResult: <unparsed command>
  - Notification: homehook.sh
  - PermissionRequest: <unparsed command>
  - PostCompact: <unparsed command>
  - PostToolUse: x.sh
  - PostToolUseFailure: ./x.sh
  - PreCompact: <unparsed command>
  - PreToolUse: <unparsed command>
  - SessionEnd: <unparsed command>
  - SessionStart: ./hook.sh
  - Setup: x.sh
  - Stop: <unparsed command>
  - SubagentStart: <unparsed command>
  - SubagentStop: script.py
  - TaskCompleted: ./a.sh
  - TeammateIdle: http.server
  - UserPromptSubmit: envhome.sh
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
