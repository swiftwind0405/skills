#!/usr/bin/env bash
set -euo pipefail

# Determine script directories
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_ROOT="$REPO_ROOT/skills"

# 1. Dynamically scan the skills directory
SKILLS=()
if [[ -d "$SKILLS_ROOT" ]]; then
  while IFS= read -r -d $'\0' dir; do
    base="$(basename "$dir")"
    # Skip hidden directories
    if [[ "$base" != .* ]]; then
      SKILLS+=("$base")
    fi
  done < <(find "$SKILLS_ROOT" -maxdepth 1 -mindepth 1 -type d -print0 | sort -z)
fi

if [[ ${#SKILLS[@]} -eq 0 ]]; then
  echo -e "\033[31mError: No skills found in $SKILLS_ROOT\033[0m" >&2
  exit 1
fi

# 2. Target Directory Selection
if [[ -t 0 ]]; then
  echo "=== Select Target Directory for Symlinking ==="
  echo "1) Universal Agent Skills (~/.agents/skills) [Default]"
  echo "2) Claude Code Global     (~/.claude/skills)"
  echo "3) Claude Code Project    (./.claude/skills)"
  echo "4) Custom Path..."
  echo "----------------------------------------------"
  read -rp "Enter choice [1-4] (default: 1): " target_choice

  case "$target_choice" in
    2)
      target_dir="${HOME}/.claude/skills"
      ;;
    3)
      target_dir="${REPO_ROOT}/.claude/skills"
      ;;
    4)
      read -rp "Enter custom target path: " custom_path
      # Tilde expansion
      target_dir="${custom_path/#\~/$HOME}"
      ;;
    *)
      target_dir="${HOME}/.agents/skills"
      ;;
  esac
else
  # Non-interactive fallback
  target_dir="${HOME}/.agents/skills"
fi

# Ensure target directory is fully resolved absolute path
mkdir -p "$target_dir"
target_dir="$(cd "$target_dir" && pwd)"
echo -e "\nTarget directory: \033[34m$target_dir\033[0m"

# 3. Interactive Skill Selection
SELECTED=()
for i in "${!SKILLS[@]}"; do
  SELECTED[$i]=1 # default to selected
done

if [[ -t 0 ]]; then
  while true; do
    echo ""
    echo "=== Select Skills to Symlink ==="
    for i in "${!SKILLS[@]}"; do
      if [[ ${SELECTED[$i]} -eq 1 ]]; then
        printf "  %2d) [\033[32mx\033[0m] %s\n" $((i+1)) "${SKILLS[$i]}"
      else
        printf "  %2d) [ ] %s\n" $((i+1)) "${SKILLS[$i]}"
      fi
    done
    echo "--------------------------------"
    echo "Options:"
    echo "  - Enter numbers separated by spaces to toggle (e.g., '1 3 5')"
    echo "  - Type 'all' to select all, 'none' to clear all"
    echo "  - Press ENTER to confirm and continue"
    echo ""
    read -rp "Selection: " input

    # Clean input whitespace
    input="$(echo "$input" | xargs || echo "$input")"

    if [[ -z "$input" ]]; then
      break
    fi

    if [[ "$input" == "all" ]]; then
      for i in "${!SKILLS[@]}"; do
        SELECTED[$i]=1
      done
      continue
    fi

    if [[ "$input" == "none" ]]; then
      for i in "${!SKILLS[@]}"; do
        SELECTED[$i]=0
      done
      continue
    fi

    # Toggle selected indices
    read -r -a choices <<< "$input"
    for choice in "${choices[@]}"; do
      if [[ "$choice" =~ ^[0-9]+$ ]] && (( choice >= 1 && choice <= ${#SKILLS[@]} )); then
        idx=$((choice - 1))
        if [[ ${SELECTED[$idx]} -eq 1 ]]; then
          SELECTED[$idx]=0
        else
          SELECTED[$idx]=1
        fi
      else
        echo -e "\033[31mInvalid choice: $choice\033[0m"
      fi
    done
  done
fi

# Check if any skill was selected
has_selected=0
for val in "${SELECTED[@]}"; do
  if [[ "$val" -eq 1 ]]; then
    has_selected=1
    break
  fi
done

if [[ "$has_selected" -eq 0 ]]; then
  echo "No skills selected. Exiting without changes."
  exit 0
fi

# 4. Perform Symlinking
echo -e "\n=== Creating Symlinks ==="
for i in "${!SKILLS[@]}"; do
  if [[ ${SELECTED[$i]} -ne 1 ]]; then
    continue
  fi

  skill="${SKILLS[$i]}"
  src="$SKILLS_ROOT/$skill"
  dst="$target_dir/$skill"

  if [[ ! -d "$src" ]]; then
    echo -e "\033[33mskip\033[0m: missing source directory $src" >&2
    continue
  fi

  if [[ -L "$dst" ]]; then
    current_target="$(readlink "$dst")"
    if [[ "$current_target" == "$src" ]]; then
      echo -e "\033[32mok\033[0m: $skill already correctly linked"
      continue
    fi
    echo -e "\033[33mre-link\033[0m: removing existing symlink pointing to $current_target"
    rm "$dst"
  elif [[ -e "$dst" ]]; then
    backup="$dst.backup-$(date +%Y%m%d-%H%M%S)"
    mv "$dst" "$backup"
    echo -e "\033[33mbackup\033[0m: moved existing non-symlink item at $dst to $backup"
  fi

  ln -s "$src" "$dst"
  echo -e "\033[32mlinked\033[0m: $skill -> $dst"
done

echo -e "\n\033[32mAll symlinks processed successfully!\033[0m"

