# Pool, then confirm: five runs each on Cat Herder 0.40.3 and 0.53.2

`tools/vet --units` at `5bfff53` for eight 0.53.2 and all 0.40.3 runs, and `035cff0` for 0.53.2 runs 1 and 4 (it adds one retry of a confirm call that answered with no JSON). Three find passes run side by side and their conflict candidates are pooled (`tools/units-confirm pool`). Each candidate is then confirmed or rejected in a call of its own that sees the reader rule, the sentence and the written test (`tools/vet-conflict-test.md`), with no tools. Only confirmed conflicts reach the answers (`units-confirm merge`), so `tools/units-verdict` counts only those. Sonnet for every call, agentbay through testslot, judge on agentbay's own config (the sample reader can't log in there). Targets: Cat Herder 0.40.3 (8442cb6b export) and 0.53.2.

- Verdict: INSTALL WITH CHANGES in 5 of 5 on 0.40.3 (before: 4 of 5 with the conflicts-first design, 3 of 5 with the baseline) and 5 of 5 on 0.53.2.
- Conflicts, by unit: the same units in every run, 33 of 33 units answered alike on 0.40.3 and 64 of 64 on 0.53.2.
- 0.40.3 confirmed the same two sentences in all five runs: `reviewer.md > Limits`, "You may try the same action, on your own judgement" (found by all three passes every time, the real conflict the earlier rounds caught in 2 of 5), and `worker.md > The worker, in a pair`, "The reviewer may try an action you reported as refused, on its own judgement". Candidates per run: 2 or 3; confirmed: 2.
- 0.53.2 confirmed conflicts in the same five units in every run (`orchestrator.md > The orchestrator`, `reviewer.md > Each review`, `reviewer.md > Limits`, `worker.md > The worker, in a pair`, `queue/SKILL.md > Working the queue`), but the sentences differ a little: runs 1, 3, 4 and 5 confirmed 8 sentences, run 2 confirmed 6. Candidates per run: 8 to 10; confirmed: 6 to 8. So the verdict and the units are steady, the sentence list is not quite. Run 2's pooling missed two sentences that the other runs' passes found once or twice each (found in 1 or 2 of 3 passes), which is the weak spot of three passes.
- Not steady, and not what this item set out to fix: the skill answer (30 of 33 alike on 0.40.3, 57 of 64 on 0.53.2) and the rules answer (25 of 33, 48 of 64). The verdict doesn't depend on them in these ten runs, since skills were kept in every run.

## Cost

Find and confirm calls, from the `total_cost_usd` each call reports: 0.40.3, $1.23 to $1.58 per vet (5 or 6 calls, median $1.35); 0.53.2, $2.39 to $2.52 per vet (11 to 13 calls, median $2.40). The report pass isn't in those dollars (the CLI text mode doesn't report cost), so the whole vet costs more.

Time per whole vet (dossier, finds in parallel, confirms in parallel, report pass): 0.40.3, 113 to 147 s, median 131; 0.53.2, 161 to 238 s, median 201. The conflicts-first baseline took 3.0 minutes on 0.40.3 on the Mac and the plain baseline 2.5 on agentbay, so on 0.40.3 this design is no slower than those; the finds and confirms run side by side.

## What went wrong on the way

- First attempt, all ten vets failed in 1 to 2 seconds: `--judge reader` can't log in on agentbay, and the find pass hid the judge's reply. The vet now prints what a failed find pass said.
- 0.53.2 runs 1 and 4 failed once each on a confirm call that answered with no JSON (the logs are in `0532/failed/`). They were rerun after the retry fix. The retry has a test; no run in these files needed it.

## Files

Per target, `run-N.md` (report), `run-N.finds-1..3.json` (each pass), `run-N.candidates.json`, `run-N.confirmations.json`, `run-N.confirmed.json`, `run-N.answers.json`, `run-N.units.json`, `run-N.log`, and `times.txt`. Compare runs with `python3 tools/units-verdict 0403/run-1.units.json 0403/run-?.answers.json`.

## What this means for SKILL.md

Pool-and-confirm makes the verdict steady here and finds the real 0.40.3 conflict every time. Writing it into SKILL.md needs Jerry's go (`verdict-stability-rules`). Open before that: a fourth find pass or a second pooling would close the sentence-level gap on 0.53.2, at about a third more cost.
