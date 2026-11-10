# Five vet runs on one unchanged target

Question: when `tools/vet` judges the same plugin five times, what changes between the reports, and at which stage?

Setup: neckbeard 1.14.0, target Cat Herder v0.53.2 (a plugin export), judge = the model on the maintainer's own config (the sample reader could not log in on the test host), run with `tools/vet-repeat TARGET OUT 5` on agentbay under `testslot`. The five reports are `run-1.md` to `run-5.md`. One target and one judge setup: this is evidence, not proof that it holds elsewhere.

## What the reports say

`vet-stability.txt` is the output of `tools/vet-stability run-?.md`:

- Verdict: COPY RULES, SKIP PLUGIN in 5 of 5.
- The reader's model-override rule (engineering rule 6) is flagged in 5 of 5. Safety rule 5 and engineering rule 4 are flagged in 2 of 5 each, engineering rule 7 in 1 of 5.
- Counts (conflicts / covered / new standing / new skill / dropped): 3/9/7/1/12, 3/7/4/1/19, 3/9/5/1/15, 4/11/5/1/30, 4/7/4/1/6.

## Where the spread enters

Three stages sit between the target and the report: the dossier (built by code), the judge's choice of which target rules to list (extraction), and the bucket it gives each (classification). `stages.txt` is `python3 stages.py run-?.md`.

1. **Dossier: not a source.** `dossier-det.sh` rebuilds the dossier five times the way `tools/vet` does (`dossier-det.txt`). The five files differ byte for byte, but only because the temp directory's path is written into them. With that path blanked all five hash the same. The judge is given the same text each run.
2. **Extraction: the largest source.** The five reports list 32, 34, 33, 51 and 22 items in all. The dropped count is exactly the number of entries on the judge's own "Dropped" line, so "dropped" measures how finely it chose to cut the plugin, not how it sorted anything: run 4 lists each slash command and each section file on its own (30 entries), run 5 lumps the same material into 6. The three tables that carry one rule per row (conflicts, covered, keep) hold 20, 15, 18, 21 and 16 rows. I grouped those 90 rows into 32 rules by theme (`stages.py`; 87 of 90 rows matched a theme, and the themes are my reading, not the judge's labels). Only 2 of the 32 appear in all five runs (the model-override conflict and "work found along the way is queued"); 19 appear in only one or two.
3. **Classification: smaller, but it moves the minor conflicts.** Of the 24 rules listed in two or more runs, 6 land in a different bucket in different runs (for example "a skipped question is unread" is keep in three runs and covered in one; "commit subjects say what changed" is keep in one run and a conflict in another). The other 18 stay in one bucket, including the model-override conflict.

So most of the spread in "covered", "new standing" and "dropped" comes from the judge choosing a different set of target rules to list each time, before it sorts them. The secondary conflicts (rules 4, 5 and 7) come from both stages: the rule is listed in some runs and not others, or listed and sorted differently.

## Ranking, by the spread each change removes per cost

1. **Have code list the target's rule units, and make the judge sort every one.** The dossier would number the candidate rules (the headings, bullets and numbered items of the rule-bearing files), the judge would return a bucket for each, and the counts would be computed from that list, not written by the judge. This fixes extraction and the count arithmetic together. It changes the dossier and the report template, so SKILL.md prose changes with it and needs Jerry's go (`verdict-stability-rules`).
2. **A written test for "covered" versus "keep" versus "dropped"**, so classification flips shrink. Edits SKILL.md, same go.
3. **Run the judge three times and keep the conflicts found in a majority** (a mode of `tools/vet`, built on `vet-repeat` and `vet-stability`). Keeps the verdict stable even when 1 and 2 are not done, at three times the judge cost.
4. **Put what hook scripts inject into the dossier.** Run 5 says it resolved the hooks by reading the target's hook code, so the judge still opens files by hand. A larger change; it removes the one known by-hand reading.

Not measured: the judge's tool use, and a second target or judge.
