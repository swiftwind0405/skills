---
name: tdl
description: Telegram Downloader. Use when user needs to login to Telegram, download media files (images, videos) from chats or messages, or manage Telegram downloads. Handles tdl CLI tool operations including authentication, download filtering by file type, and download management.
---

# TDL Skill

Wrapper for [tdl](https://github.com/iyear/tdl) (Telegram Downloader) - a CLI tool to download media from Telegram.

## Prerequisites

- tdl must be installed (check with `which tdl`)
- For first use, user must login to Telegram

## Quick Start

### 1. Login to Telegram

```bash
tdl login
```

Follow the prompts to authenticate with your Telegram account.

### 2. Download Media from a Message Link

```bash
# Download all media from a message link
tdl download -u <telegram-message-url>

# Download grouped messages (albums) - downloads all photos in the group
tdl download -u <url> --group

# Download only images and videos
tdl download -u <url> -i jpg,jpeg,png,mp4,mov,mkv

# Download to specific directory (use absolute path, not ~)
tdl download -u <url> -d /Users/you/Downloads/telegram
```

## Common Operations

### Download Grouped Messages (Albums)

When a message contains multiple photos (album/grouped message), use `--group` to download all of them:

```bash
# Download all photos in the group/album
tdl download -u <url> --group
```

### Download Specific File Types

```bash
# Images only
tdl download -u <url> -i jpg,jpeg,png,gif,webp

# Videos only
tdl download -u <url> -i mp4,mov,mkv,avi,webm

# Exclude certain types
tdl download -u <url> -e txt,json
```

### Download from Multiple Messages

```bash
# Multiple URLs
tdl download -u <url1> -u <url2> -u <url3>
```

### Resume Interrupted Downloads

```bash
# Continue from where it stopped
tdl download --continue
```

### Use Different Namespace (for multiple accounts)

```bash
# Login with namespace
tdl login -n work

# Download using that namespace
tdl download -u <url> -n work
```

## Special Channel Link Conversion

Some private channels require link format conversion to work with tdl:

### Example private channel conversion

For links from some private channels, convert the format:

**Original:** `https://t.me/c/<source_chat_id>/{msg_id}?thread={thread_id}`
**Convert to:** `https://t.me/<public_chat_id>/{thread_id}?comment={msg_id}`

**Example:**

- Original: `https://t.me/c/1234567890/1052?thread=1030`
- Converted: `https://t.me/1987654321/1030?comment=1052`

## Resources

### scripts/

- `tdl-download.sh` - Simplified download script with common options
