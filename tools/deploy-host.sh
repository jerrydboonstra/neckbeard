#!/usr/bin/env bash
# deploy-host.sh VERSION SHA: bring this machine's neckbeard to SHA, then print what it runs.
# `make deploy` runs it here and, over `ssh <host> bash -s`, on each of local.mk's HOSTS. It never builds or
# pushes: SHA must already be released, which only `make release` does.
#   1. the neckbeard marketplace's source: a directory source must be a clean git checkout, fast-forwarded to
#      exactly SHA (installs copy its working tree); a git or GitHub source is fetched by step 2
#   2. update the marketplace, then every Claude Code install of neckbeard (each scope and project)
#   3. verify: the checkout's commit, and the version each install now records
# Exit 0 only when every check passed. Kept out of bin/, which a plugin puts on every session's PATH.
set -u
version=${1:?usage: deploy-host.sh VERSION SHA}
sha=${2:?usage: deploy-host.sh VERSION SHA}
market=neckbeard
plugin=neckbeard@neckbeard
fail=0
bad() { echo "FAIL $*"; fail=1; }

echo "== $(hostname -s 2>/dev/null || hostname): neckbeard $version (${sha:0:7})"

# 1. the source
read -r type src < <(claude plugin marketplace list --json | python3 -c '
import json, sys
for m in json.load(sys.stdin):
    if m.get("name") == sys.argv[1]:
        print(m.get("source", ""), m.get("path") or m.get("installLocation") or "")' "$market")
case "${type:-}" in
  "") echo "FAIL no $market marketplace on this machine"; exit 1 ;;
  directory)
    git -C "$src" rev-parse --git-dir >/dev/null 2>&1 || { echo "FAIL $src isn't a git checkout"; exit 1; }
    [ -z "$(git -C "$src" status --porcelain --untracked-files=no)" ] ||
      { echo "FAIL $src has uncommitted changes, which every install would copy; commit or stash them"; exit 1; }
    if [ "$(git -C "$src" rev-parse HEAD)" != "$sha" ]; then
      [ "$(git -C "$src" branch --show-current)" = main ] || { echo "FAIL $src isn't on main"; exit 1; }
      git -C "$src" fetch -q origin || { echo "FAIL fetch in $src"; exit 1; }
      git -C "$src" merge -q --ff-only "$sha" 2>/dev/null || { echo "FAIL $src won't fast-forward to ${sha:0:7}"; exit 1; }
    fi ;;
  *) ;;
esac

# 2. the marketplace, then every install claude knows about
claude plugin marketplace update "$market" >/dev/null || bad "marketplace update"
installs() {
  claude plugin list --json | python3 -c '
import json, sys
for r in json.load(sys.stdin):
    if r.get("id") == sys.argv[1]:
        print(r.get("scope", ""), r.get("version", ""), r.get("projectPath", ""), sep="\t")' "$plugin"
}
while IFS=$'\t' read -r scope _ project; do
  if [ -n "$project" ] && [ ! -d "$project" ]; then
    echo "skip $scope install in $project (the folder is gone)"; continue
  fi
  (cd "${project:-$HOME}" && claude plugin update "$plugin" --scope "$scope" >/dev/null) ||
    bad "plugin update ($scope${project:+, $project})"
done < <(installs)

# 3. verify
if [ "$type" = directory ]; then
  at=$(git -C "$src" rev-parse HEAD)
  [ "$at" = "$sha" ] && echo "ok   source $src at ${at:0:7}" || bad "source $src at ${at:0:7}, not ${sha:0:7}"
fi
n=0
while IFS=$'\t' read -r scope v project; do
  [ -n "$project" ] && [ ! -d "$project" ] && continue
  n=$((n + 1))
  where="$scope${project:+ $project}"
  if [ "$v" = "$version" ]; then
    echo "ok   $v  $where"
  elif [ -n "$project" ] && [ "$(git -C "$project" rev-parse --git-dir 2>/dev/null)" != \
       "$(git -C "$project" rev-parse --git-common-dir 2>/dev/null)" ]; then
    # debt: Claude Code resolves a linked worktree to its main checkout, so `plugin update` there leaves this
    # record behind. Sessions there still load the current copy (Cat Herder checked it, 2026-09-29). Upgrade
    # path: fail here too once plugin update updates worktree records.
    echo "note $v  $where (an old record left by a git worktree; harmless)"
  else
    bad "$v  $where (wanted $version)"
  fi
done < <(installs)
[ "$n" -gt 0 ] || bad "no installs of $plugin listed"
[ "$fail" = 0 ] && echo "== deployed" || echo "== NOT fully deployed; see FAIL lines"
exit "$fail"
