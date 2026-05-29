---
name: jira-cli
description: Use when working with Caidao private Jira at http://jira.caidaocloud.com:8080/ via jira-cli or Jira REST/GreenHopper APIs. Triggers include Jira, issue, sprint, board, RapidBoard, GreenHopper, 2.0研发看板, 【2.0研发看板】, board 45, rapidView=45, DEV project, Dev Sprint, 查看当前 issue, 按 sprint 查看, 看板, 迭代, 任务, 缺陷, 故障. Prefer the GreenHopper planning endpoint for RapidBoard planning-page data because jira sprint list can miss current board 45 sprints.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [jira, caidao, rapidboard, greenhopper, sprint, issue]
    related_skills: [linear]
---

# Jira CLI

Use the installed `jira` command to operate Caidao's private Jira instance.

Default Jira server:

```text
http://jira.caidaocloud.com:8080/
```

Upstream docs: <https://github.com/ankitpokhrel/jira-cli>

## 快速参考（固化信息）

| 属性 | 值 | 说明 |
|------|-----|------|
| **Board ID** | `45` | `2.0研发看板` |
| **Project Key** | `DEV` | 默认项目 |
| **Component ID** | `10805` | `"2.0"` 组件 |
| **Issue Type** | `故事` | 必须用中文 |
| **Default Assignee** | `$(jira me)` | 当前登录用户 |

**Sprint 自动获取逻辑：**
- **Active Sprint**: 当前进行中的 sprint（如 Dev Sprint 214）
- **Next Sprint**: 下一个未来的 sprint（如 Dev Sprint 215）
- 使用 API 动态获取，不硬编码 ID

**创建 Issue 的默认流程：**
1. 优先尝试 `jira issue create` (CLI)
2. 如果失败（DEV 项目 "invalid issue types" 错误），使用 REST API
3. 自动获取并添加到 **下一个未来 sprint**（通常是 Dev Sprint 215）
4. 默认分配给 **当前登录用户**

## Prerequisites

- Do not install another Jira CLI unless `jira` is missing. First check `command -v jira` and `jira version`.
- Default config path is `~/.config/.jira/.config.yml`; override per command with `--config` or globally with `JIRA_CONFIG_FILE`.
- Never print, commit, or store Jira passwords, API tokens, or PATs in repo files.

## First-time configuration

If `jira me` or `jira serverinfo` fails because config/auth is missing, configure the CLI for the local Jira server.

For Caidao's private Jira, use basic auth unless the user confirms a Personal Access Token is available. With basic auth, `JIRA_API_TOKEN` contains the user's Jira password:

```bash
export JIRA_API_TOKEN="<jira-password>"
jira init \
  --installation local \
  --server "http://jira.caidaocloud.com:8080/" \
  --login "<jira-username-or-email>" \
  --auth-type basic \
  --project "<default-project-key>"
```

The CLI can also read the password from macOS Keychain. Store it under service `jira-cli` and account equal to the Jira login:

```bash
security add-generic-password -U -s jira-cli -a "<jira-username>" -w "<jira-password>"
```

If `jira init` verifies login/project/board but fails while "Configuring metadata" with `unexpected format`, create a minimal config manually. The `installation` value is case-sensitive and must be `Local`, not `local`:

```yaml
auth_type: basic
board: ""
installation: Local
login: <jira-username>
project:
  key: CDC
  type: classic
server: http://jira.caidaocloud.com:8080/
timezone: Asia/Shanghai
```

For a personal access token, use bearer auth:

```bash
export JIRA_API_TOKEN="<personal-access-token>"
export JIRA_AUTH_TYPE=bearer
jira init \
  --installation local \
  --server "http://jira.caidaocloud.com:8080/" \
  --login "<jira-username-or-email>" \
  --auth-type bearer \
  --project "<default-project-key>"
```

If the user has multiple Jira contexts, use a separate config file:

```bash
jira issue list --config ./caidao-jira.yml --plain
JIRA_CONFIG_FILE=./caidao-jira.yml jira issue list --plain
```

Ask only for missing non-secret values such as username, project key, board name, issue key, or desired status. For secrets, ask the user to set the environment variable locally instead of pasting the value into chat.

## Operating rules

1. Prefer machine-readable or non-interactive output for agent work:
   - `--raw` for JSON when available
   - `--plain --no-headers --no-truncate` for tables
   - `--csv` when the user wants spreadsheet-friendly output
2. Use interactive views only when the user explicitly asks to browse Jira interactively.
3. Resolve names to keys first. If the user says "my project" or "the mobile ticket", list projects/issues before mutating.
4. Confirm destructive or broad actions before running them: delete, bulk transition, bulk edit, sprint close, or changes affecting many issues.
5. After any write, verify by reading the affected issue and report the key, status, assignee, and URL when useful.
6. When a command fails, rerun with `--debug` only if needed, and redact tokens or cookies before showing output.

## Common commands

### Identity and server

```bash
jira me
jira serverinfo
jira project list
```

### Search and list issues

```bash
# Recent issues in the configured project
jira issue list --plain --no-truncate

# Assigned to me
jira issue list -a"$(jira me)" --plain --no-truncate

# Raw JQL within the configured project context
jira issue list -q 'status != Done ORDER BY updated DESC' --raw

# Cross-project JQL
jira issue list -q 'project IS NOT EMPTY AND assignee = currentUser() ORDER BY updated DESC' --plain

# Useful filters
jira issue list -s"In Progress" --created month --plain
jira issue list "search text" --plain --no-truncate
```

Useful list flags:

- `-p <KEY>`: choose project
- `-t <type>`: issue type
- `-s <status>`: status, repeatable
- `-y <priority>`: priority
- `-a <assignee>`: assignee; `x` means unassigned
- `-r <reporter>`: reporter
- `-l <label>`: label, repeatable
- `--created`, `--updated`: `today`, `week`, `month`, `year`, `yyyy-mm-dd`, or relative periods like `-10d`
- `--paginate <from>:<limit>`: limit result size
- `--columns KEY,SUMMARY,STATUS,ASSIGNEE,PRIORITY,UPDATED`: control plain output columns

### View and open

```bash
jira issue view ISSUE-123 --plain --comments 5
jira issue view ISSUE-123 --raw
jira open ISSUE-123
jira open ISSUE-123 --no-browser
```

Use `--no-browser` if the user only needs the URL or a dry lookup.

### Create issues

**策略：优先使用 CLI，失败时回退到 REST API**

#### 方法 1: 使用 jira CLI（推荐）

For simple, explicit requests, create directly:

```bash
jira issue create \
  -p PRJ \
  -t Task \
  -s "Short imperative summary" \
  -b "Description" \
  --no-input \
  --raw
```

For richer issues, present a short proposal and wait for confirmation before creating if you inferred any of:

- priority
- labels
- component or fix version
- parent/epic
- assignee
- substantial description

Create with optional fields:

```bash
jira issue create \
  -p PRJ \
  -t Story \
  -s "Implement import status polling" \
  -P EPIC-42 \
  -a "$(jira me)" \
  -l backend \
  -C API \
  -y High \
  --custom story-points=3 \
  --no-input \
  --raw
```

For long descriptions, use stdin to avoid quoting problems:

```bash
printf '%s\n' "Description text" | jira issue create -p PRJ -t Task -s "Summary" --template - --no-input
```

#### 方法 2: REST API 回退（当 CLI 失败时使用）

**已知问题：** DEV 项目的 `jira issue create` 可能会失败并返回 "invalid issue types in config" 错误。此时应使用 REST API。

**步骤：**

1. 获取 token（从 macOS Keychain）：
```bash
TOKEN=$(security find-generic-password -s jira-cli -a "$(jira me)" -w)
```

2. **DEV 项目特殊要求：**
   - Issue type 必须用中文：`"故事"` 而不是 `"Story"`
   - 必须包含 `components` 字段，使用 `"2.0"` 组件（id: `"10805"`）
   - Priority 值：`"Highest"`, `"High"`, `"Medium"`, `"Low"`, `"Lowest"`

3. 创建 issue：
```bash
curl -s -X POST \
  -u "$(jira me):${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "fields": {
      "project": {"key": "DEV"},
      "summary": "【Aida Agent】标题",
      "description": "描述内容",
      "issuetype": {"name": "故事"},
      "priority": {"name": "High"},
      "components": [{"id": "10805"}]
    }
  }' \
  "http://jira.caidaocloud.com:8080/rest/api/2/issue"
```

4. 添加到 sprint（获取 sprint ID 后）：
```bash
curl -s -X POST \
  -u "$(jira me):${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"issues": ["DEV-12345"]}' \
  "http://jira.caidaocloud.com:8080/rest/agile/1.0/sprint/${SPRINT_ID}/issue"
```

5. 分配给当前用户：
```bash
curl -s -X PUT \
  -u "$(jira me):${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"fields": {"assignee": {"name": "'$(jira me)'"}}}' \
  "http://jira.caidaocloud.com:8080/rest/api/2/issue/DEV-12345"
```

**查找 Sprint ID（动态获取）：**

```bash
# 获取 active sprint（当前进行中）
ACTIVE_SPRINT_ID=$(curl -s -X GET \
  -u "$(jira me):${TOKEN}" \
  "http://jira.caidaocloud.com:8080/rest/agile/1.0/board/45/sprint?state=active" | jq -r '.values[0].id')

# 获取下一个 future sprint（推荐：用于新 issue）
NEXT_SPRINT_ID=$(curl -s -X GET \
  -u "$(jira me):${TOKEN}" \
  "http://jira.caidaocloud.com:8080/rest/agile/1.0/board/45/sprint?state=future" | jq -r '.values[0].id')

# 查看 sprint 信息
curl -s -X GET \
  -u "$(jira me):${TOKEN}" \
  "http://jira.caidaocloud.com:8080/rest/agile/1.0/board/45/sprint?state=future,active" | jq '.values[] | {id: .id, name: .name, state: .state}'
```

**完整流程示例（自动获取 next sprint）：**
```bash
# 1. 获取 token
TOKEN=$(security find-generic-password -s jira-cli -a "$(jira me)" -w)

# 2. 创建 issue
ISSUE_KEY=$(curl -s -X POST \
  -u "$(jira me):${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "fields": {
      "project": {"key": "DEV"},
      "summary": "【Aida Agent】后端支持刷新 token",
      "description": "后端需要提供刷新 token 的接口支持...",
      "issuetype": {"name": "故事"},
      "priority": {"name": "High"},
      "components": [{"id": "10805"}]
    }
  }' \
  "http://jira.caidaocloud.com:8080/rest/api/2/issue" | jq -r '.key')

# 3. 自动获取 next sprint 并添加
NEXT_SPRINT_ID=$(curl -s -X GET \
  -u "$(jira me):${TOKEN}" \
  "http://jira.caidaocloud.com:8080/rest/agile/1.0/board/45/sprint?state=future" | jq -r '.values[0].id')

curl -s -X POST \
  -u "$(jira me):${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"issues\": [\"${ISSUE_KEY}\"]}" \
  "http://jira.caidaocloud.com:8080/rest/agile/1.0/sprint/${NEXT_SPRINT_ID}/issue"

# 4. 分配给当前登录用户（默认行为）
curl -s -X PUT \
  -u "$(jira me):${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"fields": {"assignee": {"name": "'$(jira me)'"}}}' \
  "http://jira.caidaocloud.com:8080/rest/api/2/issue/${ISSUE_KEY}"
```

### Edit, assign, comment, and transition

```bash
# Edit fields
jira issue edit ISSUE-123 -s "New summary" -b "New description" --no-input

# Add or remove labels/components/fix versions with +/- values
jira issue edit ISSUE-123 --label backend --label -old-label --no-input

# Assign
jira issue assign ISSUE-123 "$(jira me)"
jira issue assign ISSUE-123 "Display Name"
jira issue assign ISSUE-123 x

# Comment
jira issue comment add ISSUE-123 "Comment text" --no-input
printf '%s\n' "Multi-line comment" | jira issue comment add ISSUE-123 --template - --no-input

# Transition
jira issue move ISSUE-123 "In Progress"
jira issue move ISSUE-123 Done --comment "Verified and ready." --resolution Fixed
```

Before editing descriptions, first inspect the current issue with `jira issue view ISSUE-123 --plain` so important existing content is not accidentally replaced.

### Boards, sprints, epics, and releases

Use command help before less-common operations because available flags vary by Jira version and project configuration:

```bash
jira board --help
jira sprint --help
jira epic --help
jira release --help
```

#### RapidBoard planning data on Jira 8.3

For Caidao Jira 8.3, `jira sprint list` and `/rest/agile/1.0/board/{id}/sprint` can return stale or incomplete sprint data compared with the RapidBoard planning page. When the user references a URL like:

```text
http://jira.caidaocloud.com:8080/secure/RapidBoard.jspa?rapidView=45&view=planning.nodetail&issueLimit=100
```

fetch the page and inspect the `board-page-load` script. It contains the actual GreenHopper planning endpoint, for example:

```text
/rest/greenhopper/1.0/xboard/plan/backlog/data.json?rapidViewId=45&selectedProjectKey=DEV
```

Use that endpoint for sprint/issue data that must match the web UI:

```bash
TOKEN="$(security find-generic-password -s jira-cli -a "$(jira me)" -w)"
curl -fsS -u "$(jira me):${TOKEN}" \
  "http://jira.caidaocloud.com:8080/rest/greenhopper/1.0/xboard/plan/backlog/data.json?rapidViewId=45&selectedProjectKey=DEV" \
  -o /tmp/jira_board45_backlog.json

# Sprint summary, case-insensitive for names like "Dev Sprint 214"
jq -r '.sprints[]?
  | select((.name | ascii_downcase) | startswith("dev sprint"))
  | [.id, .name, .state, (.startDate // ""), (.endDate // ""), (.issuesIds | length)]
  | @tsv' /tmp/jira_board45_backlog.json
```

To list issues assigned to the current user in those sprints:

```bash
jq -r '
  . as $root
  | $root.sprints[]
  | select((.name | ascii_downcase) | startswith("dev sprint"))
  | . as $s
  | $s.issuesIds[]?
  | . as $issueId
  | ($root.issues[] | select(.id == $issueId))
  | select(.assignee == "stanley.yang")
  | [
      $s.name,
      .key,
      ($root.entityData.statuses[.statusId].statusName // .statusId),
      (.done | tostring),
      .summary
    ]
  | @tsv
' /tmp/jira_board45_backlog.json
```

Observed Caidao board mapping:

- `rapidView=45` = `2.0研发看板` = Board ID `45`
- The page's project key is `DEV`
- The planning endpoint returns current/future sprint names like `Dev Sprint 214`; do not assume all sprint names are uppercase `DEV Sprint`

**固化的 Board 和 Sprint 信息：**

| 属性 | 值 | 获取方式 |
|------|-----|---------|
| Board ID | `45` | 固化 |
| Board 名称 | `2.0研发看板` | 固化 |
| Project Key | `DEV` | 固化 |
| Active Sprint | Dev Sprint 214 | 动态获取：`state=active` 的第一个 |
| Next Sprint | Dev Sprint 215 | 动态获取：`state=future` 的第一个 |

**动态获取 Sprint ID（推荐）：**
```bash
# 获取 active sprint（当前进行中）
ACTIVE_SPRINT_ID=$(curl -s -X GET \
  -u "$(jira me):$(security find-generic-password -s jira-cli -a "$(jira me)" -w)" \
  "http://jira.caidaocloud.com:8080/rest/agile/1.0/board/45/sprint?state=active" | jq -r '.values[0].id')

# 获取 next sprint（下一个未来 sprint，用于新 issue）
NEXT_SPRINT_ID=$(curl -s -X GET \
  -u "$(jira me):$(security find-generic-password -s jira-cli -a "$(jira me)" -w)" \
  "http://jira.caidaocloud.com:8080/rest/agile/1.0/board/45/sprint?state=future" | jq -r '.values[0].id')
```

**查看所有 sprints：**
```bash
curl -s -X GET \
  -u "$(jira me):$(security find-generic-password -s jira-cli -a "$(jira me)" -w)" \
  "http://jira.caidaocloud.com:8080/rest/agile/1.0/board/45/sprint?state=future,active" | jq '.values[] | {id: .id, name: .name, state: .state}'
```

**默认 Assignee：**
- 创建 issue 时默认分配给当前登录用户：`"$(jira me)"`
- CLI 方式：`-a "$(jira me)"`
- REST API 方式：`"assignee": {"name": "'$(jira me)'"}`

For sprint actions:

- List sprints before adding issues or closing a sprint.
- Confirm before `jira sprint close`.
- Verify issue placement/status after `jira sprint add`.

## Response style

When reporting results, keep the answer compact:

```text
KEY-123 | In Progress | assignee | Short summary
http://jira.caidaocloud.com:8080/browse/KEY-123
```

For create/update actions, include:

- action completed
- issue key
- important changed fields
- direct URL if known

Do not include raw JSON unless the user asks for it.
