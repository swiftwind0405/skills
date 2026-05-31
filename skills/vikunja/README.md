# vikunja

通过 REST API 与 Vikunja 任务管理实例交互。使用安全更新模式管理任务、项目、标签、负责人和提醒。

## 配置

| 变量                  | 必填 | 说明                                         |
| --------------------- | ---- | -------------------------------------------- |
| `VIKUNJA_BASE_URL`    | 是   | 基础 URL，例如 `https://vikunja.example.com` |
| `VIKUNJA_API_TOKEN`   | 是   | 从 Settings → API Tokens 获取的 API token    |
| `VIKUNJA_SQLITE_PATH` | 否   | SQLite 数据库路径，用于直接只读访问          |

## 内置资源

- `references/`：Vikunja API 文档
