## What it adds

🟢 read in full · 🟡 partly read · 🔴 something unread

<details><summary>🟡 <b>Injects</b> · 2 skills · ~300 tokens on demand · ~21 chars of skill descriptions every session · hook text partly read</summary>

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

</details>

<details><summary>🟡 <b>Hooks</b> · 2 hooks · stay in the main session · partly read</summary>

- Hooks: partly read
  - PreToolUse (Bash): hooks/guard.sh
  - SessionStart: hooks/run.sh
  - reaches subagents: false (no event known to fire in a subagent)
  - not read: hooks: one entry could not be read (dangling symlink)

</details>

<details><summary>🟡 <b>Subagents and commands</b> · 1 agents · 1 commands</summary>

- Agents: partly read
  - reviewer
  - not read: agents: one entry could not be read (dangling symlink)
- Commands: partly read
  - ship
  - not read: commands: one entry could not be read (dangling symlink)

</details>

<details><summary>🟡 <b>State it may leave</b> · 1 file that may write state</summary>

- Persistence candidates: partly read
  - scripts/install.sh
  - not read: persistence_candidates: one entry could not be read (dangling symlink)

</details>

<details><summary>🟡 <b>Reaches outside the session</b> · 2 MCP servers</summary>

- MCP servers: partly read
  - files (local-process, node)
  - web (http, https://api.example.com)
  - not read: mcp_servers: one entry could not be read (dangling symlink)

</details>

<details><summary>🟡 <b>Source</b> · plugin · demo 1.2.0 from plugin.json</summary>

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

</details>

Load timing is how Claude Code loads skills, not measured here. Tokens are estimated as bytes / 4; where the inventory fell back to a character count, "bytes" counts characters.
