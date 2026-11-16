#!/usr/bin/env python3
"""The hooks part of neckbeard's inventory: which hooks a plugin registers, the scripts they run and what those scripts
read in, the files outside the manifest that hold hook configuration, the settings writers, and the scan for code that
persists something. Moved out of inventory.py with no change in behaviour, one step toward every shipped file being
under neckbeard's own read cap. inventory.py imports each name from here, so `inventory.<name>` still resolves. Stdlib only.
"""
import json
import os
import re
import shlex

from hook_shell import trace_shell_hook
from inventory_core import (
    READ_LIMIT, _mark_scan, _note, _prune_skipped, _walk_error, _walk_gaps, _within, measure, read_json, read_text,
)


# Events whose hooks fire on the subagent lifecycle itself.
SUBAGENT_EVENTS = {"SubagentStart", "SubagentStop"}

# Claude Code's hooks documentation states that plugin hooks "also run inside
# subagents", and names PreToolUse and PostToolUse explicitly: when a subagent
# calls a tool, those fire exactly as in the main conversation. So a plugin
# hooking them reaches every subagent, even with no Subagent* event registered.
# Reported separately from the certain set below, because the general sentence
# implies others (Stop, PermissionRequest) without documenting them one by one,
# and guessing a confident list is the failure this tool exists to prevent.
SUBAGENT_TOOL_EVENTS = {"PreToolUse", "PostToolUse"}
SUBAGENT_TOOL_EVENTS_LIKELY = {"PostToolUseFailure", "Stop", "PermissionRequest"}
# Deliberately broad. Matches constructed writes as well as direct calls --
# shell append redirection, a copy into a home-directory cache, pathlib
# write_text, appendFileSync, createWriteStream -- because a persistence scan
# that only catches the obvious calls gives false confidence. Treat any match
# as a candidate to verify by hand, not a verdict. See CASE-STUDIES.md, round 9.
PERSIST_PATTERNS = [
    # node/js
    re.compile(r"\b(writeFileSync|appendFileSync|createWriteStream|copyFileSync|mkdirSync|rmSync)\b"),
    re.compile(r"fs\.(write|append|copy|rename|unlink|rm|mkdir)\w*\("),
    # python
    re.compile(r"\bopen\([^)]*['\"][wax]"),
    re.compile(r"\.(write_text|write_bytes|mkdir|touch|unlink|rename|replace)\("),
    re.compile(r"\b(shutil\.(copy|move|rmtree)|os\.(remove|rename|makedirs|mkdir))\b"),
    # shell
    re.compile(r">>?\s*[\"']?(\$HOME|~|/)"),
    re.compile(r"\b(cp|mv|rm|mkdir|touch|tee|install)\b[^\n|]*\$HOME"),
    re.compile(r"\b(cp|mv|tee)\b\s+-?\w*\s*[\"']?[^\n]*[\"']?\s+[\"']?(\$HOME|~)/"),
    # anywhere: names a home-ish destination
    re.compile(r"os\.homedir\(\)|homedir\(\)|expanduser\(|Path\.home\(\)|process\.env\.HOME"),
    re.compile(r"[\"'/]\.(config|cache|local|claude)[\"'/]"),
]

# Extensions alone missed superpowers' own hook, which is the extension-less
# file `hooks/session-start`. Scan anything small and text-shaped instead.
SCRIPT_EXTS = (".js", ".py", ".sh", ".mjs", ".cjs", ".ts", ".bash", ".zsh", ".rb", ".pl")


JS_REQUIRE_RE = re.compile(r"""require\(\s*['"](\.[^'"]+)['"]\s*\)""")
PATH_JOIN_RE = re.compile(r"""path\.join\(\s*([^)]+?)\s*\)""")


def _literal_path_candidates(src):
    """Ordered most-trustworthy first: a path.join(...) reconstruction is
    evidence the file is actually being built as a path, while a bare quoted
    string is not, and treating a bare literal as equally confident risks
    naming an unrelated file quoted nearby over the real payload, with no note
    telling the reader to doubt it. Handles single-literal paths
    ('../skills/x/SKILL.md') and path.join(...) calls whose arguments are all
    string literals or __dirname/__filename (ponytail's actual pattern:
    path.join(__dirname, '..', 'skills', 'ponytail', 'SKILL.md')),
    reconstructed as a plain relative path. Returns (candidate, confident)
    pairs."""
    joined, bare = [], list(re.findall(r"""['"]([\w./-]+\.(?:md|txt))['"]""", src))
    out = []
    for args_raw in PATH_JOIN_RE.findall(src):
        parts, ok = [], True
        for arg in [a.strip() for a in args_raw.split(",")]:
            if arg in ("__dirname", "__filename"):
                continue  # treated as "start here", handled by the caller's base dirs
            m = re.match(r"""^['"]([^'"]*)['"]$""", arg)
            if m:
                parts.append(m.group(1))
            else:
                ok = False
                break
        if ok and parts:
            joined.append("/".join(parts))
    # confident: reconstructed from a real path expression.
    out = [(c, True) for c in joined]
    # not confident: a bare quoted filename, which may be anything.
    out += [(c, False) for c in bare if c not in joined]
    return out


def resolve_injected_text(hook_file_path, plugin_root, depth=1, notes=None):
    """Best-effort: a hook script that reads a fixed SKILL.md-shaped file and
    injects it wholesale (ponytail's pattern: SessionStart hook requires a
    sibling module, which builds the path via path.join(__dirname, ..., 'SKILL.md'))
    names that file's path in its own source or one local require() away. Follows
    one hop of local requires, reconstructs literal + path.join(...) candidates,
    and resolves each against the hook's own directory and the plugin root.
    Anything genuinely dynamic (computed from runtime state) is reported as such."""
    src = read_text(hook_file_path, limit=20_000) or ""
    if len(src) >= 20_000 and _within(hook_file_path, plugin_root) and os.path.getsize(hook_file_path) > 20_000:
        _note(notes, f"{os.path.relpath(hook_file_path, plugin_root)}: read capped at 20000 bytes", cause="tool-limit")
    candidates = _literal_path_candidates(src)
    fallback = None
    for c, confident in candidates:
        for base in (os.path.dirname(hook_file_path), plugin_root):
            p = os.path.normpath(os.path.join(base, c))
            if os.path.isfile(p) and _within(p, plugin_root):
                text = read_text(p)
                if not text:
                    continue
                hit = {"resolved_file": os.path.relpath(p, plugin_root)}
                hit.update(measure(p, text))
                if confident:
                    return hit
                # A bare literal is a guess. Hold it, keep looking for a
                # reconstructed path, and label it if nothing better turns up.
                if fallback is None:
                    hit["confidence"] = "low"
                    hit["why"] = ("matched a bare quoted filename in the hook source, not a "
                                  "reconstructed path expression; verify by reading the hook")
                    fallback = hit
    if depth > 0:
        for rel in JS_REQUIRE_RE.findall(src):
            for cand in (rel, rel + ".js", rel + ".mjs", rel + ".cjs"):
                required = os.path.normpath(os.path.join(os.path.dirname(hook_file_path), cand))
                if os.path.isfile(required):
                    found = resolve_injected_text(required, plugin_root, depth=depth - 1, notes=notes)
                    if found:
                        return found
                    break
    return fallback


def _expand_plugin_root(s, plugin_root):
    """Replace every reference to CLAUDE_PLUGIN_ROOT in a hook command with the
    plugin root: $CLAUDE_PLUGIN_ROOT, ${CLAUDE_PLUGIN_ROOT}, and the shell's
    default forms ${CLAUDE_PLUGIN_ROOT:-word}, ${...-word}, ${...:=word},
    ${...=word}, ${...:?word} and ${...?word}, whose word may itself hold ${...}. Claude Code always sets the
    variable, so each of those forms is its value and the word never runs.
    Cat Herder writes "${CLAUDE_PLUGIN_ROOT:-${PLUGIN_ROOT}}/bin/meow" so one
    hook file serves several hosts; matching only the plain forms reported all
    three of its hooks as unidentifiable. ${...:+word} (word when set) is left
    alone: its value is the word, not the root. So is $CLAUDE_PLUGIN_ROOTX, a
    different variable (1.14.0 and earlier expanded it, by a substring replace). The scan
    does not read quotes, so a quoted } inside the word ends it early and the
    hook reads as unidentifiable: an unknown, never a false all-clear."""
    head = "${CLAUDE_PLUGIN_ROOT"
    out, i = [], 0
    while True:
        j = s.find(head, i)
        if j < 0:
            break
        k = j + len(head)
        rest = s[k:]
        op = next((o for o in (":-", ":=", ":?", "-", "=", "?") if rest.startswith(o)), None)
        if not rest.startswith("}") and op is None:
            out.append(s[i:k])
            i = k
            continue
        # Find the closing brace of this ${...}, counting nested ${ ... }.
        depth, m = 1, k
        while m < len(s) and depth:
            if s.startswith("${", m):
                depth, m = depth + 1, m + 2
                continue
            if s[m] == "}":
                depth -= 1
            m += 1
        if depth:
            break
        out.append(s[i:j] + plugin_root)
        i = m
    s = "".join(out) + s[i:]
    return re.sub(r"\$CLAUDE_PLUGIN_ROOT(?![A-Za-z0-9_])", lambda _: plugin_root, s)


def _identify_hook_script(cmd, plugin_root):
    """The file a hook command actually runs, or None if it cannot be worked out.

    Deliberately not gated on an extension list or on quoting. Expands the
    plugin-root variable (with its default forms), takes every
    whitespace-separated token, strips quotes, and returns the first that
    exists as a file inside the tree. Anything else is unidentifiable, which
    is a reportable state, not silence."""
    # Expand to a token with no whitespace first, so a default word with spaces
    # still splits as the shell would, and a plugin root with spaces in its path
    # is never split; the real root goes in per token.
    mark = "\0PLUGIN_ROOT\0"
    for tok in _expand_plugin_root(cmd, mark).split():
        t = tok.strip("\"'").replace(mark, plugin_root)
        if not t or t.startswith("-"):
            continue
        cands = [t] if os.path.isabs(t) else [
            os.path.join(plugin_root, t),
            os.path.join(plugin_root, "hooks", os.path.basename(t)),
        ]
        for c in cands:
            c = os.path.normpath(c)
            if os.path.isfile(c) and _within(c, plugin_root):
                return c
    return None


SHELL_SHEBANG_RE = re.compile(r"#!\s*(/bin/(ba)?sh|/usr/bin/env\s+(ba)?sh)\s*$")


def _command_is_script_alone(cmd, plugin_root):
    """True when the hook command is the script alone, optionally after bash or sh: nothing else runs, so the script's
    own text is all there is to read."""
    mark = "\0PLUGIN_ROOT\0"
    try:
        toks = shlex.split(_expand_plugin_root(cmd, mark))
    except ValueError:
        return False
    if toks and toks[0] in ("bash", "sh", "/bin/bash", "/bin/sh"):
        toks = toks[1:]
    return len(toks) == 1 and not re.search(r"[;&|<>`$()]", toks[0].replace(mark, ""))


def _shell_trace(script, cmd, plugin_root):
    """(trace, detail) for a shell hook script resolve_injected_text found no file in. trace is hook_shell's answer when
    every statement passed, else None; detail is what to add to the unresolved note (None when the script is not a shell
    script, so the note stays as it was)."""
    text = read_text(script, limit=20_000) or ""
    if not (script.endswith(".sh") or SHELL_SHEBANG_RE.match(text.split("\n", 1)[0].strip())):
        return None, None
    if not _command_is_script_alone(cmd, plugin_root):
        return None, "the hook command runs more than the script"
    if os.path.getsize(script) > 20_000:
        return None, "line 1: longer than the 20000-byte read cap, so not traced"
    r = trace_shell_hook(text)
    if "stop" in r:
        return None, f"line {r['stop'][0]}: {r['stop'][1]}"
    return r, None


def inventory_hooks(plugin_root, plugin_json, notes=None):
    hooks_ref = plugin_json.get("hooks")
    hooks_path = None
    # plugin.json may carry its hooks inline as an object rather than naming a
    # file. That shape must be handled before it reaches os.path.join, which
    # expects a path string, or the run crashes with no dossier at all. See
    # CASE-STUDIES.md, round 14.
    if isinstance(hooks_ref, dict) and hooks_ref:
        rel, hooks_json = "plugin.json (inline hooks)", hooks_ref
    elif isinstance(hooks_ref, list) and hooks_ref and all(isinstance(h, (str, dict)) for h in hooks_ref):
        # A list of hook files (or inline objects): Claude Code merges them, and so do we.
        return _merge_hook_list(plugin_root, hooks_ref, notes)
    elif hooks_ref and not isinstance(hooks_ref, (str, dict)):
        return {"has_hooks": "unknown", "hooks_file": "plugin.json", "events": {},
                "hook_scripts": None, "hook_registrations": None,
                "hooks_reach_subagents": None,
                "parse_error": f"plugin.json's \"hooks\" is a {type(hooks_ref).__name__}, "
                               "neither a path nor an object of events; read it by hand"}
    else:
        if hooks_ref:
            hooks_path = os.path.normpath(os.path.join(plugin_root, hooks_ref))
        else:
            default = os.path.join(plugin_root, "hooks", "hooks.json")
            if os.path.isfile(default):
                hooks_path = default
        if not hooks_path or not os.path.isfile(hooks_path):
            if hooks_ref:
                _note(notes, f"plugin.json: hooks path {hooks_ref} in plugin.json not found", "failed", cause="target-fault")
            # Not where Claude Code would load them from, which is not the same
            # as nowhere. See hooks_outside_manifest().
            return hooks_outside_manifest(plugin_root, notes=notes)
        rel = os.path.relpath(hooks_path, plugin_root)
        # plugin.json names this path, and plugin.json is untrusted: "../../x.json"
        # or a symlinked hooks/ can read a file from anywhere, no symlink
        # privileges needed for the traversal case. See CASE-STUDIES.md, round 14.
        if not _within(hooks_path, plugin_root):
            return {"has_hooks": "unknown", "hooks_file": rel, "events": {},
                    "hook_scripts": None, "hook_registrations": None,
                    "hooks_reach_subagents": None,
                    "refused": "hooks file resolves outside the target tree; not read"}
        hooks_json = read_json(hooks_path)

    # A hooks file that exists but cannot be read is NOT "no hooks", and it is
    # not "hooks with no events" either. Say what is actually known, which is
    # that there is a hooks file and it did not parse. See CASE-STUDIES.md,
    # round 8.
    if hooks_json is None:
        return {"has_hooks": "unknown", "hooks_file": rel, "events": {},
                "hook_scripts": None, "hook_registrations": None,
                "hooks_reach_subagents": None,
                "parse_error": "hooks file exists but is not valid JSON; read it by hand"}

    # Claude Code nests events under a "hooks" key; some plugins write them at
    # the top level. Anything else (a list, a string, a number) is neither, and
    # must be handled explicitly rather than assumed. See CASE-STUDIES.md,
    # round 8.
    events = hooks_json.get("hooks", hooks_json) if isinstance(hooks_json, dict) else None
    if not isinstance(events, dict):
        # Name the value that is actually wrong. Reporting type(hooks_json)
        # produced "parsed as dict, not an object of events" for {"hooks": []},
        # which contradicts itself.
        inner = hooks_json.get("hooks") if isinstance(hooks_json, dict) else hooks_json
        return {"has_hooks": "unknown", "hooks_file": rel, "events": {},
                "hook_scripts": None, "hook_registrations": None,
                "hooks_reach_subagents": None,
                "parse_error": f"events container is {type(inner).__name__}, "
                               "expected an object of event names; read it by hand"}

    return _parse_events(events, rel, plugin_root, notes)


def _merge_hook_list(plugin_root, refs, notes=None):
    """plugin.json's "hooks" as a list: each entry is a path to a hooks file or an inline
    object of events. Every path passes the same containment and parse checks as a single
    file, and a bad entry makes the whole answer "unknown" rather than a quiet partial."""
    merged, names = {}, []
    for ref in refs:
        if isinstance(ref, dict):
            name, hooks_json = "plugin.json (inline hooks)", ref
        else:
            path = os.path.normpath(os.path.join(plugin_root, ref))
            name = os.path.relpath(path, plugin_root)
            if not _within(path, plugin_root):
                return {"has_hooks": "unknown", "hooks_file": name, "events": {},
                        "hook_scripts": None, "hook_registrations": None,
                        "hooks_reach_subagents": None,
                        "refused": "hooks file resolves outside the target tree; not read"}
            hooks_json = read_json(path) if os.path.isfile(path) else None
            if hooks_json is None:
                return {"has_hooks": "unknown", "hooks_file": name, "events": {},
                        "hook_scripts": None, "hook_registrations": None,
                        "hooks_reach_subagents": None,
                        "parse_error": "hooks file is missing or not valid JSON; read it by hand"}
        events = hooks_json.get("hooks", hooks_json) if isinstance(hooks_json, dict) else None
        if not isinstance(events, dict):
            return {"has_hooks": "unknown", "hooks_file": name, "events": {},
                    "hook_scripts": None, "hook_registrations": None,
                    "hooks_reach_subagents": None,
                    "parse_error": "hooks entry is not an object of event names; read it by hand"}
        names.append(name)
        for event, groups in events.items():
            merged.setdefault(event, [])
            if isinstance(groups, list):
                merged[event].extend(groups)
            else:
                merged[event] = groups  # malformed: _parse_events reports it
    return _parse_events(merged, ", ".join(names), plugin_root, notes)


def _parse_events(events, rel, plugin_root, notes=None):
    """Everything known about one object of hook events: what each registers, what
    it injects where that can be traced, and whether any of it reaches subagents."""
    result = {"has_hooks": True, "hooks_file": rel, "events": {}}
    reaches_subagents = False
    reaches_subagents_likely = False
    injected_seen = {}
    built_seen = {}   # script path -> {"trace": hook_shell's answer, "events": [...]}
    scripts_seen = set()
    resolved_scripts = set()
    unresolved_scripts = set()
    unidentifiable = set()
    malformed = []
    for event, entries in (events.items() if isinstance(events, dict) else []):
        cmds = []
        # An event's value should be a list of groups, each a dict with a
        # "hooks" list of dicts. Every one of those three levels needs checking
        # explicitly; each malformed shape below is reported, not assumed away.
        if not isinstance(entries, list):
            malformed.append(f"{event}: value is {type(entries).__name__}, expected a list")
            result["events"][event] = []
            continue
        for group in entries:
            if not isinstance(group, dict):
                malformed.append(f"{event}: group is {type(group).__name__}, expected an object")
                continue
            inner = group.get("hooks", [])
            if not isinstance(inner, list):
                malformed.append(f"{event}: inner hooks is {type(inner).__name__}, expected a list")
                continue
            for h in inner:
                if not isinstance(h, dict):
                    malformed.append(f"{event}: hook entry is {type(h).__name__}, expected an object")
                    continue
                cmd = h.get("command", "")
                if not isinstance(cmd, str):
                    _note(notes, f"{rel}: {event}: hook command is {type(cmd).__name__}, expected a string; "
                                 "this hook was not read", "failed", cause="target-fault")
                    continue
                cmds.append({"matcher": group.get("matcher"), "command": cmd})
                base = cmd.rstrip('"').split("/")[-1].strip('"')
                if base:
                    scripts_seen.add(base)
                # Three outcomes, not two. A hook whose script cannot even be
                # IDENTIFIED is a larger unknown than one that was identified
                # and whose payload could not be traced, and ranking it below
                # "nothing to inject" by saying nothing turns an unknown into a
                # false all-clear. An extension allowlist is not enough to
                # identify a script: obra/superpowers runs its hook via
                #   "${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd" session-start
                # a wrapper with no recognizable script extension, and would
                # otherwise report silence while injecting content every
                # session. Identify first, resolve second, and never let a
                # failure to identify pass as an all-clear. See
                # CASE-STUDIES.md, round 12.
                script = _identify_hook_script(cmd, plugin_root)
                if script is None:
                    unidentifiable.add(f"{event}: {cmd.strip()[:90]}")
                else:
                    inj = resolve_injected_text(script, plugin_root, notes=notes)
                    if inj:
                        injected_seen[inj["resolved_file"]] = inj.get("bytes") or inj.get("chars") or 0
                        resolved_scripts.add(os.path.basename(script))
                    else:
                        tr, detail = _shell_trace(script, cmd, plugin_root)
                        rel_script = os.path.relpath(script, plugin_root)
                        if tr is not None:
                            built = built_seen.setdefault(rel_script, {"trace": tr, "events": []})
                            if event not in built["events"]:
                                built["events"].append(event)
                            resolved_scripts.add(os.path.basename(script))
                        else:
                            unresolved_scripts.add(f"{event}: {rel_script}" + (f" ({detail})" if detail else ""))
        if event in SUBAGENT_EVENTS or event in SUBAGENT_TOOL_EVENTS:
            reaches_subagents = True
        if event in SUBAGENT_TOOL_EVENTS_LIKELY:
            reaches_subagents_likely = True
        result["events"][event] = cmds
    result["hooks_reach_subagents"] = reaches_subagents
    result["hooks_reach_subagents_basis"] = (
        "documented: a Subagent* event, or PreToolUse/PostToolUse which the docs "
        "say fire inside subagents" if reaches_subagents
        else "likely but not individually documented; read the events list"
        if reaches_subagents_likely else "no event known to fire in a subagent")
    # Report both counts. A plugin's own docs usually count distinct scripts,
    # while the registration count is higher whenever one script is wired to
    # more than one event. Reporting only the latter can read as drift against
    # a correct doc. See CHANGELOG.md 1.1.0.
    result["hook_registrations"] = sum(len(v) for v in result["events"].values())
    result["hook_scripts"] = len(scripts_seen)
    entries = [{"file": f, "bytes": b} for f, b in injected_seen.items()]
    total = sum(injected_seen.values())
    for f, built in built_seen.items():
        tr = built["trace"]
        if tr["template"] or tr["writes"]:
            entries.append({"file": f, "bytes": tr["bytes"], "events": built["events"], "built_at_run_time": True,
                            "template": tr["template"], "writes": tr["writes"], "at_least": tr["at_least"]})
            total += tr["bytes"]
    result["injected_content"] = entries or None
    result["injected_bytes_total_estimate"] = total or None
    if malformed:
        result["malformed_entries"] = malformed
        result["has_hooks"] = "partial"
    # Report unresolved hooks per script, not only when the whole set failed:
    # one hook that resolves must not silence the warning for one that does
    # not, or an unresolved PreToolUse gate looks exactly like a hook with
    # nothing to inject. See CASE-STUDIES.md, round 11.
    if unresolved_scripts:
        result["unresolved_hooks"] = sorted(unresolved_scripts)
    if unidentifiable:
        result["unidentifiable_hooks"] = sorted(unidentifiable)
    unknown = len(unresolved_scripts) + len(unidentifiable)
    if unknown:
        parts = []
        if unresolved_scripts:
            parts.append(f"{len(unresolved_scripts)} whose script was found but whose "
                         "payload could not be traced")
        if unidentifiable:
            parts.append(f"{len(unidentifiable)} whose script could not even be identified "
                         "from the command")
        result["injected_content_note"] = (
            f"{unknown} hook(s) have unknown behaviour, which is not the same as none: "
            + "; ".join(parts) + ". Read them by hand.")
    return result


# Claude Code's hook event names. A JSON object keyed by at least one of these, each
# a list, is hook configuration wherever it sits in the tree.
HOOK_EVENTS = {"PreToolUse", "PostToolUse", "PostToolUseFailure", "UserPromptSubmit",
               "Notification", "Stop", "SubagentStart", "SubagentStop", "SessionStart",
               "SessionEnd", "PreCompact", "PermissionRequest"}
# Manifests and package metadata: read elsewhere or never hook configuration.
NOT_HOOK_CONFIG = {"plugin.json", "marketplace.json", "package.json", "package-lock.json",
                   "tsconfig.json"}


def _hook_events_in(obj):
    if not isinstance(obj, dict):
        return None
    events = obj["hooks"] if isinstance(obj.get("hooks"), dict) else obj
    known = {k: v for k, v in events.items() if k in HOOK_EVENTS}
    if known and all(isinstance(v, list) for v in known.values()):
        return known
    return None


def settings_writers(root):
    """Scripts that write files and name a settings.json: the likely installers."""
    return [rel for rel in inventory_persistence(root)
            if re.search(r"settings(\.local)?\.json",
                         read_text(os.path.join(root, rel), limit=50_000) or "")]


def hooks_outside_manifest(root, max_reads=20_000, notes=None):
    """Hook configuration that no manifest names, which is not the same as none.

    A plugin can ship with no manifest at all and an installer that merges the
    "hooks" block of its install.json into ~/.claude/settings.json. Checking
    only a manifest and hooks/hooks.json reported ten hook groups, SubagentStart
    among them, as none. So search the tree for JSON shaped like hook
    configuration, and when it turns up, report it as hooks with a note saying
    how they get installed. A false alarm here costs the reader a look at one
    file; a miss costs them every session. See CHANGELOG.md 1.12.6.

    No depth limit: 1.12.6 stopped four levels down and returned a bare false
    for hooks below that (1.12.7). What bounds the walk instead is how many JSON
    files it reads, and running out is said, never silent. The largest of
    128 local trees measured read 5,378 JSON files in about 3 seconds."""
    root = root.rstrip("/")
    found, events, reads, stopped_at = [], {}, 0, None
    first_note = len(notes) if notes is not None else 0
    for dirpath, dirnames, filenames in os.walk(root, onerror=_walk_error(notes, root)):
        if stopped_at:
            break
        dirnames[:] = sorted(d for d in dirnames if d not in (".git", "node_modules", "__pycache__", "vendor"))
        _prune_skipped(dirpath, dirnames)
        _walk_gaps(notes, dirpath, dirnames, root)
        for fn in sorted(filenames):
            if not fn.endswith(".json") or fn in NOT_HOOK_CONFIG:
                continue
            fp = os.path.join(dirpath, fn)
            rel_fp = os.path.relpath(fp, root)
            try:
                if not _within(fp, root):
                    _note(notes, f"{rel_fp}: resolves outside the target tree; not searched for hooks", cause="tool-limit")
                    continue
                if os.path.getsize(fp) > READ_LIMIT:
                    _note(notes, f"{rel_fp}: over {READ_LIMIT} bytes; not searched for hooks", cause="tool-limit")
                    continue
            except OSError:
                _note(notes, f"{rel_fp}: could not be read; not searched for hooks", cause="tool-limit")
                continue
            if reads >= max_reads:
                stopped_at = os.path.relpath(dirpath, root)
                break
            reads += 1
            data = read_json(fp)
            if data is None:
                _note(notes, f"{rel_fp}: not valid JSON; not searched for hooks", cause="target-fault")
            got = _hook_events_in(data)
            if got:
                found.append(os.path.relpath(fp, root))
                for event, groups in got.items():
                    events.setdefault(event, []).extend(groups)
    _mark_scan(notes, first_note)   # the walk's own notes only: what _parse_events adds below counts as it always did
    # A search cut short says so whatever it found: before it stopped, nothing
    # means unknown, and something means those hooks and maybe more.
    incomplete = (f"The search for hook-shaped JSON stopped after {max_reads} files, at "
                  f"{stopped_at}/, before reading the whole tree, so hooks past that "
                  "point were not looked for. Look for a hooks block by hand, or "
                  "inventory the plugin's own directory.") if stopped_at else None
    if not found and stopped_at:
        return {"has_hooks": "unknown", "events": {}, "hook_scripts": None,
                "hook_registrations": None, "hooks_reach_subagents": None,
                "search_incomplete": incomplete}
    if not found:
        return {"has_hooks": False}
    # A folder of plugins (no marketplace manifest, each plugin in its own
    # directory) turns up each plugin's own hooks/hooks.json here. Those are not
    # an installer's hooks, and merging several plugins' into one list describes
    # an install that never happens, so say unknown and name the plugins.
    nested = sorted({os.path.relpath(os.path.dirname(os.path.dirname(os.path.join(root, f))), root)
                     for f in found
                     if os.path.basename(os.path.dirname(os.path.join(root, f))) == "hooks"
                     and os.path.isfile(os.path.join(os.path.dirname(os.path.dirname(
                         os.path.join(root, f))), ".claude-plugin", "plugin.json"))})
    if nested and all(any(f.startswith(n + os.sep) for n in nested) for f in found):
        return {"has_hooks": "unknown", "events": {}, "hook_scripts": None,
                "hook_registrations": None, "hooks_reach_subagents": None,
                "nested_plugins": nested,
                "nested_note": (f"Hooks found inside {len(nested)} plugin(s) nested in this "
                                f"directory ({', '.join(nested)}). Inventory each plugin "
                                "directory on its own; this directory is not one plugin."),
                **({"search_incomplete": incomplete} if incomplete else {})}
    result = _parse_events(events, ", ".join(found), root, notes)
    result["hooks_source"] = "outside-manifest"
    if incomplete:
        result["search_incomplete"] = incomplete
    writers = settings_writers(root)
    if writers:
        result["settings_writers"] = writers
    result["hooks_note"] = (
        "No manifest names these, so Claude Code does not load them from this directory. "
        "They take effect when an installer script, or the README's instructions, merge "
        "them into a settings.json, and then they run in every session that file covers, "
        "not only this tool's. Check which file the install step uses.")
    return result


def inventory_persistence(plugin_root, notes=None):
    first_note = len(notes) if notes is not None else 0
    try:
        return _persistence_walk(plugin_root, notes)
    finally:
        _mark_scan(notes, first_note)


def _persistence_walk(plugin_root, notes):
    hits = []
    for dirpath, dirnames, filenames in os.walk(plugin_root, onerror=_walk_error(notes, plugin_root)):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", "__pycache__", "vendor", "benchmarks", "tests", "test")]
        _walk_gaps(notes, dirpath, dirnames, plugin_root)
        for fn in filenames:
            fp = os.path.join(dirpath, fn)
            rel_fp = os.path.relpath(fp, plugin_root)
            if not _within(fp, plugin_root):
                _note(notes, f"{rel_fp}: resolves outside the target tree; not scanned", cause="tool-limit")
                continue
            if not fn.endswith(SCRIPT_EXTS):
                # Keep extension-less files (hooks/session-start and friends),
                # skip obvious non-scripts and anything large.
                if "." in fn or fn.startswith("."):
                    continue
                try:
                    if os.path.getsize(fp) > 200_000:
                        _note(notes, f"{rel_fp}: over 200000 bytes; not scanned", cause="tool-limit")
                        continue
                except OSError:
                    _note(notes, f"{rel_fp}: could not be read; not scanned", cause="tool-limit")
                    continue
            text = read_text(fp, limit=50_000)
            if text is None:
                _note(notes, f"{rel_fp}: could not be read; not scanned", cause="tool-limit")
                text = ""
            elif len(text) >= 50_000 and os.path.getsize(fp) > 50_000:
                _note(notes, f"{rel_fp}: read capped at 50000 bytes", cause="tool-limit")
            for pat in PERSIST_PATTERNS:
                if pat.search(text):
                    hits.append(os.path.relpath(fp, plugin_root))
                    break
    return sorted(set(hits))
