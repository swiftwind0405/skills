# url-to-markdown

Fetch any URL and convert to markdown using `baoyu-fetch` CLI (Chrome CDP with site-specific adapters). Built-in adapters for X/Twitter, YouTube transcripts, Hacker News threads, and generic pages via Defuddle. Supports login/CAPTCHA via interaction wait modes.

## Configuration

| Variable                   | Required | Description                                                      |
| -------------------------- | -------- | ---------------------------------------------------------------- |
| `BAOYU_CHROME_PROFILE_DIR` | No       | Chrome user data directory (can also use `--chrome-profile-dir`) |

## Bundled Assets

- `references/` — adapter documentation
- `scripts/` — `baoyu-fetch` and dependencies
