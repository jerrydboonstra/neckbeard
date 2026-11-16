# Contributing

Issues and pull requests are welcome. neckbeard is small and has a few rules that keep it trustworthy.

- **Standard library only.** No dependencies, so there is nothing to vet before vetting a plugin.
- **Run `make check` before you push.** It runs `skills/neckbeard/selfcheck.py`; CI runs the same thing on Python 3.11 to 3.13.
- **A new check must be seen to fail.** Break the code it guards, run `make check`, watch that case go red, then restore the code. A check nobody has seen fail is a claim, not a check. Say in the pull request how you broke it.
- **Every read from a target goes through the containment guard** (`_within` in `skills/neckbeard/inventory_core.py`). The target is untrusted by definition.
- **Never commit a dossier or an evaluation.** They contain the reader's private rules. The `.gitignore` blocks JSON for this reason.
- **Tests are plain scripts.** Each `tools/test_<name>.py` exits 0 when it passes, so `python3 tools/test_vet.py` runs one, and `skills/neckbeard/selfcheck.py` is the self-check. `make check` runs them all, plus `tools/excerpts --check`, which keeps the report quotes in `README.md` and `CASE-STUDIES.md` in step with the reports they copy from; after you regenerate a report, run `tools/excerpts`. `tests/map` lists which test modules a changed file selects. A new `tools/test_*.py` adds its own `tools/test_X.py test_X` line there, which a test enforces, and a line for each source file it covers.
- **A pull request says what changed and why**, has `make check` passing, shows the new check failing before the fix, and adds one line to `CHANGELOG.md`.
- **A release bumps the version in both manifests**, `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`, and adds a `CHANGELOG.md` entry. Installed copies are cached by version, so a change shipped under an unchanged number never reaches them. `make release` checks this.

## Merging several branches

Releases collect many branches, so build each one to merge cleanly.

- **Add to a list one entry per line, sorted, with a trailing comma in multi-line Python lists and dicts.** Two branches that each add an entry then touch different lines. A list whose order carries meaning (the self-check sections) stays in order.
- **Find things by looking, not by registering.** `make check` runs every `tools/test_*.py`, so a new test file needs no Makefile edit. Do the same wherever a central list could be a glob.
- **Keep a pure list mergeable.** `.gitattributes` sets `merge=union` for `CHANGELOG.md`. Write each entry as one line under `## Unreleased` and never edit another branch's entry.
- **Put new behaviour in a new function or a new file**, and call it with one line, rather than growing a long function in place. `selfcheck.py` and the `inventory*.py` modules are the shared files; add a function, not a paragraph of lines in the middle of one.
- **No drive-by edits in a shared file.** Do not reformat, re-sort or reword lines the change does not need.
- **Changes to the same hot file go one after another.** `SKILL.md` is one: take a single change at a time, because each edit needs a fresh judgment check. The maintainer reruns a private check before release.
- **Only a release bumps the version.** A branch never edits `plugin.json` or `marketplace.json` or adds a version heading to the changelog.
- **Keep paragraphs short in docs that many branches edit.** A paragraph is one line, so two edits to it conflict.

Changes to how the skill judges rules (`SKILL.md`) are the hardest to test; see [CASE-STUDIES.md](CASE-STUDIES.md) for how that half is evaluated, and expect a discussion before such a change is merged.
