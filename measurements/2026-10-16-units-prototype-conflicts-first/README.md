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

## What would

1. Find, then confirm. Pool the conflict candidates of several passes, so a sentence one pass misses is still on the list, then confirm or reject each candidate in a small call of its own that sees one sentence, the reader rule and the written test. The pooling catches misses, the confirmation rejects weak findings. This is `verdict-stability-codex`'s design (an independent confirmer), and the confirmer can be another provider.
2. A written rule for the borderline case: a sentence that permits, with no limit, an action that a reader rule forbids in some cases (a retry "on your own judgement" that could be destructive) is a conflict. This is the owner's call.
