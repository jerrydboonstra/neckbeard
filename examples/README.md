# Gallery

Real neckbeard reports on eight public plugins and skill packs, all run against the same [sample reader](reader/): six on 1.12.0 on 2026-09-24, calm-trader/skills on 1.12.2, and neckbeard itself on 1.12.7 on 2026-10-01. Each row links to the full report.

| plugin | verdict | ⛔ conflicts | 🔁 covered | 🆕 new | 🗑️ dropped |
|---|---|:--:|:--:|:--:|:--:|
| [DietrichGebert/ponytail](ponytail.md) 4.10.0 | 🟨 copy rules, skip plugin | 2 | 5 | 4 | 5 |
| [obra/superpowers](superpowers.md) 6.4.1 | 🟧 install with changes | 2 | 2 | 10 | 2 |
| [anthropics/claude-plugins-official: claude-security](claude-security.md) 0.11.0 | 🟧 install with changes | 1 | 3 | 6 | 6 |
| [addyosmani/agent-skills](agent-skills.md) 0.6.10 | 🟩 install | 0 | 1 | 37 | 1 |
| [github/spec-kit](spec-kit.md) 1.0.12.dev0 | 🟨 copy rules, skip plugin | 1 | 1 | 2 | 0 |
| [Koz-TV/viral-launch-pipeline](viral-launch-pipeline.md) 1.0.0 | 🟩 install | 0 | 2 | 4 | 4 |
| [jerrydboonstra/neckbeard](neckbeard.md) 1.12.7, vetting itself | 🟩 install | 0 | 2 | 1 | 1 |
| [calm-trader/skills](calm-trader-skills.md) @ 5a15cd2, a pack the author contributes to | 🟩 install | 0 | 2 | 4 | 10 |

neckbeard's report on itself is 🟩, and its README shows that badge. On 1.12.0 one run marked it down for its report format, a page that needs a nine-symbol key, against the sample reader's "plain language over jargon". Three separate runs on 1.12.7 found no conflict. The format did not change in between, so read the old finding as one run's call on a matter of taste, not as something fixed.

calm-trader/skills is a skill pack the author of neckbeard contributes to, so its row is the same kind of conflict of interest as the self-vetting one. It is included with the other maintainer's agreement, and its report says so at the top.

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

Or do all of it in one command from this repo: `tools/vet <path-to-target> <report.md>`. It builds the dossier against a throwaway copy of the reader (the judge writes into its config folder, so it never gets the real one), runs the judge in a separate `claude -p` session on Sonnet, and checks that the report has a verdict and names no local path. Where the judge can't log in with the reader as its config folder, as on a Mac, it falls back to your own config and says so.

## Keep your plugin's published report current

If your plugin publishes a neckbeard report, a release can leave it vetting an older version. `tools/vet --check REPORT TARGET` catches that: it compares the version in the report's header with the one in your `plugin.json` and fails when they differ. It needs only python3, no Claude and no login, so it fits in CI. As a GitHub Actions job, with the neckbeard tag pinned:

```yaml
neckbeard-report:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - run: git clone --depth 1 --branch v1.13.0 https://github.com/jerrydboonstra/neckbeard /tmp/nb
    - run: /tmp/nb/tools/vet --check docs/neckbeard-report.md .
```

When it fails, rebuild the report in a Claude Code web session on your plugin's repo, on your own subscription:

```bash
git clone --depth 1 https://github.com/jerrydboonstra/neckbeard /tmp/nb
/tmp/nb/tools/vet . docs/neckbeard-report.md
```

A web session logs the judge in from its environment, so the judge starts with the sample reader as its only rules. Sonnet is enough for the session itself, since it only runs the command. Keep the judge on Sonnet: in a side-by-side run on 2026-10-04, a Haiku judge finished in under a minute but missed both conflicts and all nine covered rules that the Sonnet judge found and that checked out against the files. A full run takes two to three minutes.

If the session's checkout is a private copy of your plugin, add `--repo https://github.com/<you>/<plugin>` so the report links the public repo, and `--note "..."` for a sentence of your own before the verdict's disclaimer, such as saying you wrote both. `tools/vet` sets the report's title line itself, so it always says the verdict is against the sample reader.

## How these were made

Each report was written by a separate model session (Claude Sonnet) that saw only the dossier and the target's files, and was told to ignore everything else in its context. Every report was then checked: the counts in "How its rules sorted" equal the rows in the grids, every citation points at a real reader file, and the inventory confirmed that only the sample reader was read. The calm-trader/skills report failed that check as first written: it counted 9 dropped items against 10 listed, said four hard stops where the reader has five, and named the wrong neckbeard version. Those three were corrected by hand, and its em dashes were removed to match the rest of the gallery; every other claim in it was checked against the repo and left as the session wrote it.
