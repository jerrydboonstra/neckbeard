# Contributing

Issues and pull requests are welcome. neckbeard is small and has a few rules that keep it trustworthy.

- **Standard library only.** No dependencies, so there is nothing to vet before vetting a plugin.
- **Run `make check` before you push.** It runs `skills/neckbeard/selfcheck.py`; CI runs the same thing on Python 3.11 to 3.13.
- **A new check must be seen to fail.** Break the code it guards, run `make check`, watch that case go red, then restore the code. A check nobody has seen fail is a claim, not a check. Say in the pull request how you broke it.
- **Every read from a target goes through the containment guard** (`_within` in `inventory.py`). The target is untrusted by definition.
- **Never commit a dossier or an evaluation.** They contain the reader's private rules. The `.gitignore` blocks JSON for this reason.
- **A release bumps the version in both manifests**, `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`, and adds a `CHANGELOG.md` entry. Installed copies are cached by version, so a change shipped under an unchanged number never reaches them. `make release` checks this.

## Merging several branches

Releases collect many branches, so build each one to merge cleanly. These rules came from Cat Herder's.

- **Add to a list one entry per line, sorted, with a trailing comma in multi-line Python lists and dicts.** Two branches that each add an entry then touch different lines. A list whose order carries meaning (the self-check sections) stays in order.
- **Find things by looking, not by registering.** `make check` runs every `tools/test_*.py`, so a new test file needs no Makefile edit. Do the same wherever a central list could be a glob.
- **Keep a pure list mergeable.** `.gitattributes` sets `merge=union` for `CHANGELOG.md`. Write each entry as one line under `## Unreleased` and never edit another branch's entry.
- **Put new behaviour in a new function or a new file**, and call it with one line, rather than growing a long function in place. `inventory.py` and `selfcheck.py` are the big shared files; add a function, not a paragraph of lines in the middle of one.
- **No drive-by edits in a shared file.** Do not reformat, re-sort or reword lines the change does not need.
- **Items that touch the same hot file go one after another.** `SKILL.md` is one: a single change at a time, because each edit also needs a fresh run of the held-out check.
- **Only a release bumps the version.** A branch never edits `plugin.json` or `marketplace.json` or adds a version heading to the changelog.
- **Keep paragraphs short in docs that many branches edit.** A paragraph is one line, so two edits to it conflict.

Changes to how the skill judges rules (`SKILL.md`) are the hardest to test; see [CASE-STUDIES.md](CASE-STUDIES.md) for how that half is evaluated, and expect a discussion before such a change is merged.
