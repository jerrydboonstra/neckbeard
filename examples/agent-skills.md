# 🔍 agent-skills 0.6.16 · what it adds

`2026-11-15` · neckbeard 1.17.1 · [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) 0.6.16 @ `39b723c`

## What it adds

### Injects
- Skills:
  - api-and-interface-design: description every session (251 chars); the file on demand (14938 bytes, ~3734 tokens)
  - browser-testing-with-devtools: description every session (326 chars); the file on demand (14640 bytes, ~3660 tokens)
  - ci-cd-and-automation: description every session (207 chars); the file on demand (11512 bytes, ~2878 tokens)
  - code-review-and-quality: description every session (374 chars); the file on demand (21312 bytes, ~5328 tokens)
  - code-simplification: description every session (418 chars); the file on demand (13719 bytes, ~3429 tokens)
  - constraint-driven-development: description every session (880 chars); the file on demand (22205 bytes, ~5551 tokens)
  - context-engineering: description every session (198 chars); the file on demand (15514 bytes, ~3878 tokens)
  - debugging-and-error-recovery: description every session (599 chars); the file on demand (11169 bytes, ~2792 tokens)
  - deprecation-and-migration: description every session (334 chars); the file on demand (12839 bytes, ~3209 tokens)
  - documentation-and-adrs: description every session (450 chars); the file on demand (12594 bytes, ~3148 tokens)
  - doubt-driven-development: description every session (487 chars); the file on demand (16753 bytes, ~4188 tokens)
  - frontend-ui-engineering: description every session (306 chars); the file on demand (12572 bytes, ~3143 tokens)
  - git-workflow-and-versioning: description every session (616 chars); the file on demand (14403 bytes, ~3600 tokens)
  - idea-refine: description every session (335 chars); the file on demand (9404 bytes, ~2351 tokens)
  - incremental-implementation: description every session (343 chars); the file on demand (9629 bytes, ~2407 tokens)
  - interview-me: description every session (485 chars); the file on demand (15080 bytes, ~3770 tokens)
  - observability-and-instrumentation: description every session (307 chars); the file on demand (13948 bytes, ~3487 tokens)
  - performance-optimization: description every session (295 chars); the file on demand (16783 bytes, ~4195 tokens)
  - planning-and-task-breakdown: description every session (237 chars); the file on demand (10677 bytes, ~2669 tokens)
  - security-and-hardening: description every session (600 chars); the file on demand (17592 bytes, ~4398 tokens)
  - shipping-and-launch: description every session (271 chars); the file on demand (11540 bytes, ~2885 tokens)
  - source-driven-development: description every session (308 chars); the file on demand (10104 bytes, ~2526 tokens)
  - spec-driven-development: description every session (578 chars); the file on demand (16893 bytes, ~4223 tokens)
  - test-driven-development: description every session (563 chars); the file on demand (16984 bytes, ~4246 tokens)
  - using-agent-skills: description every session (238 chars); the file on demand (10446 bytes, ~2611 tokens)
- Rule files:
  - CLAUDE.md: every session (4094 bytes, ~1023 tokens)
- Hook-injected text: partly read
  - neckbeard did not read: .opencode/skills: a symlinked folder, not followed

### Hooks
- Hooks: partly read
  - reaches subagents: unknown
  - neckbeard did not read: .opencode/skills: a symlinked folder, not followed

### Subagents and commands
- Agents:
  - code-reviewer
  - security-auditor
  - test-engineer
  - web-performance-auditor
- Commands:
  - build
  - code-simplify
  - constraints
  - planning
  - review
  - ship
  - spec
  - test
  - webperf

### State it may leave
- Persistence candidates: partly read
  - evals/fixtures/ci-cd-and-automation/src/slug.js
  - hooks/sdd-cache-post.sh
  - hooks/sdd-cache-pre.sh
  - hooks/sdd-cache-test.sh
  - hooks/session-start-test.sh
  - hooks/session-start.sh
  - hooks/simplify-ignore-test.sh
  - hooks/simplify-ignore.sh
  - scripts/floor-guard-reference-test.js
  - scripts/lib/skill-lint-test.js
  - and 12 more, in: scripts/ 12
  - neckbeard did not read: .opencode/skills: a symlinked folder, not followed; scripts/run-evals-test.js: read capped at 50000 bytes

### Reaches outside the session
- MCP servers: none

### Source
- Kind: plugin
- Name: agent-skills (from plugin.json)
- Version: 0.6.16 (from plugin.json)
- plugin.json:
  - name and version, shown above
- Marketplace: partly read
  - broken in the plugin: .claude-plugin/marketplace.json: plugin 'agent-skills' has no source string, so it was not looked for
- Commit: 39b723c

Load timing is how Claude Code loads skills, not measured here. Tokens are estimated as bytes / 4; where the inventory fell back to a character count, "bytes" counts characters.

No reader's rules were read: this report lists facts only and carries no verdict.
