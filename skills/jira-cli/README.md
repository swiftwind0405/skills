# jira-cli

通过已安装的 [ankitpokhrel/jira-cli](https://github.com/ankitpokhrel/jira-cli) 命令操作财道私有 Jira 实例。

## 配置

| 变量               | 必填 | 说明                                                    |
| ------------------ | ---- | ------------------------------------------------------- |
| `JIRA_API_TOKEN`   | 是   | basic auth 使用的 Jira 密码；如可用，也可用个人访问令牌 |
| `JIRA_AUTH_TYPE`   | 否   | 使用个人访问令牌时设置为 `bearer`                       |
| `JIRA_CONFIG_FILE` | 否   | 多 Jira 上下文使用的替代配置路径                        |

默认服务器：

```text
http://jira.caidaocloud.com:8080/
```

首次本地使用用户名/密码配置：

```bash
export JIRA_API_TOKEN="<jira-password>"
```

```bash
jira init \
  --installation local \
  --server "http://jira.caidaocloud.com:8080/" \
  --login "<jira-username-or-email>" \
  --auth-type basic \
  --project "<default-project-key>"
```

如果登录成功后 `jira init` 在生成元数据时失败，请使用手动配置，并将 `installation` 设置为 `Local`（大写 `L`），同时把密码存入 macOS Keychain 的 `jira-cli` 服务下。

## 常用命令

```bash
jira me
jira serverinfo
jira project list
jira issue list --plain --no-truncate
jira issue view ISSUE-123 --plain --comments 5
jira issue create -p PRJ -t Task -s "Summary" -b "Description" --no-input --raw
jira issue comment add ISSUE-123 "Comment" --no-input
jira issue move ISSUE-123 "In Progress"
```

## RapidBoard 计划页说明

对于 Jira 8.3 的 RapidBoard 页面，当 CLI 返回的 sprint 列表与 Web UI 不一致时，使用页面对应的 GreenHopper planning endpoint。例如 `2.0研发看板`（`rapidView=45`）：

```bash
curl -fsS -u "$(jira me):$(security find-generic-password -s jira-cli -a "$(jira me)" -w)" \
  "http://jira.caidaocloud.com:8080/rest/greenhopper/1.0/xboard/plan/backlog/data.json?rapidViewId=45&selectedProjectKey=DEV"
```

sprint 名称可能是 `Dev Sprint ...`，而不是全大写的 `DEV Sprint ...`。
