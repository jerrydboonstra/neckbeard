# 🔍 ponytail

`2026-11-18` · [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) 5.3.3 @ `7801d06` · made by neckbeard 2.0.0

**Contents**

1. [How it affects you](#how-it-affects-you): cost, reach, state and live surface at a glance. Carries a judgement: the colours.
2. [What it adds](#what-it-adds): what the plugin loads, injects and may leave on disk, written by code. No judgement.
3. [Where it takes a position](#where-it-takes-a-position): every place it tells the model what to do, by topic, in its own words. No judgement.

---

**1 · Summary · carries a judgement**

## How it affects you

| | Row | In short |
|---|---|---|
| 🟥 | Cost | adds 47,610 characters to every session, ~11,903 tokens (1,584 skill descriptions, 0 agent descriptions, 0 rule files, 23,013 hook text, counted twice because hooks reach subagents) (not read in full) |
| 🟥 | Reach | a hook runs in every session and in every subagent too (not read in full) |
| 🟧 | Leaves state | 18 files that may write state |
| 🟧 | Live surface | 1 Claude Code mod (not read in full) |
| 🟨 | Read completeness | partly read |

- **Leaves state**: the files are listed in the "State it may leave" card under [What it adds](#what-it-adds).
- **Read completeness**: not read in full: hooks (partial).

<details><summary><b>How the colours are set</b></summary>

The colours follow written rules. Each is checked top to bottom, and the first match wins. A row whose input was not read in full is never 🟩.

- Cost: 🟩 under 2,000; 🟨 2,000 to 7,999; 🟧 8,000 to 31,999; 🟥 32,000 and over. Size counts skill and agent descriptions, rule files and hook-injected text, in the dossier's unit (bytes, or characters where the inventory fell back); text a hook builds at run time counts as at least its known size. Hook text counts twice when hooks reach subagents. An entry that was refused or has no usable size counts as 0.
- Reach: 🟥 a hook and hooks reach subagents; 🟨 a hook, a Claude Code mod or a rule file (every main session); 🟩 neither (on demand only).
- Leaves state: 🟧 one or more files that may write state; 🟨 nothing found but the scan was partial or failed; 🟩 nothing found by a full scan.
- Live surface: 🟥 a hook or MCP command runs ssh, mosh, telnet, rsh, rlogin (each a remote shell); 🟧 any MCP server, any Claude Code mod, a hook running curl, wget, nc or holding an http:// or https:// URL, or a hook command too long to read; 🟨 any hook command; 🟩 none. A command word is the first word of each piece, cut at newlines and at | && || ; & outside quotes, after NAME=value words, by basename; an MCP server's command is compared by its first word and each of its args whole, by basename. The scan does not search inline code (bash -c, node -e), hook script bodies, or commands behind a wrapper (sudo, timeout, command, nohup, exec, xargs, ( ), { }, !, $( ) or backticks).
- Read completeness: 🟩 read in full; 🟨 partly read; 🟥 something unread.

</details>

---

**2 · Facts · written by code · no judgement**

## What it adds

🟢 read in full · 🟡 partly read · 🔴 something unread

<details><summary>🟡 <b>Injects</b> · 6 skills · ~5293 tokens on demand · ~1584 chars of skill descriptions every session · hook text partly read</summary>

- Skills:
  - ponytail-audit: description every session (346 chars); the file on demand (5417 bytes, ~1354 tokens)
  - ponytail-debt: description every session (201 chars); the file on demand (1769 bytes, ~442 tokens)
  - ponytail-gain: description every session (160 chars); the file on demand (2164 bytes, ~541 tokens)
  - ponytail-help: description every session (141 chars); the file on demand (3188 bytes, ~797 tokens)
  - ponytail-review: description every session (370 chars); the file on demand (5143 bytes, ~1285 tokens)
  - ponytail: description every session (366 chars); the file on demand (3496 bytes, ~874 tokens)
- Rule files: none
- Hook-injected text: partly read
  - hooks/ponytail-band-import.js: 14078 bytes, ~3519 tokens
  - hooks/ponytail-map.js: 5439 bytes, ~1359 tokens
  - skills/ponytail/SKILL.md: 3496 bytes, ~874 tokens
  - neckbeard did not read: hooks/band/register.tsx: a Claude Code mod; it runs in the session with no sandbox, and its source is not read

</details>

<details><summary>🟡 <b>Hooks</b> · 3 hooks · reach subagents · partly read</summary>

- Hooks: partly read
  - SessionStart (startup|resume|clear|compact): hooks/ponytail-activate.js
  - SubagentStart: hooks/ponytail-subagent.js
  - UserPromptSubmit: hooks/ponytail-mode-tracker.js
  - reaches subagents: true (documented: a Subagent* event, or PreToolUse/PostToolUse which the docs say fire inside subagents)
  - neckbeard did not read: hooks/band/register.tsx: a Claude Code mod; it runs in the session with no sandbox, and its source is not read

</details>

<details><summary>🟡 <b>Claude Code mods</b> · 1 mod</summary>

- Mods: partly read
  - hooks/band/register.tsx
  - a mod is code that runs inside the session with your permissions and no sandbox; neckbeard lists the files a plugin names and does not read their source
  - neckbeard did not read: hooks/band/register.tsx: a Claude Code mod; it runs in the session with no sandbox, and its source is not read

</details>

<details><summary>🟢 <b>Subagents and commands</b> · no agents · 6 commands</summary>

- Agents: none
- Commands:
  - ponytail
  - ponytail-audit
  - ponytail-debt
  - ponytail-gain
  - ponytail-help
  - ponytail-review

</details>

<details><summary>🟢 <b>State it may leave</b> · 18 files that may write state · 10 named</summary>

- Persistence candidates:
  - .opencode/plugins/ponytail-frontmatter.cjs
  - .opencode/plugins/ponytail.mjs
  - __init__.py
  - hooks/band/board.ts
  - hooks/band/metrics.ts
  - hooks/ponytail-activate.js
  - hooks/ponytail-band-import.js
  - hooks/ponytail-config.js
  - hooks/ponytail-instructions.js
  - hooks/ponytail-map.js
  - and 8 more, in: scripts/ 5, hooks/ 3

</details>

<details><summary>🟢 <b>Reaches outside the session</b> · no MCP servers</summary>

- MCP servers: none

</details>

<details><summary>🟢 <b>Source</b> · plugin · ponytail 5.3.3 from plugin.json · commit 7801d06 · no marketplace</summary>

- Kind: plugin
- Name: ponytail (from plugin.json)
- Version: 5.3.3 (from plugin.json)
- plugin.json:
  - name and version, shown above
- Marketplace: none
- Commit: 7801d06

</details>

Load timing is how Claude Code loads skills, not measured here. Tokens are estimated as bytes / 4; where the inventory fell back to a character count, "bytes" counts characters.

---

**3 · Positions · the plugin's own words · no judgement**

## Where it takes a position

> Read from the plugin's instruction files (skills, commands, agents, rule files) and from the template text of hooks that build their output at run time. Text a hook injects from elsewhere, or builds in code, is not quoted. Topics come from a fixed list, grouped by code, with no judgement.

<details><summary><b>Persona and activation</b> · 7 · "Levels: /ponytail lite (build what's asked, name the lazier…"</summary>

- "Levels: /ponytail lite (build what's asked, name the lazier alternative in one line), /ponytail (full, the default ladder: YAGNI then stdlib then native then one line then minimum), /ponytail ultra (…" [`commands/ponytail-help.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-help.toml#L2)
- "Deactivate with 'stop ponytail', 'normal mode', or /ponytail off; resume anytime with /ponytail." [`commands/ponytail-help.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-help.toml#L2)
- "With no level, keep the current level, or switch on at the default level if ponytail was off." [`commands/ponytail.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail.toml#L2)
- "Lazy senior dev mode, before any code: does it need to exist at all (YAGNI)?" [`commands/ponytail.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail.toml#L2)
- "Edits nothing, changes no mode." [`skills/ponytail-gain/SKILL.md:52`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-gain/SKILL.md#L52)
- "Set \`"off"\` to disable auto-activation on session start, activate manually with \`/ponytail\` when wanted." [`skills/ponytail-help/SKILL.md:63`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-help/SKILL.md#L63)
- "Active for the whole session until the user says "stop ponytail" or "normal mode"." [`skills/ponytail/SKILL.md:17`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail/SKILL.md#L17)

</details>

<details><summary><b>Asking vs proceeding</b> · 4 · "No style taste, no vague worries."</summary>

- "No style taste, no vague worries." [`commands/ponytail-review.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-review.toml#L2)
- "No style taste, no "consider", no vague worries." [`skills/ponytail-audit/SKILL.md:67`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L67) (also in `skills/ponytail-review/SKILL.md:67`)
- "Does it need to exist? Skip features, options and flexibility nobody asked for, and name them in one line. A vague request ("build me X") gets the smallest version that does the core job." [`skills/ponytail/SKILL.md:27`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail/SKILL.md#L27)
- "**lite** | Build what was asked. Name the smaller option in one line and let the user pick." [`skills/ponytail/SKILL.md:50`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail/SKILL.md#L50)

</details>

<details><summary><b>Scope and size of changes</b> · 13 · "Change no code."</summary>

- "Change no code." [`commands/ponytail-audit.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-audit.toml#L2)
- "Ship.' Change no code." [`commands/ponytail-review.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-review.toml#L2)
- "Start with 'What this change does:' in two or three sentences and the load you assumed." [`commands/ponytail-review.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-review.toml#L2)
- "merge: near-copies that must change together" [`skills/ponytail-audit/SKILL.md:52`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L52) (also in `skills/ponytail-review/SKILL.md:52`)
- "A change can break code it does not touch. When a signature, return value or behavior changes, grep every caller." [`skills/ponytail-review/SKILL.md:24`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-review/SKILL.md#L24)
- "Start with \`What this change does:\` in two or three sentences." [`skills/ponytail-review/SKILL.md:74`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-review/SKILL.md#L74)
- "Check what your change could break for users: data it would destroy or expose, callers that stop working." [`skills/ponytail/SKILL.md:21`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail/SKILL.md#L21)
- "Read the task and the code it touches." [`skills/ponytail/SKILL.md:21`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail/SKILL.md#L21)
- "Take the first option that fully works:" [`skills/ponytail/SKILL.md:25`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail/SKILL.md#L25)
- "Already in this codebase (a helper, component, service, pattern)? Use it the way the surrounding code does." [`skills/ponytail/SKILL.md:28`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail/SKILL.md#L28)
- "Standard library or a platform feature? Use it, unless the project has its own. A house component beats a native widget." [`skills/ponytail/SKILL.md:29`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail/SKILL.md#L29)
- "Between options of equal size, take the one that is correct on edge cases." [`skills/ponytail/SKILL.md:40`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail/SKILL.md#L40)
- "Never cut: validation at trust boundaries, error handling that prevents data loss, security, accessibility, the calibration real hardware needs, anything the user asked for." [`skills/ponytail/SKILL.md:44`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail/SKILL.md#L44)

</details>

<details><summary><b>Tests</b> · 11 · "Before calling code unused, grep the whole tree including t…"</summary>

- "Before calling code unused, grep the whole tree including tests, fixtures, config and string references." [`commands/ponytail-audit.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-audit.toml#L2)
- "Look for, in this order: bugs, risk (security holes, data loss), scale (races, the same work done by every process, memory that only grows, a query per item, O(n^2)), risky logic without a test, slow…" [`commands/ponytail-audit.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-audit.toml#L2)
- "First read the code the change touches: callers of every changed function, the functions it calls, the tests, the README (find the expected load: one person or many users and processes)." [`commands/ponytail-review.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-review.toml#L2)
- "**Missing test:** risky logic (a branch, a parser, money, security, data writes) with no test that fails when it breaks. One good test, not coverage." [`skills/ponytail-audit/SKILL.md:41`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L41)
- "split: one function or class doing several unrelated jobs, so it is hard to read or test. Split by job, never by line count, and never into helpers that exist only to make a function shorter." [`skills/ponytail-audit/SKILL.md:53`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L53)
- "Before calling code unused, grep the whole tree for it, including tests, fixtures, config, and string or dynamic references." [`skills/ponytail-audit/SKILL.md:61`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L61)
- "**Missing test:** risky new logic (a branch, a parser, money, security, data writes, a bug fix) with no test that fails when it breaks. One good test, not coverage." [`skills/ponytail-review/SKILL.md:41`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-review/SKILL.md#L41)
- "split: one function doing several unrelated jobs, so it is hard to read or test. Split by job, never by line count, and never into helpers that exist only to make a function shorter." [`skills/ponytail-review/SKILL.md:53`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-review/SKILL.md#L53)
- "List every place your change must reach: callers, tests, fixtures, config, exports." [`skills/ponytail/SKILL.md:21`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail/SKILL.md#L21)
- "Be lazy about the solution, never about the change itself: finish every part the task needs, including the callers, tests and fixtures your change breaks." [`skills/ponytail/SKILL.md:34`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail/SKILL.md#L34)
- "Lazy code without its check is unfinished: new non-trivial logic (a branch, a loop, a parser, money or security, or a whole new script or app) leaves one small test or an assert-based self-check. Tri…" [`skills/ponytail/SKILL.md:41`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail/SKILL.md#L41)

</details>

<details><summary><b>Code style and comments</b> · 8 · "Lean still matters: every extra line must be read, tested a…"</summary>

- "Lean still matters: every extra line must be read, tested and fixed later." [`skills/ponytail-audit/SKILL.md:13`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L13) (also in `skills/ponytail-review/SKILL.md:13`)
- "**Lite** | \`/ponytail lite\` | Build what was asked, name the smaller option in one line." [`skills/ponytail-help/SKILL.md:17`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-help/SKILL.md#L17)
- "\`Not checked:\` one line, if something mattered and you could not check it." [`skills/ponytail-review/SKILL.md:96`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-review/SKILL.md#L96)
- "No abstraction, wrapper, type conversion, option, config, boilerplate or "for later" code nobody asked for. Keep values in the form the platform already gives you. Deletion beats addition. Keep the s…" [`skills/ponytail/SKILL.md:35`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail/SKILL.md#L35)
- "The shortest working diff wins, once you know everything it must touch. A one-liner that needs decoding is not short." [`skills/ponytail/SKILL.md:36`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail/SKILL.md#L36)
- "Comment only the why the code cannot show, in one line." [`skills/ponytail/SKILL.md:37`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail/SKILL.md#L37)
- "Bug fix: before you edit, grep every caller of the function you touch, then fix the root cause once in the shared code." [`skills/ponytail/SKILL.md:38`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail/SKILL.md#L38)
- "A shortcut with a known limit gets a code comment in this form: \`shortcut: &lt;the limit>, &lt;when to upgrade>\`." [`skills/ponytail/SKILL.md:42`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail/SKILL.md#L42)

</details>

<details><summary><b>Dependencies</b> · 2 · "No unrequested abstractions, no avoidable dependencies, no …"</summary>

- "No unrequested abstractions, no avoidable dependencies, no boilerplate." [`commands/ponytail.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail.toml#L2)
- "An installed dependency? Use it. Never add a dependency for a few lines." [`skills/ponytail/SKILL.md:30`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail/SKILL.md#L30)

</details>

<details><summary><b>Commits and git</b> · 6 · "Grep the whole tree for comment markers (git grep --no-inde…"</summary>

- "Grep the whole tree for comment markers (git grep --no-index --exclude-standard -nE '(#|//|/\[*\]) ?(shortcut|ponytail):', skipping .git and everything .gitignore ignores; if the user names their own m…" [`commands/ponytail-debt.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-debt.toml#L2)
- "Review what the user names (uncommitted or staged changes, a branch, a PR link, files); nothing named: the uncommitted changes, or the last commit if there are none." [`commands/ponytail-review.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-review.toml#L2)
- "Grep the repo for comment markers, skipping \`.git\` and everything the \`.gitignore\` files ignore (dependencies, build output, caches, in any stack):" [`skills/ponytail-debt/SKILL.md:15`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-debt/SKILL.md#L15)
- "\`git grep --no-index --exclude-standard -nE '(#|//|/\[*\]) ?(shortcut|ponytail):'\` (add other comment prefixes if your stack uses them)" [`skills/ponytail-debt/SKILL.md:18`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-debt/SKILL.md#L18)
- "Want an owner per row too? add \`git blame -L&lt;line>,&lt;line>\`." [`skills/ponytail-debt/SKILL.md:33`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-debt/SKILL.md#L33)
- "Review what the user names: uncommitted or staged changes, a branch, a PR link, or files. Nothing named: the uncommitted changes, or the last commit if there are none." [`skills/ponytail-review/SKILL.md:18`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-review/SKILL.md#L18)

</details>

<details><summary><b>Pushes and releases</b> · 4 · "Map first: README, deploy and build config, dependencies, e…"</summary>

- "Map first: README, deploy and build config, dependencies, entry points, tests; find the expected load (one person or many users and processes); trace the main flows and read fully the paths with user…" [`commands/ponytail-audit.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-audit.toml#L2)
- "Read the README, the deploy and build config, the dependency list, the entry points (main, routes, handlers, jobs, CLI commands) and the tests." [`skills/ponytail-audit/SKILL.md:20`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L20)
- "Find the expected load in the repo (README, deploy config): one person running a script, or many users and processes at once. Judge scale against that, and say which load you assumed." [`skills/ponytail-review/SKILL.md:26`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-review/SKILL.md#L26)
- "**ultra** | Also question the request: before building, push back on any part the need does not justify." [`skills/ponytail/SKILL.md:52`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail/SKILL.md#L52)

</details>

<details><summary><b>Reviews and audits</b> · 25 · "Then at most 20 numbered findings grouped Must fix / Should…"</summary>

- "Then at most 20 numbered findings grouped Must fix / Should fix / Nice to have, most important first; each: a bold title with file:lines, then four bullets: What this is, Problem, Fix, If we skip it." [`commands/ponytail-audit.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-audit.toml#L2)
- "A shortcut marked with a shortcut: (or older ponytail:) comment that names its limit is a decision, not a finding." [`commands/ponytail-audit.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-audit.toml#L2) (also in `commands/ponytail-review.toml:2`)
- "Every finding needs a concrete case." [`commands/ponytail-audit.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-audit.toml#L2)
- "Propose the smallest fix, prefer deleting code, never add layers." [`commands/ponytail-audit.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-audit.toml#L2) (also in `commands/ponytail-review.toml:2`)
- "End with 'Verdict:', 'Lean: -N lines, -M dependencies possible.' and 'Not checked:' for the parts you did not read." [`commands/ponytail-audit.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-audit.toml#L2)
- "Commands: /ponytail-review (over-engineering review of the current changes), /ponytail-audit (whole-repo over-engineering audit), /ponytail-debt (harvest shortcut: comments into a tracked ledger), /p…" [`commands/ponytail-help.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-help.toml#L2)
- "End with 'Verdict:', 'Lean: -N lines possible.' when lean findings exist, and 'Not checked:' if something mattered and you could not check it." [`commands/ponytail-review.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-review.toml#L2)
- "Review the current code changes like the senior developer who will be paged when they break." [`commands/ponytail-review.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-review.toml#L2)
- "Look for, in this order: bugs (wrong result, crash, missed edge case, a caller broken by the change, a fix in one caller while the shared function stays broken), risk (security holes, data loss), sca…" [`commands/ponytail-review.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-review.toml#L2)
- "Every finding needs a concrete case; re-read the lines to confirm it." [`commands/ponytail-review.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-review.toml#L2)
- "Then numbered findings grouped Must fix / Should fix / Nice to have; each finding: a bold title with file:lines, then four bullets: What this is, Problem, Fix, If we skip it (one or two short sentenc…" [`commands/ponytail-review.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-review.toml#L2)
- "Every finding needs a concrete case: "this input or situation leads to this wrong result". No case, no finding." [`skills/ponytail-audit/SKILL.md:59`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L59) (also in `skills/ponytail-review/SKILL.md:59`)
- "A shortcut marked with a \`shortcut:\` (or older \`ponytail:\`) comment that names its limit is a decision, not a finding, unless the expected load already crosses it." [`skills/ponytail-audit/SKILL.md:63`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L63) (also in `skills/ponytail-review/SKILL.md:63`)
- "Propose the smallest fix that works. Prefer fixes that delete code. Never add layers, frameworks or config the problem does not need." [`skills/ponytail-audit/SKILL.md:65`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L65) (also in `skills/ponytail-review/SKILL.md:65`)
- "Then the findings in three groups, most important first, skip empty groups:" [`skills/ponytail-audit/SKILL.md:77`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L77)
- "**Must fix:** bug, security, data loss, breaks at the expected load." [`skills/ponytail-audit/SKILL.md:78`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L78) (also in `skills/ponytail-review/SKILL.md:77`)
- "**Should fix:** risky code without a test, real slowness, duplication, a function that mixes jobs, code that should not exist." [`skills/ponytail-audit/SKILL.md:79`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L79) (also in `skills/ponytail-review/SKILL.md:78`)
- "At most 20 findings; if you left smaller ones out, say how many." [`skills/ponytail-audit/SKILL.md:83`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L83)
- "Number findings across all groups, so the user can say "fix 2 and 5"." [`skills/ponytail-audit/SKILL.md:83`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L83) (also in `skills/ponytail-review/SKILL.md:82`)
- "**ponytail-review** | \`/ponytail-review\` | Quality review of a diff: bugs, security, load, missing tests, speed, what to cut. Each finding says what goes wrong and how to fix it." [`skills/ponytail-help/SKILL.md:28`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-help/SKILL.md#L28)
- "**ponytail-audit** | \`/ponytail-audit\` | The same quality review for the whole repo, ranked." [`skills/ponytail-help/SKILL.md:29`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-help/SKILL.md#L29)
- "Review a change like the senior developer who will be paged when it breaks." [`skills/ponytail-review/SKILL.md:11`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-review/SKILL.md#L11)
- "Read the diff, then the code it touches: callers of every changed function, the functions it calls, the tests, the README." [`skills/ponytail-review/SKILL.md:21`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-review/SKILL.md#L21)
- "Then the findings in three groups, skip empty groups:" [`skills/ponytail-review/SKILL.md:76`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-review/SKILL.md#L76)
- "Lists findings, changes no code." [`skills/ponytail-review/SKILL.md:101`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-review/SKILL.md#L101)

</details>

<details><summary><b>Models and subagents</b> · 1 · "Render the published agentic benchmark of Ponytail 5 (39 ta…"</summary>

- "Render the published agentic benchmark of Ponytail 5 (39 tasks on a real FastAPI + React repo plus bug fixes, security and privacy cases and small apps, Opus 5.5, 5 runs each, against the same agent …" [`commands/ponytail-gain.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-gain.toml#L2)

</details>

<details><summary><b>Replies and reporting</b> · 17 · "Clean ledger.' Report only, change nothing."</summary>

- "Clean ledger.' Report only, change nothing." [`commands/ponytail-debt.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-debt.toml#L2)
- "NEVER print a per-repo savings number: the unbuilt version was never written, so there is no real baseline to subtract from in a live repo." [`commands/ponytail-gain.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-gain.toml#L2)
- "Report only." [`commands/ponytail-gain.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-gain.toml#L2)
- "Very simple English, explain technical terms." [`commands/ponytail-review.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-review.toml#L2)
- "This is a report the user asked for, so give it in full." [`skills/ponytail-audit/SKILL.md:14`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L14) (also in `skills/ponytail-review/SKILL.md:14`)
- "Find the expected load: one person running a script, or many users and processes at once. Judge scale against that, and say which load you assumed." [`skills/ponytail-audit/SKILL.md:22`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L22)
- "Big repo: go deep where a mistake costs the most, not file by file. Say which parts you did not read." [`skills/ponytail-audit/SKILL.md:27`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L27)
- "Explain a technical term the first time you use it." [`skills/ponytail-audit/SKILL.md:71`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L71) (also in `skills/ponytail-review/SKILL.md:71`)
- "One-shot report, changes no code." [`skills/ponytail-audit/SKILL.md:103`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L103)
- "Every deliberate ponytail shortcut is marked with a \`shortcut:\` comment naming its ceiling and upgrade path (older code may say \`ponytail:\`)." [`skills/ponytail-debt/SKILL.md:9`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-debt/SKILL.md#L9)
- "Reads and reports only, changes nothing." [`skills/ponytail-debt/SKILL.md:43`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-debt/SKILL.md#L43)
- "NEVER print a per-repo savings number ("you saved X lines/tokens here"): the unbuilt version was never written, so there is no real baseline to subtract from in a live repo." [`skills/ponytail-gain/SKILL.md:44`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-gain/SKILL.md#L44)
- "The only real per-repo figures come from \`/ponytail-debt\` (a counted ledger), and this card points there instead of inventing one." [`skills/ponytail-gain/SKILL.md:46`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-gain/SKILL.md#L46)
- "**Full** | \`/ponytail\` | The smallest complete change, a check where the logic needs one, and a reply that names what was skipped and any risk. Default." [`skills/ponytail-help/SKILL.md:18`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-help/SKILL.md#L18)
- "**ponytail** | \`/ponytail\` | Lazy mode itself: least new code, clear replies that name skipped work and risks." [`skills/ponytail-help/SKILL.md:27`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-help/SKILL.md#L27)
- "Say "stop ponytail" or "normal mode"." [`skills/ponytail-help/SKILL.md:40`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-help/SKILL.md#L40)
- "End your reply with one or two lines: what you skipped or did not check, and any risk the user must know." [`skills/ponytail/SKILL.md:15`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail/SKILL.md#L15)

</details>

<details><summary><b>State and files</b> · 12 · "Harvest every `shortcut:` comment (and older `ponytail:` on…"</summary>

- "Harvest every \`shortcut:\` comment (and older \`ponytail:\` ones) in this repository into a debt ledger so deferrals do not rot into 'later means never'." [`commands/ponytail-debt.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-debt.toml#L2)
- "Tag any marker that names no upgrade path or trigger as no-trigger, those rot silently." [`commands/ponytail-debt.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-debt.toml#L2)
- "One row per marker, grouped by file: &lt;file>:&lt;line> — &lt;what was simplified>. ceiling: &lt;the limit named in the comment>. upgrade: &lt;the trigger to revisit>." [`commands/ponytail-debt.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-debt.toml#L2)
- "One shot, change nothing: do not switch mode, write flag files, or persist anything." [`commands/ponytail-gain.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-gain.toml#L2) (also in `commands/ponytail-help.toml:2`)
- "**Scale:** fine for one user, wrong for many: check-then-write races, the same work done by every process, memory or lists that only grow, a query per item, O(n^2) on big input, per-process state tha…" [`skills/ponytail-audit/SKILL.md:38`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L38) (also in `skills/ponytail-review/SKILL.md:38`)
- "reuse: two helpers doing the same thing (keep one, name the path)" [`skills/ponytail-audit/SKILL.md:47`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L47)
- "\`&lt;file>:&lt;line>, &lt;what was simplified>. ceiling: &lt;the limit named>. upgrade: &lt;the trigger to revisit>.\`" [`skills/ponytail-debt/SKILL.md:30`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-debt/SKILL.md#L30)
- "Flag the rot risk: any marker comment that names no upgrade path or trigger gets a \`no-trigger\` tag, those are the ones that silently rot." [`skills/ponytail-debt/SKILL.md:36`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-debt/SKILL.md#L36)
- "To persist it, ask and it writes the ledger to a file (e.g. \`PONYTAIL-DEBT.md\`)." [`skills/ponytail-debt/SKILL.md:43`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-debt/SKILL.md#L43)
- "One-shot: do NOT change mode, write flag files, or persist anything." [`skills/ponytail-gain/SKILL.md:11`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-gain/SKILL.md#L11)
- "One-shot, do NOT change mode, write flag files, or persist anything." [`skills/ponytail-help/SKILL.md:10`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-help/SKILL.md#L10)
- "reuse: the repo already has this helper (name the path)" [`skills/ponytail-review/SKILL.md:48`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-review/SKILL.md#L48)

</details>

<details><summary><b>Network</b> · 2 · "Enable auto-update once: open `/plugin`, go to Marketplaces…"</summary>

- "Enable auto-update once: open \`/plugin\`, go to Marketplaces, pick ponytail, Enable auto-update." [`skills/ponytail-help/SKILL.md:70`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-help/SKILL.md#L70)
- "Other hosts use their own update flow." [`skills/ponytail-help/SKILL.md:72`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-help/SKILL.md#L72)

</details>

<details><summary><b>Safety and permissions</b> · 2 · "**Risk:** security holes (injection, weak randomness, secre…"</summary>

- "**Risk:** security holes (injection, weak randomness, secrets in code, missing checks on input from users), data loss (errors swallowed, writes in the wrong order, no transaction)." [`skills/ponytail-audit/SKILL.md:35`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L35)
- "**Risk:** security holes (injection, weak randomness, secrets, missing checks on input from users), data loss (errors swallowed, writes in the wrong order, no transaction)." [`skills/ponytail-review/SKILL.md:35`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-review/SKILL.md#L35)

</details>

<details><summary><b>other</b> · 21 · "Start with 'What this repo does:' and the load you assumed."</summary>

- "Start with 'What this repo does:' and the load you assumed." [`commands/ponytail-audit.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-audit.toml#L2)
- "End with the count of markers and how many lack a trigger." [`commands/ponytail-debt.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-debt.toml#L2)
- "If none: 'No shortcut debt." [`commands/ponytail-debt.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-debt.toml#L2)
- "Show the ponytail gain scoreboard." [`commands/ponytail-gain.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-gain.toml#L2)
- "Show the ponytail quick reference." [`commands/ponytail-help.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail-help.toml#L2)
- "Build the minimum that works." [`commands/ponytail.toml:2`](https://github.com/DietrichGebert/ponytail/blob/7801d06/commands/ponytail.toml#L2)
- "Order of importance: correct, safe, holds under load, tested, fast, lean." [`skills/ponytail-audit/SKILL.md:12`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L12) (also in `skills/ponytail-review/SKILL.md:12`)
- "Trace the main flows end to end: where data comes in, what is stored, what goes out. Read those paths fully: input from users, money, auth, data writes, background jobs, anything shared between proce…" [`skills/ponytail-audit/SKILL.md:24`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L24)
- "**Lean:** code that should not exist or should be smaller." [`skills/ponytail-audit/SKILL.md:45`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L45) (also in `skills/ponytail-review/SKILL.md:46`)
- "yagni: interface with one implementation, factory with one product, wrapper that only passes calls through" [`skills/ponytail-audit/SKILL.md:50`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L50)
- "The reader may never have seen this code." [`skills/ponytail-audit/SKILL.md:72`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L72) (also in `skills/ponytail-review/SKILL.md:72`)
- "Start with \`What this repo does:\` in two or three sentences, and the load you assumed." [`skills/ponytail-audit/SKILL.md:74`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L74)
- "**If we skip it:** Late orders show the wrong date, and accounting fixes them by hand." [`skills/ponytail-audit/SKILL.md:93`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L93) (also in `skills/ponytail-review/SKILL.md:91`)
- "\`Not checked:\` the parts you did not read or could not run." [`skills/ponytail-audit/SKILL.md:98`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-audit/SKILL.md#L98)
- "If the user names their own marker word (\`/ponytail-debt TODO\`), grep for that word instead." [`skills/ponytail-debt/SKILL.md:20`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-debt/SKILL.md#L20)
- "Skip hits that are not a deferral, like a note about a keyboard shortcut." [`skills/ponytail-debt/SKILL.md:23`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-debt/SKILL.md#L23)
- "End with \`&lt;N> markers, &lt;M> with no trigger.\` Nothing found: \`No shortcut debt." [`skills/ponytail-debt/SKILL.md:39`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-debt/SKILL.md#L39)
- "Claude Code and OpenCode use the slash-command forms above (OpenCode ships all six as slash commands)." [`skills/ponytail-help/SKILL.md:35`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-help/SKILL.md#L35)
- "\`/ponytail band\` hides the band above the prompt, the same command brings it back. \`/ponytail band on\` and \`/ponytail band off\` set it directly." [`skills/ponytail-help/SKILL.md:45`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-help/SKILL.md#L45)
- "Claude Code then pulls new versions at startup (run \`/reload-plugins\` when it prompts)." [`skills/ponytail-help/SKILL.md:70`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail-help/SKILL.md#L70)
- "The best code is the code never written." [`skills/ponytail/SKILL.md:15`](https://github.com/DietrichGebert/ponytail/blob/7801d06/skills/ponytail/SKILL.md#L15)

</details>

No reader's rules were read: this report lists facts only and carries no verdict.
