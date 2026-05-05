# Project Dev Guide Skill

本地项目编码开发指引：先把项目别名解析到本机真实仓库绝对路径，再继续后续开发动作。

## Environment Variables

| Variable               | Required | Description                                              |
| ---------------------- | -------- | -------------------------------------------------------- |
| `PROJECT_PATH_ALIASES` | No       | Path to a JSON file mapping project aliases → repo paths |

### Path Aliases File Format

`PROJECT_PATH_ALIASES` 指向的 JSON 文件推荐结构：

```json
{
  "backend_root": "/absolute/path/to/backend",
  "frontend_monorepo_name": "web-monorepo",
  "frontend_monorepo_root": "/absolute/path/to/frontend",
  "ai_root": "/absolute/path/to/ai",
  "defaults": {
    "backend": "/absolute/path/to/backend",
    "frontend": "/absolute/path/to/frontend",
    "ai": "/absolute/path/to/ai",
    "ats": "/absolute/path/to/backend/ats"
  },
  "entries": [
    {
      "aliases": ["admin", "pc", "后台管理"],
      "path": "/absolute/path/to/frontend/apps/admin",
      "stack": "React 前端"
    }
  ]
}
```

### Example

```bash
export PROJECT_PATH_ALIASES="$HOME/.config/project-dev-guide/path-aliases.json"
```

如果未设置此环境变量，skill 会通过本机搜索（`find`）兜底定位仓库。
