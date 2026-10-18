# neckbeard ledger

reader: neckbeard v1.14.0, examples/reader
target: cat-herder 0.53.2

Cat Herder's first ledger, the worked example for [PLUGIN-GUIDE.md](../../PLUGIN-GUIDE.md). It was written from a scan of Cat Herder 0.53.2 and five neckbeard runs on it, and each stance was agreed with Cat Herder's owner. Line numbers are at the [v0.53.2 tag](https://github.com/jerrydboonstra/cat-herder/tree/v0.53.2). In Cat Herder's own repo this file would be `docs/neckbeard-ledger.md`.

| rule | stance | where it shows, or why | agreed |
|---|---|---|---|
| engineering 1 | comply | reuse the repo, then the standard library, then the platform, then an installed dependency (`skills/herd/roles/worker.md:93`) | |
| engineering 2 | comply | a bug fix finds every caller and fixes the cause once (`skills/herd/roles/worker.md:95`) | |
| engineering 3 | comply | the reviewer checks that new tests fail without their fixes (`skills/herd/roles/reviewer.md:38`) | |
| engineering 4 | open | no run counted a conflict, but three passages state an action with no bounds and are the likeliest to flip: "Act first, report after" (`skills/herd/SKILL.md:63`), "start the agent either way" (`skills/herd/SKILL.md:47`), "Act on every stall in that pass" (`skills/herd/roles/orchestrator.md:15`). Fix: Cat Herder item `bound-act-passages` | owner, 2026-10-17 |
| engineering 5 | comply | a deliberate corner gets a debt comment, in the marker the project's own rules name (`skills/herd/roles/worker.md:97`) | |
| engineering 6 | open | swarm instructions name `claude-haiku-5-5` when sending subagents (`skills/herd/roles/worker.md:34`, `:43`; `skills/herd/roles/orchestrator.md:25`; `skills/herd/roles/reviewer.md:36`), flagged in all five runs. Fix: Cat Herder item `swarm-agents-pin-model`, pinned agent definitions sent by name. Agent files load in Claude Code only, so on other hosts this row becomes an exception once the fix ships | owner, 2026-10-15 |
| engineering 7 | exception | Cat Herder words a commit by what changed, on purpose; the worker's sample is `pairs.md: the nested-thread sentence reworded` (`skills/herd/roles/worker.md:30`, `skills/herd/SKILL.md:76`) | owner, 2026-10-17 |
| safety 1 | comply | remote-branch cleanup runs as a dry run, then only on the owner's go-ahead (`skills/herd/SKILL.md:59`); an irreversible command heard by sound is read back first (`skills/queue/sections/field-trip.md:15`) | |
| safety 2 | comply | the queue goes on its own branch, never the code's (`skills/queue/sections/setup.md:7`) | |
| safety 3 | comply | no skill runs a deploy; the herd only respawns after the owner's `make deploy` (`skills/herd/SKILL.md:60`) | |
| safety 4 | comply | a done note replaces a secret with `<redacted>` and says so, and never holds credentials or tokens (`skills/herd/roles/worker.md:87`) | |
| safety 5 | open | the same three passages as engineering 4, read against "ask when the wrong reading is costly". Fix: `bound-act-passages` | owner, 2026-10-17 |
| answers | comply | "A verdict is never silence", and every accept lists what the reviewer didn't check (`skills/herd/roles/reviewer.md:88`) | |
| release-notes | n/a | Cat Herder's release summary can duplicate the reader's skill but doesn't contradict it | |
| cost | exception | SessionStart fires on `startup\|resume\|compact` (`hooks/claude-codex.json:18`), up from `compact` alone at 0.47.1: a role line at each start and resume, under 1 KB. The role line is wanted | owner, 2026-10-17 |
| reach | comply | no SubagentStart hook and no agents | |
| leaves state | exception | SessionEnd notes the session in this machine's state (`hooks/claude.json`), and PreCompact counts a compaction in the queue's roster (`hooks/claude-codex.json`). A git queue keeps state by design | owner, 2026-10-17 |
| live surface | exception | the hooks run the plugin's own `meow`, and PreCompact can push to the queue's git remote. A git queue pushes by design | owner, 2026-10-17 |
| refused reads | comply | none | |
