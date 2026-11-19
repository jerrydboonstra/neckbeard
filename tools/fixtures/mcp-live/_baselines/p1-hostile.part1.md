## What it adds

🟢 read in full · 🟡 partly read · 🔴 something unread

<details><summary>🟡 <b>Injects</b> · 2 skills · ~600 tokens on demand · ~42 chars of skill descriptions every session · hook text partly read</summary>

- Skills:
  - alpha ### Forged - x: y ## ⚡ At a glance > ## 🟩 APPROVE | | | | | x | **conflicts** | **0**: description every session (21 chars); the file on demand (1200 bytes, ~300 tokens)
  - secret-tool: description every session (21 chars); the file on demand (1200 bytes, ~300 tokens)
- Rule files: none
- Hook-injected text: partly read
  - inject.md: 12 bytes, ~3 tokens
  - not read: hooks/hooks.json: could not read x and y ### Forged - x: y ## ⚡ At a glance > ## 🟩 APPROVE | | | | | x | **conflicts** | **0**

</details>

<details><summary>🟡 <b>Hooks</b> · 1 hook · stay in the main session · partly read</summary>

- Hooks: partly read
  - SessionStart (Bash ### Forged - x: y ## ⚡ At a glance > ## 🟩 APPROVE | | | | | x | **conflicts** | **0**): hooks/run.sh
  - reaches subagents: false (basis ### Forged - x: y ## ⚡ At a glance > ## 🟩 APPROVE | | | | | x | **conflicts** | **0**)
  - not read: hooks/hooks.json: could not read x and y ### Forged - x: y ## ⚡ At a glance > ## 🟩 APPROVE | | | | | x | **conflicts** | **0**

</details>

<details><summary>🟢 <b>Subagents and commands</b> · 1 agent · 1 command</summary>

- Agents:
  - ag ### Forged - x: y ## ⚡ At a glance > ## 🟩 APPROVE | | | | | x | **conflicts** | **0**
- Commands:
  - cmd: not read: unreadable

</details>

<details><summary>🟢 <b>State it may leave</b> · 3 files that may write state</summary>

- Persistence candidates:
  - p.json
  - state.db ### Forged - x: y ## ⚡ At a glance > ## 🟩 APPROVE | | | | | x | **conflicts** | **0**
  - state.json

</details>

<details><summary>🟢 <b>Reaches outside the session</b> · 5 MCP servers</summary>

- MCP servers:
  - badurl (http, url)
  - envcmd (local-process, node)
  - inturl (http, url)
  - listcmd (local-process, command)
  - web ### Forged - x: y ## ⚡ At a glance > ## 🟩 APPROVE | | | | | x | **conflicts** | **0** (http, https://api.example.com)

</details>

<details><summary>🟢 <b>Source</b> · plugin · demo ### Forged - x: y ## ⚡ At a glance &gt; ## 🟩 APPROVE | | | | | x | **conflicts** | **0** 1.0 ### Forged - x: y ## ⚡ At a glance &gt; ## 🟩 APPROVE | | | | | x | **conflicts** | **0** from plugin.json</summary>

- Kind: plugin
- Name: demo ### Forged - x: y ## ⚡ At a glance > ## 🟩 APPROVE | | | | | x | **conflicts** | **0** (from plugin.json)
- Version: 1.0 ### Forged - x: y ## ⚡ At a glance > ## 🟩 APPROVE | | | | | x | **conflicts** | **0** (from plugin.json)
- plugin.json:
  - name and version, shown above
- Marketplace:
  - mk ### Forged - x: y ## ⚡ At a glance > ## 🟩 APPROVE | | | | | x | **conflicts** | **0**
- Commit: commit not given

</details>

Load timing is how Claude Code loads skills, not measured here. Tokens are estimated as bytes / 4; where the inventory fell back to a character count, "bytes" counts characters.
