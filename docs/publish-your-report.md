# Publish your plugin's report

This page is for a plugin author who wants a published report in the repo and a badge in the README. A reader who only wants to see reports should open the [gallery](../examples/README.md).

A plugin's published report is the facts report: what the plugin adds to a session, with no reader, no verdict and no model call, so it needs only python3 and no login. A fit report is a different thing: it needs a reader's own rules to judge against, so it is for your own use and is never a plugin's published verdict. The gallery has one, neckbeard's on itself, as a labelled demo.

Write it with a clone of neckbeard and one command in your plugin's folder:

```bash
git clone --depth 1 --branch v1.17.1 https://github.com/jerrydboonstra/neckbeard /tmp/nb
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
    - run: git clone --depth 1 --branch v1.17.1 https://github.com/jerrydboonstra/neckbeard /tmp/nb
    - run: /tmp/nb/tools/vet --check docs/neckbeard-report.md .
```

neckbeard guards its own release the same way: `make report` regenerates `docs/neckbeard-report.md`, and `make release` runs `make report-check` first, which checks the report as it is in the tagged tree. Commit the regenerated report before you tag, since a tag set before it is refused.

The rest of this page covers the fit report, which is for your own use.

`tools/vet --reader DIR` vets against your own rules instead of the sample reader. DIR is laid out as a Claude config folder (a `CLAUDE.md`, `rules/`, `skills/`). The report's header then carries a `Baseline:` line naming the folder, how many rule files the inventory read in it, their bytes and a 12-character fingerprint of their relative paths and contents, so the same rules in another folder give the same fingerprint, and a list of the relative paths. The default sample reader gets the same line, so every fit report has one. The title and the verdict paragraph name the folder too, and print no path of it. The folder is the config folder of the judge's session, so its `settings.json` hooks would run: pass only a folder you trust. If the inventory finds no rule files in DIR there is nothing to judge against: vet prints why and writes the `--facts` report instead.

A fit report is built by a **judge**, a separate Claude session that does the comparing, running in a Claude Code session, for example on a plugin's repo in a Claude Code web session on your own subscription, where the judge is logged in from the environment and starts with the sample reader as its only rules. On Linux without such a login, `tools/vet` copies your own login file into the throwaway reader for the run and deletes it with the folder; it skips the copy when the login is due to refresh within the hour (the default judge then falls back to your own config, while an explicit `--judge reader` stops and says why), and it refuses a report that holds the login's tokens. A judge that refreshes its copy can sign your own login out, and `tools/vet` says so when it sees that. Sonnet is enough for the session itself, since it only runs the command. Keep the judge on Sonnet: in a side-by-side run on 2026-10-04, a Haiku judge finished in under a minute but missed both conflicts and all nine covered rules that the Sonnet judge found and that checked out against the files. A full run takes two to three minutes.

For a private copy of the plugin, add `--repo https://github.com/<you>/<plugin>` so the report links the public repo, and `--note "..."` for a sentence of your own before the verdict's disclaimer, such as saying you wrote both. `tools/vet` sets the report's title line itself, so it always names the reader the verdict is against.
