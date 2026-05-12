---
name: url-translate-html
description: Convert a URL to Markdown, produce bilingual original/Chinese Markdown in a vertical comparison format, and render it to styled HTML. Use when the user says "翻译这个链接", "translate this URL/article/page", "URL 转双语 HTML", or needs a bilingual HTML from a web page.
---

# URL → Translate → HTML

Use this workflow when the user's intent is: **translate a URL/article/page into bilingual Markdown and render it to HTML**.

Typical triggers:

- "翻译这个链接 / translate this URL"
- "把这个 URL 转成双语 HTML"
- "translate this article and render HTML"
- "URL 转 Markdown、翻译、转 HTML"

## Required companion skills

Load and follow these skills first:

1. `url-to-markdown` — URL extraction to Markdown
2. `articles-translates` — translation workflow and terminology rules
3. `markdown-to-html` — render translated Markdown to HTML

## Default assumptions

- Target language: Chinese (`zh-CN`) unless the user specifies otherwise.
- Output form: **bilingual original + Chinese translation**, using vertical comparison ("上下对照"), not translation-only.
- Translation mode: `normal` unless the user asks for quick/精翻/refined.
- Preserve source metadata where available: title, author, site name, published date, cover image.

## Workflow

### 1. Prepare workspace

Use a per-task temporary directory:

```bash
mkdir -p /tmp/url_translate_html
```

Prefer a unique subdirectory if multiple tasks may run concurrently.

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
  --output /tmp/url_translate_html/source.md \
  --debug-dir /tmp/url_translate_html/debug \
  --timeout 60000
```

If `bun` is installed, either direct CLI or the wrapper is fine.

Quality gate:

- Read/inspect `source.md` after extraction.
- Ensure it contains the actual article/post content, not a login page, error page, or empty scaffold.
- If extraction is low quality, retry with `--wait-for interaction` or use a browser-authenticated workflow per `url-to-markdown`.

### 3. Produce bilingual Markdown

Use `articles-translates` rules, but **override the final output format**: this workflow must produce a bilingual original/Chinese Markdown document, not translation-only Markdown.

For short/medium articles, produce:

- `01-analysis.md`
- `02-prompt.md`
- `translation.md` — bilingual vertical comparison Markdown

For long articles, follow the chunking/subagent workflow from `articles-translates`, but each chunk must preserve source blocks and append Chinese translations block-by-block.

Practical long-X-article shortcut:

- If `source.md` is medium/long but still a single coherent X article/thread, a single `delegate_task` with `file`/`terminal` toolsets can efficiently produce `01-analysis.md`, `02-prompt.md`, and `translation.md` in the same workspace without flooding the main context.
- The subagent prompt must be explicit that the output is **bilingual vertical comparison**, not translation-only, and that it must not render HTML.
- After the subagent returns, verify `translation.md` before rendering: check that the original title/major headings remain, Chinese translations appear as blockquotes immediately after them, frontmatter is clean, and the file is substantially larger than the source. Fix formatting issues before HTML conversion.

Bilingual output requirements:

1. Preserve the original Markdown hierarchy and structure, including headings, lists, blockquotes, code blocks, tables, links, images, footnotes, alerts, and other Markdown constructs.
2. For every translatable heading, paragraph, blockquote line, and list item, show the original first, then the Chinese translation immediately after it.
3. Use vertical comparison ("上下对照") format:

   ```markdown
   ## Original heading

   > 中文标题

   Original paragraph.

   > 中文译文段落。

   - Original list item
     > 中文列表项
   ```

4. Do **not** translate code block contents. Keep fenced code blocks exactly as source, including language labels and indentation. Translate only prose before/after the code block.
5. Do not translate URLs, image URLs, file paths, commands, variable names, function names, API names, package names, model names, or identifiers.
6. For proper nouns and technical terms, keep the English term when useful; on first occurrence, optionally add a Chinese explanation, e.g. `middleware（中间件）`.
7. Output must remain valid Markdown.
8. Preserve source layout as much as possible. Do not restructure, summarize, omit, merge, or delete content.
9. Translation style: accurate, natural, and suitable for technical-document reading.

Markdown element handling:

- **Headings**: keep the original heading as the actual heading; put the Chinese heading as a blockquote immediately below.
- **Paragraphs**: keep original paragraph, blank line, then Chinese translation as a blockquote.
- **Lists**: keep each original list item; place a nested blockquote translation directly under that same item. Preserve nesting.
- **Blockquotes**: preserve original blockquote syntax and add translated blockquote content immediately after, using a clear nested/adjacent quote while keeping valid Markdown.
- **Tables**: preserve table structure where possible. Prefer adding "原文 / 译文" inside each relevant cell, or if the table becomes unreadable, duplicate the table as original table followed by translated table with the same columns.
- **Images**: keep original image Markdown unchanged. If an image has alt text, add a translated alt-text note below only if useful; never rewrite the image URL.
- **Links**: translate visible link text when it is prose, but keep the URL unchanged.
- **Footnotes**: preserve footnote IDs and links; add translations next to the footnote text without changing references.
- **HTML blocks**: preserve raw HTML unless it contains visible prose that can be safely translated without breaking markup.

Frontmatter handling:

- Preserve or transform YAML frontmatter carefully:
  - source metadata fields should be renamed to `source*` where appropriate;
  - translated title/summary may be added as top-level translated metadata;
  - the body must still contain bilingual title/content in the vertical comparison format.

### 4. Render translated Markdown to HTML

Use `markdown-to-html`.

Important pitfall:

- The HTML renderer may misparse YAML frontmatter when values contain characters such as colons (`:`), even if the frontmatter looks quoted.
- To avoid polluted HTML titles/body, create a body-only Markdown file before rendering.

Example:

```python
from pathlib import Path
p = Path('/tmp/url_translate_html/translation.md')
s = p.read_text(encoding='utf-8')
if s.startswith('---'):
    body = s.split('---', 2)[2].lstrip('\n')
else:
    body = s
Path('/tmp/url_translate_html/translation-body.md').write_text(body, encoding='utf-8')
```

Then render:

```bash
npx -y bun /Users/stanley/Workspace/main/skills/skills/markdown-to-html/scripts/main.ts \
  /tmp/url_translate_html/translation-body.md \
  --theme modern \
  --color blue \
  --keep-title \
  --title '<ORIGINAL_TITLE> / <TRANSLATED_TITLE>'
```

Expected output:

```text
/tmp/url_translate_html/translation-body.html
```

Verify the HTML:

- `<title>` is a clean title (prefer `<original title> / <Chinese title>`), not raw frontmatter.
- The body starts with the bilingual article, not YAML metadata.
- Original text appears before Chinese blockquote translations throughout.
- Images/code blocks are present where expected; code block contents remain unchanged.

Renderer fallback for remote-image TLS failures:

- If `markdown-to-html` fails while downloading remote images with errors such as `unknown certificate verification error`, retry once with the same command and `NODE_TLS_REJECT_UNAUTHORIZED=0`.
- If Bun/Node still fails, do not block the capture. Render a self-contained/simple HTML file with Python Markdown in a temporary venv, preserving remote image URLs instead of downloading them:

  ```bash
  python3 -m venv /tmp/url_translate_html/venv
  /tmp/url_translate_html/venv/bin/pip install markdown pygments
  /tmp/url_translate_html/venv/bin/python - <<'PY'
  from pathlib import Path
  import html, markdown
  work = Path('/tmp/url_translate_html')
  md_path = work / 'translation-body.md'
  body = md_path.read_text(encoding='utf-8')
  html_body = markdown.markdown(
      body,
      extensions=['extra', 'sane_lists', 'fenced_code', 'codehilite', 'tables'],
  )
  title = '<ORIGINAL_TITLE> / <TRANSLATED_TITLE>'
  css = 'body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans SC",Arial,sans-serif;line-height:1.75;max-width:860px;margin:0 auto;padding:32px 20px}blockquote{border-left:4px solid #0F4C81;background:#f0f7ff;padding:.7em 1em;border-radius:8px}img{max-width:100%;height:auto;border-radius:12px}pre{overflow:auto}'
  out = f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>{css}</style></head><body>{html_body}</body></html>'
  (work / 'translation-body.html').write_text(out, encoding='utf-8')
  PY
  ```

- Verify the fallback HTML by checking file size and that representative original and Chinese strings both occur in the file.

## Final response format

Report concise completion details:

```text
已完成：
- 原文 Markdown: <source.md>
- 双语 Markdown: <translation.md>
- 双语 HTML: <translation-body.html>
```

If images likely contain source-language text, add:

```text
注意：正文已按原文/中文上下对照输出；原文配图中的文字可能仍是源语言。
```

## Common gotchas

- `url-to-markdown/scripts/baoyu-fetch` may fail when only `npx` is available because the wrapper runs `exec bun ...`; call `scripts/lib/cli.ts` through `npx -y bun` instead.
- Do not produce translation-only Markdown for this workflow; the default required output is bilingual vertical comparison.
- Strip frontmatter before HTML rendering if the renderer pollutes output with YAML metadata.
