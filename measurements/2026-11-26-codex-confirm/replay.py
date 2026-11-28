#!/usr/bin/env python3
"""replay.py [--limit N]: replay the committed confirm calls through Codex, three times each, beside Sonnet's answers.

Run from anywhere inside this repo checkout on a machine with a Codex login. Writes one JSON per source run beside this file.
A source run whose JSON already holds three answers for every candidate is not called again.
The prompt is rendered as tools/vet renders it: tools/vet-confirm.md filled with label, heading, rule, sentence and test.
"""
import concurrent.futures, glob, json, os, re, signal, subprocess, sys, tempfile, threading, time

HERE = os.path.dirname(os.path.abspath(__file__))
NB = os.path.dirname(os.path.dirname(HERE))
M = os.path.join(NB, "measurements")
CODEX = ["codex", "exec", "-m", "gpt-6.1-sol", "-c", "model_reasoning_effort=high", "--sandbox", "read-only",
         "--skip-git-repo-check", "--ephemeral", "--json"]   # --json only so that any tool use and the token counts are recorded
SAMPLES, AT_ONCE, CAP_SECONDS = 3, 4, 300


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def sources():
    """(output name, candidates file, Sonnet's answers file), and nothing else under measurements/ is read."""
    for target in ("0403", "0532"):
        for n in range(1, 6):
            stem = f"{M}/2026-10-16-units-confirm/{target}/run-{n}"
            yield f"units-confirm-{target}-run-{n}", stem + ".recand.json", stem + ".reconf.json", stem + ".units.json"
    for n in range(1, 6):
        stem = f"{M}/2026-11-18-units-default/run-{n}"
        yield f"units-default-run-{n}", stem + ".candidates.json", stem + ".confirmations.json", stem + ".units.json"


def read_text(name):
    with open(os.path.join(NB, "tools", name), encoding="utf-8") as f:
        return f.read()


TEMPLATE = read_text("vet-confirm.md")
TEST = read_text("vet-conflict-test.md").rstrip("\n")   # tools/vet reads it with $(cat ...), which drops the final newline


def render(c):
    return TEMPLATE.format(rule=c["reader_rule"], sentence=c["quote"], test=TEST,
                           label=c["reader_rule"].split(": ", 1)[0], heading=c.get("heading", ""))


def call(prompt, cwd):
    """One codex exec. Returns (final message text, tool item types, token usage, error or None)."""
    p = subprocess.Popen([*CODEX, "-"], cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, start_new_session=True)
    try:
        out, err = p.communicate(prompt, timeout=CAP_SECONDS)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL)
        p.communicate()
        return "", [], {}, f"no answer within {CAP_SECONDS} s"
    text, tools, usage = "", [], {}
    for line in out.splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        item = e.get("item") or {}
        if e.get("type") == "item.completed":
            if item.get("type") == "agent_message":
                text = item.get("text", "")
            elif item.get("type") not in ("reasoning", "error"):   # error items here are startup warnings
                tools.append(item.get("type"))
        if e.get("type") == "turn.completed":
            usage = e.get("usage", {})
    return text, tools, usage, None if p.returncode == 0 else f"codex exited {p.returncode}"


def ask(prompt):
    """One sample: the answer, with one retry on no usable JSON, as tools/vet does."""
    why_not = []
    for attempt in (1, 2):
        cwd = tempfile.mkdtemp()   # empty
        start = time.time()
        text, tools, usage, error = call(prompt, cwd)
        seconds = round(time.time() - start, 1)
        try:
            a = json.loads(re.search(r"\{.*\}", text, re.S).group(0))
            assert isinstance(a["conflict"], bool)
            assert isinstance(a.get("hard_stop"), bool) or not a["conflict"]
        except Exception:
            why_not.append(error or f"no usable JSON in: {text[:200]!r}")
            continue
        return {"conflict": a["conflict"], "hard_stop": a.get("hard_stop") is True, "why": str(a.get("why", "")),
                "attempts": attempt, "seconds": seconds, "tool_items": tools,
                "input_tokens": usage.get("input_tokens"), "output_tokens": usage.get("output_tokens")}
    return {"conflict": None, "attempts": 2, "no_answer": why_not}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    runs, jobs = [], []
    for name, candf, conff, unitf in sources():
        cands = load(candf)["candidates"]
        sonnet = {c["cid"]: c for c in load(conff)["confirmations"]}
        units = {u["id"]: u for u in load(unitf)["units"]}
        path = os.path.join(HERE, name + ".json")
        old = {c["cid"]: c.get("codex", []) for c in load(path)["candidates"]} if os.path.exists(path) else {}
        rows = []
        for c in cands:
            s, u = sonnet[c["cid"]], units.get(c["id"], {})
            row = {"cid": c["cid"], "unit": c["id"], "unit_file": u.get("file"), "unit_heading": u.get("heading"),
                   "sentence": c["quote"], "reader_rule": c["reader_rule"], "heading": c.get("heading", ""),
                   "sonnet": {"conflict": s["conflict"], "hard_stop": s.get("hard_stop"), "why": s.get("why", "")},
                   "codex": old.get(c["cid"]) or [None] * SAMPLES}
            rows.append(row)
            for i in range(SAMPLES):
                if row["codex"][i] is None:
                    jobs.append((path, rows, row, i, render(c)))
        runs.append((path, candf, rows))
    jobs = jobs[:limit]
    source_of = {path: os.path.relpath(candf, NB) for path, candf, _ in runs}
    lock, done = threading.Lock(), []

    def one(job):
        path, rows, row, i, prompt = job
        a = ask(prompt)
        with lock:
            row["codex"][i] = a
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"source": source_of[path], "candidates": rows}, f, indent=1)
                f.write("\n")
            done.append(1)
            print(f"{len(done)}/{len(jobs)} {os.path.basename(path)} {row['cid']} sample {i + 1}: {a['conflict']}", flush=True)

    start = time.time()
    with concurrent.futures.ThreadPoolExecutor(AT_ONCE) as ex:
        list(ex.map(one, jobs))
    print(f"{len(jobs)} samples, {sum(len(r) for _, _, r in runs)} candidates, wall {time.time() - start:.0f} s", flush=True)


if __name__ == "__main__":
    main()
