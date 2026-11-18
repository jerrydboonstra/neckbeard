# 🔍 cat-herder 0.40.3 · vetted against the sample reader

`2026-11-18` · neckbeard 1.17.8 · cat-herder 0.40.3 @ `8442cb6be6`

> **🟨 INSTALL WITH CHANGES** · keep 26 skills  
> ⛔ **2** conflicts · 🔁 **0** covered · 🟩 **26** keep (26 skills) · 🗑️ **7** dropped  
> *against the sample reader (cat-herder)*

<details><summary>📝 <b>Why this verdict</b> · keep 26 skills</summary>

The verdict is INSTALL WITH CHANGES. Of 33 units, 26 are kept as skills and 7 are dropped; none duplicate the reader's rules. The plugin is almost all its own queue, herd and capture mechanics, so most of it is neutral to the reader's rules. Two conflicts matter, both hard stops. The reviewer role in skills/herd/roles/reviewer.md (Limits) says it "may try the same action, on your own judgement" after a refusal, and the worker role in skills/herd/roles/worker.md says the reviewer may retry an action reported as refused. Both cut against the reader's first safety rule, which bars anything destructive without an explicit go-ahead in the conversation, so a refused delete or force-push could be retried on the agent's own say-so. Two general rules are worth keeping: the reviewer's "Cite every claim you accept with a file:line and a quoted span" (the starred one), and the worker's "Report what you observed, never the verdict". The seven dropped units are the herder skill's own persona and handoff text, which add nothing the reader needs.

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
| 🆕 | **new, on-demand skill** | **24** | 🟩 ×24 |
| 🗑️ | **dropped** (persona, extras, no value) | **7** | ⬛ ×7 |

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

<details><summary>🟩 <b>Keep</b> · 26 skills · Capture; An interruption, so keep it short; Asked to do work yourself: every; Rescue session: every…</summary>

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
| 15 | Each review (skills/herd/roles/reviewer.md) | skill | 🟩 |
| 16 | Limits (skills/herd/roles/reviewer.md) | skill | 🟩 |
| 17 | Who started you, and stopping (skills/herd/roles/reviewer.md) | skill | 🟩 |
| 18 | Cite every claim you accept with a file:line and a quoted span. A criterion asserted without a citation isn't met. (skills/herd/roles/reviewer.md) | skill | ⭐ |
| 19 | The worker, in a pair (skills/herd/roles/worker.md) | skill | 🟩 |
| 20 | Report what you observed, never the verdict: paste exact commands, exit codes and error text, and never paraphrase evidence. (skills/herd/roles/worker.md) | skill | 🟩 |
| 21 | The queue (skills/queue/SKILL.md) | skill | 🟩 |
| 22 | Working the queue (skills/queue/SKILL.md) | skill | 🟩 |
| 23 | Telling the owner what another session said (skills/queue/SKILL.md) | skill | 🟩 |
| 24 | Questions for you (skills/queue/SKILL.md) | skill | 🟩 |
| 25 | Staying reasonable (skills/queue/SKILL.md) | skill | 🟩 |
| 26 | (top) (command) | skill | 🟩 |

</details>

<details><summary>🗑️ <b>Dropped</b> · 7 · skills/herder/SKILL.md; skills/herder/SKILL.md; skills/herder/SKILL.md; skills/herder/SKILL.md; ski…</summary>

`skills/herder/SKILL.md > The herder` · `skills/herder/SKILL.md > /herder and /herder off` · `skills/herder/SKILL.md > Cat names` · `skills/herder/SKILL.md > Capture` · `skills/herder/SKILL.md > Leaving Cat Herder` · `skills/herder/SKILL.md > Handoffs, in chat` · `skills/herder/SKILL.md > The voice rule`

</details>

<details><summary>✅ <b>Do this</b> · 6 steps · Install the plugin only if you; Where a retry is kept, require; Skip the herder skill (skills/herde…</summary>

- ⬜ 1. Install the plugin only if you want the queue and herd workflow, and fix the two conflicting passages first: in skills/herd/roles/reviewer.md under Limits and in skills/herd/roles/worker.md, remove the sentences that let the reviewer retry a refused action on its own judgement.
- ⬜ 2. Where a retry is kept, require your explicit go-ahead in the conversation for any destructive or published-history action, as rules/safety.md already says.
- ⬜ 3. Skip the herder skill (skills/herder/SKILL.md): its seven units are dropped.
- ⬜ 4. Keep the other 26 skill units as they come with the plugin; they need no rule changes.
- ⬜ 5. Copy the two new standing rules from the patch below into your engineering rules, so they hold even when the plugin is off.
- ⬜ 6. Re-run the vet after editing the plugin's role files to confirm the two conflicts are gone.

</details>

<details><summary>📋 <b>Proposed rules patch</b> · 26 skills · Capture; An interruption, so keep it short; Asked to do work yourself: every; Rescue session: every…</summary>

Add both rules to the end of the numbered list in examples/reader/rules/engineering.md. They fit its style of a bold lead sentence followed by one line of detail. No change is needed in examples/reader/rules/safety.md; the conflicts are fixed in the plugin, not in the reader's hard stops.

```diff
--- a/examples/reader/rules/engineering.md
+++ b/examples/reader/rules/engineering.md
@@
 7. **Commit messages:** imperative subject under 60 characters, then why.
+8. **Cite what you accept.** A reviewer cites every claim it accepts with a
+   file:line and a quoted span. A criterion asserted without a citation is
+   not met.
+9. **Report observations, not verdicts.** Done notes paste the exact commands,
+   exit codes and error text. Never paraphrase evidence.
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
