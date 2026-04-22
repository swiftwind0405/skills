#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HERMES_SKILLS_DIR="${HOME}/.hermes/skills"
SKILLS=(
  obsidian-cli
  jenkins-job-trigger
  project-dev-guide
  tdl
  vikunja
)

mkdir -p "$HERMES_SKILLS_DIR"

for skill in "${SKILLS[@]}"; do
  src="$REPO_ROOT/$skill"
  dst="$HERMES_SKILLS_DIR/$skill"

  if [[ ! -d "$src" ]]; then
    echo "skip: missing source directory $src" >&2
    continue
  fi

  if [[ -L "$dst" ]]; then
    current_target="$(readlink "$dst")"
    if [[ "$current_target" == "$src" ]]; then
      echo "ok: $skill already linked"
      continue
    fi
    rm "$dst"
  elif [[ -e "$dst" ]]; then
    backup="$dst.backup-$(date +%Y%m%d-%H%M%S)"
    mv "$dst" "$backup"
    echo "backup: moved existing $dst -> $backup"
  fi

  ln -s "$src" "$dst"
  echo "linked: $dst -> $src"
done

echo "done"
