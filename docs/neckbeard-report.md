# 🔍 neckbeard 1.17.0 · what it adds

`2026-11-12` · neckbeard 1.17.0 · [jerrydboonstra/neckbeard](https://github.com/jerrydboonstra/neckbeard) 1.17.0 @ `eefa633`

## What it adds

### Injects
- Skills:
  - neckbeard: description every session (764 chars); the file on demand (14535 bytes, ~3633 tokens)
- Rule files: none
- Hook-injected text: partly read
  - neckbeard did not read: tools/fixtures/read-status/hooks-search-dangling/data/x.json: could not be read; not searched for hooks
  - broken in the plugin: tools/fixtures/read-status/hooks-search-bad-json/data/broken.json: not valid JSON; not searched for hooks; tools/fixtures/read-status/mcp-malformed/.mcp.json: not valid JSON; not searched for hooks

### Hooks
- Hooks: partly read
  - reaches subagents: unknown
  - neckbeard did not read: tools/fixtures/read-status/hooks-search-dangling/data/x.json: could not be read; not searched for hooks
  - broken in the plugin: tools/fixtures/read-status/hooks-search-bad-json/data/broken.json: not valid JSON; not searched for hooks; tools/fixtures/read-status/mcp-malformed/.mcp.json: not valid JSON; not searched for hooks

### Subagents and commands
- Agents: none
- Commands: none

### State it may leave
- Persistence candidates: partly read
  - Makefile
  - measurements/2026-10-16-units-confirm/reconfirm.py
  - skills/neckbeard/inventory.py
  - skills/neckbeard/mcp_live.py
  - skills/neckbeard/selfcheck.py
  - tools/deploy-host.sh
  - tools/excerpts
  - tools/mutate-selfcheck
  - tools/part1
  - tools/rule-units
  - and 10 more, in: tools/ 10
  - neckbeard did not read: tools/fixtures/read-status/persist-dangling/scripts/x.sh: could not be read; not scanned; skills/neckbeard/inventory.py: read capped at 50000 bytes

### Reaches outside the session
- MCP servers: none

### Source
- Kind: plugin
- Name: neckbeard (from plugin.json)
- Version: 1.17.0 (from plugin.json)
- plugin.json:
  - name and version, shown above
- Marketplace: none
- Commit: eefa633

Load timing is how Claude Code loads skills, not measured here. Tokens are estimated as bytes / 4; where the inventory fell back to a character count, "bytes" counts characters.

No reader's rules were read: this report lists facts only and carries no verdict.
