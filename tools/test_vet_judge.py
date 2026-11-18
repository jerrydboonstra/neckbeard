#!/usr/bin/env python3
"""tools/vet's judge and login checks, run end to end against a fake `claude`: the web session and Mac cases, a judge that
writes no report or a bad one, a login copied on Linux (and what must never reach the report or the output), and an
explicit --judge reader. Split from tools/test_vet.py to keep each file under neckbeard's read cap; the fake `claude` and
the helpers both share are in tools/vet_harness.py.

    python3 tools/test_vet_judge.py
"""
import json, os, re, shutil, subprocess, sys, tempfile

import vet_harness
from vet_harness import *

# 11. vet-reader-login: on Linux the default reader gets a copy of the caller's login, so reader mode can log in
import time
ACCESS, REFRESH = "MARKERACCESS-zz11-aaaa", "MARKERREFRESH-zz22-bbbb"
def login_file(hours=24):
    return json.dumps({"claudeAiOauth": {"accessToken": ACCESS, "refreshToken": REFRESH, "expiresAt": int((time.time() + hours * 3600) * 1000)}})
LOGIN = {".credentials.json": login_file()}
SECRET = dict(FAKE_SECRET=ACCESS)
r = run("login-copy", login="file", uname="Linux", caller=LOGIN, fake_env=SECRET)
j = judges(r)[0] if judges(r) else {}
chk("login-copy: the default judge on Linux with a login file runs as the reader", (r["rc"], "judge: reader" in r["out"], "can't log in" in r["out"]), (0, True, False))
chk("login-copy: the judge saw the login file, mode 600", (j.get("cred_seen"), j.get("cred_mode")), (True, "0o600"))
chk("login-copy: the folder the judge ran in is gone once vet exits", (bool(r["cfg_left"]), any(r["cfg_left"])), (True, False))
chk("login-copy: no secret and no file name in the report, the dossier or vet's output", (ACCESS in r["text"] or REFRESH in r["text"], any(c["dossier_has_secret"] for c in r["calls"]), ACCESS in r["out"] or REFRESH in r["out"], ".credentials.json" in r["out"]), (False, False, False, False))
chk("login-copy: nothing is left in vet's temp folder", r["temp_left"], [])
chk("login-copy: the caller's own login file is left as it was, byte for byte", r["caller_after"].get(".credentials.json"), LOGIN[".credentials.json"])
r = run("login-leak", login="file", uname="Linux", caller=LOGIN, fake_env=dict(SECRET, FAKE_PROSE="secret"))
chk("login-leak: a prose text that holds the login's token is not written into a report, and vet fails without printing it", (r["rc"] != 0, r["report"], ACCESS in r["out"]), (True, False, False))
def token_in_skill(target):   # a skill name that part 1 prints, so only the scan of the finished report can see the token
    open(os.path.join(target, "skills", "demo", "SKILL.md"), "w").write("---\nname: " + ACCESS + "\ndescription: A demo skill.\n---\n\nAlways run the tests before you commit.\n")
r = run("login-report-part1", login="file", uname="Linux", caller=LOGIN, fake_env=SECRET, setup=token_in_skill)
chk("login-report: a token that reaches the finished report through part 1 (read from the dossier, never from a judge file) leaves no report and no side file, exit non-zero, no value printed", (r["rc"] != 0, r["report"], ACCESS in r["out"], r["side_left"]), (True, False, False, []))
r = run("login-say-clean", login="file", uname="Linux", caller=LOGIN, fake_env=dict(FAKE_SAY=" judge-said-this"))
chk("login-say: a clean judge reply leaves the run passing", r["rc"], 0)
r = run("login-leak-refresh", login="file", uname="Linux", caller=LOGIN, fake_env=dict(FAKE_SECRET=REFRESH, FAKE_PROSE="secret"))
chk("login-leak: a report holding only the refresh token is refused too", (r["rc"] != 0, r["report"], REFRESH in r["out"]), (True, False, False))
for tok, name in ((ACCESS, "access"), (REFRESH, "refresh")):
    r = run("login-say-" + name, login="file", uname="Linux", caller=LOGIN, fake_env=dict(FAKE_SAY=" " + tok))
    chk("login-say: a judge reply that holds the %s token is refused, with one line and no value" % name, (r["rc"] != 0, tok in r["out"], "held your login's secrets" in r["out"]), (True, False, True))
r = run("login-side", login="file", uname="Linux", caller=LOGIN, extra=("--units",), units="units-install", fake_env=dict(FAKE_SIDE=ACCESS))
chk("login-side: a token in a --units side file leaves no report and no side file, exit non-zero, no value printed", (r["rc"] != 0, r["report"], ACCESS in r["out"], r["side_left"]), (True, False, False, []))
r = run("login-find-die", login="file", uname="Linux", caller=LOGIN, extra=("--units",), units="units-install", finds="tokenanswer", fake_env=SECRET)
chk("login-find: a find pass that answers with the token and writes no candidates: non-zero, no value in vet's output, no side file left", (r["rc"] != 0, ACCESS in r["out"], r["side_left"]), (True, False, []))
r = run("login-find-space", login="file", uname="Linux", caller=LOGIN, extra=("--units",), units="units-install", finds="tokenanswer", fake_env=SECRET, outname="my report.md")
chk("login-find: an OUT path with a space is scanned and cleaned whole", (r["rc"] != 0, ACCESS in r["out"], r["side_left"]), (True, False, []))
r = run("login-refresh", login="file", uname="Linux", caller=LOGIN, fake_env=dict(FAKE_REFRESH="1"))
chk("login-refresh: a judge that rewrote its login file gets one line saying so", (r["rc"], "log in again" in r["out"], ACCESS in r["out"]), (0, True, False))
chk("login-refresh: the caller's own login file is untouched by it", r["caller_after"].get(".credentials.json"), LOGIN[".credentials.json"])
# no copy, and the fallback line says why
with_reader = tempfile.mkdtemp()
try:
    mine = reader_copy(with_reader)
    cases = [("never gets your login", dict(caller=LOGIN, uname="Linux", extra=("--reader", mine))),
             ("logs in only on Linux", dict(caller=LOGIN, uname="Darwin")),
             ("no login file in your config folder", dict(caller={}, uname="Linux")),
             ("due to refresh within the hour", dict(caller={".credentials.json": login_file(hours=1 / 6)}, uname="Linux")),
             ("login file couldn't be read", dict(caller={".credentials.json": "not json"}, uname="Linux")),
             ("login file couldn't be read", dict(caller={".credentials.json": '{"claudeAiOauth": {"accessToken": "x"}}'}, uname="Linux")),
             ("login didn't work as the reader", dict(caller=LOGIN, uname="Linux", login="never"))]
    for why, kw in cases:
        r = run("no-copy " + why, **{"login": "file", **kw})
        if "didn't work" in why:
            chk("no-copy: the copy is removed once the probe fails, before the own judge runs", any(c["reader_cred_left"] for c in r["calls"] if "single word ok" not in c["prompt"]), False)
        chk("no-copy: " + why, ("judge: own" in r["out"], "can't log in" in r["out"], why in r["out"], any(c["cred_seen"] and "single word ok" in c["prompt"] for c in r["calls"]) and "didn't work" not in why, ACCESS in r["out"]), (True, True, True, False, False))
finally:
    shutil.rmtree(with_reader)
r = run("login-facts", extra=("--facts",), uname="Linux", caller=LOGIN, fake_body=NO_CLAUDE)
chk("facts: no login is copied, no model is called", (r["rc"], r["calls"]), (0, []))
r = run("login-own", login="file", uname="Linux", caller=LOGIN, extra=("--judge", "own"), fake_env=SECRET)
chk("own: an explicit --judge own copies nothing", (r["rc"], any(c["reader_cred_left"] for c in r["calls"])), (0, False))

# 12. vet-forced-reader-no-fallback: an explicit --judge reader copies the login like auto, and never falls back to own
FORCED = ("--judge", "reader")
if True:   # uname is faked, so these run on any host
    r = run("forced-copy", login="file", uname="Linux", caller=LOGIN, extra=FORCED, fake_env=SECRET)
    j = judges(r)[0] if judges(r) else {}
    chk("forced-copy: --judge reader on Linux with a fresh login file judges as the reader with the copy in place", (r["rc"], j.get("cred_seen"), j.get("cred_mode"), "judge: reader" in r["out"]), (0, True, "0o600", True))
    chk("forced-copy: no secret in the report or vet's output, and the folder is gone", (ACCESS in r["text"] or REFRESH in r["text"], ACCESS in r["out"] or REFRESH in r["out"], any(r["cfg_left"])), (False, False, False))
    for why, kw in (("no login file in your config folder", dict(caller={})),
                    ("due to refresh within the hour", dict(caller={".credentials.json": login_file(hours=1 / 6)})),
                    ("your login didn't work as the reader", dict(caller=LOGIN, login="never"))):
        r = run("forced-stop " + why, **{"login": "file", "uname": "Linux", "extra": FORCED, **kw})
        chk("forced-stop: " + why + ": non-zero, no report, no judge call, the reason and --judge own on stderr", (r["rc"] != 0, r["report"], [c for c in r["calls"] if "single word ok" not in c["prompt"]], why in r["out"], "--judge own" in r["out"], ACCESS in r["out"]), (True, False, [], True, True, False))
    mine = reader_copy(tempfile.mkdtemp())
    r = run("forced-reader-dir", login="never", uname="Linux", caller=LOGIN, extra=(*FORCED, "--reader", mine))
    chk("forced-stop: a --reader folder never gets your login, and the line says so", (r["rc"] != 0, r["report"], "a --reader folder never gets your login" in r["out"], "--judge own" in r["out"]), (True, False, True, True))
    shutil.rmtree(os.path.dirname(mine))
    mine = reader_copy(tempfile.mkdtemp())
    r = run("forced-reader-dir-nocopy", login="env", uname="Linux", caller=LOGIN, extra=(*FORCED, "--reader", mine))
    chk("forced-reader-dir: a --reader folder gets no copy of your login, and the judge runs as that reader", (r["rc"], any(c["cred_seen"] for c in r["calls"])), (0, False))
    shutil.rmtree(os.path.dirname(mine))
    r = run("forced-web", login="env", uname="Linux", caller={}, extra=FORCED)
    j = judges(r)[0] if judges(r) else {}
    chk("forced-web: no login file but the probe passes (a web session): judges as the reader", (r["rc"], j.get("cfg") != "", "can't log in" in r["out"]), (0, True, False))
# a failing call() says why: the last lines of its own error, and never a token
r = run("call-fail", extra=("--units",), units="units-install", finds="one", confirm="fail")
chk("call-fail: a confirm call that exits non-zero: its last error lines reach stderr", (r["rc"] != 0, "fake-claude-error: quota exceeded" in r["out"]), (True, True))
r = run("call-fail-token", login="file", uname="Linux", caller=LOGIN, extra=("--units", *FORCED), units="units-install", finds="one", confirm="fail", fake_env=dict(FAKE_SECRET=ACCESS, FAKE_FAIL_MSG="denied for " + ACCESS))
chk("call-fail: an error line holding the login's token is dropped, not printed, and the call's error file is scanned and removed", (r["rc"] != 0, ACCESS in r["out"], "files holding your login's secrets were removed" in r["out"]), (True, False, True))
# the probe's own error follows the stop line; a token in it is dropped
r = run("forced-probe-msg", login="never", uname="Linux", caller=LOGIN, extra=FORCED, fake_env=SECRET)
lines = r["out"].split("\n")
stop = [i for i, l in enumerate(lines) if "--judge reader can't log in" in l]
chk("forced-probe: the probe's error line reaches stderr after the stop line", (len(stop) == 1 and any("Not logged in" in l for l in lines[stop[0] + 1:]) if stop else False), True)
r = run("forced-probe-token", login="never", uname="Linux", caller=LOGIN, extra=FORCED, fake_env=dict(FAKE_SECRET=ACCESS, FAKE_PROBE_MSG="denied for " + ACCESS))
chk("forced-probe: a probe error holding the login's token is dropped, not printed", (r["rc"] != 0, r["report"], ACCESS in r["out"], "--judge reader can't log in" in r["out"]), (True, False, False, True))
# the main judge failing: the last lines of its stdout reach stderr; a token never does
r = run("judge-fail", fake_env=dict(FAKE_JUDGE_FAIL="1"))
chk("judge-fail: a prose judge that exits non-zero: its last lines reach stderr", (r["rc"] != 0, "fake-judge-error: out of credit" in r["out"], "the prose judge exited non-zero" in r["out"]), (True, True, True))
r = run("judge-fail-token", login="file", uname="Linux", caller=LOGIN, extra=FORCED, fake_env=dict(FAKE_SECRET=ACCESS, FAKE_JUDGE_FAIL="1", FAKE_FAIL_MSG="denied for " + ACCESS))
chk("judge-fail: a judge message holding the login's token is not printed", (r["rc"] != 0, ACCESS in r["out"], r["report"]), (True, False, False))
# the judged report names the judge that ran, and vet --check still passes on it
for name, kw, want in (("judge-line-reader", dict(login="env"), "Judge: the sample reader's config"),
                       ("judge-line-own", dict(login="default", uname="Darwin"), "Judge: your own config, told to ignore it")):
    r = run(name, **kw)
    chk(name + ": the report carries the Judge line", want in r["text"], True)
    chk(name + ": the Judge line sits after the Baseline line, not in header lines 1-2", (want in r["text"].split("\n")[:3], r["text"].find("Baseline:") < r["text"].find(want)), (False, True))
    d = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(d, ".claude-plugin")); json.dump({"name": "demo", "version": "1.0.0"}, open(os.path.join(d, ".claude-plugin", "plugin.json"), "w"))
        open(os.path.join(d, "report.md"), "w", encoding="utf-8").write(r["text"])
        c = subprocess.run([VET, "--check", os.path.join(d, "report.md"), d], capture_output=True, text=True)
        chk(name + ": vet --check passes on it", c.returncode, 0)
    finally:
        shutil.rmtree(d)

sys.exit(vet_harness.summary("test_vet_judge"))
