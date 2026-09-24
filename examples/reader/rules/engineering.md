# Engineering

1. **Reuse before writing.** Check the codebase, then the standard library, then
   an existing dependency, before adding code.
2. **Fix the cause, not the symptom.** Before changing a function, find every
   caller.
3. **A test is not done until it has been seen to fail.** Break the code it
   guards, watch it go red, restore it.
4. **The scope I asked for is the deliverable.** Do not narrow it quietly or
   widen it unasked; say what you would change and let me decide.
5. **Leave deliberate shortcuts marked:** `TODO(debt):` plus what breaks first
   and how to fix it.
6. **Subagents run on the model their definition pins.** Do not override it on
   the dispatch call.
7. **Commit messages:** imperative subject under 60 characters, then why.
