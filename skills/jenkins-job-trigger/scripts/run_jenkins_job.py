#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Trigger a Jenkins job with username+API token.

- Supports optional parameters (buildWithParameters)
- Auto-handles CSRF crumb when enabled
- Can wait for queue -> build -> result

Credentials:
  JENKINS_USER / JENKINS_TOKEN (recommended via env)
"""

import argparse
import os
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

import requests


def default_aliases_path():
    env_path = os.getenv("JENKINS_JOB_ALIASES", "").strip()
    if env_path:
        return env_path
    return ""


def parse_kv_params(pairs):
    out = {}
    for p in pairs or []:
        if "=" not in p:
            raise ValueError(f"Bad param '{p}', expected k=v")
        k, v = p.split("=", 1)
        out[k] = v
    return out


def get_crumb(session: requests.Session, jenkins_url: str):
    api = urljoin(jenkins_url.rstrip("/") + "/", "crumbIssuer/api/json")
    r = session.get(api, timeout=15)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    data = r.json()
    return data["crumbRequestField"], data["crumb"]


def trigger_build(session: requests.Session, jenkins_url: str, job_path: str, params: dict):
    job_path = job_path.strip("/")
    endpoint = f"{job_path}/buildWithParameters" if params else f"{job_path}/build"
    url = urljoin(jenkins_url.rstrip("/") + "/", endpoint)

    headers = {}
    # Some Jenkins instances require a Referer for Stapler form submissions.
    headers.setdefault(
        "Referer",
        urljoin(jenkins_url.rstrip("/") + "/", job_path.strip("/") + "/"),
    )
    crumb = get_crumb(session, jenkins_url)
    if crumb:
        headers[crumb[0]] = crumb[1]

    # Jenkins occasionally returns HTTP 400 "Nothing is submitted" if the POST has no form body.
    # Send a default 'delay' field to make the request a proper form submit.
    # Force a classic HTML form submission (x-www-form-urlencoded).
    headers.setdefault("Content-Type", "application/x-www-form-urlencoded")

    # Jenkins Stapler expects a form submission including a 'json' field.
    # For non-parameterized builds, an empty parameter array works.
    import json as _json
    payload = {"delay": "0sec", "json": _json.dumps({"parameter": []})}
    payload.update(params or {})

    r = session.post(url, headers=headers, data=payload, timeout=30, allow_redirects=False)

    if r.status_code not in (200, 201, 302):
        raise RuntimeError(f"Trigger failed: HTTP {r.status_code}\n{r.text}")

    return r.headers.get("Location")


def wait_for_build_from_queue(session: requests.Session, queue_url: str, poll: int, timeout: int):
    """Wait for queue item -> executable.

    Only works when queue_url points to /queue/item/<id>/.
    """
    if not queue_url:
        return None, None
    if "/queue/item/" not in queue_url:
        return None, None

    api = queue_url.rstrip("/") + "/api/json"
    deadline = time.time() + timeout

    while time.time() < deadline:
        try:
            r = session.get(api, timeout=15)
            r.raise_for_status()
            q = r.json()
        except requests.RequestException:
            time.sleep(poll)
            continue

        if q.get("cancelled"):
            raise RuntimeError("Queue item was cancelled")

        exe = q.get("executable")
        if exe:
            return exe.get("number"), exe.get("url")

        time.sleep(poll)

    raise TimeoutError("Timed out waiting for job to leave the queue")


def fetch_console_tail(session: requests.Session, build_url: str, lines: int = 120):
    """Fetch last N lines of Jenkins consoleText."""
    api = build_url.rstrip("/") + "/consoleText"
    r = session.get(api, timeout=30)
    r.raise_for_status()
    all_lines = r.text.splitlines()
    if lines <= 0:
        return ""
    return "\n".join(all_lines[-lines:])


def analyze_console_tail(tail: str):
    """Best-effort heuristic analysis of a failed build log tail."""
    t = (tail or "").lower()
    if "no space left on device" in t:
        return "Agent/node disk full: No space left on device"
    if "could not resolve host" in t or "name or service not known" in t:
        return "Network/DNS issue: could not resolve host"
    if "authentication failed" in t or "permission denied" in t:
        return "Auth/permission issue (repo/credentials)"
    if "error fetching remote repo" in t and "git" in t:
        return "Git fetch failed (check repo URL/credentials/network)"
    return None


def wait_for_result(session: requests.Session, build_url: str, poll: int, timeout: int):
    api = build_url.rstrip("/") + "/api/json"
    deadline = time.time() + timeout

    while time.time() < deadline:
        try:
            r = session.get(api, timeout=15)
            r.raise_for_status()
            b = r.json()
        except requests.RequestException:
            time.sleep(poll)
            continue

        if not b.get("building", False):
            return b.get("result"), b.get("url")

        time.sleep(poll)

    raise TimeoutError("Timed out waiting for build result")


def get_last_build(session: requests.Session, jenkins_url: str, job_path: str):
    api = urljoin(jenkins_url.rstrip("/") + "/", job_path.strip("/") + "/lastBuild/api/json")
    r = session.get(api, timeout=15)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()


def wait_for_last_build_change(
    session: requests.Session,
    jenkins_url: str,
    job_path: str,
    before_number: int | None,
    after_ms: int,
    poll: int,
    timeout: int,
):
    """Fallback tracking when Jenkins doesn't return a queue item URL.

    We try to detect the *new* build by:
    - lastBuild.number changes compared to before_number (preferred)
    - AND timestamp >= after_ms (guard against picking an older build)

    This works even when the trigger response doesn't include a queue item URL.
    """
    api = urljoin(jenkins_url.rstrip("/") + "/", job_path.strip("/") + "/lastBuild/api/json")
    deadline = time.time() + timeout

    while time.time() < deadline:
        try:
            r = session.get(api, timeout=15)
            r.raise_for_status()
            lb = r.json()
        except requests.RequestException:
            # Jenkins sometimes closes idle connections; treat as transient.
            time.sleep(poll)
            continue

        n = lb.get("number")
        ts = lb.get("timestamp")
        if ts is None:
            time.sleep(poll)
            continue

        changed = (before_number is None and n is not None) or (n is not None and before_number is not None and int(n) != int(before_number))
        if changed and int(ts) >= int(after_ms):
            return n, lb.get("url")

        time.sleep(poll)

    raise TimeoutError("Timed out waiting for lastBuild to change")


def main():
    ap = argparse.ArgumentParser(description="Trigger Jenkins job and optionally wait for result.")
    ap.add_argument("--jenkins", default=os.getenv("JENKINS_URL", "").strip(), help="Jenkins base URL")
    ap.add_argument(
        "--job-path",
        default=os.getenv("JOB_PATH", "").strip(),
        help="Job path like job/<folder>/job/<job>",
    )
    ap.add_argument(
        "--job-name",
        default="",
        help="Friendly job name (resolved via --aliases). Example: 202前端pc",
    )
    ap.add_argument(
        "--aliases",
        default=default_aliases_path(),
        help="Path to JSON mapping of friendly job names -> job paths",
    )
    ap.add_argument("--user", default=os.getenv("JENKINS_USER", "").strip())
    ap.add_argument("--token", default=os.getenv("JENKINS_TOKEN", "").strip())
    ap.add_argument("--param", action="append", default=[], help="Build param k=v (repeatable)")
    ap.add_argument("--poll", type=int, default=int(os.getenv("POLL_SECONDS", "3")))
    ap.add_argument("--queue-timeout", type=int, default=int(os.getenv("QUEUE_TIMEOUT", "600")))
    ap.add_argument("--build-timeout", type=int, default=int(os.getenv("BUILD_TIMEOUT", "1800")))
    ap.add_argument("--no-wait", action="store_true", help="Trigger only, do not wait for completion")
    ap.add_argument(
        "--console-tail",
        type=int,
        default=int(os.getenv("CONSOLE_TAIL_LINES", "0")),
        help="If build fails, fetch last N lines of consoleText and print them",
    )
    args = ap.parse_args()

    if not args.jenkins:
        print("Missing --jenkins (or env JENKINS_URL)", file=sys.stderr)
        return 2
    # Resolve job by friendly name if provided.
    if args.job_name and not args.job_path:
        try:
            import json

            with open(args.aliases, "r", encoding="utf-8") as f:
                aliases = json.load(f)
            args.job_path = aliases.get(args.job_name, "").strip()
        except FileNotFoundError:
            print(f"Aliases file not found: {args.aliases}", file=sys.stderr)
            return 2
        except Exception as e:
            print(f"Failed to read aliases file: {e}", file=sys.stderr)
            return 2

    if not args.job_path:
        print("Missing --job-path (or --job-name that resolves via aliases)", file=sys.stderr)
        return 2
    if not args.user or not args.token:
        print("Missing auth: set JENKINS_USER and JENKINS_TOKEN (API token)", file=sys.stderr)
        return 2

    params = parse_kv_params(args.param)

    with requests.Session() as s:
        s.auth = (args.user, args.token)

        print(f"Jenkins: {args.jenkins}")
        print(f"Job:     {args.job_path}")
        print(f"Params:  {params if params else '(none)'}")

        # Capture lastBuild before triggering, so we can identify the new build quickly
        before = get_last_build(s, args.jenkins, args.job_path)
        before_num = before.get("number") if isinstance(before, dict) else None

        start_ms = int(time.time() * 1000)
        queue_url = trigger_build(s, args.jenkins, args.job_path, params)
        print(f"Queued:  {queue_url or '(no queue url returned)'}")

        if args.no_wait:
            return 0

        # Prefer queue tracking when available; otherwise fall back to polling lastBuild.
        num, build_url = wait_for_build_from_queue(s, queue_url, poll=args.poll, timeout=args.queue_timeout)
        if not build_url:
            print("Track:   (no queue item url; fallback to polling lastBuild)")
            num, build_url = wait_for_last_build_change(
                s,
                args.jenkins,
                args.job_path,
                before_number=before_num,
                after_ms=start_ms,
                poll=args.poll,
                timeout=args.queue_timeout,
            )

        print(f"Build:   #{num} {build_url}")
        # Machine-parsable hint for chat automations
        print(f"BUILD_ID={num}")

        result, final_url = wait_for_result(s, build_url, poll=args.poll, timeout=args.build_timeout)
        print(f"Result:  {result} ({final_url})")

        if result != "SUCCESS" and args.console_tail and args.console_tail > 0:
            tail = fetch_console_tail(s, final_url or build_url, lines=args.console_tail)
            reason = analyze_console_tail(tail)
            if reason:
                print(f"Diagnosis: {reason}")
            print(f"--- console tail (last {args.console_tail} lines) ---")
            print(tail)

        return 0 if result == "SUCCESS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
