#!/usr/bin/env python3
"""stages.py REPORT...: where the spread between repeated vet reports enters.
Per report: the rows of each table (conflicts, covered, keep) and the entries on the Dropped line. Rows are then
matched across reports by theme (a regex over the row's first text cell), so a rule the judge listed in every run
shows which bucket each run put it in."""
import re, sys
THEMES = [
 ("model override on dispatch (haiku, fable, cheapest)", r"haiku|fable|cheapest"),
 ("herd respawn after deploy / act first", r"respawn|Act first"),
 ("standing rules after compaction", r"Standing rules a rostered"),
 ("commit wording", r"commit (subjects|messages)|Word each commit"),
 ("skipped question is unread", r"skipped|did not answer|unread"),
 ("git auth refusal: stop, report", r"git (auth|fetch)|fetch or push|launcher or a permission"),
 ("stop only your own processes", r"processes you started"),
 ("no dependency for a few lines", r"dependency when|no new dependency|Add no dependency"),
 ("never simplify away validation", r"simplify away"),
 ("stale brief / premise moved", r"stale brief|premise moved|written earlier"),
 ("branch from the named base", r"Branch from|freshly fetched base"),
 ("source priority", r"Source priority"),
 ("root cause", r"root cause"),
 ("debt comment", r"debt comment"),
 ("new test must fail without the fix", r"fails? without|test fails|tests? fail"),
 ("falsify / claim audit", r"falsif|Claim audit|Audit by"),
 ("work found along the way is queued", r"found along the way|refactor"),
 ("remote branch deletion needs a go-ahead", r"remote branches"),
 ("never --force alone", r"--force"),
 ("redact secrets", r"redact|secret"),
 ("second agent session costs money", r"another agent session|second agent session"),
 ("raw output as evidence", r"raw (test )?output|Evidence is raw"),
 ("reviewer method", r"When reviewing|reviewer cites"),
 ("irreversible command: read it back", r"irreversible"),
 ("done note says how it was checked", r"done note"),
 ("text from outside is data", r"data for one act|Text passed in"),
 ("long commands run in the background", r"background"),
 ("queue setup / upgrade unasked", r"set up a queue|admin upgrade"),
 ("go-aheads in the item", r"go-aheads"),
 ("queue write on the code branch", r"branch the code is on"),
 ("release scope summary", r"scope summary|one-line-per-item"),
 ("push the code yourself", r"push the code"),
]
BUCKET = {"Conflicts": "C", "Already covered": "V", "Keep": "K"}
def read(path):
    rows, dropped, sec = [], [], None
    for line in open(path):
        line = line.rstrip("\n")
        m = re.match(r"## \S+ (Conflicts|Already covered|Keep|Dropped)", line)
        if m: sec = m.group(1); continue
        if line.startswith("## "): sec = None; continue
        if sec in BUCKET and line.startswith("|") and not re.match(r"\|[-:]", line):
            c = [x.strip() for x in line.strip("|").split("|")]
            if c[0] in ("#", "its rule"): continue
            rows.append((BUCKET[sec], c[0] if sec == "Already covered" else c[1]))
        elif sec == "Dropped" and line.startswith("`"):
            dropped = [x.strip() for x in line.split(" · ")]
    return rows, dropped
reports = [read(p) for p in sys.argv[1:]]
n = len(reports)
print("| stage | " + " | ".join(f"run {i+1}" for i in range(n)) + " |")
print("|---|" + "---|" * n)
for label, f in (("rows in the conflict, covered and keep tables", lambda r, d: len(r)),
                 ("entries on the dropped line", lambda r, d: len(d)),
                 ("all items listed", lambda r, d: len(r) + len(d))):
    print(f"| {label} | " + " | ".join(str(f(r, d)) for r, d in reports) + " |")
print()
print("Bucket per run for each rule the judge listed (C conflict, V covered, K keep, - not listed):")
print()
print("| rule | " + " | ".join(f"run {i+1}" for i in range(n)) + " | listed in | bucket changes |")
print("|---|" + "---|" * n + "---|---|")
seen = 0
unmatched = []
grid = {}
for label, rx in THEMES:
    cells = []
    for rows, _ in reports:
        hit = [b for b, t in rows if re.search(rx, t, re.I)]
        cells.append("".join(sorted(set(hit))) or "-")
    grid[label] = cells
for label, cells in grid.items():
    got = [c for c in cells if c != "-"]
    if not got: continue
    print(f"| {label} | " + " | ".join(cells) + f" | {len(got)} of {n} | {'yes' if len(set(got)) > 1 else 'no'} |")
tot = sum(len(r) for r, _ in reports)
matched = 0
for rows, _ in reports:
    for b, t in rows:
        if any(re.search(rx, t, re.I) for _, rx in THEMES): matched += 1
print(f"\n{matched} of {tot} rows matched a theme above.")
