UNITS PROTOTYPE. This run judges a fixed list of units instead of choosing which of the target's rules to list. It changes Step 2 and the verdict; everything else in the method stands.

UNITS: {units}. Each unit is one section of one of the target's instruction files, with an id, its file, its heading and its text. Judge every unit, and only these.

Each unit gets three answers, because they are three questions. Answer them in this order.

**skill: keep or drop.** keep when the unit is part of one of the target's own skills, commands or agents, that skill works as shipped, and it does something none of the reader's rules or skills already do. Needing the plugin's own tool (its CLI, its queue, its scripts) is not a reason to drop it: the owner's rule is that a plugin's own workflow skills are kept whenever they work as shipped. drop for persona and voice, routing for other hosts (Cursor, Codex), text that only describes or wraps something judged elsewhere, and anything the reader already has.

**conflicts: every sentence in the unit that breaks a reader rule.** Read the unit sentence by sentence, all of it, and check each against the reader's rules; do not stop at the first rule you find. A sentence conflicts when it tells the model to do something a reader rule forbids, or not to do something a reader rule requires, in a situation where both apply. A rule that looks similar but governs a different situation (a session the plugin starts is not a subagent dispatch, for example) is not a conflict. Give each as {{"quote": "the sentence", "reader_rule": "file and the rule's words"}}; [] when none.

**rules: what general rule the unit holds that matters outside the skill.** A rule inside an on-demand skill applies only while that skill is loaded, so a general rule is worth copying as a standing rule even when the plugin is kept. Pick the first that applies:
1. new-standing: a general rule about how to build or work, not tied to the plugin's tool, that the reader's rules do not already state. Quote it.
2. new-skill-text: a one-shot procedure, not tied to the plugin's tool, worth writing down as a small skill of the reader's own.
3. duplicate: its general rules are already in force; name the reader rule that covers them.
4. none: nothing general, only the plugin's own mechanics.

Write the answers to {answers} as JSON, {{"answers": [{{"id": "u1", "skill": "keep", "conflicts": [], "rules": "new-standing", "quote": "the rule to copy, if any", "why": "one sentence"}}]}}, one entry per unit, in unit order. Then run `python3 {nb}/tools/units-verdict {units} {answers}` and use the verdict it prints, unchanged, in the banner. In "How its rules sorted" use its rule counts (conflicts, new standing, new skill, covered) and put the skills kept and the units dropped beside them. The grids list units, one row per unit, named by file and heading: conflicts, rules to copy (new-standing and new-skill-text, quoted, whatever the verdict), covered, then the skill sections kept; the dropped section lists unit ids. Do not decide the verdict yourself: if you disagree with the computed one, say so in one sentence under the banner and keep it.
