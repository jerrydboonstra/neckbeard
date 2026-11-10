# Conflicts asked on their own, five runs on Cat Herder 0.40.3

`tools/vet --units` at `fcb845d`: each section gets a skill answer, a list of every sentence that breaks a reader rule, and one rules answer for the copy list. Sonnet on the Mac through testslot, judge on the Mac's own config, as in `../2026-10-16-units-prototype-two-answers/`.

- Verdict: INSTALL WITH CHANGES 4 of 5, INSTALL 1 of 5 (before: 3 of 5 and 2 of 5).
- Skill answer: 33 of 33 sections the same in every run. Rules answer: 29 of 33.
- Each run found one conflict or none, and not the same one (`units-verdict.txt` and each `run-N.answers.json`):
  - runs 3 and 5: `reviewer.md > Limits`, "You may try the same action, on your own judgement", against the reader's "never run anything destructive without my explicit go-ahead";
  - run 1: `queue/SKILL.md > The queue`, "Short. The answer first", against the reader's "Short is good; complete is required";
  - run 4: `reviewer.md > Each review`, a bare `meow accept`, against "give the reasoning with the verdict";
  - run 2: none.

So the better verdict count is partly luck: the reviewer sentence that looks like a real conflict is found in only 2 of 5 runs, and runs 1 and 4 reach the same verdict through weaker findings. Asking about conflicts on their own made the skill answer exact but did not make conflict finding steady. Each run reads 33 sections and finds at most one borderline sentence; whether it lands on it is chance.

## Does the prototype beat the baseline?

On the skill judgment, yes: 0.40.3's old flip (keep its own workflow skills, or drop them as machinery) is gone, 33 of 33 sections the same in every run, and 0.53.2 holds at INSTALL WITH CHANGES 5 of 5. On the verdict, not yet: 0.40.3 still depends on which conflict a run finds. The fix the owner chose (pool, then confirm; a sentence that permits, with no limit, an action a reader rule forbids in some cases is a conflict) is queued as `verdict-units-confirm`.

Which design each number comes from: this directory's design (`fcb845d`) ran on 0.40.3 only. The 0.53.2 numbers are the two-answer design (`c5ae5ee`, `../2026-10-16-units-prototype-two-answers/`, 5 runs) and the one-answer design (`9e43fbf`, `../2026-10-16-units-prototype/`, 2 runs).

## Cost

No run logs a dollar cost, so this is wall time per run, from the gaps between consecutive report files (judge and dossier together, Sonnet): baseline 1.14.0 on 0.40.3, agentbay, median 2.5 minutes (2.1 to 2.6); one answer, agentbay, 2.0; two answers, Mac, 2.3 on 0.40.3 and 2.7 on 0.53.2; this design, Mac, 3.0 (2.1 to 3.5). So about a fifth more time than the baseline, with the judge also writing the answers file. Pool-and-confirm would roughly triple it plus the confirm calls.

## Report quality

The unit-grid report reads about as well as the baseline's: the same banner and At a glance, and the rules to copy now cite section and quote (8 in run 1 against the baseline's 4), which is more useful. Two things read worse. The conflict row in run 1 mixes the reader's file and the target's section in one "held in" cell. And the count table puts "skills kept 25 of 33" beside rule counts that also cover those 33 sections, which needed a sentence of explanation in run 5. The judge's one real error is the weak conflict itself (run 1's "Short. The answer first", which concerns phone replies, not reports).

## What would

1. Find, then confirm. Pool the conflict candidates of several passes, so a sentence one pass misses is still on the list, then confirm or reject each candidate in a small call of its own that sees one sentence, the reader rule and the written test. The pooling catches misses, the confirmation rejects weak findings. This is `verdict-stability-codex`'s design (an independent confirmer), and the confirmer can be another provider.
2. A written rule for the borderline case: a sentence that permits, with no limit, an action that a reader rule forbids in some cases (a retry "on your own judgement" that could be destructive) is a conflict. This is the owner's call.
