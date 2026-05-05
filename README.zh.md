# Agent Skills

[English](./README.md)

这个仓库用来维护一组面向实际本地工作流的自定义 Agent Skills。

## 使用方式

这个仓库可以按两种方式使用：

1. 通过 `bunx skills add` 或 `npx skills add` 直接作为 skills source 安装。
2. 通过 [`scripts/link-skills.sh`](./scripts/link-skills.sh) 把本地技能目录软链到 `~/.hermes/skills/`。

直接作为技能源安装：

```bash
bunx skills add https://github.com/swiftwind0405/skills
```

或者：

```bash
npx skills add https://github.com/swiftwind0405/skills
```

## Skills Catalog

下表列出了当前仓库维护的技能。

| Name                                                           | Description                                                                                        | Bundled Assets            |
| -------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- | ------------------------- |
| [`articles-translates`](./skills/articles-translates/SKILL.md) | 三模式文章翻译（快速/普通/精细），支持术语表、长文分块处理，可自定义风格与读者群体偏好。           | `references/`, `scripts/` |
| [`format-markdown`](./skills/format-markdown/SKILL.md)         | 格式化纯文本或 Markdown，自动生成 frontmatter、标题、摘要、层级标题、加粗、列表，含 CJK 排版修复。 | `references/`, `scripts/` |
| [`huntly-manager`](./skills/huntly-manager/SKILL.md)           | 以混合模式使用 Huntly：读操作走 MCP，写入内容与 collection/group 管理走 REST API 脚本。            | `references/`, `scripts/` |
| [`jenkins-job-trigger`](./skills/jenkins-job-trigger/SKILL.md) | 通过 API Token + CSRF crumb 触发 Jenkins 构建，可等待结果，失败时自动拉取 console 尾部日志。       | `references/`, `scripts/` |
| [`markdown-to-html`](./skills/markdown-to-html/SKILL.md)       | 将 Markdown 转换为带主题样式的 HTML，支持代码高亮、数学公式、脚注、提示框及微信外链转底部引用。    | `scripts/`                |
| [`obsidian-cli`](./skills/obsidian-cli/SKILL.md)               | 通过自带的 `obsidian` CLI 读写与管理 Obsidian 笔记，遵循 PARA 目录结构。                           | None                      |
| [`project-dev-guide`](./skills/project-dev-guide/SKILL.md)     | 读代码或改代码前，先把项目别名解析到本机真实仓库绝对路径。                                         | `references/`             |
| [`tdl`](./skills/tdl/SKILL.md)                                 | 登录 Telegram 并通过 `tdl` 下载媒体（按类型过滤、下载相册组、断点续传）。                          | `scripts/`                |
| [`url-to-markdown`](./skills/url-to-markdown/SKILL.md)         | 通过 Chrome CDP 抓取任意 URL 并转为 Markdown，内置 X/Twitter、YouTube、Hacker News 等适配器。      | `references/`, `scripts/` |
| [`url-translate-html`](./skills/url-translate-html/SKILL.md)   | 将 URL 转为双语原文/中文上下对照 Markdown，并渲染为带主题样式的 HTML。                             | None                      |
| [`vikunja`](./skills/vikunja/SKILL.md)                         | 通过 REST API 管理 Vikunja 任务、项目、标签、指派人、提醒，遵循安全更新模式。                      | `references/`             |

## 仓库结构

每个 skill 都放在独立目录中，并遵循统一结构：

```text
skills/
  <skill-name>/
    SKILL.md
    references/   # 可选，补充文档
    scripts/      # 可选，可执行脚本
```

仓库同时提供一套很轻量的维护工具：

- [`package.json`](./package.json) 提供 Markdown 格式化命令
- [`.github/workflows/markdown.yml`](./.github/workflows/markdown.yml) 负责格式检查
- [`.github/workflows/markdown-fix.yml`](./.github/workflows/markdown-fix.yml) 负责手动触发自动格式化

## 开发维护

安装依赖：

```bash
bun install
```

检查 Markdown 格式：

```bash
bun run check:md
```

格式化 Markdown：

```bash
bun run format:md
```

## 说明

- 核心说明放在各自的 `SKILL.md` 中。
- 较长的补充内容放进 `references/`，不要把 `SKILL.md` 写得过重。
- 需要复用的辅助脚本优先放到对应 skill 自己的 `scripts/` 目录中。
- 如果要让本地仓库持续作为 Hermes 软链源，使用 [`scripts/link-skills.sh`](./scripts/link-skills.sh)。
