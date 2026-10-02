# Tomas Vykruta's `AGENTS.md` rules

Source: [Tomas Vykruta (@tvykruta), X thread, September 30, 2026](https://x.com/tvykruta/status/2105302045573959697).
Transcribed from the screenshots Tomas published in that thread. The rules and
application steps below are his; numbering outside invariants 10–12 was added so
the transcription can be referenced unambiguously.

Tomas reported that one feature took five days, 49 PRs and about $640 in tokens
before these rules; afterward, he reported roughly 7× lower cost per PR, 9×
fewer tokens and first-try merges. Those are the author's measurements, not
Neckbeard's.

## The rules

Constraints, not a checklist; when two conflict, pick the lowest future cost
for this repo and say so in the commit. `AGENTS.md` invariants 10–12 are the hard
form of these.

### The design principles (every file)

1. **Separation of concerns:** domain (`services/<domain>/`) · persistence
   (`models.py`, `alembic/`) · presentation (templates, `static/`) · routing
   (`pocket/`, `app.py`). Name the one concern of the file you edit.
2. **Encapsulation:** public contracts only; read another module's tables and
   caches through its functions.
3. **Cohesion / coupling:** one rule change touches one module.
4. **DRY:** grep before writing logic; one home per rule, threshold, format or
   schema fact. Do not abstract coincidental similarity.
5. **KISS / YAGNI:** simplest working shape; function over class; no speculative
   hooks, flags or frameworks.
6. **Single responsibility:** if you describe it with "and", split it. Names say
   intent; comments say why.
7. **Depend on contracts:** domain code takes and returns plain values; never
   imports Flask, request or templates.
8. **Composition over inheritance** · open/closed only where change has happened
   twice · Demeter (no `a.b.c.d`) · fail fast (validate at edges, never swallow
   errors) · optimize for deletion · boring tech.

### The hard invariants (never violate)

10. **One owning module per domain** — each business domain's logic (pricing,
    valuation, pedigree reading, sharing, imports, analytics...) lives in one
    module with its rules doc; everyone else calls it. Pricing:
    `services/pricing/` + `docs/PRICING_RULES.md`. Consolidate a scattered domain
    before adding to it. Extend the domain's existing module; create a new one
    only when you can say why the old one cannot own it. A new rule goes in its
    domain's owner, not in the first feature that needs it; a function-level
    import to dodge a cycle means the logic is in the wrong module.
11. **Never duplicate logic** — second use of existing logic: (1) move it to a
    shared module, (2) switch the original caller, tests green, no behaviour
    change, (3) then build the new use. First grep for the expression (the
    arithmetic, the format string, the threshold) and list every copy; the move
    switches them all or the commit names each one left and why. A new helper
    beside old copies is one more duplicate. The move keeps each caller's exact
    results (guards, rounding, clamps); any behaviour change is its own commit.
    Same for schemas (one fact, one column) and UX (one partial per repeated
    piece).
12. **No business logic in rendering** — templates, JS, routes and view builders
    only display values; they never compute prices, rules or classifications.
    Arithmetic or rules on business data there is a bug; move it to the owning
    module. Who sees a value is decided in Python, not by a template if.

### How to work

13. **Refactor first, then change:** a behaviour-preserving refactor with tests
    green (plus an output dump for pricing-sized domains), then the change.
    Never both in one unverifiable diff.
14. **Gates, not promises.** A prompted "never" alone does not protect the SoT;
    a rule that matters is enforced by CI or a hook.

The original thread numbers only invariants 10–12. The other numbers were added
for reference; there is no rule 9 in the post.

## How to apply it

1. Put the rules in your `AGENTS.md` (or `CLAUDE.md`).
2. Pick the system that hurts most. Ask Claude for a staff-engineer architecture
   review of just that system against the rules. Use numbers, not opinions:
   every file holding its logic, every copy of every formula and every place
   the copies disagree.
3. Ask for a refactor plan: small behavior-preserving steps, one PR each, with
   no new features in the plan.
4. Run the plan step by step. Tests stay green after every step. If a step
   changes behavior, it is a bug in the refactor.
5. Add a check that fails if the mess returns: a copy, math in a template or
   logic outside the owner.
6. Ask for a second staff-level architecture review of the same system. Compare
   it with the first, pattern by pattern and with the same numbers. Anything not
   fully compliant returns to step 3.
7. Only then build the feature you originally wanted.
8. Then pick the next system.
