# Vikunja Skill

Manage Vikunja tasks, projects, labels, assignees, and reminders via REST API.

## Environment Variables

| Variable              | Required | Description                                                                |
| --------------------- | -------- | -------------------------------------------------------------------------- |
| `VIKUNJA_BASE_URL`    | Yes      | Base URL of the instance, e.g. `https://vikunja.example.com`               |
| `VIKUNJA_API_TOKEN`   | Yes      | API token created under Settings → API Tokens in the Vikunja web UI        |
| `VIKUNJA_SQLITE_PATH` | No       | Path to the Vikunja SQLite database for direct read-only access (fallback) |

### Example

```bash
export VIKUNJA_BASE_URL="https://vikunja.example.com"
export VIKUNJA_API_TOKEN="your-api-token-here"
export VIKUNJA_SQLITE_PATH="/path/to/vikunja/db/vikunja.db"
```
