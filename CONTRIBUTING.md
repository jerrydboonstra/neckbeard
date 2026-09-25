# Contributing

Issues and pull requests are welcome. neckbeard is small and has a few rules that keep it trustworthy.

- **Standard library only.** No dependencies, so there is nothing to vet before vetting a plugin.
- **Run `make check` before you push.** It runs `skills/neckbeard/selfcheck.py`; CI runs the same thing on Python 3.11 to 3.13.
- **A new check must be seen to fail.** Break the code it guards, run `make check`, watch that case go red, then restore the code. A check nobody has seen fail is a claim, not a check. Say in the pull request how you broke it.
- **Every read from a target goes through the containment guard** (`_within` in `inventory.py`). The target is untrusted by definition.
- **Never commit a dossier or an evaluation.** They contain the reader's private rules. The `.gitignore` blocks JSON for this reason.
- **A release bumps the version in both manifests**, `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`, and adds a `CHANGELOG.md` entry. Installed copies are cached by version, so a change shipped under an unchanged number never reaches them. `make release` checks this.

Changes to how the skill judges rules (`SKILL.md`) are the hardest to test; see [CASE-STUDIES.md](CASE-STUDIES.md) for how that half is evaluated, and expect a discussion before such a change is merged.
