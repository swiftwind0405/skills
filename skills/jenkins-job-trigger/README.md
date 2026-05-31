# jenkins-job-trigger

通过内置 Python 脚本触发 Jenkins 任务。脚本使用用户名 + API token 认证，处理 CSRF crumb，支持构建参数，并可等待队列/构建完成。

## 配置

| 变量                  | 必填 | 说明                                                          |
| --------------------- | ---- | ------------------------------------------------------------- |
| `JENKINS_URL`         | 是   | Jenkins 基础 URL，例如 `http://jenkins.example.com:8080`      |
| `JENKINS_USER`        | 是   | Jenkins 用户名                                                |
| `JENKINS_TOKEN`       | 是   | Jenkins API token（不是密码）                                 |
| `JOB_PATH`            | 否   | 默认任务路径，例如 `job/example-folder/job/example-web-build` |
| `JENKINS_JOB_ALIASES` | 否   | JSON 文件路径，用于将易记名称映射到任务路径                   |

### 任务别名格式

```json
{
  "web-build": "job/example-folder/job/example-web-build",
  "mobile-build": "job/example-folder/job/example-mobile-build"
}
```

## 内置资源

- `references/`：Jenkins API 说明
- `scripts/`：`jenkins_trigger.py`
