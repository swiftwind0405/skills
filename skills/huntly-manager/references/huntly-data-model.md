# Huntly Data Model Reference

SQLite database path is configured in `huntly.local.json` (`sqlitePath` field).

Derived from the official [huntly-knowledge-base](https://github.com/lcomplete/huntly/blob/main/skills/huntly-knowledge-base/SKILL.md) skill.

## Core Rule: Library Content First

By default, query **Library content** (user actively saved), not auto-collected content.

**Library Filter:**

```sql
WHERE library_save_status IN (1, 2)
```

| Type       | Condition                 | Order By        |
| ---------- | ------------------------- | --------------- |
| My List    | `library_save_status = 1` | `saved_at`      |
| Archive    | `library_save_status = 2` | `archived_at`   |
| Starred    | `is_starred = 1`          | `starred_at`    |
| Read Later | `is_read_later = 1`       | `read_later_at` |

## Main Table: `page`

| Field                                                                  | Description                                               |
| ---------------------------------------------------------------------- | --------------------------------------------------------- |
| `id`, `title`, `url`                                                   | Basic identifiers                                         |
| `description`, `content`                                               | Text content (content is HTML)                            |
| `author`, `author_screen_name`                                         | Author info                                               |
| `domain`, `site_name`                                                  | Source website info                                       |
| `thumb_url`                                                            | Thumbnail image URL                                       |
| `library_save_status`                                                  | 0/NULL=unsaved, 1=My List, 2=Archive                      |
| `is_starred`, `is_read_later`, `is_mark_read`                          | Boolean flags                                             |
| `connector_type`                                                       | NULL=web, 1=RSS, 2=GitHub                                 |
| `connector_id`                                                         | FK → connector                                            |
| `content_type`                                                         | 0=history, 1=tweet, 2=markdown, 3=quoted tweet, 4=snippet |
| `collection_id`                                                        | FK → collection                                           |
| `created_at`, `saved_at`, `starred_at`, `archived_at`, `read_later_at` | Timestamps                                                |
| `highlight_count`                                                      | Statistics                                                |
| `page_json_properties`                                                 | JSON string with extra data (see below)                   |

## `page_json_properties` Field

JSON string containing type-specific metadata:

### For tweets (`content_type=1`): `TweetProperties`

- `tweetIdStr`, `userIdStr`, `userName`, `userScreeName`, `userProfileImageUrl`
- `fullText`, `createdAt`
- `quoteCount`, `replyCount`, `retweetCount`, `favoriteCount`, `viewCount`
- `medias[]` (mediaUrl, type, videoInfo), `hashtags[]`, `urls[]`, `userMentions[]`
- `quotedTweet`, `retweetedTweet` (nested TweetProperties)
- `card` (title, description, imageUrl, url, domain)

### For GitHub repos (`connector_type=2`): `GithubRepoProperties`

- `name`, `nodeId`, `defaultBranch`, `homepage`
- `stargazersCount`, `forksCount`, `watchersCount`
- `topics[]`, `updatedAt`

## Related Tables

- **`page_highlight`**: `page_id`, `highlighted_text`, `created_at`
- **`connector`**: `id`, `name`, `type` (1=RSS, 2=GitHub), `subscribe_url`, `folder_id`
- **`collection`**: `id`, `name`, `parent_id`
- **`folder`**: `id`, `name` (RSS folder organization)
