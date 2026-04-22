# Custom Hermes Skills

This repository is the source of truth for my customized Hermes skills.

## Managed skills

- `obsidian-cli`
- `jenkins-job-trigger`
- `project-dev-guide`
- `tdl`
- `vikunja`

## How it works

The actual skill content lives in this repo. Hermes loads the same files through symlinks under:

```bash
~/.hermes/skills/
```

Example:

```bash
~/.hermes/skills/obsidian-cli -> ~/Workspace/main/skills/obsidian-cli
```

So edits in this repo take effect immediately for Hermes.

## Daily workflow

### Edit a skill

Edit files directly in this repo, for example:

```bash
~/Workspace/main/skills/obsidian-cli/SKILL.md
```

### Check status

```bash
cd ~/Workspace/main/skills
git status
```

### Commit changes

```bash
cd ~/Workspace/main/skills
git add .
git commit -m "update hermes skills"
```

### Sync to another device

1. Clone this repo on the other device.
2. Recreate the symlinks from `~/.hermes/skills/` to the repo directories.
3. Run a new Hermes session or `/reset` if needed.

## New device setup

```bash
git clone <your-repo-url> ~/Workspace/main/skills
cd ~/Workspace/main/skills
./scripts/link-skills.sh
```

Then start a new Hermes session, or run `/reset` inside Hermes if it is already running.

### Local private overrides

This repo is public-safe, so runtime-specific values should go into ignored local override files instead of public `SKILL.md` examples.

Current convention:

- `project-dev-guide/references/path-aliases.local.json` — real local project paths
- `jenkins-job-trigger/references/job-aliases.local.json` — real local Jenkins job aliases

These files are ignored by git via `*.local.json`.

When setting up on a new machine:

1. Copy the corresponding `*.example.json` file if present, or create the `*.local.json` file manually.
2. Fill in machine-specific paths / aliases.
3. Restart Hermes or `/reset` so subsequent sessions use the updated skill behavior.

If a skill needs to be both **public** and **runnable locally**, prefer this pattern:

- public examples in `SKILL.md` or non-local reference files
- real values in ignored `*.local.json`
- scripts / instructions should prefer local override files first, then fall back to public examples

If you update skills later on that device:

```bash
cd ~/Workspace/main/skills
git pull
./scripts/link-skills.sh
```

## Recreate symlinks manually

Example pattern:

```bash
ln -s ~/Workspace/main/skills/obsidian-cli ~/.hermes/skills/obsidian-cli
```

If a destination already exists, remove or move it first.

## Notes

- Treat this repo as the single source of truth for customized skills.
- Avoid keeping editable duplicate copies under `~/.hermes/skills/`.
- If Hermes doesn't reflect changes, start a new session or use `/reset`.
