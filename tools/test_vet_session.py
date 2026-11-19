#!/usr/bin/env python3
"""tools/vet's session mode (vet-session-answers): --dossier, --answers and --prose assemble a fit report from a calling session's own
judgement, with no model call. Split from tools/test_vet.py to stay under the test-module size cap; the helpers it shares are in
tools/vet_harness.py.

    python3 tools/test_vet_session.py
"""
import json, os, shutil, subprocess, sys, tempfile

import vet_harness
from vet_harness import *


# 13. session mode: --dossier, --answers and --prose assemble a fit report from a calling session's own judgement, with no model call
# (vet-session-answers). The dossier is built by the real inventory under a fixture home and project; a `claude` on PATH fails if it is called.
import hashlib
FIX = os.path.join(os.path.dirname(VET), "fixtures", "vet-session")
SESSION_SKILL = "---\nname: demo\ndescription: A demo skill.\n---\n\nAlways run the tests before you commit.\n\n## Second\n\nKeep commits small.\n"
TOOLS = os.path.dirname(VET)


def session_fixture(tmp, project_in_home=False, no_rules=False, name="demo", project="proj"):
    """tmp/home, a project, a plugin and a real dossier of them; returns paths."""
    home = os.path.join(tmp, "home")
    os.makedirs(os.path.join(home, ".claude"))
    proj = {"home": home, "above": tmp}.get(project) or (os.path.join(home, "work", "proj") if project_in_home else os.path.join(tmp, "proj"))
    os.makedirs(proj, exist_ok=True)
    other = os.path.join(tmp, "other"); os.makedirs(other)
    if not no_rules:
        shutil.copy(os.path.join(FIX, "home", ".claude", "CLAUDE.md"), os.path.join(home, ".claude", "CLAUDE.md"))
        shutil.copy(os.path.join(FIX, "project", "CLAUDE.md"), os.path.join(proj, "CLAUDE.md"))
        shutil.copy(os.path.join(FIX, "other", "outside-rules.md"), os.path.join(other, "outside-rules.md"))
    target = os.path.join(tmp, name)
    os.makedirs(os.path.join(target, ".claude-plugin")); os.makedirs(os.path.join(target, "skills", "demo"))
    json.dump({"name": name, "version": "1.0.0"}, open(os.path.join(target, ".claude-plugin", "plugin.json"), "w"))
    open(os.path.join(target, "skills", "demo", "SKILL.md"), "w").write(SESSION_SKILL)
    dossier = os.path.join(tmp, "caller", name + "-dossier.json")
    os.makedirs(os.path.dirname(dossier))
    env = {**os.environ, "HOME": home, "CLAUDE_CONFIG_DIR": os.path.join(home, ".claude")}
    extra = [] if no_rules else ["--extra-rules", os.path.join(other, "outside-rules.md")]
    subprocess.run([sys.executable, os.path.join(TOOLS, "..", "skills", "neckbeard", "inventory.py"), target, "--project-dir", proj, "--out", dossier, *extra], env=env, check=True, capture_output=True)
    units = os.path.join(tmp, "caller", "units.json")
    subprocess.run([sys.executable, os.path.join(TOOLS, "rule-units"), dossier, units], check=True, capture_output=True)
    ids = [u["id"] for u in json.load(open(units))["units"]]
    return dict(tmp=tmp, home=home, proj=proj, other=other, target=target, dossier=dossier, ids=ids)


def write_answers(fx, name="answers.json", edit=None):
    answers = [{"id": i, "skill": "keep", "rules": "none", "quote": "", "why": "x", "conflicts": [], "star": n == 0} for n, i in enumerate(fx["ids"])]
    if edit:
        answers = edit(answers)
    path = os.path.join(fx["tmp"], "caller", name)
    json.dump({"answers": answers}, open(path, "w"))
    return path


def session_vet(fx, answers=None, prose=None, args=None, target=None, out=None, dossier=None):
    """tools/vet in session mode; returns rc, combined output, the report's text (None when not written), the log of `claude` calls."""
    bindir = os.path.join(fx["tmp"], "bin"); os.makedirs(bindir, exist_ok=True)
    open(os.path.join(bindir, "claude"), "w").write(NO_CLAUDE); os.chmod(os.path.join(bindir, "claude"), 0o755)
    log = os.path.join(fx["tmp"], "claude.log")
    out = out or os.path.join(fx["tmp"], "out", "report.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if os.path.exists(out) and not out.endswith(".verdict.json"):
        os.remove(out)   # each run starts with no report, so a refusal is seen to write none
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_CONFIG_DIR"}
    os.makedirs(os.path.join(fx["tmp"], "t"), exist_ok=True)
    env.update(HOME=fx["home"], PATH=bindir + os.pathsep + env["PATH"], FAKE_LOG=log, TMPDIR=os.path.join(fx["tmp"], "t"))
    if args is None:
        args = ["--dossier", dossier or fx["dossier"], "--answers", answers or write_answers(fx), "--prose", prose or os.path.join(FIX, "prose.json")]
    p = subprocess.run([VET, target or fx["target"], out, *args], env=env, capture_output=True, text=True, cwd=fx["tmp"])
    return dict(rc=p.returncode, out=p.stdout + p.stderr, stdout=p.stdout, outpath=out, text=open(out, encoding="utf-8").read() if os.path.exists(out) else None,
                calls=[json.loads(l) for l in open(log)] if os.path.exists(log) else [], temp_left=os.listdir(env["TMPDIR"]))


def verdict_of(fx, answers):
    units = os.path.join(fx["tmp"], "caller", "units.json")
    return json.loads(subprocess.run([sys.executable, os.path.join(TOOLS, "units-verdict"), units, answers, "--json"], capture_output=True, text=True, check=True).stdout)


def fingerprint(files):
    h = hashlib.sha256()
    for name, data in sorted(files):
        h.update(name.encode("utf-8") + b"\0" + data + b"\0")
    return h.hexdigest()[:12]


def with_session(fn):
    tmp = tempfile.mkdtemp()
    try:
        return fn(tmp)
    finally:
        shutil.rmtree(tmp)


def case_main(tmp):
    fx = session_fixture(tmp)
    answers = write_answers(fx)
    caller_before = {f: open(os.path.join(tmp, "caller", f), "rb").read() for f in os.listdir(os.path.join(tmp, "caller"))}
    prose_before = open(os.path.join(FIX, "prose.json"), "rb").read()
    r = session_vet(fx, answers=answers)
    v = verdict_of(fx, answers)
    files = [("~/.claude/CLAUDE.md", open(os.path.join(FIX, "home", ".claude", "CLAUDE.md"), "rb").read()),
             ("CLAUDE.md", open(os.path.join(FIX, "project", "CLAUDE.md"), "rb").read()),
             ("outside-rules.md", open(os.path.join(FIX, "other", "outside-rules.md"), "rb").read())]
    fp, nbytes = fingerprint(files), sum(len(d) for _, d in files)
    text = r["text"] or ""
    chk("session: exit 0, report written", (r["rc"], r["text"] is not None), (0, True))
    chk("session: title ends ' · against your rules'", text.split("\n")[0], "# \U0001F50D demo 1.0.0 · how it affects you, what it adds, where it takes a position · against your rules")
    marks = {"INSTALL": "\U0001F7E9", "INSTALL WITH CHANGES": "\U0001F7E8", "COPY RULES, SKIP PLUGIN": "\U0001F7E8", "DON'T INSTALL": "\U0001F7E5"}
    chk("session: the verdict strip is the one units-verdict computes", ("> **" + marks.get(v["verdict"], "?") + " " + v["verdict"] + "**") in text, True)
    chk("session: the Baseline line, with the fingerprint over the shown names", f"Baseline: your rules · 3 rule files · {nbytes} bytes · sha256 {fp}" in text, True)
    chk("session: the Judge line", "Judge: this session" in text, True)
    chk("session: no other judge named", ("the sample reader's config" in text, "told to ignore it" in text), (False, False))
    chk("session: Rule files named ~/..., project-relative or by basename", [f"- `{n}`" in text for n in ("~/.claude/CLAUDE.md", "CLAUDE.md", "outside-rules.md")], [True] * 3)
    chk("session: the 'Verdict is relative' sentence", f"Verdict is relative to your 3 rule files (fingerprint {fp}), not a judgment of the plugin's quality." in text, True)
    chk("session: the prose is the session's own", "The session's own prose: one skill is worth keeping." in text, True)
    chk("session: the Contents line says 'your rules', not 'your rules's rules'", ("your rules's" in text, "the fit against your rules." in text), (False, True))
    chk("session: no local path in the report", [p in text for p in (tmp, os.path.realpath(tmp), fx["home"], fx["target"])], [False] * 4)
    chk("session: no claude process started", r["calls"], [])
    chk("session: the prose file is as it was", open(os.path.join(FIX, "prose.json"), "rb").read() == prose_before, True)
    chk("session: the caller's dossier and answers are as they were, and not moved", {f: open(os.path.join(tmp, "caller", f), "rb").read() for f in os.listdir(os.path.join(tmp, "caller")) if f in caller_before} == caller_before, True)
    stem = r["outpath"][:-3]
    chk("session: the units and the verdict records are kept beside the report; the caller's files are not copied there",
        sorted(f for f in os.listdir(os.path.dirname(r["outpath"])) if f != "report.md"), ["report.units.json", "report.verdict.json"])
    chk("session: temp folder removed", r["temp_left"], [])
    # a confirmed conflict in the units-confirm form counts
    answers = write_answers(fx, "answers2.json", edit=lambda a: [{**a[0], "conflicts": [{"quote": "Always run the tests before you commit.", "reader_rule": "CLAUDE.md: Prefer small commits.", "held_in": "CLAUDE.md", "hard_stop": False}]}, *a[1:]])
    r = session_vet(fx, answers=answers)
    v2 = verdict_of(fx, answers)
    chk("session: a conflict gives INSTALL WITH CHANGES and the counts units-verdict gives", (r["rc"], v2["verdict"], v2["counts"]["conflicts"], "> **\U0001F7E8 INSTALL WITH CHANGES**" in (r["text"] or ""), "\u26d4 **1** conflicts" in (r["text"] or "")), (0, "INSTALL WITH CHANGES", 1, True, True))
    # the session writes held_in as the Rule files block names it, and vet uses it as given
    answers = write_answers(fx, "answers3.json", edit=lambda a: [{**a[0], "skill": "drop", "rules": "duplicate", "covered_by": "Never run anything destructive", "held_in": "~/.claude/CLAUDE.md (as the session wrote it)", "star": False}, *a[1:]])
    r = session_vet(fx, answers=answers)
    chk("session: held_in is used as given", (r["rc"], "~/.claude/CLAUDE.md (as the session wrote it)" in (r["text"] or "")), (0, True))
    # --note works beside the three flags
    r = session_vet(fx, answers=answers, args=["--dossier", fx["dossier"], "--answers", answers, "--prose", os.path.join(FIX, "prose.json"), "--note", "A self-vetting."])
    chk("session: --note leads the 'Verdict is relative' sentence", (r["rc"], "A self-vetting. Verdict is relative to your 3 rule files" in (r["text"] or "")), (0, True))


def case_names(tmp):
    fx = session_fixture(tmp, project_in_home=True)
    r = session_vet(fx)
    text = r["text"] or ""
    chk("session: a project inside the home folder is named project-relative, the global file ~/...", (r["rc"], "- `CLAUDE.md`" in text, "- `~/.claude/CLAUDE.md`" in text, "work/proj" in text), (0, True, True, False))


def case_project_roots(tmp):
    for where in ("home", "above"):
        with_session_dir = tempfile.mkdtemp(dir=tmp)
        fx = session_fixture(with_session_dir, project=where)
        text = session_vet(fx)["text"] or ""
        chk("session: a project that is the home folder or above it: the global file is named ~/..., and no folder name leaks (" + where + ")",
            ("- `~/.claude/CLAUDE.md`" in text, os.path.basename(fx["home"]) + "/.claude" in text.replace("~/.claude", "")), (True, False))


def case_refusals(tmp):
    fx = session_fixture(tmp)
    one = lambda a: a[:-1]
    r = session_vet(fx, answers=write_answers(fx, edit=one))
    chk("session: answers that miss a unit: exit 1, the unit named, no report", (r["rc"], fx["ids"][-1] + ": no answer" in r["out"], r["text"]), (1, True, None))
    r = session_vet(fx, answers=write_answers(fx, edit=lambda a: [*a, {**a[0], "id": "u99"}]))
    chk("session: an unknown unit id: exit 1, named, no report", (r["rc"], "u99: no such unit" in r["out"], r["text"]), (1, True, None))
    r = session_vet(fx, answers=write_answers(fx, edit=lambda a: [{**a[0], "skill": "maybe"}, *a[1:]]))
    chk("session: answers units-verdict refuses: exit 1, its reason named, no report", (r["rc"], "skill 'maybe'" in r["out"], r["text"]), (1, True, None))
    other = os.path.join(tmp, "elsewhere"); shutil.copytree(fx["target"], other)
    r = session_vet(fx, target=other)
    chk("session: a dossier for another target: exit 1, says so, no report", (r["rc"], "dossier" in r["out"], r["text"]), (1, True, None))
    d = json.load(open(fx["dossier"])); d["target"]["path"] = None
    nulled = os.path.join(tmp, "caller", "null-dossier.json"); json.dump(d, open(nulled, "w"))
    r = session_vet(fx, dossier=nulled)
    chk("session: a dossier with no target path: exit 1, says so, no traceback, no report", (r["rc"], "names no target path" in r["out"], "Traceback" in r["out"], r["text"]), (1, True, False, None))
    link = os.path.join(tmp, "link"); os.symlink(fx["target"], link)
    r = session_vet(fx, target=link)
    chk("session: the same folder through a symlink is the same target", (r["rc"], r["text"] is not None), (0, True))
    r = session_vet(fx, target="demo@some-market")
    chk("session: a target that is not a local folder: usage, exit 2", (r["rc"], "usage:" in r["out"], r["text"]), (2, True, None))
    # the caller's answers file is never taken for a file vet writes
    for clash_name in ("report.verdict.json", "report.units.json"):
        clash = os.path.join(tmp, "out", clash_name)
        shutil.copy(write_answers(fx), clash)
        before = open(clash, "rb").read()
        r = session_vet(fx, answers=clash)
        chk("session: an answers file named " + clash_name + " beside OUT is refused and survives", (r["rc"], open(clash, "rb").read() == before if os.path.exists(clash) else None, r["text"]), (1, True, None))
        os.remove(clash)
    dos = shutil.copy(fx["dossier"], os.path.join(tmp, "out", "report.units.json"))
    r = session_vet(fx, dossier=dos)
    chk("session: a dossier named like a file vet writes is refused and survives", (r["rc"], os.path.exists(dos), r["text"]), (1, True, None))
    os.remove(dos)
    chk("session: the caller's dossier is never deleted", os.path.exists(fx["dossier"]), True)
    os.rename(os.path.join(tmp, "proj", "CLAUDE.md"), os.path.join(tmp, "proj", "gone.md"))
    r = session_vet(fx)
    chk("session: a listed rule file that can no longer be read: exit 1, named, no report", (r["rc"], "CLAUDE.md" in r["out"] and "can no longer be read" in r["out"], r["text"]), (1, True, None))


def case_no_rules(tmp):
    fx = session_fixture(tmp, no_rules=True)
    r = session_vet(fx, answers=write_answers(fx, edit=lambda a: []))
    chk("session: a dossier that lists no rule files gets the facts report, exit 0, one line saying why",
        (r["rc"], "No reader's rules were read" in (r["text"] or ""), "> **" in (r["text"] or ""), "no rule files" in r["out"], r["calls"]), (0, True, False, True, []))
    r = session_vet(fx, answers=write_answers(fx, edit=lambda a: []), args=["--dossier", fx["dossier"], "--answers", write_answers(fx, edit=lambda a: []), "--prose", os.path.join(FIX, "prose.json"), "--note", "Dropped here."])
    chk("session: --note does not carry over to the facts fallback", (r["rc"], "Dropped here." in (r["text"] or ""), "No reader's rules were read" in (r["text"] or "")), (0, False, True))


def case_usage(tmp):
    fx = session_fixture(tmp)
    a, d, p = write_answers(fx), fx["dossier"], os.path.join(FIX, "prose.json")
    some = [["--dossier", d], ["--answers", a], ["--prose", p], ["--dossier", d, "--answers", a], ["--dossier", d, "--prose", p], ["--answers", a, "--prose", p]]
    rcs = [session_vet(fx, args=x) for x in some]
    chk("session: only some of the three flags: usage, exit 2, no report, no claude", [(r["rc"], "usage:" in r["out"], r["text"], r["calls"]) for r in rcs], [(2, True, None, [])] * len(some))
    full = ["--dossier", d, "--answers", a, "--prose", p]
    bad = [["--reader", fx["home"]], ["--judge", "own"], ["--model", "sonnet"], ["--units"], ["--facts"]]
    rcs = [session_vet(fx, args=full + x) for x in bad]
    chk("session: with --reader, --judge, --model, --units or --facts: usage, exit 2, no report, no claude", [(r["rc"], "usage:" in r["out"], r["text"], r["calls"]) for r in rcs], [(2, True, None, [])] * len(bad))
    chk("session: the usage line names the three flags", "--dossier DOSSIER --answers ANSWERS --prose PROSE" in session_vet(fx, args=["--dossier", d])["out"], True)


for case in (case_main, case_names, case_project_roots, case_refusals, case_no_rules, case_usage):
    with_session(case)


sys.exit(vet_harness.summary("test_vet_session"))
