# Huntly Manager Skill

Use Huntly in mixed mode: read via MCP, save content and manage collections/groups via REST API scripts.

## Environment Variables

| Variable             | Required | Description                                                |
| -------------------- | -------- | ---------------------------------------------------------- |
| `HUNTLY_BASE_URL`    | Yes      | Base URL, e.g. `https://huntly.example.com`                |
| `HUNTLY_TOKEN`       | Yes\*    | JWT token for authentication                               |
| `HUNTLY_USERNAME`    | Yes\*    | Username (alternative to token)                            |
| `HUNTLY_PASSWORD`    | Yes\*    | Password (alternative to token)                            |
| `HUNTLY_SQLITE_PATH` | No       | Path to Huntly SQLite database for direct read-only access |

\*Provide either `HUNTLY_TOKEN` or both `HUNTLY_USERNAME` + `HUNTLY_PASSWORD`.

### Example

```bash
export HUNTLY_BASE_URL="https://huntly.example.com"
export HUNTLY_TOKEN="your-jwt-token-here"
# or:
# export HUNTLY_USERNAME="your-username"
# export HUNTLY_PASSWORD="your-password"
export HUNTLY_SQLITE_PATH="/path/to/huntly/db.sqlite"
```
