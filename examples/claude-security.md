# 🔍 claude-plugins-official 0.12.0 · what it adds

`2026-11-15` · neckbeard 1.17.1 · [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) 0.12.0 @ `b5b01ac`

## What it adds

### Injects
- Skills:
  - claude-security: description every session (446 chars); the file on demand (5569 bytes, ~1392 tokens)
- Rule files: none
- Hook-injected text: partly read
  - neckbeard did not read: hooks/hooks.json: unresolved hooks: PermissionRequest: hooks/hooks.sh; PostToolUse: hooks/hooks.sh; PostToolUseFailure: hooks/hooks.sh; UserPromptExpansion: hooks/hooks.sh; hooks/hooks.json: 4 hook(s) have unknown behaviour, which is not the same as none: 4 whose script was found but whose payload could not be traced. Read them by hand.

### Hooks
- Hooks: partly read
  - PermissionRequest (AskUserQuestion): hooks/hooks.sh
  - PostToolUse (Bash): hooks/hooks.sh
  - PostToolUse (Bash): hooks/hooks.sh
  - PostToolUse (Bash): hooks/hooks.sh
  - PostToolUseFailure (Bash): hooks/hooks.sh
  - UserPromptExpansion (^claude-security:claude-security$): hooks/hooks.sh
  - reaches subagents: true (documented: a Subagent* event, or PreToolUse/PostToolUse which the docs say fire inside subagents)
  - neckbeard did not read: hooks/hooks.json: unresolved hooks: PermissionRequest: hooks/hooks.sh; PostToolUse: hooks/hooks.sh; PostToolUseFailure: hooks/hooks.sh; UserPromptExpansion: hooks/hooks.sh; hooks/hooks.json: 4 hook(s) have unknown behaviour, which is not the same as none: 4 whose script was found but whose payload could not be traced. Read them by hand.

### Subagents and commands
- Agents:
  - claude-security
  - explore
  - patch-generator
  - patch-verifier
  - scan-inventory
  - scan-loader
  - scan-redactor
  - scan-researcher
  - scan-verifier
- Commands: none

### State it may leave
- Persistence candidates: partly read
  - hooks/hooks.py
  - hooks/hooks.sh
  - scripts/lib/absolute.py
  - scripts/lib/finding.py
  - scripts/patch_artifacts.py
  - scripts/render_report.py
  - scripts/save_result.py
  - scripts/write_scan_meta.py
  - workflows/scan.js
  - neckbeard did not read: workflows/scan.js: read capped at 50000 bytes; scripts/patch_artifacts.py: read capped at 50000 bytes

### Reaches outside the session
- MCP servers: none

### Source
- Kind: plugin
- Name: claude-security (from plugin.json)
- Version: 0.12.0 (from plugin.json)
- plugin.json:
  - name and version, shown above
- Marketplace: not applicable
- Commit: b5b01ac

Load timing is how Claude Code loads skills, not measured here. Tokens are estimated as bytes / 4; where the inventory fell back to a character count, "bytes" counts characters.

No reader's rules were read: this report lists facts only and carries no verdict.
