---
name: vikunja
description: Interact with a Vikunja task management instance via its REST API. Use when the user wants to manage tasks, projects, labels, assignees, or reminders in Vikunja — including creating tasks, listing what's due, marking things done, adding labels, assigning users, or organizing projects. Trigger on phrases like "add a task", "what's due today", "create a project in Vikunja", "assign this to me", "set a reminder", or any mention of Vikunja task management.
---

# Vikunja Skill

Connects an agent to any Vikunja instance via its REST API (`/api/v1`).
Uses an API token for authentication — no session management needed.

## Configuration (required env vars)

| Variable            | Description                                                  |
| ------------------- | ------------------------------------------------------------ |
| `VIKUNJA_BASE_URL`  | Base URL of the instance, e.g. `https://vikunja.example.com` |
| `VIKUNJA_API_TOKEN` | API token created under Settings → API Tokens                |

The agent must confirm both vars are set before making any request.
If missing, tell the user exactly which var is absent and where to create the token
(Settings → API Tokens in the Vikunja web UI).

## Local config

Copy `references/vikunja.example.json` to `references/vikunja.local.json` and fill in real values on the current machine.

Example:

```json
{
  "baseUrl": "https://vikunja.example.com",
  "apiToken": "YOUR_API_TOKEN",
  "sqlitePath": "/path/to/vikunja/db/vikunja.db"
}
```

Check these in order for configuration:

1. Environment variables (`VIKUNJA_BASE_URL`, `VIKUNJA_API_TOKEN`)
2. `references/vikunja.local.json`
3. `references/vikunja.example.json` only as a format reference, never as a real credential source

## Important API conventions

> **Vikunja uses non-standard HTTP verbs:**
>
> - `PUT` = **create** a new resource
> - `POST` = **update** an existing resource
> - `GET` = read / list
> - `DELETE` = delete

All requests:

- Header: `Authorization: Bearer <VIKUNJA_API_TOKEN>`
- Header: `Content-Type: application/json`
- Base: `${VIKUNJA_BASE_URL}/api/v1`

Paginated list endpoints accept `?page=N&per_page=50&s=<search>`.
Response headers `x-pagination-total-pages` and `x-pagination-result-count`
tell you if more pages exist.

## Supported operations

See `references/endpoints.md` for the full endpoint reference.

### Projects

- List all projects the user has access to
- Create a new project
- Get a single project by ID

### Tasks

- List tasks (all, or filtered by project)
- Get a single task by ID
- Create a task in a project
- Update a task (title, description, priority, due date, percent done)
- Mark a task as done (`"done": true`)
- Delete a task

### Labels

- List all available labels
- Create a label
- Add a label to a task
- Remove a label from a task

### Assignees

- Add a user as assignee to a task
- Remove an assignee from a task
- List task assignees

### Reminders

- Add a reminder to a task (absolute datetime or relative offset)
- Remove a reminder from a task
- Reminders are part of the task object — use the task update flow

### Task Relations

- Create a relation between two tasks (precedes, follows, blocked_by, subtask, etc.)
- Delete a relation
- When creating a new task with a known relation, use `related_tasks` inline in the body — no separate call needed
- When adding relations to already-existing tasks, use `PUT /tasks/{id}/relations`

## Workflow guidelines

1. **Resolve names to IDs first.** If the user says "add a task to my Work
   project", list projects and find the ID for "Work" before creating the task.
2. **Confirm destructive actions.** Before deleting a task or project, confirm
   with the user.
3. **Show structured output.** When listing tasks, present title, due date,
   priority, labels, and done status. Format dates in a human-readable way.
4. **Handle pagination.** If `x-pagination-total-pages > 1`, fetch subsequent
   pages or inform the user that results are truncated.
5. **Error handling.** On HTTP 4xx/5xx, surface the `message` field from the
   JSON response to the user. On 401, remind them to check `VIKUNJA_API_TOKEN`.

## Smart task creation

When the user asks to create a task, follow this enrichment workflow before
making any write requests.

### Step 1 — Gather context (parallel where possible)

- Resolve project name → ID (GET /projects if needed)
- GET /projects/{projectID}/tasks?per_page=50 — fetch existing tasks so you
  can spot related work, naming conventions, and priority patterns
- GET /labels?per_page=50 — fetch available labels so you can suggest matching ones

### Step 2 — Infer task fields

Using the user's request and the context collected above, reason about:

| Field           | How to infer                                                                                                                                                                                                       |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **title**       | Clean, imperative phrasing. Extract from the request.                                                                                                                                                              |
| **description** | Only if the task is non-trivial. Write a short summary and, where applicable, a markdown checklist (`- [ ] step`) for action items.                                                                                |
| **priority**    | Match signal words: "urgent"/"asap"/"critical" → 4-5; "important"/"soon" → 3; "when you can"/"low" → 1; otherwise leave at 0 (none).                                                                               |
| **labels**      | Match against existing labels by keyword similarity. Never create new labels silently — propose only existing ones.                                                                                                |
| **due_date**    | Parse explicit deadlines/dates in the request ("due Friday", "by end of month"). Convert to UTC ISO-8601. If ambiguous (e.g. "soon"), ask the user rather than guessing.                                           |
| **start_date**  | Set only when the user explicitly mentions a start date or "beginning on X". Do not infer from context alone — if it seems relevant but wasn't stated, ask.                                                        |
| **relations**   | Scan existing tasks for titles or IDs mentioned in the request. Infer relation kind: "after X" → `follows`, "before X" → `precedes`, "part of X" → `subtask`, "blocks X" → `blocking`, "related to X" → `related`. |

**Simplicity rule:** If the request is a single, unambiguous action with no
implied context (e.g. "add a task called 'Buy milk'"), skip enrichment entirely
and create the task with just the title. Do not over-engineer simple requests.

### Step 3 — Confirm if enriched

If you inferred **any** of the following beyond the raw title, present a
structured proposal and ask the user to confirm or adjust before creating:

- a non-empty description
- a priority > 0
- one or more labels
- a due date or start date
- any relations

Present the proposal in this format:

```
**New task proposal**
Title: <title>
Project: <project name>
Priority: <level or none>
Start: <date or none>
Due: <date or none>
Labels: <list or none>
Relations: <list or none>
Description:
<description or none>

Shall I create it as above, or would you like to change anything?
```

**Date rules:**

- If the user gives an explicit date → parse and include it, no need to ask.
- If the user uses vague time language ("soon", "eventually") → ask for a
  concrete date rather than guessing. Do not silently skip if context strongly
  implies urgency.
- If no date is mentioned and context doesn't call for one → omit both fields.

If the user confirms (or the task is simple and no confirmation is needed),
proceed to Step 4.

### Step 4 — Create and apply

1. PUT /projects/{projectID}/tasks — with title, description, priority,
   due_date, and `related_tasks` inline (for relations to existing tasks)
2. For each confirmed label: PUT /tasks/{newTaskID}/labels with `{"label_id": N}`
3. Report back: task title, its assigned ID/index, and a link if possible.

> **Labels cannot be set during creation** — they must be applied via separate
> PUT /tasks/{id}/labels calls after the task is created.

### Safe task update — mandatory pattern

> **Vikunja's POST /tasks/{id} resets fields to zero/null if they are absent
> from the body** — including percent_done, due_date, start_date,
> end_date, priority, hex_color, and description.

**Always follow this pattern before updating any existing task:**

1. GET /tasks/{id} — fetch current state
2. Build update body by starting **from the full current object** and overriding
   only the fields you intend to change
3. Always preserve these fields from the GET response (even if not changing them):
   - description
   - done
   - done_at
   - due_date
   - reminders
   - repeat_after / repeat_mode
   - priority
   - start_date
   - end_date
   - assignees
   - hex_color
   - percent_done
   - cover_image_attachment_id
   - is_favorite

   > See: https://github.com/go-vikunja/vikunja/issues/1459

4. POST /tasks/{id} with the merged body

**Never send a partial update body without first reading the task.**
This applies when bulk-updating multiple tasks too: GET each one individually
before POSTing.

## Troubleshooting / recovery

When the configured API path fails, do not assume the token is wrong — first verify the instance itself.

### 1. Verify the base URL is actually Vikunja

A common failure mode is that `VIKUNJA_BASE_URL` points at a different self-hosted app (for example Linkding) while reusing a Vikunja token. Symptoms:

- `/api/v1/*` returns `404 Not Found`
- the site root serves HTML for a different app
- auth appears set, but every Vikunja endpoint is missing

Quick check pattern:

1. print `VIKUNJA_BASE_URL`
2. request the site root and inspect the returned HTML/app identity
3. request a lightweight Vikunja endpoint such as `/api/v1/projects?per_page=1`

If the root HTML clearly belongs to another app, fix `VIKUNJA_BASE_URL` before doing anything else.

### 2. For self-hosted VPS installs, check whether Vikunja is even running

If the API returns 502/connection errors, inspect the host/container rather than retrying blindly.

Useful checks on a Docker host:

```bash
ssh vps 'docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"'
ssh vps 'docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}" | grep -i vikunja || true'
ssh vps 'docker compose ls 2>/dev/null | grep -i vikunja || true'
ssh vps 'find /data /root /var/lib/docker/volumes/portainer_data/_data/compose -maxdepth 4 \( -iname "*vikunja*" -o -name docker-compose.yml -o -name compose.yml -o -name compose.yaml \) 2>/dev/null | grep -i vikunja || true'
```

### 3. Emergency read-only recovery from SQLite

If Vikunja is down but the user only needs to _read_ data, and this is a self-hosted instance you can access, use the SQLite database as a fallback.

The SQLite database path is stored in `references/vikunja.local.json` under the `sqlitePath` key. See [references/vikunja-data-model.md](references/vikunja-data-model.md) for the full schema and useful queries.

**Important:** this fallback is read-only. Do not write directly to the database unless the user explicitly asks for DB-level repair and you have confirmed backups/scope.

### 4. Name matching should be fuzzy enough for human typos

When the user asks for a project by name and an exact API/DB match fails, also check case-insensitive `contains` matches and visually similar titles. Real data may contain typoed project names like `Wistlist` when the user says `wishlist`.

## Example interactions

- "What tasks are due this week?" → GET /tasks/all with filter, format results
- "Mark task 42 as done" → POST /tasks/42 with `{"done": true}`
- "Add the 'urgent' label to task 17" → resolve label ID, PUT /tasks/17/labels
- "Assign me to task 5" → look up current user via GET /user, PUT /tasks/5/assignees
- "Set a reminder for task 8 in 2 hours" → compute absolute datetime, POST /tasks/8

### Smart creation examples

- "Add a task called 'Buy milk' to Errands" → simple, no enrichment needed.
  Create directly with just the title.

- "In the Backend project add a task to migrate the auth service to JWT" →
  Fetch project tasks + labels. Notice existing auth-related tasks. Infer:
  title "Migrate auth service to JWT", description with checklist (design
  schema, update endpoints, write tests, update docs), priority medium (no
  urgency signal), labels matching "backend"/"auth" if available. Present
  proposal, wait for confirmation, then create + apply labels.

- "Add an urgent task in DevOps to fix the broken CI pipeline, it's blocking
  the release" → priority = urgent (5), infer relation `blocking` to any
  release-related task found in the project. Include a short description.
  Present proposal for confirmation before creating.

- "Create a task for next week Monday to review Q2 roadmap in Planning" →
  Parse "next week Monday" → set due_date. No start_date implied. If labels
  like "review" or "planning" exist, suggest them. Present proposal.

Read `references/endpoints.md` for exact request/response shapes.

## Data model reference

See [references/vikunja-data-model.md](references/vikunja-data-model.md) for the full Vikunja SQLite schema including `projects`, `tasks`, `labels`, `label_tasks`, `task_assignees`, `task_relations`, `task_reminders`, and `users` tables. Use this as a reference when constructing direct SQL queries or interpreting API results.

## Local database

The SQLite database path is stored in `references/vikunja.local.json` under the `sqlitePath` key. Use this for direct SQLite queries when the Vikunja service is unavailable, or when ad-hoc SQL is more convenient than the API (e.g. complex joins, bulk analysis).
