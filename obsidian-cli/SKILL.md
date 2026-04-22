---
name: obsidian-cli
description: Read, create, and manage Obsidian vault notes via the built-in `obsidian` CLI. Use when the user asks to interact with their Obsidian vault or develop Obsidian plugins/themes.
---

# Obsidian CLI

Use the `obsidian` CLI to interact with a running Obsidian instance. Requires Obsidian to be open.

## Prerequisites

> **DO NOT** attempt to install `obsidian-cli` via npm, brew, pip, or any other package manager.
> The `obsidian` command is **bundled with the Obsidian desktop app** and is already available at
> `/Applications/Obsidian.app/Contents/MacOS/obsidian`. No separate installation is needed.
> If the command is not found, ensure the Obsidian app is installed and its path is in `$PATH`.

---

## Vault structure & note placement (PARA method)

The vault `ObsidianDoc` follows the **PARA** organisation. Use this section to decide **where to create** a new note and **where to search** for existing notes.

### Default vault

```
vault="ObsidianDoc"
```

### Default location for new notes

**When in doubt, always create notes in `00 Inbox`.**

```bash
obsidian create vault="ObsidianDoc" name="My Note" path="00 Inbox/My Note.md" silent
```

### Folder map

| Folder | Purpose | When to use |
|---|---|---|
| **`00 Inbox`** | Default drop zone for all new notes. | Any new note that doesn't clearly belong elsewhere. Quick captures, drafts, unprocessed ideas. |
| **`10 Project`** | Active, time-bound projects with clear goals. | Notes tied to a specific project (e.g. `Hermes`, `claude-code-study`). Create a subfolder per project. |
| **`20 Area`** | Long-term areas of responsibility / knowledge domains. | Ongoing knowledge that is neither a project nor a reference. Has many sub-areas (see below). |
| **`30 Resource`** | Reference material, reading notes, topic deep-dives. | Book notes (`微信读书/`, `读书笔记/`), topic compilations (`专题笔记/`), curated collections (`Flomo/`). |
| **`40 Archive`** | Completed or paused projects and notes. | Notes/projects that are no longer active. |
| **`Templates`** | Note templates. | Never place regular notes here. Only templates. |
| **`Attachments`** | Images and file attachments. | Binary files, images referenced by notes. |
| **`Excalidraw`** | Excalidraw drawings. | `.excalidraw` files only. |

### `20 Area` sub-areas (knowledge domains)

| Sub-folder | Topics |
|---|---|
| `20 Area/AI` | AI/LLM/Agent/MCP/Prompt/RAG – all AI-related knowledge |
| `20 Area/11 前端` | Frontend: JavaScript, React, CSS, TypeScript, Node.js, browser, performance, state management |
| `20 Area/12 算法和数据结构` | Algorithms & data structures |
| `20 Area/15 计算机基础` | CS fundamentals: networking, compilers, OS, CPU |
| `20 Area/17 容器和虚拟化` | Docker, containers, virtualisation |
| `20 Area/19 编程` | General programming: Go, Java, Python, C/C++, design patterns, architecture |
| `20 Area/Work` | Work-related: team standards, code review, interviews, leadership |
| `20 Area/工具` | Developer tools: Git, Vim, Tmux, Shell, Obsidian, network debugging |

### `30 Resource` sub-areas

| Sub-folder | Content type |
|---|---|
| `30 Resource/专题笔记` | Topic-based notes & collections (e.g. `Openclaw`, travel guides) |
| `30 Resource/读书笔记` | Manually written reading notes |
| `30 Resource/微信读书` | Book highlights exported from WeRead |
| `30 Resource/Flomo` | Notes imported from Flomo |

### Placement decision flowchart

1. **Is it a quick capture / draft / unclear where it belongs?** → `00 Inbox`
2. **Is it tied to an active project?** → `10 Project/<project-name>/`
3. **Is it long-term knowledge in a specific domain?** → Find the matching `20 Area/` sub-folder
4. **Is it a book note, reading highlight, or reference collection?** → `30 Resource/` appropriate sub-folder
5. **Is it about a completed/paused topic?** → `40 Archive/`
6. **Still unsure?** → `00 Inbox` (the user will refile later)

### Templates

Two templates are available:

- **`Template - Note`** — Standard note with `tags` frontmatter and a `## References` section.
- **`Template - Progressive Note`** — Progressive summarisation note with `## SUMMARY`, `## FULL NOTES`, and `## REFERENCE` sections.

```bash
# Create with template
obsidian create vault="ObsidianDoc" name="New Topic" path="00 Inbox/New Topic.md" template="Template - Note" silent
```

---

## Command reference

Run `obsidian help` to see all available commands. This is always up to date. Full docs: https://help.obsidian.md/cli

## Syntax

**Parameters** take a value with `=`. Quote values with spaces:

```bash
obsidian create name="My Note" content="Hello world"
```

**Flags** are boolean switches with no value:

```bash
obsidian create name="My Note" silent overwrite
```

For multiline content use `\n` for newline and `\t` for tab.

## File targeting

Many commands accept `file` or `path` to target a file. Without either, the active file is used.

- `file=<name>` — resolves like a wikilink (name only, no path or extension needed)
- `path=<path>` — exact path from vault root, e.g. `folder/note.md`

## Vault targeting

Commands target the most recently focused vault by default. Use `vault=<name>` as the first parameter to target a specific vault:

```bash
obsidian vault="ObsidianDoc" search query="test"
```

## Searching for notes

Use `search` to find notes. Combine with your knowledge of the folder structure to narrow results:

```bash
# Full-text search
obsidian vault="ObsidianDoc" search query="search term" limit=10

# Search by tag
obsidian vault="ObsidianDoc" tags sort=count counts

# Find backlinks to a note
obsidian vault="ObsidianDoc" backlinks file="My Note"
```

> **Tip**: If you know the topic domain, you can use `read` with the known path directly instead of searching:
> ```bash
> obsidian vault="ObsidianDoc" read path="20 Area/AI/AI Agent Study.md"
> ```

## Common patterns

```bash
obsidian vault="ObsidianDoc" read file="My Note"
obsidian vault="ObsidianDoc" create name="New Note" path="00 Inbox/New Note.md" content="# Hello" template="Template - Note" silent
obsidian vault="ObsidianDoc" append file="My Note" content="New line"
obsidian vault="ObsidianDoc" search query="search term" limit=10
obsidian vault="ObsidianDoc" daily:read
obsidian vault="ObsidianDoc" daily:append content="- [ ] New task"
obsidian vault="ObsidianDoc" property:set name="status" value="done" file="My Note"
obsidian vault="ObsidianDoc" tasks daily todo
obsidian vault="ObsidianDoc" tags sort=count counts
obsidian vault="ObsidianDoc" backlinks file="My Note"
```

Use `copy` on any command to copy output to clipboard. Use `silent` to prevent files from opening. Use `total` on list commands to get a count.

## Plugin development

### Develop/test cycle

After making code changes to a plugin or theme, follow this workflow:

1. **Reload** the plugin to pick up changes:
   ```bash
   obsidian plugin:reload id=my-plugin
   ```
2. **Check for errors** — if errors appear, fix and repeat from step 1:
   ```bash
   obsidian dev:errors
   ```
3. **Verify visually** with a screenshot or DOM inspection:
   ```bash
   obsidian dev:screenshot path=screenshot.png
   obsidian dev:dom selector=".workspace-leaf" text
   ```
4. **Check console output** for warnings or unexpected logs:
   ```bash
   obsidian dev:console level=error
   ```

### Additional developer commands

Run JavaScript in the app context:

```bash
obsidian eval code="app.vault.getFiles().length"
```

Inspect CSS values:

```bash
obsidian dev:css selector=".workspace-leaf" prop=background-color
```

Toggle mobile emulation:

```bash
obsidian dev:mobile on
```

Run `obsidian help` to see additional developer commands including CDP and debugger controls.