# Five vet runs on the target that flipped

Question: does the verdict still flip on neckbeard 1.14.0 for the target that flipped on 1.13.0, and through which stage?

Setup: neckbeard 1.14.0 (SKILL.md as released; `tools/vet-stability` as fixed on `bugfix/verdict-stability-runs`), target Cat Herder 0.40.3 at `8442cb6b` (a `git archive` export), Sonnet judge on the test host's own config (the sample reader could not log in there), `tools/vet-repeat TARGET OUT 5` under `testslot --track`. Same setup as `../2026-10-15-vet-stability/`. On 1.13.0 this target gave INSTALL, INSTALL, COPY RULES (2026-10-06).

## Result

`vet-stability.txt`: COPY RULES, SKIP PLUGIN in 3 of 5, INSTALL in 2 of 5. No run found a conflict.

## Where it flips

One judgment decides it: whether the reader would use the plugin's own workflow skills (`capture`, `queue`, `herd`).

- Runs 2 and 4 keep all three as new on-demand skills (new skill = 3), and the verdict is INSTALL.
- Runs 1, 3 and 5 drop the same three because they all need the plugin's `meow` queue, which the reader doesn't run (new skill = 1, a smaller procedure kept as text), and the verdict is COPY RULES. Run 1's banner hedges both ways: "install only for the queue itself".

The rules kept vary as well (see `stages.txt`), but no run's verdict depends on them. The dossier is the same in every run (shown for this neckbeard version in `../2026-10-15-vet-stability/dossier-det.txt`), and conflicts are 0 throughout, so neither the dossier nor conflict detection is the cause here.

## What this means for the fix

The prototype planned in `verdict-prototype-units` (numbered rule units and a written conflict test) would not fix this flip: it is not a conflict, and listing every unit still leaves the judge to decide whether a skill that needs the plugin's own machinery is worth keeping. What decides this case is a written rule for that call, and a verdict computed by code from the per-item answers. For example: a skill whose steps need a tool the plugin ships counts as "new skill" only if the reader's files show a use for that tool; otherwise it is dropped, and the report names the condition under which it would be worth installing.
