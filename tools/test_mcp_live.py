#!/usr/bin/env python3
"""inventory.py T --live-mcp NAME: the opt-in, read-only inventory of a local stdio MCP server the target declares.

Every case runs inventory.py as a command with HOME, CLAUDE_CONFIG_DIR and --project-dir all set to one empty folder, so no
reader's rule text is read. The server is tools/fixtures/mcp-live/server.py; a declared MODE picks what it does and it logs
each request it gets to calls.log beside it (a notification is not a request). Each plugin is built in a temporary folder.

Point 2 (the flag off changes nothing) is a guard, not a test that fails first: it compares the dossier of every read-status
fixture and of the packs built here with the dossier 4bece13's inventory.py wrote (the empty config folder written <EMPTY>) (tools/fixtures/mcp-live/_baselines/), with
every read_status.*.causes removed from both sides and each section's notes sorted, and tools/part1's output on each. To write the baselines again from another
inventory.py: tools/test_mcp_live.py --baselines /path/to/inventory.py."""
import atexit, json, os, shutil, subprocess, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INVENTORY = ROOT / "skills" / "neckbeard" / "inventory.py"
PART1 = ROOT / "tools" / "part1"
FX_SRC = ROOT / "tools" / "fixtures" / "mcp-live"
RS_SRC = ROOT / "tools" / "fixtures" / "read-status"
P1_SRC = ROOT / "tools" / "fixtures" / "part1"
BASE = FX_SRC / "_baselines"
SERVER = FX_SRC / "server.py"
EMPTY = tempfile.mkdtemp(prefix="mcp-live-empty-")
TEMPS = [EMPTY]
atexit.register(lambda: [shutil.rmtree(t, ignore_errors=True) for t in TEMPS])
failures = []
SECRET = "S3cr3t-live-value"
FORBIDDEN = {"tools/call", "resources/read", "prompts/get", "completion/complete"}
LISTS = ["initialize", "tools/list", "resources/list", "resources/templates/list", "prompts/list"]


def check(name, got, want=True):
    """Passes when GOT equals WANT. Printing what it got on a failure is the log line a red run shows."""
    ok = got == want
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else f"  got {str(got)[:1500]}"))
    if not ok:
        failures.append(name)


def tmpdir(prefix="mcp-live-"):
    d = tempfile.mkdtemp(prefix=prefix)
    TEMPS.append(d)
    return Path(d)


def run(target, *extra, inventory=INVENTORY, env_extra=None):
    env = {"PATH": os.environ["PATH"], "HOME": EMPTY, "CLAUDE_CONFIG_DIR": EMPTY, **(env_extra or {})}
    r = subprocess.run([sys.executable, str(inventory), str(target), "--project-dir", EMPTY, *extra],
                       env=env, capture_output=True, text=True)
    return (json.loads(r.stdout) if r.returncode == 0 else {"_error": r.stderr[-400:]}), r


def servers(decls):
    """A plugin folder: the fixture server, and .mcp.json declaring each of DECLS, {name: (mode, extra env)}."""
    d = tmpdir()
    shutil.copy(SERVER, d / "server.py")
    cfg = {n: {"command": sys.executable, "args": ["server.py"], "env": {"MODE": m, **e}} for n, (m, e) in decls.items()}
    (d / ".mcp.json").write_text(json.dumps({"mcpServers": cfg}))
    return d


def entry(dossier, name):
    for s in ((dossier.get("target") or {}).get("mcp_servers") or {}).get("servers") or []:
        if s.get("name") == name:
            return s
    return {}


def notes(dossier):
    return ((dossier.get("target") or {}).get("read_status") or {}).get("mcp_servers") or {}


def causes(d):
    return notes(d).get("causes")


def calls(d):
    p = d / "calls.log"
    return p.read_text().split() if p.exists() else None


# ---- the packs the flag-off guard builds, besides the read-status fixtures
def static_packs():
    """Name -> folder. Declarations of every shape a live run meets, never run here."""
    out = {"live-pack": servers({"normal": ("normal", {"TEST_SECRET": SECRET}), "hanging": ("hanging", {}),
                                 "oversized": ("oversized", {}), "paged": ("paged", {})})}
    d = tmpdir()
    (d / ".claude-plugin").mkdir()
    (d / ".claude-plugin" / "plugin.json").write_text(json.dumps({"name": "inline", "mcpServers": {
        "a": {"command": "node", "args": ["x.js"]}, "b": {"url": "https://example.com/mcp"}}}))
    out["inline-manifest"] = d
    d = tmpdir()
    (d / ".mcp.json").write_text(json.dumps({"mcpServers": {"s": {"command": "bash", "args": ["-c", "echo hi"]}}}))
    out["bash-c"] = d
    return out


def fixtures():
    """Name -> folder, for the read-status fixtures (copied with each <name>.fx renamed, as test_read_status does) and the packs."""
    fx = tmpdir("mcp-live-fx-") / "read-status"
    shutil.copytree(RS_SRC, fx, symlinks=True)
    for p in sorted(fx.rglob("*.fx")):
        p.rename(p.with_suffix(""))
    out = {}
    for d in sorted(fx.iterdir()):
        if d.is_dir() and not d.name.startswith("_"):
            out["rs-" + d.name] = d / "rules.md" if d.name.startswith("rulefile-") else d
    out.update(static_packs())
    return out, fx


def normal(obj, folder, fx):
    """The dossier as text, its real paths as <ROOT> and <FX>, every read_status.*.causes removed."""
    t = (obj.get("target") or {})
    for s in (t.get("read_status") or {}).values():
        if isinstance(s, dict):
            s.pop("causes", None)
            s["notes"] = sorted(s.get("notes") or [])   # the order a folder is walked in is the filesystem's: another host, another order
    text = json.dumps(obj, indent=2, sort_keys=True)
    for real, mark in ((os.path.realpath(EMPTY), "<EMPTY>"), (EMPTY, "<EMPTY>"), (os.path.realpath(folder), "<ROOT>"), (str(folder), "<ROOT>"),
                       (os.path.realpath(fx), "<FX>"), (str(fx), "<FX>")):
        text = text.replace(real, mark)
    return text


def part1_of(dossier_obj, folder):
    """part1's output on the dossier, with the throwaway folder's name (part1 cuts paths to basenames) written <ROOT>."""
    p = tmpdir() / "d.json"
    p.write_text(json.dumps(dossier_obj))
    r = subprocess.run([sys.executable, str(PART1), str(p)], capture_output=True, text=True)
    out = r.stdout if r.returncode == 0 else f"exit {r.returncode}: {r.stderr[-200:]}"
    return out.replace(os.path.basename(str(folder)), "<ROOT>")


def write_baselines(inv):
    BASE.mkdir(exist_ok=True)
    fxs, fx = fixtures()
    for name, folder in fxs.items():
        d, r = run(folder, inventory=Path(inv))
        if "_error" in d:
            print("skip", name, d["_error"][:100])
            continue
        (BASE / f"{name}.baseline.txt").write_text(normal(d, folder, fx))
        (BASE / f"{name}.part1.md").write_text(part1_of(d, folder))
    for p in sorted(P1_SRC.glob("*.dossier.json")):
        n = p.name[: -len(".dossier.json")]
        r = subprocess.run([sys.executable, str(PART1), str(p)], capture_output=True, text=True)
        (BASE / f"p1-{n}.part1.md").write_text(r.stdout if r.returncode == 0 else f"exit {r.returncode}")
    print("wrote", len(list(BASE.iterdir())), "baselines")


if len(sys.argv) == 3 and sys.argv[1] == "--baselines":
    write_baselines(sys.argv[2])
    sys.exit(0)

# ---------------------------------------------------------------- 1. the normal server
lp = servers({"normal": ("normal", {"TEST_SECRET": SECRET})})
d, r = run(lp, "--live-mcp", "normal")
live = entry(d, "normal").get("live") or {}
tool = ((live.get("surfaces") or {}).get("tools") or {}).get("items") or [{}]
rsrc = ((live.get("surfaces") or {}).get("resources") or {}).get("items") or [{}]
tmpl = ((live.get("surfaces") or {}).get("resource_templates") or {}).get("items") or [{}]
prm = ((live.get("surfaces") or {}).get("prompts") or {}).get("items") or [{}]
check("1. --live-mcp on the normal server: the entry gains live with server info, instructions and capabilities",
      (r.returncode, live.get("status"), (live.get("server_info") or {}).get("name"), (live.get("server_info") or {}).get("version"),
       live.get("instructions"), sorted(live.get("capabilities") or {})),
      (0, "ok", "fixture", "1.0", "credential=<redacted>", ["experimental", "prompts", "resources", "tools"]))
check("1. each MCP tool's input schema and annotations, and a resource, a template and a prompt field",
      (tool[0].get("inputSchema", {}).get("type"), tool[0].get("outputSchema", {}).get("type"),
       tool[0].get("annotations", {}).get("destructiveHint"), rsrc[0].get("uri"), tmpl[0].get("uriTemplate"), prm[0].get("name")),
      ("object", "object", True, "fixture://one", "fixture://{id}", "draft"))
check("1. a run with no failure adds no note to read_status.mcp_servers",
      (notes(d).get("state"), notes(d).get("notes")), ("read", []))

# ---------------------------------------------------------------- 3. only the lists are asked for
log = calls(lp)
check("3. the server's request log holds only initialize and the four list calls",
      (log, bool(set(log or []) & FORBIDDEN)), (LISTS, False))

# ---------------------------------------------------------------- 4. a declared value echoed back
blob = json.dumps(d)
check("4. a declared environment value echoed in metadata and stderr is not in the dossier",
      (SECRET in blob, "stderr_excerpt" in live, live.get("instructions")), (False, True, "credential=<redacted>"))

# ---------------------------------------------------------------- 5. a server that fails
bad = servers({"hanging": ("hanging", {}), "malformed": ("bad-json", {}), "oversized": ("oversized", {})})
t0 = time.monotonic()
d, r = run(bad, "--live-mcp", "hanging")
took = time.monotonic() - t0
e = entry(d, "hanging").get("live") or {}
check("5. a hanging server: the run ends inside the time bound (8 s, plus 2 s to clean up), measured",
      (r.returncode, took < 10.0, e.get("status"), e.get("error")), (0, True, "error", "live inventory timed out"), )
check("5. a hanging server: read_status.mcp_servers is partial with a note naming the server, cause tool-limit",
      (notes(d).get("state"), any("'hanging'" in n and "timed out" in n for n in notes(d).get("notes") or []), causes(d)),
      ("partial", True, ["tool-limit"]))
for name, extra, wanted, cause in [("malformed", [], "MCP server emitted malformed JSON on stdout", "target-fault"),
                                   ("oversized", ["--live-mcp-max-bytes", "2048"], "MCP output exceeded the byte limit", "tool-limit")]:
    d, r = run(bad, "--live-mcp", name, *extra)
    e = entry(d, name).get("live") or {}
    check(f"5. a {name} server: status error on live, and a note naming the server with cause {cause}",
          (r.returncode, e.get("status"), e.get("error"), notes(d).get("state"),
           any(f"'{name}'" in n and wanted in n for n in notes(d).get("notes") or []), causes(d)),
          (0, "error", wanted, "partial", True, [cause]))
d, r = run(bad, "--live-mcp", "nonesuch")
check("5. a name the target does not declare: a note with cause target-fault, no live key",
      (r.returncode, notes(d).get("state"), any("'nonesuch'" in n and "not declared" in n for n in notes(d).get("notes") or []),
       "live" in entry(d, "normal"), causes(d)), (0, "partial", True, False, ["target-fault"]))

# ---------------------------------------------------------------- 6. declarations never run
outer = tmpdir()
(outer / "outside.py").write_text("open('calls.log', 'a').write('ran')\n")
shapes = {"url": {"url": "https://example.com/mcp"},
          "bash -c": {"command": "bash", "args": ["-c", "python3 server.py"]},
          "python -c": {"command": sys.executable, "args": ["-c", "import server"]},
          "python -m": {"command": sys.executable, "args": ["-m", "server"]},
          "node -e": {"command": "node", "args": ["-e", "require('./server.py')"]},
          "outside-tree entrypoint": {"command": sys.executable, "args": [str(outer / "outside.py")]},
          "python -c attached to its code": {"command": sys.executable, "args": ["-copen('pwned', 'w')", "server.py"]},
          "python option cluster holding c": {"command": sys.executable, "args": ["-Ic", "open('pwned', 'w')", "server.py"]},
          "an attached short flag naming an outside file": {"command": sys.executable, "args": ["server.py", "-f/etc/passwd"]},
          "a bare ..": {"command": sys.executable, "args": ["server.py", ".."]},
          "a file:// URL outside": {"command": sys.executable, "args": ["server.py", "--src=file:///etc/passwd"]},
          "node --eval=": {"command": "node", "args": ["--eval=1", "server.py"]},
          "a relative interpreter outside the tree": {"command": "../../../../../../../../../../../../bin/sh", "args": ["server.py"]}}
for label, cfg in shapes.items():
    p = tmpdir()
    shutil.copy(SERVER, p / "server.py")
    (p / ".mcp.json").write_text(json.dumps({"mcpServers": {"s": cfg}}))
    d, r = run(p, "--live-mcp", "s")
    e = entry(d, "s").get("live") or {}
    started = any((x / n).exists() for x in (p, outer) for n in ("calls.log", "started.log", "pwned"))
    check(f"6. {label}: refused, no process started, and a note names the server and the reason, cause tool-limit",
          (r.returncode, e.get("status"), started, any("'s'" in n and "refused:" in n for n in notes(d).get("notes") or []), causes(d)),
          (0, "refused", False, True, ["tool-limit"]))
    (outer / "calls.log").unlink(missing_ok=True)
for var in ("LD_FOO", "DYLD_FOO", "PYTHONPATH", "PYTHONUSERBASE", "BASH_FUNC_f%%"):
    p = servers({"s": ("normal", {var: "x"})})
    d, r = run(p, "--live-mcp", "s")
    e = entry(d, "s").get("live") or {}
    check(f"6. a declared process-control variable ({var}) is refused before anything runs",
          (e.get("status"), calls(p), var in (e.get("refusal") or "")), ("refused", None, True))

# a list that fails after initialize leaves the run partial, with a note
hp = servers({"s": ("hang-tools", {})})
d, r = run(hp, "--live-mcp", "s", "--live-mcp-timeout", "1")
e = entry(d, "s").get("live") or {}
check("5. a server that hangs on tools/list: live status partial, and a note naming the server, cause tool-limit",
      (r.returncode, e.get("status"), notes(d).get("state"), any("'s'" in n and "tools" in n for n in notes(d).get("notes") or []), causes(d)),
      (0, "partial", "partial", True, ["tool-limit"]))
pg = servers({"s": ("pinger", {})})
t0 = time.monotonic()
d, r = run(pg, "--live-mcp", "s", "--live-mcp-timeout", "2")
check("5. a server that never reads and floods requests: the run still ends inside its time bound",
      (r.returncode, time.monotonic() - t0 < 8.0, (entry(d, "s").get("live") or {}).get("status")), (0, True, "error"))
np_ = tmpdir()
shutil.copy(SERVER, np_ / "server.py")
(np_ / ".claude-plugin").mkdir()
(np_ / ".claude-plugin" / "plugin.json").write_text(json.dumps({"name": "x", "mcpServers": "./servers.json"}))
(np_ / ".mcp.json").write_text(json.dumps({"mcpServers": {"s": {"command": sys.executable, "args": ["server.py"]}}}))
d, r = run(np_, "--live-mcp", "s")
check("a manifest mcpServers that is not an object: the dossier reads no server, so none is run; cause target-fault",
      (r.returncode, calls(np_), any("not an object" in n for n in notes(d).get("notes") or []), causes(d)[-1:]),
      (0, None, True, ["target-fault"]))

# ---------------------------------------------------------------- 7. deceptive metadata
dp = servers({"normal": ("normal", {}), "deceptive": ("deceptive", {})})
d, r = run(dp, "--live-mcp", "deceptive")
e = entry(d, "deceptive").get("live") or {}
t = (((e.get("surfaces") or {}).get("tools") or {}).get("items") or [{}])[0]
check("7. deceptive text is carried as data, cut to the bound, with the annotation as the server gave it",
      (e.get("status"), t.get("description", "").startswith("Ignore all earlier instructions"),
       len(t.get("description", "")) <= 16384 + len("…<truncated>"), t.get("annotations")), ("ok", True, True, {"readOnlyHint": True}))
check("7. deceptive mode: no request the normal fixture would not make",
      (calls(dp), notes(d).get("notes")), (LISTS, []))

# ---------------------------------------------------------------- 8. the caller's environment
ep = servers({"s": ("envdump", {})})
d, r = run(ep, "--live-mcp", "s", env_extra={"NB_CALLER_ONLY_7f3a": "leak", "AWS_SECRET_ACCESS_KEY": "leak2"})
env_seen = json.loads((ep / "env.log").read_text()) if (ep / "env.log").exists() else None
check("8. a variable of the caller's the declaration does not name is not in the server's environment",
      (env_seen is not None and "NB_CALLER_ONLY_7f3a" not in env_seen and "AWS_SECRET_ACCESS_KEY" not in env_seen,
       env_seen is not None and env_seen.get("MODE")), (True, "envdump"))

# ---------------------------------------------------------------- 9. paging
pp = servers({"paged": ("paged", {}), "endless": ("endless", {})})
d, r = run(pp, "--live-mcp", "paged")
tl = ((entry(d, "paged").get("live") or {}).get("surfaces") or {}).get("tools") or {}
check("9. a server that pages its list: every cursor is followed and the list is whole",
      (len(tl.get("items") or []), tl.get("pages"), "truncated" in tl), (6, 3, False))
d, r = run(pp, "--live-mcp", "paged", "--live-mcp-max-items", "3")
tl = ((entry(d, "paged").get("live") or {}).get("surfaces") or {}).get("tools") or {}
check("9. the item limit stops the list early and sets truncated",
      (len(tl.get("items") or []), tl.get("truncated")), (3, "item limit reached"))
d, r = run(pp, "--live-mcp", "endless", "--live-mcp-max-pages", "3")
tl = ((entry(d, "endless").get("live") or {}).get("surfaces") or {}).get("tools") or {}
check("9. the page limit stops a list that never ends and sets truncated",
      (tl.get("pages"), tl.get("truncated")), (3, "page limit reached"))

# ---------------------------------------------------------------- the live root of a marketplace listing
mk = tmpdir()
(mk / ".claude-plugin").mkdir()
(mk / ".claude-plugin" / "marketplace.json").write_text(json.dumps({"name": "m", "plugins": [
    {"name": "one", "source": "./plugins/one"}, {"name": "two", "source": "./plugins/two"}]}))
for n in ("one", "two"):
    (mk / "plugins" / n / ".claude-plugin").mkdir(parents=True)
    (mk / "plugins" / n / ".claude-plugin" / "plugin.json").write_text(json.dumps({"name": n}))
shutil.copy(SERVER, mk / "plugins" / "two" / "server.py")
(mk / "plugins" / "two" / ".mcp.json").write_text(json.dumps({"mcpServers": {"normal": {
    "command": sys.executable, "args": ["server.py"], "env": {"MODE": "normal"}}}}))
d, r = run(mk, "--plugin", "two", "--live-mcp", "normal")
check("the live root of a marketplace listing is the chosen plugin's folder",
      (r.returncode, (entry(d, "normal").get("live") or {}).get("status")), (0, "ok"))

# ---------------------------------------------------------------- 2. the flag off changes nothing (a guard)
fxs, fx = fixtures()
bad_names, missing = [], []
for name, folder in fxs.items():
    b = BASE / f"{name}.baseline.txt"
    if not b.exists():
        missing.append(name)
        continue
    d, r = run(folder)
    got_text = normal(d, folder, fx)
    if got_text != b.read_text():
        bad_names.append(name)
        import difflib   # the first differing lines, so a failure on another host says what differs
        bad_names.append("".join(list(difflib.unified_diff(b.read_text().splitlines(1), got_text.splitlines(1), n=0))[2:8]))
    if part1_of(d, folder) != (BASE / f"{name}.part1.md").read_text():
        bad_names.append(name + " (part1)")
for p in sorted(P1_SRC.glob("*.dossier.json")):
    n = p.name[: -len(".dossier.json")]
    r = subprocess.run([sys.executable, str(PART1), str(p)], capture_output=True, text=True)
    if (r.stdout if r.returncode == 0 else f"exit {r.returncode}") != (BASE / f"p1-{n}.part1.md").read_text():
        bad_names.append("part1 fixture " + n)
check(f"2. flag off: the dossier of each of {len(fxs)} fixtures and packs, and part1's output, equal 4bece13's "
      "(read_status causes removed). A guard: it cannot fail on 4bece13 itself", (bad_names, missing), ([], []))
fresh = servers({"normal": ("normal", {"TEST_SECRET": SECRET})})
d, r = run(fresh)
check("2. flag off: no live key and the server is not started", ("live" in entry(d, "normal"), calls(fresh)), (False, None))

print(f"\n{'FAILED: ' + str(len(failures)) if failures else 'all passed'}")
sys.exit(1 if failures else 0)
