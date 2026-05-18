# huntly-manager

Use Huntly in mixed mode: MCP for reads, REST API scripts for saving content and managing collections/groups.

## Configuration

| Variable             | Required | Description                                                     |
| -------------------- | -------- | --------------------------------------------------------------- |
| `HUNTLY_BASE_URL`    | Yes      | Base URL, e.g. `https://huntly.example.com`                     |
| `HUNTLY_TOKEN`       | Yes\*    | Normal Huntly login JWT for REST write APIs (not the MCP token) |
| `HUNTLY_USERNAME`    | Yes\*    | Username (alternative to token; script signs in to obtain JWT)  |
| `HUNTLY_PASSWORD`    | Yes\*    | Password (alternative to token)                                 |
| `HUNTLY_SQLITE_PATH` | No       | Path to SQLite DB for direct read-only access                   |

\* Either `HUNTLY_TOKEN` or `HUNTLY_USERNAME` + `HUNTLY_PASSWORD` is required.

## Bundled Assets

- `references/` — API documentation
- `scripts/` — `huntly_save_content.py`, `huntly_collections.py`
