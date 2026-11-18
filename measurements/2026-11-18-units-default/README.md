# The units path as the default: five runs on Cat Herder 0.40.3

Five runs of `tools/vet` (the fit report, now on the units path by default) on the target whose verdict flipped in October, then `tools/vet-stability` over the five reports. Item `units-default-measure`, split from `verdict-stability-rules` (its Done when 5).

- **Target:** Cat Herder 0.40.3 at `8442cb6be6` (the commit "0.40.3: CHANGELOG section ... and the version in every manifest", 2026-10-06), a clean checkout of that commit, named `cat-herder` so the reports carry the plugin's name.
- **neckbeard:** `a62e067d989b` (`dev/integrate/2.0.0` after `verdict-stability-rules` merged; plugin.json says 1.17.8), exported with `git archive`.
- **Host and slot:** agentbay (Linux), one `testslot run --track --max-minutes 60` job that ran the five vets one after another. Date: 2026-11-18.
- **Command, once per run N:** `tools/vet <target checkout> out/run-N.md`, with no `--judge`, `--model` or `--reader`: the default reader (`examples/reader`, "the sample reader") and the default model (`NECKBEARD_MODEL`, else `sonnet`).
- **Judge:** the default judge tries the sample reader as its config folder first. On agentbay it fell back in all five runs to the caller's own config, told to ignore it ("Judge: your own config, told to ignore it" in each report), because the login was due to refresh within the hour (the line is in each `run-N.log`). That matches October's note that the sample reader can't log in there, for a different reason.
- **Cost and time, from each log:** $1.95 to $2.22 per vet in the find, confirm, answering and prose calls (6 or 7 calls each); 74 to 89 s per whole vet (`times.txt`).

## Result: the verdict is steady, the counts are not

`vet-stability.txt` is the tool's own output: **NOT stable**.

- **Verdict:** INSTALL WITH CHANGES in 5 of 5 (October's 0.40.3 runs: 5 of 5 too).
- **Conflicts:** the conflict is against `rules/safety.md` in all five runs, but the Conflicts card has 2 rows in four runs and 1 in run 3. The difference is one unit, `skills/herd/roles/worker.md > The worker, in a pair` (u19): confirmed a conflict in 4 runs, not in run 3. In October the two sentences on 0.40.3 were confirmed in 5 of 5 runs.
- **Keep:** 25 skills in runs 1 to 3, 26 in runs 4 and 5. The difference is `skills/queue/SKILL.md > Questions for you` (u31, skill answer keep 2, drop 3). The starred row (the ⭐) sits at a different place in the runs that kept 25 and the runs that kept 26, so the Keep colours differ between those two groups.
- **Dropped:** 8 in runs 1 to 3, 7 in runs 4 and 5, the same unit.
- **Already covered:** 0 in all five.
- **Rules answers** (`units-verdict.txt`): 28 of 33 units answered alike in all five runs. The five that differ are u2, u15, u16, u18 and u19 (duplicate against none or new-standing). This moves the "new standing rule" row (2, 1, 2, 2, 3) and the "new, on-demand skill" row (23, 24, 23, 24, 23).
- **Units:** the same 33 units in every run (`run-N.units.json` are identical), so the differences are in the answers, not the unit list.

So the verdict code, the units list and the card counts agree on everything except three units' answers (u19 conflict, u31 skill, and the rules answers). The disagreement lines name each card that differs: Conflicts, Keep and Dropped, by count, and Conflicts and Keep by colour. That is a finding for the planner, not a failure of the item (the item's cold read).

## Files

`run-N.md` is the report; `run-N.units.json`, `run-N.finds-1..3.json`, `run-N.candidates.json`, `run-N.confirmations.json`, `run-N.confirmed.json`, `run-N.answers.json`, `run-N.verdict.json` and `run-N.prose.json` are the steps beside it; `run-N.log` is vet's stderr. `times.txt` and `testslot.log` come from the slot. `vet-stability.txt` is `python3 tools/vet-stability run-?.md`; `units-verdict.txt` is `python3 tools/units-verdict run-1.units.json run-?.answers.json`.
