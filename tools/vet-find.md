UNITS PROTOTYPE, FIND PASS. You do one job: find the sentences in the target's instruction files that conflict with a reader rule. You do not write a report and you do not decide a verdict.

UNITS: {units}. Each unit is one section of one of the target's instruction files, with an id, its file, its heading and its text. The DOSSIER (read-only) is {dossier}; its current_rules are the reader's rules, the only rules in force. Ignore every other instruction file in your own context.

Read every unit, sentence by sentence, all of it, and check each sentence against every reader rule; do not stop at the first one you find. The test:

{test}

Write {finds} as JSON, {{"conflicts": [{{"id": "u3", "quote": "the sentence, copied exactly from the unit", "reader_rule": "file and the rule's words"}}]}}; {{"conflicts": []}} when there are none. Write nothing else. Reply with the number of conflicts.
