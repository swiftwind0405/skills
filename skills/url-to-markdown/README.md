# url-to-markdown

使用 `baoyu-fetch` CLI 获取任意 URL 并转换为 Markdown（基于 Chrome CDP，并带站点专用适配器）。内置 X/Twitter、YouTube transcript、Hacker News thread，以及通过 Defuddle 处理通用页面的适配器。支持通过交互等待模式处理登录/CAPTCHA。

## 配置

所有设置都直接从系统环境变量读取。

| 变量                       | 必填条件               | 说明                                                               |
| -------------------------- | ---------------------- | ------------------------------------------------------------------ |
| `BAOYU_CHROME_PROFILE_DIR` | 否                     | Chrome 用户数据目录（也可使用 `--chrome-profile-dir`）             |
| `COS_SECRET_ID`            | 使用 `--upload-cos` 时 | 腾讯云 COS SecretId                                                |
| `COS_SECRET_KEY`           | 使用 `--upload-cos` 时 | 腾讯云 COS SecretKey                                               |
| `COS_BUCKET`               | 使用 `--upload-cos` 时 | COS bucket 名称，例如 `my-bucket-1250000000`                       |
| `COS_REGION`               | 使用 `--upload-cos` 时 | COS 地域，例如 `ap-guangzhou`                                      |
| `COS_PREFIX`               | 否                     | 对象 key 前缀（默认：`url-to-markdown`）                           |
| `COS_ACL`                  | 否                     | 对象 ACL（默认：`public-read`；设为 `default` 则使用 bucket 策略） |
| `COS_BASE_URL`             | 否                     | 用于重写链接的自定义 CDN 域名（默认：COS bucket 域名）             |

## 媒体上传到 COS

使用 `--upload-cos` 时，下载的图片/视频会上传到腾讯云 COS，Markdown 链接会改写为 COS URL，本地副本会被删除。该选项隐含启用 `--download-media`，并要求提供 `--output`。使用前请将上表中的四个 `COS_*` 凭据设置为系统环境变量：

```bash
export COS_SECRET_ID=xxx
export COS_SECRET_KEY=xxx
export COS_BUCKET=my-bucket-1250000000
export COS_REGION=ap-guangzhou

baoyu-fetch <url> --output article.md --upload-cos
```

对象会存储在 `{prefix}/{output-slug}/{imgs|videos}/{filename}` 下。前缀默认是 `url-to-markdown`，可通过 `COS_PREFIX` 环境变量或 `--cos-prefix` 参数指定（参数优先），例如 `--cos-prefix articles-collect` 会将对象存到 `articles-collect/...` 下。上传对象默认使用 `public-read`，因此改写后的链接可在默认 COS bucket 域名下访问；设置 `COS_ACL=default` 可改为依赖 bucket 策略或 CDN 配置。上传失败时，该文件会保留在本地，链接也保持不变。

## 内置资源

- `references/`：适配器文档
- `scripts/`：`baoyu-fetch` 及其依赖
