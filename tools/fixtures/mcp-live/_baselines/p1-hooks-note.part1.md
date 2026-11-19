## What it adds

🟢 read in full · 🟡 partly read · 🔴 something unread

<details><summary>🔴 <b>Injects</b> · 2 skills · ~375 tokens on demand · ~22 chars of skill descriptions every session · hook text something unread</summary>

- Skills:
  - alpha: description every session (21 chars); the file on demand (1200 bytes, ~300 tokens)
  - beta: description every session (1 chars); the file on demand (303 bytes, ~75 tokens) (read capped)
- Rule files:
  - CLAUDE.md: every session (400 bytes, ~100 tokens)
- Hook-injected text: neckbeard did not read: hook payloads cannot be traced

</details>

<details><summary>🟢 <b>Hooks</b> · 2 hooks · stay in the main session · read in full</summary>

- Hooks:
  - PreToolUse (Bash): hooks/guard.sh
  - SessionStart: hooks/run.sh
  - reaches subagents: false (no event known to fire in a subagent)

</details>

<details><summary>🟢 <b>Subagents and commands</b> · 1 agent · 1 command</summary>

- Agents:
  - reviewer
- Commands:
  - ship

</details>

<details><summary>🟢 <b>State it may leave</b> · 2 files that may write state</summary>

- Persistence candidates:
  - hooks/run.sh
  - scripts/install.sh

</details>

<details><summary>🟢 <b>Reaches outside the session</b> · 2 MCP servers</summary>

- MCP servers:
  - files (local-process, node)
  - web (http, https://api.example.com)

</details>

<details><summary>🟢 <b>Source</b> · plugin · demo 1.2.0 from plugin.json</summary>

- Kind: plugin
- Name: demo (from plugin.json)
- Version: 1.2.0 (from plugin.json)
- plugin.json:
  - name and version, shown above
- Marketplace:
  - m
- Commit: commit not given

</details>

Load timing is how Claude Code loads skills, not measured here. Tokens are estimated as bytes / 4; where the inventory fell back to a character count, "bytes" counts characters.
