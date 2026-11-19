# `--live-mcp`: starting one MCP server to list what it offers

`tools/neckbeard <target> --live-mcp NAME` is a separate, explicit trust decision. The static default never starts anything. Back to the [README](../README.md).

- **What an MCP server is:** a program a plugin can start to give Claude extra tools. A **stdio** server talks to Claude over standard input and output.
- **What it does:** for one local stdio server declared by the target, neckbeard starts its target-owned entrypoint, initializes MCP, and lists the advertised tools, resources, resource templates, and prompts.
- **What it records:** metadata and schemas only. It never calls a tool, reads a resource, expands a prompt, opens a browser, or performs a login.
- **What it refuses:** remote servers, shell snippets, package runners, missing or outside-tree entrypoints, unbounded output, and hung servers fail closed.
- **Secrets:** declared environment values are passed only to that isolated process and are redacted from the dossier, even if the server echoes one back. A value of four characters or more is redacted wherever it appears; a shorter one only where a whole string equals it.
- **The risk:** live inventory executes target code under your user account. The temporary home reduces accidental access but is not a sandbox, so read the static report first.
