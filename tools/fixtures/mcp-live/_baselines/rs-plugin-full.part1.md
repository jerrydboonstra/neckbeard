## What it adds

🟢 read in full · 🟡 partly read · 🔴 something unread

<details><summary>🟢 <b>Injects</b> · 1 skills · ~13 tokens on demand · ~16 chars of skill descriptions every session · hook text read in full</summary>

- Skills:
  - a: description every session (16 chars); the file on demand (52 bytes, ~13 tokens)
- Rule files:
  - CLAUDE.md: every session (6 bytes, ~1 tokens)
- Hook-injected text:
  - hooks/inject.md: 15 bytes, ~3 tokens

</details>

<details><summary>🟢 <b>Hooks</b> · 1 hooks · stay in the main session · read in full</summary>

- Hooks:
  - SessionStart: hooks/run.sh
  - reaches subagents: false (no event known to fire in a subagent)

</details>

<details><summary>🟢 <b>Subagents and commands</b> · 1 agents · 1 commands</summary>

- Agents:
  - x
- Commands:
  - x

</details>

<details><summary>🟢 <b>State it may leave</b> · 1 files that may write state</summary>

- Persistence candidates:
  - hooks/install.sh

</details>

<details><summary>🟢 <b>Reaches outside the session</b> · 1 MCP servers</summary>

- MCP servers:
  - s (local-process, node)

</details>

<details><summary>🟢 <b>Source</b> · plugin · <ROOT> 1.0.0 from plugin.json · no marketplace</summary>

- Kind: plugin
- Name: <ROOT> (from plugin.json)
- Version: 1.0.0 (from plugin.json)
- plugin.json:
  - name and version, shown above
- Marketplace: not applicable
- Commit: commit not given

</details>

Load timing is how Claude Code loads skills, not measured here. Tokens are estimated as bytes / 4; where the inventory fell back to a character count, "bytes" counts characters.
