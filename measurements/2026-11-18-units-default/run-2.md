# 🔍 cat-herder 0.40.3 · vetted against the sample reader

`2026-11-18` · neckbeard 1.17.8 · cat-herder 0.40.3 @ `8442cb6be6`

> **🟨 INSTALL WITH CHANGES** · keep 25 skills  
> ⛔ **2** conflicts · 🔁 **0** covered · 🟩 **25** keep (25 skills) · 🗑️ **8** dropped  
> *against the sample reader (cat-herder)*

<details><summary>📝 <b>Why this verdict</b> · keep 25 skills</summary>

The verdict is install with changes because two units conflict with a hard stop in the reader's safety rules. The reviewer role (skills/herd/roles/reviewer.md, Limits) lets a reviewer retry an action the worker reported as refused, on its own judgement, and the worker role (skills/herd/roles/worker.md) tells the worker to expect that. The reader's rule says never run anything destructive without an explicit go-ahead in this conversation, so a retried refusal could break it. The rest of the plugin is skill text: 25 of 33 units are kept as procedure for the meow queue, herd pairs, handoffs and capture, and none of them is injected as a standing rule. The eight dropped units are the herder persona and cat-voice text plus one worked-example bullet, which add no working procedure. Three kept units repeat reader rules (a test must be seen to fail, and the scope asked for is the deliverable), so nothing needs adding there. One unit is worth copying as a standing rule: the builder text in skills/herd/roles/worker.md says never to simplify away validation at a trust boundary, error handling that prevents data loss, or a security measure, and the reader's files do not say that.

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
| 🆕 | **new, standing rule** | **1** | 🟩 |
| 🆕 | **new, on-demand skill** | **24** | 🟩 ×24 |
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

<details><summary>🟩 <b>Keep</b> · 25 skills · Capture; Splitting is bookkeeping, not new scope:; Asked to do work yourself: every; Rescue session…</summary>

| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| 1 | Capture (skills/capture/SKILL.md) | skill | 🟩 |
| 2 | Splitting is bookkeeping, not new scope: the items together cover exactly what was asked, nothing added. (skills/capture/SKILL.md) | skill | 🟩 |
| 3 | Asked to do work yourself: every session, not only the worker (skills/capture/SKILL.md) | skill | 🟩 |
| 4 | Rescue session: everything this session was tracking (skills/capture/SKILL.md) | skill | 🟩 |
| 5 | Stream-of-consciousness: the owner is riffing (skills/capture/SKILL.md) | skill | 🟩 |
| 6 | Herd (skills/herd/SKILL.md) | skill | 🟩 |
| 7 | The associate (skills/herd/roles/associate.md) | skill | 🟩 |
| 8 | Handing off to a new session (skills/herd/roles/handoff.md) | skill | 🟩 |
| 9 | If you're retiring (skills/herd/roles/handoff.md) | skill | 🟩 |
| 10 | If you're the one that stays (skills/herd/roles/handoff.md) | skill | 🟩 |
| 11 | Push your branch to origin early and often, because a clone can be removed at any time and unpushed work with it. (skills/herd/roles/handoff.md) | skill | 🟩 |
| 12 | In chat (skills/herd/roles/handoff.md) | skill | 🟩 |
| 13 | (top) (skills/herd/roles/reviewer.md) | skill | 🟩 |
| 14 | Setting up (once, when this pair starts) (skills/herd/roles/reviewer.md) | skill | 🟩 |
| 15 | Do the tests fail without the change? (skills/herd/roles/reviewer.md) | skill | 🟩 |
| 16 | Limits (skills/herd/roles/reviewer.md) | skill | 🟩 |
| 17 | Who started you, and stopping (skills/herd/roles/reviewer.md) | skill | 🟩 |
| 18 | Does the test pin the claim? Revert the change in your scratch copy and watch the test fail. (skills/herd/roles/reviewer.md) | skill | 🟩 |
| 19 | The worker, in a pair (skills/herd/roles/worker.md) | skill | 🟩 |
| 20 | Never simplify away validation at a trust boundary, error handling that prevents data loss, or a security measure. (skills/herd/roles/worker.md) | skill | ⭐ |
| 21 | The queue (skills/queue/SKILL.md) | skill | 🟩 |
| 22 | Working the queue (skills/queue/SKILL.md) | skill | 🟩 |
| 23 | Telling the owner what another session said (skills/queue/SKILL.md) | skill | 🟩 |
| 24 | Staying reasonable (skills/queue/SKILL.md) | skill | 🟩 |
| 25 | (top) (command) | skill | 🟩 |

</details>

<details><summary>🗑️ <b>Dropped</b> · 8 · skills/herder/SKILL.md; skills/herder/SKILL.md; skills/herder/SKILL.md; skills/herder/SKILL.md; ski…</summary>

`skills/herder/SKILL.md > The herder` · `skills/herder/SKILL.md > /herder and /herder off` · `skills/herder/SKILL.md > Cat names` · `skills/herder/SKILL.md > Capture` · `skills/herder/SKILL.md > Leaving Cat Herder` · `skills/herder/SKILL.md > Handoffs, in chat` · `skills/herder/SKILL.md > The voice rule` · `skills/queue/SKILL.md > Questions for you`

</details>

<details><summary>✅ <b>Do this</b> · 5 steps · Do not install as is: first; If you install anyway, narrow the; Copy the one new standing rule; Kee…</summary>

- ⬜ 1. Do not install as is: first deal with the retry-a-refused-action wording in the reviewer Limits section and in the worker role, since both clash with the destructive-action hard stop.
- ⬜ 2. If you install anyway, narrow the two clashing passages so a reviewer reports a refusal and asks you, and never retries a refused action on its own.
- ⬜ 3. Copy the one new standing rule from the patch below into your engineering rules, since it is general and holds without the plugin.
- ⬜ 4. Keep the capture, herd, queue and /meow skills only if you use the meow queue; they carry plugin mechanics and no rules, so they can be loaded on demand.
- ⬜ 5. Skip the herder skill entirely: it holds only persona text, and leaving it out costs nothing.

</details>

<details><summary>📋 <b>Proposed rules patch</b> · 25 skills · Capture; Splitting is bookkeeping, not new scope:; Asked to do work yourself: every; Rescue session…</summary>

Add one rule to examples/reader/rules/engineering.md, after the existing numbered rules. It comes from the builder text in skills/herd/roles/worker.md and is the only kept unit the reader does not already cover. Number it to follow the last rule in that file (5 is assumed here).

```diff
--- a/examples/reader/rules/engineering.md
+++ b/examples/reader/rules/engineering.md
@@
+5. Never simplify away validation at a trust boundary, error handling that prevents data loss, or a security measure.
```

Examples/reader/rules/safety.md needs no addition. Its rule 1 on destructive actions already holds and should stay as written; narrow the plugin instead, as the steps above say.

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
