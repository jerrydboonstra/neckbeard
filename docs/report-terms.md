# Terms in a neckbeard report

What the words in the [README](../README.md) and in a neckbeard report mean.

- **Hook:** a script Claude Code runs on its own at an event, such as the start of a session.
- **Subagent:** a helper session that Claude starts for one job.
- **Facts report:** neckbeard's list of the hooks a plugin has, the text it injects, the sessions and subagents it reaches, and the files it may write outside your project. It says which parts it could not read. It needs none of your rules.
- **Fit report:** neckbeard's comparison of each rule the plugin carries with the rules you already run. It says which of the plugin's rules duplicate one of yours, which contradict one, and which are new. It needs your own rules.
- **Injects:** the text a plugin adds to the model's context.
- **Hook-injected text:** the text a plugin's hooks add.
- **Persistence candidates:** scripts that might write files outside your project. In neckbeard's own report these are the skill's own scripts, which write only the report you name and temporary folders, as [SECURITY.md](../SECURITY.md) says, and the repo's build, deploy, test and measurement tools.
- **MCP servers:** programs a plugin can start to give Claude extra tools. [live-mcp.md](live-mcp.md) says how neckbeard can start one, and what it records.

A fit verdict needs the rules you already run, so a facts report gives none. Point neckbeard at your own rules with `--reader DIR` (a folder of rules standing in for yours), or ask Claude to "vet this plugin" with the skill installed.
