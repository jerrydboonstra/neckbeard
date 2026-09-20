# Security

## The threat model

Neckbeard exists to be pointed at code you have not decided to trust yet. That
is the whole point, and it shapes everything below.

**It never executes the target.** It reads files and parses manifests. It does
not run hooks, import the plugin's code, invoke its build, or start an MCP
server. A plugin that is malicious is still only ever text to this tool.

**It writes in two places and nowhere else**: the path given to `--out`, and a
temporary clone directory when the target is a git URL. It does not edit your
rules files, your settings, or the plugin it is reading, and it never uninstalls
anything.

**It reads your rules in order to compare against them.** That is how it tells
duplicate from conflict. Those rules are private, and they end up in the
evaluation it writes.

## Handle the output as private

An evaluation contains your own rules, quoted. On this project that was a real
defect rather than a hypothetical: an evaluation could carry tens of kilobytes
of private configuration into a repo whose ignore rules did not cover it. The
fix has two layers, and both are still here. The shipped `.gitignore` denies
JSON by default and allows only the two manifests, and every write prints a
warning to stderr saying what the file contains.

**If you run this in a repo you publish, check that your ignore rules cover
wherever you send `--out`.** The tool cannot know where you point it.

## Known boundary

Symlinks inside a plugin are resolved and checked for containment before a file
is read. A skill file symlinked to something outside the plugin root is refused.
This was added after an audit demonstrated the escape, so it is a guard that has
been seen to fail rather than one that has only been written.

## Reporting

Open an issue at https://github.com/jerrydboonstra/neckbeard/issues. For anything
you would rather not post publicly, use GitHub's private vulnerability reporting
on the same repository.

There is no support commitment here. This is a small tool maintained by one
person, and a report may sit for a while. It will not be ignored.
