# 🔍 ch-v0403 0.40.3 · vetted against the sample reader

> ## 🟧 INSTALL WITH CHANGES · keep the queue, herd and capture skills, fix one reviewer rule
> 25 of 33 units are skills that work as shipped and add something the reader lacks; 8 are voice text or an example and are dropped. One sentence in the reviewer role lets a reviewer retry an action the worker was refused, which breaks the reader's destructive-action stop. Five general rules are worth copying as standing rules whatever you decide about the plugin.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-15` · neckbeard 1.14.0 · ch-v0403 0.40.3

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟨 | **Cost** | Four skill descriptions load with the plugin and one command (`commands/meow.md`). Hooks add one line to stdout after an automatic compaction, and only in a session on a queue's roster; the inventory could not size it (3 hooks unidentifiable, read by hand in `lib/cat_herder/hooks.py`) |
| 🟩 | **Reach** | Main session only (no hooked event fires in a subagent) |
| 🟨 | **Leaves state** | Counts compactions in the queue roster and notes a closed session in the machine's state (`hooks/claude.json`, `hooks/claude-codex.json`); the `meow` tool commits and pushes queue state to a git remote or local ref; `tools/` holds ssh, tmux and cloud launchers |
| 🟨 | **Live surface** | `meow` CLI, git pushes to the queue remote, `tools/remote-session`, `tools/cloud-launcher`, `tools/deploy-host.sh`; no MCP servers |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 25 skill sections and 5 rules |

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **1** | 🟥 |
| 🔁 | **already covered** | **3** | ⬜⬜⬜ |
| 🆕 | **new, standing rule** | **5** | 🟩🟩🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **0** | none |
| 🗑️ | **dropped** (persona, extras, no value) | **8** | ⬛⬛⬛⬛⬛⬛⬛⬛ |

Skills kept: 25 of 33 units. A further 24 units (kept or dropped) hold nothing general beyond the plugin's own mechanics, so they sit in no rule row.

## ⛔ Conflicts: 1

| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| 1 | `skills/herd/roles/reviewer.md` "Limits": "You may try the same action, on your own judgement, and report the result" (an action the worker's session was refused) | "Never run anything destructive without my explicit go-ahead in this conversation" | examples/reader/rules/safety.md rule 1 | 🟥 |

The reviewer acts on its own judgement, so a refused deletion or force-push could run with no go-ahead from you. The worker role (`skills/herd/roles/worker.md`) says the opposite for the worker: never ask the reviewer to run it.

## 🔁 Already covered: 3

| its rule | covered by | held in |
|---|---|---|
| `skills/capture/SKILL.md` "Asked to do work yourself": work found along the way "is captured the same way, not done inline" | "The scope I asked for is the deliverable" | examples/reader/rules/engineering.md rule 4 |
| `skills/queue/SKILL.md` "The queue" (phone rules): never act on a guessed reading of an irreversible command | Ask when the wrong reading is costly | examples/reader/rules/safety.md rule 5 |
| `skills/queue/SKILL.md` "Working the queue": reread a stale item before starting, never use `--force` unasked | Say what you would change and let me decide; stop and ask | examples/reader/rules/engineering.md rule 4, examples/reader/rules/safety.md rule 1 |

I cite engineering rule 4 for the first row because it states scope as a rule in its own right; the capture text only applies it to queueing.

## 🟩 Rules to copy: 5

| # | unit | rule | kind |
|:--:|---|---|:--:|
| 1 | `skills/capture/SKILL.md` "An interruption, so keep it short" | "mark anything else as an assumption" (facts come from the conversation or a file you checked) | 🆕 standing |
| 2 | `skills/herd/roles/reviewer.md` "Each review" | a diff that "both restructures code and changes behaviour" is a finding; split the refactor out | 🆕 standing |
| 3 | `skills/herd/roles/reviewer.md` "When the item says rigor: build" | "Stop only the processes you started, by their PID, never by port." | 🆕 standing |
| 4 | `skills/herd/roles/worker.md` "When the item says rigor: build" | "Never simplify away validation at a trust boundary" (also data-loss error handling and security measures) | 🆕 standing |
| 5 | `skills/queue/SKILL.md` "Staying reasonable" | "A question the owner skipped is unread, not answered." | 🆕 standing |

## 🟩 Keep: 25

| # | skill section | kind | |
|:--:|---|:--:|:--:|
| 1 | `skills/capture/SKILL.md` "Capture" | skill | 🟩 |
| 2 | `skills/capture/SKILL.md` "An interruption, so keep it short" | skill | 🟩 |
| 3 | `skills/capture/SKILL.md` "Asked to do work yourself: every session, not only the worker" | skill | 🟩 |
| 4 | `skills/capture/SKILL.md` "Rescue session: everything this session was tracking" | skill | 🟩 |
| 5 | `skills/capture/SKILL.md` "Stream-of-consciousness: the owner is riffing" | skill | 🟩 |
| 6 | `skills/herd/SKILL.md` "Herd" | skill | 🟩 |
| 7 | `skills/herd/roles/associate.md` "The associate" | role | 🟩 |
| 8 | `skills/herd/roles/handoff.md` "Handing off to a new session" | role | 🟩 |
| 9 | `skills/herd/roles/handoff.md` "If you're retiring" | role | 🟩 |
| 10 | `skills/herd/roles/handoff.md` "If you're the one that stays" | role | 🟩 |
| 11 | `skills/herd/roles/handoff.md` "If you're the new session" | role | 🟩 |
| 12 | `skills/herd/roles/handoff.md` "In chat" | role | 🟩 |
| 13 | `skills/herd/roles/reviewer.md` "(top)" | role | 🟩 |
| 14 | `skills/herd/roles/reviewer.md` "Setting up (once, when this pair starts)" | role | 🟩 |
| 15 | `skills/herd/roles/reviewer.md` "Each review" | role | 🟩 |
| 16 | `skills/herd/roles/reviewer.md` "Limits" (after the conflict above is fixed) | role | 🟧 |
| 17 | `skills/herd/roles/reviewer.md` "Who started you, and stopping" | role | 🟩 |
| 18 | `skills/herd/roles/reviewer.md` "When the item says rigor: build" | role | 🟩 |
| 19 | `skills/herd/roles/worker.md` "The worker, in a pair" | role | 🟩 |
| 20 | `skills/herd/roles/worker.md` "When the item says rigor: build" | role | 🟩 |
| 21 | `skills/queue/SKILL.md` "The queue" | skill | 🟩 |
| 22 | `skills/queue/SKILL.md` "Working the queue" | skill | 🟩 |
| 23 | `skills/queue/SKILL.md` "Telling the owner what another session said" | skill | 🟩 |
| 24 | `skills/queue/SKILL.md` "Staying reasonable" | skill | 🟩 |
| 25 | `commands/meow.md` "(top)" | command | 🟩 |

## 🗑️ Dropped
Units u21 to u27 (`skills/herder/SKILL.md`, every section: cat-voice persona) · u31 (`skills/queue/SKILL.md` "Questions for you", an example bullet with no rule of its own)

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| Skills `capture`, `herd`, `herder`, `queue` | on demand | no | 15,941 / 52,380 / 6,811 / 28,123 chars |
| Command `meow` | when typed | no | 1,651 chars |
| Hook PreCompact (auto) | before an automatic compaction | no | unknown, counts the compaction in the roster |
| Hook SessionStart (compact) | after a compaction | no | one line, size not traced |
| Hook SessionEnd | when a session closes | no | no output, writes a notice to machine state |

## ✅ Do this
- ⬜ 1. If you install, fix the `Limits` sentence in `skills/herd/roles/reviewer.md` so a reviewer never retries a refused action without your go-ahead, or leave the herd roles unused.
- ⬜ 2. Copy the five standing rules below whether or not you install.
- ⬜ 3. Skip the `herder` skill; it is voice only.

Case: the plugin injects only on compaction in a rostered session and not in subagents, so the carrying cost is small, and it has real skills worth keeping, so installing is reasonable once the conflict is handled.

## 📋 Proposed rules patch
Add to `rules/engineering.md` after rule 7, keeping its numbered style:

```diff
+8. **Mark assumptions.** Facts come from the conversation or a file you checked;
+   mark anything else as an assumption.
+9. **Do not mix a refactor with a behaviour change.** If a diff does both and you
+   cannot tell which lines do which, split the refactor out first.
+10. **Stop only the processes you started,** by their PID, never by port.
+11. **Never simplify away validation at a trust boundary,** error handling that
+    prevents data loss, or a security measure.
```

Add to `rules/safety.md` as rule 6:

```diff
+6. **A question I skipped is unread, not answered.** Do not treat silence as a
+   go-ahead; ask again and carry on with whatever does not depend on it.
```

Nothing to add as a new skill.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
