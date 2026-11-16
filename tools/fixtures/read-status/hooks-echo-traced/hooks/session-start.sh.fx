#!/usr/bin/env bash
# session-start.sh: runs `doctor.sh --quick` once per installed imagegen version. Prints nothing when every check passes;
# otherwise one line for Claude to read. A marker ~/.cache/imagegen/doctor-<version> is written only when the required
# checks pass, so a version that fails reports again at the next session start. Never installs, never calls codex,
# always exits 0, and ends within 2 seconds (the Pillow import gets 1).
root=${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." 2>/dev/null && pwd)}
{
  version=$(sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$root/.claude-plugin/plugin.json" 2>/dev/null | head -n 1)
  [ -n "$version" ] || exit 0
  marker=${HOME:-/nonexistent}/.cache/imagegen/doctor-$version
  [ ! -e "$marker" ] || exit 0
  out=$(IMAGEGEN_DOCTOR_PY_TIMEOUT=1 bash "$root/skills/imagegen/doctor.sh" --quick 2>/dev/null); rc=$?
  failed=$(printf '%s\n' "$out" | sed -n -e 's/^FAIL  *\([a-z]*\):.*/\1/p' -e 's/^warn  *\([a-z]*\):.*/\1 (recommended)/p' | tr '\n' ',' | sed 's/,$//; s/,/, /g')
  [ "$rc" != 0 ] || { mkdir -p "$(dirname "$marker")" && : > "$marker"; }
  [ -z "$failed" ] || echo "imagegen doctor: $failed missing; run skills/imagegen/doctor.sh for fixes"
} 2>/dev/null
exit 0
