#!/usr/bin/env bash
# dossier-det.sh NB TARGET N OUT: rebuild the dossier N times the way tools/vet does (fresh sample-reader copy,
# empty project, CLAUDE_CONFIG_DIR=reader), keep each, hash each, and hash each again with its temp path blanked.
nb=$1 target=$2 n=$3 out=$4
mkdir -p "$out"
for i in $(seq "$n"); do
  work=$(mktemp -d)
  cp -R "$nb/examples/reader" "$work/reader" && mkdir "$work/project"
  reader=$(cd "$work/reader" && pwd -P); project=$(cd "$work/project" && pwd -P)
  CLAUDE_CONFIG_DIR=$reader python3 "$nb/skills/neckbeard/inventory.py" "$target" --project-dir "$project" --out "$out/dossier-$i.json" >"$out/inventory-$i.log" 2>&1; echo "run $i exit $?"
  sed "s#$work#<WORK>#g" "$out/dossier-$i.json" >"$out/dossier-$i.norm.json"
  rm -rf "$work"
done
echo "-- raw"; sha256sum "$out"/dossier-?.json
echo "-- with the temp path blanked"; sha256sum "$out"/dossier-?.norm.json
