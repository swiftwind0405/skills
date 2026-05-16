# url-to-markdown

Fetch any URL and convert to markdown using `baoyu-fetch` CLI (Chrome CDP with site-specific adapters). Built-in adapters for X/Twitter, YouTube transcripts, Hacker News threads, and generic pages via Defuddle. Supports login/CAPTCHA via interaction wait modes.

## Configuration

All settings are read directly from system environment variables.

| Variable                   | Required           | Description                                                        |
| -------------------------- | ------------------ | ------------------------------------------------------------------ |
| `BAOYU_CHROME_PROFILE_DIR` | No                 | Chrome user data directory (can also use `--chrome-profile-dir`)   |
| `COS_SECRET_ID`            | For `--upload-cos` | Tencent Cloud COS SecretId                                         |
| `COS_SECRET_KEY`           | For `--upload-cos` | Tencent Cloud COS SecretKey                                        |
| `COS_BUCKET`               | For `--upload-cos` | COS bucket name, e.g. `my-bucket-1250000000`                       |
| `COS_REGION`               | For `--upload-cos` | COS region, e.g. `ap-guangzhou`                                    |
| `COS_PREFIX`               | No                 | Object key prefix (default: `url-to-markdown`)                     |
| `COS_BASE_URL`             | No                 | Custom CDN domain for rewritten links (default: COS bucket domain) |

## Media Upload to COS

With `--upload-cos`, downloaded images/videos are uploaded to Tencent Cloud COS,
markdown links are rewritten to the COS URLs, and the local copies are deleted.
It implies `--download-media` and requires `--output`. Set the four `COS_*`
credentials above as system environment variables before use:

```bash
export COS_SECRET_ID=xxx
export COS_SECRET_KEY=xxx
export COS_BUCKET=my-bucket-1250000000
export COS_REGION=ap-guangzhou

baoyu-fetch <url> --output article.md --upload-cos
```

Objects are stored under `{COS_PREFIX}/{slug}/{imgs|videos}/{filename}`.
A failed upload keeps that file local and leaves its link unchanged.

## Bundled Assets

- `references/` — adapter documentation
- `scripts/` — `baoyu-fetch` and dependencies
