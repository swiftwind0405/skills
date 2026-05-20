# tmux

A Codex skill for using `tmux` as a durable command runner.

Use this skill when an agent needs to run or inspect long-lived shell work such
as dev servers, watchers, build jobs, logs, interactive CLIs, or shared
coordination panes.

## Contents

- `SKILL.md`: Codex-facing workflow instructions.
- `scripts/tmux-send-and-capture`: Helper for sending text to a tmux pane and
  capturing recent output.
- `agents/openai.yaml`: UI metadata for the skill.

## Helper

Send a message or command to a tmux pane and capture recent output:

```bash
scripts/tmux-send-and-capture -t "project-shared:coordination.0" -n 80 "status please"
```

Queue text into a busy Codex pane:

```bash
scripts/tmux-send-and-capture -t "project-agent:main.0" --codex-queue "queue this after the current task"
```
