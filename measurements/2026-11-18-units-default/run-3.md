# 🔍 cat-herder 0.40.3 · vetted against the sample reader

`2026-11-18` · neckbeard 1.17.8 · cat-herder 0.40.3 @ `8442cb6be6`

> **🟨 INSTALL WITH CHANGES** · keep 25 skills  
> ⛔ **1** conflicts · 🔁 **0** covered · 🟩 **25** keep (25 skills) · 🗑️ **8** dropped  
> *against the sample reader (cat-herder)*

<details><summary>📝 <b>Why this verdict</b> · keep 25 skills</summary>

The verdict is INSTALL WITH CHANGES because almost all of the plugin is useful but one line collides with a hard stop. Of 33 units, 25 are kept as skills (the meow queue, capture, herd roles, handoff and reviewer procedures), and 8 are dropped, all of them the cat voice and persona text in skills/herder/SKILL.md plus one voice-flavoured section of skills/queue/SKILL.md. Nothing was found already covered by the reader's rules. The one conflict is in skills/herd/roles/reviewer.md under Limits, which says a reviewer may try a refused action "on your own judgement" and report the result; that clashes with the reader's rule in rules/safety.md that nothing destructive runs without an explicit go-ahead, and it is marked a hard stop. Two units are worth copying as standing rules because they apply beyond this plugin: the reviewer's habit of citing every accepted claim with a file and line plus a quoted span, and the worker's habit of pasting raw output and reporting what was observed, never the verdict (the starred one).

Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

Baseline: the sample reader · 4 rule files · 2347 bytes · sha256 b564c945bf65

Judge: your own config, told to ignore it

<details><summary>Rule files</summary>

- `CLAUDE.md`
- `rules/engineering.md`
- `rules/safety.md`
- `skills/release-notes/SKILL.md`

</details>

**How its rules sorted**

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **1** | 🟥 |
| 🔁 | **already covered** | **0** |  |
| 🆕 | **new, standing rule** | **2** | 🟩🟩 |
| 🆕 | **new, on-demand skill** | **23** | 🟩 ×23 |
| 🗑️ | **dropped** (persona, extras, no value) | **8** | ⬛ ×8 |

</details>

<details><summary>⛔ <b>Conflicts</b> · 1 · You may try the same action,</summary>

| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| 1 | "You may try the same action, on your own judgement, and report the result, allowed or refused, as a data point." | "1. **Never run anything destructive without my explicit go-ahead in this conversation:** deleting files outside the working tree, `rm -rf`, dropping tables, fo…" | rules/safety.md | 🟥 |

</details>

<details><summary>🔁 <b>Already covered</b> · none</summary>

None.

</details>

<details><summary>🟩 <b>Keep</b> · 25 skills · Capture; An interruption, so keep it short; Asked to do work yourself: every; Rescue session: every…</summary>

| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| 1 | Capture (skills/capture/SKILL.md) | skill | 🟩 |
| 2 | An interruption, so keep it short (skills/capture/SKILL.md) | skill | 🟩 |
| 3 | Asked to do work yourself: every session, not only the worker (skills/capture/SKILL.md) | skill | 🟩 |
| 4 | Rescue session: everything this session was tracking (skills/capture/SKILL.md) | skill | 🟩 |
| 5 | Stream-of-consciousness: the owner is riffing (skills/capture/SKILL.md) | skill | 🟩 |
| 6 | Herd (skills/herd/SKILL.md) | skill | 🟩 |
| 7 | The associate (skills/herd/roles/associate.md) | skill | 🟩 |
| 8 | Handing off to a new session (skills/herd/roles/handoff.md) | skill | 🟩 |
| 9 | If you're retiring (skills/herd/roles/handoff.md) | skill | 🟩 |
| 10 | If you're the one that stays (skills/herd/roles/handoff.md) | skill | 🟩 |
| 11 | If you're the new session (skills/herd/roles/handoff.md) | skill | 🟩 |
| 12 | In chat (skills/herd/roles/handoff.md) | skill | 🟩 |
| 13 | (top) (skills/herd/roles/reviewer.md) | skill | 🟩 |
| 14 | Setting up (once, when this pair starts) (skills/herd/roles/reviewer.md) | skill | 🟩 |
| 15 | Run the tests that cover the change; review the commits the note names, never a working tree. (skills/herd/roles/reviewer.md) | skill | 🟩 |
| 16 | Limits (skills/herd/roles/reviewer.md) | skill | 🟩 |
| 17 | Who started you, and stopping (skills/herd/roles/reviewer.md) | skill | 🟩 |
| 18 | Cite every claim you accept with a `file:line` and a quoted span. A criterion asserted without a citation isn't met. (skills/herd/roles/reviewer.md) | skill | 🟩 |
| 19 | The worker, in a pair (skills/herd/roles/worker.md) | skill | 🟩 |
| 20 | Paste raw output in the done note... Report what you observed, never the verdict. (skills/herd/roles/worker.md) | skill | ⭐ |
| 21 | The queue (skills/queue/SKILL.md) | skill | 🟩 |
| 22 | Working the queue (skills/queue/SKILL.md) | skill | 🟩 |
| 23 | Telling the owner what another session said (skills/queue/SKILL.md) | skill | 🟩 |
| 24 | Staying reasonable (skills/queue/SKILL.md) | skill | 🟩 |
| 25 | (top) (command) | skill | 🟩 |

</details>

<details><summary>🗑️ <b>Dropped</b> · 8 · skills/herder/SKILL.md; skills/herder/SKILL.md; skills/herder/SKILL.md; skills/herder/SKILL.md; ski…</summary>

`skills/herder/SKILL.md > The herder` · `skills/herder/SKILL.md > /herder and /herder off` · `skills/herder/SKILL.md > Cat names` · `skills/herder/SKILL.md > Capture` · `skills/herder/SKILL.md > Leaving Cat Herder` · `skills/herder/SKILL.md > Handoffs, in chat` · `skills/herder/SKILL.md > The voice rule` · `skills/queue/SKILL.md > Questions for you`

</details>

<details><summary>✅ <b>Do this</b> · 6 steps · Install the plugin only after removing; Do not enable the herder persona:; Keep the 25 skill units …</summary>

- ⬜ 1. Install the plugin only after removing or overriding the Limits passage in skills/herd/roles/reviewer.md that lets a reviewer retry a refused action on its own judgement, so rules/safety.md stays in force.
- ⬜ 2. Do not enable the herder persona: skip skills/herder/SKILL.md and the cat-voice section of skills/queue/SKILL.md, which add style text and no mechanics.
- ⬜ 3. Keep the 25 skill units as they ship: capture, herd and its roles, handoff, and the queue skills. They carry the plugin's own meow mechanics and need no rule changes.
- ⬜ 4. Copy the two new standing rules from the patch below into the reader's rules so they hold outside the plugin too.
- ⬜ 5. Load the plugin for one session first (claude with --plugin-dir) and confirm a reviewer session still asks before any destructive step.
- ⬜ 6. If installed anyway, narrow it: restrict the reviewer role to read-only commands and tests, and tell reviewers a refused action stays refused.

</details>

<details><summary>📋 <b>Proposed rules patch</b> · 25 skills · Capture; An interruption, so keep it short; Asked to do work yourself: every; Rescue session: every…</summary>

Add the two rules as a new file, examples/reader/rules/evidence.md, written in the numbered, bold-lead style of examples/reader/rules/safety.md. Leave examples/reader/rules/safety.md unchanged: its destructive-action rule is what resolves the conflict.

```diff
--- /dev/null
+++ examples/reader/rules/evidence.md
@@ -0,0 +1,2 @@
+1. **Cite every claim you accept:** give a `file:line` and a short quoted span. A criterion asserted without a citation isn't met.
+2. **Report what you observed, never the verdict:** paste the raw output when handing work off, and let the reader judge it.
```

</details>

## What it adds

🟢 read in full · 🟡 partly read · 🔴 something unread

<details><summary>🟡 <b>Injects</b> · 4 skills · ~16981 tokens on demand · ~2357 chars of skill descriptions every session · hook text partly read</summary>

- Skills:
  - capture: description every session (976 chars); the file on demand (14273 bytes, ~3568 tokens)
  - herd: description every session (564 chars); the file on demand (20779 bytes, ~5194 tokens)
  - herder: description every session (238 chars); the file on demand (6062 bytes, ~1515 tokens)
  - queue: description every session (579 chars); the file on demand (26817 bytes, ~6704 tokens)
- Rule files: none
- Hook-injected text: partly read
  - neckbeard did not read: hooks/claude-codex.json, hooks/claude.json: unresolved hooks: PreCompact: bin/meow; SessionEnd: bin/meow; SessionStart: bin/meow; hooks/claude-codex.json, hooks/claude.json: 3 hook(s) have unknown behaviour, which is not the same as none: 3 whose script was found but whose payload could not be traced. Read them by hand.

</details>

<details><summary>🟡 <b>Hooks</b> · 3 hooks · stay in the main session · partly read</summary>

- Hooks: partly read
  - PreCompact (auto): bin/meow
  - SessionEnd: bin/meow
  - SessionStart (compact): bin/meow
  - reaches subagents: false (no event known to fire in a subagent)
  - neckbeard did not read: hooks/claude-codex.json, hooks/claude.json: unresolved hooks: PreCompact: bin/meow; SessionEnd: bin/meow; SessionStart: bin/meow; hooks/claude-codex.json, hooks/claude.json: 3 hook(s) have unknown behaviour, which is not the same as none: 3 whose script was found but whose payload could not be traced. Read them by hand.

</details>

<details><summary>🟢 <b>Subagents and commands</b> · no agents · 1 commands</summary>

- Agents: none
- Commands:
  - meow

</details>

<details><summary>🟢 <b>State it may leave</b> · 36 files that may write state · 10 named</summary>

- Persistence candidates:
  - Makefile
  - lib/cat_herder/addresses.py
  - lib/cat_herder/behavior.py
  - lib/cat_herder/checkin.py
  - lib/cat_herder/cli.py
  - lib/cat_herder/ended.py
  - lib/cat_herder/fieldtrip.py
  - lib/cat_herder/hike.py
  - lib/cat_herder/integrate.py
  - lib/cat_herder/names.py
  - and 26 more, in: lib/ 13, tools/ 13

</details>

<details><summary>🟢 <b>Reaches outside the session</b> · no MCP servers</summary>

- MCP servers: none

</details>

<details><summary>🟢 <b>Source</b> · plugin · cat-herder 0.40.3 from plugin.json · commit 8442cb6 · no marketplace</summary>

- Kind: plugin
- Name: cat-herder (from plugin.json)
- Version: 0.40.3 (from plugin.json)
- plugin.json:
  - name and version, shown above
- Marketplace: none
- Commit: 8442cb6be6

</details>

Load timing is how Claude Code loads skills, not measured here. Tokens are estimated as bytes / 4; where the inventory fell back to a character count, "bytes" counts characters.
