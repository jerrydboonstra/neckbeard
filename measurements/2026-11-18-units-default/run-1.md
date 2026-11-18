# 🔍 cat-herder 0.40.3 · vetted against the sample reader

`2026-11-18` · neckbeard 1.17.8 · cat-herder 0.40.3 @ `8442cb6be6`

> **🟨 INSTALL WITH CHANGES** · keep 25 skills  
> ⛔ **2** conflicts · 🔁 **0** covered · 🟩 **25** keep (25 skills) · 🗑️ **8** dropped  
> *against the sample reader (cat-herder)*

<details><summary>📝 <b>Why this verdict</b> · keep 25 skills</summary>

The verdict is INSTALL WITH CHANGES because most of the plugin is its own mechanics, but two lines collide with the reader's hard stop in rules/safety.md. Of 33 units, 25 are kept as skills (capture, herd roles, queue), 8 are dropped as persona and voice text (the herder skill and the queue's questions section), and none are covered by rules already in force. Both conflicts say a reviewer may try an action the worker reported as refused, on its own judgement: one in skills/herd/roles/reviewer.md (Limits) and one in skills/herd/roles/worker.md. That cuts against the rule never to run anything destructive without an explicit go-ahead, so a refused force-push or delete could be retried without asking. Worth keeping: two new standing rules, reviewing the exact commits a note names and never a working tree, and reporting raw output instead of a verdict (the starred one). The plugin's test-must-fail check duplicates a rule in rules/engineering.md.

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
| ⛔ | **conflicts** with a rule you run | **2** | 🟥🟥 |
| 🔁 | **already covered** | **0** |  |
| 🆕 | **new, standing rule** | **2** | 🟩🟩 |
| 🆕 | **new, on-demand skill** | **23** | 🟩 ×23 |
| 🗑️ | **dropped** (persona, extras, no value) | **8** | ⬛ ×8 |

</details>

<details><summary>⛔ <b>Conflicts</b> · 2 · You may try the same action,; The reviewer may try an action</summary>

| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| 1 | "You may try the same action, on your own judgement, and report the result, allowed or refused, as a data point." | "1. **Never run anything destructive without my explicit go-ahead in this conversation:** deleting files outside the working tree, `rm -rf`, dropping tables, fo…" | rules/safety.md | 🟥 |
| 2 | "The reviewer may try an action you reported as refused, on its own judgement, and report what happened." | "1. **Never run anything destructive without my explicit go-ahead in this conversation:** deleting files outside the working tree, `rm -rf`, dropping tables, fo…" | rules/safety.md | 🟥 |

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
| 15 | review the commits the note names, never a working tree (skills/herd/roles/reviewer.md) | skill | 🟩 |
| 16 | Limits (skills/herd/roles/reviewer.md) | skill | 🟩 |
| 17 | Who started you, and stopping (skills/herd/roles/reviewer.md) | skill | 🟩 |
| 18 | Does the test pin the claim? Revert the change in your scratch copy and watch the test fail (skills/herd/roles/reviewer.md) | skill | 🟩 |
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

<details><summary>✅ <b>Do this</b> · 5 steps · Do not install as is: first; Copy the two new rules from; If you install anyway, load only; Leave t…</summary>

- ⬜ 1. Do not install as is: first remove or rewrite the retry-a-refused-action sentences in skills/herd/roles/reviewer.md and skills/herd/roles/worker.md so a refusal stays final unless the owner says go.
- ⬜ 2. Copy the two new rules from the patch below into the reader's engineering rules instead of relying on the plugin to carry them.
- ⬜ 3. If you install anyway, load only the capture, herd and queue skills, and exclude skills/herder/SKILL.md, which is persona and voice text.
- ⬜ 4. Leave the rigor: build test-must-fail step out of your rules, since rules/engineering.md already holds it.
- ⬜ 5. Run the plugin only in a session where rules/safety.md loads, and watch that a reviewer never repeats an action reported as refused.

</details>

<details><summary>📋 <b>Proposed rules patch</b> · 25 skills · Capture; An interruption, so keep it short; Asked to do work yourself: every; Rescue session: every…</summary>

Add both rules to examples/reader/rules/engineering.md, as new bullets after the existing review and testing rules. The conflict fix goes in the plugin's own files, not in the reader's rules, because rules/safety.md already forbids the retry.

```diff
--- a/examples/reader/rules/engineering.md
+++ b/examples/reader/rules/engineering.md
@@ review and reporting @@
+- **Review the commits the note names, never a working tree.** A reviewer checks the exact committed change it was pointed at, so what it approves is what ships.
+- **Report what you observed, never the verdict.** Paste raw output in the done note (commands run, results seen) and leave the pass or fail call to the reviewer.
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
