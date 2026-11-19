# Sealed judge rerun on 2.0

One rerun of the sealed fixture (12 points per run) under its full protocol: two full-arm runs (neckbeard 2.0) and two cut-down-arm runs. 2.0 passes the pre-registered bar. The fixture does not discriminate between the arms, and the planner and grader read the all-12 full arm as making it suspect (the pre-registered reading 4 wording is not met). The fixture is now spent.

| | |
|---|---|
| Tip | `2e21621d9776` (integrate/2.0.0; reports print 1.17.8 from the unbumped manifest; the loaded export matched a fresh export of the commit apart from dangling-symlink test fixtures) |
| Model | claude-opus-5-5, all four runs |
| Date | 2026-11-18, as the grader recorded it |
| Runs | Four: F1 and F2 (full arm), C1 and C2 (cut-down arm) |
| Void runs | None. Both full-arm dossiers listed exactly the three corpus sources; neither cut-down transcript called neckbeard |
| Bar | At least 10 of 12 per run with both trap items right (pre-registered, "54a") |

## Scores

| Run | Score | Sorts | Citations | Carrying cost | Traps | Wrong |
|---|---|---|---|---|---|---|
| F1 | 12 of 12 | 7/7 | 4/4 | 1/1 | both right | none |
| F2 | 12 of 12 | 7/7 | 4/4 | 1/1 | both right | none |
| C1 | 12 of 12 | 7/7 | 4/4 | 1/1 | both right | none |
| C2 | 11 of 12 | 6/7 | 4/4 | 1/1 | both right | `stamped-names` |

## Disagreements

- Full arm: none.
- Cut-down arm: `stamped-names` (C2 chose the on-demand skill, C1 the standing rule).

## Readings

1. 2.0 passes: both full runs scored at least 10 with both traps right.
2. 2.0 is not failed.
3. The fixture does not discriminate: C1's 12 is not below the full runs, and the mean gap is 0.5, under 1.5. The result reads "passes the bar, judgment half unverified".
4. The pre-registered test is not met. Its fixed wording is all four runs at 12 of 12 with no disagreement, and C2 scored 11 and the cut-down arm disagreed. Separately, the grader and the planner read the full arm alone as suspect: both full runs scored 12 of 12 with no disagreement.

## How it ran

The owner ran it at the Mac. The grader's report came back with scores and ids only; no fixture text is recorded here. The report did not say whether each executor had its own scratch copy or whether the copies were deleted afterwards.

## Spent

The fixture is spent.
