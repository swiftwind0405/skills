---
name: tmux
description: Use tmux to run long-lived, interactive, parallel, or shared shell commands from Codex. Use when Codex needs to create named tmux sessions, run commands that should survive tool timeouts, monitor logs or dev servers, coordinate shared project sessions across threads, or create dedicated sessions for individual agent/thread ownership.
---

# Tmux

## Overview

Use tmux as the durable command runner for work that should keep running after a single shell call returns. Prefer tmux for dev servers, watchers, interactive CLIs, long builds, log tails, and commands shared across multiple Codex threads.

## Session Model

Use two session types:

- **Shared sessions**: Project-level sessions used by multiple threads for common services, logs, or coordination. Use a stable name such as `project-shared`, `<repo>-shared`, or `<app>-shared`.
- **Dedicated sessions**: Thread-owned sessions used by one agent/thread. Use a unique name such as `<repo>-<role>-<thread-short>` or `<repo>-codex-<purpose>`.

Keep names lowercase and shell-friendly: letters, digits, hyphens, and underscores only.

## Create A Named Session

Create a detached named session in the current directory:

```bash
SESSION="project-codex-build"
tmux has-session -t "$SESSION" 2>/dev/null || tmux new-session -d -s "$SESSION" -c "$PWD" -n main
```

Create a detached named session in a specific directory:

```bash
SESSION="project-shared"
WORKDIR="/path/to/project"
tmux has-session -t "$SESSION" 2>/dev/null || tmux new-session -d -s "$SESSION" -c "$WORKDIR" -n main
```

Create a session and immediately run a command:

```bash
SESSION="project-dev-server"
WORKDIR="/path/to/project"
tmux new-session -d -s "$SESSION" -c "$WORKDIR" -n server 'bash -lc "npm run dev; exec bash -l"'
```

Use `exec bash -l` or `exec zsh -l` at the end when you want the pane to remain open after the command exits.

## Run Commands In A Session

Send a command to an existing session/window/pane:

```bash
tmux send-keys -t "project-codex-build:main.0" 'cargo test' C-m
```

For Codex-to-Codex or pane-to-pane handoffs, use the bundled helper to send
text, send `C-m` as a separate `tmux send-keys` command, and immediately return
the last N lines from the target pane:

```bash
scripts/tmux-send-and-capture -t "project-codex-build:main.0" -n 80 "status please"
```

When the target is a Codex live session, prefer `--codex-queue`. It sends `C-m`
twice as separate commands, with a short delay between them, so Codex submits or
queues the message reliably after the current task:

```bash
scripts/tmux-send-and-capture -t "project-agent:main.0" --codex-queue -n 80 "queue this after the current task"
```

Use `--stdin` for multi-line messages:

```bash
printf '%s\n' "Please summarize current state." "Then wait for my next instruction." \
	| scripts/tmux-send-and-capture -t "project-codex-build:main.0" --stdin -n 120
```

Create a new window for a command:

```bash
tmux new-window -t "project-codex-build:" -n tests -c "$PWD" 'bash -lc "cargo test; exec bash -l"'
```

For complex commands, prefer writing a temporary script under the project temp directory and running the script. This avoids fragile nested quoting:

```bash
SCRIPT="/path/to/project/Temp/run-tests.sh"
chmod +x "$SCRIPT"
tmux new-window -t "project-codex-build:" -n tests -c "$PWD" "bash -lc '$SCRIPT; exec bash -l'"
```

Do not use tmux to hide failures. Always capture output or inspect the pane before reporting completion.

## Monitor And Inspect

List sessions, windows, and panes:

```bash
tmux list-sessions
tmux list-windows -t "project-codex-build"
tmux list-panes -a -F '#{session_name}:#{window_name}.#{pane_index} #{pane_current_command} #{pane_current_path}'
```

Capture recent pane output:

```bash
tmux capture-pane -pt "project-codex-build:tests.0" -S -200
```

Watch a pane without attaching:

```bash
tmux capture-pane -pt "project-codex-build:tests.0" -S -80
```

Attach only when interactive control is required:

```bash
tmux attach-session -t "project-codex-build"
```

Detach from an attached session with `Ctrl-b d`.

## Shared Sessions

Use shared sessions for project-wide processes that multiple threads may rely on, such as app servers, watchers, log tails, or coordination shells.

Rules:

- Use a stable project-level name, for example `project-shared`.
- Create separate windows for distinct concerns: `server`, `logs`, `tests`, `coordination`.
- Before modifying or killing a shared pane, inspect it with `capture-pane` and `list-panes`.
- Do not interrupt or kill a shared command unless the user asked for it or it is clearly owned by the current task.
- If a command is likely to affect other agents, create a new window instead of reusing an existing pane.
- Leave a visible shell prompt or final status in the pane when finished.

Typical shared session setup:

```bash
SESSION="project-shared"
WORKDIR="/path/to/project"

tmux has-session -t "$SESSION" 2>/dev/null || tmux new-session -d -s "$SESSION" -c "$WORKDIR" -n coordination
tmux new-window -t "$SESSION:" -n logs -c "$WORKDIR"
tmux new-window -t "$SESSION:" -n server -c "$WORKDIR"
```

## Dedicated Sessions

Use dedicated sessions for commands owned by one Codex thread. This is the default for risky, noisy, experimental, or task-specific work.

Rules:

- Include the project name and a unique thread/purpose suffix, for example `project-codex-tests` or `project-codex-build`.
- Keep all windows in the session related to the same task.
- It is acceptable to stop, restart, or kill commands in your own dedicated session.
- Capture final output before reporting success or failure.
- Kill the session when it is no longer useful unless the user asked to keep it running.

Typical dedicated session setup:

```bash
SESSION="project-codex-test"
WORKDIR="/path/to/project"

tmux has-session -t "$SESSION" 2>/dev/null || tmux new-session -d -s "$SESSION" -c "$WORKDIR" -n main
tmux new-window -t "$SESSION:" -n tests -c "$WORKDIR" 'bash -lc "npm test; exec bash -l"'
tmux capture-pane -pt "$SESSION:tests.0" -S -200
```

## Cleanup

Stop a specific pane command with `Ctrl-c`:

```bash
tmux send-keys -t "project-codex-build:tests.0" C-c
```

Kill a dedicated session:

```bash
tmux kill-session -t "project-codex-build"
```

Avoid killing shared sessions by default. If cleanup is required, kill only the specific window or pane you own:

```bash
tmux kill-window -t "project-shared:logs"
tmux kill-pane -t "project-shared:server.1"
```

## Reporting

When reporting tmux work, include:

- Session name.
- Window or pane target.
- Command started or inspected.
- Current status and key output.
- Whether the process is still running.
