# Gallery

Real neckbeard 1.12.0 reports on seven public plugins, all run against the same [sample reader](reader/) on 2026-09-24. Each row links to the full report.

| plugin | verdict | ⛔ conflicts | 🔁 covered | 🆕 new | 🗑️ dropped |
|---|---|:--:|:--:|:--:|:--:|
| [ponytail](ponytail.md) 4.10.0 | 🟨 copy rules, skip plugin | 2 | 5 | 4 | 5 |
| [obra/superpowers](superpowers.md) 6.4.1 | 🟧 install with changes | 2 | 2 | 10 | 2 |
| [claude-security](claude-security.md) 0.11.0 | 🟧 install with changes | 1 | 3 | 6 | 6 |
| [addyosmani/agent-skills](agent-skills.md) 0.6.10 | 🟩 install | 0 | 1 | 37 | 1 |
| [github/spec-kit](spec-kit.md) 1.0.12.dev0 | 🟨 copy rules, skip plugin | 1 | 1 | 2 | 0 |
| [viral-launch-pipeline](viral-launch-pipeline.md) 1.0.0 | 🟩 install | 0 | 2 | 4 | 4 |
| [neckbeard](neckbeard.md) 1.12.0, vetting itself | 🟧 install with changes | 1 | 2 | 1 | 1 |

## The verdicts are about fit, not quality

Every verdict says how a plugin fits **this sample reader's rules**. A conflict means the plugin tells the model to do something the reader's rules forbid, such as proceeding on a guess where the reader says to ask first. A different reader gets different verdicts from the same plugin. None of these pages is a judgment of the plugin or its authors.

## The sample reader

[`reader/`](reader/) is the "rules already in force" for a fictional developer, laid out the way a real Claude Code config is:

- [`CLAUDE.md`](reader/CLAUDE.md), which pulls in the other two with `@` imports
- [`rules/safety.md`](reader/rules/safety.md): five hard stops (nothing destructive without a go-ahead, never push to `main`, deploy only on "ship it", no secrets in output, ask when a wrong reading is costly)
- [`rules/engineering.md`](reader/rules/engineering.md): seven working rules (reuse first, fix causes, tests seen to fail, scope is the deliverable, and more)
- [`skills/release-notes/`](reader/skills/release-notes/SKILL.md): one personal skill

It is small on purpose, so every citation in a report can be checked by eye.

## Reproduce one

Clone the target, then point neckbeard's discovery at the sample reader instead of your own config, and at an empty project so no other `CLAUDE.md` is found:

```bash
P=$(mktemp -d)
CLAUDE_CONFIG_DIR="$PWD/examples/reader" \
  python3 skills/neckbeard/inventory.py <path-to-target> --project-dir "$P" --out "$P/dossier.json"
```

`current_rules` in the dossier should list exactly the four reader files. Then follow Steps 2 to 4 of [`SKILL.md`](../skills/neckbeard/SKILL.md) against that dossier. The classification is a model's judgment, so a rerun will not match word for word; the counts may move by an item or two, and a verdict that flips is worth reporting.

## How these were made

Each report was written by a separate model session (Claude Sonnet) that saw only the dossier and the target's files, and was told to ignore everything else in its context. Every report was then checked: the counts in "How its rules sorted" equal the rows in the grids, every citation points at a real reader file, and the inventory confirmed that only the sample reader was read.
