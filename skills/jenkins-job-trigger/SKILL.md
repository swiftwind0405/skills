---
name: jenkins-job-trigger
description: Trigger Jenkins jobs/builds from chat by running a bundled Python script that authenticates with username+API token, handles CSRF crumb, supports optional build parameters, and can wait for queue/build completion and report the result. Use when the user asks to run/trigger/rebuild a Jenkins job, kick off a CI build, or automate Jenkins job execution.
---

# Jenkins Job Trigger

Use the bundled script to trigger a Jenkins job and (optionally) wait for completion.

## What to do

1. Collect inputs (**ask only what's missing**):

- **First check environment variables**; if they're present, do **not** ask the user again.
- `JENKINS_URL` (e.g. `http://jenkins.example.com:8080`)
- Job selector: either
  - `--job-path job/<folder>/job/<job>` (recommended)
  - or `--job-name "友好名字"` resolved via the JSON file at `JENKINS_JOB_ALIASES` env var
- Auth: `JENKINS_USER` + `JENKINS_TOKEN` (API token)
- Optional parameters: `k=v` pairs
- Whether to wait for result (default: wait)

2. Run the script via the `exec` tool.

- Pass credentials via environment variables (never write tokens into code or logs).
- The script already defaults from env:
  - `--jenkins` ← `JENKINS_URL`
  - `--user` ← `JENKINS_USER`
  - `--token` ← `JENKINS_TOKEN`
  - `--job-path` ← `JOB_PATH`
  - `--aliases` ← `JENKINS_JOB_ALIASES` (path to a JSON file mapping friendly names → job paths)
- Prefer a single command so the transcript is reproducible.

## Commands

### Trigger by job path (wait for result)

```bash
python3 skills/jenkins-job-trigger/scripts/run_jenkins_job.py \
  --jenkins "$JENKINS_URL" \
  --job-path "job/example-folder/job/example-web-build"
```

### Trigger by friendly job name (wait for result)

```bash
python3 skills/jenkins-job-trigger/scripts/run_jenkins_job.py \
  --jenkins "$JENKINS_URL" \
  --job-name "web-build"
```

### Trigger + auto-diagnose on failure (print console tail)

```bash
python3 skills/jenkins-job-trigger/scripts/run_jenkins_job.py \
  --job-name "web-build" \
  --console-tail 120
```

### Trigger with parameters

```bash
python3 skills/jenkins-job-trigger/scripts/run_jenkins_job.py \
  --jenkins "$JENKINS_URL" \
  --job-path "job/example-folder/job/example-web-build" \
  --param branch=main \
  --param env=dev
```

### Fire-and-forget (do not wait)

```bash
python3 skills/jenkins-job-trigger/scripts/run_jenkins_job.py \
  --jenkins "$JENKINS_URL" \
  --job-path "job/example-folder/job/example-web-build" \
  --no-wait
```

## Notes / gotchas

- If Jenkins has CSRF protection enabled, the script auto-fetches a crumb and includes it.
- Some Jenkins instances do **not** return a queue item URL when triggering a build. The script will fall back to polling `lastBuild` and still print `Build: #<id> ...` plus `BUILD_ID=<id>` for easy parsing.
- If the build fails due to agent issues (e.g., `No space left on device`), use `--console-tail` to fetch log tail and the script will print a best-effort `Diagnosis:`.
- If Jenkins is a multibranch pipeline, the "job path" often includes the branch as another `job/<branch>` segment; ask the user for the exact URL/path if unsure.
