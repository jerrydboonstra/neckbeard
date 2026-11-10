# The units prototype, measured

`tools/vet --units` (branch `bugfix/verdict-prototype-units`): the judge sorts every numbered section of the target by the written tests in `tools/vet-units.md`, and `tools/units-verdict` computes the verdict. Sonnet, the same host and judge setup as `../2026-10-15-vet-stability/` and `../2026-10-16-vet-stability-0.40.3/`.

| target | baseline (1.14.0) | units prototype |
|---|---|---|
| Cat Herder 0.40.3 | COPY RULES 3 of 5, INSTALL 2 of 5 | INSTALL 5 of 5; 31 of 33 sections judged the same in every run |
| Cat Herder 0.53.2 | COPY RULES 5 of 5; conflicts by rule 5, 2, 2, 1 of 5 | INSTALL WITH CHANGES 2 of 2 (runs 3 to 5 held for agentbay); 4 conflicts in both; 63 of 64 sections the same |

The sections that split: `skills/herd/roles/handoff.md > Handing off to a new session` and `skills/herd/roles/reviewer.md > Setting up` (in both targets), each between install-skill and dropped.

What it costs: every rule-bearing section of a kept skill lands in install-skill, so the report no longer proposes rules to copy as text (new standing 0 in every run). The verdict moves on 0.53.2 because of the owner's rule (keep a plugin's own workflow skills whenever they work as shipped), not because of noise.
