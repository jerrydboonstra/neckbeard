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
- **Conflicts:** the conflict is against `rules/safety.md` in all five runs, but the Conflicts card has 2 rows in four runs and 1 in run 3. The cause is a pool miss, not a confirm decision. The sentence is in `skills/herd/roles/worker.md > The worker, in a pair` (u19, "may try an action"); run 3's three find passes never offered it (`run-3.finds-1..3.json` do not contain it; `run-3.log`: "1 candidates from 3 passes", the one candidate being u16, `reviewer.md > Limits`). The find passes offered it in 3 of 3 passes in run 2, 2 of 3 in runs 1 and 4, 1 of 3 in run 5 and 0 of 3 in run 3. Every pooled candidate was confirmed in all five runs (2 of 2 in runs 1, 2, 4 and 5; 1 of 1 in run 3, from the logs), so the confirm step rejected nothing. The two causes need different fixes: a fourth find pass helps only a pool miss. In October the two sentences on 0.40.3 were confirmed in 5 of 5 runs, so this run is the first to miss one in pooling on this target.
- **Keep:** 25 skills in runs 1 to 3, 26 in runs 4 and 5. The difference is `skills/queue/SKILL.md > Questions for you` (u31, skill answer keep 2, drop 3). The starred row (the ⭐) sits at a different place in the runs that kept 25 and the runs that kept 26, so the Keep colours differ between those two groups.
- **Dropped:** 8 in runs 1 to 3, 7 in runs 4 and 5, the same unit.
- **Already covered:** 0 in all five.
- **Rules answers** (`units-verdict.txt`): 28 of 33 units answered alike in all five runs. The five that differ are u2, u15, u16, u18 and u19 (duplicate against none or new-standing). This moves the "new standing rule" row (2, 1, 2, 2, 3) and the "new, on-demand skill" row (23, 24, 23, 24, 23).
- **Units:** the same 33 units in every run (`run-N.units.json` are identical), so the differences are in the answers, not the unit list.

So the verdict, the units list and the Already covered count agree in all five runs. The Conflicts, Keep and Dropped cards differ because of three things: a pool miss of u19 in run 3, the skill answer for u31, and the rules answers of five units. The disagreement lines name each card that differs: Conflicts, Keep and Dropped by count, Conflicts and Keep by colour. That is a finding for the planner, not a failure of the item (the item's cold read).

## Files

`run-N.md` is the report; `run-N.units.json`, `run-N.finds-1..3.json`, `run-N.candidates.json`, `run-N.confirmations.json`, `run-N.confirmed.json`, `run-N.answers.json`, `run-N.verdict.json` and `run-N.prose.json` are the steps beside it; `run-N.log` is vet's stderr. `times.txt` and `testslot.log` come from the slot. `vet-stability.txt` is `python3 tools/vet-stability run-?.md`; `units-verdict.txt` is `python3 tools/units-verdict run-1.units.json run-?.answers.json`.
