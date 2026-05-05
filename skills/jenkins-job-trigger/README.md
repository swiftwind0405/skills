# Jenkins Job Trigger Skill

Trigger Jenkins jobs with API token + CSRF crumb, wait for build result, and auto-diagnose failures.

## Environment Variables

| Variable              | Required | Description                                                       |
| --------------------- | -------- | ----------------------------------------------------------------- |
| `JENKINS_URL`         | Yes      | Jenkins base URL, e.g. `http://jenkins.example.com:8080`          |
| `JENKINS_USER`        | Yes      | Jenkins username                                                  |
| `JENKINS_TOKEN`       | Yes      | Jenkins API token (not password)                                  |
| `JOB_PATH`            | No       | Default job path, e.g. `job/example-folder/job/example-web-build` |
| `JENKINS_JOB_ALIASES` | No       | Path to a JSON file mapping friendly job names → job paths        |

### Job Aliases File Format

The `JENKINS_JOB_ALIASES` env var should point to a JSON file with this structure:

```json
{
  "web-build": "job/example-folder/job/example-web-build",
  "mobile-build": "job/example-folder/job/example-mobile-build",
  "ai-service": "job/example-folder/job/example-ai-service",
  "backend-api": "job/example-folder/job/example-backend-api"
}
```

### Example

```bash
export JENKINS_URL="http://jenkins.example.com:8080"
export JENKINS_USER="your-username"
export JENKINS_TOKEN="your-api-token"
export JENKINS_JOB_ALIASES="/path/to/job-aliases.json"
```
