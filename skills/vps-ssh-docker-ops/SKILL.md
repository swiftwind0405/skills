---
name: vps-ssh-docker-ops
description: Use when operating the user's VPS servers through SSH aliases `vps-cc` or `vps-dmit`: outage triage, SSH hardening, Docker service deploy/remove/cleanup, abuse investigation, or VPS residue cleanup.
metadata:
  version: "2.0.0"
---

# VPS SSH Docker Ops

Prefix your first line with 🥷 inline, not as its own paragraph.

Use this skill for direct work on the user's VPS servers.

## Known Hosts

| Alias | IP | User | Key | Notes |
|---|---|---|---|---|
| `vps-cc` | 142.171.39.167 | root | `~/.ssh/id_vps` | CC 机房 |
| `vps-dmit` | 69.63.201.37 | root | `~/.ssh/id_ed25519_dmit` | DMIT 机房 |

When the user says "VPS" without specifying which one, ask which host they mean. If context makes it obvious (e.g. a service only runs on one), state your assumption and proceed.

## Starting Checks

- Confirm alias and target: `ssh -G <alias> | rg '^(hostname|user|identityfile) '`.
- Prefer short probes: `ssh -o BatchMode=yes -o ConnectTimeout=8 <alias> 'hostname; date -Is; whoami'`.
- Keep local vs remote context explicit. If the workload is on the VPS, local Docker/OrbStack errors are usually irrelevant.
- If sandbox networking blocks SSH with `Operation not permitted`, request escalation and retry the same probe.

## Incident Triage

For "无法连接", banner timeout, slow VPS, or "重启后才连上":

1. Check boot and shutdown timeline: `last -x`, `uptime`, `journalctl -b -1`.
2. Check SSH evidence: `journalctl -u ssh --since '...'`, `sshd -T | rg 'maxstartups|passwordauthentication|permitrootlogin|logingracetime|maxauthtries'`.
3. Check resource pressure: `free -h`, `df -h`, `journalctl -b -1 -k | rg -i 'oom|killed|panic|segfault'`.
4. Check auth abuse without overstating intrusion: `lastb`, `journalctl -u ssh | rg -i 'failed|timeout|MaxStartups|authentication'`.

Important distinction: `beginning MaxStartups throttling` plus many `Timeout before authentication` entries proves pre-auth pressure, not a kernel crash or successful intrusion.

## Docker Service Deploy/Remove

- Known service root pattern: `/root/data/docker_data/<service>`.
- For compose services, operate remotely from the service directory, then verify from a stable directory like `/root`.
- Removal means more than stop: `docker compose down --remove-orphans`, remove images if requested, remove data paths if the user says `都不要了` or `全部删除`.
- After deleting a working directory, `cd /root` before verification to avoid `getcwd() failed`.
- For Huntly, backend port `7188` and `GET /` are meaningful; `HEAD /` can mislead. A short `Connection reset by peer` after restart may be warm-up noise, so retry once after a brief wait.

## SSH Hardening

- If the user asks for minimal hardening, prefer the smallest accepted change first: `PasswordAuthentication no`.
- Validate before reload: `sshd -t`.
- Confirm a fresh key login after reload.
- Accepted broader pattern on these VPS hosts:
  - `PermitRootLogin prohibit-password`
  - `PasswordAuthentication no`
  - `PubkeyAuthentication yes`
  - `LoginGraceTime 20`
  - `MaxAuthTries 3`
  - `MaxStartups 5:30:20`
  - conservative fail2ban: `findtime=10m`, `maxretry=8`, `bantime=1h`

## Abuse Blocking

- Prefer narrow, evidence-backed blocks from `lastb` and `journalctl`.
- Region-wide geo-blocking has been rejected as too damaging; treat it as opt-in and fully reversible.
- If the user rejects a broad block, remove all related nftables/systemd artifacts, not just the active rule.

## OpenClaw/Tailscale Residue

- OpenClaw can be a root user-level systemd service plus a global Node package:
  - `systemctl --user status openclaw-gateway`
  - `npm -g uninstall openclaw`
- Stale shell errors after uninstall can come from `/root/.bashrc` sourcing `/root/.openclaw/completions/openclaw.bash`.
- Tailscale is a normal system package/service: verify packages, binaries, and `tailscaled.service`.

## Outcome Format

Report:

```text
Root cause:
Changes:
Verification:
Residual risk:
```
