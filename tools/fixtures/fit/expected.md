> **🟨 COPY RULES, SKIP PLUGIN** · keep two rules and one skill as text  
> ⛔ **2** conflicts · 🔁 **1** covered · 🟩 **3** keep (2 rules, 1 skill) · 🗑️ **5** dropped  
> *against the sample reader (demo)*

<details><summary>📝 <b>Why this verdict</b> · keep two rules and one skill as text</summary>

It injects rules at every session start. Two short rules and one review skill are worth having, copied as text.

Verdict is relative to the sample reader.

Baseline: the sample reader · 4 rule files · 2347 bytes · sha256 b564c945bf65

Judge: the sample reader's config

<details><summary>Rule files</summary>

- `CLAUDE.md`
- `rules/safety.md`

</details>

**How its rules sorted**

| | verdict | count | |
|:--:|---|:--:|---|
| ⛔ | **conflicts** with a rule you run | **2** | 🟥🟥 |
| 🔁 | **already covered** | **1** | ⬜ |
| 🆕 | **new, standing rule** | **2** | 🟩🟩 |
| 🆕 | **new, on-demand skill** | **1** | 🟩 |
| 🗑️ | **dropped** (persona, extras, no value) | **5** | ⬛⬛⬛⬛⬛ |

</details>

<details><summary>⛔ <b>Conflicts</b> · 2 · A vague request gets the smallest; A deferred shortcut gets a comment</summary>

| # | it says | collides with | held in | |
|:--:|---|---|---|:--:|
| 1 | "A vague request gets the smallest version." | "If a request is ambiguous and the wrong reading is costly, ask." | rules/safety.md | 🟥 |
| 2 | "A deferred shortcut gets a comment shortcut:" | "Leave deliberate shortcuts marked: TODO(debt):" | rules/engineering.md | 🟧 |

</details>

<details><summary>🔁 <b>Already covered</b> · 1 · Reuse the codebase first.</summary>

| its rule | covered by | held in |
|---|---|---|
| Reuse the codebase first. | Rule 1, Reuse before writing | rules/engineering.md |

</details>

<details><summary>🟩 <b>Keep</b> · 2 rules + 1 skill · Never cut protection to make a; New non-trivial logic ships with one; Review a change by reading the</summary>

| # | rule or skill | kind | |
|:--:|---|:--:|:--:|
| 1 | Never cut protection to make a change smaller. (skills/a/SKILL.md) | rule | ⭐ |
| 2 | New non-trivial logic ships with one small test. (skills/a/SKILL.md) | rule | 🟩 |
| 3 | Review a change by reading the callers. (skills/b/SKILL.md) | skill | 🟩 |

</details>

<details><summary>🗑️ <b>Dropped</b> · 5 · skills/a/SKILL.md; commands/a.toml; commands/b.toml; skills/c/SKILL.md; skills/d/SKILL.md</summary>

`skills/a/SKILL.md > Levels` ⛔1 · `commands/a.toml` ⛔2 · `commands/b.toml` ⛔2 · `skills/c/SKILL.md > Help` · `skills/d/SKILL.md > Persona`

</details>

<details><summary>✅ <b>Do this</b> · 2 steps · Skip the plugin. Copy the two; If you install anyway, never use</summary>

- ⬜ 1. Skip the plugin. Copy the two rules from the Keep card.
- ⬜ 2. If you install anyway, never use the smallest-version reading for a vague request.

</details>

<details><summary>📋 <b>Proposed rules patch</b> · 2 rules + 1 skill · Never cut protection to make a; New non-trivial logic ships with one; Review a change by reading the</summary>

Add to rules/engineering.md:

```diff
+8. **Never cut protection to make a change smaller.**
```

</details>
