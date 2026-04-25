---
name: url-translate-huntly-save
description: Convert a URL to Markdown, translate it, render translated Markdown to HTML, and save/import the translated HTML into Huntly. Use when the user says they want to translate a URL/article/page/post and collect/save/bookmark/import it into Huntly or their reading library.
---

# URL → Translate → HTML → Huntly

Use this workflow when the user's intent is: **translate a URL and save/collect/import/bookmark it in Huntly**.

Typical triggers:

- “把这个 URL 翻译一下然后收藏”
- “翻译这个链接并导入 Huntly”
- “转成 Markdown、翻译、转 HTML、放到 Huntly”
- “save this translated article to Huntly”

## Required companion skills

Load and follow these skills first:

1. `url-to-markdown` — URL extraction to Markdown
2. `articles-translates` — translation workflow and terminology rules
3. `markdown-to-html` — render translated Markdown to HTML
4. `huntly-manager` — write/import translated HTML into Huntly

## Default assumptions

- Target language: Chinese (`zh-CN`) unless the user specifies otherwise.
- Translation mode: `normal` unless the user asks for quick/精翻/refined.
- Huntly save mode: `my-list` unless the user specifies Archive/collection.
- Use cleaned translated HTML as Huntly `content`, not raw Markdown.
- Preserve the original source URL as the Huntly URL.
- Preserve source metadata where available: title, author, site name, published date, cover image.

## Workflow

### 1. Prepare workspace

Use a per-task temporary directory:

```bash
mkdir -p /tmp/huntly_url_translate_import
```

Prefer a unique subdirectory if multiple imports may run concurrently.

### 2. Extract URL to Markdown

Use the `url-to-markdown` skill.

Resolve runtime:

```bash
command -v bun || command -v npx
```

If only `npx` is available, do **not** run the shell wrapper through `npx -y bun`; the wrapper itself is a shell script that expects a `bun` binary. Instead call the TypeScript CLI directly:

```bash
npx -y bun /Users/stanley/Workspace/main/skills/skills/url-to-markdown/scripts/lib/cli.ts \
  '<URL>' \
  --output /tmp/huntly_url_translate_import/source.md \
  --debug-dir /tmp/huntly_url_translate_import/debug \
  --timeout 60000
```

If `bun` is installed, either direct CLI or the wrapper is fine.

Quality gate:

- Read/inspect `source.md` after extraction.
- Ensure it contains the actual article/post content, not a login page, error page, or empty scaffold.
- If extraction is low quality, retry with `--wait-for interaction` or use a browser-authenticated workflow per `url-to-markdown`.

### 3. Translate Markdown

Use `articles-translates` rules.

For short/medium articles, produce:

- `01-analysis.md`
- `02-prompt.md`
- `translation.md`

For long articles, follow the chunking/subagent workflow from `articles-translates`.

Translation requirements:

- Translate into natural target-language prose, not literal word-by-word output.
- Preserve Markdown structure, links, images, code blocks, and factual meaning.
- Preserve or transform YAML frontmatter carefully:
  - source metadata fields should be renamed to `source*` where appropriate;
  - translated title/summary should be added as top-level translated metadata.

### 4. Render translated Markdown to HTML

Use `markdown-to-html`.

Important pitfall:

- The HTML renderer may misparse YAML frontmatter when values contain characters such as colons (`:`), even if the frontmatter looks quoted.
- To avoid polluted HTML titles/body, create a body-only Markdown file before rendering.

Example:

```python
from pathlib import Path
p = Path('/tmp/huntly_url_translate_import/translation.md')
s = p.read_text(encoding='utf-8')
if s.startswith('---'):
    body = s.split('---', 2)[2].lstrip('\n')
else:
    body = s
Path('/tmp/huntly_url_translate_import/translation-body.md').write_text(body, encoding='utf-8')
```

Then render:

```bash
npx -y bun /Users/stanley/Workspace/main/skills/skills/markdown-to-html/scripts/main.ts \
  /tmp/huntly_url_translate_import/translation-body.md \
  --theme modern \
  --color blue \
  --keep-title \
  --title '<TRANSLATED_TITLE>'
```

Expected output:

```text
/tmp/huntly_url_translate_import/translation-body.html
```

Verify the HTML:

- `<title>` is the translated title, not raw frontmatter.
- The body starts with the translated article, not YAML metadata.
- Images/code blocks are present where expected.

### 5. Save/import translated HTML into Huntly

Use the `huntly-manager` script for writes:

```bash
python3 /Users/stanley/Workspace/main/skills/skills/huntly-manager/scripts/huntly_save_content.py \
  --url '<ORIGINAL_CANONICAL_URL>' \
  --title '<TRANSLATED_TITLE>' \
  --description '<TRANSLATED_SUMMARY_OR_SHORT_DESCRIPTION>' \
  --author '<AUTHOR_IF_AVAILABLE>' \
  --site-name '<SITE_NAME_IF_AVAILABLE>' \
  --content-file /tmp/huntly_url_translate_import/translation-body.html \
  --save-mode my-list
```

If the user specified Archive:

```bash
--save-mode archive
```

If the user specified a Huntly collection, resolve the collection via `huntly-manager` collection commands first, then pass:

```bash
--collection-id <ID>
```

### 6. Verify Huntly import

At minimum, verify the save script returns:

- `ok: true`
- a numeric `page_id`
- requested `save_mode`

If `sqlitePath` is configured in `huntly-manager/references/huntly.local.json`, verify directly:

```bash
sqlite3 '<sqlitePath>' "select id,title,url,library_save_status,length(content) from page where id=<PAGE_ID>;"
```

Expected:

- title matches translated title;
- URL is the original source URL;
- `library_save_status = 1` for My List;
- `length(content)` is non-trivial.

## Final response format

Report concise completion details:

```text
已完成：
- Markdown: <source.md>
- 中文 Markdown: <translation.md>
- HTML: <translation-body.html>
- Huntly page_id: <id>
- 保存位置: My List / Archive / collection <name>
```

If images likely contain source-language text, add:

```text
注意：正文已翻译，原文配图中的文字可能仍是源语言。
```

## Common gotchas

- `url-to-markdown/scripts/baoyu-fetch` may fail when only `npx` is available because the wrapper runs `exec bun ...`; call `scripts/lib/cli.ts` through `npx -y bun` instead.
- Do not ask about Huntly if the user clearly says “收藏/导入 Huntly”; proceed with default `my-list`.
- Do not use Huntly browser UI for writes; use `huntly_save_content.py`.
- For Huntly reads, prefer MCP when native Huntly MCP tools are available; for writes/imports, use REST script.
- Strip frontmatter before HTML rendering if the renderer pollutes output with YAML metadata.
