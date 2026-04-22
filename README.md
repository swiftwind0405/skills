# Agent Skills

[简体中文](./README.zh.md)

This repository maintains a small set of custom Agent Skills for practical local workflows.

## How To Use

You can use this repository in two ways:

1. Add it directly as a skill source with `bunx skills add` or `npx skills add`.
2. Symlink the local skill folders into `~/.hermes/skills/` with [`scripts/link-skills.sh`](./scripts/link-skills.sh).

Install this repository as a skill source:

```bash
bunx skills add https://github.com/swiftwind0405/skills
```

or:

```bash
npx skills add https://github.com/swiftwind0405/skills
```

## Skills Catalog

The table below lists the skills maintained in this repository.

| Name                                                           | Description                                                                                                     | Bundled Assets            |
| -------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------- |
| [`jenkins-job-trigger`](./skills/jenkins-job-trigger/SKILL.md) | Trigger Jenkins jobs with API token + CSRF crumb; optionally wait for build result and tail console on failure. | `references/`, `scripts/` |
| [`obsidian-cli`](./skills/obsidian-cli/SKILL.md)               | Read, create, and manage Obsidian vault notes via the bundled `obsidian` CLI; follows PARA structure.           | None                      |
| [`project-dev-guide`](./skills/project-dev-guide/SKILL.md)     | Resolve local project aliases to real repo absolute paths before reading or editing code.                       | `references/`             |
| [`tdl`](./skills/tdl/SKILL.md)                                 | Log in to Telegram and download media (filter by file type, group albums, resume) via `tdl`.                    | `scripts/`                |
| [`vikunja`](./skills/vikunja/SKILL.md)                         | Manage Vikunja tasks, projects, labels, assignees, reminders via REST API with safe-update pattern.             | `references/`             |

## Repository Layout

Each skill lives in its own folder and follows the Agent Skills specification:

```text
skills/
  <skill-name>/
    SKILL.md
    references/   # optional supporting docs
    scripts/      # optional executable helpers
```

The repository also includes lightweight maintenance tooling:

- [`package.json`](./package.json) for Markdown formatting commands
- [`.github/workflows/markdown.yml`](./.github/workflows/markdown.yml) for formatting checks
- [`.github/workflows/markdown-fix.yml`](./.github/workflows/markdown-fix.yml) for manual Markdown autofix

## Development

Install tooling:

```bash
bun install
```

Check Markdown formatting:

```bash
bun run check:md
```

Format Markdown files:

```bash
bun run format:md
```

## Notes

- Keep core instructions in each `SKILL.md`.
- Move larger supporting material into `references/` instead of bloating the main skill file.
- Keep helper scripts colocated inside the owning skill's `scripts/` directory when possible.
- Use [`scripts/link-skills.sh`](./scripts/link-skills.sh) when you want the local repository to stay as the source of truth for Hermes symlinks.
