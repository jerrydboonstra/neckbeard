# Pool, then confirm: five runs each on Cat Herder 0.40.3 and 0.53.2

`tools/vet --units` at `5bfff53` for the five 0.40.3 runs and 0.53.2 runs 2, 3 and 5, and `035cff0` for 0.53.2 runs 1 and 4 (it adds one retry of a confirm call that answered with no JSON). These runs predate the fix below (the confirm call got the finder's `reader_rule` text as written); see "Re-confirmed with the reader's own rule text". Three find passes run side by side and their conflict candidates are pooled (`tools/units-confirm pool`). Each candidate is then confirmed or rejected in a call of its own that sees the reader rule, the sentence and the written test (`tools/vet-conflict-test.md`), with no tools. Only confirmed conflicts reach the answers (`units-confirm merge`), so `tools/units-verdict` counts only those. Sonnet for every call, agentbay through testslot, judge on agentbay's own config (the sample reader can't log in there). Targets: Cat Herder 0.40.3 (8442cb6b export) and 0.53.2.

- Verdict: INSTALL WITH CHANGES in 5 of 5 on 0.40.3 (before: 4 of 5 with the conflicts-first design, 3 of 5 with the baseline) and 5 of 5 on 0.53.2.
- Conflicts, by unit: the same units in every run, 33 of 33 units answered alike on 0.40.3 and 64 of 64 on 0.53.2.
- 0.40.3 confirmed the same two sentences in all five runs: `reviewer.md > Limits`, "You may try the same action, on your own judgement" (found by all three passes every time, the real conflict the earlier rounds caught in 2 of 5), and `worker.md > The worker, in a pair`, "The reviewer may try an action you reported as refused, on its own judgement". Candidates per run: 2 or 3; confirmed: 2.
- 0.53.2 confirmed conflicts in the same five units in every run (`orchestrator.md > The orchestrator`, `reviewer.md > Each review`, `reviewer.md > Limits`, `worker.md > The worker, in a pair`, `queue/SKILL.md > Working the queue`), but the sentences differ a little: runs 1, 3, 4 and 5 confirmed 8 sentences, run 2 confirmed 6. Candidates per run: 8 to 10; confirmed: 6 to 8. So the verdict and the units are steady, the sentence list is not quite. Two causes, not one. Pooling: run 2's three find passes never offered "The reviewer may try an action you reported as refused" (the other four runs found it). Confirming: run 2 did pool "Before `done`, one more read-only Haiku checks each docs or CHANGELOG ..." (`run-2.candidates.json` c7), the same sentence runs 1, 3, 4 and 5 confirmed, and its confirm call rejected it. A fourth find pass would help the first cause and not the second.
- Not steady, and not what this item set out to fix: the skill answer (30 of 33 alike on 0.40.3, 57 of 64 on 0.53.2) and the rules answer (25 of 33, 48 of 64). The verdict doesn't depend on them in these ten runs, since skills were kept in every run.

## Re-confirmed with the reader's own rule text

The reviewer found that the confirm call was not as isolated as designed. `reader_rule` is free text from the find pass, and in 11 of the 59 pooled candidates it carried the finder's argument after the rule, for example `(the permission to retry a refused action is unlimited, so it covers destructive actions)`, so the call was handed the verdict. The fix (`tools/units-confirm pool` now takes the dossier): a finder's `reader_rule` only points at a rule, and the candidate carries the reader's own rule text from the dossier's `current_rules`, or is dropped if it matches no rule. One sentence against two reader rules now stays two candidates.

`reconfirm.py` pools the committed `run-N.finds-1..3.json` again with the fixed code and confirms every candidate in a fresh call (same prompt, Sonnet, no tools, one retry), for all ten runs: 59 candidates, 59 calls. Files: `run-N.recand.json`, `run-N.reconf.json`, `run-N.reconfirmed.json`, `recost.txt`.

- 0.40.3: the same two sentences, `reviewer.md > Limits` and `worker.md > The worker, in a pair`, confirmed in 5 of 5 runs. The result holds without the finder's help, including runs 2, 4 and 5, where the headline candidate had carried an argument. The third candidate in runs 1, 2 and 5 (`TODO(debt):`) is rejected, as before.
- 0.53.2: run 1, 2, 3 and 5 confirm exactly the sentences they confirmed before (8, 6, 8, 8). Run 4 confirms 7, not 8: it now rejects "one more read-only Haiku checks each docs or CHANGELOG line" (run 2 rejected it before). That sentence is confirmed in runs 1, 3 and 5 and rejected in runs 2 and 4, so the confirm step is not steady on it. The other sentences were steady. The five units are the same in every run.
- Cost of the 59 calls: $0.42 on 0.40.3 (13 calls) and $1.85 on 0.53.2 (46 calls).

So the weak spot on 0.53.2 is two things: one borderline sentence the confirm call decides both ways, and one sentence that a pooling of three passes sometimes misses. The verdict and the conflicting units are steady.

## Cost

Find and confirm calls, from the `total_cost_usd` each call reports: 0.40.3, $1.23 to $1.58 per vet (5 or 6 calls, median $1.35); 0.53.2, $2.39 to $2.52 per vet (11 to 13 calls, median $2.40). The report pass isn't in those dollars (the CLI text mode doesn't report cost), so the whole vet costs more.

Time per whole vet (dossier, finds in parallel, confirms in parallel, report pass): 0.40.3, 113 to 147 s, median 131; 0.53.2, 161 to 238 s, median 201. The conflicts-first baseline took 3.0 minutes on 0.40.3 on the Mac and the plain baseline 2.5 on agentbay, so on 0.40.3 this design is no slower than those; the finds and confirms run side by side.

## What went wrong on the way

- First attempt, all ten vets failed in 1 to 2 seconds: `--judge reader` can't log in on agentbay, and the find pass hid the judge's reply. The vet now prints what a failed find pass said.
- 0.53.2 runs 1 and 4 failed once each on a confirm call that answered with no JSON (the logs are in `0532/failed/`). They were rerun after the retry fix. The retry has a test; no run in these files needed it.

## Files

Per target, `run-N.md` (report), `run-N.finds-1..3.json` (each pass), `run-N.candidates.json`, `run-N.confirmations.json`, `run-N.confirmed.json`, `run-N.answers.json`, `run-N.units.json`, `run-N.log`, `times.txt`, and the re-confirmation files named above. Compare runs with `python3 tools/units-verdict 0403/run-1.units.json 0403/run-?.answers.json`.

## What this means for SKILL.md

Pool-and-confirm makes the verdict steady here and finds the real 0.40.3 conflict every time. Writing it into SKILL.md needs Jerry's go (`verdict-stability-rules`). Open before that: the sentence-level gap on 0.53.2 has two causes (a pool miss and a borderline confirm, see above). A fourth find pass would address only the first, at about a third more cost.
