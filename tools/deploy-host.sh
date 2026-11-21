#!/usr/bin/env bash
# deploy-host.sh VERSION SHA [ORIGIN_URL]: bring this machine's neckbeard to SHA, then print what it runs.
# `make deploy` runs it here and, over `ssh <host> bash -s`, on each of local.mk's HOSTS. It never builds or
# pushes: SHA must already be released, which only `make release` does.
#   1. the export: ~/.claude/plugin-src/neckbeard, a clone of origin that the neckbeard marketplace loads from.
#      It is made from ORIGIN_URL when missing, then fast-forwarded to exactly SHA (only a sha on origin/main,
#      only on a clean main). Nothing in it is ever edited by hand, so the working checkout can be on any branch
#      and as dirty as it likes. A marketplace that loads from anywhere else fails with the steps to switch it;
#      a git or GitHub source needs no export, step 2 fetches it. Only the local run gets ORIGIN_URL: this
#      machine's origin may be an ssh alias another host lacks, and each host reaches GitHub its own way. A
#      host with no export refuses and prints the clone step, for its owner to run with that host's transport
#   2. update the marketplace, then every Claude Code install of neckbeard (each scope and project)
#   3. verify: the export's commit, and the version each install now records
# Exit 0 only when every check passed. Kept out of bin/, which a plugin puts on every session's PATH.
set -u
version=${1:?usage: deploy-host.sh VERSION SHA [ORIGIN_URL]}
sha=${2:?usage: deploy-host.sh VERSION SHA [ORIGIN_URL]}
url=${3:-}
market=neckbeard
plugin=neckbeard@neckbeard
src=$HOME/.claude/plugin-src/neckbeard
fail=0
bad() { echo "FAIL $*"; fail=1; }

echo "== $(hostname -s 2>/dev/null || hostname): neckbeard $version (${sha:0:7})"

# the steps that point this machine's marketplace at the export, once
switch() {
  echo "To load neckbeard from $src, once on this machine:"
  [ -d "$src/.git" ] || echo "  git clone ${url:-<the neckbeard origin URL>} $src"
  echo "  claude plugin marketplace remove $market"
  echo "  claude plugin marketplace add $src"
  echo "  claude plugin install $plugin --scope user"
  echo "and for a project that installs it, from that project's folder: claude plugin install $plugin --scope project"
}

# 1. the export
read -r type loads < <(claude plugin marketplace list --json | python3 -c '
import json, sys
for m in json.load(sys.stdin):
    if m.get("name") == sys.argv[1]:
        print(m.get("source", ""), m.get("path") or m.get("installLocation") or "")' "$market")
case "${type:-}" in
  "") echo "FAIL no $market marketplace on this machine"; switch; exit 1 ;;
  directory)
    if [ "$(cd "$loads" 2>/dev/null && pwd -P)" != "$(cd "$src" 2>/dev/null && pwd -P)" ]; then
      echo "FAIL the $market marketplace loads from $loads, not from $src; any edit or checkout there reaches every session"
      switch; exit 1
    fi
    if [ ! -d "$src/.git" ]; then
      [ -n "$url" ] || { echo "FAIL no clone at $src and no origin URL to make one from"
                         echo "To make the export, once on this machine, with this machine's own way to reach origin:"
                         echo "  git clone <that host's own origin URL> $src"; exit 1; }
      mkdir -p "$(dirname "$src")" && git clone -q "$url" "$src" || { echo "FAIL clone of $url into $src"; exit 1; }
    fi
    [ -z "$(git -C "$src" status --porcelain --untracked-files=no)" ] ||
      { echo "FAIL $src has uncommitted changes, which every install would copy; nothing should edit it"; exit 1; }
    [ "$(git -C "$src" branch --show-current)" = main ] || { echo "FAIL $src isn't on main"; exit 1; }
    git -C "$src" fetch -q origin || { echo "FAIL fetch in $src"; exit 1; }
    git -C "$src" merge-base --is-ancestor "$sha" origin/main 2>/dev/null ||
      { echo "FAIL ${sha:0:7} isn't on $src's origin/main; run make release first"; exit 1; }
    git -C "$src" merge -q --ff-only "$sha" 2>/dev/null || { echo "FAIL $src won't fast-forward to ${sha:0:7}"; exit 1; }
    # an export with commits of its own on top of SHA merges "cleanly" and would be installed as it stands
    [ "$(git -C "$src" rev-parse HEAD)" = "$sha" ] || { echo "FAIL $src is ahead of ${sha:0:7}; installs would copy commits that were never released"; exit 1; } ;;
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
  [ "$at" = "$sha" ] && echo "ok   export $src at ${at:0:7}" || bad "export $src at ${at:0:7}, not ${sha:0:7}"
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
