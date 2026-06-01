#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: deploy-pages.sh <local_dir> [slug]

Environment:
  DEPLOY_PAGES_REMOTE   SSH host, default: vps-dmit
  DEPLOY_PAGES_ROOT     Remote root, default: /srv/pages
  DEPLOY_PAGES_DOMAIN   Public domain, default: pages.stanleywind.org
  DEPLOY_PAGES_OWNER    Remote owner, default: root:root. Set empty to skip chown.
  DEPLOY_PAGES_UPDATE_INDEX
                       Update the root page directory after deploy, default: 1.
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -lt 1 || $# -gt 2 ]]; then
  usage >&2
  exit 2
fi

local_dir="${1%/}"
slug="${2:-$(basename "$local_dir")}"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

remote="${DEPLOY_PAGES_REMOTE:-vps-dmit}"
root="${DEPLOY_PAGES_ROOT:-/srv/pages}"
domain="${DEPLOY_PAGES_DOMAIN:-pages.stanleywind.org}"
owner="${DEPLOY_PAGES_OWNER-root:root}"
update_index="${DEPLOY_PAGES_UPDATE_INDEX:-1}"

if [[ ! -d "$local_dir" ]]; then
  echo "Local directory does not exist: $local_dir" >&2
  exit 1
fi

if [[ ! -f "$local_dir/index.html" ]]; then
  echo "Missing index.html in: $local_dir" >&2
  exit 1
fi

if [[ ! "$slug" =~ ^[A-Za-z0-9._-]+$ ]]; then
  echo "Invalid slug: $slug" >&2
  echo "Allowed characters: letters, numbers, dots, underscores, hyphens" >&2
  exit 1
fi

remote_dir="$root/$slug"

ssh "$remote" install -d -m 0755 "$remote_dir"
rsync -rltz --delete --chmod=Du=rwx,Dgo=rx,Fu=rw,Fgo=r --stats "$local_dir"/ "$remote:$remote_dir/"

if [[ -n "$owner" ]]; then
  ssh "$remote" chown -R "$owner" "$remote_dir"
fi

echo "Published: https://$domain/$slug/"

if [[ "$update_index" != "0" ]]; then
  DEPLOY_PAGES_REMOTE="$remote" \
    DEPLOY_PAGES_ROOT="$root" \
    DEPLOY_PAGES_DOMAIN="$domain" \
    DEPLOY_PAGES_OWNER="$owner" \
    "$script_dir/update-pages-index.sh"
fi
