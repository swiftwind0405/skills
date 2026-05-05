---
name: huntly-manager
description: Use Huntly in mixed mode: MCP for reads and REST API scripts for saving content plus collection/group management, without driving the browser extension UI.
---

# Huntly Manager (MCP Reads + REST Writes)

Use Huntly in mixed mode: prefer MCP tools for read/query tasks, and use REST API scripts for saving content plus collection/group management instead of controlling the extension UI.

## When to use

Trigger this skill when the user asks to:

- save a URL/page/webpage into Huntly
- add extracted content into Huntly
- send a page to Huntly My List / Archive
- import content into Huntly from chat
- translate a URL/article and save/bookmark it into Huntly
- inspect Huntly collection groups / collection tree
- create a collection group or collection
- update / rename / move a collection
- look up a collection ID by group/path

## Why this route

The extension ultimately calls Huntly's REST API. Relevant endpoints include:

- `POST /api/page/save`
- `POST /api/page/saveToLibrary/{id}`
- `POST /api/page/archive/{id}`
- `PATCH /api/page/{id}/collection`
- `GET /api/collections/tree`
- `POST /api/collections`
- `PUT /api/collections/{id}`
- `GET /api/collection-groups`
- `POST /api/collection-groups`
- `PUT /api/collection-groups/{id}`

This is more stable than driving the extension popup and is general enough for both content import and collection management.

## Inputs to collect

Ask only for what is missing.

### For save/import requests

Required minimum:

- `url`

Strongly recommended:

- `title`
- `content` or at least `description`

Optional:

- `author`
- `siteName`
- `faviconUrl`
- `collectionId`
- save mode: `my-list` (default), `archive`, or `none`

### For collection management

Typical inputs:

- group name or `groupId`
- collection path like `Toolbox/items/ai` or a known `collectionId`
- desired operation: query, create, rename/update, or move
- optional icon/color

## Configuration

| Variable             | Required | Description                                                |
| -------------------- | -------- | ---------------------------------------------------------- |
| `HUNTLY_BASE_URL`    | Yes      | Base URL, e.g. `https://huntly.example.com`                |
| `HUNTLY_TOKEN`       | Yes\*    | JWT token for authentication                               |
| `HUNTLY_USERNAME`    | Yes\*    | Username (alternative to token)                            |
| `HUNTLY_PASSWORD`    | Yes\*    | Password (alternative to token)                            |
| `HUNTLY_SQLITE_PATH` | No       | Path to Huntly SQLite database for direct read-only access |

\*Provide either `HUNTLY_TOKEN` or both `HUNTLY_USERNAME` + `HUNTLY_PASSWORD`.

The agent must confirm auth is configured before making any request.

## Bundled scripts

### 1) Save/import content

```bash
python3 skills/huntly-manager/scripts/huntly_save_content.py --url "https://example.com/post"
```

This script will:

1. authenticate with Huntly
2. call `POST /api/page/save`
3. optionally move the item into My List or Archive
4. optionally assign a collection
5. print JSON result to stdout

### 2) Manage collections/groups

```bash
python3 skills/huntly-manager/scripts/huntly_collections.py tree --flat
```

This script supports:

- `tree` — fetch full collection tree
- `groups` — list collection groups
- `get-collection` — query a collection by id or group/path
- `create-group` — create a group
- `update-group` — update a group
- `create-collection` — create a collection under a group or parent collection
- `update-collection` — rename/update/move a collection

## Recommended workflow

### Preferred mixed mode: MCP for reads, REST scripts for writes

When Huntly's MCP server is configured, prefer a mixed approach:

- use Huntly MCP tools for read/query tasks such as recent items, library browsing, full-text search, highlights, RSS feeds, and content details
- use this skill's REST scripts for write/update tasks such as saving pages, sending items to My List or Archive, assigning collections, and managing collection groups/collections

This keeps reads aligned with the server's MCP surface while preserving the broader write capabilities already implemented in this skill.

Important auth note:

- Huntly MCP uses its own dedicated MCP token, not the normal login JWT
- generate that token from `POST /api/setting/general/generateMcpToken` after signing in as a normal user
- then configure the MCP header as `Authorization: Bearer <mcp-token>`

### MCP fallback when native tools are unavailable

If Huntly's native MCP tools are not injected into Hermes, you can still read from Huntly by speaking MCP over its SSE transport manually from `terminal`/Python:

1. `GET /api/mcp/sse` with:
   - `Authorization: Bearer <mcp-token>`
   - `Accept: text/event-stream`
2. Read the initial SSE event:
   - `event:endpoint`
   - `data:/api/mcp/message?sessionId=...`
3. `POST` JSON-RPC messages to that endpoint with:
   - `Authorization: Bearer <mcp-token>`
   - `Content-Type: application/json`
   - **Do not send an `Accept` header on the POST** for Huntly's server
4. Initialize the session:
   - `initialize`
   - then `notifications/initialized`
5. Call read tools through `tools/call`, for example `list_recent_content`

Observed Huntly-specific quirk:

- posting to `/api/mcp/message?...` with `Accept: application/json` or `Accept: application/json, text/event-stream` triggered `HttpMediaTypeNotAcceptableException`
- posting with no explicit `Accept` header succeeded and returned `202 Accepted`, with the actual JSON-RPC response delivered back on the SSE stream
- plain `mcporter list/call` currently did not work against this Huntly endpoint because of this response-negotiation behavior

### Huntly MCP routing map

Use this quick routing table when deciding whether to call Huntly MCP or the REST scripts in this skill.

#### Read/query tasks → Huntly MCP

- `get_library_content`
  - query My List / Archive / Starred / Read Later
  - optional filters: `source_type`, date range, `limit`, `title_only`
- `list_recent_content`
  - query recently saved content across all sources
  - optional filters: source type, date range, unread only
- `search_content`
  - full-text search across saved Huntly content
  - supports `content_type`, `library_filter`, title-only search, read-state filtering
- `get_content_details`
  - fetch full details for up to 50 known content ids
  - use after search/list results when the user wants the actual content or metadata
- `get_highlights`
  - list highlighted passages with source content context
- `list_rss_feeds`
  - list RSS subscriptions and discover `connector_id`
- `list_rss_items`
  - list entries from one RSS feed by `connector_id`
- `get_unread_rss`
  - fetch unread RSS items across feeds
- `list_tweets`
  - list saved tweets/X posts
- `list_github_stars`
  - list synced GitHub starred repositories

#### Write/update tasks → REST scripts in this skill

- save/import content by URL or extracted content
  - `scripts/huntly_save_content.py`
- send saved item to My List / Archive
  - `scripts/huntly_save_content.py`
- assign collection after saving
  - `scripts/huntly_save_content.py`
- inspect collection tree / groups / collection path
  - `scripts/huntly_collections.py`
- create / rename / move collection
  - `scripts/huntly_collections.py`
- create / update group
  - `scripts/huntly_collections.py`
- update group / collection icon or color
  - `scripts/huntly_collections.py`

#### Practical intent mapping

- "查我最近存了什么" → `list_recent_content`
- "搜一下我 Huntly 里关于 XXX 的内容" → `search_content`
- "把这篇文章加到 Huntly" → `huntly_save_content.py`
- "把这篇放进 My List / Archive" → `huntly_save_content.py`
- "把文章放到某个 collection" → `huntly_save_content.py` or `huntly_collections.py` depending on whether the item already exists
- "看看有哪些 RSS 源" → `list_rss_feeds`
- "看某个 RSS 源最近的文章" → `list_rss_items`
- "查我的 highlights" → `get_highlights`
- "建一个 collection / 改名 / 挪位置 / 改 icon" → `huntly_collections.py`

#### Link preference

Many Huntly MCP read tools return both:

- `huntlyUrl` = Huntly internal reading page
- `url` = original source URL

When referencing saved Huntly content back to the user, prefer `huntlyUrl` when present.

### A. Save/import content into Huntly

1. If the user gives only a URL, first extract the page content with Hermes tools.
2. Prefer sending cleaned content HTML to Huntly.
3. Run `huntly_save_content.py`.
4. Verify the write when possible:
   - If `HUNTLY_SQLITE_PATH` is set, query the page by returned `page_id` and confirm `title`, `url`, `library_save_status`, and non-empty `content` length.
   - Example: `sqlite3 "$sqlitePath" "select id,title,url,library_save_status,length(content) from page where id=<page_id>;"`
5. Report back the created `page_id`, save mode, collection assignment if any, and verification result.

### B. Query collection info

1. Run `huntly_collections.py tree --flat` when you need a broad view.
2. If the user refers to a path, resolve group + nested path from the tree.
3. Return the matched IDs and path so later operations are unambiguous.

### C. Create a collection

1. Look up the target group from `collections/tree`.
2. If the user names a parent path, resolve it first.
3. Prefer `--ensure-unique` so the script returns an existing sibling instead of creating a duplicate.
4. Return the created/existing collection id and group info.

### D. Edit / move a collection

1. Query the target collection first.
2. Use `update-collection` with only the fields that should change.
3. If moving within hierarchy, pass the new parent id.
4. If moving across groups, pass the new group id.

### E. Translate URL and save to Huntly

Use when the user wants to translate a URL/article/page and save/collect/import it into Huntly.

Typical triggers:

- "translate and save/bookmark this URL"
- "put this URL translated then collect"
- "translate this link and import to Huntly"
- "save this translated article to Huntly"

Required companion skill:

- `url-translate-html` -- URL to bilingual Markdown to HTML

Workflow:

1. Call the `url-translate-html` skill to produce bilingual HTML. That skill handles URL extraction, bilingual translation, and HTML rendering.
2. After `url-translate-html` completes, import the HTML into Huntly:

```bash
python3 skills/huntly-manager/scripts/huntly_save_content.py \
  --url '<ORIGINAL_CANONICAL_URL>' \
  --title '<ORIGINAL_TITLE> / <TRANSLATED_TITLE>' \
  --description '<BILINGUAL_OR_TRANSLATED_SUMMARY>' \
  --author '<AUTHOR_IF_AVAILABLE>' \
  --site-name '<SITE_NAME_IF_AVAILABLE>' \
  --content-file /tmp/url_translate_html/translation-body.html \
  --save-mode my-list
```

If the user specified Archive: `--save-mode archive`.
If the user specified a collection, resolve it via `huntly_collections.py` first, then pass `--collection-id <ID>`.

3. Verify the import:
   - Save script returns `ok: true`, a numeric `page_id`, and `save_mode`.
   - If `HUNTLY_SQLITE_PATH` is set, verify directly:

```bash
sqlite3 '<sqlitePath>' "select id,title,url,library_save_status,length(content) from page where id=<PAGE_ID>;"
```

Expected: title is bilingual, URL is original source, `library_save_status = 1` for My List, `length(content)` is non-trivial, content contains both languages.

Default assumptions:

- Save mode: `my-list` unless user specifies Archive/collection.
- Use cleaned bilingual HTML as Huntly `content`, not raw Markdown.
- Preserve original source URL as the Huntly URL.
- Title format: `<original title> / <Chinese title>`.

Response format:

```text
Done:
- Source Markdown: <source.md>
- Bilingual Markdown: <translation.md>
- Bilingual HTML: <translation-body.html>
- Huntly page_id: <id>
- Save location: My List / Archive / collection <name>
```

Gotchas:

- Do not ask about Huntly if the user clearly says collect/import Huntly; proceed with default `my-list`.
- For this user, Huntly actions must use Huntly MCP-provided tools only unless the user explicitly authorizes another path. If Huntly MCP authentication fails, stop and ask whether to update/provide a new MCP token or allow a one-off API/UI fallback; do not silently use REST scripts.
- Do not use Huntly browser UI for writes; use `huntly_save_content.py`.

## Common commands

### Minimal save to My List

```bash
python3 skills/huntly-manager/scripts/huntly_save_content.py \
  --url "https://example.com/post" \
  --title "Example Post" \
  --description "Short summary"
```

### Save with HTML content from a file

```bash
python3 skills/huntly-manager/scripts/huntly_save_content.py \
  --url "https://example.com/post" \
  --title "Example Post" \
  --content-file /tmp/content.html \
  --description "Short summary" \
  --author "Author Name" \
  --site-name "Example"
```

### Save directly to Archive and assign a collection

```bash
python3 skills/huntly-manager/scripts/huntly_save_content.py \
  --url "https://example.com/post" \
  --title "Example Post" \
  --save-mode archive \
  --collection-id 123
```

### Inspect the collection tree

```bash
python3 skills/huntly-manager/scripts/huntly_collections.py tree --flat
```

### List groups

```bash
python3 skills/huntly-manager/scripts/huntly_collections.py groups
```

### Query a collection by path inside a group

```bash
python3 skills/huntly-manager/scripts/huntly_collections.py get-collection \
  --group-name "Toolbox" \
  --path "items/ai"
```

### Create a top-level collection under Toolbox

```bash
python3 skills/huntly-manager/scripts/huntly_collections.py create-collection \
  --group-name "Toolbox" \
  --name "items" \
  --ensure-unique
```

### Create a nested collection under a parent path

```bash
python3 skills/huntly-manager/scripts/huntly_collections.py create-collection \
  --group-name "Toolbox" \
  --parent-path "items" \
  --name "ai" \
  --ensure-unique
```

### Rename a collection

```bash
python3 skills/huntly-manager/scripts/huntly_collections.py update-collection \
  --collection-id 123 \
  --name "agents"
```

### Create or rename a group

```bash
python3 skills/huntly-manager/scripts/huntly_collections.py create-group --name "Toolbox"
python3 skills/huntly-manager/scripts/huntly_collections.py update-group --group-id 3 --name "AI Tools"
```

## Notes / gotchas

- Huntly requires `url` and `domain`; the save script derives `domain` from the URL if omitted.
- Huntly stores saved `content` as HTML. Prefer extracted HTML over raw Markdown when possible.
- `save-mode my-list` is the default because `page/save` alone only creates the item; it does not guarantee the item lands in the user's library list.
- For collection creation, `groupId` targets the group and `parentId` is only for nesting under another collection.
- `collections/tree` returns groups with nested collections; group names and collection names should not be conflated.
- The backend enforces duplicate group-name checks, but collection duplicate prevention is mainly a client-side convention, so prefer querying first or using `--ensure-unique`.
- Prefer API auth over browser-cookie reuse in skills.

## Data model reference

See [references/huntly-data-model.md](references/huntly-data-model.md) for the full Huntly SQLite schema including the `page` table, `page_json_properties` JSON structure (tweets, GitHub repos), and related tables (`page_highlight`, `connector`, `collection`, `folder`). Use this as a reference when constructing direct SQL queries or interpreting MCP/REST results.

## Local database

The SQLite database path is read from the `HUNTLY_SQLITE_PATH` environment variable. Use this for direct SQLite queries when the Huntly service or MCP is unavailable, or when ad-hoc SQL is more convenient than the API (e.g. complex joins, bulk analysis).
