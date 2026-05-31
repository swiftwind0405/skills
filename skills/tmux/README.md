# tmux

用于将 `tmux` 作为持久命令运行器的 Codex skill。

当 Agent 需要运行或检查长期 shell 工作时使用此技能，例如开发服务器、watcher、构建任务、日志、交互式 CLI 或共享协作 pane。

## 内容

- `SKILL.md`：面向 Codex 的工作流说明。
- `scripts/tmux-send-and-capture`：用于向 tmux pane 发送文本并捕获近期输出的辅助工具。
- `agents/openai.yaml`：该技能的 UI 元数据。

## 辅助工具

向 tmux pane 发送消息或命令，并捕获近期输出：

```bash
scripts/tmux-send-and-capture -t "project-shared:coordination.0" -n 80 "status please"
```

向繁忙的 Codex pane 排队发送文本：

```bash
scripts/tmux-send-and-capture -t "project-agent:main.0" --codex-queue "queue this after the current task"
```
