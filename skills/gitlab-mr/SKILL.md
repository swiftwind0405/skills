---
name: gitlab-mr
description: Operate on GitLab merge requests via glab CLI — create, merge, approve, list, view, close, and comment. Use when the user asks to manage GitLab MRs on a private or self-hosted GitLab instance.
---

# GitLab MR Operations

Use the `glab` CLI to operate on GitLab merge requests. All commands run directly via Bash — no wrapper script needed.

## Pre-flight: Auth

Before any MR operation, verify `glab` is authenticated. If not, guide the user:

```bash
glab auth login --hostname gitlab.example.com
```

Check current auth status:

```bash
glab auth status
```

## Core MR Commands

All commands accept `<id>` (MR number) or `<branch>` (source branch name). Use `-R` to target a different repo.

### List MRs

```bash
# Open MRs in current repo
glab mr list

# All MRs (including closed/merged)
glab mr list --all

# MRs assigned to me
glab mr list --assignee @me

# With search filter
glab mr list --search "keyword"
```

### View MR details

```bash
glab mr view <id|branch>

# Open in browser
glab mr view <id|branch> --web
```

### Create MR

```bash
# Interactive (prompts for title, description, etc.)
glab mr create

# Quick create — auto-fill from commit messages, push branch, and don't prompt
glab mr create --fill --yes

# With explicit title, description, labels, assignee
glab mr create \
  --title "fix: resolve timeout issue" \
  --description "Closes #42. Root cause: ..." \
  --label "bug,backend" \
  --assignee @me

# Draft MR
glab mr create --draft --title "WIP: refactor auth"

# From a specific branch to a specific target
glab mr create --source-branch feature/x --target-branch main

# Auto-merge when checks pass
glab mr create --fill --auto-merge
```

### Approve MR

```bash
glab mr approve <id|branch>
```

### Merge MR

```bash
# Merge when pipeline passes
glab mr merge <id|branch>

# Merge immediately (skip pipeline)
glab mr merge <id|branch> --immediate

# Squash merge
glab mr merge <id|branch> --squash

# Delete source branch after merge
glab mr merge <id|branch> --remove-source-branch
```

### Close / Reopen MR

```bash
glab mr close <id|branch>
glab mr reopen <id|branch>
```

### Add a comment

```bash
glab mr note <id|branch> -m "LGTM, let's ship this"
```

### View MR diff

```bash
glab mr diff <id|branch>
```

### Check out MR locally

```bash
glab mr checkout <id|branch>
```

## Targeting a specific repo

When working outside a Git repo or targeting a different project:

```bash
# By owner/repo
glab mr list -R group/subgroup/repo

# By full URL
glab mr list -R https://gitlab.example.com/group/repo
```

## Notes

- `glab` respects the Git remote of the current directory. If you're inside a cloned repo, `-R` is usually unnecessary.
- For self-hosted GitLab, use `glab auth login --hostname <your-instance>` to point at the right server.
- The CLI caches auth tokens and repo context — no need to re-auth every command.
- Pipeline status is shown inline in `mr view` output.
- Use `glab mr update <id>` to edit title, description, labels, assignees, etc. post-creation.
