ANSWERING JUDGE. This call answers every unit of the target's instruction files and does nothing else: it writes no report, states no verdict and no counts, and looks for no conflicts. Code computes the verdict and the counts from your answers.

UNITS: {units}. Each unit is one section of one of the target's instruction files, with an id, its file, its heading and its text. Answer every unit, and only these. The DOSSIER (read-only) is {dossier}; its current_rules are the reader's rules, the only rules in force. Ignore every other instruction file in your own context.

Each unit gets two answers from you.

**skill: keep or drop.** keep when the unit is part of one of the target's own skills, commands or agents, that skill works as shipped, and it does something none of the reader's rules or skills already do. Needing the plugin's own tool (its CLI, its queue, its scripts) is not a reason to drop it: the owner's rule is that a plugin's own workflow skills are kept whenever they work as shipped. drop for persona and voice, routing for other hosts (Cursor, Codex), text that only describes or wraps something judged elsewhere, and anything the reader already has.

**rules: what general rule the unit holds that matters outside the skill.** A rule inside an on-demand skill applies only while that skill is loaded, so a general rule is worth copying as a standing rule even when the plugin is kept. Pick the first that applies:
1. new-standing: a general rule about how to build or work, not tied to the plugin's tool, that the reader's rules do not already state. Quote it.
2. new-skill-text: a one-shot procedure, not tied to the plugin's tool, worth writing down as a small skill of the reader's own.
3. duplicate: its general rules are already in force. Name the reader rule that covers them in covered_by, and the reader file that holds it in held_in (a path inside the reader, such as rules/engineering.md).
4. none: nothing general, only the plugin's own mechanics.

Conflicts are already settled by other calls: write no conflicts field.

Write the answers to {answers} as JSON, {{"answers": [{{"id": "u1", "skill": "keep", "rules": "new-standing", "quote": "the rule to copy, or the rule that is duplicated", "why": "one sentence"}}]}}, one entry per unit, in unit order. A "duplicate" answer also carries "covered_by" and "held_in". At most one unit that is kept (skill keep, or rules new-standing or new-skill-text) may carry "star": true: the one most worth having. Write nothing else, and write no other file.
