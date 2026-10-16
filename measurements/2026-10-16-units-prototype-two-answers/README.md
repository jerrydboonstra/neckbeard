# The units prototype with two answers per section

`tools/vet --units` at `c5ae5ee`: each section gets a `skill` answer (keep or drop) and a `rules` answer (conflict, new-standing, new-skill-text, duplicate, none), so a kept skill's general rules are still offered to copy. Sonnet, run on the Mac through testslot (the agentbay hold), judge on the Mac's own config, so these ten runs compare with each other, not exactly with the agentbay runs.

| target | one answer per section (agentbay) | two answers per section (Mac) |
|---|---|---|
| Cat Herder 0.40.3 | INSTALL 5 of 5, nothing to copy | INSTALL WITH CHANGES 3 of 5, INSTALL 2 of 5; 3 to 6 rules to copy in every run |
| Cat Herder 0.53.2 | INSTALL WITH CHANGES 2 of 2, nothing to copy | INSTALL WITH CHANGES 5 of 5; 3 to 8 rules to copy |

The skill answer is steady: 30 of 33 and 62 of 64 sections the same in every run. The rules answer is not: 26 of 33 and 50 of 64.

## The flip that is left

On 0.40.3 one section decides it: `skills/herd/roles/reviewer.md > Limits`. Runs 1, 4 and 5 quote "You may try the same action, on your own judgement, and report the result" (a reviewer retrying an action the worker was refused) against the reader's "never run anything destructive without my explicit go-ahead", a conflict. Runs 2 and 3 answer about another sentence in the same section (none, or the rule that a relayed approval lapses) and never reach that one. The written tests say "pick the first that applies", and the judge stops at the first rule it reads instead of checking every sentence for a conflict.

## Next

Ask about conflicts on their own, before anything else: a `conflicts` list per section (every sentence that breaks a reader rule, with both quotes, empty when none), separate from the one `rules` answer that fills the copy list. Then measure five runs on 0.40.3 again.
