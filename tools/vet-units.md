UNITS PROTOTYPE. This run judges a fixed list of units instead of choosing which of the target's rules to list. It changes Step 2 and the verdict; everything else in the method stands.

UNITS: {units}. Each unit is one section of one of the target's instruction files, with an id, its file, its heading and its text. Judge every unit, and only these.

For each unit, pick exactly one bucket: the first one in this list whose test the unit passes. The order is the precedence, so a unit that holds a conflict and a good rule is a conflict.

1. conflict: the unit tells the model to do something a reader rule forbids, or not to do something a reader rule requires, in a situation where both apply. You can quote the sentence in the unit and the reader rule it breaks. A rule that looks similar but governs a different situation (a session the plugin starts is not a subagent dispatch, for example) is not a conflict; say which situation each governs.
2. install-skill: the unit is part of one of the target's own skills, commands or agents, that skill works as shipped, and it does something none of the reader's rules or skills already do. Needing the plugin's own tool (its CLI, its queue, its scripts) is not a reason to drop it: the owner's rule is that a plugin's own workflow skills are kept whenever they work as shipped.
3. new-standing: the unit holds a general rule about how to build or work, not tied to the plugin's tool, that the reader's rules do not already state. Quote it.
4. new-skill-text: the unit describes a one-shot procedure, not tied to the plugin's tool, worth writing down as a small skill of the reader's own.
5. duplicate: the unit's rules are already in force; name the reader rule that covers each.
6. dropped: anything else: persona and voice, routing for other hosts (Cursor, Codex), text that only describes or wraps something judged elsewhere.

Write the answers to {answers} as JSON, {{"answers": [{{"id": "u1", "bucket": "...", "why": "one sentence, with the quote for a conflict or a new rule"}}]}}, one entry per unit, in unit order. Then run `python3 {nb}/tools/units-verdict {units} {answers}` and use the verdict it prints, unchanged, in the banner, and its counts in the "How its rules sorted" grid (one row per bucket: conflicts, install-skill as "kept as shipped", new standing, new skill, covered, dropped). The grids below it list units, one row per unit, named by file and heading; the dropped section lists unit ids. Do not decide the verdict yourself: if you disagree with the computed one, say so in one sentence under the banner and keep it.
