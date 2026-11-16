# 🔍 neckbeard 1.17.4 · what it adds

`2026-11-15` · neckbeard 1.17.4 · [jerrydboonstra/neckbeard](https://github.com/jerrydboonstra/neckbeard) 1.17.4 @ `024f5aa`

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
  - skills/neckbeard/inventory_core.py
  - skills/neckbeard/inventory_hooks.py
  - skills/neckbeard/inventory_parts.py
  - skills/neckbeard/mcp_live.py
  - skills/neckbeard/selfcheck.py
  - tools/deploy-host.sh
  - tools/excerpts
  - and 18 more, in: tools/ 18
  - neckbeard did not read: tools/fixtures/read-status/persist-dangling/scripts/x.sh: could not be read; not scanned

### Reaches outside the session
- MCP servers: none

### Source
- Kind: plugin
- Name: neckbeard (from plugin.json)
- Version: 1.17.4 (from plugin.json)
- plugin.json:
  - name and version, shown above
- Marketplace: none
- Commit: 024f5aa

Load timing is how Claude Code loads skills, not measured here. Tokens are estimated as bytes / 4; where the inventory fell back to a character count, "bytes" counts characters.

No reader's rules were read: this report lists facts only and carries no verdict.
