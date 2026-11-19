# 🔍 viral-launch-pipeline

`2026-11-18` · [Koz-TV/viral-launch-pipeline](https://github.com/Koz-TV/viral-launch-pipeline) 1.0.0 @ `475705f` · made by neckbeard 2.0.0

**Contents**

1. [How it affects you](#how-it-affects-you): cost, reach, state and live surface at a glance. Carries a judgement: the colours.
2. [What it adds](#what-it-adds): what the plugin loads, injects and may leave on disk, written by code. No judgement.
3. [Where it takes a position](#where-it-takes-a-position): every place it tells the model what to do, by topic, in its own words. No judgement.

---

**1 · Summary · carries a judgement**

## How it affects you

| | Row | In short |
|---|---|---|
| 🟩 | Cost | adds 571 characters to every session, ~143 tokens (571 characters of skill descriptions, 0 agent descriptions, 0 rule files, 0 hook text) |
| 🟩 | Reach | on demand only |
| 🟩 | Leaves state | nothing found |
| 🟩 | Live surface | no hook commands, MCP servers or mods found |
| 🟩 | Read completeness | read in full |

<details><summary><b>How the colours are set</b></summary>

The colours follow written rules. Each is checked top to bottom, and the first match wins. A row whose input was not read in full is never 🟩.

- Cost: 🟩 under 2,000; 🟨 2,000 to 7,999; 🟧 8,000 to 31,999; 🟥 32,000 and over. Size counts skill and agent descriptions in characters, and rule files and hook-injected text in bytes (the dossier's own units), so a total that holds both says "characters and bytes"; text a hook builds at run time counts as at least its known size. Hook text counts twice when hooks reach subagents. An entry that was refused or has no usable size counts as 0.
- Reach: 🟥 a hook and hooks reach subagents; 🟨 a hook, a Claude Code mod or a rule file (every main session); 🟩 neither (on demand only).
- Leaves state: 🟧 one or more files that may write state; 🟨 nothing found but the scan was partial or failed; 🟩 nothing found by a full scan.
- Live surface: 🟥 a hook or MCP command runs ssh, mosh, telnet, rsh, rlogin (each a remote shell); 🟧 any MCP server, any Claude Code mod, a hook running curl, wget, nc or holding an http:// or https:// URL, or a hook command too long to read; 🟨 any hook command; 🟩 none. A command word is the first word of each piece, cut at newlines and at | && || ; & outside quotes, after NAME=value words, by basename; an MCP server's command is compared by its first word and each of its args whole, by basename. The scan does not search inline code (bash -c, node -e), hook script bodies, or commands behind a wrapper (sudo, timeout, command, nohup, exec, xargs, ( ), { }, !, $( ) or backticks).
- Read completeness: 🟩 read in full; 🟨 partly read; 🟥 something unread.

</details>

---

**2 · Facts · written by code · no judgement**

## What it adds

🟢 read in full · 🟡 partly read · 🔴 something unread

<details><summary>🟢 <b>Injects</b> · 1 skills · ~3979 tokens on demand · ~571 chars of skill descriptions every session · hook text read in full</summary>

- Skills:
  - viral-launch: description every session (571 chars); the file on demand (15919 bytes, ~3979 tokens)
- Rule files: none
- Hook-injected text: none

</details>

<details><summary>🟢 <b>Hooks</b> · 0 hooks · read in full</summary>

- Hooks: none

</details>

<details><summary>🟢 <b>Subagents and commands</b> · no agents · 0 commands</summary>

- Agents: none
- Commands: none

</details>

<details><summary>🟢 <b>State it may leave</b> · 0 files that may write state</summary>

- Persistence candidates: none

</details>

<details><summary>🟢 <b>Reaches outside the session</b> · no MCP servers</summary>

- MCP servers: none

</details>

<details><summary>🟢 <b>Source</b> · plugin · viral-launch-pipeline 1.0.0 from plugin.json · commit 475705f · no marketplace</summary>

- Kind: plugin
- Name: viral-launch-pipeline (from plugin.json)
- Version: 1.0.0 (from plugin.json)
- plugin.json:
  - name and version, shown above
- Marketplace: none
- Commit: 475705f

</details>

Load timing is how Claude Code loads skills, not measured here. Tokens are estimated as bytes / 4; where the inventory fell back to a character count, "bytes" counts characters.

---

**3 · Positions · the plugin's own words · no judgement**

## Where it takes a position

> Read from the plugin's instruction files (skills, commands, agents, rule files) and from the template text of hooks that build their output at run time. Text a hook injects from elsewhere, or builds in code, is not quoted. Topics come from a fixed list, grouped by code, with no judgement.

<details><summary><b>Asking vs proceeding</b> · 10 · "If you don't know the launch date, write "unknown — ask use…"</summary>

- "If you don't know the launch date, write "unknown — ask user"." [`skills/viral-launch/prompts/01_brand_brief.md:12`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/01_brand_brief.md#L12)
- "❌ Filling OPEN QUESTIONS with trivia ("favorite color of founder?") — only ask what stages 2-21 actually need" [`skills/viral-launch/prompts/01_brand_brief.md:76`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/01_brand_brief.md#L76)
- "❌ \`competitor_terms: \["Notion", "ClickUp", "Asana", "Monday", "Linear", "Jira", "Trello"\]\` — pick 2-4 actual competitors, not a list of every tool in the space" [`skills/viral-launch/prompts/02_keywords.md:50`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/02_keywords.md#L50)
- "Pick a winner OR fail the iteration." [`skills/viral-launch/prompts/09_hook_manager.md:11`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/09_hook_manager.md#L11)
- "Pick the highest-scoring candidate" [`skills/viral-launch/prompts/09_hook_manager.md:53`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/09_hook_manager.md#L53)
- "If its score ≥ 8 AND \`three_question_pass = true\` AND no blocking issues → \`pass: true\`, \`winner_id: &lt;candidate_number>\`" [`skills/viral-launch/prompts/09_hook_manager.md:54`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/09_hook_manager.md#L54)
- "Pick pass or fail." [`skills/viral-launch/prompts/11_giveaway_manager.md:9`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/11_giveaway_manager.md#L9) (also in `skills/viral-launch/prompts/17_body_manager.md:11`)
- "Pick ONE place where a contrarian beat fits naturally (usually paragraph 4 "what changed under the hood" or paragraph 5 "metric")." [`skills/viral-launch/prompts/14_controversy_specialist.md:21`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/14_controversy_specialist.md#L21)
- "If exists, read it and pick a formula appropriate to the launch type." [`skills/viral-launch/prompts/21_deliver.md:23`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/21_deliver.md#L23)
- "**3 topics maximum.** Pick from PH's existing taxonomy (e.g. "Artificial Intelligence", "Productivity", "Developer Tools")." [`skills/viral-launch/references/channel-specs.md:109`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/channel-specs.md#L109)

</details>

<details><summary><b>Scope and size of changes</b> · 9 · "**Check for existing launch:**"</summary>

- "**Check for existing launch:**" [`skills/viral-launch/SKILL.md:60`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L60)
- "**Never edit a manager's critique to make it pass.** Honest scores even on iter 3 — the user accepts the iteration budget; you don't get to fudge it." [`skills/viral-launch/SKILL.md:242`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L242)
- "The recommended top-3 must include the highest-defensibility angle even if it's not the most emotional — Hook Writer needs options." [`skills/viral-launch/prompts/07_research_compiler.md:58`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/07_research_compiler.md#L58)
- "Preserve the 7-beat narrative structure from stage_12. Don't reorder." [`skills/viral-launch/prompts/13_weapons_specialist.md:64`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/13_weapons_specialist.md#L64)
- "**"We don't have a mobile app. We never will. {Product} is a tool for the 2 hours a day you're at your desk doing work that matters."** → counter-positions against "build for every platform" instinct" [`skills/viral-launch/prompts/14_controversy_specialist.md:52`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/14_controversy_specialist.md#L52)
- "❌ Over-adapting LinkedIn to look like a tweet — it's a different platform with different reading habits" [`skills/viral-launch/prompts/21_deliver.md:66`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/21_deliver.md#L66)
- "**No threading hashtags in tweet 1.** Hashtags reduce reach on X. Move to last tweet if at all." [`skills/viral-launch/references/channel-specs.md:13`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/channel-specs.md#L13)
- "**Why never existed?** Nothing — there are dozens already." [`skills/viral-launch/references/hook-three-question-test.md:27`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/hook-three-question-test.md#L27)
- "Do not regress on what already passed." [`skills/viral-launch/references/rubric-format.md:90`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/rubric-format.md#L90)

</details>

<details><summary><b>Tests</b> · 17 · "18 | mom_test | check (kicks back to 12) | no | 1 kickback …"</summary>

- "18 | mom_test | check (kicks back to 12) | no | 1 kickback budget" [`skills/viral-launch/SKILL.md:44`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L44)
- "Read \`stage_18_mom_test/output.md\`." [`skills/viral-launch/SKILL.md:167`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L167)
- "Read \`meta.json\` for \`iterations.18_mom_test\`." [`skills/viral-launch/SKILL.md:167`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L167)
- "The Mom Test is the only kickback that loops backward." [`skills/viral-launch/SKILL.md:183`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L183)
- "Avoid every disqualifier word listed in \`hook-three-question-test.md\`" [`skills/viral-launch/prompts/08_hook_writer.md:14`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/08_hook_writer.md#L14)
- "No disqualifier words from \`hook-three-question-test.md\`." [`skills/viral-launch/prompts/08_hook_writer.md:58`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/08_hook_writer.md#L58)
- "Hook must answer all 3 test questions with information IN the hook — not in a follow-up tweet." [`skills/viral-launch/prompts/08_hook_writer.md:59`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/08_hook_writer.md#L59)
- "Use \`rubric_used: "hook_three_question_test"\`." [`skills/viral-launch/prompts/09_hook_manager.md:21`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/09_hook_manager.md#L21)
- "(iter ≥ 2 only) \`stage_17_body_manager/critique_v{N-1}.json\` AND/OR \`stage_18_mom_test/kickbacks.md\`" [`skills/viral-launch/prompts/12_body_writer.md:8`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/12_body_writer.md#L8)
- "No em dashes. No disqualifier words from \`hook-three-question-test.md\`." [`skills/viral-launch/prompts/12_body_writer.md:74`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/12_body_writer.md#L74) (also in `skills/viral-launch/prompts/16_flow_specialist.md:53`)
- "**The Mom Test is the article's most important QA gate.** Launch content that goes viral (10M+ views) must be comprehensible to mass-market readers, not just to other founders in the bubble." [`skills/viral-launch/prompts/18_mom_test.md:11`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/18_mom_test.md#L11)
- "(optional, if file exists) \`hook-formulas.md\` (LinkedIn formula library; check via \`Bash test -f\` first)" [`skills/viral-launch/prompts/21_deliver.md:6`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/21_deliver.md#L6)
- "**Each file passes its own format checks** (char counts, tweet counts, no em dashes, etc.). Self-check before writing." [`skills/viral-launch/prompts/21_deliver.md:43`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/21_deliver.md#L43)
- "If \`hook-formulas.md\` exists (check via \`Bash test -f\`), pick one of:" [`skills/viral-launch/references/channel-specs.md:65`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/channel-specs.md#L65)
- "Every hook the pipeline produces must pass this test." [`skills/viral-launch/references/hook-three-question-test.md:3`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/hook-three-question-test.md#L3)
- "A hook can pass the 3-question test and still fail the rubric if the "why never existed" claim is **undefensible** by the brief or research." [`skills/viral-launch/references/hook-three-question-test.md:69`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/hook-three-question-test.md#L69)
- "Mom Test: \`stage_18_mom_test/output.md\` (always) and \`kickbacks.md\` (only if triggered)" [`skills/viral-launch/references/orchestrator-protocol.md:70`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/orchestrator-protocol.md#L70)

</details>

<details><summary><b>Code style and comments</b> · 15 · "`references/rubric-format.md` (the JSON schema you MUST fol…"</summary>

- "\`references/rubric-format.md\` (the JSON schema you MUST follow)" [`skills/viral-launch/prompts/09_hook_manager.md:7`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/09_hook_manager.md#L7)
- "Be **concrete and actionable.** Not "make it more novel" — instead "pivot all 5 candidates to lead with the verbatim pain quote from stage_05 line 42, drop all 'first' claims since competitor Foo inv…" [`skills/viral-launch/prompts/09_hook_manager.md:68`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/09_hook_manager.md#L68)
- "**Invention novelty** — does this line claim something specifically only THIS product can do (or do better than competitors), as opposed to generic marketing prose?" [`skills/viral-launch/prompts/13_weapons_specialist.md:10`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/13_weapons_specialist.md#L10)
- "**Copy intensity** — is this line sharp? Concrete? Specific? Does it use named entities, numbers, verbs? Or is it limp marketing fluff?" [`skills/viral-launch/prompts/13_weapons_specialist.md:11`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/13_weapons_specialist.md#L11)
- "A constraint: "trained on 4M lines of MIT-licensed code, no scraping"" [`skills/viral-launch/prompts/15_technical_specialist.md:17`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/15_technical_specialist.md#L17)
- "\`references/channel-specs.md\` (THE format spec for each channel — read this carefully)" [`skills/viral-launch/prompts/21_deliver.md:5`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/21_deliver.md#L5)
- "Each must hit the channel's exact format constraints from \`references/channel-specs.md\`." [`skills/viral-launch/prompts/21_deliver.md:14`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/21_deliver.md#L14)
- "The novelty angle must be the SAME across all three — only the format changes." [`skills/viral-launch/prompts/21_deliver.md:14`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/21_deliver.md#L14)
- "**Adapt for each channel separately.** Do NOT generate all three at once and then "tweak" — each format has different muscle." [`skills/viral-launch/prompts/21_deliver.md:24`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/21_deliver.md#L24)
- "All three must ship the same novelty angle, but with each channel's own format constraints." [`skills/viral-launch/references/channel-specs.md:3`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/channel-specs.md#L3)
- "**Each tweet ≤280 chars.** Use \`len()\` on each line before writing." [`skills/viral-launch/references/channel-specs.md:11`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/channel-specs.md#L11)
- "**Single post** (no carousel, no document). LinkedIn rewards single-format right now." [`skills/viral-launch/references/channel-specs.md:55`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/channel-specs.md#L55)
- "**No external links in the post body.** Links go in the first comment." [`skills/viral-launch/references/channel-specs.md:61`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/channel-specs.md#L61)
- "**Maker's first comment**: 3 paragraphs, no fluff." [`skills/viral-launch/references/channel-specs.md:108`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/channel-specs.md#L108)
- "If you disagree with a critique item, leave a 1-line \`&lt;!-- DISAGREE: &lt;reason> -->\` HTML comment next to the relevant candidate and address the next-most-actionable issue."" [`skills/viral-launch/references/rubric-format.md:90`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/rubric-format.md#L90)

</details>

<details><summary><b>Dependencies</b> · 2 · "A single tweet or short post → use `linkedin-post-writer` (…"</summary>

- "A single tweet or short post → use \`linkedin-post-writer\` (if installed) or write directly" [`skills/viral-launch/SKILL.md:17`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L17)
- "You have no other dependencies." [`skills/viral-launch/prompts/01_brand_brief.md:5`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/01_brand_brief.md#L5)

</details>

<details><summary><b>Commits and git</b> · 1 · "If the compiler's output includes `## Open contradictions s…"</summary>

- "If the compiler's output includes \`## Open contradictions surfaced\` with any items, surface those to the user before proceeding — they may need to amend the brief." [`skills/viral-launch/SKILL.md:95`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L95)

</details>

<details><summary><b>Reviews and audits</b> · 12 · "20 | final_review | single | no | 1"</summary>

- "20 | final_review | single | no | 1" [`skills/viral-launch/SKILL.md:46`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L46)
- "Writes \`stage_20_final_review/output.md\` (the master launch document)." [`skills/viral-launch/SKILL.md:195`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L195)
- ""Final Review locked. Deliver running for X + LinkedIn + PH."" [`skills/viral-launch/SKILL.md:305`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L305)
- "❌ Mixing in user reviews from G2/Capterra — those are different signal (use stage 6 for that)" [`skills/viral-launch/prompts/05_reddit_research.md:65`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/05_reddit_research.md#L65)
- "**Skin-in-the-game challenge** — "Reply with your hardest {use case}. We'll do it live. Best one wins {prize}."" [`skills/viral-launch/prompts/10_giveaway_writer.md:69`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/10_giveaway_writer.md#L69)
- ""We turned a 5-hour customer support shift into a 12-minute review queue."" [`skills/viral-launch/prompts/13_weapons_specialist.md:49`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/13_weapons_specialist.md#L49)
- "You do NOT auto-trigger kickbacks. Your verdict goes to the user (via main-Claude) for a decision. Supervisor signals are too coarse to auto-loop on." [`skills/viral-launch/prompts/19_call_supervisor.md:67`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/19_call_supervisor.md#L67)
- "**Body's demo moment uses a use case for ICP "A", but brief and hook target ICP "B"** — re-run stage 12" [`skills/viral-launch/prompts/19_call_supervisor.md:76`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/19_call_supervisor.md#L76)
- "\`stage_20_final_review/output.md\` (the master launch document)" [`skills/viral-launch/prompts/21_deliver.md:4`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/21_deliver.md#L4)
- "Stage 21 (\`deliver\`) reads \`stage_20_final_review/output.md\` (the master launch document) and adapts it into **three channel-specific artifacts**." [`skills/viral-launch/references/channel-specs.md:3`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/channel-specs.md#L3)
- "**Why never existed?** Implicit — review queue framing (you stay in the loop) is the novelty axis vs. full autopilot competitors" [`skills/viral-launch/references/hook-three-question-test.md:49`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/hook-three-question-test.md#L49)
- "20 final_review | stage_08/final, stage_10/final, stage_17/final, stage_19/output (both passes)" [`skills/viral-launch/references/orchestrator-protocol.md:61`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/orchestrator-protocol.md#L61)

</details>

<details><summary><b>Models and subagents</b> · 13 · "You dispatch 21 specialized subagents in sequence via the `…"</summary>

- "You dispatch 21 specialized subagents in sequence via the \`Agent\` tool, persist their artifacts to disk, and run manager-feedback loops." [`skills/viral-launch/SKILL.md:8`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L8)
- "Each "dispatch stage NN" means: build the wrapper prompt per \`references/orchestrator-protocol.md\` and invoke \`Agent(subagent_type="general-purpose", prompt=&lt;wrapper>)\`." [`skills/viral-launch/SKILL.md:53`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L53)
- "This is the only parallel batch in the entire pipeline. **In ONE assistant message, emit FOUR \`Agent\` tool calls** — one each for stages 03, 04, 05, 06." [`skills/viral-launch/SKILL.md:87`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L87)
- "**Never write launch copy yourself.** Every line of the launch goes through an \`Agent\` dispatch. Your job is the loop." [`skills/viral-launch/SKILL.md:233`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L233)
- "**Research batch (stages 3-6) MUST be one assistant message with 4 parallel Agent calls.** Otherwise you've spent 4× the wall time." [`skills/viral-launch/SKILL.md:237`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L237)
- "**If a subagent returns a summary that's ambiguous about success/failure → re-dispatch with a clarification prompt, or surface to user.** Never advance on uncertain state." [`skills/viral-launch/SKILL.md:241`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L241)
- "Extract 8-15 search keywords/phrases that the research agents (stages 3-6) will use as their \`WebSearch\` queries." [`skills/viral-launch/prompts/02_keywords.md:7`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/02_keywords.md#L7)
- "Before declaring \`deliver\` complete, the agent must verify:" [`skills/viral-launch/references/channel-specs.md:156`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/channel-specs.md#L156)
- "If any check fails, the agent rewrites and re-verifies before returning." [`skills/viral-launch/references/channel-specs.md:163`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/channel-specs.md#L163)
- "**Why never existed?** Context window constraint; only model X just made this feasible (defensible if true)" [`skills/viral-launch/references/hook-three-question-test.md:35`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/hook-three-question-test.md#L35)
- "Every \`Agent(subagent_type="general-purpose", prompt=...)\` call must use this exact wrapper template:" [`skills/viral-launch/references/orchestrator-protocol.md:7`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/orchestrator-protocol.md#L7)
- "Dependencies are passed as **paths** so the subagent can \`Read\` them selectively. Cheap, lets it skim." [`skills/viral-launch/references/orchestrator-protocol.md:34`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/orchestrator-protocol.md#L34)
- "**Stop at 12 results per agent.** More breadth doesn't beat the first 8-12 outliers." [`skills/viral-launch/references/search-query-templates.md:105`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/search-query-templates.md#L105)

</details>

<details><summary><b>Replies and reporting</b> · 39 · "**Extract product name** from the user message. Slugify per…"</summary>

- "**Extract product name** from the user message. Slugify per \`references/artifact-schema.md\` rules." [`skills/viral-launch/SKILL.md:59`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L59)
- "If \`new\`: \`mkdir -p ./launches/&lt;slug>/stage_01_brand_brief\` ... (create all 21 stage subdirs), write fresh \`meta.json\` (current_stage=1, completed_stages=\[\], iterations={}, status="in_progress"). Tel…" [`skills/viral-launch/SKILL.md:65`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L65)
- "If user said "resume": pick up at \`current_stage\`. Tell user: "Resuming &lt;product> from stage &lt;N> (&lt;stage_name>). &lt;X> stages completed."" [`skills/viral-launch/SKILL.md:68`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L68)
- "If user did not say "resume": ask the user (via plain text response, not a separate tool): "Found existing launch at \`./launches/&lt;slug>/\` (stage &lt;N>, status: &lt;status>). **Resume / Start fresh (\`-v2\` …" [`skills/viral-launch/SKILL.md:69`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L69)
- "**Confirm the launch parameters with user before stage 1:** product name (exact capitalization), one-line pitch, founder handle, launch date, channels (default: X + LinkedIn + ProductHunt — confirm o…" [`skills/viral-launch/SKILL.md:71`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L71)
- "Surface the report to the user" [`skills/viral-launch/SKILL.md:126`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L126)
- "Read the output and verify all checkmarks (☑) at the bottom are true." [`skills/viral-launch/SKILL.md:197`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L197)
- "In a final text response (no tool call), present:" [`skills/viral-launch/SKILL.md:210`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L210)
- "If meta.json says \`current_stage=12, iterations.12_body=2\` but only \`output_v1.md\` exists on disk → meta.json is ahead of disk; trust disk, fix meta." [`skills/viral-launch/SKILL.md:259`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L259)
- "If \`input.md\` is missing key facts, your output should include a \`## OPEN QUESTIONS\` section at the end listing them." [`skills/viral-launch/prompts/01_brand_brief.md:10`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/01_brand_brief.md#L10)
- "If the founder voice samples are absent, say so." [`skills/viral-launch/prompts/01_brand_brief.md:12`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/01_brand_brief.md#L12)
- "If category has no viral launches → say so explicitly in synthesis. Don't pad with weak examples." [`skills/viral-launch/prompts/04_twitter_research.md:47`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/04_twitter_research.md#L47)
- "❌ Quoting comments by what they "say" — must be verbatim" [`skills/viral-launch/prompts/05_reddit_research.md:63`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/05_reddit_research.md#L63)
- "Each angle's claim is ≤120 chars, written as the founder would say it." [`skills/viral-launch/prompts/07_research_compiler.md:55`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/07_research_compiler.md#L55)
- "\`stage_01_brand_brief/output.md\` (for defensibility check)" [`skills/viral-launch/prompts/09_hook_manager.md:5`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/09_hook_manager.md#L5)
- "\`stage_06_industry_research/output.md\` (for "is this claim actually new" check)" [`skills/viral-launch/prompts/09_hook_manager.md:6`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/09_hook_manager.md#L6)
- "\`urgency\` (1-10) — does it answer "why now"?" [`skills/viral-launch/prompts/09_hook_manager.md:46`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/09_hook_manager.md#L46)
- "Entry mechanic must require **public action** (reply / RT / tag) — DM-to-enter kills virality." [`skills/viral-launch/prompts/10_giveaway_writer.md:60`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/10_giveaway_writer.md#L60)
- "Fraud-risk check: the mechanic shouldn't reward bots — "reply with your story" is bot-resistant; "RT to enter" is not." [`skills/viral-launch/prompts/10_giveaway_writer.md:62`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/10_giveaway_writer.md#L62)
- "**Founder-curated access** — "10 lifetime seats, but I pick the winners from the best replies" (creates content)" [`skills/viral-launch/prompts/10_giveaway_writer.md:68`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/10_giveaway_writer.md#L68)
- "Output the full revised body — every line should now score ≥7 on both axes." [`skills/viral-launch/prompts/13_weapons_specialist.md:20`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/13_weapons_specialist.md#L20)
- "When it sees a refund request with order history under $200 and no flagged keywords, it drafts the reply in 8 seconds." [`skills/viral-launch/prompts/13_weapons_specialist.md:58`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/13_weapons_specialist.md#L58)
- "\`stage_01_brand_brief/output.md\` (defensibility check)" [`skills/viral-launch/prompts/14_controversy_specialist.md:5`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/14_controversy_specialist.md#L5)
- "\`stage_06_industry_research/output.md\` (the dead phrases competitors use)" [`skills/viral-launch/prompts/14_controversy_specialist.md:6`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/14_controversy_specialist.md#L6)
- "Inject **ONE contrarian edge** into the body — a paragraph or sentence that takes a defensible-but-uncomfortable position that the competitor wouldn't say." [`skills/viral-launch/prompts/14_controversy_specialist.md:9`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/14_controversy_specialist.md#L9)
- "If you can't find a defensible contrarian beat, write \`## NO CONTRARIAN BEAT POSSIBLE\` and explain why (e.g. "product genuinely doesn't disagree with the market consensus on anything"). Stage 17 mana…" [`skills/viral-launch/prompts/14_controversy_specialist.md:69`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/14_controversy_specialist.md#L69)
- "Re-read the launch body **as Margaret** — a 61-year-old retired nurse who uses email and Facebook, has never written a line of code, doesn't know what an "API" is, can't tell a "database" from a "spr…" [`skills/viral-launch/prompts/18_mom_test.md:7`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/18_mom_test.md#L7)
- "Read the locked artifacts and answer:" [`skills/viral-launch/prompts/19_call_supervisor.md:19`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/19_call_supervisor.md#L19)
- "If a slug collides with an existing directory and the user does NOT say "resume", append \`-v2\`, \`-v3\`, … until free." [`skills/viral-launch/references/artifact-schema.md:12`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/artifact-schema.md#L12)
- "A hook is a pass **only** if, after reading it once with no other context, a stranger can answer all three:" [`skills/viral-launch/references/hook-three-question-test.md:7`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/hook-three-question-test.md#L7)
- "If the reader can only answer 2 of 3 → fail." [`skills/viral-launch/references/hook-three-question-test.md:13`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/hook-three-question-test.md#L13)
- "If they answer all 3 → pass on this axis (score still depends on clarity, urgency, voice)." [`skills/viral-launch/references/hook-three-question-test.md:13`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/hook-three-question-test.md#L13)
- "A mechanism the founder can explain in one sentence" [`skills/viral-launch/references/hook-three-question-test.md:80`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/hook-three-question-test.md#L80)
- "Worker non-iterated: \`stage_NN_&lt;name>/output.md\`" [`skills/viral-launch/references/orchestrator-protocol.md:66`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/orchestrator-protocol.md#L66)
- "Worker iterated: \`stage_NN_&lt;name>/output_v{N}.md\` and on pass also \`stage_NN_&lt;name>/final.md\`" [`skills/viral-launch/references/orchestrator-protocol.md:67`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/orchestrator-protocol.md#L67)
- "\`urgency\` — does it answer "why now"?" [`skills/viral-launch/references/rubric-format.md:58`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/rubric-format.md#L58)
- "**Output:** \`## Verbatim pain quotes\` section + \`## User vocabulary\` section + \`## Active subreddits\` list." [`skills/viral-launch/references/search-query-templates.md:78`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/search-query-templates.md#L78)
- "**Output:** markdown competitor matrix (cols: name, headline, sub-headline, CTA, entry price) + 1-paragraph "positioning gap": which axis is empty? what is every competitor saying that the user could…" [`skills/viral-launch/references/search-query-templates.md:98`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/search-query-templates.md#L98)
- "**Flag dead ends to the orchestrator.** If a category has no viral launches on X, say so explicitly in the synthesis paragraph — the Hook Writer needs to know it's working in a virgin niche." [`skills/viral-launch/references/search-query-templates.md:106`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/search-query-templates.md#L106)

</details>

<details><summary><b>State and files</b> · 20 · "Count jargon flags."</summary>

- "Count jargon flags." [`skills/viral-launch/SKILL.md:167`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L167)
- "Read each file briefly to confirm format compliance (hook ≤280 in x_thread, char count in linkedin_post, tagline ≤60 in producthunt)" [`skills/viral-launch/SKILL.md:205`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L205)
- "(Use emojis here only because the user opted into a richer presentation moment; do not use them in artifact files.)" [`skills/viral-launch/SKILL.md:229`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L229)
- "Don't paste artifact contents into the chat; the user can read them on disk." [`skills/viral-launch/SKILL.md:307`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L307)
- "You write TWO files:" [`skills/viral-launch/prompts/09_hook_manager.md:17`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/09_hook_manager.md#L17)
- "On pass, you MUST write \`final.md\` in \`stage_10_giveaway_writer/\` — orchestrator depends on this path." [`skills/viral-launch/prompts/11_giveaway_manager.md:66`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/11_giveaway_manager.md#L66)
- "Every novelty claim traces to stage_01 brief or stage_07 angles. If you need a claim that isn't in either, flag with \`&lt;!-- NEEDS_BRIEF_FACT: {what} -->\` HTML comment." [`skills/viral-launch/prompts/12_body_writer.md:73`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/12_body_writer.md#L73)
- "Note: you write to the **body_writer** stage directory, not your own." [`skills/viral-launch/prompts/13_weapons_specialist.md:26`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/13_weapons_specialist.md#L26)
- "You source these from \`stage_01_brief\` only. **Never fabricate.** If a credibility hole exists (a claim that the brief doesn't substantiate), flag it in a \`## TECHNICAL_GAPS\` section at the bottom." [`skills/viral-launch/prompts/15_technical_specialist.md:10`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/15_technical_specialist.md#L10)
- "On pass, you MUST write \`stage_12_body_writer/final.md\` (not in your own stage directory)." [`skills/viral-launch/prompts/17_body_manager.md:68`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/17_body_manager.md#L68)
- "Flag a term if Margaret would skip it OR feel stupid." [`skills/viral-launch/prompts/18_mom_test.md:54`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/18_mom_test.md#L54)
- "Acronyms = always flag (API, SaaS, GPU, LLM, REST, JSON, CSV, etc.) unless the surrounding sentence defines them." [`skills/viral-launch/prompts/18_mom_test.md:58`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/18_mom_test.md#L58)
- "Different word choices — only flag if the underlying claims differ" [`skills/viral-launch/prompts/19_call_supervisor.md:82`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/19_call_supervisor.md#L82)
- "You write THREE files (paths exact):" [`skills/viral-launch/prompts/21_deliver.md:29`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/21_deliver.md#L29)
- "**All three files must exist** before you return success. Missing one = task failure." [`skills/viral-launch/prompts/21_deliver.md:42`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/21_deliver.md#L42)
- "All runtime artifacts live under the user's current working directory at \`./launches/&lt;slug>/\`. **The plugin itself never writes inside its own install directory.**" [`skills/viral-launch/references/artifact-schema.md:3`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/artifact-schema.md#L3)
- "**No em dashes** anywhere (em-dash heuristic flags AI on LinkedIn)." [`skills/viral-launch/references/channel-specs.md:60`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/channel-specs.md#L60)
- "Mutate in memory: bump \`current_stage\`, append to \`completed_stages\`, increment relevant \`iterations\` counter, set \`last_updated = now()\`" [`skills/viral-launch/references/orchestrator-protocol.md:78`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/orchestrator-protocol.md#L78)
- "A pass=true critique **must** also write \`final.md\` in the sibling worker's directory containing only the winning artifact (no commentary, no scores)." [`skills/viral-launch/references/rubric-format.md:51`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/rubric-format.md#L51)
- "When the orchestrator dispatches iteration N>1 of the worker, the wrapper's \`DEPENDENCY_FILE_LIST\` includes the previous \`critique_v{N-1}.json\`." [`skills/viral-launch/references/rubric-format.md:88`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/rubric-format.md#L88)

</details>

<details><summary><b>Network</b> · 11 · "Reference [[1]](https://x.com/) — the article this implemen…"</summary>

- "Reference \[\[1\]\](https://x.com/) — the article this implements states explicitly: *"Claude is not allowed to just 'write the launch.' That is how you get AI slop."*" [`skills/viral-launch/SKILL.md:8`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L8)
- "**Update meta.json after every successful Agent return.** No exceptions — this is what makes resumability work." [`skills/viral-launch/SKILL.md:236`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L236)
- "Keep updates SHORT." [`skills/viral-launch/SKILL.md:298`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L298)
- "\`input.md\` in your stage directory contains whatever raw facts the user provided to main-Claude (product URL, founder name, rough pitch, etc.)." [`skills/viral-launch/prompts/01_brand_brief.md:4`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/01_brand_brief.md#L4)
- "Every row in the table must have a real URL in the \`## Sources\` list." [`skills/viral-launch/prompts/03_youtube_research.md:51`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/03_youtube_research.md#L51)
- "Distinguish between "launch tweet" (product debut) and "milestone tweet" (post-launch update). Prefer launch tweets." [`skills/viral-launch/prompts/04_twitter_research.md:46`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/04_twitter_research.md#L46)
- "**Every quote MUST have a permalink.** If WebSearch only gives you a snippet, \`WebFetch\` the thread URL to recover the quote in context." [`skills/viral-launch/prompts/05_reddit_research.md:55`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/05_reddit_research.md#L55)
- ""Cross-channel facts" must be derived directly from stage_01 brief. If brief disagrees with what's currently in the body (e.g. founder's @ handle), update the body and log in micro-fixes." [`skills/viral-launch/prompts/20_final_review.md:98`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/20_final_review.md#L98)
- "❌ Forgetting to update product name capitalization if the body has it wrong" [`skills/viral-launch/prompts/20_final_review.md:106`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/20_final_review.md#L106)
- "Each agent must run **at least 4 distinct search queries**, then \`WebFetch\` the top 2-3 URLs from the highest-signal results." [`skills/viral-launch/references/search-query-templates.md:3`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/search-query-templates.md#L3)
- "**WebSearch first, WebFetch only on the top 2-3 URLs.** Each WebFetch is expensive — pick the highest-signal ones." [`skills/viral-launch/references/search-query-templates.md:104`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/search-query-templates.md#L104)

</details>

<details><summary><b>Safety and permissions</b> · 2 · "❌ Writing "they all do similar things" — that's the lazy ve…"</summary>

- "❌ Writing "they all do similar things" — that's the lazy version. Force yourself to find the specific empty axis." [`skills/viral-launch/prompts/06_industry_research.md:59`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/06_industry_research.md#L59)
- "❌ Refusing to rank because "they're all good" — force a ranking; downstream needs decisiveness" [`skills/viral-launch/prompts/07_research_compiler.md:65`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/07_research_compiler.md#L65)

</details>

<details><summary><b>other</b> · 181 · "You do **not** write launch copy yourself."</summary>

- "You do **not** write launch copy yourself." [`skills/viral-launch/SKILL.md:8`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L8)
- "**Use this skill when:**" [`skills/viral-launch/SKILL.md:12`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L12)
- "**Do NOT use this skill for:**" [`skills/viral-launch/SKILL.md:16`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L16)
- "A LinkedIn-only post (no X/PH planned) → use \`linkedin-post-writer\`" [`skills/viral-launch/SKILL.md:19`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L19)
- "1 | brand_brief | single | no | 1" [`skills/viral-launch/SKILL.md:26`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L26)
- "2 | keywords | single | no | 1" [`skills/viral-launch/SKILL.md:27`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L27)
- "7 | research_compiler | single | no | 1" [`skills/viral-launch/SKILL.md:32`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L32)
- "8 | hook_writer | worker (→ 9) | no | 3" [`skills/viral-launch/SKILL.md:33`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L33)
- "9 | hook_manager | manager (← 8) | no | —" [`skills/viral-launch/SKILL.md:34`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L34)
- "10 | giveaway_writer | worker (→ 11) | no | 3" [`skills/viral-launch/SKILL.md:35`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L35)
- "11 | giveaway_manager | manager (← 10) | no | —" [`skills/viral-launch/SKILL.md:36`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L36)
- "19 | call_supervisor (mid) | meta | no | 1" [`skills/viral-launch/SKILL.md:37`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L37)
- "12 | body_writer | worker (→ 17, chain 13-16) | no | 3" [`skills/viral-launch/SKILL.md:38`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L38)
- "13 | weapons_specialist | specialist (mutates 12) | no | 1 per body iter" [`skills/viral-launch/SKILL.md:39`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L39)
- "14 | controversy_specialist | specialist | no | 1 per body iter" [`skills/viral-launch/SKILL.md:40`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L40)
- "15 | technical_specialist | specialist | no | 1 per body iter" [`skills/viral-launch/SKILL.md:41`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L41)
- "16 | flow_specialist | specialist | no | 1 per body iter" [`skills/viral-launch/SKILL.md:42`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L42)
- "17 | body_manager | manager (← 12, kicks back to 12) | no | —" [`skills/viral-launch/SKILL.md:43`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L43)
- "19 | call_supervisor (late) | meta | no | 1" [`skills/viral-launch/SKILL.md:45`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L45)
- "21 | deliver | single (multi-channel) | no | 1" [`skills/viral-launch/SKILL.md:47`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L47)
- "Read \`meta.json\`" [`skills/viral-launch/SKILL.md:67`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L67)
- "Loop until the brief has no open questions." [`skills/viral-launch/SKILL.md:77`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L77)
- "**Stage 19 Call Supervisor never auto-kicks-back.** Its FAIL verdicts always surface to the user." [`skills/viral-launch/SKILL.md:239`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L239)
- "**If a manager doesn't write \`final.md\` on pass → halt.** This is an integrity check; downstream stages depend on \`final.md\` paths." [`skills/viral-launch/SKILL.md:240`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L240)
- "The \`iterations\` map in meta.json tracks each worker's iteration count." [`skills/viral-launch/SKILL.md:257`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/SKILL.md#L257)
- "Do NOT fabricate facts." [`skills/viral-launch/prompts/01_brand_brief.md:12`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/01_brand_brief.md#L12)
- "Use these exact headings, in this order:" [`skills/viral-launch/prompts/01_brand_brief.md:16`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/01_brand_brief.md#L16)
- "No marketing language in your own writing: just facts" [`skills/viral-launch/prompts/01_brand_brief.md:70`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/01_brand_brief.md#L70)
- "If the product is "Cursor 2.0" but normal people search for "AI code editor", use "AI code editor" as a category term." [`skills/viral-launch/prompts/02_keywords.md:9`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/02_keywords.md#L9)
- "The keywords must be **searchable in the wild** — not internal product names." [`skills/viral-launch/prompts/02_keywords.md:9`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/02_keywords.md#L9)
- "**Use quotes** around multi-word phrases that should be searched as a unit." [`skills/viral-launch/prompts/02_keywords.md:44`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/02_keywords.md#L44)
- "**No marketing words** — "intelligent X", "AI-powered Y" — those don't appear in search history." [`skills/viral-launch/prompts/02_keywords.md:45`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/02_keywords.md#L45)
- "❌ Reusing the product's own name in \`category_terms\` — that's not how strangers search" [`skills/viral-launch/prompts/02_keywords.md:52`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/02_keywords.md#L52)
- "Find 8-12 viral video **outliers** in this product's adjacent categories." [`skills/viral-launch/prompts/03_youtube_research.md:8`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/03_youtube_research.md#L8)
- "\`WebSearch\` — run AT LEAST the 4 queries listed in the search templates" [`skills/viral-launch/prompts/03_youtube_research.md:13`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/03_youtube_research.md#L13)
- "No fabrication. If a query returns nothing, log "No results for: {query}"." [`skills/viral-launch/prompts/03_youtube_research.md:15`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/03_youtube_research.md#L15)
- ""Why it's an outlier" must reference *something* about the channel's typical performance (estimate ok: "this channel usually gets 5-10k views, this hit 800k")." [`skills/viral-launch/prompts/03_youtube_research.md:52`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/03_youtube_research.md#L52)
- "If you cannot find 8 outliers, write only what you have and add a \`## DEAD ENDS\` section listing the queries that returned nothing — downstream Hook Writer needs to know it's working in a virgin nich…" [`skills/viral-launch/prompts/03_youtube_research.md:53`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/03_youtube_research.md#L53)
- "Find 8-12 viral product **launches** on X/Twitter in this product's category or adjacent." [`skills/viral-launch/prompts/04_twitter_research.md:8`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/04_twitter_research.md#L8)
- "\`WebSearch\` — run all 4 primary queries from the template, plus nitter.net fallback if X results are sparse" [`skills/viral-launch/prompts/04_twitter_research.md:11`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/04_twitter_research.md#L11)
- "No fabrication." [`skills/viral-launch/prompts/04_twitter_research.md:13`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/04_twitter_research.md#L13) (also in `skills/viral-launch/prompts/06_industry_research.md:13`)
- "Tweet 1 hook must be VERBATIM (with quotes around it). Paraphrase = fail downstream." [`skills/viral-launch/prompts/04_twitter_research.md:44`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/04_twitter_research.md#L44)
- "\`WebSearch\` — run the 4 primary queries plus 2-3 subreddit-targeted queries" [`skills/viral-launch/prompts/05_reddit_research.md:11`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/05_reddit_research.md#L11)
- "No fabrication. Made-up Reddit quotes are an instant launch killer." [`skills/viral-launch/prompts/05_reddit_research.md:13`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/05_reddit_research.md#L13)
- "Quotes ≤120 chars. Trim with \`\[…\]\` if needed; don't paraphrase." [`skills/viral-launch/prompts/05_reddit_research.md:56`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/05_reddit_research.md#L56)
- "Keep typos, lowercase, casual punctuation — that's the voice. Fixing it loses the signal." [`skills/viral-launch/prompts/05_reddit_research.md:57`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/05_reddit_research.md#L57)
- "5-10 quotes, no more. The Hook Writer doesn't have time to read 30." [`skills/viral-launch/prompts/05_reddit_research.md:58`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/05_reddit_research.md#L58)
- "If the category is too quiet on Reddit (e.g. very niche B2B), write \`## DEAD ENDS\` listing the queries that produced nothing. Don't pad." [`skills/viral-launch/prompts/05_reddit_research.md:59`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/05_reddit_research.md#L59)
- "Headlines must be VERBATIM with quotes. Paraphrasing destroys the dead-phrase analysis." [`skills/viral-launch/prompts/06_industry_research.md:50`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/06_industry_research.md#L50)
- ""Positioning gap" must be specific and actionable — not "no one is doing X really well", but "no competitor mentions Y on their homepage"." [`skills/viral-launch/prompts/06_industry_research.md:52`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/06_industry_research.md#L52)
- "If pricing is gated behind a sales call ("contact us"), write that exactly — it's signal for the giveaway stage." [`skills/viral-launch/prompts/06_industry_research.md:53`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/06_industry_research.md#L53)
- "Read all four research outputs and synthesize **5-8 novelty angles** the launch could lead with." [`skills/viral-launch/prompts/07_research_compiler.md:11`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/07_research_compiler.md#L11)
- "Emotional charge × Defensibility × Contrarian is intuitive, not formal — your overall ranking should be your honest gut feeling about which angle a Twitter audience would care about, NOT a mechanical…" [`skills/viral-launch/prompts/07_research_compiler.md:57`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/07_research_compiler.md#L57)
- "❌ "First X" claims with no evidence — defensibility =1, will fail in stage 9 anyway" [`skills/viral-launch/prompts/07_research_compiler.md:64`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/07_research_compiler.md#L64)
- "(iter ≥ 2 only) \`stage_08_hook_writer/critique_v{N-1}.json\` — address every BLOCKING and MAJOR issue" [`skills/viral-launch/prompts/08_hook_writer.md:7`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/08_hook_writer.md#L7)
- "Write **5 hook candidates** for the product launch." [`skills/viral-launch/prompts/08_hook_writer.md:10`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/08_hook_writer.md#L10)
- "Each candidate must:" [`skills/viral-launch/prompts/08_hook_writer.md:10`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/08_hook_writer.md#L10)
- "Fit in ≤280 chars (X tweet 1 hard limit)" [`skills/viral-launch/prompts/08_hook_writer.md:11`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/08_hook_writer.md#L11)
- "Five candidates from at least **two different top-3 angles** — don't write 5 variations on the same one." [`skills/viral-launch/prompts/08_hook_writer.md:16`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/08_hook_writer.md#L16)
- "5 candidates, no more, no fewer." [`skills/viral-launch/prompts/08_hook_writer.md:55`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/08_hook_writer.md#L55)
- "Each candidate ≤280 chars (count yourself before submitting)." [`skills/viral-launch/prompts/08_hook_writer.md:56`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/08_hook_writer.md#L56)
- "Mix these — don't use the same pattern across all 5." [`skills/viral-launch/prompts/08_hook_writer.md:71`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/08_hook_writer.md#L71)
- "You write a critique + rewrite guidance the writer can act on." [`skills/viral-launch/prompts/09_hook_manager.md:13`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/09_hook_manager.md#L13)
- "You do not rewrite." [`skills/viral-launch/prompts/09_hook_manager.md:13`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/09_hook_manager.md#L13)
- "Contains ONLY the winning hook, no commentary:" [`skills/viral-launch/prompts/09_hook_manager.md:29`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/09_hook_manager.md#L29)
- "Makes a "first/only X" claim that stage_06 industry research contradicts" [`skills/viral-launch/prompts/09_hook_manager.md:61`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/09_hook_manager.md#L61)
- "You don't write hooks. You write critiques." [`skills/viral-launch/prompts/09_hook_manager.md:74`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/09_hook_manager.md#L74)
- "The critique JSON must be valid JSON (no trailing commas, all strings quoted)." [`skills/viral-launch/prompts/09_hook_manager.md:75`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/09_hook_manager.md#L75)
- "On pass, you MUST write \`final.md\` — otherwise orchestrator can't advance." [`skills/viral-launch/prompts/09_hook_manager.md:76`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/09_hook_manager.md#L76)
- "If 5/5 candidates have blocking issues, score them honestly low. Don't soft-pass to escape the iteration." [`skills/viral-launch/prompts/09_hook_manager.md:77`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/09_hook_manager.md#L77)
- "(iter ≥ 2 only) \`stage_10_giveaway_writer/critique_v{N-1}.json\`" [`skills/viral-launch/prompts/10_giveaway_writer.md:7`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/10_giveaway_writer.md#L7)
- "The giveaway must:" [`skills/viral-launch/prompts/10_giveaway_writer.md:10`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/10_giveaway_writer.md#L10)
- "**Reinforce the hook's promise.** If the hook claims "first AI X", the giveaway should reward people for showing they need an "AI X"." [`skills/viral-launch/prompts/10_giveaway_writer.md:11`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/10_giveaway_writer.md#L11)
- "**Have a clear entry mechanic** — what the entrant must do to enter." [`skills/viral-launch/prompts/10_giveaway_writer.md:14`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/10_giveaway_writer.md#L14)
- "Prize must be **concrete**, not "credits" or "discount" or "swag" (those don't move people)." [`skills/viral-launch/prompts/10_giveaway_writer.md:59`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/10_giveaway_writer.md#L59)
- "Quantity × fulfillment-time must be realistic (don't promise 50 founder calls)." [`skills/viral-launch/prompts/10_giveaway_writer.md:61`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/10_giveaway_writer.md#L61)
- "Patterns that DON'T work:" [`skills/viral-launch/prompts/10_giveaway_writer.md:72`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/10_giveaway_writer.md#L72)
- "\`stage_08_hook_writer/final.md\` (to check hook-giveaway alignment)" [`skills/viral-launch/prompts/11_giveaway_manager.md:5`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/11_giveaway_manager.md#L5)
- "Use \`rubric_used: "giveaway"\`." [`skills/viral-launch/prompts/11_giveaway_manager.md:15`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/11_giveaway_manager.md#L15)
- "Pass requires \`score ≥ 8\` AND no blocking issues." [`skills/viral-launch/prompts/11_giveaway_manager.md:26`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/11_giveaway_manager.md#L26) (also in `skills/viral-launch/prompts/17_body_manager.md:30`)
- "Giveaway has no logical connection to the hook's claim — \`on_brand\` ≤ 3" [`skills/viral-launch/prompts/11_giveaway_manager.md:55`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/11_giveaway_manager.md#L55)
- "You don't redesign giveaways. You score and critique." [`skills/viral-launch/prompts/11_giveaway_manager.md:64`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/11_giveaway_manager.md#L64)
- "The critique JSON must be valid JSON." [`skills/viral-launch/prompts/11_giveaway_manager.md:65`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/11_giveaway_manager.md#L65)
- "(iter ≥ 2 only) \`stage_12_body_writer/input.md\` may have appended jargon replacement instructions" [`skills/viral-launch/prompts/12_body_writer.md:9`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/12_body_writer.md#L9)
- "Write the strong base, they polish." [`skills/viral-launch/prompts/12_body_writer.md:14`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/12_body_writer.md#L14)
- "Don't try to do their jobs." [`skills/viral-launch/prompts/12_body_writer.md:14`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/12_body_writer.md#L14)
- "**Giveaway tie-in** (1-2 sentences) — natural beat to mention the giveaway. Should feel like a continuation, not a bolt-on." [`skills/viral-launch/prompts/12_body_writer.md:23`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/12_body_writer.md#L23)
- "The giveaway tie-in must reference the giveaway by what it IS, not just "we're running a giveaway"." [`skills/viral-launch/prompts/12_body_writer.md:75`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/12_body_writer.md#L75)
- "❌ Multiple CTAs → reader picks none; one CTA only" [`skills/viral-launch/prompts/12_body_writer.md:83`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/12_body_writer.md#L83)
- "Read the body." [`skills/viral-launch/prompts/13_weapons_specialist.md:17`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/13_weapons_specialist.md#L17)
- "Don't preserve filler." [`skills/viral-launch/prompts/13_weapons_specialist.md:22`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/13_weapons_specialist.md#L22)
- "Intensity 9: concrete number, concrete action, no fluff" [`skills/viral-launch/prompts/13_weapons_specialist.md:51`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/13_weapons_specialist.md#L51)
- "Don't add new claims that weren't in stage_01 brief or stage_07 angles. You sharpen, you don't invent." [`skills/viral-launch/prompts/13_weapons_specialist.md:63`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/13_weapons_specialist.md#L63)
- "Word count can drop 10-30% (filler removal) but shouldn't grow." [`skills/viral-launch/prompts/13_weapons_specialist.md:65`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/13_weapons_specialist.md#L65)
- "The contrarian beat must be:" [`skills/viral-launch/prompts/14_controversy_specialist.md:13`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/14_controversy_specialist.md#L13)
- "**Counter-positioning** against the dead phrases from stage_06 — saying out loud what competitors avoid" [`skills/viral-launch/prompts/14_controversy_specialist.md:15`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/14_controversy_specialist.md#L15)
- "**Embedded in the narrative** — not a standalone "hot take", but a beat that strengthens the demo or mechanism" [`skills/viral-launch/prompts/14_controversy_specialist.md:16`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/14_controversy_specialist.md#L16)
- "Read the body and the stage_06 dead-phrase list." [`skills/viral-launch/prompts/14_controversy_specialist.md:20`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/14_controversy_specialist.md#L20)
- "Write the contrarian beat." [`skills/viral-launch/prompts/14_controversy_specialist.md:22`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/14_controversy_specialist.md#L22)
- "**"The first version cost us $84 in API credits per user. We kept the architecture anyway, because the alternative was the same dumb autocomplete every competitor ships."** → counter-positions agains…" [`skills/viral-launch/prompts/14_controversy_specialist.md:54`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/14_controversy_specialist.md#L54)
- "❌ "We think AI is overhyped." — too abstract, no defensible specific" [`skills/viral-launch/prompts/14_controversy_specialist.md:60`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/14_controversy_specialist.md#L60)
- "No insult of named competitors. Counter-position against the *pattern*, not the company." [`skills/viral-launch/prompts/14_controversy_specialist.md:68`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/14_controversy_specialist.md#L68)
- "Add **2-4 credibility details** to the body — concrete numbers, mechanisms, named technologies, or benchmarks that make the novelty claim feel earned." [`skills/viral-launch/prompts/15_technical_specialist.md:8`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/15_technical_specialist.md#L8)
- "A named mechanism: "we use tree-sitter to parse the call graph, not regex"" [`skills/viral-launch/prompts/15_technical_specialist.md:15`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/15_technical_specialist.md#L15)
- "❌ "Industry-leading performance" — no, that's marketing" [`skills/viral-launch/prompts/15_technical_specialist.md:22`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/15_technical_specialist.md#L22)
- "❌ "Best-in-class architecture" — no" [`skills/viral-launch/prompts/15_technical_specialist.md:23`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/15_technical_specialist.md#L23)
- "**2-4 details only.** Five+ turns the body into a spec sheet." [`skills/viral-launch/prompts/15_technical_specialist.md:52`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/15_technical_specialist.md#L52)
- "Insert at natural beats — usually paragraphs 3 (demo), 4 (mechanism), 5 (metric). Don't dump them all in one paragraph." [`skills/viral-launch/prompts/15_technical_specialist.md:54`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/15_technical_specialist.md#L54)
- "Kill repeated sentence starts (no two consecutive sentences start with the same word; no paragraph has 3 sentences starting with "We")" [`skills/viral-launch/prompts/16_flow_specialist.md:11`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/16_flow_specialist.md#L11)
- "Tighten transitions between paragraphs (the last sentence of paragraph N should make the first sentence of paragraph N+1 feel inevitable)" [`skills/viral-launch/prompts/16_flow_specialist.md:12`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/16_flow_specialist.md#L12)
- "Cut filler words ("really", "very", "just", "actually" when they add nothing)" [`skills/viral-launch/prompts/16_flow_specialist.md:13`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/16_flow_specialist.md#L13)
- "Replace abstract verbs with concrete ones ("utilize" → "use"; "leverages" → "uses"; "facilitates" → "lets")" [`skills/viral-launch/prompts/16_flow_specialist.md:14`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/16_flow_specialist.md#L14)
- "What you DO NOT do:" [`skills/viral-launch/prompts/16_flow_specialist.md:16`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/16_flow_specialist.md#L16)
- "Add new facts" [`skills/viral-launch/prompts/16_flow_specialist.md:17`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/16_flow_specialist.md#L17)
- "Word count should DROP or stay flat — never grow. Flow polish is about cutting filler." [`skills/viral-launch/prompts/16_flow_specialist.md:51`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/16_flow_specialist.md#L51)
- "The preservation check at the bottom must be honestly filled — if you accidentally cut a credibility detail, restore it before submitting." [`skills/viral-launch/prompts/16_flow_specialist.md:54`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/16_flow_specialist.md#L54)
- "❌ Adding new transitional phrases that pad ("In conclusion,", "To summarize,") — cut, don't add" [`skills/viral-launch/prompts/16_flow_specialist.md:58`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/16_flow_specialist.md#L58)
- "❌ Replacing a strong verb with a weaker one for "flow" — never weaken" [`skills/viral-launch/prompts/16_flow_specialist.md:59`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/16_flow_specialist.md#L59)
- "Use \`rubric_used: "body"\`." [`skills/viral-launch/prompts/17_body_manager.md:17`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/17_body_manager.md#L17)
- "\`no_ai_slop\` (1-10) — zero disqualifier words / dead phrases?" [`skills/viral-launch/prompts/17_body_manager.md:25`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/17_body_manager.md#L25)
- "\`no_brief_contradictions\` (1-10) — no facts contradict stage_01?" [`skills/viral-launch/prompts/17_body_manager.md:26`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/17_body_manager.md#L26)
- "Multiple CTAs OR no CTA → \`cta_clear\` ≤ 4" [`skills/viral-launch/prompts/17_body_manager.md:54`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/17_body_manager.md#L54)
- "Word count &lt;500 or >1100" [`skills/viral-launch/prompts/17_body_manager.md:57`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/17_body_manager.md#L57)
- "Keep paragraphs 1, 2, 5, 6, 7 intact (they passed)." [`skills/viral-launch/prompts/17_body_manager.md:62`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/17_body_manager.md#L62)
- "You don't rewrite the body. You critique." [`skills/viral-launch/prompts/17_body_manager.md:66`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/17_body_manager.md#L66)
- "If \`score = 7\` with no blocking issues and the body would be passable for a less-ambitious launch, still mark \`pass: false\` — the project standard is 8+. Surface the gap honestly." [`skills/viral-launch/prompts/17_body_manager.md:70`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/17_body_manager.md#L70)
- "The suggested replacement must preserve the original sentence's TRUTH — don't replace "tree-sitter" with "magic" just to make Margaret happy." [`skills/viral-launch/prompts/18_mom_test.md:57`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/18_mom_test.md#L57)
- "Named tools she's never heard of (Postgres, Redis, Kafka, Vercel, Cursor, etc.) unless they're the product itself" [`skills/viral-launch/prompts/18_mom_test.md:76`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/18_mom_test.md#L76)
- "❌ Flagging the product's own name — that's the brand, leave it" [`skills/viral-launch/prompts/18_mom_test.md:81`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/18_mom_test.md#L81)
- "❌ Flagging fewer than 3 just to avoid the kickback — be honest; the orchestrator handles the budget" [`skills/viral-launch/prompts/18_mom_test.md:83`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/18_mom_test.md#L83)
- "FAIL verdicts MUST include a specific recommendation (which stage to re-run, OR "consciously accept the drift because X")." [`skills/viral-launch/prompts/19_call_supervisor.md:70`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/19_call_supervisor.md#L70)
- "**Hook says "first to do X", body's demo doesn't actually show X** — re-run stage 12" [`skills/viral-launch/prompts/19_call_supervisor.md:74`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/19_call_supervisor.md#L74)
- "**Body's CTA contradicts giveaway timing** (e.g. CTA = "join the waitlist" but giveaway requires "use it today") — re-run stage 10 or 12" [`skills/viral-launch/prompts/19_call_supervisor.md:77`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/19_call_supervisor.md#L77)
- "Capitalization (product names, company names, founder names — match stage_01 brief exactly)" [`skills/viral-launch/prompts/20_final_review.md:16`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/20_final_review.md#L16)
- "**You do not rewrite.** Polish only." [`skills/viral-launch/prompts/20_final_review.md:95`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/20_final_review.md#L95)
- "All checkmarks at the bottom must be true (☑) before you return. If any is false, log the issue in \`## Micro-fixes applied\` with status "UNRESOLVED — escalate to user" and main-Claude will halt." [`skills/viral-launch/prompts/20_final_review.md:96`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/20_final_review.md#L96)
- "The hook, body, and giveaway are LOCKED. Touch only typos, capitalization, and a single transition sentence if needed." [`skills/viral-launch/prompts/20_final_review.md:97`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/20_final_review.md#L97)
- "**Read \`references/channel-specs.md\`** in full. The constraints there are exhaustive." [`skills/viral-launch/prompts/21_deliver.md:18`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/21_deliver.md#L18)
- "**Check for the linkedin-skills hook-formulas reference:**" [`skills/viral-launch/prompts/21_deliver.md:19`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/21_deliver.md#L19)
- "If missing, use \`generic-launch-narrative\` fallback (also documented in channel-specs.md)." [`skills/viral-launch/prompts/21_deliver.md:23`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/21_deliver.md#L23)
- "**Run the cross-channel consistency check** documented at the bottom of \`channel-specs.md\` before finalizing. If a check fails, fix and re-verify." [`skills/viral-launch/prompts/21_deliver.md:25`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/21_deliver.md#L25)
- "**No new claims.** Everything traces to stage_20 master document." [`skills/viral-launch/prompts/21_deliver.md:45`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/21_deliver.md#L45)
- "**No fabricated quotes / endorsements / numbers** that aren't in stage_20." [`skills/viral-launch/prompts/21_deliver.md:46`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/21_deliver.md#L46)
- "❌ Skipping the consistency check at the end — the cross-channel novelty angle MUST match" [`skills/viral-launch/prompts/21_deliver.md:67`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/prompts/21_deliver.md#L67)
- "Lowercase, alphanumerics + hyphens only, max 40 chars." [`skills/viral-launch/references/artifact-schema.md:7`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/artifact-schema.md#L7)
- "\`current_stage\` — the stage that is *about to* run, or *currently* running. On clean resume, this is where the orchestrator picks up." [`skills/viral-launch/references/artifact-schema.md:109`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/artifact-schema.md#L109)
- "\`iterations.NN_&lt;name>\` — how many times the worker for that stage has been dispatched (so we know the budget left)." [`skills/viral-launch/references/artifact-schema.md:111`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/artifact-schema.md#L111)
- "\`blockers\` — list of short strings describing what's preventing progress (e.g. \`"stage_19_mid_failed_drift"\`)" [`skills/viral-launch/references/artifact-schema.md:113`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/artifact-schema.md#L113)
- "\`current_stage\` ≥ max(\`completed_stages\`) — never advance back without explicit user decision" [`skills/viral-launch/references/artifact-schema.md:118`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/artifact-schema.md#L118)
- "On \`current_stage > 21\`, set \`status = "done"\`" [`skills/viral-launch/references/artifact-schema.md:120`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/artifact-schema.md#L120)
- "**Tweet 1 = HOOK**: ≤280 characters INCLUDING any link or media reference. No exceptions." [`skills/viral-launch/references/channel-specs.md:9`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/channel-specs.md#L9)
- "**One idea per tweet.** If a tweet has two ideas, split." [`skills/viral-launch/references/channel-specs.md:12`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/channel-specs.md#L12)
- "**Giveaway tweet sits at position N-1**, not N. Final tweet is always CTA + link." [`skills/viral-launch/references/channel-specs.md:14`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/channel-specs.md#L14)
- "**Same novelty angle in all three.** The hook claim from X tweet 1 should be detectable in LinkedIn post hook AND in ProductHunt tagline. Not identical wording — same claim." [`skills/viral-launch/references/channel-specs.md:158`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/channel-specs.md#L158)
- "**Same product name capitalization** everywhere." [`skills/viral-launch/references/channel-specs.md:159`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/channel-specs.md#L159)
- "**Same metric numbers** if any number from the brief shows up in 2+ channels, the digits must match." [`skills/viral-launch/references/channel-specs.md:160`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/channel-specs.md#L160)
- "**Why does it matter NOW?** — what changed, what timing makes this urgent, why should the reader care this minute" [`skills/viral-launch/references/hook-three-question-test.md:10`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/hook-three-question-test.md#L10)
- "**Why never existed?** Uses YOUR content (most AI tools generate from prompts, this orchestrates around assets)" [`skills/viral-launch/references/hook-three-question-test.md:21`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/hook-three-question-test.md#L21)
- "**Why never existed?** Nothing — "marketing workflows" is a dead phrase" [`skills/viral-launch/references/hook-three-question-test.md:41`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/hook-three-question-test.md#L41)
- "**Why never existed?** Nothing — "powerful", "seamless", "modern" are dead generic" [`skills/viral-launch/references/hook-three-question-test.md:55`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/hook-three-question-test.md#L55)
- ""First AI to write working code" — false, fail" [`skills/viral-launch/references/hook-three-question-test.md:72`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/hook-three-question-test.md#L72)
- ""First AI to write a working iOS app from a single prompt" — defensible if true, check brief" [`skills/viral-launch/references/hook-three-question-test.md:73`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/hook-three-question-test.md#L73)
- "The Hook Manager must trace every novelty claim back to either:" [`skills/viral-launch/references/hook-three-question-test.md:77`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/hook-three-question-test.md#L77)
- "01 brand_brief | (user-supplied facts only, written into \`input.md\` by main-Claude before dispatch)" [`skills/viral-launch/references/orchestrator-protocol.md:41`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/orchestrator-protocol.md#L41)
- "Manager: \`stage_NN_&lt;name>/critique_v{N}.json\` and on pass also writes the sibling worker's \`final.md\` (winning artifact only)" [`skills/viral-launch/references/orchestrator-protocol.md:68`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/orchestrator-protocol.md#L68)
- "Read current meta.json" [`skills/viral-launch/references/orchestrator-protocol.md:77`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/orchestrator-protocol.md#L77)
- "Write meta.json back" [`skills/viral-launch/references/orchestrator-protocol.md:79`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/orchestrator-protocol.md#L79)
- "No other stages parallelize." [`skills/viral-launch/references/orchestrator-protocol.md:87`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/orchestrator-protocol.md#L87)
- "All **manager** stages (9 hook_manager, 11 giveaway_manager, 17 body_manager) write exactly this JSON to \`critique_v{N}.json\`:" [`skills/viral-launch/references/rubric-format.md:3`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/rubric-format.md#L3)
- "\`voice\` — does it match the founder's voice from stage_01 brief?" [`skills/viral-launch/references/rubric-format.md:59`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/rubric-format.md#L59)
- "\`no_ai_slop\` — none of these phrases: "in today's fast-paced", "game-changer", "revolutionize", "leverage", "seamlessly", "robust", "powerful", "intelligent" (unless directly quoting)" [`skills/viral-launch/references/rubric-format.md:77`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/rubric-format.md#L77)
- "\`no_brief_contradictions\` — every fact in the body is traceable to stage_01 brief or earlier research" [`skills/viral-launch/references/rubric-format.md:78`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/rubric-format.md#L78)
- "**blocking** — pass is mathematically impossible while this exists. Examples: claim is factually false per brief; hook has no novelty axis at all; body contradicts stage_01." [`skills/viral-launch/references/rubric-format.md:82`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/rubric-format.md#L82)
- "Stages 3-6 (YouTube, X/Twitter, Reddit, Industry) use \`WebSearch\` and \`WebFetch\`." [`skills/viral-launch/references/search-query-templates.md:3`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/search-query-templates.md#L3)
- "**Required queries (run all four):**" [`skills/viral-launch/references/search-query-templates.md:9`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/search-query-templates.md#L9)
- "Channel name + subscriber tier (small=&lt;10k, mid=10k-500k, big=>500k)" [`skills/viral-launch/references/search-query-templates.md:19`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/search-query-templates.md#L19)
- "View count if visible (or "≥X" from typical channel range)" [`skills/viral-launch/references/search-query-templates.md:20`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/search-query-templates.md#L20)
- "Did they use a giveaway? what kind?" [`skills/viral-launch/references/search-query-templates.md:51`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/search-query-templates.md#L51)
- "**Subreddit-targeted (run 2-3 of these too, after eyeballing top subs from above):**" [`skills/viral-launch/references/search-query-templates.md:67`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/search-query-templates.md#L67)
- "**Verbatim pain quotes** (5-10 of them) — must be exact quote, ≤120 chars, with permalink" [`skills/viral-launch/references/search-query-templates.md:74`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/search-query-templates.md#L74)
- "**No fabrication.** If a search returns nothing, write \`No results.\` Don't invent fake quotes, view counts, or competitor data." [`skills/viral-launch/references/search-query-templates.md:102`](https://github.com/Koz-TV/viral-launch-pipeline/blob/475705f/skills/viral-launch/references/search-query-templates.md#L102)

</details>

No reader's rules were read: this report lists facts only and carries no verdict.
