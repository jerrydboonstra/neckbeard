# 🔍 superpowers 7.0.2 · what it adds

`2026-11-15` · neckbeard 1.17.1 · [obra/superpowers](https://github.com/obra/superpowers) 7.0.2 @ `22f0b46`

## What it adds

### Injects
- Skills:
  - brainstorming: description every session (213 chars); the file on demand (15190 bytes, ~3797 tokens)
  - diagnosing-superpowers: description every session (375 chars); the file on demand (6941 bytes, ~1735 tokens)
  - dispatching-parallel-agents: description every session (106 chars); the file on demand (6078 bytes, ~1519 tokens)
  - executing-plans: description every session (170 chars); the file on demand (18364 bytes, ~4591 tokens)
  - finishing-a-development-branch: description every session (101 chars); the file on demand (7781 bytes, ~1945 tokens)
  - receiving-code-review: description every session (234 chars); the file on demand (6203 bytes, ~1550 tokens)
  - requesting-code-review: description every session (107 chars); the file on demand (2974 bytes, ~743 tokens)
  - subagent-driven-development: description every session (85 chars); the file on demand (19740 bytes, ~4935 tokens)
  - systematic-debugging: description every session (91 chars); the file on demand (9530 bytes, ~2382 tokens)
  - test-driven-development: description every session (79 chars); the file on demand (9578 bytes, ~2394 tokens)
  - using-git-worktrees: description every session (196 chars); the file on demand (6813 bytes, ~1703 tokens)
  - using-superpowers: description every session (154 chars); the file on demand (3192 bytes, ~798 tokens)
  - verification-before-completion: description every session (225 chars); the file on demand (3646 bytes, ~911 tokens)
  - writing-plans: description every session (84 chars); the file on demand (10335 bytes, ~2583 tokens)
  - writing-skills: description every session (97 chars); the file on demand (16738 bytes, ~4184 tokens)
- Rule files: none
- Hook-injected text: partly read
  - neckbeard did not read: hooks/hooks.json: unresolved hooks: SessionStart: hooks/run-hook.cmd; hooks/hooks.json: 1 hook(s) have unknown behaviour, which is not the same as none: 1 whose script was found but whose payload could not be traced. Read them by hand.

### Hooks
- Hooks: partly read
  - SessionStart (startup|clear|compact): hooks/run-hook.cmd
  - reaches subagents: false (no event known to fire in a subagent)
  - neckbeard did not read: hooks/hooks.json: unresolved hooks: SessionStart: hooks/run-hook.cmd; hooks/hooks.json: 1 hook(s) have unknown behaviour, which is not the same as none: 1 whose script was found but whose payload could not be traced. Read them by hand.

### Subagents and commands
- Agents: none
- Commands: none

### State it may leave
- Persistence candidates:
  - .opencode/plugins/superpowers.js
  - hooks/session-start
  - scripts/bump-version.sh
  - scripts/lint-shell.sh
  - scripts/package-codex-plugin.sh
  - scripts/render-antigravity-logo.sh
  - scripts/sync-to-codex-plugin.sh
  - skills/brainstorming/scripts/helper.js
  - skills/brainstorming/scripts/server.cjs
  - skills/brainstorming/scripts/start-server.sh
  - and 8 more, in: skills/ 8

### Reaches outside the session
- MCP servers: none

### Source
- Kind: plugin
- Name: superpowers (from plugin.json)
- Version: 7.0.2 (from plugin.json)
- plugin.json:
  - name and version, shown above
- Marketplace: none
- Commit: 22f0b46

Load timing is how Claude Code loads skills, not measured here. Tokens are estimated as bytes / 4; where the inventory fell back to a character count, "bytes" counts characters.

No reader's rules were read: this report lists facts only and carries no verdict.
