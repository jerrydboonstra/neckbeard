# neckbeard ledger

reader: neckbeard v1.14.0, examples/reader
target: cat-herder 0.53.2

Cat Herder's first ledger, the worked example for [PLUGIN-GUIDE.md](../../PLUGIN-GUIDE.md). It was written from a scan of Cat Herder 0.53.2 and the conflicts five neckbeard runs on it counted, and Cat Herder's owner agreed each exception and open row. Line numbers are at the [v0.53.2 tag](https://github.com/jerrydboonstra/cat-herder/tree/v0.53.2). In Cat Herder's own repo this file would be `docs/neckbeard-ledger.md`.

neckbeard 1.14.0 can't tie Cat Herder's three hook commands to a file (they run `${CLAUDE_PLUGIN_ROOT:-${PLUGIN_ROOT}}/bin/meow`), so it lists them as unidentifiable. The cost, leaves state and live surface rows come from reading the hooks, not from a traced run.

| rule | stance | files | where it shows, or why | agreed |
|---|---|---|---|---|
| engineering 1 | comply | `skills/herd/roles/worker.md` | reuse the repo, then the standard library, then the platform, then an installed dependency (line 93) | |
| engineering 2 | comply | `skills/herd/roles/worker.md` | a bug fix finds every caller and fixes the cause once (line 95) | |
| engineering 3 | comply | `skills/herd/roles/reviewer.md` | the reviewer checks that new tests fail without their fixes (line 38) | |
| engineering 4 | open | `skills/herd/SKILL.md`, `skills/herd/roles/orchestrator.md` | runs 2 and 3 counted a conflict on "run `meow herd respawn <your who>` when `make deploy` says to, unasked" (SKILL.md:60). By reading, three more passages state an action with no bounds and are likely to flip: "Act first, report after" (SKILL.md:63), "start the agent either way" (SKILL.md:47), "Act on every stall in that pass" (orchestrator.md:15). Fix: Cat Herder item `bound-act-passages` | owner, 2026-10-17 |
| engineering 5 | comply | `skills/herd/roles/worker.md` | a deliberate corner gets a debt comment, in the marker the project's own rules name (line 97) | |
| engineering 6 | open | `skills/queue/SKILL.md`, `skills/herd/roles/worker.md`, `skills/herd/roles/orchestrator.md`, `skills/herd/roles/reviewer.md` | grooming hands work "to agents on the cheapest capable model your host offers" (queue SKILL.md:60), counted in all five runs; swarm instructions name `claude-haiku-5-5` when sending subagents (worker.md:34 and 43, orchestrator.md:25, reviewer.md:36), counted in runs 1, 3, 4 and 5; run 1 also counted the escalated-item advisor passing `claude-fable-5-1` (orchestrator.md:27). Fix: Cat Herder item `swarm-agents-pin-model`, pinned agent definitions sent by name. Agent files load in Claude Code only, so other hosts will still name a model once the fix ships | owner, 2026-10-15 |
| engineering 7 | exception | `skills/herd/roles/worker.md`, `skills/herd/SKILL.md` | Cat Herder words a commit by what changed, file first, with no agent or session names: the worker's sample is `pairs.md: the nested-thread sentence reworded` (worker.md:30, SKILL.md:76) | owner, 2026-10-17 |
| safety 1 | comply | `skills/herd/SKILL.md`, `skills/queue/sections/field-trip.md` | remote-branch cleanup runs as a dry run, then only on the owner's go-ahead (SKILL.md:59); an irreversible command heard by sound is read back first (field-trip.md:15) | |
| safety 2 | comply | `skills/queue/sections/setup.md` | the queue goes on its own branch, never the code's (line 7) | |
| safety 3 | comply | `skills/herd/SKILL.md` | no skill runs a deploy; the herd only respawns after the owner's `make deploy` (line 60) | |
| safety 4 | comply | `skills/herd/roles/worker.md` | a done note replaces a secret with `<redacted>` and says so, and never holds credentials or tokens (line 87) | |
| safety 5 | open | `skills/herd/SKILL.md`, `skills/herd/roles/orchestrator.md`, `lib/cat_herder/names.py`, `docs/reference.md` | run 2 counted "Act first, report after" (SKILL.md:63); run 5 counted the standing rule "never ask the owner while they're away", where an ask's reversible default stands after its deadline (names.py:933 to 934, reference.md:750, 752 and 764). The other passages under engineering 4 read the same way. Fix: `bound-act-passages` | owner, 2026-10-17 |
| answers | comply | `skills/herd/roles/reviewer.md` | "A verdict is never silence", and every accept lists what the reviewer didn't check (line 88) | |
| release-notes | comply | | Cat Herder's release summary groups changes as the reader's skill does, and nothing in it contradicts the skill | |
| cost | exception | `hooks/claude-codex.json` | SessionStart fires on startup, resume and compact (line 18), up from compact alone at 0.47.1: a role line at each start and resume, under 1 KB. The role line is wanted | owner, 2026-10-17 |
| reach | comply | | no hook on an event that fires inside subagents | |
| leaves state | exception | `hooks/claude.json`, `hooks/claude-codex.json` | SessionEnd notes the session in this machine's state, and PreCompact counts a compaction in the queue's roster. A git queue keeps state by design | owner, 2026-10-17 |
| live surface | exception | `hooks/claude-codex.json` | the hooks run the plugin's own `meow`, and PreCompact can push to the queue's git remote. A git queue pushes by design | owner, 2026-10-17 |
| refused reads | comply | | none | |
