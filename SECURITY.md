# Security

## The threat model

Neckbeard exists to be pointed at code you have not decided to trust yet. That is the whole point, and it shapes everything below.

**It never executes the target.** It reads files and parses manifests. It does not run hooks, import the plugin's code, invoke its build, or start an MCP server. A plugin that is malicious is still only ever text to this tool.

**The script writes in two places and nowhere else**: the path given to `--out`, and a temporary clone directory when the target is a git URL. The skill also writes one file, the evaluation, and checks first that git ignores its path. It does not edit your rules files, your settings, or the plugin it is reading, and it never uninstalls anything.

**It reads your rules in order to compare against them.** That is how it tells duplicate from conflict. Those rules are private, and they end up in the evaluation it writes.

## Handle the output as private

An evaluation contains your own rules, quoted. On this project that was a real defect rather than a hypothetical: an evaluation could carry tens of kilobytes of private configuration into a repo whose ignore rules did not cover it. The fix has two layers, and both are still here. The shipped `.gitignore` denies JSON by default and allows only the two manifests, and every write prints a warning to stderr saying what the file contains.

**If you run this in a repo you publish, check that your ignore rules cover wherever you send `--out`, and the `evaluations/` directory the skill writes into.** Neckbeard's own `.gitignore` protects neckbeard's repo and nothing else. You will usually run it from inside some other project, and that project's ignore rules are the ones that count. The tool cannot know where you point it.

## Known boundary

Every file the tool reads from a target is resolved, symlinks included, and checked for containment first: skills, commands, agents, the hooks file, hook scripts and what they inject, `plugin.json`, `.mcp.json`, a root `CLAUDE.md` and every file it imports with `@path`, and the README. A file that resolves outside the target is refused and the dossier says so. So is a path the target names for itself, such as `"hooks": "../../elsewhere.json"` in `plugin.json`.

This paragraph used to make the same claim when only three read paths checked. An adversarial review on 2026-09-24 found five more open, and all eight now go through one guard. Commands, agents, a root `CLAUDE.md` and its imports were added to the tool later, behind the same guard. `selfcheck.py` now plants a marker outside the target for each path and fails if it reaches the dossier, and each check has been seen to fail with its guard removed.

## Reporting

Open an issue at https://github.com/jerrydboonstra/neckbeard/issues. For anything you would rather not post publicly, use GitHub's private vulnerability reporting on the same repository.

Only the latest release is supported. There is no support commitment here. This is a small tool maintained by one person, and a report may sit for a while. It will not be ignored.
