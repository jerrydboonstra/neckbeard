#!/usr/bin/env bash
# ci-wait.sh <sha>: pass once GitHub Actions' CI workflow has passed on <sha>, waiting while it runs. tools/release-push runs
# it after pushing main to GitHub, so a release is tagged only on a commit CI passed. It reads the workflow run for the
# exact commit, looked up by sha. One passing run is enough (a re-run that passed after a flaky one counts). Adapted from
# Cat Herder's tools/ci-wait.sh.
# Env: CI_REPO (owner/name), CI_POLL (seconds between looks), CI_WAIT (most seconds to wait for a run to finish),
# CI_GRACE (seconds to wait for a run to appear after a push), GH (the gh to run).
set -u
sha=${1:?usage: ci-wait.sh <sha>}
# the API matches full SHAs only; expand an abbreviation or a ref here, when this repo knows it
sha=$(git rev-parse -q --verify "$sha^{commit}" 2>/dev/null || echo "$sha")
repo=${CI_REPO:-jerrydboonstra/neckbeard} poll=${CI_POLL:-20} wait=${CI_WAIT:-1500} grace=${CI_GRACE:-90}
gh=${GH:-gh}
said=
SECONDS=0   # time spent here; a slow gh counts too
while :; do
  runs=$("$gh" api "repos/$repo/actions/runs?head_sha=$sha&per_page=50" \
         --jq '.workflow_runs[] | select(.name == "CI") | [.status, (.conclusion // ""), .html_url] | @tsv') ||
    { echo "ci: can't read CI runs for ${sha:0:7} from $repo (is gh signed in?)"; exit 1; }
  if grep -q $'^completed\tsuccess\t' <<<"$runs"; then
    echo "ok   CI passed on ${sha:0:7}: $(grep $'^completed\tsuccess\t' <<<"$runs" | head -1 | cut -f3)"
    exit 0
  fi
  waited=$SECONDS
  if [ -z "$runs" ]; then
    [ "$waited" -ge "$grace" ] && { echo "ci: no CI run for ${sha:0:7} on $repo; CI runs when main moves there, or by hand: gh workflow run CI --ref main"; exit 1; }
  elif ! grep -qv $'^completed\t' <<<"$runs"; then
    echo "ci: CI didn't pass on ${sha:0:7}:"
    cut -f2,3 <<<"$runs" | sed 's/^/     /'
    exit 1
  elif [ "$waited" -ge "$wait" ]; then
    echo "ci: CI on ${sha:0:7} still hasn't finished after ${wait}s: $(cut -f3 <<<"$runs" | head -1)"
    exit 1
  fi
  [ -n "$runs" ] && [ -z "$said" ] && { echo "ci: waiting for CI on ${sha:0:7}: $(cut -f3 <<<"$runs" | head -1)"; said=1; }
  sleep "$poll"
done
