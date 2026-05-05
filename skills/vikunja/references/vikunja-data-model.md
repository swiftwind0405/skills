# Vikunja Data Model Reference

SQLite database path is configured via the `VIKUNJA_SQLITE_PATH` environment variable.

## Core Tables

### `projects`

| Field               | Description                       |
| ------------------- | --------------------------------- |
| `id`                | Primary key                       |
| `title`             | Project name                      |
| `description`       | Project description               |
| `identifier`        | Short identifier prefix for tasks |
| `is_archived`       | Whether the project is archived   |
| `hex_color`         | Display color                     |
| `parent_project_id` | FK → projects (nesting)           |
| `created`           | Timestamp                         |
| `updated`           | Timestamp                         |

### `tasks`

| Field                       | Description                                         |
| --------------------------- | --------------------------------------------------- |
| `id`                        | Primary key                                         |
| `index`                     | Task number within project                          |
| `title`                     | Task title                                          |
| `description`               | Markdown description                                |
| `done`                      | Boolean: task completed                             |
| `done_at`                   | Timestamp when marked done                          |
| `due_date`                  | Due date (UTC ISO-8601)                             |
| `start_date`                | Start date                                          |
| `end_date`                  | End date                                            |
| `priority`                  | 0=none, 1=low, 2=medium, 3=high, 4=urgent, 5=DO NOW |
| `percent_done`              | Progress 0.0–1.0                                    |
| `hex_color`                 | Display color                                       |
| `project_id`                | FK → projects                                       |
| `repeat_after`              | Repeat interval in seconds                          |
| `repeat_mode`               | Repeat mode                                         |
| `cover_image_attachment_id` | FK → task_attachments                               |
| `is_favorite`               | Boolean                                             |
| `created`                   | Timestamp                                           |
| `updated`                   | Timestamp                                           |
| `created_by_id`             | FK → users                                          |

### `labels`

| Field       | Description   |
| ----------- | ------------- |
| `id`        | Primary key   |
| `title`     | Label name    |
| `hex_color` | Display color |
| `created`   | Timestamp     |
| `updated`   | Timestamp     |

### `label_tasks`

| Field      | Description |
| ---------- | ----------- |
| `id`       | Primary key |
| `task_id`  | FK → tasks  |
| `label_id` | FK → labels |

### `task_assignees`

| Field     | Description |
| --------- | ----------- |
| `task_id` | FK → tasks  |
| `user_id` | FK → users  |

### `task_relations`

| Field           | Description                                                                                                                          |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `task_id`       | FK → tasks                                                                                                                           |
| `other_task_id` | FK → tasks                                                                                                                           |
| `relation_kind` | precedes, follows, related, duplicates, duplicated_by, blocked_by, blocking, caused_by, copied_from, copied_to, parent_task, subtask |
| `created_by_id` | FK → users                                                                                                                           |
| `created`       | Timestamp                                                                                                                            |

### `task_reminders`

| Field             | Description                                     |
| ----------------- | ----------------------------------------------- |
| `task_id`         | FK → tasks                                      |
| `reminder`        | Absolute datetime (UTC)                         |
| `relative_to`     | Reference field: due_date, start_date, end_date |
| `relative_period` | Offset in seconds (negative = before)           |

### `users`

| Field      | Description   |
| ---------- | ------------- |
| `id`       | Primary key   |
| `username` | Login name    |
| `email`    | Email address |
| `name`     | Display name  |

## Useful Queries

### List projects

```sql
SELECT id, title, is_archived FROM projects ORDER BY id;
```

### List tasks in a project

```sql
SELECT t.id, t."index", t.title, t.done, t.priority, t.due_date
FROM tasks t
WHERE t.project_id = ?
ORDER BY t.done ASC, t."index" ASC, t.id ASC;
```

### Labels for a task

```sql
SELECT l.title
FROM labels l
JOIN label_tasks lt ON l.id = lt.label_id
WHERE lt.task_id = ?
ORDER BY l.title;
```

### Undone tasks due today or overdue

```sql
SELECT t.id, t."index", t.title, t.priority, t.due_date, p.title AS project
FROM tasks t
JOIN projects p ON t.project_id = p.id
WHERE t.done = 0
  AND t.due_date <= datetime('now', '+1 day', 'start of day')
  AND t.due_date != ''
ORDER BY t.due_date ASC, t.priority DESC;
```

### Tasks with assignees

```sql
SELECT t.id, t.title, u.username
FROM tasks t
JOIN task_assignees ta ON t.id = ta.task_id
JOIN users u ON ta.user_id = u.id
WHERE t.project_id = ?
ORDER BY t."index";
```
