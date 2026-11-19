# 🔍 spec-kit · how it affects you, what it adds, where it takes a position

`2026-11-18` · neckbeard 1.17.8 · [github/spec-kit](https://github.com/github/spec-kit) @ `0019fa14`

**Contents**

1. [How it affects you](#how-it-affects-you): cost, reach, state and live surface at a glance. Carries a judgement: the colours.
2. [What it adds](#what-it-adds): what the plugin loads, injects and may leave on disk, written by code. No judgement.
3. [Where it takes a position](#where-it-takes-a-position): every place it tells the model what to do, by topic, in its own words. No judgement.

---

**1 · Summary · carries a judgement**

## How it affects you

| | Row | In short |
|---|---|---|
| 🟨 | Cost | adds 626 to every session, ~157 tokens (626 skill descriptions, 0 agent descriptions, 0 rule files, 0 hook text) (not read in full) |
| 🟨 | Reach | on demand only (not read in full) |
| 🟧 | Leaves state | 124 files that may write state |
| 🟨 | Live surface | no hook commands, MCP servers or mods found (not read in full) |
| 🟨 | Read completeness | partly read |

<details><summary><b>At a glance in full</b></summary>

- **Cost** 🟨: adds 626 to every session, ~157 tokens (626 skill descriptions, 0 agent descriptions, 0 rule files, 0 hook text) (not read in full)
  - skill .github/skills/code-review/SKILL.md: 303 of description
  - skill .github/skills/add-community-extension/SKILL.md: 323 of description
- **Reach** 🟨: on demand only (not read in full)
- **Leaves state** 🟧: 124 files that may write state
  - may write state: .devcontainer/post-create.sh
  - may write state: .github/scripts/check_extension_version_bump.py
  - may write state: .github/scripts/check_security_requirements.py
  - may write state: .github/scripts/validate_community_preset.py
  - may write state: .github/scripts/validate_community_workflow_step.py
  - may write state: extensions/agent-context/scripts/bash/update-agent-context.sh
  - may write state: extensions/agent-context/scripts/python/update_agent_context.py
  - may write state: extensions/git/scripts/bash/auto-commit.sh
  - may write state: extensions/git/scripts/bash/create-new-feature-branch.sh
  - may write state: extensions/git/scripts/bash/git-common.sh
  - and 114 more
- **Live surface** 🟨: no hook commands, MCP servers or mods found (not read in full)
- **Read completeness** 🟨: partly read
  - agents: read
  - commands: read
  - hooks: partial
  - marketplace: not-applicable
  - mcp_servers: read
  - persistence_candidates: read
  - plugin_json: not-applicable
  - rule_files: read
  - skills: read

</details>

The colours follow written rules. Each is checked top to bottom, and the first match wins. A row whose input was not read in full is never 🟩.

- Cost: 🟩 under 2,000; 🟨 2,000 to 7,999; 🟧 8,000 to 31,999; 🟥 32,000 and over. Size counts skill and agent descriptions, rule files and hook-injected text, in the dossier's unit (bytes, or characters where the inventory fell back); text a hook builds at run time counts as at least its known size. Hook text counts twice when hooks reach subagents. An entry that was refused or has no usable size counts as 0.
- Reach: 🟥 a hook and hooks reach subagents; 🟨 a hook, a Claude Code mod or a rule file (every main session); 🟩 neither (on demand only).
- Leaves state: 🟧 one or more files that may write state; 🟨 nothing found but the scan was partial or failed; 🟩 nothing found by a full scan.
- Live surface: 🟥 a hook or MCP command runs ssh, mosh, telnet, rsh, rlogin (each a remote shell); 🟧 any MCP server, any Claude Code mod, a hook running curl, wget, nc or holding an http:// or https:// URL, or a hook command too long to read; 🟨 any hook command; 🟩 none. A command word is the first word of each piece, cut at newlines and at | && || ; & outside quotes, after NAME=value words, by basename; an MCP server's command is compared by its first word and each of its args whole, by basename. The scan does not search inline code (bash -c, node -e), hook script bodies, or commands behind a wrapper (sudo, timeout, command, nohup, exec, xargs, ( ), { }, !, $( ) or backticks).
- Read completeness: 🟩 read in full; 🟨 partly read; 🟥 something unread.

---

**2 · Facts · written by code · no judgement**

## What it adds

🟢 read in full · 🟡 partly read · 🔴 something unread

<details><summary>🟡 <b>Injects</b> · 2 skills · ~2120 tokens on demand · ~626 chars of skill descriptions every session · hook text partly read</summary>

- Skills:
  - add-community-extension: description every session (323 chars); the file on demand (6704 bytes, ~1676 tokens)
  - code-review: description every session (303 chars); the file on demand (1777 bytes, ~444 tokens)
- Rule files: none
- Hook-injected text: partly read
  - neckbeard did not read: extensions/catalog.community.json: over 200000 bytes; not searched for hooks
  - broken in the plugin: .devcontainer/devcontainer.json: not valid JSON; not searched for hooks

</details>

<details><summary>🟡 <b>Hooks</b> · partly read</summary>

- Hooks: partly read
  - reaches subagents: unknown
  - neckbeard did not read: extensions/catalog.community.json: over 200000 bytes; not searched for hooks
  - broken in the plugin: .devcontainer/devcontainer.json: not valid JSON; not searched for hooks

</details>

<details><summary>🟢 <b>Subagents and commands</b> · no agents · 0 commands</summary>

- Agents: none
- Commands: none

</details>

<details><summary>🟢 <b>State it may leave</b> · 124 files that may write state · 10 named</summary>

- Persistence candidates:
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

</details>

<details><summary>🟢 <b>Reaches outside the session</b> · no MCP servers</summary>

- MCP servers: none

</details>

<details><summary>🟢 <b>Source</b> · generic-pack · spec-kit · commit 0019fa1 · no marketplace</summary>

- Kind: generic-pack
- Name: spec-kit
- Version: no version
- plugin.json: not applicable
- Marketplace: not applicable
- Commit: 0019fa14

</details>

Load timing is how Claude Code loads skills, not measured here. Tokens are estimated as bytes / 4; where the inventory fell back to a character count, "bytes" counts characters.

---

**3 · Positions · the plugin's own words · no judgement**

## Where it takes a position

> Read from the plugin's instruction files (skills, commands, agents, rule files) and from the template text of hooks that build their output at run time. Text a hook injects from elsewhere, or builds in code, is not quoted. Topics come from a fixed list, grouped by code, with no judgement.

<details><summary><b>Persona and activation</b> · 1 · "**Don't forget the catalog `updated_at`** — the top-level t…"</summary>

- "**Don't forget the catalog \`updated_at\`** — the top-level timestamp in \`catalog.community.json\` must be refreshed." [`.github/skills/add-community-extension/SKILL.md:169`](https://github.com/github/spec-kit/blob/0019fa14/.github/skills/add-community-extension/SKILL.md#L169)

</details>

<details><summary><b>Scope and size of changes</b> · 2 · "Ensure wording changes use repository-consistent terms; exc…"</summary>

- "Ensure wording changes use repository-consistent terms; exclude community-authored catalog content and its generated documentation from this check." [`.github/skills/code-review/SKILL.md:11`](https://github.com/github/spec-kit/blob/0019fa14/.github/skills/code-review/SKILL.md#L11)
- "Check the changes against the applicable design requirements, including implementation boundaries, ownership, lifecycle, and delivery requirements. Reference the documents rather than duplicating the…" [`.github/skills/code-review/SKILL.md:13`](https://github.com/github/spec-kit/blob/0019fa14/.github/skills/code-review/SKILL.md#L13)

</details>

<details><summary><b>Tests</b> · 1 · "Ensure each code change has test cases that verify what the…"</summary>

- "Ensure each code change has test cases that verify what the code should do and what it should prevent." [`.github/skills/code-review/SKILL.md:9`](https://github.com/github/spec-kit/blob/0019fa14/.github/skills/code-review/SKILL.md#L9)

</details>

<details><summary><b>Code style and comments</b> · 2 · "Use the existing entries as the format template."</summary>

- "Use the existing entries as the format template." [`.github/skills/add-community-extension/SKILL.md:57`](https://github.com/github/spec-kit/blob/0019fa14/.github/skills/add-community-extension/SKILL.md#L57)
- "**Category** — free-form; common values: \`docs\`, \`code\`, \`process\`, \`integration\`, \`visibility\` **Effect** — write canonical values \`read-only\` or \`read-write\` in \`extension.yml\` and \`catalog.communi…" [`.github/skills/add-community-extension/SKILL.md:121`](https://github.com/github/spec-kit/blob/0019fa14/.github/skills/add-community-extension/SKILL.md#L121)

</details>

<details><summary><b>Dependencies</b> · 1 · "If the extension has optional tool dependencies, add a `"to…"</summary>

- "If the extension has optional tool dependencies, add a \`"tools"\` array inside \`"requires"\`:" [`.github/skills/add-community-extension/SKILL.md:95`](https://github.com/github/spec-kit/blob/0019fa14/.github/skills/add-community-extension/SKILL.md#L95)

</details>

<details><summary><b>Pushes and releases</b> · 1 · "GitHub release exists matching version | Check releases on …"</summary>

- "GitHub release exists matching version | Check releases on the repo page" [`.github/skills/add-community-extension/SKILL.md:38`](https://github.com/github/spec-kit/blob/0019fa14/.github/skills/add-community-extension/SKILL.md#L38)

</details>

<details><summary><b>Reviews and audits</b> · 1 · "Ensure bug-fix pull requests include a regression test that…"</summary>

- "Ensure bug-fix pull requests include a regression test that demonstrates the bug was reproducible before the change and is fixed afterward; if the reviewer cannot run the comparison, use available ev…" [`.github/skills/code-review/SKILL.md:10`](https://github.com/github/spec-kit/blob/0019fa14/.github/skills/code-review/SKILL.md#L10)

</details>

<details><summary><b>Models and subagents</b> · 1 · "Identify the affected domains and read the applicable docum…"</summary>

- "Identify the affected domains and read the applicable documents in \`design/\` before evaluating architectural consistency. For CLI command changes, use \`design/cli.md\`; for agent integrations, use \`de…" [`.github/skills/code-review/SKILL.md:12`](https://github.com/github/spec-kit/blob/0019fa14/.github/skills/code-review/SKILL.md#L12)

</details>

<details><summary><b>State and files</b> · 1 · "**Match the proposed entry but verify** — the issue may inc…"</summary>

- "**Match the proposed entry but verify** — the issue may include a proposed JSON block, but always validate field values against the actual repository state." [`.github/skills/add-community-extension/SKILL.md:172`](https://github.com/github/spec-kit/blob/0019fa14/.github/skills/add-community-extension/SKILL.md#L172)

</details>

<details><summary><b>Network</b> · 8 · "Process an extension submission issue and add or update it …"</summary>

- "Process an extension submission issue and add or update it in the community catalog." [`.github/skills/add-community-extension/SKILL.md:9`](https://github.com/github/spec-kit/blob/0019fa14/.github/skills/add-community-extension/SKILL.md#L9)
- "You need to add or update a community extension in \`extensions/catalog.community.json\` and \`docs/community/extensions.md\`" [`.github/skills/add-community-extension/SKILL.md:15`](https://github.com/github/spec-kit/blob/0019fa14/.github/skills/add-community-extension/SKILL.md#L15)
- "Update only the fields that changed (typically \`version\`, \`download_url\`, \`description\`, \`provides\`, \`requires\`, \`tags\`, \`updated_at\`)." [`.github/skills/add-community-extension/SKILL.md:55`](https://github.com/github/spec-kit/blob/0019fa14/.github/skills/add-community-extension/SKILL.md#L55)
- "**Update:** Find the existing row and update the description or other changed fields in-place." [`.github/skills/add-community-extension/SKILL.md:113`](https://github.com/github/spec-kit/blob/0019fa14/.github/skills/add-community-extension/SKILL.md#L113)
- "Use \`add-\` for new extensions, \`update-\` for updates:" [`.github/skills/add-community-extension/SKILL.md:126`](https://github.com/github/spec-kit/blob/0019fa14/.github/skills/add-community-extension/SKILL.md#L126)
- "**Title:** \`Add &lt;Name> extension to community catalog\` (or \`Update &lt;Name> extension to v&lt;version>\`)" [`.github/skills/add-community-extension/SKILL.md:161`](https://github.com/github/spec-kit/blob/0019fa14/.github/skills/add-community-extension/SKILL.md#L161)
- "**Preserve \`created_at\` on updates** — keep the original \`created_at\` value; only change \`updated_at\`." [`.github/skills/add-community-extension/SKILL.md:173`](https://github.com/github/spec-kit/blob/0019fa14/.github/skills/add-community-extension/SKILL.md#L173)
- "**Preserve \`downloads\` and \`stars\` on updates** — these reflect usage metrics and must not be reset." [`.github/skills/add-community-extension/SKILL.md:174`](https://github.com/github/spec-kit/blob/0019fa14/.github/skills/add-community-extension/SKILL.md#L174)

</details>

<details><summary><b>other</b> · 7 · "Read the GitHub issue to extract all metadata:"</summary>

- "Read the GitHub issue to extract all metadata:" [`.github/skills/add-community-extension/SKILL.md:21`](https://github.com/github/spec-kit/blob/0019fa14/.github/skills/add-community-extension/SKILL.md#L21)
- "Extension ID, name, version, description, author" [`.github/skills/add-community-extension/SKILL.md:22`](https://github.com/github/spec-kit/blob/0019fa14/.github/skills/add-community-extension/SKILL.md#L22)
- "Check **all** of the following (per \`docs/extensions/publishing.md\`):" [`.github/skills/add-community-extension/SKILL.md:30`](https://github.com/github/spec-kit/blob/0019fa14/.github/skills/add-community-extension/SKILL.md#L30)
- "Extension ID is lowercase-with-hyphens only | Regex: \`^\[a-z\]\[a-z0-9-\]*$\`" [`.github/skills/add-community-extension/SKILL.md:40`](https://github.com/github/spec-kit/blob/0019fa14/.github/skills/add-community-extension/SKILL.md#L40)
- "**New extension:** Insert a new row into the \`# Community Extensions\` table in **alphabetical order** by extension name." [`.github/skills/add-community-extension/SKILL.md:111`](https://github.com/github/spec-kit/blob/0019fa14/.github/skills/add-community-extension/SKILL.md#L111)
- "**Alphabetical order matters** — entries must be sorted by ID in the JSON and by name in the docs table." [`.github/skills/add-community-extension/SKILL.md:168`](https://github.com/github/spec-kit/blob/0019fa14/.github/skills/add-community-extension/SKILL.md#L168)
- "**Use \`Closes\` not \`Fixes\`** — \`Closes #N\` is the correct keyword for submission issues." [`.github/skills/add-community-extension/SKILL.md:171`](https://github.com/github/spec-kit/blob/0019fa14/.github/skills/add-community-extension/SKILL.md#L171)

</details>

No reader's rules were read: this report lists facts only and carries no verdict.
