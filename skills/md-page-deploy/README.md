# md-page-deploy

把用户提供的 Markdown 转成更易读的本地静态 HTML 页面，或直接部署已有 HTML 页面，预览确认后发布到 Caddy/Pages 静态站点。

## 用途

- 从 Markdown 文件或粘贴内容生成 `pages/<slug>/index.html`
- 跳过生成步骤，直接部署已有 `index.html` 目录
- 将单个 `.html` 文件整理为 `pages/<slug>/index.html` 后部署
- 本地启动 HTTP 预览，让用户确认效果
- 经用户明确同意后，通过 SSH + rsync 上传部署

## 默认部署目标

| 参数       | 默认值                  | 环境变量              |
| ---------- | ----------------------- | --------------------- |
| SSH host   | `vps-dmit`              | `DEPLOY_PAGES_REMOTE` |
| 远端根目录 | `/srv/pages`            | `DEPLOY_PAGES_ROOT`   |
| 公网域名   | `pages.stanleywind.org` | `DEPLOY_PAGES_DOMAIN` |
| 远端 owner | `root:root`             | `DEPLOY_PAGES_OWNER`  |

部署后 URL：

```text
https://pages.stanleywind.org/<slug>/
```

## 脚本

```bash
bash scripts/deploy-pages.sh pages/<slug> [slug]
```

脚本会校验目录、`index.html` 和 slug，然后用 `rsync --delete` 同步到远端。
