# jenkins-job-trigger

Trigger Jenkins jobs via a bundled Python script that authenticates with username + API token, handles CSRF crumb, supports build parameters, and can wait for queue/build completion.

## Configuration

| Variable | Required | Description |
|---|---|---|
| `JENKINS_URL` | Yes | Jenkins base URL, e.g. `http://jenkins.example.com:8080` |
| `JENKINS_USER` | Yes | Jenkins username |
| `JENKINS_TOKEN` | Yes | Jenkins API token (not password) |
| `JOB_PATH` | No | Default job path, e.g. `job/example-folder/job/example-web-build` |
| `JENKINS_JOB_ALIASES` | No | Path to JSON file mapping friendly names → job paths |

### Job Aliases Format

```json
{
  "web-build": "job/example-folder/job/example-web-build",
  "mobile-build": "job/example-folder/job/example-mobile-build"
}
```

## Bundled Assets

- `references/` — Jenkins API notes
- `scripts/` — `jenkins_trigger.py`
