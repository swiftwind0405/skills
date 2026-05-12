# vikunja

Interact with a Vikunja task management instance via its REST API. Manage tasks, projects, labels, assignees, and reminders with safe-update patterns.

## Configuration

| Variable | Required | Description |
|---|---|---|
| `VIKUNJA_BASE_URL` | Yes | Base URL, e.g. `https://vikunja.example.com` |
| `VIKUNJA_API_TOKEN` | Yes | API token from Settings → API Tokens |
| `VIKUNJA_SQLITE_PATH` | No | Path to SQLite DB for direct read-only access |

## Bundled Assets

- `references/` — Vikunja API documentation
