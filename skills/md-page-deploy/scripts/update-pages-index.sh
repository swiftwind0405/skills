#!/usr/bin/env bash
set -euo pipefail

remote="${DEPLOY_PAGES_REMOTE:-vps-dmit}"
root="${DEPLOY_PAGES_ROOT:-/srv/pages}"
domain="${DEPLOY_PAGES_DOMAIN:-pages.stanleywind.org}"
owner="${DEPLOY_PAGES_OWNER-root:root}"

remote_root_q="$(printf '%q' "$root")"
slugs=()
while IFS= read -r slug; do
  slugs+=("$slug")
done < <(ssh "$remote" "root=$remote_root_q; for d in \"\$root\"/*; do [ -d \"\$d\" ] && [ -f \"\$d/index.html\" ] && basename \"\$d\"; done | sort")

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

{
  cat <<HTML
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Pages Directory</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f7f7f4;
      --paper: #ffffff;
      --ink: #202124;
      --muted: #667085;
      --line: #d9ddd3;
      --accent: #176b72;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      line-height: 1.6;
    }

    main {
      max-width: 1040px;
      margin: 0 auto;
      padding: 48px 24px 72px;
    }

    header { margin-bottom: 28px; }

    h1 {
      margin: 0 0 8px;
      font-size: clamp(34px, 7vw, 64px);
      line-height: 1;
      letter-spacing: 0;
    }

    p {
      margin: 0;
      color: var(--muted);
      font-size: 17px;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
      gap: 14px;
    }

    a.card {
      display: block;
      min-height: 104px;
      padding: 18px;
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 8px;
      color: inherit;
      text-decoration: none;
      transition: border-color 140ms ease, transform 140ms ease;
    }

    a.card:hover {
      border-color: var(--accent);
      transform: translateY(-1px);
    }

    .name {
      display: block;
      margin-bottom: 8px;
      color: var(--accent);
      font-size: 19px;
      font-weight: 700;
      overflow-wrap: anywhere;
    }

    .url {
      display: block;
      color: var(--muted);
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 13px;
      overflow-wrap: anywhere;
    }

    footer {
      margin-top: 28px;
      color: var(--muted);
      font-size: 14px;
    }
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Pages Directory</h1>
      <p>Published static pages on ${domain}.</p>
    </header>

    <section class="grid" aria-label="Published pages">
HTML

  for slug in "${slugs[@]}"; do
    printf '      <a class="card" href="/%s/"><span class="name">%s</span><span class="url">/%s/</span></a>\n' "$slug" "$slug" "$slug"
  done

  cat <<HTML
    </section>

    <footer>Generated from ${root}.</footer>
  </main>
</body>
</html>
HTML
} > "$tmp"

rsync -ltz --chmod=Fu=rw,Fgo=r "$tmp" "$remote:$root/index.html"

if [[ -n "$owner" ]]; then
  ssh "$remote" chown "$owner" "$root/index.html"
fi

echo "Updated directory: https://$domain/"
