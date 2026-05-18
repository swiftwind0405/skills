# vps-ssh-docker-ops

Operate VPS servers through SSH: outage triage, SSH hardening, Docker service deploy/remove/cleanup, abuse investigation, and residue cleanup.

## Configuration

Set host info via environment variables or EXTEND.md (see SKILL.md for details):

| Variable        | Description                                |
| --------------- | ------------------------------------------ |
| `VPS_CC_HOST`   | IP or hostname for CC alias (`vps-cc`)     |
| `VPS_CC_USER`   | SSH user for CC (default: `root`)          |
| `VPS_CC_KEY`    | SSH identity file for CC                   |
| `VPS_DMIT_HOST` | IP or hostname for DMIT alias (`vps-dmit`) |
| `VPS_DMIT_USER` | SSH user for DMIT (default: `root`)        |
| `VPS_DMIT_KEY`  | SSH identity file for DMIT                 |

## Features

- Incident triage (connectivity, resource pressure, auth abuse)
- Docker Compose service deploy, remove, and cleanup
- SSH hardening (key-only auth, fail2ban)
- Abuse blocking (evidence-backed, narrow scope)
- Service residue cleanup (OpenClaw, Tailscale, etc.)
