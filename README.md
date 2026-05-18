# Agent Skills

[简体中文](./README.zh.md)

A curated set of custom Agent Skills for local engineering workflows.

## Usage

Add as a skill source:

```bash
bunx skills add https://github.com/swiftwind0405/skills
```

Or symlink local folders into `~/.hermes/skills/`:

```bash
bash scripts/link-skills.sh
```

## Skills

- [articles-translates](./skills/articles-translates/)
- [format-markdown](./skills/format-markdown/)
- [huntly-manager](./skills/huntly-manager/)
- [jenkins-job-trigger](./skills/jenkins-job-trigger/)
- [markdown-to-html](./skills/markdown-to-html/)
- [mcp-builder](./skills/mcp-builder/)
- [obsidian-cli](./skills/obsidian-cli/)
- [tdl](./skills/tdl/)
- [url-to-markdown](./skills/url-to-markdown/)
- [url-translate-html](./skills/url-translate-html/)
- [vikunja](./skills/vikunja/)
- [vps-ssh-docker-ops](./skills/vps-ssh-docker-ops/)

Each skill has its own README with details and configuration.

## Layout

```text
skills/
  <skill-name>/
    SKILL.md
    README.md      # skill overview & config
    references/
    scripts/
```

## Development

```bash
bun install
bun run check:md    # validate Markdown formatting
bun run format:md   # auto-fix Markdown formatting
```
