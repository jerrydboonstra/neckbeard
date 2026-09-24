# Attribution

A tool that exists to find out what a plugin took from somewhere else should be exact about what it took from somewhere else.

No code was taken from either project below. `skills/neckbeard/inventory.py` is original and uses only the Python standard library.

## The method, from Yanhua (@yanhua1010)

https://x.com/yanhua1010/status/2094612609932910828 (2026-09-01, in Chinese) Resulting rules: https://gist.github.com/yanhua1010/5d868d2e68c6b9ef7d738dcec40d3572

Yanhua nearly installed `ponytail` off the GitHub trending list, read the whole thing instead, and published what he did. That procedure is what this plugin automates, in four steps:

1. Read all of it before deciding anything. He read all 670 lines of hook code.
2. Diff it against the rules already in force. He found about 60 percent overlap with his own config and five direct conflicts.
3. Count what it costs to carry. Once installed, the main agent and every subagent carry a second copy of the whole rule set.
4. Keep only what is new. He extracted four rules and dropped the rest.

**Four of the five rules that came out of this plugin's first real run are his**, near-identical in substance: source priority, dependency discipline, the guardrail list (security, trust boundaries, error handling that prevents data loss), and debt comments naming a ceiling and an upgrade path. Only the root-cause rule came from elsewhere.

## `ponytail`, by Dietrich Gebert (MIT)

https://github.com/DietrichGebert/ponytail

Not a source of code or of rules, but of three other things:

1. **The first real evaluation target.** The worked example this plugin was built against and verified on.
2. **What to inspect.** Its structure taught the inventory what a real plugin does: injection reached two hops away through `require()` and a path built from `path.join(__dirname, ...)` rather than a single string literal, and bundled mirrors for other agent ecosystems that inflate a naive file count by double. Both are handled because ponytail does both.
3. **The name.** Neckbeard is a play on ponytail. Two kinds of hair, two developer archetypes.

## The logo

`assets/logo.webp` was generated with OpenAI's image model, from prompts written for this project. Under current US law a purely AI-generated image has no human author, so the repository's MIT copyright line does not cover it. Nobody owns it, and you may reuse it.
