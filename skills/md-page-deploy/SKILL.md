---
name: md-page-deploy
description: Turn a user-provided Markdown file or pasted Markdown into a readable standalone HTML page, or deploy an existing local HTML page, then preview locally and publish to a static Pages host after explicit user approval. Use when the user asks to publish, deploy, upload, share, or make a readable web page from Markdown or HTML.
---

# Markdown Page Deploy

Create a static, readable HTML page from Markdown, or deploy an existing HTML page, preview it locally, and deploy it only after the user approves the preview.

## Defaults

| Setting       | Default                 | Environment override  |
| ------------- | ----------------------- | --------------------- |
| SSH host      | `vps-dmit`              | `DEPLOY_PAGES_REMOTE` |
| Remote root   | `/srv/pages`            | `DEPLOY_PAGES_ROOT`   |
| Public domain | `pages.stanleywind.org` | `DEPLOY_PAGES_DOMAIN` |
| Remote owner  | `root:root`             | `DEPLOY_PAGES_OWNER`  |

Published pages use:

```text
https://pages.stanleywind.org/<slug>/
```

Set `DEPLOY_PAGES_OWNER=""` to skip remote `chown`.

## Inputs

- Markdown file path, pasted Markdown, HTML file path, deployable HTML directory, or a clear instruction to create Markdown first.
- Optional title, slug, audience, visual style, assets, language, and deployment target.

If the source is not available in the prompt, inspect likely local files first. Ask the user only when the source cannot be discovered.

## Output

Create a deployable folder in the current project:

```text
pages/<slug>/index.html
```

Use a lowercase URL-safe slug from the user request, source frontmatter, first heading, HTML title, directory name, or filename. Allowed slug characters: letters, numbers, dots, underscores, and hyphens.

## Workflow

### 1. Choose the entry path

- If the user provides Markdown or asks to make Markdown readable as a page, use the Markdown generation path below.
- If the user provides a directory that already contains `index.html`, skip generation and use that directory as the deployable folder.
- If the user provides a single `.html` file, skip generation and copy it to `pages/<slug>/index.html` before previewing.
- If the user provides existing HTML, preserve it unless the user explicitly asks for redesign, cleanup, or readability improvements.

### 2. Analyze the Markdown

Before writing HTML, identify:

- Core topic and intended audience.
- Heading hierarchy and section relationships.
- Dense or hard-to-scan parts: long lists, tables, workflows, comparisons, nested logic, code, warnings, appendices.
- Content types: prose, commands, code blocks, tables, checklists, step-by-step instructions, Q&A, callouts.
- Language: Chinese, English, or mixed.

Skip this step for existing HTML input unless the user asks for changes.

### 3. Generate the HTML

Create a complete standalone `index.html` with inline CSS and minimal inline JavaScript only when it improves navigation or comprehension.

Requirements:

- Include `<!doctype html>`, `<html>`, `<head>`, responsive viewport metadata, and `<body>`.
- Use semantic structure: `header`, `main`, `article`, `section`, `nav`, `footer`.
- No remote fonts, analytics, tracking, or CDN dependencies unless the user explicitly asks.
- Mobile-first layout with no text overlap or horizontal body overflow.
- Make the first viewport immediately useful; do not create a marketing landing page unless requested.
- Avoid decorative gradient/orb/bokeh backgrounds and generic visual noise.

Design for comprehension, not ornament:

- Add a table of contents for documents with 3 or more headings.
- Make heading levels visually distinct through size, weight, spacing, and color.
- Use chapter-like spacing for major sections.
- Render tables in responsive scroll containers with readable headers and row separation.
- Render code blocks in a monospace font, horizontally scrollable, with language or filename labels when useful.
- Convert blockquotes or note/warning/tip syntax into clear callout boxes.
- Treat ordered workflows as steps or timelines when it helps readers follow the sequence.
- Use side-by-side panels or cards only for genuinely parallel content such as options, features, or comparisons.
- For long secondary content, use `<details>` for progressive disclosure.

Typography:

- Base font size: 16-18px.
- Body line height: 1.6-1.8 for Latin text, 1.8-2.0 for CJK text.
- Max reading width: 720-840px.
- Use accessible contrast.
- For Chinese or mixed CJK content, prefer `"Noto Sans SC", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif`.

Quality check:

- The HTML must be easier to scan and understand than the source Markdown.
- If the output is only browser-default Markdown with nicer fonts, improve the structure.
- Keep the page simple enough that the user can manually edit it later.

### 4. Validate and preview

Verify:

- `pages/<slug>/index.html` exists.
- The page can be opened as a static file.
- Local links, anchors, tables, code blocks, and responsive layout behave reasonably.

Start a local preview server from the project root:

```bash
python3 -m http.server 8000
```

If port `8000` is busy, use the next available port. Report the preview URL:

```text
http://localhost:<port>/pages/<slug>/
```

### 5. Ask for approval

Do not deploy automatically. Ask the user to review the local preview and explicitly approve publishing.

Approval must be clear, such as "发布", "deploy", "上线", "可以上传", or equivalent.

### 6. Deploy after approval

Resolve this skill directory as `{baseDir}` and run:

```bash
bash {baseDir}/scripts/deploy-pages.sh pages/<slug> [slug]
```

The script validates the directory, `index.html`, slug, SSH access, and uses `rsync --delete` to publish.

After success, report:

```text
https://<domain>/<slug>/
```

## Deployment Notes

- Remote host must be reachable by SSH.
- Remote host must have `rsync`.
- Caddy or another static server must serve `DEPLOY_PAGES_ROOT` at `DEPLOY_PAGES_DOMAIN`.
- `rsync --delete` removes files on the remote slug path that no longer exist locally; this is expected.
- If SSH or rsync fails, report the command failure and suggest checking SSH config, remote permissions, and Caddy root.
