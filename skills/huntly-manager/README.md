# huntly-manager

以混合模式使用 Huntly：读取操作通过 MCP 完成，保存内容和管理收藏/分组通过 REST API 脚本完成。

## 配置

| 变量                 | 必填 | 说明                                                        |
| -------------------- | ---- | ----------------------------------------------------------- |
| `HUNTLY_BASE_URL`    | 是   | 基础 URL，例如 `https://huntly.example.com`                 |
| `HUNTLY_TOKEN`       | 是\* | 用于 REST 写入 API 的普通 Huntly 登录 JWT（不是 MCP token） |
| `HUNTLY_USERNAME`    | 是\* | 用户名（可替代 token；脚本会登录并获取 JWT）                |
| `HUNTLY_PASSWORD`    | 是\* | 密码（可替代 token）                                        |
| `HUNTLY_SQLITE_PATH` | 否   | SQLite 数据库路径，用于直接只读访问                         |

\* 必须提供 `HUNTLY_TOKEN`，或同时提供 `HUNTLY_USERNAME` + `HUNTLY_PASSWORD`。

## 内置资源

- `references/`：API 文档
- `scripts/`：`huntly_save_content.py`、`huntly_collections.py`
