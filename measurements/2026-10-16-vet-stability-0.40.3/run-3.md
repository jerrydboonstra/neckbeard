# 🔍 ch-v0403 0.40.3 · vetted against the sample reader

> ## 🟨 COPY RULES, SKIP PLUGIN · keep five small rules and one skill idea as text
> The plugin is a git-backed work queue and multi-agent review system, not a rules pack, and the reader has no queue to run it on. Its hooks cost almost nothing in a normal session, and none of its rules collide with the reader's hard stops. Most of its coding and review rules repeat what the reader already runs, so only six items are worth carrying, and text carries them cheaper than a plugin does.
>
> Verdict is relative to the [sample reader](https://github.com/jerrydboonstra/neckbeard/tree/main/examples/reader), not a judgment of the plugin's quality. Reproduce: see [examples/README.md](https://github.com/jerrydboonstra/neckbeard/blob/main/examples/README.md).

`2026-10-15` · neckbeard 1.14.0 · ch-v0403 0.40.3

## ⚡ At a glance

| | | |
|:--:|---|---|
| 🟩 | **Cost** | No text injected at session start. After an automatic compaction, one or two lines, and only in a session on a queue roster. The four skill descriptions (about 2.3 KB) sit in every session's skill list. |
| 🟩 | **Reach** | Main session only (likely). The three hooks fire on compaction, session start after compaction and session end, none of which fire inside a subagent. |
| 🟨 | **Leaves state** | SessionEnd writes an ended-sessions record to a per-machine Cat Herder state folder in the user's home. PreCompact pushes a commit to the queue remote, but only for a session on a roster. |
| 🟨 | **Live surface** | A `meow` command on PATH (`bin/meow`), git pushes to a queue branch over ssh or https, and optional launchers (`tools/remote-session` needs ssh and tmux). No MCP servers. |
| 🟩 | **Refused reads** | none |
| 🟩 | **Worth keeping** | 6: 5 rules and 1 skill |

The dossier listed all three hooks as unidentifiable, so I read `lib/cat_herder/hooks.py` and `hooks/claude.json`, `hooks/claude-codex.json` by hand. `hooks/claude-codex.json` registers PreCompact and SessionStart (matcher `compact`), and `hooks/claude.json` registers SessionEnd. Each ends in `meow _hook <event>`, is silent, and exits 0 on any error. The other hook files target Cursor and Antigravity, and Claude Code does not load them.

## 🧮 How its rules sorted

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **0** | none |
| 🔁 | **already covered** | **12** | ▰ ×12 |
| 🆕 | **new, standing rule** | **5** | 🟩🟩🟩🟩🟩 |
| 🆕 | **new, on-demand skill** | **1** | 🟩 |
| 🗑️ | **dropped** (persona, extras, no value) | **15** | ▰ ×15 |

## ⛔ Conflicts: 0
Nothing found. I checked the reader's five hard stops in `examples/reader/rules/safety.md` against the target. Its queue refuses to run on the code branch, `meow herd clean` waits for the owner, `integrate` never pushes, and deploys and releases need the owner's word. `meow herd pair start` also defaults a started session to opus. That does not collide with `examples/reader/rules/engineering.md` rule 6, because a session it starts has no definition that pins a model, and the plugin says to pass the owner's choice instead.

## 🔁 Already covered: 12
| its rule | covered by | held in |
|---|---|---|
| Source priority, and no new dependency when a few lines do it (`skills/herd/roles/worker.md`) | rule 1, "Reuse before writing" | examples/reader/rules/engineering.md |
| Fix the root cause, find every caller (`skills/herd/roles/worker.md`) | rule 2, "Fix the cause, not the symptom" | examples/reader/rules/engineering.md |
| Debt comment naming ceiling and upgrade path; the project's own marker wins (`skills/herd/roles/worker.md`) | rule 5, which names `TODO(debt):`, so the target's deferral gives the same result | examples/reader/rules/engineering.md |
| Does the test pin the claim: revert the change and watch it fail (`skills/herd/roles/reviewer.md`) | rule 3, "seen to fail" | examples/reader/rules/engineering.md |
| Splitting is bookkeeping, the scope asked for stays the deliverable; out-of-scope findings are suggestions (`skills/capture/SKILL.md`, `skills/herd/roles/reviewer.md`) | rule 4, "The scope I asked for" | examples/reader/rules/engineering.md |
| Never paste secrets, use `<redacted>` (`skills/herd/roles/worker.md`) | rule 4, "Secrets never appear" | examples/reader/rules/safety.md |
| Never run `meow herd clean` on your own, it deletes folders outside the tree (`skills/herd/roles/worker.md`) | rule 1, destructive actions need a go-ahead | examples/reader/rules/safety.md |
| Stop before any queue write if the queue sits on main (`skills/queue/SKILL.md`) | rule 2, "Never push to `main`" | examples/reader/rules/safety.md |
| Read back an irreversible command matched by sound and wait for a yes (`skills/queue/SKILL.md`) | rule 5, ask when the wrong reading is costly. Chosen over rule 1 because the trigger is a guessed reading, not the kind of action. | examples/reader/rules/safety.md |
| Blocked is a real answer: do the clear parts, ask about the rest (`skills/herd/roles/worker.md`) | rule 5, "ask" | examples/reader/rules/safety.md |
| A relayed answer never stands in for the owner's word on a deploy or release (`skills/herd/roles/worker.md`) | rule 3, "Deploys happen only after" | examples/reader/rules/safety.md |
| Cite every claim with file and line, list what you did not check, report observations not verdicts (`skills/herd/roles/reviewer.md`, `skills/herd/roles/worker.md`) | first bullet, "saying what was checked" | examples/reader/CLAUDE.md |

## 🟩 Keep: 5 rules, 1 skill
| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| 1 | Stop only the processes you started, by process id, never by port (`skills/herd/roles/worker.md`) | rule | 🟩 |
| 2 | Never simplify away validation at a trust boundary, error handling that prevents data loss, or a security measure (`skills/herd/roles/worker.md`) | rule | 🟩 |
| 3 | Before starting from an old brief, check what changed since it was written. If its premise moved, show what changed and wait, do not build the old version (`skills/queue/SKILL.md`, ready check) | rule | 🟩 |
| 4 | Ask before starting anything that costs money while it runs, such as a reviewer session (`skills/herd/SKILL.md`, `skills/herd/roles/worker.md`) | rule | 🟩 |
| 5 | A diff that restructures code and changes behaviour together is a finding: split the refactor out (`skills/herd/roles/reviewer.md`) | rule | 🟩 |
| 6 | Hand off a session in steps: the leaver writes a brief of what the tracker does not hold, the successor reads it back, the staying partner checks it before the new session takes over (`skills/herd/roles/handoff.md`) | skill | 🟩 |

## 🗑️ Dropped
`herder voice and cat names (skills/herder/SKILL.md)` · `overheard block and "For you:" line (skills/queue/SKILL.md)` · `Field Trip phone rules and dictation reading (skills/queue/SKILL.md)` · `/meow wrapper (commands/meow.md)` · `default model for started sessions (skills/herd/SKILL.md)` · `associate role and domains (skills/herd/roles/associate.md)` · `Cursor rule file (rules/cat-herder.mdc)` · `queue setup, move, peer and transfer (skills/queue/SKILL.md)` · `capture levels, sizing, rigor, topics (skills/capture/SKILL.md)` · `question ledger (skills/queue/SKILL.md)` · `hikes, grooming, introspection, supervisor (skills/herd/SKILL.md)` · `deprecation markers (skills/herd/roles/worker.md)` · `rescue session and idea-dump mode (skills/capture/SKILL.md)` · `launcher and clone folder rules (skills/herd/SKILL.md)` · `--force and state-field rules (skills/queue/SKILL.md)`

## 🧩 What it installs

| surface | when | reaches subagents | size |
|---|---|:--:|--:|
| Skill descriptions: capture, herd, herder, queue | listed every session | no (likely) | about 2.3 KB |
| Skill bodies: the same four | when triggered, for example "fix this" in a repo with a queue loads capture | no (likely) | 67.9 KB |
| Role files under `skills/herd/roles/` | when a pair, hike or handoff starts | no (likely) | 29.8 KB |
| `/meow` command (`commands/meow.md`) | only when the user types it (`disable-model-invocation`) | no | 1.4 KB |
| Hook PreCompact, matcher auto (`hooks/claude-codex.json`) | before an automatic compaction; network write for a rostered session | no (likely) | none injected |
| Hook SessionStart, matcher compact (`hooks/claude-codex.json`) | after a compaction; one or two lines to the model for a rostered session | no (likely) | under 0.3 KB |
| Hook SessionEnd (`hooks/claude.json`) | at session end; local state write only | no (likely) | none injected |

## ✅ Do this
- ⬜ 1. Do not install. Copy rules 1 to 5 from the Keep grid into `examples/reader/rules/engineering.md`, matching its numbered, bold-lead style. See the patch below.
- ⬜ 2. If you want the handoff routine, write it as a small skill (name below). Do not take the plugin for it.
- ⬜ 3. Install the plugin only if you decide to run a git-backed work queue with paired reviewers. That is a separate decision from these rules, and it adds git pushes to a queue branch and a state folder.

Case: the plugin has hooks, and they inject only after a compaction on a roster session, so the always-on cost is small. The five rules and the one skill are light enough to copy as text, which is cheaper than a plugin whose real product (the queue) the reader does not use.

## 📋 Proposed rules patch
Target file: `examples/reader/rules/engineering.md`. It is a short numbered list of rules, each with a bold lead, so the new rules continue that list as 8 to 12. I did not read any other file for placement, and a section split is not needed at this length. Not applied.

```diff
 7. **Commit messages:** imperative subject under 60 characters, then why.
+8. **Stop only the processes you started,** by process id, never by port.
+9. **Do not simplify away safeguards.** Keep validation at trust boundaries, error handling that prevents data loss, and security measures.
+10. **Check an old brief before building from it.** See what changed since it was written. If its premise moved, say what changed and wait for me.
+11. **Ask before starting anything that costs money while it runs,** such as another agent session.
+12. **Keep refactors and behaviour changes in separate diffs.** When a review finds both mixed, send the refactor back as its own change.
```

Proposed skill (the name is my proposal, the target does not name it): `session-handoff` · "Hand a long task to a fresh session: write a brief of what the tracker does not hold, have the successor read it back, and have a partner check it before the new session takes over." The dossier shows the reader keeps one personal skill, `examples/reader/skills/release-notes/SKILL.md`, so a skill folder next to it is the natural home. The choice is the reader's.

**Key:** 🟥 high · 🟧 medium · 🟨 partly · 🟩 keep · ⬜ covered · ⬛ dropped · ⛔ conflict · 🔁 duplicate · 🆕 new · ⭐ standout · ✅ done · ❓ unknown
