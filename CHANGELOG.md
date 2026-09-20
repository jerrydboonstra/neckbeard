# Changelog

**Everything below 1.11.2 was pre-release and never published.** The version
number is high for a first release because the tool was rewritten fifteen times
in thirty-one hours, each time because something found a defect in it. Those
numbers are kept rather than collapsed to 1.0.0, since the plugin cache is keyed
to version and 1.0.0 already refers to different content.

What each round cost the tool is written up in `CASE-STUDIES.md`. This file is
the short version.

## 1.11.2 (2026-09-19)

First public release.

Recorded how the last claim resting on the author's own account was closed. The
judgment half, the instructions that sort a plugin's rules into duplicate,
conflict and new, has no filesystem to check it against. An outside auditor
built a held-out fixture, sealed the ground truth before running anything,
pre-registered a rubric, and graded its own six evaluations. The author has
never seen it.

## 1.11.1 (2026-09-19)

Recorded the lesson from the first re-audit that came back clean: a real
third-party plugin with an awkward hook wrapper caught a defect that 39 catalog
plugins and 13 purpose-built fixtures all missed.

## 1.11.0 (2026-09-19)

**Fixed a regression introduced by the previous fix.** The 1.9.0 change narrowed
hook-command resolution to a short extension allowlist, which silenced a real
plugin entirely instead of reporting that it could not resolve the command.
Worse, it shipped alongside a sentence claiming silence meant nothing to inject.
Hook commands now report in three buckets: resolved, unresolved, and absent.

## 1.10.0 (2026-09-19)

Tested the judgment half against a hard fixture with several overlapping rule
sources, and fixed a silence it exposed.

## 1.9.0 (2026-09-19)

First test of the judgment half at all. Fixed three defects in the instructions,
including a step that named a rules-file section heading that only existed on
the author's own machine.

## 1.8.0 (2026-09-19)

Closed the remaining audit findings and corrected three published numbers that
did not reproduce.

## 1.7.0 (2026-09-19)

Fixed five blocking findings from an independent audit, including a symlinked
skill file that escaped the plugin directory and was read and embedded.

## 1.6.0 (2026-09-19)

**Security.** Evaluations embedded the user's own rules verbatim, including
host names and private identifiers, into a file that a deny-by-default
`.gitignore` did not cover. Added the ignore rules and a runtime warning on
every write. Verified nothing had ever been committed.

## 1.5.0 (2026-09-19)

Closed the last unexercised branches in hook parsing: one crash, and one
confident wrong answer on a hooks file that does not parse. `has_hooks` became
three-state so "could not read that" stopped collapsing into "no".

## 1.4.0 (2026-09-19)

Attacked branches no real plugin exercises, using purpose-built directories.
Three bugs, including declared MCP servers reported nowhere at all.

## 1.3.0 (2026-09-19)

Swept all 39 of Anthropic's first-party plugins and fixed the bug that found.

## 1.2.0 (2026-09-19)

Fifth case study, against Anthropic's `claude-security`, and the two fixes it
forced.

## 1.1.0 (2026-09-19)

Corrected a claim about plugin caching that the tool disproved when run against
itself. Separated hook scripts from hook registrations, which are different
counts.

## 1.0.0 (2026-09-18)

Initial build. Replaced an unmeasured "zero cost" claim with the measured token
count.
