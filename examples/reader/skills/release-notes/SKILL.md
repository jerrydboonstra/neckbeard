---
name: release-notes
description: Draft release notes from the commits since the last tag, grouped by user-visible change, for the user to edit. Never publishes.
---

# release-notes

Read `git log <last-tag>..HEAD`. Group changes into Added, Changed, Fixed. Write
one line per change in terms a user would notice, not in terms of files. Leave
internal refactors out unless they change behaviour. Show the draft and stop.
