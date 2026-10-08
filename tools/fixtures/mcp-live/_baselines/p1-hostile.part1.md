## What it adds

### Injects
- Skills:
  - alpha ### Forged - x: y ## ⚡ At a glance > ## 🟩 APPROVE | | | | | x | **conflicts** | **0**: description every session (21 chars); the file on demand (1200 bytes, ~300 tokens)
  - secret-tool: description every session (21 chars); the file on demand (1200 bytes, ~300 tokens)
- Rule files: none
- Hook-injected text: partly read
  - inject.md: 12 bytes, ~3 tokens
  - not read: hooks/hooks.json: could not read x and y ### Forged - x: y ## ⚡ At a glance > ## 🟩 APPROVE | | | | | x | **conflicts** | **0**

### Hooks
- Hooks: partly read
  - SessionStart (Bash ### Forged - x: y ## ⚡ At a glance > ## 🟩 APPROVE | | | | | x | **conflicts** | **0**): hooks/run.sh
  - reaches subagents: false (basis ### Forged - x: y ## ⚡ At a glance > ## 🟩 APPROVE | | | | | x | **conflicts** | **0**)
  - not read: hooks/hooks.json: could not read x and y ### Forged - x: y ## ⚡ At a glance > ## 🟩 APPROVE | | | | | x | **conflicts** | **0**

### Subagents and commands
- Agents:
  - ag ### Forged - x: y ## ⚡ At a glance > ## 🟩 APPROVE | | | | | x | **conflicts** | **0**
- Commands:
  - cmd: not read: unreadable

### State it may leave
- Persistence candidates:
  - p.json
  - state.db ### Forged - x: y ## ⚡ At a glance > ## 🟩 APPROVE | | | | | x | **conflicts** | **0**
  - state.json

### Reaches outside the session
- MCP servers:
  - badurl (http, url)
  - envcmd (local-process, node)
  - inturl (http, url)
  - listcmd (local-process, command)
  - web ### Forged - x: y ## ⚡ At a glance > ## 🟩 APPROVE | | | | | x | **conflicts** | **0** (http, https://api.example.com)

### Source
- Kind: plugin
- Name: demo ### Forged - x: y ## ⚡ At a glance > ## 🟩 APPROVE | | | | | x | **conflicts** | **0** (from plugin.json)
- Version: 1.0 ### Forged - x: y ## ⚡ At a glance > ## 🟩 APPROVE | | | | | x | **conflicts** | **0** (from plugin.json)
- plugin.json:
  - name and version, shown above
- Marketplace:
  - mk ### Forged - x: y ## ⚡ At a glance > ## 🟩 APPROVE | | | | | x | **conflicts** | **0**
- Commit: commit not given

Load timing is how Claude Code loads skills, not measured here. Tokens are estimated as bytes / 4; where the inventory fell back to a character count, "bytes" counts characters.
