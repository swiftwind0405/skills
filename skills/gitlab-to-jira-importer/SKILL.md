---
name: gitlab-to-jira-importer
description: 将 GitLab issues 批量导入到 Jira DEV 项目，自动设置 components 为 AI
version: 1.0.0
author: hermes
---

# GitLab to Jira Issues Importer

将 GitLab (gitee.52emp.com) 的 issues 批量导入到 Jira DEV 项目，自动设置 components 为 "2.0" (AI)。

## 功能

- 从 GitLab API 自动获取 issues
- 支持从 JSON/CSV 文件导入
- 自动设置 Jira issue 的 components 为 AI ("2.0")
- 自动添加到下一个 Sprint
- 自动分配给当前用户
- 支持试运行模式 (dry-run)

## 使用方法

### 方式 1: 使用 GitLab Token 自动获取

```bash
python3 ~/.hermes/skills/gitlab-to-jira-importer/scripts/import-gitlab-issues.py \
  --gitlab-token <your-gitlab-token>
```

### 方式 2: 从 JSON 文件导入

如果无法直接访问 GitLab，可以手动导出 issues 到 JSON 文件：

```bash
# 文件格式示例: issues.json
[
  {
    "title": "【Aida Agent】Checkpoint 断点恢复",
    "description": "详细描述...",
    "state": "opened",
    "labels": ["P1", "backend"],
    "web_url": "https://gitee.52emp.com/caidao-web-project/aida/-/issues/16"
  },
  ...
]

python3 ~/.hermes/skills/gitlab-to-jira-importer/scripts/import-gitlab-issues.py \
  --from-file issues.json
```

### 方式 3: 从 CSV 文件导入

```bash
# CSV 格式: title,description,state,labels
title,description,state,labels
"【Aida Agent】Checkpoint 断点恢复","详细描述...","opened","P1,backend"

python3 ~/.hermes/skills/gitlab-to-jira-importer/scripts/import-gitlab-issues.py \
  --from-csv issues.csv
```

## 参数说明

| 参数 | 说明 |
|------|------|
| `--gitlab-token` | GitLab API Token |
| `--from-file` | 从 JSON 文件导入 |
| `--from-csv` | 从 CSV 文件导入 |
| `--dry-run` | 试运行，不实际创建 |
| `--skip-sprint` | 跳过添加到 Sprint |

## 配置

脚本中的默认配置：

```python
GITLAB_URL = "https://gitee.52emp.com"
PROJECT_PATH = "caidao-web-project/aida"
JIRA_URL = "http://jira.caidaocloud.com:8080"
JIRA_PROJECT = "DEV"
JIRA_COMPONENT_ID = "10805"  # "2.0" 组件 (AI)
JIRA_BOARD_ID = "45"
```

## 依赖

- Python 3.7+
- jira-cli 已配置 (`jira me` 可正常工作)
- GitLab API Token (如果需要从 API 获取)

## 工作流程

1. 获取 Jira 认证信息（从 macOS Keychain）
2. 获取 GitLab issues（通过 API 或文件）
3. 获取下一个 Sprint ID
4. 为每个 issue 创建 Jira issue：
   - 标题：GitLab issue 标题
   - 描述：GitLab issue 描述 + 原始链接
   - Issue Type: 故事
   - Priority: 根据 GitLab labels (P0/P1/P2) 自动映射
   - Components: "2.0" (AI)
5. 添加到 Sprint
6. 分配给当前用户

## 示例输出

```
🔐 获取 Jira 认证信息...
✅ Jira 用户: stanley.yang
📥 从 GitLab API 获取 issues...
📋 找到 26 个 issues
📅 目标 Sprint ID: 1234

⚠️ 将创建 26 个 Jira issues
组件: 2.0 (AI)
Sprint: 1234

确认导入? (y/N): y

🚀 开始导入...

[1/26] 【Aida Agent】Checkpoint 断点恢复... ✅ DEV-12345
   📅 已添加到 Sprint
   👤 已分配
[2/26] 【Aida Agent】多模型路由... ✅ DEV-12346
   📅 已添加到 Sprint
   👤 已分配
...

============================================================
✅ 成功创建: 26 个
============================================================

创建的 issues:
  - http://jira.caidaocloud.com:8080/browse/DEV-12345
  - http://jira.caidaocloud.com:8080/browse/DEV-12346
  ...
```

## 注意事项

1. **Issue Type**: 使用中文 "故事"，不是 "Story"
2. **Components**: 固定为 "2.0" (ID: 10805)
3. **Priority 映射**:
   - P0 → Highest
   - P1 → High
   - P2 → Medium
4. **Sprint**: 自动获取下一个 future sprint
5. **Assignee**: 自动分配给当前登录用户

## 手动导出 GitLab Issues

如果无法使用 API，可以手动从 GitLab 页面导出：

1. 打开 https://gitee.52emp.com/caidao-web-project/aida/-/issues
2. 复制 issues 列表
3. 创建 JSON 文件：

```json
[
  {
    "title": "【Aida Agent】Checkpoint 断点恢复",
    "description": "希望 Agent 执行过程中如果服务重启了...",
    "labels": ["P1"],
    "web_url": "https://gitee.52emp.com/caidao-web-project/aida/-/issues/16"
  }
]
```

4. 运行导入脚本：`--from-file issues.json`
