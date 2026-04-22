# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

`AGENTS.md` and `GEMINI.md` are symlinks to this file. Edit `CLAUDE.md` only.

## Project Overview

Curated set of custom Agent Skills for local engineering workflows.

- Skills live in [`skills/`](./skills), one folder per skill.
- Each skill is Markdown-first, centered on required `SKILL.md`.
- Supporting assets stay bundled with owning skill in `references/` or `scripts/`.

## Repository Layout

```text
skills/
  <skill-name>/
    SKILL.md
    references/   # optional
    scripts/      # optional
```

Keep aligned when relevant:

- [`README.md`](./README.md)
- [`README.zh.md`](./README.zh.md)
- [`package.json`](./package.json)
- [`.github/workflows/markdown.yml`](./.github/workflows/markdown.yml)
- [`.github/workflows/markdown-fix.yml`](./.github/workflows/markdown-fix.yml)

## Commands

```bash
bun run check:md    # validate Markdown formatting
bun run format:md   # auto-fix Markdown formatting
```

No unit tests. Primary validation = structure review + Markdown formatting.

## SKILL.md Format

Each `SKILL.md` starts with YAML frontmatter:

```yaml
---
name: <skill-name>
description: <what it does and when to use it>
---
```

Body: execution-oriented instructions. Prefer imperative steps over background explanation.

## Workflow

When adding or editing a skill:

1. Work inside `skills/<skill-name>/`.
2. Keep main instructions in `SKILL.md`.
3. Put large supporting docs in `references/`.
4. Put reusable helpers in skill's `scripts/`.
5. Update [`README.md`](./README.md) and [`README.zh.md`](./README.zh.md) if public catalog changes.
6. Run `bun run check:md` before finishing. If fails, run `bun run format:md` then re-check.

## Conventions

- Follow [`.editorconfig`](./.editorconfig): UTF-8, LF, spaces, width 2.
- Markdown formatting governed by [`.prettierrc.json`](./.prettierrc.json).
- Prefer clear execution-oriented instructions over long background.
- Use relative repo links for in-repo files.
- Avoid repo-wide tooling unless maintenance burden justified.
