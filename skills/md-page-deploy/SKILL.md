---
name: md-page-deploy
description: Turn a user-provided Markdown file or pasted Markdown into a readable standalone HTML page, or deploy an existing local HTML page, then preview locally and publish to a static Pages host after explicit user approval. Use when the user asks to publish, deploy, upload, share, or make a readable web page from Markdown or HTML.
---

# Markdown Page Deploy

Create a static, readable HTML page from Markdown, or deploy an existing HTML page, preview it locally, and deploy it only after the user approves the preview.

Default production hosting is Cloudflare Pages with GitHub integration from the standalone docs repository. The legacy VPS/Caddy rsync path remains available only when explicitly requested.

## Defaults

| Setting             | Default                                            | Environment override       |
| ------------------- | -------------------------------------------------- | -------------------------- |
| Docs repo path      | `/Users/stanley/Workspace/main/stanley-docs-pages` | `DEPLOY_PAGES_REPO`        |
| GitHub repo         | `swiftwind0405/stanley-docs-pages`                 | `DEPLOY_PAGES_GITHUB_REPO` |
| Source directory    | `pages`                                            | `DEPLOY_PAGES_SOURCE`      |
| Build directory     | `.deploy/cloudflare-pages`                         | `DEPLOY_PAGES_BUILD_DIR`   |
| Public domain       | `docs.stanleywind.org`                             | `DEPLOY_PAGES_DOMAIN`      |
| Cloudflare project  | `stanley-docs-github`                              | `DEPLOY_PAGES_CF_PROJECT`  |
| Legacy SSH host     | `vps-dmit`                                         | `DEPLOY_PAGES_REMOTE`      |
| Legacy remote root  | `/srv/pages`                                       | `DEPLOY_PAGES_ROOT`        |
| Legacy remote owner | `root:root`                                        | `DEPLOY_PAGES_OWNER`       |

Published pages use:

```text
https://docs.stanleywind.org/<slug>/
```

For the legacy rsync path, set `DEPLOY_PAGES_OWNER=""` to skip remote `chown`.

## Inputs

- Markdown file path, pasted Markdown, HTML file path, deployable HTML directory, or a clear instruction to create Markdown first.
- Optional title, slug, audience, visual style, assets, language, and deployment target.

If the source is not available in the prompt, inspect likely local files first. Ask the user only when the source cannot be discovered.

## Output

Create a deployable folder in the docs repository:

```text
<docs-repo>/pages/<slug>/index.html
```

Use a lowercase URL-safe slug from the user request, source frontmatter, first heading, HTML title, directory name, or filename. Allowed slug characters: letters, numbers, dots, underscores, and hyphens.

## Workflow

### 1. Choose the entry path

- If the user provides Markdown or asks to make Markdown readable as a page, use the Markdown generation path below.
- If the user provides a directory that already contains `index.html`, skip generation and use that directory as the deployable folder.
- If the user provides a single `.html` file, skip generation and copy it to `<docs-repo>/pages/<slug>/index.html` before previewing.
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

- `<docs-repo>/pages/<slug>/index.html` exists.
- `bash scripts/build-cloudflare-pages.sh` succeeds from the docs repo root.
- The page can be opened as a static file.
- Local links, anchors, tables, code blocks, and responsive layout behave reasonably.

Start a local preview server from the docs repo root:

```bash
python3 -m http.server 8000
```

If port `8000` is busy, use the next available port. Report the page preview URL:

```text
http://localhost:<port>/pages/<slug>/
```

Also report the generated directory preview when useful:

```text
http://localhost:<port>/.deploy/cloudflare-pages/
```

### 5. Ask for approval

Do not deploy automatically. Ask the user to review the local preview and explicitly approve publishing.

Approval must be clear, such as "发布", "deploy", "上线", "可以上传", or equivalent.

### 6. Deploy after approval

Default deployment is GitHub-driven Cloudflare Pages:

1. Build the Cloudflare Pages output directory.

   ```bash
   cd /Users/stanley/Workspace/main/stanley-docs-pages
   bash scripts/build-cloudflare-pages.sh
   ```

2. Commit the changed `pages/`, scripts, and docs in the docs repo.
3. Push the configured production branch to GitHub.
4. Let Cloudflare Pages build from GitHub using:

   ```bash
   bash scripts/build-cloudflare-pages.sh
   ```

   with output directory:

   ```text
   .deploy/cloudflare-pages
   ```

5. Verify:

   ```bash
   curl -I https://docs.stanleywind.org/
   curl -I https://docs.stanleywind.org/<slug>/
   ```

After success, report:

```text
https://docs.stanleywind.org/<slug>/
```

### 7. Legacy VPS Deploy

Use this only when the user explicitly asks for the existing VPS/Caddy host.

Resolve this skill directory as `{baseDir}` and run:

```bash
bash {baseDir}/scripts/deploy-pages.sh pages/<slug> [slug]
```

The script validates the directory, `index.html`, slug, SSH access, uses `rsync --delete` to publish, and updates the legacy root directory index.

After success, report:

```text
https://<domain>/<slug>/
```

## Deployment Notes

- Cloudflare Pages GitHub integration deploys the whole build output as one immutable deployment.
- A single changed HTML file still creates a new deployment, but unchanged assets are reused by Cloudflare internally.
- The root directory page is generated during build from all `pages/*/index.html` folders in the docs repo.
- Do not manually edit `.deploy/cloudflare-pages`; it is generated output.
- Remote host must be reachable by SSH for legacy deployment.
- Remote host must have `rsync` for legacy deployment.
- Caddy or another static server must serve `DEPLOY_PAGES_ROOT` at `DEPLOY_PAGES_DOMAIN` for legacy deployment.
- `rsync --delete` removes files on the remote slug path that no longer exist locally; this is expected.
- If SSH or rsync fails, report the command failure and suggest checking SSH config, remote permissions, and Caddy root.
