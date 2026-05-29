# Agent Skills

[English](./README.md)

面向本地工程工作流的自定义 Agent Skills 集合。

## 使用方式

作为技能源安装：

```bash
bunx skills add https://github.com/swiftwind0405/skills
```

或将本地目录软链到 `~/.hermes/skills/`：

```bash
bash scripts/link-skills.sh
```

## 技能列表

- [articles-translates](./skills/articles-translates/)
- [format-markdown](./skills/format-markdown/)
- [huntly-manager](./skills/huntly-manager/)
- [jenkins-job-trigger](./skills/jenkins-job-trigger/)
- [jira-cli](./skills/jira-cli/)
- [markdown-to-html](./skills/markdown-to-html/)
- [mcp-builder](./skills/mcp-builder/)
- [obsidian-cli](./skills/obsidian-cli/)
- [tdl](./skills/tdl/)
- [url-to-markdown](./skills/url-to-markdown/)
- [url-translate-html](./skills/url-translate-html/)
- [vikunja](./skills/vikunja/)
- [vps-ssh-docker-ops](./skills/vps-ssh-docker-ops/)

每个技能目录内有独立的 README 说明用途与配置。

## 目录结构

```text
skills/
  <skill-name>/
    SKILL.md
    README.md      # 技能概览与配置说明
    references/
    scripts/
```

## 开发维护

```bash
bun install
bun run check:md    # 检查 Markdown 格式
bun run format:md   # 自动修复 Markdown 格式
```
