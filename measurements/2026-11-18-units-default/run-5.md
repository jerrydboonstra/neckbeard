# 🔍 cat-herder 0.40.3 · vetted against the sample reader

`2026-11-18` · neckbeard 1.17.8 · cat-herder 0.40.3 @ `8442cb6be6`

> **🟨 INSTALL WITH CHANGES** · keep 26 skills  
> ⛔ **2** conflicts · 🔁 **0** covered · 🟩 **26** keep (26 skills) · 🗑️ **7** dropped  
> *against the sample reader (cat-herder)*

<details><summary>📝 <b>Why this verdict</b> · keep 26 skills</summary>

The plugin is mostly queue and herd mechanics for its own multi-session workflow, so 26 of 33 units are kept as skills and 7 persona units in skills/herder/SKILL.md (the cat voice) are dropped as not being work rules. Two conflicts matter, both hard stops: skills/herd/roles/reviewer.md (Limits) lets a reviewer retry a refused action on its own judgement, and skills/herd/roles/worker.md says the reviewer may do the same. That cuts against the reader's rule never to run anything destructive without an explicit go-ahead, because a refusal is exactly where a destructive action would be blocked. Three ideas are new and worth keeping: split a diff that mixes refactor and behaviour change, name the failure you fear and then try to produce it (listing what was not checked), and report raw observations rather than a verdict. The rest of the scope and debt-marker guidance duplicates the reader's engineering rules 4 and 5.

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
| 🆕 | **new, standing rule** | **3** | 🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **23** | 🟩 ×23 |
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

<details><summary>🟩 <b>Keep</b> · 26 skills · Capture; The scope I asked for is; Asked to do work yourself: every; Rescue session: everything thi…</summary>

| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| 1 | Capture (skills/capture/SKILL.md) | skill | 🟩 |
| 2 | The scope I asked for is the deliverable. (skills/capture/SKILL.md) | skill | 🟩 |
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
| 15 | A diff that both restructures code and changes behaviour, so you can't tell which lines do which, is a finding: split the refactor out and make the change wait… (skills/herd/roles/reviewer.md) | skill | 🟩 |
| 16 | A finding outside the item's scope goes in your note as a suggestion, not a reason to reopen. (skills/herd/roles/reviewer.md) | skill | 🟩 |
| 17 | Who started you, and stopping (skills/herd/roles/reviewer.md) | skill | 🟩 |
| 18 | Name the failure you fear: write "I claim X; the failure I fear is Y", then try to produce Y. A verdict is never silence; list what you didn't check. (skills/herd/roles/reviewer.md) | skill | ⭐ |
| 19 | Leave deliberate shortcuts marked: TODO(debt): (skills/herd/roles/worker.md) | skill | 🟩 |
| 20 | Report what you observed, never the verdict: paste raw commands, exit codes and output; "All 12 tests pass" is an observation, "verified" is the reviewer's cal… (skills/herd/roles/worker.md) | skill | 🟩 |
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

<details><summary>✅ <b>Do this</b> · 5 steps · Install only with changes: remove or; Skip or disable the herder persona; Use the queue, capture an…</summary>

- ⬜ 1. Install only with changes: remove or rewrite the two retry-a-refused-action passages in skills/herd/roles/reviewer.md and skills/herd/roles/worker.md so a refusal is never retried without the reader's explicit go-ahead.
- ⬜ 2. Skip or disable the herder persona skill (skills/herder/SKILL.md) if you do not want cat voice in replies.
- ⬜ 3. Use the queue, capture and herd skills only in sessions where you want that workflow; they add nothing to ordinary work.
- ⬜ 4. Copy the three new standing rules from the patch into your engineering rules rather than relying on the reviewer and worker role files to carry them.
- ⬜ 5. Do not copy the scope and debt-marker items, since your rules already cover them.

</details>

<details><summary>📋 <b>Proposed rules patch</b> · 26 skills · Capture; The scope I asked for is; Asked to do work yourself: every; Rescue session: everything thi…</summary>

Add these to examples/reader/rules/engineering.md, after the existing numbered rules, in the same style:

```diff
+6. A diff that both restructures code and changes behaviour is a finding: split the refactor out and land it first.
+7. Before calling work verified, name the failure you fear ("I claim X; the failure I fear is Y"), try to produce it, and list what you did not check.
+8. Report what you observed, not the verdict: paste the raw command, exit code and output, and leave "verified" to the reviewer.
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
