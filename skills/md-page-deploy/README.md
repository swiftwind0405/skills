# md-page-deploy

把用户提供的 Markdown 转成更易读的本地静态 HTML 页面，或直接部署已有 HTML 页面，预览确认后发布到 Cloudflare Pages。

## 用途

- 从 Markdown 文件或粘贴内容生成 `pages/<slug>/index.html`
- 跳过生成步骤，直接部署已有 `index.html` 目录
- 将单个 `.html` 文件整理为 `pages/<slug>/index.html` 后部署
- 本地启动 HTTP 预览，让用户确认效果
- 经用户明确同意后，通过 GitHub push 触发 Cloudflare Pages 部署

## 默认部署目标

| 参数           | 默认值                                             | 环境变量                   |
| -------------- | -------------------------------------------------- | -------------------------- |
| Docs repo path | `/Users/stanley/Workspace/main/stanley-docs-pages` | `DEPLOY_PAGES_REPO`        |
| GitHub repo    | `swiftwind0405/stanley-docs-pages`                 | `DEPLOY_PAGES_GITHUB_REPO` |
| 源目录         | `pages`                                            | `DEPLOY_PAGES_SOURCE`      |
| 构建目录       | `.deploy/cloudflare-pages`                         | `DEPLOY_PAGES_BUILD_DIR`   |
| 公网域名       | `docs.stanleywind.org`                             | `DEPLOY_PAGES_DOMAIN`      |

部署后 URL：

```text
https://docs.stanleywind.org/<slug>/
```

## 脚本

```bash
cd /Users/stanley/Workspace/main/stanley-docs-pages
bash scripts/build-cloudflare-pages.sh
```

脚本会扫描 `pages/*/index.html`，生成 Cloudflare Pages 发布目录和根目录索引。
