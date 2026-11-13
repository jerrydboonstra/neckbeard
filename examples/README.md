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
| [jerrydboonstra/neckbeard](neckbeard.md) 1.12.7, vetting itself (the labelled demo of a fit report) | 🟩 install | 0 | 2 | 1 | 1 |
| [calm-trader/skills](calm-trader-skills.md) @ 5a15cd2, a pack the author contributes to | 🟩 install | 0 | 2 | 4 | 10 |

neckbeard's fit report on itself is 🟩; it is kept here as the labelled demo of a fit report against the sample reader. neckbeard's own published report is [docs/neckbeard-report.md](../docs/neckbeard-report.md), which has no reader and no verdict, and its README badge links that. On 1.12.0 one run marked it down for its report format, a page that needs a nine-symbol key, against the sample reader's "plain language over jargon". Three separate runs on 1.12.7 found no conflict. The format did not change in between, so read the old finding as one run's call on a matter of taste, not as something fixed.

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

Or do all of it in one command from this repo: `tools/vet <path-to-target> <report.md>`. It builds the dossier against a throwaway copy of the reader (the judge writes into its config folder, so it never gets the real one), runs the judge in a separate `claude -p` session on Sonnet, puts a "What it adds" section above the report's At a glance (what the target injects, reaches and leaves behind, written by `tools/part1` from the dossier with no reference to your rules), and checks that the report has a verdict and names no local path. Where the judge can't log in with the reader as its config folder, as on a Mac, it falls back to your own config and says so.

## Keep your plugin's published report current

A plugin's published report is the facts report: what the plugin adds to a session, with no reader, no verdict and no model call, so it needs only python3 and no login. A fit report against the sample reader, like the ones in this gallery, is a demo of what a local run prints, never a plugin's published verdict, because it depends on a reader's rules that a stranger does not have.

Write it with a clone of neckbeard and one command in your plugin's folder:

```bash
git clone --depth 1 --branch v1.17.0 https://github.com/jerrydboonstra/neckbeard /tmp/nb
/tmp/nb/tools/vet . docs/neckbeard-report.md --facts
```

The report is the title `# 🔍 <name> <version> · what it adds`, a header line (date, neckbeard version, source, version, commit), the "What it adds" section written by `tools/part1` from the dossier, and one closing line saying no reader's rules were read. If the session's checkout is a private copy of your plugin, add `--repo https://github.com/<you>/<plugin>` so the report links the public repo. `--facts` takes `--repo` and no other option.

It also prints one Markdown badge line as the last line of its output, linked to the report's path as you gave it. Paste it into your README. The message is your plugin's version and how much of the plugin neckbeard could read, from the dossier's read states alone:

| the badge says | colour | when |
|---|---|---|
| neckbeard report \| 1.2.3 · read in full | brightgreen | every section was read or does not apply |
| neckbeard report \| 1.2.3 · partly read | yellow | at least one section was read in part, and none failed |
| neckbeard report \| 1.2.3 · something unread | red | at least one section could not be read |

Every gap counts toward the colour, whether the gap is neckbeard's limit or the plugin's own. The report behind the badge lists each one, so a reader can tell which it is.

A release can leave the report describing an older version. `tools/vet --check REPORT TARGET` catches that: it compares the version in the report's header with the one in your `plugin.json` and fails when they differ. It needs only python3, so it fits in CI. As a GitHub Actions job, with the neckbeard tag pinned:

```yaml
neckbeard-report:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - run: git clone --depth 1 --branch v1.17.0 https://github.com/jerrydboonstra/neckbeard /tmp/nb
    - run: /tmp/nb/tools/vet --check docs/neckbeard-report.md .
```

neckbeard guards its own release the same way: `make report` regenerates `docs/neckbeard-report.md`, and `make release` runs `make report-check` first, which checks the report as it is in the tagged tree. Commit the regenerated report before you tag, since a tag set before it is refused.

The rest of this page covers the fit report, which is for your own use.

`tools/vet --reader DIR` vets against your own rules instead of the sample reader. DIR is laid out as a Claude config folder (a `CLAUDE.md`, `rules/`, `skills/`). The report's header then carries a `Baseline:` line naming the folder, how many rule files the inventory read in it, their bytes and a 12-character fingerprint of their relative paths and contents, so the same rules in another folder give the same fingerprint, and a list of the relative paths. The default sample reader gets the same line, so every report now has one. The title and the verdict paragraph name the folder too, and print no path of it. The folder is the config folder of the judge's session, so its `settings.json` hooks would run: pass only a folder you trust. If the inventory finds no rule files in DIR there is nothing to judge against: vet prints why and writes the `--facts` report instead.

A fit report is built by a judge running in a Claude Code session, for example on a plugin's repo in a Claude Code web session on your own subscription, where the judge is logged in from the environment and starts with the sample reader as its only rules. Sonnet is enough for the session itself, since it only runs the command. Keep the judge on Sonnet: in a side-by-side run on 2026-10-04, a Haiku judge finished in under a minute but missed both conflicts and all nine covered rules that the Sonnet judge found and that checked out against the files. A full run takes two to three minutes.

For a private copy of the plugin, add `--repo https://github.com/<you>/<plugin>` so the report links the public repo, and `--note "..."` for a sentence of your own before the verdict's disclaimer, such as saying you wrote both. `tools/vet` sets the report's title line itself, so it always names the reader the verdict is against.

## How these were made

Each report was written by a separate model session (Claude Sonnet) that saw only the dossier and the target's files, and was told to ignore everything else in its context. Every report was then checked: the counts in "How its rules sorted" equal the rows in the grids, every citation points at a real reader file, and the inventory confirmed that only the sample reader was read. The calm-trader/skills report failed that check as first written: it counted 9 dropped items against 10 listed, said four hard stops where the reader has five, and named the wrong neckbeard version. Those three were corrected by hand, and its em dashes were removed to match the rest of the gallery; every other claim in it was checked against the repo and left as the session wrote it.
