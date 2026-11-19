#!/usr/bin/env python3
"""skip-disabled-skill-cost: the inventory records, for each skill, whether Claude Code puts its description in every session.
A skill whose frontmatter sets `disable-model-invocation: true` (YAML true, or the string "true" in any case) loads only when the
user calls it by name, so its dossier entry has model_invocable false; with the key absent or false it is true.

    python3 tools/test_inventory_skills.py
"""
import os, sys, tempfile, shutil, subprocess, json

HERE = os.path.dirname(os.path.abspath(__file__))
NB = os.path.dirname(HERE)
INVENTORY = os.path.join(NB, "skills", "neckbeard", "inventory.py")
TEMPS = []
fail = checks = 0


def chk(name, ok, detail=""):
    global fail, checks
    checks += 1
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        fail += 1


def skill_entries(frontmatter_lines, plugin=True):
    """The dossier's skills for one SKILL.md with these frontmatter lines, read by running the inventory on a temp target."""
    root = tempfile.mkdtemp(prefix="inv-skills-test-")
    TEMPS.append(root)
    if plugin:
        os.makedirs(os.path.join(root, ".claude-plugin"))
        with open(os.path.join(root, ".claude-plugin", "plugin.json"), "w") as f:
            json.dump({"name": "demo", "version": "1.0.0"}, f)
    os.makedirs(os.path.join(root, "skills", "x"))
    with open(os.path.join(root, "skills", "x", "SKILL.md"), "w") as f:
        f.write("---\nname: x\ndescription: Does x.\n" + "".join(l + "\n" for l in frontmatter_lines) + "---\nBody.\n")
    r = subprocess.run([sys.executable, INVENTORY, root], capture_output=True, text=True)
    try:
        return json.loads(r.stdout)["target"]["skills"]
    except Exception:
        return [{"error": (r.stdout + r.stderr)[:300]}]


CASES = [
    ("key true (YAML)", ["disable-model-invocation: true"], False),
    ('key "True" (string)', ['disable-model-invocation: "True"'], False),
    ('key "TRUE" (string)', ['disable-model-invocation: "TRUE"'], False),
    ("key false", ["disable-model-invocation: false"], True),
    ("key absent", [], True),
]
for plugin in (True, False):
    for name, fm, want in CASES:
        got = skill_entries(fm, plugin)
        chk(f"3. {'a plugin' if plugin else 'a plain pack'}, {name}: model_invocable is {want}",
            len(got) == 1 and got[0].get("model_invocable") is want, got)

for t_ in TEMPS:
    shutil.rmtree(t_, ignore_errors=True)
print(f"test_inventory_skills: {fail} failed" if fail else "test_inventory_skills: all passed")
sys.exit(1 if fail else 0)
