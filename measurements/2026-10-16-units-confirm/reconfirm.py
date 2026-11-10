#!/usr/bin/env python3
"""reconfirm.py NB DOSSIER RUNDIR...: pool the committed find passes again with the reader's own rule text, and confirm again.

For each RUNDIR/run-N.finds-[123].json: tools/units-confirm pool (with DOSSIER, so the rule is the reader's own text), then one
tool-less Sonnet call per candidate, as tools/vet makes it (one retry on no JSON). Writes run-N.recand.json,
run-N.reconf.json, run-N.reconfirmed.json and appends "cost duration_ms" lines to RUNDIR/recost.txt.
Run on agentbay: python3 reconfirm.py ~/runs/nb-confirm-tip2 DOSSIER 0403 0532
"""
import concurrent.futures, glob, json, os, re, subprocess, sys, tempfile

nb, dossier, rundirs = sys.argv[1], sys.argv[2], sys.argv[3:]
test = open(f"{nb}/tools/vet-conflict-test.md", encoding="utf-8").read()
template = open(f"{nb}/tools/vet-confirm.md", encoding="utf-8").read()
cwd = tempfile.mkdtemp()


def ask(prompt):
    for _ in range(2):
        r = subprocess.run(["claude", "-p", "--model", "sonnet", "--allowedTools", "", "--output-format", "json"],
                           input=prompt, capture_output=True, text=True, cwd=cwd)
        try:
            j = json.loads(r.stdout)
            text = j.get("result", "")
            a = json.loads(re.search(r"\{.*\}", text, re.S).group(0))
            assert isinstance(a["conflict"], bool)
            return a, j.get("total_cost_usd", 0), j.get("duration_ms", 0)
        except Exception:
            continue
    return None, 0, 0


for d in rundirs:
    for units in sorted(glob.glob(f"{d}/run-?.units.json")):
        stem = units[: -len(".units.json")]
        finds = sorted(glob.glob(f"{stem}.finds-?.json"))
        subprocess.run([f"{nb}/tools/units-confirm", "pool", units, dossier, f"{stem}.recand.json", *finds], check=True)
        cands = json.load(open(f"{stem}.recand.json"))["candidates"]
        prompts = [template.format(rule=c["reader_rule"], sentence=c["quote"], test=test) for c in cands]
        with concurrent.futures.ThreadPoolExecutor(len(cands) or 1) as ex:
            got = list(ex.map(ask, prompts))
        confs, kept = [], []
        for c, (a, cost, ms) in zip(cands, got):
            if a is None:
                sys.exit(f"{stem} {c['cid']}: no usable answer")
            open(f"{d}/recost.txt", "a").write(f"{cost} {ms}\n")
            confs.append({"cid": c["cid"], "conflict": a["conflict"], "why": str(a.get("why", ""))})
            if a["conflict"]:
                kept.append(c)
        json.dump({"confirmations": confs}, open(f"{stem}.reconf.json", "w"), indent=1)
        json.dump({"confirmed": kept}, open(f"{stem}.reconfirmed.json", "w"), indent=1)
        print(f"{stem}: {len(kept)} of {len(cands)} confirmed")
