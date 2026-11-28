#!/usr/bin/env python3
"""persist-scan: which shell redirects make inventory_persistence list a script. A redirect to a device (/dev/null and the like) and the
`<name>/` placeholder in usage text are not writes; a redirect to a file that persists still is. Each case is a one-script tree scanned
in this process."""
import atexit, os, shutil, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "skills", "neckbeard"))
from inventory_hooks import inventory_persistence  # noqa: E402

fail = checks = 0


def chk(name, ok, detail=""):
    global fail, checks
    checks += 1
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        fail += 1


def listed(line, end="\n"):
    """True when a tree holding one shell script with this line has it listed."""
    d = tempfile.mkdtemp(prefix="persist-scan-")
    atexit.register(shutil.rmtree, d, True)
    with open(os.path.join(d, "s.sh"), "w") as f:
        f.write("#!/bin/sh\n" + line + end)
    return inventory_persistence(d) == ["s.sh"]


NOT_WRITES = {
    "1. a redirect to /dev/null is not a write": [
        "cmd >/dev/null 2>&1", "cmd 2>/dev/null", "cmd >> /dev/null", "cmd &>/dev/null", 'cmd > "/dev/null"',
        "x=$(cmd 2>/dev/null)", "cmd >/dev/null; next", "cmd >/dev/null|next",
        "cmd >/dev/null\nnext", "first\ncmd 2>/dev/null\nsecond\nthird",
        "cmd >/dev/null& next", "sh -c 'cmd >/dev/null'", "(cmd >/dev/null)", "x=`cmd 2>/dev/null`", "cmd >/dev/null<in",
        "cmd 2>/dev/null>log", "sh -c \"sh -c 'cmd >/dev/null'\"", "cmd >/dev/null \\\n  --flag", "cmd >/dev/null\\\n next",
    ],
    "1. a redirect to /dev/stderr, /dev/fd/2, /dev/stdout or /dev/tty is not a write": [
        "echo x >/dev/stderr", "echo x > /dev/fd/2", "echo x >/dev/stdout", "echo x > /dev/tty", "echo x >/dev/fd/10",
    ],
    "2. usage text holding <name>/ is not a write": [
        'echo "usage: tool <name>/.claude-plugin"', 'echo "see <base-dir>/work and <home>/runs"',
    ],
}
WRITES = [
    "echo x > ~/.foo", 'echo x >> "$HOME/.foo"', "echo x > $HOME/x", "echo x > /tmp/x", "echo x >/etc/x",
    "cat foo>/tmp/x", "echo x > /dev/../home/x", "echo x >/dev/nullx", "echo x >/dev/null/x", "echo x > /dev/shm/x",
    "echo x >/dev/fd/x", "cmd >/dev/null >/tmp/x", "echo '<name>' >/tmp/x", "sort <in >/tmp/x", "echo <name>>/tmp/x",
    "sort <in>~/x", "exec 3<>/tmp/x", "echo x > '/tmp/x'", "echo x > '$HOME/x'", "echo x >>$HOME/x", "echo x >~/x",
    "echo x >>/tmp/x",
    'echo x >/dev/null"x"', "echo x >/dev/null'x'", "echo x >/dev/null,log", "echo x >/dev/null\\ x", 'sh -c "cmd >/dev/null\\"x\\""',
    "echo x >/dev/null\\\nx", "echo x >/dev/null`printf .log`",
]

for name, lines in NOT_WRITES.items():
    wrong = [l for l in lines if listed(l)]
    chk(name, not wrong, f"listed: {wrong}")
chk("1. a device redirect that ends the file, with no newline, is not a write", not listed("cmd >/dev/null", end=""))
wrong = [l for l in WRITES if not listed(l)]
chk("3. a redirect to a file that persists is still a write", not wrong, f"not listed: {wrong}")

print(f"{checks - fail}/{checks} checks pass")
sys.exit(1 if fail else 0)
