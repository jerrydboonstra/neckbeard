## What it adds

🟢 read in full · 🟡 partly read · 🔴 something unread

<details><summary>🟢 <b>Injects</b> · 0 skills · ~0 tokens on demand · ~0 chars of skill descriptions every session · hook text read in full</summary>

- Skills: none
- Rule files: none
- Hook-injected text:
  - hooks/session-start.sh (SessionStart, built at run time, at least 66 bytes): imagegen doctor: … missing; run skills/imagegen/doctor.sh for fixes
  writes: mkdir -p …; : > …
  - built at run time: read from the script's own text, not run; commands it runs are not followed and may print or write files

</details>

<details><summary>🟢 <b>Hooks</b> · 1 hook · stay in the main session · read in full</summary>

- Hooks:
  - SessionStart: hooks/session-start.sh
  - reaches subagents: false (no event known to fire in a subagent)

</details>

<details><summary>🟢 <b>Subagents and commands</b> · no agents · 0 commands</summary>

- Agents: none
- Commands: none

</details>

<details><summary>🟢 <b>State it may leave</b> · 1 file that may write state</summary>

- Persistence candidates:
  - hooks/session-start.sh

</details>

<details><summary>🟢 <b>Reaches outside the session</b> · no MCP servers</summary>

- MCP servers: none

</details>

<details><summary>🟢 <b>Source</b> · generic-pack · <ROOT> · no marketplace</summary>

- Kind: generic-pack
- Name: <ROOT>
- Version: no version
- plugin.json: not applicable
- Marketplace: not applicable
- Commit: commit not given

</details>

Load timing is how Claude Code loads skills, not measured here. Tokens are estimated as bytes / 4; where the inventory fell back to a character count, "bytes" counts characters.
