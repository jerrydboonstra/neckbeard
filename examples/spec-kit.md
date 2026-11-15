# 🔍 spec-kit · what it adds

`2026-11-15` · neckbeard 1.17.1 · [github/spec-kit](https://github.com/github/spec-kit) @ `0019fa1`

## What it adds

### Injects
- Skills:
  - add-community-extension: description every session (323 chars); the file on demand (6704 bytes, ~1676 tokens)
  - code-review: description every session (303 chars); the file on demand (1777 bytes, ~444 tokens)
- Rule files: none
- Hook-injected text: partly read
  - neckbeard did not read: extensions/catalog.community.json: over 200000 bytes; not searched for hooks
  - broken in the plugin: .devcontainer/devcontainer.json: not valid JSON; not searched for hooks

### Hooks
- Hooks: partly read
  - reaches subagents: unknown
  - neckbeard did not read: extensions/catalog.community.json: over 200000 bytes; not searched for hooks
  - broken in the plugin: .devcontainer/devcontainer.json: not valid JSON; not searched for hooks

### Subagents and commands
- Agents: none
- Commands: none

### State it may leave
- Persistence candidates: partly read
  - .devcontainer/post-create.sh
  - .github/scripts/check_extension_version_bump.py
  - .github/scripts/check_security_requirements.py
  - .github/scripts/validate_community_preset.py
  - .github/scripts/validate_community_workflow_step.py
  - extensions/agent-context/scripts/bash/update-agent-context.sh
  - extensions/agent-context/scripts/python/update_agent_context.py
  - extensions/git/scripts/bash/auto-commit.sh
  - extensions/git/scripts/bash/create-new-feature-branch.sh
  - extensions/git/scripts/bash/git-common.sh
  - and 114 more, in: src/ 102, scripts/ 7, extensions/ 5
  - neckbeard did not read: src/specify_cli/agents.py: read capped at 50000 bytes; src/specify_cli/command_init.py: read capped at 50000 bytes; src/specify_cli/workflows/engine.py: read capped at 50000 bytes; src/specify_cli/workflows/_commands.py: read capped at 50000 bytes; src/specify_cli/extensions/__init__.py: read capped at 50000 bytes; and 4 more

### Reaches outside the session
- MCP servers: none

### Source
- Kind: generic-pack
- Name: spec-kit
- Version: no version
- plugin.json: not applicable
- Marketplace: not applicable
- Commit: 0019fa1

Load timing is how Claude Code loads skills, not measured here. Tokens are estimated as bytes / 4; where the inventory fell back to a character count, "bytes" counts characters.

No reader's rules were read: this report lists facts only and carries no verdict.
