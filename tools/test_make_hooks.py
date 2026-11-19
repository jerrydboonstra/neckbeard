#!/usr/bin/env python3
"""The POST_DEPLOY hook in the Makefile: `make post-deploy`, and where `make deploy` calls it.

Runs `make post-deploy` in this checkout. The deploy cases, `make -n deploy` (the recipe as text; it
calls post-deploy through a variable so that -n runs nothing) included, run in a scratch repo:
a copy of the Makefile and plugin.json, a bare origin on main, and a stub tools/deploy-host.sh.
The hook is `echo` or `false`, so nothing is deleted, no model is called and there is no network.

    python3 tools/test_make_hooks.py
"""
import json, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = json.load(open(os.path.join(ROOT, ".claude-plugin", "plugin.json")))["version"]
fail = checks = 0


def chk(name, got, want):
    global fail, checks
    checks += 1
    ok = got == want
    fail += not ok
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + ("" if ok else f": {got!r}, wanted {want!r}"))


def make(cwd, *args):
    p = subprocess.run(["make", *args], cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def sh(cwd, *a):
    subprocess.run(a, cwd=cwd, capture_output=True, text=True, check=True)


def scratch(host_exit):
    """A scratch checkout on main whose origin's main is the same commit, and a deploy-host.sh stub."""
    d = tempfile.mkdtemp()
    origin, work = os.path.join(d, "origin.git"), os.path.join(d, "work")
    sh(d, "git", "init", "-q", "--bare", "-b", "main", origin)
    os.makedirs(os.path.join(work, ".claude-plugin"))
    os.makedirs(os.path.join(work, "tools"))
    shutil.copy(os.path.join(ROOT, "Makefile"), work)
    shutil.copy(os.path.join(ROOT, ".claude-plugin", "plugin.json"), os.path.join(work, ".claude-plugin"))
    with open(os.path.join(work, "tools", "deploy-host.sh"), "w") as f:
        f.write(f"echo host-deployed\nexit {host_exit}\n")
    sh(work, "git", "init", "-q", "-b", "main")
    sh(work, "git", "remote", "add", "origin", origin)
    sh(work, "git", "add", "-A")
    sh(work, "git", "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-q", "-m", "x")
    sh(work, "git", "push", "-q", "origin", "main")
    return d, work


print("make post-deploy")
code, out = make(ROOT, "post-deploy", "POST_DEPLOY=echo shipped $(VERSION)")
chk("a set hook runs once and sees the plugin.json version", (code, out.count("shipped " + VERSION), out.strip()), (0, 1, "shipped " + VERSION))
code, out = make(ROOT, "post-deploy", "POST_DEPLOY=")
chk("an empty hook prints nothing and exits 0", (code, out), (0, ""))
code, out = make(ROOT, "post-deploy", "POST_DEPLOY=false")
chk("a failing hook fails the target", code != 0, True)

print("make -n deploy, in a scratch repo (a deploy line that ran under -n would print the stub's host-deployed)")
d, work = scratch(0)
code, out = make(work, "-n", "deploy", "POST_DEPLOY=echo shipped $(VERSION)")
shutil.rmtree(d)
i_loop, i_if, i_call = out.find("deploy-host.sh"), out.find("if [ $fail -eq 0 ]"), out.find("post-deploy VERSION=" + VERSION)
chk("the post-deploy call sits after the host loop and behind the fail check",
    (i_loop != -1, i_loop < i_if < i_call, out.rfind("done;") < i_if), (True, True, True))
chk("the recipe ends with the exit on fail", out.rstrip().endswith("exit $fail"), True)
chk("-n runs no host deploy and no hook", (code, out.count("shipped " + VERSION), "host-deployed" in out), (0, 0, False))

print("make deploy in a scratch repo")
d, work = scratch(0)
code, out = make(work, "deploy", "POST_DEPLOY=echo shipped $(VERSION)")
chk("every host deployed: the hook runs after the host, and deploy exits 0",
    (code, out.find("host-deployed") < out.find("shipped " + VERSION), out.count("shipped " + VERSION)), (0, True, 1))
code, out = make(work, "deploy", "POST_DEPLOY=false")
chk("a failing hook is printed and deploy fails (make exits 2)", (code, "deploy: post-deploy failed" in out), (2, True))
code, out = make(work, "deploy")
chk("no hook set: deploy exits 0 and prints no hook output", (code, "post-deploy" in out), (0, False))
shutil.rmtree(d)

d, work = scratch(1)
code, out = make(work, "deploy", "POST_DEPLOY=echo shipped $(VERSION)")
chk("a host failed: the hook does not run, and deploy fails (make exits 2)", (code, "shipped" in out), (2, False))
shutil.rmtree(d)

print(f"\n{checks - fail} passed, {fail} failed")
sys.exit(1 if fail else 0)
