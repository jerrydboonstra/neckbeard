#!/usr/bin/env bash
# guard: refuse a tree that holds a word from a private list. Run by `make release` (through `make guard`) before it pushes.
# Env: GUARD_WORDS, the list file (the Makefile passes PRIVATE_WORDS as it), one word per line; blank lines and lines
# starting with # are skipped. GUARD_REQUIRE_WORDS, when non-empty, makes a missing list a failure instead of a skip.
# Reads tracked text files only (git grep -I -n -w -F, from the repo top): a hit is a whole word, case counts, and a
# match touched by a letter, digit or underscore is not one. The list sits outside the repo, so it is never scanned.
# Prints file:line and the word's line in the list, never the word or the list's path: the output may reach a public log.
# Exit 0 clean, 1 a hit (or no list while GUARD_REQUIRE_WORDS is set), 2 an unreadable list or a failed search.
# Written for bash 3.2.
list=${GUARD_WORDS:-}
if [ -z "$list" ]; then
  echo "guard: GUARD_WORDS is not set, so no private-words check ran" >&2
  [ -n "${GUARD_REQUIRE_WORDS:-}" ] && exit 1
  exit 0
fi
if [ ! -f "$list" ] || ! exec 3<"$list"; then
  echo "guard: GUARD_WORDS: list unreadable" >&2
  exit 2
fi
top=$(git rev-parse --show-toplevel 2>/dev/null) && cd "$top" || { echo "guard: not in a git repository" >&2; exit 2; }
n=0
found=0
while IFS= read -r word <&3 || [ -n "$word" ]; do
  n=$((n + 1))
  case $word in '' | '#'*) continue ;; esac
  [ -z "${word//[[:space:]]/}" ] && continue
  out=$(git grep -I -n -w -F -e "$word" 2>/dev/null)
  rc=$?
  if [ $rc -eq 0 ]; then
    printf '%s\n' "$out" | cut -d: -f1,2 | sed "s/\$/ (list line $n)/"
    found=1
  elif [ $rc -ne 1 ]; then
    echo "guard: the search failed" >&2
    exit 2
  fi
done
if [ $found -eq 1 ]; then
  echo "guard: the tree holds a word from the private list" >&2
  exit 1
fi
exit 0
