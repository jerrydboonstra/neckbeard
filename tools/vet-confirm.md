CONFIRM CALL. Decide one question and nothing else. You have no other context; do not look for other conflicts.

A reader rule, from the reader's file {label}, under the heading "{heading}":
{rule}

A sentence from a plugin's instruction file:
{sentence}

The test for a conflict:
{test}

Does the sentence conflict with the reader rule, by that test? Also answer hard_stop: true when the reader rule is a hard stop or safety rule (its file or heading says so, or the rule itself says to stop and ask), false when it is an ordinary working rule. Reply with one line of JSON and nothing else: {{"conflict": true or false, "hard_stop": true or false, "why": "one sentence"}}
