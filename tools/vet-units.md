UNITS PROTOTYPE. This run judges a fixed list of units instead of choosing which of the target's rules to list. It changes Step 2 and the verdict; everything else in the method stands.

UNITS: {units}. Each unit is one section of one of the target's instruction files, with an id, its file, its heading and its text. Judge every unit, and only these.

Each unit gets two answers from you, and a third that is already settled.

**skill: keep or drop.** keep when the unit is part of one of the target's own skills, commands or agents, that skill works as shipped, and it does something none of the reader's rules or skills already do. Needing the plugin's own tool (its CLI, its queue, its scripts) is not a reason to drop it: the owner's rule is that a plugin's own workflow skills are kept whenever they work as shipped. drop for persona and voice, routing for other hosts (Cursor, Codex), text that only describes or wraps something judged elsewhere, and anything the reader already has.

**conflicts: already settled.** Before this pass, three find passes pooled their candidates and each was confirmed or rejected in a call of its own. CONFIRMED: {confirmed} lists the conflicts that were confirmed, as {{"cid", "id", "quote", "reader_rule", "why"}}. Do not look for others and do not write a conflicts field: the tool puts these in the answers. List them in the report's conflicts grid, by unit, quoting the sentence and the reader rule; for a conflict of the kind "permits with no limit", say what limit to ask for.

**rules: what general rule the unit holds that matters outside the skill.** A rule inside an on-demand skill applies only while that skill is loaded, so a general rule is worth copying as a standing rule even when the plugin is kept. Pick the first that applies:
1. new-standing: a general rule about how to build or work, not tied to the plugin's tool, that the reader's rules do not already state. Quote it.
2. new-skill-text: a one-shot procedure, not tied to the plugin's tool, worth writing down as a small skill of the reader's own.
3. duplicate: its general rules are already in force; name the reader rule that covers them.
4. none: nothing general, only the plugin's own mechanics.

Write the answers to {answers} as JSON, {{"answers": [{{"id": "u1", "skill": "keep", "rules": "new-standing", "quote": "the rule to copy, if any", "why": "one sentence"}}]}}, one entry per unit, in unit order. Then run `python3 {nb}/tools/units-confirm merge {cands} {confs} {answers}` (it puts the confirmed conflicts into your answers), then `python3 {nb}/tools/units-verdict {units} {answers}` and use the verdict it prints, unchanged, in the banner. In "How its rules sorted" use its counts (confirmed conflicts, new standing, new skill, covered) and put the skills kept and the units dropped beside them. The grids list units, one row per unit, named by file and heading: conflicts, rules to copy (new-standing and new-skill-text, quoted, whatever the verdict), covered, then the skill sections kept; the dropped section lists unit ids. Do not decide the verdict yourself: if you disagree with the computed one, say so in one sentence under the banner and keep it.
