#!/usr/bin/env python3
"""tools/test-parallel and tools/test-changed, the runner the herd's `meow herd test run` calls, and tests/map.

The line shapes meow reads are checked against the regexes in Cat Herder's lib/catherder_fleet/test_receipts.py
(MODULE_RESULT, UNIT_START and FINISHED at e150d426bb6f245df96dd7ac4bf4c5e405bbb5d6), copied here as fixed strings: a
change to the runner that stops a receipt reading it fails here first. Each case runs the real scripts in a throwaway
project, so the project under test is never this checkout."""
import os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULE_RESULT = re.compile(r"^\[\d+/\d+\] (\S+) (ok|FAIL under load|FAIL)(?: |$)")
UNIT_START = re.compile(r"^\[\d+/\d+\] (\S+) start(?: |$)")
FINISHED = re.compile(r"^\[\d+/(\d+)\] \S+ (ok|FAIL) ", re.M)
failures = []


def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        failures.append(name)


def project(modules, selfcheck=None, mapfile=None):
    """A throwaway git project holding this checkout's runner. `modules` maps a module name to its script's text."""
    d = Path(tempfile.mkdtemp(prefix="tp-"))
    (d / "tools").mkdir()
    for tool in ("test-parallel", "test-changed"):
        if (ROOT / "tools" / tool).exists():
            shutil.copy(ROOT / "tools" / tool, d / "tools" / tool)
            os.chmod(d / "tools" / tool, 0o755)
    for name, text in modules.items():
        (d / "tools" / f"{name}.py").write_text(text)
    if selfcheck is not None:
        (d / "skills" / "neckbeard").mkdir(parents=True)
        (d / "skills" / "neckbeard" / "selfcheck.py").write_text(selfcheck)
    if mapfile is not None:
        (d / "tests").mkdir()
        (d / "tests" / "map").write_text(mapfile)
    return d


def sh(args, cwd, env=None, **kw):
    e = dict(os.environ)
    e.update(env or {})
    return subprocess.run(args, cwd=cwd, env=e, capture_output=True, text=True, **kw)


def run(d, *args, env=None):
    return sh([sys.executable, str(d / "tools" / "test-parallel"), *args], d, env)


OK, BAD = "import sys\nsys.exit(0)\n", "import sys\nprint('boom')\nsys.exit(1)\n"

# ---------------------------------------------------------------- the line shapes
d = project({"test_a": OK, "test_b": BAD, "test_c": OK}, selfcheck=OK)
r = run(d, "-j", "2")
lines = r.stdout.splitlines()
starts = [UNIT_START.match(l).group(1) for l in lines if UNIT_START.match(l)]
results = {m.group(1): m.group(2) for l in lines if (m := MODULE_RESULT.match(l))}
check("a run starts every module, test_*.py plus selfcheck, one start line each", sorted(starts) == ["selfcheck", "test_a", "test_b", "test_c"], repr(starts))
check("a passing module ends '[i/N] <module> ok <seconds>s'", results.get("test_a") == "ok" and any(re.fullmatch(r"\[\d+/4\] test_a ok \d+\.\ds", l) for l in lines), repr(lines[:8]))
check("a failing module ends '[i/N] <module> FAIL <seconds>s' and the run exits 1", results.get("test_b") == "FAIL" and r.returncode == 1, f"{results} rc={r.returncode}")
check("FINISHED reads every ending line, with the module count as its first group", len(FINISHED.findall(r.stdout)) == 4 and FINISHED.findall(r.stdout)[0][0] == "4", repr(FINISHED.findall(r.stdout)))
check("a failed module's output is printed under '===== failure output: <module> ====='", "===== failure output: test_b =====" in r.stdout and "boom" in r.stdout)
check("the run closes with 'Slowest modules:'", "\nSlowest modules:" in r.stdout)
check("a run of passing modules exits 0", run(project({"test_a": OK}), "-j", "1").returncode == 0)

# ---------------------------------------------------------------- choosing modules
r = run(d, "test_a", "selfcheck")
check("named modules are the only ones run", sorted(UNIT_START.match(l).group(1) for l in r.stdout.splitlines() if UNIT_START.match(l)) == ["selfcheck", "test_a"], r.stdout[:200])
r = run(d, "test_nope")
check("an unknown module exits 2 and says 'no such test module'", r.returncode == 2 and "no such test module: test_nope" in r.stderr, f"rc={r.returncode} {r.stderr}")
shard_runs = [run(d, "--shard", f"{k}/3") for k in (1, 2, 3)]
parts = [sorted(UNIT_START.match(l).group(1) for l in s.stdout.splitlines() if UNIT_START.match(l)) for s in shard_runs]
check("--shard K/N: the shards together run every module once", sorted(sum(parts, [])) == ["selfcheck", "test_a", "test_b", "test_c"], repr(parts))
r = run(d, "--shard", "4/3")
check("--shard K/N: bad shard exits 2 and says so", r.returncode == 2 and "test-parallel:" in r.stderr and "shard" in r.stderr, r.stderr)
r = run(d, "--tier", "functional")
check("an option meow sends only to a project with tiers (--tier) is refused, exit 2", r.returncode == 2 and "test-parallel:" in r.stderr, r.stderr)

# ---------------------------------------------------------------- a failure under load is run again alone
flaky = ("import os, sys\nm = os.environ['MARK']\nif os.path.exists(m):\n    sys.exit(0)\nopen(m, 'w').close()\nsys.exit(1)\n")
d2 = project({"test_flaky": flaky})
r = run(d2, env={"MARK": str(d2 / "mark"), "TEST_PARALLEL_LOAD": "99"})
check("a module that fails under load and passes alone: 'FAIL under load', 'passed alone: a load flake', exit 0",
      "test_flaky FAIL under load" in r.stdout and "test_flaky passed alone: a load flake" in r.stdout and r.returncode == 0, r.stdout[-400:])
r = run(d, "test_b", env={"TEST_PARALLEL_LOAD": "99"})
check("a module that fails under load and fails alone: 'failed alone too: a real failure', exit 1",
      "test_b FAIL under load" in r.stdout and "test_b failed alone too: a real failure" in r.stdout and r.returncode == 1, r.stdout[-400:])
check("MODULE_RESULT reads the under-load line", any(MODULE_RESULT.match(l) and MODULE_RESULT.match(l).group(2) == "FAIL under load" for l in r.stdout.splitlines()))
r = run(d, "test_b")
check("a failure on a quiet machine is not run again", "test_b FAIL " in r.stdout and "alone" not in r.stdout, r.stdout[-300:])

# ---------------------------------------------------------------- test-changed
M = "src/a.py test_a\nsrc/b.py test_b\nlib/** test_a test_c\n"
d3 = project({"test_a": OK, "test_b": OK, "test_c": OK}, mapfile=M)
for p, text in (("src/a.py", "a\n"), ("src/b.py", "b\n"), ("lib/x/y.py", "y\n"), ("other.txt", "o\n")):
    (d3 / p).parent.mkdir(parents=True, exist_ok=True)
    (d3 / p).write_text(text)
sh(["git", "init", "-q", "-b", "main"], d3)
sh(["git", "add", "-A"], d3)
sh(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "base"], d3)
base = sh(["git", "rev-parse", "HEAD"], d3).stdout.strip()


def changed(path, text="changed\n"):
    (d3 / path).parent.mkdir(parents=True, exist_ok=True)
    (d3 / path).write_text(text)
    sh(["git", "add", "-A"], d3)
    sh(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", f"change {path}"], d3)
    r = sh([sys.executable, str(d3 / "tools" / "test-changed"), "--list", base], d3)
    sh(["git", "reset", "-q", "--hard", base], d3)
    return r


r = changed("src/a.py")
check("--changed: a path with a map line selects exactly its modules", "test-changed: test_a" in r.stdout.splitlines() and "test_b" not in r.stdout.split("test-changed: test_a")[-1], r.stdout)
r = changed("lib/x/y.py")
check("--changed: a ** glob crosses folders", "test-changed: test_a test_c" in r.stdout, r.stdout)
r = changed("other.txt")
check("--changed: a path with no map line selects the whole suite and says so",
      "other.txt has no tests/map entry" in r.stdout and "running the whole suite" in r.stdout, r.stdout)
r = sh([sys.executable, str(d3 / "tools" / "test-changed"), "--list", "no-such-commit"], d3)
check("--changed: a base that is not a commit exits 2 and says so", r.returncode == 2 and "test-changed:" in r.stderr, f"rc={r.returncode} {r.stderr}")
(d3 / "src" / "b.py").write_text("changed b\n")
sh(["git", "add", "-A"], d3)
sh(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "b"], d3)
r = sh([sys.executable, str(d3 / "tools" / "test-changed"), base], d3)
check("--changed without --list runs the selection through tools/test-parallel, only test_b",
      r.returncode == 0 and "test_b start" in r.stdout and "test_a start" not in r.stdout, r.stdout[-300:] + r.stderr[-200:])

# ---------------------------------------------------------------- this repo's tests/map
mp = ROOT / "tests" / "map"
rows = {}
if mp.exists():
    for line in mp.read_text().splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            glob, *mods = line.split()
            rows[glob] = mods
modules = {p.stem for p in (ROOT / "tools").glob("test_*.py")} | {"selfcheck"}
check("tests/map exists and has rows", bool(rows))
check("every module a map row names exists", bool(rows) and all(m in modules or m == "*" for ms in rows.values() for m in ms),
      repr(sorted({m for ms in rows.values() for m in ms} - modules - {"*"})))
check("every tools/test_X.py has its own row, tools/test_X.py -> test_X",
      all(rows.get(f"tools/{m}.py") and m in rows[f"tools/{m}.py"] for m in modules if m.startswith("test_")),
      repr([m for m in modules if m.startswith("test_") and m not in (rows.get(f"tools/{m}.py") or [])]))
check("tools/vet selects test_vet and test_vet_stability, and nothing else", sorted(rows.get("tools/vet", [])) == ["test_vet", "test_vet_stability"], repr(rows.get("tools/vet")))
check("skills/neckbeard/inventory.py selects selfcheck", "selfcheck" in rows.get("skills/neckbeard/inventory.py", []))
check("the runner's own files select its test", all("test_test_parallel" in rows.get(f"tools/{f}", []) for f in ("test-parallel", "test-changed")))
d4 = project({"test_vet": OK}, mapfile=mp.read_text() if mp.exists() else "")
(d4 / "tools" / "vet").write_text("#!/bin/sh\n")
(d4 / "README.md").write_text("r\n")
sh(["git", "init", "-q", "-b", "main"], d4)
sh(["git", "add", "-A"], d4)
sh(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "base"], d4)
b4 = sh(["git", "rev-parse", "HEAD"], d4).stdout.strip()
(d4 / "tools" / "vet").write_text("#!/bin/sh\necho changed\n")
sh(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-am", "vet"], d4)
r = sh([sys.executable, str(d4 / "tools" / "test-changed"), "--list", b4], d4)
sel = [l for l in r.stdout.splitlines() if l.startswith("test-changed: test_")]
check("this repo's map: a diff touching only tools/vet selects test_vet and test_vet_stability and nothing else",
      len(sel) == 1 and sorted(sel[0].split()[1:]) == ["test_vet", "test_vet_stability"], r.stdout + r.stderr)

print(f"test_test_parallel: {'all passed' if not failures else str(len(failures)) + ' failed'}")
sys.exit(1 if failures else 0)
